import frappe
from frappe.tests.utils import FrappeTestCase

from crm.api.lead_management import (
	bulk_tag_leads,
	capture_lead,
	get_lead_funnel,
	preview_duplicates,
	reassign_leads,
	score_lead,
)


class TestLeadManagementUAT(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def setUp(self):
		self.ensure_statuses()
		self.ensure_lost_reason()
		self.suffix = frappe.generate_hash(length=8)
		self.phone_suffix = "".join(str(ord(char) % 10) for char in self.suffix)

	def ensure_statuses(self):
		for status, status_type, position in (
			("New", "Open", 1),
			("Qualified", "Won", 2),
			("Lost", "Lost", 3),
		):
			if not frappe.db.exists("CRM Lead Status", status):
				frappe.get_doc(
					{
						"doctype": "CRM Lead Status",
						"lead_status": status,
						"type": status_type,
						"position": position,
					}
				).insert(ignore_permissions=True)

	def ensure_lost_reason(self):
		if not frappe.db.exists("CRM Lost Reason", "Other"):
			frappe.get_doc({"doctype": "CRM Lost Reason", "lost_reason": "Other"}).insert(
				ignore_permissions=True
			)

	def test_capture_scores_routes_and_blocks_exact_duplicate(self):
		result = capture_lead(
			{
				"lead_name": "UAT Capture Lead",
				"email": f"uat.capture.{self.suffix}@example.com",
				"mobile_no": f"+62812{self.phone_suffix}",
				"organization": f"UAT Capture Org {self.suffix}",
				"campaign": None,
				"source": "Web Form",
				"npwp": f"12.345.{self.phone_suffix[:3]}.{self.phone_suffix[3:6]}",
			},
			channel="Web Form",
		)

		self.assertTrue(result["created"])
		lead = frappe.get_doc("CRM Lead", result["lead"])
		self.assertEqual(lead.capture_channel, "Web Form")
		self.assertEqual(lead.source, "Web Form")
		self.assertGreaterEqual(lead.lead_score, 40)
		self.assertTrue(lead.lead_score_band)
		self.assertTrue(lead.lead_owner)
		self.assertTrue(lead.first_assigned_on)

		duplicate = capture_lead(
			{
				"lead_name": "UAT Capture Lead Duplicate",
				"email": f"uat.capture.{self.suffix}@example.com",
			},
			channel="Web Form",
		)
		self.assertFalse(duplicate["created"])
		self.assertEqual(duplicate["duplicate"]["name"], lead.name)

	def test_duplicate_preview_bulk_tag_reassign_and_funnel(self):
		first = capture_lead(
			{
				"lead_name": "UAT Funnel Lead",
				"email": f"uat.funnel.{self.suffix}@example.com",
				"mobile_no": f"+62813{self.phone_suffix}",
				"organization": f"UAT Funnel Org {self.suffix}",
				"source": "Referral",
			},
			channel="Referral",
		)["lead"]
		second = capture_lead(
			{
				"lead_name": "UAT Funnel Similar",
				"mobile_no": f"+62814{self.phone_suffix}",
				"organization": f"UAT Funnel Org {self.suffix}",
				"source": "Referral",
			},
			channel="Referral",
			allow_duplicate=True,
		)["lead"]

		duplicates = preview_duplicates(lead=second)
		self.assertTrue(any(row["name"] == first for row in duplicates))

		tag_result = bulk_tag_leads([first, second], "UAT Priority", "#0f766e")
		self.assertEqual(tag_result["updated"], 2)

		with self.assertRaises(frappe.ValidationError):
			reassign_leads([first], "Administrator", "")

		reassign_result = reassign_leads([first, second], "Administrator", "UAT workload balancing")
		self.assertEqual(reassign_result["updated"], 2)
		self.assertEqual(frappe.db.get_value("CRM Lead", first, "lead_owner"), "Administrator")
		self.assertTrue(frappe.db.exists("CRM Lead Assignment Log", {"lead": first}))

		score = score_lead(first)
		self.assertIn(score["band"], ["Cold", "Warm", "Hot"])

		funnel = get_lead_funnel()
		self.assertGreaterEqual(funnel["total"], 2)
		self.assertIn("conversion_rate", funnel)

	def test_lead_status_change_log_uses_lead_status_type(self):
		lead = frappe.get_doc(
			{
				"doctype": "CRM Lead",
				"first_name": "UAT Status",
				"email": f"uat.status.{self.suffix}@example.com",
				"status": "New",
			}
		)
		lead.insert(ignore_permissions=True)
		lead.status = "Lost"
		lead.lost_reason = "Other"
		lead.lost_notes = "UAT drop-off"
		lead.save(ignore_permissions=True)

		lead.reload()
		self.assertTrue(lead.dropped_off_on)
		self.assertEqual(lead.status_change_log[-2].to_type, "Lost")
