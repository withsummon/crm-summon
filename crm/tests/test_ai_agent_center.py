import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe
import requests

from crm.ai.kimi import DEFAULT_KIMI_MODEL, MAX_RETRIES, _request_with_retry, call_kimi_chat, normalize_kimi_model, stream_kimi_chat_events
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
		settings = frappe._dict({"kimi_model": DEFAULT_KIMI_MODEL})
		fake_frappe = SimpleNamespace(db=SimpleNamespace(sql=lambda *args, **kwargs: [[0]]), utils=SimpleNamespace(today=lambda: "2026-05-24"))
		with patch("crm.api.ai_agent_center.ensure_ai_tables"), patch("crm.api.ai_agent_center.get_ai_settings", return_value=settings), patch("crm.api.ai_agent_center.frappe", fake_frappe):
			self.assertEqual(len(get_agents.__wrapped__()), 10)

	def test_kimi_client_uses_kimi_26_chat_completion_payload(self):
		class Response:
			status_code = 200
			text = "{}"

			def json(self):
				return {
					"model": DEFAULT_KIMI_MODEL,
					"choices": [{"message": {"content": "ok"}}],
					"usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3},
				}

		settings = frappe._dict(
			{
				"kimi_api_key": "test-key",
				"kimi_base_url": "https://api.moonshot.ai/v1",
				"kimi_model": DEFAULT_KIMI_MODEL,
				"thinking_mode": "disabled",
			}
		)

		with patch("crm.ai.kimi.get_ai_settings", return_value=settings), patch("crm.ai.kimi._request_with_retry", return_value=Response()) as req:
			result = call_kimi_chat([{"role": "user", "content": "hello"}])

		self.assertEqual(result.content, "ok")
		payload = json.loads(req.call_args.kwargs["data"])
		self.assertEqual(payload["model"], DEFAULT_KIMI_MODEL)
		self.assertEqual(payload["thinking"], {"type": "disabled"})
		self.assertEqual(req.call_args.args[1], "https://api.moonshot.ai/v1/chat/completions")

	def test_legacy_kimi_model_alias_maps_to_kimi_26(self):
		self.assertEqual(normalize_kimi_model("kimi-k2"), DEFAULT_KIMI_MODEL)
		self.assertEqual(normalize_kimi_model("kimi-k2-latest"), DEFAULT_KIMI_MODEL)

	def test_kimi_client_streams_delta_events(self):
		class Response:
			status_code = 200
			text = ""

			def iter_lines(self, decode_unicode=True):
				yield 'data: {"model":"kimi-k2.6","choices":[{"delta":{"content":"hel"}}]}'
				yield 'data: {"model":"kimi-k2.6","choices":[{"delta":{"content":"lo"}}],"usage":{"total_tokens":4}}'
				yield "data: [DONE]"

		settings = frappe._dict(
			{
				"kimi_api_key": "test-key",
				"kimi_base_url": "https://api.moonshot.ai/v1",
				"kimi_model": DEFAULT_KIMI_MODEL,
				"thinking_mode": "disabled",
			}
		)

		with patch("crm.ai.kimi.get_ai_settings", return_value=settings), patch("crm.ai.kimi._request_with_retry", return_value=Response()) as req:
			events = list(stream_kimi_chat_events([{"role": "user", "content": "hello"}]))

		self.assertEqual("".join(event.delta for event in events if event.event == "delta"), "hello")
		self.assertEqual(events[-1].event, "done")
		self.assertEqual(events[-1].total_tokens, 4)
		self.assertTrue(json.loads(req.call_args.kwargs["data"])["stream"])

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
			frappe._dict({"event": "delta", "delta": '{"title":"Analisis Portofolio","executive_summary":"Risiko utama terkendali.","confidence":0.9,"sections":[{"title":"Ringkasan Portofolio","summary":"Tidak ada breach mayor."}],"actions":[]}', "model": DEFAULT_KIMI_MODEL}),
			frappe._dict({"event": "done", "model": DEFAULT_KIMI_MODEL, "total_tokens": 11, "cost": 0}),
		]

		with (
			patch("crm.api.ai_agent_center._save_session", return_value="AI-SESSION-001"),
			patch("crm.api.ai_agent_center._save_message", return_value="AI-MSG-001"),
			patch("crm.api.ai_agent_center.query_rag", return_value=rag_response),
			patch("crm.api.ai_agent_center.get_ai_settings", return_value=frappe._dict({"kimi_model": DEFAULT_KIMI_MODEL, "thinking_mode": "disabled"})),
			patch("crm.api.ai_agent_center.stream_kimi_chat_events", return_value=iter(stream_events)),
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
				"model": DEFAULT_KIMI_MODEL,
				"total_tokens": 7,
				"cost": 0,
			}
		)

		try:
			with (
				patch("crm.api.ai_agent_center.query_rag", return_value=rag_response),
				patch("crm.api.ai_agent_center.get_ai_settings", return_value=frappe._dict({"kimi_model": DEFAULT_KIMI_MODEL, "thinking_mode": "disabled"})),
				patch("crm.api.ai_agent_center.call_kimi_chat", return_value=kimi_response),
				patch.object(frappe.db, "sql_ddl", side_effect=AssertionError("DDL should not run during chat when tables exist")),
			):
				response = query_agent.__wrapped__("credit_analyst", "summarize the application")
			created_session = response["session_id"]
			self.assertIn("Grounded answer", response["response"])
			self.assertEqual(response["structured_response"]["title"], "Output AI perlu divalidasi")
			self.assertEqual(response["structured_response"]["agent_key"], "credit_analyst")
			self.assertTrue(response["structured_response"]["limitations"])
			self.assertEqual(response["model"], DEFAULT_KIMI_MODEL)
			self.assertEqual(response["confidence"], 0.9)
		finally:
			if created_session:
				for table in ("CRM AI Action Log", "CRM AI Message"):
					frappe.db.sql(f"DELETE FROM `tab{table}` WHERE session=%s", (created_session,))
				frappe.db.sql("DELETE FROM `tabCRM AI Audit Log` WHERE prompt=%s", ("summarize the application",))
				frappe.db.sql("DELETE FROM `tabCRM AI Session` WHERE name=%s", (created_session,))
				frappe.db.commit()

	def test_request_with_retry_succeeds_on_first_attempt(self):
		class Response:
			status_code = 200
			text = "ok"

		with patch("crm.ai.kimi.requests.Session.request", return_value=Response()) as req:
			result = _request_with_retry("POST", "https://example.com/api", headers={}, data="{}", timeout=10)

		self.assertEqual(result.status_code, 200)
		req.assert_called_once()

	def test_request_with_retry_fails_after_max_retries(self):
		class Response:
			status_code = 503
			text = "Service Unavailable"

		responses = [Response() for _ in range(MAX_RETRIES + 1)]
		call_count = [0]

		def side_effect(*args, **kwargs):
			call_count[0] += 1
			return responses[call_count[0] - 1]

		with (
			patch("crm.ai.kimi.requests.Session.request", side_effect=side_effect),
			patch("crm.ai.kimi.frappe.log_error"),
			patch("crm.ai.kimi.time.sleep"),
		):
			result = _request_with_retry("POST", "https://example.com/api", headers={}, data="{}", timeout=10)

		self.assertEqual(result.status_code, 503)
		self.assertEqual(call_count[0], MAX_RETRIES + 1)

	def test_request_with_retry_raises_on_connection_error(self):
		def side_effect(*args, **kwargs):
			raise requests.ConnectionError("Connection refused")

		with (
			patch("crm.ai.kimi.requests.Session.request", side_effect=side_effect),
			patch("crm.ai.kimi.frappe.log_error"),
			patch("crm.ai.kimi.time.sleep"),
		):
			with self.assertRaises(frappe.ValidationError) as ctx:
				_request_with_retry("POST", "https://example.com/api", headers={}, data="{}", timeout=10)

		self.assertIn("Connection refused", str(ctx.exception))

	def test_save_ai_settings_rejects_empty_model(self):
		with self.assertRaises(frappe.ValidationError) as ctx:
			save_ai_settings.__wrapped__("Kimi", "")
		self.assertIn("cannot be empty", str(ctx.exception).lower())

	def test_save_ai_settings_rejects_whitespace_model(self):
		with self.assertRaises(frappe.ValidationError) as ctx:
			save_ai_settings.__wrapped__("Kimi", "  kimi-k2.6  ")
		self.assertIn("whitespace", str(ctx.exception).lower())

	def test_save_ai_settings_rejects_invalid_provider(self):
		with self.assertRaises(frappe.ValidationError) as ctx:
			save_ai_settings.__wrapped__("InvalidProvider", "kimi-k2.6")
		self.assertIn("invalid", str(ctx.exception).lower())

	def test_save_ai_settings_accepts_valid_input(self):
		settings = frappe._dict({"ai_provider": "Kimi", "kimi_model": DEFAULT_KIMI_MODEL, "kimi_base_url": "https://api.moonshot.ai/v1", "save": lambda **kwargs: None, "as_dict": lambda: settings})

		with (
			patch("crm.api.ai_agent_center.frappe.get_doc", return_value=settings),
			patch.object(frappe.db, "commit"),
		):
			result = save_ai_settings.__wrapped__("Kimi", "kimi-k2.6", base_url="https://api.moonshot.ai/v1")
			self.assertEqual(result["kimi_model"], DEFAULT_KIMI_MODEL)
