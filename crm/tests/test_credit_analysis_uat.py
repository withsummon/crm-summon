import os
import zipfile
from unittest import TestCase
from unittest.mock import patch
from xml.sax.saxutils import escape

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
	import_statement_file,
	run_cashflow_projection,
	run_scenario,
	run_sensitivity,
	save_spreading,
	submit_memo_for_approval,
)
from crm.api.credit import create_credit_application, create_or_update_customer360_record


class TestCreditAnalysisUAT(TestCase):
	def setUp(self):
		if not frappe.db.table_exists("Customer"):
			self.skipTest("Customer doctype is not installed")
		if not frappe.db.table_exists("CRM Credit Application"):
			self.skipTest("Credit doctypes are not migrated")
		self.created = {"CRM Credit Application": [], "Customer": [], "CRM Collateral": [], "CRM Task": []}
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
			for doctype in ("CRM Task", "CRM Collateral", "CRM Credit Application", "Customer"):
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

	def _spread_rows(self, years=None):
		years = years or [2021, 2022, 2023, 2024, 2025]
		rows = []
		for idx, year in enumerate(years):
			revenue = 10_000_000_000 + idx * 800_000_000
			cogs = revenue * 0.62
			gross_profit = revenue - cogs
			opex = revenue * 0.16
			ebitda = gross_profit - opex
			interest = 400_000_000
			tax = 250_000_000
			net_income = ebitda - interest - tax
			cash = revenue * 0.12
			receivables = revenue * 0.18
			inventory = cogs * 0.2
			current_assets = cash + receivables + inventory
			current_liabilities = revenue * 0.2
			debt = 3_000_000_000 - idx * 150_000_000
			total_liabilities = current_liabilities + debt
			equity = 6_000_000_000 + idx * 450_000_000
			total_assets = total_liabilities + equity
			payables = cogs * 0.1
			operating_cf = ebitda * 0.8
			capex = revenue * 0.05
			financing_cf = -250_000_000
			period_cf = operating_cf - capex + financing_cf
			ending_cash = cash + period_cf
			values = {
				"revenue": revenue,
				"cogs": cogs,
				"gross_profit": gross_profit,
				"operating_expense": opex,
				"ebitda": ebitda,
				"interest_expense": interest,
				"tax": tax,
				"net_income": net_income,
				"cash": cash,
				"receivables": receivables,
				"inventory": inventory,
				"current_assets": current_assets,
				"total_assets": total_assets,
				"payables": payables,
				"current_liabilities": current_liabilities,
				"debt": debt,
				"total_liabilities": total_liabilities,
				"equity": equity,
				"operating_cf": operating_cf,
				"capex": capex,
				"financing_cf": financing_cf,
				"period_cf": period_cf,
				"ending_cash": ending_cash,
			}
			labels = {
				"P&L": [
					("revenue", "Pendapatan / Sales"),
					("cogs", "Beban Pokok Penjualan"),
					("gross_profit", "Laba Kotor"),
					("operating_expense", "Beban Operasional"),
					("ebitda", "EBITDA"),
					("interest_expense", "Beban Bunga"),
					("tax", "Pajak"),
					("net_income", "Laba Bersih"),
				],
				"Balance Sheet": [
					("cash", "Kas dan Setara Kas"),
					("receivables", "Piutang Usaha"),
					("inventory", "Persediaan"),
					("current_assets", "Aset Lancar"),
					("total_assets", "Total Aset"),
					("payables", "Utang Usaha"),
					("current_liabilities", "Liabilitas Jangka Pendek"),
					("debt", "Pinjaman Berbunga"),
					("total_liabilities", "Total Liabilitas"),
					("equity", "Ekuitas"),
				],
				"Cash Flow": [
					("operating_cf", "Arus Kas Operasi"),
					("capex", "Belanja Modal"),
					("financing_cf", "Arus Kas Pendanaan"),
					("period_cf", "Arus Kas Periode Berjalan"),
					("ending_cash", "Kas Akhir Periode"),
				],
			}
			for statement_type, metrics in labels.items():
				for metric_key, metric_label in metrics:
					rows.append(
						{
							"statement_type": statement_type,
							"metric_key": metric_key,
							"metric_label": metric_label,
							"year": year,
							"amount": values[metric_key],
							"adjusted_amount": values[metric_key],
							"confidence": 1,
							"source": "Test Fixture",
						}
					)
		return rows

	def _write_xlsx(self, filename, rows):
		file_path = frappe.get_site_path("private", "files", filename)
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		headers = ["statement_type", "metric_key", "metric_label", "year", "amount", "adjusted_amount", "notes"]
		data = [headers] + [
			[
				row["statement_type"],
				row["metric_key"],
				row["metric_label"],
				row["year"],
				row["amount"],
				row["adjusted_amount"],
				"fixture",
			]
			for row in rows
		]
		sheet_rows = []
		for row_idx, row in enumerate(data, start=1):
			cells = []
			for col_idx, value in enumerate(row):
				ref = f"{chr(65 + col_idx)}{row_idx}"
				if isinstance(value, (int, float)):
					cells.append(f'<c r="{ref}"><v>{value}</v></c>')
				else:
					cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>')
			sheet_rows.append(f'<row r="{row_idx}">{"".join(cells)}</row>')
		with zipfile.ZipFile(file_path, "w") as archive:
			archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="xml" ContentType="application/xml"/></Types>')
			archive.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>{"".join(sheet_rows)}</sheetData></worksheet>')
		return f"/private/files/{filename}"

	def test_uat_proof_pack_covers_every_credit_analysis_excel_feature(self):
		proof = get_uat_proof_pack(scope="credit_analysis", application_id=self.application.name)
		keys = {row["feature_key"] for row in proof["rows"]}

		self.assertEqual(proof["credit_analysis_total"], len(CREDIT_UAT_FEATURES))
		self.assertEqual(len(keys), len(CREDIT_UAT_FEATURES))
		self.assertTrue({feature["key"] for feature in CREDIT_UAT_FEATURES}.issubset(keys))

	def test_spreading_ratios_dscr_scenario_sensitivity_and_cashflow_are_deterministic(self):
		saved = save_spreading(self.application.name, rows=self._spread_rows(), status="Draft")
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
			"financial_year": 2025,
			"revenue": 5000000000,
			"ebitda": 1000000000,
			"net_profit": 500000000,
			"total_assets": 12000000000,
			"total_liabilities": 8000000000,
			"equity": 4000000000,
			"current_ratio": 1.5,
			"der": 2.0,
		}

		application = create_credit_application(payload)
		self.created["CRM Credit Application"].append(application.name)
		self.created["Customer"].append(application.borrower)
		workspace = get_credit_workspace(application.name)

		self.assertEqual(application.borrower_type, "Company")
		self.assertEqual(application.facility_type, "Working Capital")
		self.assertEqual(len(workspace["spreading"]), 6)
		self.assertGreaterEqual(len(workspace["proof"]), 20)

	def test_create_credit_application_accepts_large_idr_values(self):
		payload = {
			"borrower_name": f"BNI Large Applicant {frappe.generate_hash(length=8)}",
			"borrower_type": "Company",
			"facility_type": "Working Capital",
			"requested_amount": 125000000000,
			"status": "Credit Analysis",
			"financial_year": 2025,
			"revenue": 600000000000,
			"ebitda": 90000000000,
			"net_profit": 42000000000,
			"total_assets": 850000000000,
			"total_liabilities": 510000000000,
			"equity": 340000000000,
		}

		application = create_credit_application(payload)
		self.created["CRM Credit Application"].append(application.name)
		self.created["Customer"].append(application.borrower)

		self.assertIn(application.status, {"Credit Analysis", "In Progress"})
		self.assertEqual(int(application.revenue), payload["revenue"])

	def test_customer360_task_modal_ignores_invalid_optional_assignee(self):
		task = create_or_update_customer360_record(
			"CRM Task",
			{
				"title": "Follow up customer documents",
				"assigned_to": "bni",
				"priority": "Medium",
				"status": "Todo",
				"reference_doctype": "Customer",
				"reference_docname": self.customer.name,
			},
		)

		self.created["CRM Task"].append(task.get("name"))
		self.assertFalse(task.get("assigned_to"))
		self.assertEqual(task.get("reference_docname"), self.customer.name)

	def test_statement_file_import_persists_real_spreading_rows(self):
		file_url = self._write_xlsx(f"credit-analysis-{frappe.generate_hash(length=8)}.xlsx", self._spread_rows([2022, 2023, 2024]))

		result = import_statement_file(self.application.name, file_url)

		self.assertEqual(result["status"], "Imported")
		self.assertEqual(result["import_type"], "xlsx")
		self.assertGreaterEqual(result["row_count"], 60)
		self.assertTrue(result["workspace"]["ratios"])
		self.assertEqual(result["workspace"]["extraction"]["cell_count"], result["row_count"])
		self.assertGreaterEqual(len(result["workspace"]["extraction"]["review_cells"]), 60)
		self.assertTrue(all(row["source"] == file_url for row in result["workspace"]["spreading"]))

	def test_pdf_import_without_ai_config_fails_without_seeded_rows(self):
		file_url = "/private/files/credit-analysis-empty.pdf"
		file_path = frappe.get_site_path("private", "files", "credit-analysis-empty.pdf")
		os.makedirs(os.path.dirname(file_path), exist_ok=True)
		with open(file_path, "wb") as handle:
			handle.write(b"%PDF-1.4\n%%EOF")

		with patch("crm.ai.kimi.get_ai_settings", return_value=frappe._dict({"kimi_api_key": "", "thinking_mode": "disabled"})):
			result = import_statement_file(self.application.name, file_url, file_type="pdf")

		self.assertEqual(result["status"], "Failed")
		self.assertEqual(result["row_count"], 0)
		self.assertEqual(get_credit_workspace(self.application.name)["spreading"], [])

	def test_ai_memo_recommendation_approval_export_and_demo_proof(self):
		save_spreading(self.application.name, rows=self._spread_rows(), status="Draft")
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
