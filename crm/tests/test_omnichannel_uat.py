from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from crm.api.omnichannel import (
	CONVERSATION,
	MESSAGE,
	ROUTING_RULE,
	SLA_POLICY,
	TEMPLATE,
	bulk_update_conversations,
	create_broadcast,
	evaluate_routing,
	export_archive,
	generate_reply_suggestions,
	get_broadcast_report,
	get_channel_kpis,
	get_conversation,
	get_conversations,
	get_templates,
	recalculate_sla,
	save_template,
	search_archive,
	send_message,
	upsert_inbound_message,
)


class TestOmnichannelUAT(FrappeTestCase):
	def setUp(self):
		if not frappe.db.table_exists(CONVERSATION):
			self.skipTest("Omnichannel doctypes are not migrated")
		if not frappe.db.table_exists("Customer"):
			self.skipTest("Customer doctype is not installed")

	def tearDown(self):
		frappe.db.rollback()

	def make_customer(self):
		customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
		return frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": f"Omni UAT {frappe.generate_hash(length=8)}",
				"customer_type": "Individual",
				"customer_group": customer_group,
				"territory": territory,
			}
		).insert(ignore_permissions=True)

	def test_empty_inbox_returns_no_demo_rows(self):
		with patch("crm.api.omnichannel.frappe.get_all", return_value=[]), patch(
			"crm.api.omnichannel.frappe.db.count", return_value=0
		):
			result = get_conversations()

		self.assertEqual(result["rows"], [])
		self.assertEqual(result["counts"]["all"], 0)

	def test_inbound_message_is_idempotent_and_detail_has_customer_context(self):
		customer = self.make_customer()

		first = upsert_inbound_message(
			channel="WhatsApp",
			content="Saya ingin cek aplikasi kredit",
			provider_message_id="wa-uat-001",
			sender="+628111111",
			recipient="+6221555",
			customer=customer.name,
		)
		second = upsert_inbound_message(
			channel="WhatsApp",
			content="Saya ingin cek aplikasi kredit",
			provider_message_id="wa-uat-001",
			sender="+628111111",
			recipient="+6221555",
			customer=customer.name,
		)
		detail = get_conversation(first["conversation"])

		self.assertEqual(first["status"], "Created")
		self.assertEqual(second["status"], "Duplicate")
		self.assertEqual(frappe.db.count(MESSAGE, {"conversation": first["conversation"]}), 1)
		self.assertEqual(detail["conversation"]["customer"], customer.name)
		self.assertIn("customer_context", detail)
		self.assertEqual(detail["conversation"]["unread_count"], 1)

	def test_send_without_provider_stores_provider_not_configured(self):
		customer = self.make_customer()
		inbound = upsert_inbound_message(
			channel="SMS",
			content="Need help",
			provider_message_id="sms-uat-001",
			sender="+628122222",
			customer=customer.name,
		)

		result = send_message(inbound["conversation"], content="Kami bantu cek.")

		self.assertEqual(result["status"], "Provider Not Configured")
		self.assertTrue(
			frappe.db.exists(
				MESSAGE,
				{"conversation": inbound["conversation"], "direction": "Outbound", "status": "Provider Not Configured"},
			)
		)

	def test_template_routing_sla_bulk_archive_and_analytics(self):
		customer = self.make_customer()
		frappe.get_doc(
			{
				"doctype": ROUTING_RULE,
				"rule_name": f"UAT Routing {frappe.generate_hash(length=6)}",
				"enabled": 1,
				"priority": 1,
				"channel": "Email",
				"keyword": "limit",
				"assign_to": frappe.session.user,
				"assign_team": "Credit RM",
			}
		).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": SLA_POLICY,
				"policy_name": f"UAT SLA {frappe.generate_hash(length=6)}",
				"enabled": 1,
				"channel": "Email",
				"first_response_minutes": 1,
			}
		).insert(ignore_permissions=True)
		save_template(
			{
				"template_code": f"uat-template-{frappe.generate_hash(length=6)}",
				"template_name": "UAT Follow Up",
				"channel": "Email",
				"body": "Dear {{customer_name}}, kami bantu cek.",
				"is_active": 1,
			}
		)
		inbound = upsert_inbound_message(
			channel="Email",
			subject="Mohon cek limit",
			content="limit saya belum update",
			provider_message_id="email-uat-001",
			sender="customer@example.com",
			customer=customer.name,
		)

		route = evaluate_routing(inbound["conversation"])
		sla = recalculate_sla(inbound["conversation"])
		bulk = bulk_update_conversations([inbound["conversation"]], "tag", "Priority")
		templates = get_templates(channel="Email")
		archive = bulk_update_conversations([inbound["conversation"]], "archive")
		archives = search_archive({"conversation": inbound["conversation"]})
		export = export_archive({"conversation": inbound["conversation"]})
		kpis = get_channel_kpis()

		self.assertEqual(route["status"], "Matched")
		self.assertEqual(route["assigned_to"], frappe.session.user)
		self.assertIn("status", sla)
		self.assertEqual(bulk["updated"], [inbound["conversation"]])
		self.assertTrue(any(row["channel"] == "Email" for row in templates))
		self.assertEqual(archive["updated"], [inbound["conversation"]])
		self.assertEqual(len(archives), 1)
		self.assertEqual(export["status"], "Exported")
		self.assertTrue(any(row["channel"] == "Email" for row in kpis))

	def test_ai_suggestions_and_broadcast_report(self):
		customer = self.make_customer()
		inbound = upsert_inbound_message(
			channel="In-App",
			content="Bisa bantu follow up dokumen?",
			provider_message_id="chat-uat-001",
			customer=customer.name,
		)

		with patch("crm.api.ai_agent_center.query_agent", return_value={"response": "1. Baik, kami cek dokumen.\n2. Mohon kirim file terbaru.\n3. Kami eskalasi ke RM."}):
			suggestions = generate_reply_suggestions(inbound["conversation"], tone="Formal")

		broadcast = create_broadcast(
			{
				"campaign_name": "UAT Broadcast",
				"channel": "WhatsApp",
				"recipients": [{"customer": customer.name, "recipient": "+628133333"}],
			}
		)
		report = get_broadcast_report(broadcast["campaign"])

		self.assertEqual(suggestions["status"], "Generated")
		self.assertEqual(len(suggestions["suggestions"]), 3)
		self.assertEqual(report["counts"]["Queued"], 1)
