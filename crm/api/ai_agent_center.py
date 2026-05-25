import json
import re
import uuid
import importlib.util
import html
import io
from decimal import Decimal

import frappe
from frappe import _
from frappe.utils import cstr
from werkzeug.wrappers import Response

from crm.ai.kimi import DEFAULT_KIMI_MODEL, call_kimi_chat, estimate_kimi_cost, get_ai_settings, normalize_kimi_model, stream_kimi_chat_events
from crm.ai.rag import parser_command_available, query_rag, reindex_structured_data


AGENTS = [
	{
		"key": "credit_analyst",
		"name": "AI Credit Analyst Agent",
		"role": "credit analyst co-pilot",
		"icon": "file-text",
		"uat": ["Reads financial PDFs", "Auto-spreads PL/BS/CF", "Calculates ratios", "Drafts credit memo", "Recommends decision with reasoning"],
	},
	{
		"key": "relationship_manager",
		"name": "AI Relationship Manager Agent",
		"role": "relationship manager assistant",
		"icon": "users",
		"uat": ["Suggests next-best action", "Drafts emails/WA", "Summarizes calls", "Detects intent", "Books follow-ups"],
	},
	{
		"key": "collection_officer",
		"name": "AI Collection Officer Agent",
		"role": "collections prioritization and dunning assistant",
		"icon": "repeat",
		"uat": ["Prioritizes overdues", "Drafts polite reminders", "Negotiates PTP", "Routes escalations"],
	},
	{
		"key": "document_validator",
		"name": "AI Document Validator Agent",
		"role": "document completeness and authenticity checker",
		"icon": "check-square",
		"uat": ["Reads uploaded docs", "Checks signature/stamp/dates", "Flags suspicious items", "Scores 0-100", "Explains issues"],
	},
	{
		"key": "financial_analyst",
		"name": "AI Financial Analyst Agent",
		"role": "financial trend and anomaly analyst",
		"icon": "trending-up",
		"uat": ["Year-on-year analysis", "Benchmark comparison", "Anomaly detection", "Scenario simulations"],
	},
	{
		"key": "proposal_generator",
		"name": "AI Proposal Generator Agent",
		"role": "banking proposal drafting assistant",
		"icon": "briefcase",
		"uat": ["Customer + product input", "Structured proposal", "Editable draft", "Pricing logic", "PDF export"],
	},
	{
		"key": "risk_analyst",
		"name": "AI Risk Analyst Agent",
		"role": "hidden risk and risk score analyst",
		"icon": "shield",
		"uat": ["Scans customer/portfolio data", "Identifies risk signals", "Outputs score + factors", "Compares historical data"],
	},
	{
		"key": "customer_support",
		"name": "AI Customer Support Agent",
		"role": "customer-facing Bahasa and English support assistant",
		"icon": "message-circle",
		"uat": ["24/7 chat", "Multi-language", "Human handoff", "Satisfaction tracking"],
	},
	{
		"key": "compliance_checker",
		"name": "AI Compliance Checker Agent",
		"role": "AML/PEP and compliance scanning assistant",
		"icon": "lock",
		"uat": ["AML/PEP scans", "Suspicious flags", "SAR draft", "New regulation knowledge"],
	},
	{
		"key": "portfolio_monitor",
		"name": "AI Portfolio Monitor Agent",
		"role": "portfolio early-warning monitor",
		"icon": "activity",
		"uat": ["Daily portfolio scan", "Early warning signals", "Alert list", "Suggested action"],
	},
]

GENERAL_AGENT = {
	"key": "general",
	"name": "AI Agent Center",
	"role": "general CRM banking assistant",
	"icon": "cpu",
	"uat": ["Universal chat", "RAG grounded answers", "CRM action execution"],
}

LOW_RISK_ACTIONS = {"create_task", "create_note", "draft_communication", "create_recommendation", "book_follow_up", "generate_pdf_report"}
HIGH_RISK_ACTIONS = {"update_record", "send_communication", "fire_workflow", "export_regulatory_draft"}

