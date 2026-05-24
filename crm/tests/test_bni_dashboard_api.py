import frappe
from unittest import TestCase

from crm.api.dashboard import get_bni_crm_dashboard


class TestBNIDashboardAPI(TestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_bni_dashboard_payload_is_zero_safe(self):
		payload = get_bni_crm_dashboard("2026-01-01", "2026-01-31")

		self.assertIn("metrics", payload)
		self.assertEqual(len(payload["metrics"]), 4)
		self.assertIn("revenue", payload)
		self.assertIn("months", payload["revenue"])
		self.assertIn("calendar", payload)
		self.assertIn("lead_management", payload)
		self.assertIn("lead_gen", payload)
		self.assertIn("regions", payload)
		self.assertIn("top_branches", payload)
		self.assertIn("retention", payload)
		self.assertIn("company_breakdown", payload["lead_gen"])
		self.assertIn("pic_ownership", payload["lead_gen"])
		self.assertIn("follow_up_load", payload["lead_gen"])
