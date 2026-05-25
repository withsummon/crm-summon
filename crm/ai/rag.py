import asyncio
import hashlib
import json
import os
import re
from functools import partial

import frappe
from frappe import _

from crm.ai.kimi import call_kimi_chat, get_ai_settings


STRUCTURED_DOCTYPES = {
	"CRM Lead": ["name", "lead_name", "status", "organization", "email", "mobile_no", "source", "modified"],
	"CRM Deal": ["name", "organization", "status", "annual_revenue", "deal_value", "modified"],
	"Contact": ["name", "first_name", "last_name", "email_id", "mobile_no", "company_name", "modified"],
	"CRM Organization": ["name", "organization_name", "industry", "website", "annual_revenue", "modified"],
	"CRM Task": ["name", "title", "status", "priority", "due_date", "reference_doctype", "reference_docname", "modified"],
	"FCRM Note": ["name", "title", "content", "reference_doctype", "reference_docname", "modified"],
	"CRM Call Log": ["name", "type", "status", "duration", "summary", "modified"],
	"CRM Credit Application": ["name", "borrower", "status", "facility_type", "requested_amount", "purpose", "modified"],
	"CRM Credit Facility": ["name", "customer", "facility_type", "product_type", "status", "outstanding", "limit_amount", "health", "modified"],
	"CRM KYC Review": ["name", "customer", "status", "npwp", "nik", "next_review_date", "watchlist", "watchlist_reason", "modified"],
	"CRM Relationship": ["name", "customer", "related_party", "relationship_type", "ownership_percent", "exposure", "aml_pep_status", "modified"],
	"CRM Bureau Report": ["name", "customer", "source", "kol_status", "score", "external_exposure", "notes", "modified"],
	"CRM Customer Document": ["name", "customer", "document_type", "title", "folder", "file", "expiry_status", "notes", "modified"],
	"CRM Customer Communication": ["name", "customer", "channel", "direction", "subject", "status", "message", "modified"],
	"CRM Transaction History": ["name", "customer", "facility", "transaction_type", "amount", "status", "notes", "modified"],
	"CRM Risk Profile": ["name", "customer", "risk_grade", "internal_score", "watchlist_status", "risk_factors", "early_warning_triggers", "modified"],
	"CRM Financial Statement": ["name", "customer", "statement_type", "metric", "year", "amount", "auditor", "notes", "modified"],
	"CRM Site Visit": ["name", "customer", "visit_date", "notes", "report_pdf", "photo_attachment", "modified"],
	"CRM AI Insight": ["name", "customer", "insight_type", "title", "confidence_score", "status", "suggested_action", "notes", "modified"],
}


def get_rag_storage_path():
	settings = get_ai_settings()
	if settings.rag_storage_path:
		return frappe.get_site_path(settings.rag_storage_path) if not os.path.isabs(settings.rag_storage_path) else settings.rag_storage_path
	return frappe.get_site_path("private", "files", "ai_agent_center_rag")