AGENT_TOOLS = {
	"credit_analyst": ["financial_spreading", "ratio_analysis", "dscr_projection", "scenario_simulation", "create_recommendation", "generate_pdf_report"],
	"relationship_manager": ["next_best_action", "draft_communication", "book_follow_up", "create_task", "generate_pdf_report"],
	"collection_officer": ["overdue_prioritization", "draft_communication", "book_follow_up", "create_task", "generate_pdf_report"],
	"document_validator": ["document_completeness_check", "authenticity_flags", "create_note", "generate_pdf_report"],
	"financial_analyst": ["trend_analysis", "benchmark_comparison", "scenario_simulation", "generate_pdf_report"],
	"proposal_generator": ["proposal_draft", "pricing_logic", "create_recommendation", "generate_pdf_report"],
	"risk_analyst": ["risk_signal_scan", "risk_score_explanation", "create_recommendation", "generate_pdf_report"],
	"customer_support": ["customer_answer_draft", "human_handoff_task", "draft_communication", "generate_pdf_report"],
	"compliance_checker": ["aml_pep_scan", "suspicious_activity_draft", "export_regulatory_draft", "generate_pdf_report"],
	"portfolio_monitor": ["portfolio_early_warning_scan", "watchlist_recommendation", "create_task", "generate_pdf_report"],
	"general": ["rag_answer", "create_task", "create_note", "generate_pdf_report"],
}


def _get_agent(agent_key):
	for agent in AGENTS:
		if agent["key"] == agent_key:
			return agent
	return GENERAL_AGENT


def _agent_tools(agent_key):
	return AGENT_TOOLS.get(agent_key) or AGENT_TOOLS["general"]


def _doctype_ready(doctype):
	try:
		return bool(frappe.db.exists("DocType", doctype))
	except Exception:
		return False


def ensure_ai_tables():
	ddl = {
		"CRM AI Session": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Session` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, user VARCHAR(255),
				agent_key VARCHAR(140), customer VARCHAR(255), title VARCHAR(255), status VARCHAR(140)
			)
		""",
		"CRM AI Message": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Message` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, session VARCHAR(255),
				user VARCHAR(255), agent_key VARCHAR(140), role VARCHAR(40), content LONGTEXT,
				sources_json LONGTEXT, tokens INT, cost DECIMAL(18,9)
			)
		""",
		"CRM AI Memory": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Memory` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, user VARCHAR(255),
				scope VARCHAR(140), memory_key VARCHAR(255), content LONGTEXT, source VARCHAR(255)
			)
		""",
		"CRM AI Action Log": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Action Log` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, user VARCHAR(255),
				agent_key VARCHAR(140), session VARCHAR(255), action_type VARCHAR(140), status VARCHAR(140),
				risk_level VARCHAR(40), payload_json LONGTEXT, result_json LONGTEXT
			)
		""",
		"CRM AI Audit Log": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Audit Log` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, user VARCHAR(255),
				agent_key VARCHAR(140), model VARCHAR(140), prompt LONGTEXT, response LONGTEXT,
				sources_json LONGTEXT, tokens INT, cost DECIMAL(18,9), confidence DECIMAL(10,4), status VARCHAR(140)
			)
		""",
		"CRM AI Feedback": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Feedback` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, user VARCHAR(255),
				message_id VARCHAR(255), rating VARCHAR(40), comment TEXT
			)
		""",
		"CRM AI Performance Metric": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Performance Metric` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, agent_key VARCHAR(140),
				metric_date DATE, total_calls INT, avg_confidence DECIMAL(10,4), hallucination_failures INT,
				avg_latency_ms INT
			)
		""",
		"CRM AI Recommendation": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Recommendation` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, user VARCHAR(255),
				agent_key VARCHAR(140), reference_doctype VARCHAR(140), reference_docname VARCHAR(255),
				title VARCHAR(255), recommendation LONGTEXT, reasoning LONGTEXT, status VARCHAR(140), confidence DECIMAL(10,4)
			)
		""",
		"CRM AI Prompt": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Prompt` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, agent_key VARCHAR(140),
				title VARCHAR(255), prompt LONGTEXT, status VARCHAR(140), version INT
			)
		""",
		"CRM AI Automation Rule": """
			CREATE TABLE IF NOT EXISTS `tabCRM AI Automation Rule` (
				name VARCHAR(255) PRIMARY KEY, creation DATETIME, modified DATETIME, agent_key VARCHAR(140),
				title VARCHAR(255), threshold DECIMAL(10,4), action_type VARCHAR(140), requires_approval INT, enabled INT
			)
		""",
	}
	for table, statement in ddl.items():
		if frappe.db.table_exists(table):
			continue
		frappe.db.sql_ddl(statement)


