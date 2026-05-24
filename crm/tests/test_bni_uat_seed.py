import frappe
from unittest import TestCase

from crm.demo.bni_uat import clear_bni_uat_seed, create_bni_uat_seed


class TestBNIUATSeed(TestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_seed_create_and_clear(self):
		if not frappe.db.table_exists("Customer"):
			self.skipTest("Customer doctype is not installed")
		if not frappe.db.table_exists("CRM Lead"):
			self.skipTest("CRM Lead doctype is not installed")

		frappe.set_user("Administrator")
		created = create_bni_uat_seed()

		self.assertIn("records", created)
		self.assertGreaterEqual(created.get("customers_seeded", 0), 1)

		already_seeded = create_bni_uat_seed()
		self.assertEqual(already_seeded.get("status"), "already_seeded")

		cleared = clear_bni_uat_seed()
		self.assertTrue(cleared.get("cleared"))