def ensure_rag_tables():
	ddl = {
		"CRM AI RAG Chunk": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI RAG Chunk` (
				name VARCHAR(255) PRIMARY KEY,
				creation DATETIME,
				modified DATETIME,
				reference_doctype VARCHAR(140),
				reference_docname VARCHAR(255),
				customer VARCHAR(255),
				agent_key VARCHAR(140),
				source_title VARCHAR(255),
				content LONGTEXT,
				content_hash VARCHAR(64),
				INDEX idx_customer (customer),
				INDEX idx_reference (reference_doctype, reference_docname),
				INDEX idx_hash (content_hash)
			)
		""",
		"CRM AI RAG Document": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI RAG Document` (
				name VARCHAR(255) PRIMARY KEY,
				creation DATETIME,
				modified DATETIME,
				source_type VARCHAR(140),
				reference_doctype VARCHAR(140),
				reference_docname VARCHAR(255),
				customer VARCHAR(255),
				title VARCHAR(255),
				file_url TEXT,
				index_status VARCHAR(140),
				last_indexed_on DATETIME,
				error TEXT
			)
		""",
	}
	for table, statement in ddl.items():
		if frappe.db.table_exists(table):
			continue
		frappe.db.sql_ddl(statement)


def _doctype_ready(doctype):
	try:
		return bool(frappe.db.exists("DocType", doctype))
	except Exception:
		return False


def _safe_fields(doctype, fields):
	meta = frappe.get_meta(doctype)
	valid = {"name", "creation", "modified", "owner"}
	valid.update(df.fieldname for df in meta.fields)
	return [field for field in fields if field in valid]


def _record_to_text(doctype, row):
	lines = [f"Doctype: {doctype}", f"Record: {row.get('name')}"]
	for key, value in row.items():
		if value not in (None, ""):
			lines.append(f"{key.replace('_', ' ').title()}: {value}")
	return "\n".join(lines)


def collect_structured_content(customer=None, limit=80):
	content_list = []
	for doctype, fields in STRUCTURED_DOCTYPES.items():
		if not _doctype_ready(doctype):
			continue
		safe_fields = _safe_fields(doctype, fields)
		filters = {}
		if customer:
			if "customer" in safe_fields:
				filters["customer"] = customer
			elif "borrower" in safe_fields:
				filters["borrower"] = customer
			elif "reference_doctype" in safe_fields and "reference_docname" in safe_fields:
				filters.update({"reference_doctype": "Customer", "reference_docname": customer})
			elif doctype == "Customer":
				filters["name"] = customer
			else:
				continue
		try:
			rows = frappe.get_all(doctype, fields=safe_fields, filters=filters, order_by="modified desc", limit=limit)
		except Exception:
			continue
		for row in rows:
			text = _record_to_text(doctype, row)
			content_list.append(
				{
					"type": "text",
					"text": text,
					"page_idx": 0,
					"metadata": {
						"doctype": doctype,
						"docname": row.get("name"),
						"customer": row.get("customer") or row.get("borrower") or row.get("reference_docname"),
						"title": row.get("title") or row.get("lead_name") or row.get("organization") or row.get("name"),
					},
				}
			)
	return content_list


def _upsert_chunk(item, agent_key=None):
	metadata = item.get("metadata") or {}
	text = item.get("text") or item.get("table_body") or json.dumps(item, default=str)
	content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
	name = f"RAG-{content_hash[:28]}"
	now = frappe.utils.now_datetime()
	frappe.db.sql(
		"""
		REPLACE INTO `tabCRM AI RAG Chunk`
		(name, creation, modified, reference_doctype, reference_docname, customer, agent_key, source_title, content, content_hash)
		VALUES (%s, COALESCE((SELECT creation FROM (SELECT creation FROM `tabCRM AI RAG Chunk` WHERE name=%s) existing), %s), %s, %s, %s, %s, %s, %s, %s, %s)
	""",
		(
			name,
			name,
			now,
			now,
			metadata.get("doctype"),
			metadata.get("docname"),
			metadata.get("customer"),
			agent_key,
			metadata.get("title") or metadata.get("docname"),
			text,
			content_hash,
		),
	)
	return name


def _run_async(coro):
	try:
		loop = asyncio.get_event_loop()
	except RuntimeError:
		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
	if loop.is_running():
		return None
	return loop.run_until_complete(coro)


def _local_embedding_func():
	settings = get_ai_settings()
	from lightrag.utils import EmbeddingFunc
	from sentence_transformers import SentenceTransformer

	model = SentenceTransformer(settings.local_embedding_model or "BAAI/bge-m3")

	async def embed(texts):
		if isinstance(texts, str):
			texts = [texts]
		return model.encode(list(texts), normalize_embeddings=True).tolist()

	dim = len(model.encode(["dimension probe"], normalize_embeddings=True)[0])
	return EmbeddingFunc(embedding_dim=dim, max_token_size=8192, func=embed)


def get_raganything_instance():
	from raganything import RAGAnything, RAGAnythingConfig

	settings = get_ai_settings()
	working_dir = get_rag_storage_path()
	os.makedirs(working_dir, exist_ok=True)

	def llm_model_func(prompt, system_prompt=None, history_messages=None, **kwargs):
		messages = []
		if system_prompt:
			messages.append({"role": "system", "content": system_prompt})
		for row in history_messages or []:
			messages.append(row)
		messages.append({"role": "user", "content": prompt})
		return call_kimi_chat(messages, thinking_mode=settings.thinking_mode).content

	def vision_model_func(prompt, system_prompt=None, history_messages=None, image_data=None, messages=None, **kwargs):
		if messages:
			return call_kimi_chat(messages, thinking_mode=settings.thinking_mode).content
		payload = [{"type": "text", "text": prompt}]
		if image_data:
			payload.insert(0, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}})
		return call_kimi_chat(
			[
				{"role": "system", "content": system_prompt or "You are a banking document analysis assistant."},
				{"role": "user", "content": payload},
			],
			thinking_mode=settings.thinking_mode,
		).content

	config = RAGAnythingConfig(
		working_dir=working_dir,
		parser="mineru",
		parse_method="auto",
		enable_image_processing=True,
		enable_table_processing=True,
		enable_equation_processing=True,
	)
	return RAGAnything(config=config, llm_model_func=llm_model_func, vision_model_func=vision_model_func, embedding_func=_local_embedding_func())


def reindex_structured_data(scope=None, docname=None, agent_key=None):
	ensure_rag_tables()
	customer = docname if scope in ("Customer", "customer_360") else None
	content_list = collect_structured_content(customer=customer)
	for item in content_list:
		_upsert_chunk(item, agent_key=agent_key)

	rag_status = "fallback_indexed"
	try:
		rag = get_raganything_instance()
		if content_list:
			_run_async(
				rag.insert_content_list(
					content_list=content_list,
					file_path=f"{scope or 'crm'}:{docname or 'all'}",
					display_stats=False,
				)
			)
			rag_status = "raganything_indexed"
	except Exception as exc:
		frappe.log_error(frappe.get_traceback(), "RAGAnything Index Error")
		rag_status = f"fallback_indexed: {str(exc)[:160]}"

	frappe.db.commit()
	return {"indexed": len(content_list), "status": rag_status}


def retrieve_sources(query, customer=None, limit=8):
	ensure_rag_tables()
	words = [word for word in re.findall(r"[\w]+", (query or "").lower()) if len(word) > 2]
	if not words:
		words = ["customer", "credit", "risk"]
	conditions = []
	params = []
	if customer:
		conditions.append("(customer=%s OR reference_docname=%s)")
		params.extend([customer, customer])
	where = " AND ".join(conditions) if conditions else "1=1"
	rows = frappe.db.sql(
		f"""
		SELECT name, reference_doctype, reference_docname, customer, source_title, content
		FROM `tabCRM AI RAG Chunk`
		WHERE {where}
		ORDER BY modified DESC
		LIMIT 200
	""",
		params,
		as_dict=True,
	)
	scored = []
	for row in rows:
		text = (row.content or "").lower()
		score = sum(text.count(word) for word in words)
		if score or not words:
			scored.append((score, row))
	scored.sort(key=lambda item: item[0], reverse=True)
	results = []
	for score, row in scored[:limit]:
		results.append(
			{
				"id": row.name,
				"title": row.source_title or row.reference_docname or row.reference_doctype or "CRM Source",
				"doctype": row.reference_doctype,
				"docname": row.reference_docname,
				"customer": row.customer,
				"excerpt": (row.content or "")[:700],
				"score": score,
			}
		)
	return results


def query_rag(query, agent_key=None, customer=None):
	settings = get_ai_settings()
	sources = retrieve_sources(query, customer=customer)
	if not sources:
		reindex_structured_data(scope="customer_360" if customer else "crm", docname=customer, agent_key=agent_key)
		sources = retrieve_sources(query, customer=customer)

	context = "\n\n".join(f"[{idx + 1}] {source['title']}\n{source['excerpt']}" for idx, source in enumerate(sources))
	confidence = min(0.95, 0.2 + (len(sources) * 0.1))
	return {
		"context": context,
		"sources": sources,
		"confidence": confidence,
		"passes_guardrail": confidence >= settings.guardrail_confidence_threshold,
	}