def _raw_insert(table, values):
	ensure_ai_tables()
	now = frappe.utils.now_datetime()
	payload = {"name": values.get("name") or str(uuid.uuid4()), "creation": now, "modified": now, **values}
	columns = list(payload.keys())
	frappe.db.sql(
		f"INSERT INTO `tab{table}` ({', '.join('`' + col + '`' for col in columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
		[payload[col] for col in columns],
	)
	return payload["name"]


def _save_session(agent_key, customer=None, session_id=None, title=None):
	ensure_ai_tables()
	if session_id:
		frappe.db.sql("UPDATE `tabCRM AI Session` SET modified=%s WHERE name=%s", (frappe.utils.now_datetime(), session_id))
		return session_id
	return _raw_insert(
		"CRM AI Session",
		{
			"user": frappe.session.user,
			"agent_key": agent_key,
			"customer": customer,
			"title": title or _get_agent(agent_key)["name"],
			"status": "Open",
		},
	)


def _save_message(session_id, agent_key, role, content, sources=None, tokens=0, cost=Decimal("0")):
	return _raw_insert(
		"CRM AI Message",
		{
			"session": session_id,
			"user": frappe.session.user,
			"agent_key": agent_key,
			"role": role,
			"content": content,
			"sources_json": json.dumps(sources or [], default=str),
			"tokens": tokens or 0,
			"cost": cost,
		},
	)


def _audit(agent_key, model, prompt, response, sources=None, tokens=0, cost=Decimal("0"), confidence=0, status="Completed"):
	return _raw_insert(
		"CRM AI Audit Log",
		{
			"user": frappe.session.user,
			"agent_key": agent_key,
			"model": model,
			"prompt": prompt,
			"response": response,
			"sources_json": json.dumps(sources or [], default=str),
			"tokens": tokens or 0,
			"cost": cost,
			"confidence": confidence or 0,
			"status": status,
		},
	)


def _system_prompt(agent, rag_context, customer=None):
	tools = ", ".join(_agent_tools(agent["key"]))
	return (
		f"You are {agent['name']}, a {agent['role']} for BNI SUMMON CRM.\n"
		"Answer in the user's language, be concise, professional, and banking-specific.\n"
		"Use only the provided CRM/RAG sources for factual customer, credit, risk, document, and transaction claims.\n"
		"If sources are insufficient, say what is missing instead of inventing facts.\n"
		"Return structured Markdown using these sections unless the user asks for another format:\n"
		"## Executive Summary\n## Key Findings\n## Recommended Actions\n## Sources\n"
		"Use Markdown tables when useful. Include source numbers in the Sources section.\n"
		"Actions must be returned as JSON in a fenced block with _action, payload, and risk_level.\n"
		"Low-risk actions may create tasks, notes, draft communications, recommendations, follow-ups, or PDF reports.\n"
		"When the user asks for a report, laporan, PDF, or export, use _action generate_pdf_report with title, content, reference_doctype, and reference_docname in payload.\n"
		"High-risk actions must request confirmation.\n\n"
		f"Customer context: {customer or 'not scoped'}\n"
		f"Agent UAT obligations: {', '.join(agent.get('uat') or [])}\n\n"
		f"Available tools: {tools}\n\n"
		f"RAG sources:\n{rag_context or 'No RAG sources available.'}"
	)


def _markdown_to_report_html(text):
	escaped = html.escape(text or "").strip()
	lines = []
	for line in escaped.splitlines():
		if line.startswith("### "):
			lines.append(f"<h3>{line[4:]}</h3>")
		elif line.startswith("## "):
			lines.append(f"<h2>{line[3:]}</h2>")
		elif line.startswith("# "):
			lines.append(f"<h1>{line[2:]}</h1>")
		elif line.startswith("- "):
			lines.append(f"<p>&bull; {line[2:]}</p>")
		elif line:
			lines.append(f"<p>{line}</p>")
		else:
			lines.append("<br>")
	return "\n".join(lines)


