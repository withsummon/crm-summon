import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch

import frappe

from crm.ai.kimi import DEFAULT_KIMI_MODEL, call_kimi_chat
from crm.api.ai_agent_center import AGENTS, ensure_ai_tables, get_agents, query_agent


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

		with patch("crm.ai.kimi.get_ai_settings", return_value=settings), patch("crm.ai.kimi.requests.post", return_value=Response()) as post:
			result = call_kimi_chat([{"role": "user", "content": "hello"}])

		self.assertEqual(result.content, "ok")
		payload = json.loads(post.call_args.kwargs["data"])
		self.assertEqual(payload["model"], DEFAULT_KIMI_MODEL)
		self.assertEqual(payload["thinking"], {"type": "disabled"})
		self.assertEqual(post.call_args.args[0], "https://api.moonshot.ai/v1/chat/completions")

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
			self.assertEqual(response["response"], "Grounded answer.\n\nSources\n1. Demo CRM customer context")
			self.assertEqual(response["model"], DEFAULT_KIMI_MODEL)
			self.assertEqual(response["confidence"], 0.9)
		finally:
			if created_session:
				for table in ("CRM AI Action Log", "CRM AI Message"):
					frappe.db.sql(f"DELETE FROM `tab{table}` WHERE session=%s", (created_session,))
				frappe.db.sql("DELETE FROM `tabCRM AI Audit Log` WHERE prompt=%s", ("summarize the application",))
				frappe.db.sql("DELETE FROM `tabCRM AI Session` WHERE name=%s", (created_session,))
				frappe.db.commit()
