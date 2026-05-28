import frappe
from frappe.tests.utils import FrappeTestCase

from crm.api.lead_management import (
	_choose_assignment_user,
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
		# Ensure no active scoring model (handles stale models from prior runs)
		for row in frappe.get_all("CRM Lead Scoring Model", {"is_active": 1}):
			frappe.db.set_value("CRM Lead Scoring Model", row["name"], "is_active", 0)
		self.suffix = frappe.generate_hash(length=8)
		self.phone_suffix = "".join(str(ord(char) % 10) for char in self.suffix)

	def ensure_statuses(self):
		for status, status_type, position in (
			("New", "Open", 1),
			("Contacted", "Ongoing", 2),
			("Nurture", "Ongoing", 3),
			("Qualified", "Won", 4),
			("Converted", "Won", 5),
			("Unqualified", "Lost", 6),
			("Junk", "Lost", 7),
			("Lost", "Lost", 8),
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

	def _ensure_scoring_model(self):
		"""Create an active scoring model so scores are non-zero."""
		model_name = "UAT Test Model"
		model = None
		if frappe.db.exists("CRM Lead Scoring Model", model_name):
			model = frappe.get_doc("CRM Lead Scoring Model", model_name)
			if not model.is_active:
				model.is_active = 1
				model.save(ignore_permissions=True)
		else:
			model = frappe.get_doc(
				{
					"doctype": "CRM Lead Scoring Model",
					"model_name": model_name,
					"is_active": 1,
					"rules": [
						{"fieldname": "email", "operator": "is set", "weight": 40},
						{"fieldname": "mobile_no", "operator": "is set", "weight": 40},
						{"fieldname": "organization", "operator": "is set", "weight": 20},
					],
				}
			).insert(ignore_permissions=True)
		return model_name

	def test_scoring_returns_zero_and_unscored_without_active_model(self):
		result = capture_lead(
			{
				"lead_name": "UAT No Model Lead",
				"email": f"uat.nomodel.{self.suffix}@example.com",
				"mobile_no": f"+62815{self.phone_suffix}",
				"organization": f"UAT No Model Org {self.suffix}",
			},
			channel="Web Form",
		)
		self.assertTrue(result["created"])
		lead = frappe.get_doc("CRM Lead", result["lead"])
		self.assertEqual(lead.lead_score, 0)
		self.assertEqual(lead.lead_score_band, "")
		self.assertEqual(lead.lead_quality_confidence, 0)
		self.assertTrue(lead.lead_owner)

	def test_capture_scores_routes_and_blocks_exact_duplicate(self):
		self._ensure_scoring_model()
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
		self.assertIn(lead.lead_score_band, ["Cold", "Warm", "Hot"])
		self.assertEqual(lead.lead_quality_confidence, 85)
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
		self._ensure_scoring_model()
		shared_email = f"uat.funnel.{self.suffix}@example.com"
		first = capture_lead(
			{
				"lead_name": "UAT Funnel Lead",
				"email": shared_email,
				"mobile_no": f"+62813{self.phone_suffix}",
				"organization": f"UAT Funnel Org {self.suffix}",
				"source": "Referral",
			},
			channel="Referral",
		)["lead"]
		second = capture_lead(
			{
				"lead_name": "UAT Funnel Similar",
				"email": shared_email,
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
		self.assertEqual(score["confidence"], 85)

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

	def test_unscored_lead_without_model_unchanged_by_score_lead(self):
		lead = frappe.get_doc(
			{
				"doctype": "CRM Lead",
				"first_name": "UAT Unscored",
				"email": f"uat.unscored.{self.suffix}@example.com",
				"organization": f"UAT Unscored Org {self.suffix}",
				"status": "New",
			}
		)
		lead.insert(ignore_permissions=True)
		score = score_lead(lead.name)
		self.assertEqual(score["score"], 0)
		self.assertEqual(score["band"], "")
		self.assertEqual(score["confidence"], 0)

	def test_nine_stage_lifecycle_enforces_forward_progression(self):
		lead = frappe.get_doc(
			{
				"doctype": "CRM Lead",
				"first_name": "UAT Lifecycle",
				"email": f"uat.lifecycle.{self.suffix}@example.com",
				"organization": f"UAT Lifecycle Org {self.suffix}",
				"status": "New",
			}
		)
		lead.insert(ignore_permissions=True)

		# Can move forward: New (Open) → Contacted (Ongoing)
		lead.status = "Contacted"
		lead.save(ignore_permissions=True)
		self.assertEqual(lead.status, "Contacted")

		# Can move forward: Contacted (Ongoing) → Nurture (Ongoing) — same type, allowed
		lead.status = "Nurture"
		lead.save(ignore_permissions=True)
		self.assertEqual(lead.status, "Nurture")

		# Cannot move backward: Nurture (Ongoing) → New (Open)
		lead.status = "New"
		with self.assertRaises(frappe.ValidationError):
			lead.save(ignore_permissions=True)
		lead.reload()

	def test_nine_stage_lifecycle_allows_transition_to_terminal_states(self):
		lead = frappe.get_doc(
			{
				"doctype": "CRM Lead",
				"first_name": "UAT Terminal",
				"email": f"uat.terminal.{self.suffix}@example.com",
				"organization": f"UAT Terminal Org {self.suffix}",
				"status": "New",
			}
		)
		lead.insert(ignore_permissions=True)

		# Can move from Open to Lost (terminal)
		lead.lost_reason = "Other"
		lead.lost_notes = "UAT lifecycle test"
		lead.status = "Unqualified"
		lead.save(ignore_permissions=True)
		self.assertEqual(lead.status, "Unqualified")

		# Cannot leave Lost terminal state
		lead.status = "New"
		with self.assertRaises(frappe.ValidationError):
			lead.save(ignore_permissions=True)

	def test_duplicate_of_set_on_allowed_duplicate(self):
		self._ensure_scoring_model()
		email = f"uat.dupof.{self.suffix}@example.com"
		first = capture_lead(
			{
				"lead_name": "UAT DupOf First",
				"email": email,
				"mobile_no": f"+62815{self.phone_suffix}",
				"organization": f"UAT DupOf Org {self.suffix}",
			},
			channel="Web Form",
		)
		self.assertTrue(first["created"])

		second = capture_lead(
			{
				"lead_name": "UAT DupOf Second",
				"email": email,
				"mobile_no": f"+62816{self.phone_suffix}",
				"organization": f"UAT DupOf Org {self.suffix}",
			},
			channel="Web Form",
			allow_duplicate=True,
		)
		self.assertTrue(second["created"])
		lead = frappe.get_doc("CRM Lead", second["lead"])
		self.assertEqual(lead.duplicate_of, first["lead"])
		self.assertGreaterEqual(lead.duplicate_score, 70)

	def test_nine_stage_lifecycle_prevents_skipping_types(self):
		lead = frappe.get_doc(
			{
				"doctype": "CRM Lead",
				"first_name": "UAT Skip",
				"email": f"uat.skip.{self.suffix}@example.com",
				"organization": f"UAT Skip Org {self.suffix}",
				"status": "New",
			}
		)
		lead.insert(ignore_permissions=True)

		# Cannot skip from Open directly to Won (must go through Ongoing)
		lead.status = "Qualified"
		with self.assertRaises(frappe.ValidationError):
			lead.save(ignore_permissions=True)
		lead.reload()
		self.assertEqual(lead.status, "New")

		# Valid progression: New → Contacted → Qualified (Won)
		lead.status = "Contacted"
		lead.save(ignore_permissions=True)
		lead.status = "Qualified"
		lead.save(ignore_permissions=True)
		self.assertEqual(lead.status, "Qualified")

	def test_assignment_fairness_picks_user_with_fewest_leads(self):
		fair_user = "fair_test_user_a@example.com"
		loaded_user = "fair_test_user_b@example.com"
		for idx, user_email in enumerate((fair_user, loaded_user)):
			if not frappe.db.exists("User", user_email):
				frappe.get_doc(
					{
						"doctype": "User",
						"email": user_email,
						"first_name": f"Fairness Test {chr(65 + idx)}",
						"send_welcome_email": 0,
						"roles": [{"role": "Sales User"}],
					}
				).insert(ignore_permissions=True)

		frappe.db.delete("CRM Lead", {"lead_owner": ["in", [fair_user, loaded_user]]})

		for i in range(3):
			frappe.get_doc(
				{
					"doctype": "CRM Lead",
					"first_name": f"Bulk Load {i}",
					"email": f"bulk.{i}.{self.suffix}@example.com",
					"organization": f"Bulk Org {self.suffix}",
					"status": "New",
					"lead_owner": loaded_user,
				}
			).insert(ignore_permissions=True)

		chosen = _choose_assignment_user({"lead_owner": None})
		self.assertEqual(chosen, fair_user)

		frappe.db.delete("CRM Lead", {"lead_owner": loaded_user})