def _create_pdf_report(payload):
	from frappe.utils.pdf import get_pdf

	title = cstr(payload.get("title") or "AI Agent Report").strip() or "AI Agent Report"
	content = payload.get("content") or payload.get("report") or payload.get("summary") or ""
	if not content:
		frappe.throw(_("PDF report content is required"))
	report_html = f"""
		<html>
			<head>
				<meta charset="utf-8">
				<style>
					body {{ font-family: Arial, sans-serif; color: #0f172a; font-size: 12px; line-height: 1.55; }}
					h1 {{ color: #0f766e; font-size: 22px; margin-bottom: 8px; }}
					h2 {{ color: #0f172a; font-size: 16px; margin-top: 18px; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; }}
					h3 {{ color: #334155; font-size: 13px; margin-top: 14px; }}
					p {{ margin: 6px 0; }}
					.meta {{ color: #64748b; font-size: 10px; margin-bottom: 18px; }}
				</style>
			</head>
			<body>
				<h1>{html.escape(title)}</h1>
				<div class="meta">Generated by AI Agent Center on {frappe.utils.now()}</div>
				{_markdown_to_report_html(content)}
			</body>
		</html>
	"""
	try:
		pdf = get_pdf(report_html)
	except OSError:
		pdf = _create_reportlab_pdf(title, content)
	file_name = frappe.scrub(f"{title}-{uuid.uuid4().hex[:8]}") + ".pdf"
	private_dir = frappe.get_site_path("private", "files")
	frappe.create_folder(private_dir)
	file_path = frappe.get_site_path("private", "files", file_name)
	with open(file_path, "wb") as file:
		file.write(pdf)
	file_doc = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": file_name,
			"file_url": f"/private/files/{file_name}",
			"is_private": 1,
			"attached_to_doctype": payload.get("reference_doctype"),
			"attached_to_name": payload.get("reference_docname"),
		}
	).insert(ignore_permissions=True)
	return {"doctype": "File", "name": file_doc.name, "file_url": file_doc.file_url, "file_name": file_doc.file_name}


def _create_reportlab_pdf(title, content):
	from reportlab.lib.pagesizes import A4
	from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
	from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

	buffer = io.BytesIO()
	styles = getSampleStyleSheet()
	styles.add(ParagraphStyle(name="BNITitle", parent=styles["Title"], textColor="#0f766e", fontSize=18, leading=22))
	styles.add(ParagraphStyle(name="BNIHeading", parent=styles["Heading2"], textColor="#0f172a", fontSize=13, leading=16, spaceBefore=10))
	styles.add(ParagraphStyle(name="BNIBody", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=5))
	doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
	story = [
		Paragraph(html.escape(title), styles["BNITitle"]),
		Paragraph(f"Generated by AI Agent Center on {html.escape(frappe.utils.now())}", styles["BNIBody"]),
		Spacer(1, 10),
	]
	for raw_line in cstr(content).splitlines():
		line = raw_line.strip()
		if not line:
			story.append(Spacer(1, 6))
			continue
		if line.startswith("#"):
			story.append(Paragraph(html.escape(line.lstrip("#").strip()), styles["BNIHeading"]))
		elif line.startswith("- "):
			story.append(Paragraph(f"&bull; {html.escape(line[2:].strip())}", styles["BNIBody"]))
		else:
			story.append(Paragraph(html.escape(line), styles["BNIBody"]))
	doc.build(story)
	return buffer.getvalue()


def _extract_actions(text):
	actions = []
	for match in re.finditer(r"```json\s*(\{.*?\})\s*```", text or "", re.DOTALL):
		try:
			data = json.loads(match.group(1))
			if data.get("_action"):
				actions.append(data)
		except Exception:
			continue
	return actions


def _clean_action_blocks(text):
	return re.sub(r"```json\s*\{.*?\"_action\".*?\}\s*```", "", text or "", flags=re.DOTALL).strip()


