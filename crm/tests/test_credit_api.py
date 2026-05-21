import frappe
from unittest import TestCase

from crm.api.credit import (
	create_or_update_customer360_record,
	export_customer_profile,
	global_customer_search,
	get_customer_360,
	get_customer_360_table,
	get_credit_analysis_table,
	get_credit_application_queue,
	merge_customers,
	refresh_public_company_snapshot,
	save_customer_summary,
)


class TestCreditAPI(TestCase):
	def tearDown(self):
		frappe.db.rollback()

	def setUp(self):
		if not frappe.db.table_exists("Customer"):
			self.skipTest("Customer doctype is not installed")
		if not frappe.db.table_exists("CRM Credit Application"):
			self.skipTest("Credit doctypes are not migrated")

	def make_customer(self):
		customer_name = frappe.generate_hash(length=8)
		customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
		return frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": f"Credit API {customer_name}",
				"customer_type": "Individual",
				"customer_group": customer_group,
				"territory": territory,
			}
		).insert(ignore_permissions=True)

	def test_public_company_snapshot_fallback_is_cached(self):
		snapshot = refresh_public_company_snapshot("BBCA")

		self.assertEqual(snapshot["ticker"], "BBCA")
		self.assertEqual(snapshot["status"], "Source Unavailable")
		self.assertTrue(frappe.db.exists("CRM Public Company Snapshot", "BBCA"))
		self.assertEqual(snapshot["normalized"]["status"], "source_unavailable")

	def test_credit_queue_and_customer_360_aggregate_records(self):
		customer = self.make_customer()
		frappe.get_doc(
			{
				"doctype": "CRM Credit Application",
				"borrower": customer.name,
				"borrower_type": "Individual",
				"facility_type": "Working Capital",
				"requested_amount": 100000000,
				"status": "In Progress",
				"public_company_ticker": "BBCA",
			}
		).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "CRM Credit Facility",
				"customer": customer.name,
				"facility_type": "Working Capital",
				"outstanding": 25000000,
				"limit_amount": 100000000,
				"health": "KOL-1",
			}
		).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "CRM Bureau Report",
				"customer": customer.name,
				"source": "SLIK/OJK Manual Upload",
				"kol_status": "KOL-1",
				"score": 782,
				"external_exposure": 12000000,
			}
		).insert(ignore_permissions=True)
		frappe.get_doc(
			{
				"doctype": "CRM Task",
				"title": "Follow up customer",
				"reference_doctype": "Customer",
				"reference_docname": customer.name,
				"status": "Todo",
			}
		).insert(ignore_permissions=True)

		queue = get_credit_application_queue()
		table = get_credit_analysis_table(customer.customer_name[:8])
		customer_table = get_customer_360_table(customer.customer_name[:8])
		customer_360 = get_customer_360(customer.name)

		self.assertTrue(any(row["borrower"] == customer.name for row in queue))
		self.assertTrue(any(row["borrower"] == customer.name for row in table))
		self.assertTrue(any(row["name"] == customer.name for row in customer_table))
		self.assertEqual(customer_360["summary"]["total_outstanding"], 25000000)
		self.assertEqual(customer_360["summary"]["risk_grade"], "KOL-1")
		self.assertEqual(len(customer_360["tasks"]), 1)

	def test_customer_360_new_uat_records_are_aggregated(self):
		customer = self.make_customer()
		create_or_update_customer360_record(
			"CRM KYC Review",
			{
				"customer": customer.name,
				"status": "Verified",
				"npwp": "123456789012345",
				"nik": "1234567890123456",
				"watchlist": 1,
				"watchlist_reason": "UAT risk review",
			},
		)
		create_or_update_customer360_record(
			"CRM Relationship",
			{
				"customer": customer.name,
				"related_party": "UAT Owner",
				"relationship_type": "Shareholder",
				"ownership_percent": 100,
				"is_ubo": 1,
			},
		)
		for doctype, doc in {
			"CRM Bank Account": {"bank": "BNI", "account_number": "123", "verification_status": "Verified"},
			"CRM Customer Document": {"title": "KTP", "document_type": "KYC", "expiry_status": "Valid"},
			"CRM Customer Communication": {"subject": "Follow up", "channel": "Email"},
			"CRM Transaction History": {"transaction_type": "Repayment", "amount": 5000},
			"CRM Risk Profile": {"risk_grade": "B+", "internal_score": 780},
			"CRM AI Insight": {"title": "Payroll cross-sell", "insight_type": "Cross-sell", "confidence_score": 80},
			"CRM Customer Tag": {"tag": "Priority", "color": "#0f766e"},
		}.items():
			doc["customer"] = customer.name
			create_or_update_customer360_record(doctype, doc)

		save_customer_summary(customer.name, "- UAT summary")
		profile = get_customer_360(customer.name)

		self.assertEqual(profile["summary"]["kyc_status"], "Verified")
		self.assertTrue(profile["summary"]["watchlist"])
		self.assertTrue(profile["summary"]["shareholder_balanced"])
		self.assertEqual(len(profile["bank_accounts"]), 1)
		self.assertEqual(len(profile["documents"]), 1)
		self.assertEqual(len(profile["communications"]), 1)
		self.assertEqual(len(profile["transactions"]), 1)
		self.assertEqual(profile["summary"]["risk_grade"], "B+")
		self.assertEqual(len(profile["ai_insights"]), 1)
		self.assertEqual(len(profile["tags"]), 1)

	def test_customer_360_validation_search_export_and_merge_preview(self):
		customer = self.make_customer()
		target = self.make_customer()

		with self.assertRaises(frappe.ValidationError):
			create_or_update_customer360_record(
				"CRM KYC Review",
				{"customer": customer.name, "nik": "123", "npwp": "123456789012345"},
			)

		create_or_update_customer360_record(
			"CRM KYC Review",
			{"customer": customer.name, "nik": "1234567890123456", "npwp": "123456789012345"},
		)

		results = global_customer_search(customer.customer_name[:8])
		self.assertTrue(any(row["name"] == customer.name for row in results))

		export = export_customer_profile(customer.name, scope="Full Profile", watermark="UAT", password="secret")
		self.assertEqual(export["customer"], customer.name)
		self.assertIn("password_protected", export.get("notes", ""))

		merge = merge_customers(customer.name, target.name, field_map={"customer_name": "target"}, confirm=0)
		self.assertEqual(merge["status"], "Preview")
