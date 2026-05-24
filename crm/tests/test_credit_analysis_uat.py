from unittest import TestCase
from unittest.mock import patch

import frappe

from crm.api.credit_analysis import (
	CREDIT_UAT_FEATURES,
	calculate_dscr,
	calculate_ratios,
	create_uat_demo_pack,
	delete_credit_analysis_artifacts,
	export_credit_memo_pdf,
	generate_credit_memo,
	generate_credit_recommendation,
	get_credit_workspace,
	get_uat_proof_pack,
	run_cashflow_projection,
	run_scenario,
	run_sensitivity,
	save_spreading,
	submit_memo_for_approval,
)
from crm.api.credit import create_credit_application


class TestCreditAnalysisUAT(TestCase):
	def setUp(self):
		if not frappe.db.table_exists("Customer"):
			self.skipTest("Customer doctype is not installed")
		if not frappe.db.table_exists("CRM Credit Application"):
			self.skipTest("Credit doctypes are not migrated")
		self.created = {"CRM Credit Application": [], "Customer": [], "CRM Collateral": []}
		self.customer = self._make_customer()
		self.application = frappe.get_doc(
			{
				"doctype": "CRM Credit Application",
				"borrower": self.customer.name,
				"borrower_name": self.customer.customer_name,
				"borrower_type": "Company",
				"status": "In Progress",
				"facility_type": "Working Capital",
				"requested_amount": 5000000000,
				"industry": "Financial Services",
				"kbli": "6419",
				"risk_grade": "B+",
				"purpose": "UAT credit analysis test application.",
			}
		).insert(ignore_permissions=True)
		self.created["CRM Credit Application"].append(self.application.name)
		if frappe.db.table_exists("CRM Collateral"):
			collateral = frappe.get_doc(
				{
					"doctype": "CRM Collateral",
					"customer": self.customer.name,
					"asset": "UAT receivables pledge",
					"collateral_type": "Receivables",
					"collateral_value": 8500000000,
					"ltv_percent": 58,
					"reappraisal_status": "Not Required",
				}
			).insert(ignore_permissions=True)
			self.created["CRM Collateral"].append(collateral.name)

	def tearDown(self):
		try:
			delete_credit_analysis_artifacts(self.created.get("CRM Credit Application", []))
			for doctype in ("CRM Collateral", "CRM Credit Application", "Customer"):
				for name in self.created.get(doctype, []):
					if frappe.db.exists(doctype, name):
						frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()

	def _make_customer(self):
		customer_group = frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
		customer = frappe.get_doc(
			{
				"doctype": "Customer",
				"customer_name": f"Credit Analysis UAT {frappe.generate_hash(length=8)}",
				"customer_type": "Company",
				"customer_group": customer_group,
				"territory": territory,
			}
		).insert(ignore_permissions=True)
		self.created["Customer"].append(customer.name)
		return customer

	def test_uat_proof_pack_covers_every_credit_analysis_excel_feature(self):
		proof = get_uat_proof_pack(scope="credit_analysis", application_id=self.application.name)
		keys = {row["feature_key"] for row in proof["rows"]}

		self.assertEqual(proof["credit_analysis_total"], len(CREDIT_UAT_FEATURES))
		self.assertEqual(len(keys), len(CREDIT_UAT_FEATURES))
		self.assertTrue({feature["key"] for feature in CREDIT_UAT_FEATURES}.issubset(keys))

	def test_spreading_ratios_dscr_scenario_sensitivity_and_cashflow_are_deterministic(self):
		saved = save_spreading(self.application.name, status="Draft")
		workspace = get_credit_workspace(self.application.name)
		ratios = calculate_ratios(self.application.name)
		dscr = calculate_dscr(self.application.name)
		scenario = run_scenario(self.application.name)
		sensitivity = run_sensitivity(self.application.name)
		cashflow = run_cashflow_projection(self.application.name)

		self.assertGreaterEqual(saved["row_count"], 100)
		self.assertTrue(all(row["status"] == "Balanced" for row in workspace["balance_checks"]))
		self.assertTrue(any(row["key"] == "current_ratio" for row in ratios["ratios"]))
		self.assertIn("min_dscr", dscr)
		self.assertEqual(len(scenario["scenarios"]), 3)
		self.assertGreaterEqual(len(sensitivity["matrix"]), 3)
		self.assertEqual(len(cashflow["items"]), 5)

	def test_create_credit_application_initializes_workspace(self):
		payload = {
			"borrower_name": f"BNI UAT Applicant {frappe.generate_hash(length=8)}",
			"borrower_type": "Company",
			"facility_type": "Working Capital",
			"requested_amount": 7500000000,
			"industry": "Financial Services",
			"kbli": "6419",
			"status": "Draft",
			"purpose": "New credit analysis creation flow.",
		}

		application = create_credit_application(payload)
		self.created["CRM Credit Application"].append(application.name)
		self.created["Customer"].append(application.borrower)
		workspace = get_credit_workspace(application.name)

		self.assertEqual(application.borrower_type, "Company")
		self.assertEqual(application.facility_type, "Working Capital")
		self.assertGreaterEqual(len(workspace["spreading"]), 100)
		self.assertGreaterEqual(len(workspace["proof"]), 20)

	def test_ai_memo_recommendation_approval_export_and_demo_proof(self):
		save_spreading(self.application.name, status="Draft")
		fake_response = {
			"response": "AI generated credit memo with sourced recommendation.",
			"sources": [{"title": "Credit Analysis workspace"}],
			"confidence": 0.81,
			"model": "kimi-k2.6",
		}
		with patch("crm.api.ai_agent_center.query_agent", return_value=fake_response):
			memo = generate_credit_memo(self.application.name)
			recommendation = generate_credit_recommendation(self.application.name)
		approval = submit_memo_for_approval(self.application.name)
		export = export_credit_memo_pdf(self.application.name, watermark="BNI UAT")
		demo = create_uat_demo_pack(self.application.name)

		self.assertIn("AI generated credit memo", memo["content"])
		self.assertIn(recommendation["decision"], {"Approve", "Refer", "Reject"})
		self.assertEqual(approval["status"], "Submitted")
		self.assertEqual(export["watermark"], "BNI UAT")
		self.assertEqual(demo["application"], self.application.name)
		self.assertGreaterEqual(demo["proof"]["credit_analysis_total"], 20)