def _execute_low_risk_action(agent_key, session_id, action):
	action_type = action.get("_action")
	payload = frappe._dict(action.get("payload") or action)
	result = {}

	if action_type in {"create_task", "book_follow_up"}:
		doc = frappe.get_doc(
			{
				"doctype": "CRM Task",
				"title": payload.get("title") or payload.get("subject") or "AI follow-up",
				"priority": payload.get("priority") or "Medium",
				"status": "Todo",
				"due_date": payload.get("due_date"),
				"reference_doctype": payload.get("reference_doctype"),
				"reference_docname": payload.get("reference_docname"),
				"description": payload.get("description") or payload.get("notes"),
				"assigned_to": payload.get("assigned_to") or frappe.session.user,
			}
		).insert(ignore_permissions=True)
		result = {"doctype": "CRM Task", "name": doc.name, "title": doc.title}
	elif action_type == "create_note":
		doc = frappe.get_doc(
			{
				"doctype": "FCRM Note",
				"title": payload.get("title") or "AI note",
				"content": payload.get("content") or payload.get("notes") or "",
				"reference_doctype": payload.get("reference_doctype"),
				"reference_docname": payload.get("reference_docname"),
			}
		).insert(ignore_permissions=True)
		result = {"doctype": "FCRM Note", "name": doc.name, "title": doc.title}
	elif action_type == "draft_communication" and _doctype_ready("CRM Customer Communication"):
		doc = frappe.get_doc(
			{
				"doctype": "CRM Customer Communication",
				"customer": payload.get("customer"),
				"channel": payload.get("channel") or "Email",
				"direction": "Outbound",
				"subject": payload.get("subject") or "AI drafted communication",
				"message": payload.get("message") or "",
				"status": "Open",
				"compose_status": "Manual",
			}
		).insert(ignore_permissions=True)
		result = {"doctype": "CRM Customer Communication", "name": doc.name, "subject": doc.subject}
	elif action_type == "create_recommendation":
		result_name = _raw_insert(
			"CRM AI Recommendation",
			{
				"user": frappe.session.user,
				"agent_key": agent_key,
				"reference_doctype": payload.get("reference_doctype"),
				"reference_docname": payload.get("reference_docname"),
				"title": payload.get("title") or "AI Recommendation",
				"recommendation": payload.get("recommendation") or payload.get("content") or "",
				"reasoning": payload.get("reasoning") or "",
				"status": "Open",
				"confidence": payload.get("confidence") or 0,
			},
		)
		result = {"doctype": "CRM AI Recommendation", "name": result_name}
	elif action_type == "generate_pdf_report":
		result = _create_pdf_report(payload)
	else:
		result = {"message": "Action queued for manual handling"}

	action_id = _raw_insert(
		"CRM AI Action Log",
		{
			"user": frappe.session.user,
			"agent_key": agent_key,
			"session": session_id,
			"action_type": action_type,
			"status": "Completed",
			"risk_level": "low",
			"payload_json": json.dumps(payload, default=str),
			"result_json": json.dumps(result, default=str),
		},
	)
	return {"action_id": action_id, "status": "Completed", "result": result}


def _queue_high_risk_action(agent_key, session_id, action):
	action_id = _raw_insert(
		"CRM AI Action Log",
		{
			"user": frappe.session.user,
			"agent_key": agent_key,
			"session": session_id,
			"action_type": action.get("_action"),
			"status": "Pending Confirmation",
			"risk_level": action.get("risk_level") or "high",
			"payload_json": json.dumps(action.get("payload") or action, default=str),
			"result_json": "{}",
		},
	)
	return {"action_id": action_id, "status": "Pending Confirmation"}


def _handle_actions(agent_key, session_id, reply_text):
	results = []
	for action in _extract_actions(reply_text):
		action_type = action.get("_action")
		risk = (action.get("risk_level") or ("high" if action_type in HIGH_RISK_ACTIONS else "low")).lower()
		if action_type in LOW_RISK_ACTIONS and risk != "high":
			results.append(_execute_low_risk_action(agent_key, session_id, action))
		else:
			results.append(_queue_high_risk_action(agent_key, session_id, action))
	return results


@frappe.whitelist()
def get_agents():
	ensure_ai_tables()
	settings = get_ai_settings()
	rows = []
	for agent in AGENTS:
		today = frappe.utils.today()
		cost = frappe.db.sql(
			"""
			SELECT COALESCE(SUM(cost), 0) FROM `tabCRM AI Audit Log`
			WHERE agent_key=%s AND DATE(creation)=%s
		""",
			(agent["key"], today),
		)[0][0]
		last_activity = frappe.db.sql(
			"SELECT MAX(creation) FROM `tabCRM AI Audit Log` WHERE agent_key=%s",
			(agent["key"],),
		)[0][0]
		rows.append({**agent, "tools": _agent_tools(agent["key"]), "model": settings.kimi_model or DEFAULT_KIMI_MODEL, "status": "Ready", "cost_today": float(cost or 0), "last_activity": last_activity})
	return rows


