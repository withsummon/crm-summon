import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from crm.ai.openrouter import DEFAULT_LLM_MODEL, call_llm_chat, stream_llm_chat_events
from crm.api.ai_agent_center import (
	AGENTS,
	OUTPUT_PROFILES,
	ensure_ai_tables,
	get_agents,
	get_rag_status,
	query_agent,
	query_agent_stream,
	save_ai_settings,
	_parse_structured_response,
)


class TestAIAgentCenter(TestCase):
	def tearDown(self):
		try:
			frappe.db.rollback()
		except Exception:
			pass

	def test_agent_registry_matches_uat_scope(self):
		self.assertEqual(len(AGENTS), 10)
		self.assertIn("credit_analyst", {agent["key"] for agent in AGENTS})
		self.assertIn("portfolio_monitor", {agent["key"] for agent in AGENTS})
		settings = frappe._dict({"model": DEFAULT_LLM_MODEL})
		fake_frappe = SimpleNamespace(db=SimpleNamespace(sql=lambda *args, **kwargs: [[0]]), utils=SimpleNamespace(today=lambda: "2026-05-24"))
		with patch("crm.api.ai_agent_center.ensure_ai_tables"), patch("crm.api.ai_agent_center.get_ai_settings", return_value=settings), patch("crm.api.ai_agent_center.frappe", fake_frappe):
			self.assertEqual(len(get_agents.__wrapped__()), 10)

	def test_openrouter_client_uses_configured_model_and_actual_cost(self):
		settings = frappe._dict({"api_key": "test-key", "model": DEFAULT_LLM_MODEL})
		response = SimpleNamespace(
			model=DEFAULT_LLM_MODEL,
			choices=[SimpleNamespace(message=SimpleNamespace(content="ok"))],
			usage=SimpleNamespace(prompt_tokens=2, completion_tokens=1, total_tokens=3, cost=0.001),
			model_dump=lambda: {"model": DEFAULT_LLM_MODEL},
		)
		with patch("crm.ai.openrouter.get_ai_settings", return_value=settings), patch("crm.ai.openrouter.OpenRouter") as sdk:
			sdk.return_value.__enter__.return_value.chat.send.return_value = response
			result = call_llm_chat([{"role": "user", "content": "hello"}])
		self.assertEqual(result.content, "ok")
		self.assertEqual(str(result.cost), "0.001")
		self.assertEqual(sdk.return_value.__enter__.return_value.chat.send.call_args.kwargs["model"], DEFAULT_LLM_MODEL)

	def test_openrouter_client_streams_delta_events(self):
		settings = frappe._dict({"api_key": "test-key", "model": DEFAULT_LLM_MODEL})
		events = [
			SimpleNamespace(model=DEFAULT_LLM_MODEL, choices=[SimpleNamespace(delta=SimpleNamespace(content="hel"))], usage=None),
			SimpleNamespace(model=DEFAULT_LLM_MODEL, choices=[SimpleNamespace(delta=SimpleNamespace(content="lo"))], usage=SimpleNamespace(prompt_tokens=2, completion_tokens=2, total_tokens=4, cost=0.002)),
		]
		with patch("crm.ai.openrouter.get_ai_settings", return_value=settings), patch("crm.ai.openrouter.OpenRouter") as sdk:
			sdk.return_value.__enter__.return_value.chat.send.return_value = iter(events)
			result = list(stream_llm_chat_events([{"role": "user", "content": "hello"}]))
		self.assertEqual("".join(event.delta for event in result if event.event == "delta"), "hello")
		self.assertEqual(result[-1].total_tokens, 4)
		self.assertEqual(str(result[-1].cost), "0.002")
		self.assertTrue(sdk.return_value.__enter__.return_value.chat.send.call_args.kwargs["stream"])

	def test_stream_endpoint_returns_event_stream_response(self):
		response = query_agent_stream.__wrapped__("general", "hello")
		self.assertEqual(response.mimetype, "text/event-stream")

	def test_structured_parser_accepts_valid_json(self):
		payload = {
			"schema_version": "1.0",
			"agent_key": "credit_analyst",
			"title": "Analisis Kredit PT Demo",
			"executive_summary": "Debitur menunjukkan performa memadai.",
			"confidence": 0.82,
			"sections": [{"title": "Rasio & DSCR", "summary": "DSCR di atas ambang minimum.", "metrics": [{"label": "DSCR", "value": "1,42x"}]}],
			"recommendations": [{"title": "Approve", "rationale": "Cash flow memadai.", "priority": "medium", "next_step": "Review covenant"}],
			"risks": [{"title": "Konsentrasi pelanggan", "severity": "medium", "description": "Top buyer dominan.", "mitigation": "Pantau AR aging"}],
			"actions": [],
			"sources": [{"id": "S1", "title": "Financial Spread", "doctype": "CRM Credit Application", "docname": "APP-001", "excerpt": "DSCR 1,42x"}],
			"limitations": [],
		}

		result = _parse_structured_response(json.dumps(payload), "credit_analyst", confidence=0.5)

		self.assertEqual(result["title"], "Analisis Kredit PT Demo")
		self.assertEqual(result["agent_key"], "credit_analyst")
		self.assertEqual(result["confidence"], 0.82)
		self.assertEqual(result["sections"][0]["metrics"][0]["label"], "DSCR")

	def test_structured_parser_accepts_fenced_json(self):
		raw = """```json
{"title":"Ringkasan RM","executive_summary":"Nasabah perlu follow-up.","confidence":75,"sections":[{"title":"Next Best Action","items":["Telepon hari ini"]}],"actions":[]}
```"""

		result = _parse_structured_response(raw, "relationship_manager")

		self.assertEqual(result["agent_key"], "relationship_manager")
		self.assertEqual(result["confidence"], 0.75)
		self.assertEqual(result["sections"][0]["items"], ["Telepon hari ini"])

	def test_structured_parser_accepts_fenced_json_with_nested_proposal(self):
		raw = """Berikut draft proposal:
```json
{
  "title": "Proposal Kredit PT Demo",
  "executive_summary": "Proposal layak dikaji.",
  "sections": [
    {
      "title": "Struktur Proposal",
      "summary": {"headline": "Limit Rp5 miliar", "reasoning": {"basis": "cash flow positif"}},
      "items": [{"title": "Produk", "description": "BNI Kredit Modal Kerja"}, {"title": "Tenor", "value": "12 bulan"}]
    }
  ],
  "recommendations": [{"title": "Lanjutkan", "rationale": {"detail": "Dokumen utama tersedia"}, "next_step": {"task": "Review legalitas"}}],
  "risks": [{"title": "Kelengkapan dokumen", "description": {"issue": "NPWP belum terverifikasi"}, "mitigation": {"step": "Validasi ulang"}}],
  "actions": []
}
```
Silakan validasi."""

		result = _parse_structured_response(raw, "proposal_generator")

		self.assertEqual(result["title"], "Proposal Kredit PT Demo")
		self.assertIn("Limit Rp5 miliar", result["sections"][0]["summary"])
		self.assertIn("BNI Kredit Modal Kerja", result["sections"][0]["items"][0])
		self.assertIn("Dokumen utama tersedia", result["recommendations"][0]["rationale"])
		self.assertNotIn("{", result["sections"][0]["summary"])
		self.assertNotIn("{", result["recommendations"][0]["rationale"])

	def test_structured_parser_falls_back_for_broken_output(self):
		result = _parse_structured_response("Saya tidak sengaja menulis markdown.\n\n| A | B |", "portfolio_monitor")

		self.assertEqual(result["title"], "Output AI perlu divalidasi")
		self.assertEqual(result["agent_key"], "portfolio_monitor")
		self.assertTrue(result["limitations"])
		self.assertIn("markdown", result["executive_summary"].lower())

	def test_all_agent_profiles_have_required_sections(self):
		for agent_key, titles in OUTPUT_PROFILES.items():
			with self.subTest(agent_key=agent_key):
				result = _parse_structured_response("{}", agent_key)
				section_titles = [section["title"] for section in result["sections"]]
				self.assertEqual(section_titles[:3], titles[:3])

	def test_stream_endpoint_emits_status_and_structured_done_without_delta(self):
		rag_response = {
			"passes_guardrail": True,
			"context": "Source 1: Demo CRM customer context.",
			"sources": [{"title": "Demo CRM customer context"}],
			"confidence": 0.9,
		}
		stream_events = [
			frappe._dict({"event": "delta", "delta": '{"title":"Analisis Portofolio","executive_summary":"Risiko utama terkendali.","confidence":0.9,"sections":[{"title":"Ringkasan Portofolio","summary":"Tidak ada breach mayor."}],"actions":[]}', "model": DEFAULT_LLM_MODEL}),
			frappe._dict({"event": "done", "model": DEFAULT_LLM_MODEL, "total_tokens": 11, "cost": 0}),
		]

		with (
			patch("crm.api.ai_agent_center._save_session", return_value="AI-SESSION-001"),
			patch("crm.api.ai_agent_center._save_message", return_value="AI-MSG-001"),
			patch("crm.api.ai_agent_center.query_rag", return_value=rag_response),
			patch("crm.api.ai_agent_center.get_ai_settings", return_value=frappe._dict({"model": DEFAULT_LLM_MODEL, "thinking_mode": "disabled"})),
			patch("crm.api.ai_agent_center.stream_llm_chat_events", return_value=iter(stream_events)),
			patch("crm.api.ai_agent_center._handle_actions", return_value=[]),
			patch("crm.api.ai_agent_center._audit"),
			patch.object(frappe.db, "commit"),
		):
			response = query_agent_stream.__wrapped__("portfolio_monitor", "scan portfolio")
			body = "".join(response.response)

		self.assertIn("event: status", body)
		self.assertIn("event: sources", body)
		self.assertIn("event: done", body)
		self.assertIn("structured_response", body)
		self.assertNotIn("event: delta", body)

	def test_rag_status_reports_counts(self):
		status = get_rag_status.__wrapped__()
		self.assertIn("native_raganything_ready", status)
		self.assertIn("chunk_count", status)

	def test_query_agent_does_not_run_ddl_when_ai_tables_exist(self):
		ensure_ai_tables()
		created_session = None
		rag_response = {
			"passes_guardrail": True,
			"context": "Source 1: Demo CRM customer context.",
			"sources": [{"title": "Demo CRM customer context"}],
			"confidence": 0.9,
		}
		kimi_response = frappe._dict(
			{
				"content": "Grounded answer.\n\nSources\n1. Demo CRM customer context",
				"model": DEFAULT_LLM_MODEL,
				"total_tokens": 7,
				"cost": 0,
			}
		)

		try:
			with (
				patch("crm.api.ai_agent_center.query_rag", return_value=rag_response),
				patch("crm.api.ai_agent_center.get_ai_settings", return_value=frappe._dict({"model": DEFAULT_LLM_MODEL, "thinking_mode": "disabled"})),
				patch("crm.api.ai_agent_center.call_llm_chat", return_value=kimi_response),
				patch.object(frappe.db, "sql_ddl", side_effect=AssertionError("DDL should not run during chat when tables exist")),
			):
				response = query_agent.__wrapped__("credit_analyst", "summarize the application")
			created_session = response["session_id"]
			self.assertIn("Grounded answer", response["response"])
			self.assertEqual(response["structured_response"]["title"], "Output AI perlu divalidasi")
			self.assertEqual(response["structured_response"]["agent_key"], "credit_analyst")
			self.assertTrue(response["structured_response"]["limitations"])
			self.assertEqual(response["model"], DEFAULT_LLM_MODEL)
			self.assertEqual(response["confidence"], 0.9)
		finally:
			if created_session:
				for table in ("CRM AI Action Log", "CRM AI Message"):
					frappe.db.sql(f"DELETE FROM `tab{table}` WHERE session=%s", (created_session,))
				frappe.db.sql("DELETE FROM `tabCRM AI Audit Log` WHERE prompt=%s", ("summarize the application",))
				frappe.db.sql("DELETE FROM `tabCRM AI Session` WHERE name=%s", (created_session,))
				frappe.db.commit()

	def test_save_ai_settings_rejects_empty_model(self):
		with patch("crm.api.ai_agent_center.frappe.only_for"):
			with self.assertRaises(frappe.ValidationError):
				save_ai_settings.__wrapped__("")

	def test_save_ai_settings_rejects_whitespace_model(self):
		with patch("crm.api.ai_agent_center.frappe.only_for"):
			with self.assertRaises(frappe.ValidationError):
				save_ai_settings.__wrapped__("  openai/gpt-6-luna  ")

	def test_save_ai_settings_accepts_valid_input_without_returning_key(self):
		settings = frappe._dict({"save": lambda **kwargs: None})
		with (
			patch("crm.api.ai_agent_center.frappe.only_for"),
			patch("crm.api.ai_agent_center.frappe.get_doc", return_value=settings),
			patch.object(frappe.db, "commit"),
		):
			result = save_ai_settings.__wrapped__(DEFAULT_LLM_MODEL, api_key="test-key")
		self.assertEqual(settings.openrouter_api_key, "test-key")
		self.assertEqual(result, {"provider": "OpenRouter", "model": DEFAULT_LLM_MODEL})