@frappe.whitelist()
def query_agent(agent_key="general", message=None, session_id=None, customer=None, attachments=None):
	if not message or not str(message).strip():
		frappe.throw(_("Message is required"))
	agent = _get_agent(agent_key)
	session_id = _save_session(agent["key"], customer=customer, session_id=session_id, title=agent["name"])
	_save_message(session_id, agent["key"], "user", message)

	rag = query_rag(message, agent_key=agent["key"], customer=customer)
	if not rag["passes_guardrail"]:
		response = _("I do not have enough grounded CRM/RAG sources to answer that safely. Please index or attach the relevant customer/document data first.")
		message_id = _save_message(session_id, agent["key"], "assistant", response, rag["sources"])
		_audit(agent["key"], DEFAULT_KIMI_MODEL, message, response, rag["sources"], confidence=rag["confidence"], status="Guardrail Blocked")
		return {"response": response, "session_id": session_id, "message_id": message_id, "sources": rag["sources"], "actions": [], "confidence": rag["confidence"]}

	settings = get_ai_settings()
	system_prompt = _system_prompt(agent, rag["context"], customer=customer)
	messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]
	result = call_kimi_chat(messages, model=settings.kimi_model, thinking_mode=settings.thinking_mode)
	actions = _handle_actions(agent["key"], session_id, result.content)
	reply = _clean_action_blocks(result.content)
	message_id = _save_message(session_id, agent["key"], "assistant", reply, rag["sources"], result.total_tokens, result.cost)
	_audit(agent["key"], result.model, message, reply, rag["sources"], result.total_tokens, result.cost, rag["confidence"])
	frappe.db.commit()
	return {
		"response": reply,
		"session_id": session_id,
		"message_id": message_id,
		"sources": rag["sources"],
		"actions": actions,
		"confidence": rag["confidence"],
		"model": result.model,
		"tokens": result.total_tokens,
		"cost": float(result.cost),
	}


def _sse(event, data):
	return f"event: {event}\ndata: {json.dumps(data, default=str)}\n\n"


@frappe.whitelist(methods=["POST"])
def query_agent_stream(agent_key="general", message=None, session_id=None, customer=None, attachments=None):
	def generate():
		try:
			if not message or not str(message).strip():
				yield _sse("error", {"message": _("Message is required")})
				return

			agent = _get_agent(agent_key)
			current_session = _save_session(agent["key"], customer=customer, session_id=session_id, title=agent["name"])
			_save_message(current_session, agent["key"], "user", message)
			yield _sse("meta", {"session_id": current_session, "agent_key": agent["key"]})

			rag = query_rag(message, agent_key=agent["key"], customer=customer)
			if not rag["passes_guardrail"]:
				reply = _("I do not have enough grounded CRM/RAG sources to answer that safely. Please index or attach the relevant customer/document data first.")
				message_id = _save_message(current_session, agent["key"], "assistant", reply, rag["sources"])
				_audit(agent["key"], DEFAULT_KIMI_MODEL, message, reply, rag["sources"], confidence=rag["confidence"], status="Guardrail Blocked")
				frappe.db.commit()
				yield _sse("sources", {"sources": rag["sources"], "confidence": rag["confidence"]})
				yield _sse("delta", {"delta": reply})
				yield _sse(
					"done",
					{
						"response": reply,
						"session_id": current_session,
						"message_id": message_id,
						"sources": rag["sources"],
						"actions": [],
						"confidence": rag["confidence"],
						"model": DEFAULT_KIMI_MODEL,
						"tokens": 0,
						"cost": 0,
					},
				)
				return

			settings = get_ai_settings()
			system_prompt = _system_prompt(agent, rag["context"], customer=customer)
			messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": message}]
			yield _sse("sources", {"sources": rag["sources"], "confidence": rag["confidence"]})

			content_parts = []
			stream_meta = frappe._dict({"model": settings.kimi_model or DEFAULT_KIMI_MODEL, "total_tokens": 0, "cost": Decimal("0")})
			for event in stream_kimi_chat_events(messages, model=settings.kimi_model, thinking_mode=settings.thinking_mode):
				if event.event == "delta":
					content_parts.append(event.delta)
					yield _sse("delta", {"delta": event.delta})
				elif event.event == "done":
					stream_meta = event

			full_content = "".join(content_parts)
			actions = _handle_actions(agent["key"], current_session, full_content)
			reply = _clean_action_blocks(full_content)
			message_id = _save_message(current_session, agent["key"], "assistant", reply, rag["sources"], stream_meta.total_tokens, stream_meta.cost)
			_audit(agent["key"], stream_meta.model, message, reply, rag["sources"], stream_meta.total_tokens, stream_meta.cost, rag["confidence"])
			frappe.db.commit()
			yield _sse("actions", {"actions": actions})
			yield _sse(
				"done",
				{
					"response": reply,
					"session_id": current_session,
					"message_id": message_id,
					"sources": rag["sources"],
					"actions": actions,
					"confidence": rag["confidence"],
					"model": stream_meta.model,
					"tokens": stream_meta.total_tokens,
					"cost": float(stream_meta.cost),
				},
			)
		except Exception as exc:
			frappe.log_error(frappe.get_traceback(), "AI Agent Center Stream Error")
			frappe.db.rollback()
			yield _sse("error", {"message": cstr(exc)[:500]})

	return Response(
		generate(),
		mimetype="text/event-stream",
		headers={
			"Cache-Control": "no-cache",
			"X-Accel-Buffering": "no",
		},
	)


@frappe.whitelist()
def get_rag_status():
	chunk_count = frappe.db.count("CRM AI RAG Chunk") if frappe.db.table_exists("CRM AI RAG Chunk") else 0
	document_count = frappe.db.count("CRM AI RAG Document") if frappe.db.table_exists("CRM AI RAG Document") else 0
	raganything_available = importlib.util.find_spec("raganything") is not None
	mineru_package_available = importlib.util.find_spec("mineru") is not None
	mineru_command_available = parser_command_available()
	mineru_available = mineru_package_available and mineru_command_available
	return {
		"native_raganything_ready": bool(raganything_available and mineru_available),
		"fallback_retrieval_ready": chunk_count > 0,
		"raganything_package_available": raganything_available,
		"mineru_package_available": mineru_package_available,
		"mineru_command_available": mineru_command_available,
		"mineru_parser_available": mineru_available,
		"chunk_count": chunk_count,
		"document_count": document_count,
		"status": "RAGAnything Ready" if raganything_available and mineru_available else "Fallback RAG Ready" if chunk_count else "Not Indexed",
		"message": _("Install the MinerU CLI command and reindex RAG to enable native RAGAnything parsing.") if raganything_available and not mineru_available else "",
	}


@frappe.whitelist()
def generate_summary(scope, docname, length="Standard"):
	if scope not in {"Customer", "customer_360"}:
		frappe.throw(_("Only Customer 360 summaries are supported."))
	if not docname or not frappe.db.exists("Customer", docname):
		frappe.throw(_("Customer not found"))
	length = length if length in {"TL;DR", "Standard", "Detailed"} else "Standard"
	prompt = (
		f"Generate a {length} AI Customer Summary and actionable banking insights for customer {docname}. "
		"Cover credit exposure, KYC, risk, documents, transactions, relationships, and next best actions. "
		"Use only sourced CRM/RAG facts. Return structured Markdown with these sections: "
		"## Customer Snapshot, ## Risk Signals, ## Opportunities, ## Recommended Actions, ## Sources."
	)
	response = query_agent("risk_analyst", prompt, customer=docname)
	summary = response["response"]
	from crm.api.credit import save_customer_summary

	save_customer_summary(docname, summary)
	if _doctype_ready("CRM AI Insight"):
		frappe.get_doc(
			{
				"doctype": "CRM AI Insight",
				"customer": docname,
				"insight_type": "Risk",
				"title": f"RAG {length} customer summary",
				"confidence_score": min(100, int((response.get("confidence") or 0) * 100)),
				"status": "Open",
				"suggested_action": "Review AI Agent Center sources and approve next-best action.",
				"notes": summary,
			}
		).insert(ignore_permissions=True)
	frappe.db.commit()
	return response


@frappe.whitelist()
def confirm_action(action_id):
	ensure_ai_tables()
	row = frappe.db.sql("SELECT * FROM `tabCRM AI Action Log` WHERE name=%s", (action_id,), as_dict=True)
	if not row:
		frappe.throw(_("Action not found"))
	action = row[0]
	payload = frappe.parse_json(action.payload_json or "{}")
	result = {"confirmed_by": frappe.session.user}
	status = "Confirmed"
	if action.action_type == "update_record":
		doctype = payload.get("doctype")
		docname = payload.get("docname")
		values = payload.get("values") or {}
		if doctype and docname and values:
			doc = frappe.get_doc(doctype, docname)
			for fieldname, value in values.items():
				if fieldname in doc.meta.get_valid_columns():
					doc.set(fieldname, value)
			doc.save(ignore_permissions=False)
			result.update({"doctype": doctype, "docname": docname, "updated_fields": list(values.keys())})
			status = "Completed"
	elif action.action_type == "send_communication":
		result.update({"message": "External channel adapter is not configured; communication remains queued for manual send."})
	frappe.db.sql(
		"UPDATE `tabCRM AI Action Log` SET status=%s, modified=%s, result_json=%s WHERE name=%s",
		(status, frappe.utils.now_datetime(), json.dumps(result, default=str), action_id),
	)
	frappe.db.commit()
	return {"name": action_id, "status": status, "action_type": action.action_type, "result": result}


@frappe.whitelist()
def reject_action(action_id, reason=None):
	ensure_ai_tables()
	frappe.db.sql(
		"UPDATE `tabCRM AI Action Log` SET status=%s, modified=%s, result_json=%s WHERE name=%s",
		("Rejected", frappe.utils.now_datetime(), json.dumps({"rejected_by": frappe.session.user, "reason": reason}, default=str), action_id),
	)
	frappe.db.commit()
	return {"name": action_id, "status": "Rejected"}


@frappe.whitelist()
def clear_memory(scope, key):
	ensure_ai_tables()
	frappe.db.sql(
		"DELETE FROM `tabCRM AI Memory` WHERE user=%s AND scope=%s AND memory_key=%s",
		(frappe.session.user, scope, key),
	)
	frappe.db.commit()
	return {"cleared": True}


@frappe.whitelist()
def submit_feedback(message_id, rating, comment=None):
	name = _raw_insert(
		"CRM AI Feedback",
		{"user": frappe.session.user, "message_id": message_id, "rating": rating, "comment": comment},
	)
	frappe.db.commit()
	return {"name": name, "status": "Recorded"}


@frappe.whitelist()
def get_cost_dashboard(filters=None):
	ensure_ai_tables()
	rows = frappe.db.sql(
		"""
		SELECT agent_key, user, COUNT(*) calls, COALESCE(SUM(tokens), 0) tokens, COALESCE(SUM(cost), 0) cost
		FROM `tabCRM AI Audit Log`
		GROUP BY agent_key, user
		ORDER BY cost DESC
		LIMIT 100
	""",
		as_dict=True,
	)
	total = sum(float(row.cost or 0) for row in rows)
	return {"total_cost": total, "rows": rows}


@frappe.whitelist()
def get_audit_log(filters=None):
	ensure_ai_tables()
	return frappe.db.sql(
		"""
		SELECT name, creation, user, agent_key, model, tokens, cost, confidence, status, LEFT(prompt, 240) prompt_preview, LEFT(response, 240) response_preview
		FROM `tabCRM AI Audit Log`
		ORDER BY creation DESC
		LIMIT 100
	""",
		as_dict=True,
	)


@frappe.whitelist()
def run_sandbox(prompt_id=None, input_payload=None, model_override=None):
	payload = frappe.parse_json(input_payload) if isinstance(input_payload, str) else (input_payload or {})
	prompt = payload.get("prompt") or payload.get("message") or ""
	if prompt_id:
		row = frappe.db.sql("SELECT prompt FROM `tabCRM AI Prompt` WHERE name=%s", (prompt_id,), as_dict=True)
		if row:
			prompt = row[0].prompt + "\n\nInput:\n" + json.dumps(payload, default=str, indent=2)
	if not prompt:
		frappe.throw(_("Sandbox prompt is required"))
	result = call_kimi_chat(
		[
			{"role": "system", "content": "You are testing an AI Agent Center prompt in sandbox mode. Do not mutate production data. Return structured Markdown with headings, tables, and source notes when useful. Do not return raw JSON unless explicitly requested."},
			{"role": "user", "content": prompt},
		],
		model=model_override,
	)
	_audit("sandbox", result.model, prompt, result.content, [], result.total_tokens, result.cost, 1, "Sandbox")
	frappe.db.commit()
	return {"response": result.content, "model": result.model, "tokens": result.total_tokens, "cost": float(result.cost)}


@frappe.whitelist()
def reindex_rag(scope=None, docname=None):
	return reindex_structured_data(scope=scope, docname=docname, reset_native=True)


@frappe.whitelist()
def save_ai_settings(provider, model, base_url=None, api_key=None):
	settings = frappe.get_doc("FCRM Settings", "FCRM Settings")
	settings.ai_provider = provider
	settings.kimi_model = normalize_kimi_model(model)
	if base_url is not None:
		settings.kimi_base_url = (base_url or "https://api.moonshot.ai/v1").rstrip("/")
	if api_key:
		if provider == "Gemini":
			settings.gemini_api_key = api_key
		else:
			settings.kimi_api_key = api_key
	settings.save(ignore_permissions=True)
	frappe.db.commit()
	return settings.as_dict()
