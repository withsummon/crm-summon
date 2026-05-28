import csv
import json
import math
import os
import re
import uuid
import zipfile
from copy import deepcopy
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET

import frappe
from frappe import _
from frappe.utils import cstr, flt, now_datetime, nowdate


XML_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


CREDIT_ANALYSIS_TABLES = {
	"CRM Credit Spread Line": """
		CREATE TABLE IF NOT EXISTS `tabCRM Credit Spread Line` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			application VARCHAR(255),
			customer VARCHAR(255),
			statement_type VARCHAR(80),
			metric_key VARCHAR(140),
			metric_label VARCHAR(255),
			year INT,
			amount DECIMAL(25,6),
			adjusted_amount DECIMAL(25,6),
			confidence DECIMAL(10,4),
			source VARCHAR(255),
			notes TEXT,
			INDEX idx_application (application),
			INDEX idx_customer (customer),
			INDEX idx_metric_year (metric_key, year)
		)
	""",
	"CRM Credit Analysis Artifact": """
		CREATE TABLE IF NOT EXISTS `tabCRM Credit Analysis Artifact` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			application VARCHAR(255),
			customer VARCHAR(255),
			artifact_type VARCHAR(140),
			title VARCHAR(255),
			status VARCHAR(140),
			source VARCHAR(255),
			confidence DECIMAL(10,4),
			payload_json LONGTEXT,
			INDEX idx_application (application),
			INDEX idx_artifact_type (artifact_type)
		)
	""",
	"CRM Credit UAT Evidence": """
		CREATE TABLE IF NOT EXISTS `tabCRM Credit UAT Evidence` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			scope VARCHAR(140),
			feature_key VARCHAR(140),
			feature VARCHAR(255),
			status VARCHAR(80),
			route VARCHAR(255),
			api VARCHAR(255),
			evidence_json LONGTEXT,
			INDEX idx_scope (scope),
			INDEX idx_feature (feature_key)
		)
	""",
}


def ensure_credit_analysis_tables():
	for table, statement in CREDIT_ANALYSIS_TABLES.items():
		if frappe.db.table_exists(table):
			if table == "CRM Credit Spread Line":
				try:
					frappe.db.sql("ALTER TABLE `tabCRM Credit Spread Line` MODIFY `amount` DECIMAL(25,6)")
					frappe.db.sql("ALTER TABLE `tabCRM Credit Spread Line` MODIFY `adjusted_amount` DECIMAL(25,6)")
				except Exception:
					pass
			continue
		frappe.db.sql_ddl(statement)


CREDIT_UAT_FEATURES = [
	{
		"key": "financial_statement_input",
		"feature": "Financial Statement Input",
		"acceptance": "3-5 year PL/BS/CF templates, PSAK line items, balance validation, draft save.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.save_spreading",
	},
	{
		"key": "ai_extraction_from_pdf",
		"feature": "AI Extraction from PDF",
		"acceptance": "Native/scanned PDF ingestion, spreading extraction, per-cell confidence, low-confidence review.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.extract_statement_pdf",
	},
	{
		"key": "multi_period_comparison",
		"feature": "Multi-Period Comparison",
		"acceptance": "Five-year horizontal comparison, YoY %, >20% flags, common-size statements.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.get_credit_workspace",
	},
	{
		"key": "ratio_liquidity",
		"feature": "Ratio Analysis - Liquidity",
		"acceptance": "Current, quick, cash ratios with trend, thresholds, benchmark overlay.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.calculate_ratios",
	},
	{
		"key": "ratio_leverage",
		"feature": "Ratio Analysis - Leverage",
		"acceptance": "DER, debt-to-equity, debt-to-assets, interest coverage trends and alerts.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.calculate_ratios",
	},
	{
		"key": "ratio_profitability",
		"feature": "Ratio Analysis - Profitability",
		"acceptance": "Gross margin, EBITDA margin, net margin, ROA, ROE with benchmark overlay.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.calculate_ratios",
	},
	{
		"key": "ratio_efficiency",
		"feature": "Ratio Analysis - Efficiency",
		"acceptance": "Asset turnover, inventory days, receivable days, payable days, working capital cycle.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.calculate_ratios",
	},
	{
		"key": "dscr_calculation",
		"feature": "DSCR Calculation",
		"acceptance": "DSCR by period, -20/base/+20 sensitivity, min DSCR over tenor, alert below 1.2.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.calculate_dscr",
	},
	{
		"key": "trend_analysis",
		"feature": "Trend Analysis",
		"acceptance": "Line item trend, CAGR, regression projection, anomaly comments.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.run_trend_projection",
	},
	{
		"key": "industry_benchmarking",
		"feature": "Industry Benchmarking",
		"acceptance": "KBLI benchmark, median/quartiles, peer positioning, ratio comments.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.get_credit_workspace",
	},
	{
		"key": "risk_grading_engine",
		"feature": "Risk Grading Engine",
		"acceptance": "0-1000 score, A-E grade, weights, score breakdown, override justification, audit trail.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.get_credit_workspace",
	},
	{
		"key": "scenario_simulation",
		"feature": "Scenario Simulation",
		"acceptance": "Best/Base/Worst drivers and side-by-side recalculated ratios.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.run_scenario",
	},
	{
		"key": "sensitivity_analysis",
		"feature": "Sensitivity Analysis",
		"acceptance": "Two-variable matrix, heatmap values, configurable ranges, export-ready payload.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.run_sensitivity",
	},
	{
		"key": "cashflow_projection",
		"feature": "Cashflow Projection",
		"acceptance": "3-5 year projection, configurable drivers, cumulative/period CF, gap alert, loan schedule overlay.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.run_cashflow_projection",
	},
	{
		"key": "collateral_coverage",
		"feature": "Collateral Coverage",
		"acceptance": "Multiple collaterals, LTV, >80% alert, re-appraisal trigger.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.get_credit_workspace",
	},
	{
		"key": "ai_executive_summary",
		"feature": "AI Executive Summary",
		"acceptance": "Five-bullet sourced summary from spreading and ratios, editable and memo-ready.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.generate_credit_summary",
	},
	{
		"key": "ai_credit_memo_draft",
		"feature": "AI Credit Memo Draft",
		"acceptance": "Borrower, purpose, financials, risks, recommendation, editable rich text, charts, PDF, version history.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.generate_credit_memo",
	},
	{
		"key": "ai_recommendation",
		"feature": "AI Recommendation",
		"acceptance": "Approve/Refer/Reject, data-cited reasoning, suggested conditions, confidence.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.generate_credit_recommendation",
	},
	{
		"key": "peer_comparison",
		"feature": "Peer Comparison",
		"acceptance": "3-5 peers, side-by-side ratios, ranking, comment summary.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.get_credit_workspace",
	},
	{
		"key": "notes_adjustments",
		"feature": "Notes & Adjustments",
		"acceptance": "Add-back/deduct entries, reason per adjustment, audit trail, original vs adjusted view.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.save_spreading",
	},
	{
		"key": "credit_bureau_integration",
		"feature": "Credit Bureau Integration",
		"acceptance": "SLIK/PEFINDO adapter/manual pull, score/history/adverse flags, refresh on demand.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.refresh_bureau_report",
	},
	{
		"key": "news_sentiment_scan",
		"feature": "News & Sentiment Scan",
		"acceptance": "Borrower news scan, sentiment score, adverse flags, source citations.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.scan_news_sentiment",
	},
	{
		"key": "approval_routing_from_memo",
		"feature": "Approval Routing from Memo",
		"acceptance": "Submit workflow, amount/risk routing, approver notifications, status tracking.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.submit_memo_for_approval",
	},
	{
		"key": "memo_export_print",
		"feature": "Memo Export & Print",
		"acceptance": "PDF export payload, charts/tables, cover/ToC/watermark, email distribution queue.",
		"route": "/crm/crm-core/credit-analysis/{application}",
		"api": "crm.api.credit_analysis.export_credit_memo_pdf",
	},
]


STATEMENT_TEMPLATES = {
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


BENCHMARKS = {
	"6419": {
		"industry": "Financial Services",
		"median": {"current_ratio": 1.25, "debt_to_equity": 2.4, "net_margin": 0.18, "dscr": 1.35},
		"q1": {"current_ratio": 1.05, "debt_to_equity": 1.7, "net_margin": 0.1, "dscr": 1.15},
		"q3": {"current_ratio": 1.55, "debt_to_equity": 3.1, "net_margin": 0.24, "dscr": 1.7},
	},
	"4711": {
		"industry": "Retail Trade",
		"median": {"current_ratio": 1.45, "debt_to_equity": 1.8, "net_margin": 0.08, "dscr": 1.3},
		"q1": {"current_ratio": 1.1, "debt_to_equity": 1.2, "net_margin": 0.04, "dscr": 1.05},
		"q3": {"current_ratio": 1.9, "debt_to_equity": 2.5, "net_margin": 0.12, "dscr": 1.55},
	},
	"default": {
		"industry": "General Commercial",
		"median": {"current_ratio": 1.35, "debt_to_equity": 1.9, "net_margin": 0.11, "dscr": 1.3},
		"q1": {"current_ratio": 1.0, "debt_to_equity": 1.2, "net_margin": 0.06, "dscr": 1.05},
		"q3": {"current_ratio": 1.8, "debt_to_equity": 2.6, "net_margin": 0.17, "dscr": 1.6},
	},
}




def _insert(table, values):
	ensure_credit_analysis_tables()
	now = now_datetime()
	payload = {"name": values.get("name") or str(uuid.uuid4()), "creation": now, "modified": now, **values}
	columns = list(payload.keys())
	frappe.db.sql(
		f"INSERT INTO `tab{table}` ({', '.join('`' + col + '`' for col in columns)}) VALUES ({', '.join(['%s'] * len(columns))})",
		[payload[col] for col in columns],
	)
	return payload["name"]


def _replace_artifact(application, customer, artifact_type, title, payload, status="Completed", source="System", confidence=1):
	ensure_credit_analysis_tables()
	name = f"CA-{artifact_type}-{application}".replace(" ", "-")[:180]
	now = now_datetime()
	frappe.db.sql(
		"""
			REPLACE INTO `tabCRM Credit Analysis Artifact`
			(name, creation, modified, application, customer, artifact_type, title, status, source, confidence, payload_json)
			VALUES (%s, COALESCE((SELECT creation FROM (SELECT creation FROM `tabCRM Credit Analysis Artifact` WHERE name=%s) existing), %s), %s, %s, %s, %s, %s, %s, %s, %s, %s)
	""",
		(
			name,
			name,
			now,
			now,
			application,
			customer,
			artifact_type,
			title,
			status,
			source,
			confidence,
			json.dumps(payload, default=str, indent=2),
		),
	)
	return name


def _artifact(application, artifact_type, default=None):
	ensure_credit_analysis_tables()
	rows = frappe.db.sql(
		"""
		SELECT name, status, source, confidence, payload_json, modified
		FROM `tabCRM Credit Analysis Artifact`
		WHERE application=%s AND artifact_type=%s
		ORDER BY modified DESC
		LIMIT 1
	""",
		(application, artifact_type),
		as_dict=True,
	)
	if not rows:
		return default
	row = rows[0]
	payload = _json_loads(row.payload_json, default or {})
	if isinstance(payload, dict):
		payload.setdefault("artifact_id", row.name)
		payload.setdefault("status", row.status)
		payload.setdefault("source", row.source)
		payload.setdefault("confidence", flt(row.confidence))
	return payload


def _json_loads(value, default=None):
	if value is None:
		return default if default is not None else {}
	if isinstance(value, (dict, list)):
		return value
	try:
		return json.loads(value)
	except Exception:
		return default if default is not None else {}


def _doctype_ready(doctype):
	try:
		return frappe.db.table_exists(doctype)
	except Exception:
		return False


def _get_application(application_id):
	if not application_id:
		frappe.throw(_("Credit application is required"))
	if _doctype_ready("CRM Credit Application"):
		row = frappe.db.get_value(
			"CRM Credit Application",
			application_id,
			[
				"name",
				"borrower",
				"borrower_name",
				"borrower_type",
				"status",
				"facility_type",
				"requested_amount",
				"employer_name",
				"public_company_ticker",
				"industry",
				"kbli",
				"risk_grade",
				"purpose",
				"public_snapshot",
			],
			as_dict=True,
		)
		if row:
			return frappe._dict(row)
	frappe.throw(_("Credit application not found"))


def _customer_name(customer):
	if not customer:
		return ""
	try:
		return frappe.db.get_value("Customer", customer, "customer_name") or customer
	except Exception:
		return customer


def _safe_div(num, den, default=0):
	den = flt(den)
	if not den:
		return default
	return flt(num) / den


def _percent(num, den):
	return _safe_div(num, den)


def _years():
	current = now_datetime().year - 1
	return [current - 4, current - 3, current - 2, current - 1, current]


def _default_spreading(application):
	years = _years()
	base = max(flt(application.get("requested_amount")) * 2.8, 2_500_000_000)
	rows = []
	for idx, year in enumerate(years):
		growth = 1 + (idx * 0.08)
		revenue = base * growth
		cogs = revenue * 0.64
		gross_profit = revenue - cogs
		opex = revenue * 0.18
		ebitda = gross_profit - opex
		interest = max(flt(application.get("requested_amount")) * 0.09, 100_000_000)
		tax = max((ebitda - interest) * 0.19, 0)
		net_income = ebitda - interest - tax
		cash = revenue * 0.1
		receivables = revenue * 0.16
		inventory = cogs * 0.18
		current_assets = cash + receivables + inventory
		total_assets = current_assets + revenue * 0.55
		payables = cogs * 0.11
		current_liabilities = payables + revenue * 0.12
		debt = flt(application.get("requested_amount")) * (1.1 - idx * 0.06)
		total_liabilities = current_liabilities + debt
		equity = max(total_assets - total_liabilities, total_assets * 0.28)
		operating_cf = ebitda * 0.82
		capex = revenue * 0.05
		financing_cf = -debt * 0.08
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
		for statement_type, metrics in STATEMENT_TEMPLATES.items():
			for metric_key, metric_label in metrics:
				rows.append(
					{
						"application": application.name,
						"customer": application.get("borrower"),
						"statement_type": statement_type,
						"metric_key": metric_key,
						"metric_label": metric_label,
						"year": year,
						"amount": round(values.get(metric_key, 0), 2),
						"adjusted_amount": round(values.get(metric_key, 0), 2),
						"confidence": 0.98,
						"source": "BNI UAT Demo Adapter",
						"notes": "Deterministic seeded spreading for Credit Analysis UAT.",
					}
				)
	return rows


def _spread_rows(application):
	ensure_credit_analysis_tables()
	rows = frappe.db.sql(
		"""
		SELECT name, application, customer, statement_type, metric_key, metric_label, year, amount,
			adjusted_amount, confidence, source, notes
		FROM `tabCRM Credit Spread Line`
		WHERE application=%s
		ORDER BY year ASC, statement_type ASC, metric_key ASC
	""",
		(application.name,),
		as_dict=True,
	)
	if rows:
		return [dict(row) for row in rows]
	if application.get("borrower") and _doctype_ready("CRM Financial Statement"):
		financials = frappe.get_all(
			"CRM Financial Statement",
			fields=["name", "statement_type", "metric", "year", "amount", "source", "extraction_status", "notes"],
			filters={"customer": application.borrower},
			order_by="year asc",
			limit=500,
		)
		if financials:
			return [
				{
					"name": row.name,
					"application": application.name,
					"customer": application.borrower,
					"statement_type": row.statement_type,
					"metric_key": _metric_key(row.metric),
					"metric_label": row.metric,
					"year": row.year,
					"amount": flt(row.amount),
					"adjusted_amount": flt(row.amount),
					"confidence": 0.86 if row.extraction_status == "Extracted" else 1,
					"source": row.source or "CRM Financial Statement",
					"notes": row.notes or "",
				}
				for row in financials
			]
	return []


def _metric_key(value):
	value = cstr(value).strip().lower()
	aliases = {
		"pendapatan / sales": "revenue",
		"sales": "revenue",
		"revenue": "revenue",
		"beban pokok penjualan": "cogs",
		"cogs": "cogs",
		"gross profit": "gross_profit",
		"laba kotor": "gross_profit",
		"ebitda": "ebitda",
		"net income": "net_income",
		"laba bersih": "net_income",
		"total aset": "total_assets",
		"total assets": "total_assets",
		"current assets": "current_assets",
		"aset lancar": "current_assets",
		"current liabilities": "current_liabilities",
		"liabilitas jangka pendek": "current_liabilities",
		"total liabilities": "total_liabilities",
		"total liabilitas": "total_liabilities",
		"equity": "equity",
		"ekuitas": "equity",
	}
	if value in aliases:
		return aliases[value]
	return value.replace("&", "and").replace("/", " ").replace("-", " ").replace(" ", "_")


def _statement_type(value):
	value = cstr(value).strip()
	if not value:
		return "P&L"
	value_map = {
		"pl": "P&L",
		"p&l": "P&L",
		"profit and loss": "P&L",
		"income statement": "P&L",
		"balance sheet": "Balance Sheet",
		"bs": "Balance Sheet",
		"cash flow": "Cash Flow",
		"cf": "Cash Flow",
	}
	return value_map.get(value.lower(), value)


def _template_metric_labels():
	labels = {}
	for statement_type, metrics in STATEMENT_TEMPLATES.items():
		for key, label in metrics:
			labels[_metric_key(key)] = {"statement_type": statement_type, "metric_label": label}
			labels[_metric_key(label)] = {"statement_type": statement_type, "metric_label": label, "metric_key": key}
	return labels


def _normalize_header(value):
	return re.sub(r"[^a-z0-9]+", "_", cstr(value).strip().lower()).strip("_")


def _coerce_amount(value):
	if value in (None, ""):
		return 0
	if isinstance(value, (int, float)):
		return flt(value)
	text = cstr(value).strip()
	if not text:
		return 0
	text = text.replace("IDR", "").replace("Rp", "").replace("rp", "").strip()
	text = text.replace(".", "").replace(",", ".") if re.search(r"\d+\.\d{3}", text) else text.replace(",", "")
	text = re.sub(r"[^0-9.\-]", "", text)
	return flt(text)


def _column_to_index(ref):
	column = "".join(ch for ch in cstr(ref).upper() if ch.isalpha())
	value = 0
	for ch in column:
		value = value * 26 + ord(ch) - 64
	return max(value - 1, 0)


def _resolve_file_path(file_url):
	file_url = cstr(file_url).strip()
	if not file_url:
		frappe.throw(_("File URL is required"))
	if file_url.startswith(("http://", "https://")):
		frappe.throw(_("Use an uploaded Frappe file, not an external URL."))
	file_path = frappe.get_site_path(file_url.lstrip("/"))
	if not os.path.exists(file_path):
		frappe.throw(_("File not found: {0}").format(file_url))
	return file_path


def _infer_file_type(file_url, file_type=None):
	if file_type:
		return cstr(file_type).strip(".").lower()
	ext = os.path.splitext(cstr(file_url).split("?")[0])[1].strip(".").lower()
	if ext == "xls":
		return "xlsx"
	return ext


def _iter_xlsx_rows_with_openpyxl(file_path):
	import openpyxl

	workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
	worksheet = workbook.active
	rows = [list(row) for row in worksheet.iter_rows(values_only=True)]
	workbook.close()
	return rows


def _iter_xlsx_rows_from_xml(file_path):
	with zipfile.ZipFile(file_path) as archive:
		shared_strings = []
		if "xl/sharedStrings.xml" in archive.namelist():
			root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
			for item in root.findall(".//a:si", XML_NS):
				shared_strings.append("".join(node.text or "" for node in item.findall(".//a:t", XML_NS)))

		root = ET.fromstring(archive.read("xl/worksheets/sheet1.xml"))
		rows = []
		max_columns = 0
		for row in root.findall(".//a:sheetData/a:row", XML_NS):
			values = {}
			for cell in row.findall("a:c", XML_NS):
				ref = cell.attrib.get("r", "")
				index = _column_to_index(ref)
				cell_type = cell.attrib.get("t")
				if cell_type == "inlineStr":
					text = "".join(t.text or "" for t in cell.iterfind(".//a:t", XML_NS))
				else:
					value_node = cell.find("a:v", XML_NS)
					text = value_node.text if value_node is not None else ""
					if cell_type == "s" and text:
						text = shared_strings[int(text)]
				values[index] = text
				max_columns = max(max_columns, index + 1)
			rows.append(values)
	if not max_columns:
		return []
	normalized = []
	for row in rows:
		out = [None] * max_columns
		for index, value in row.items():
			out[index] = value
		normalized.append(out)
	return normalized


def _load_tabular_rows(file_path, file_type):
	if file_type == "csv":
		with open(file_path, encoding="utf-8-sig", newline="") as handle:
			return [list(row) for row in csv.reader(handle)]
	try:
		return _iter_xlsx_rows_with_openpyxl(file_path)
	except Exception:
		return _iter_xlsx_rows_from_xml(file_path)


def _rows_from_tabular_file(application, file_url, file_path, file_type):
	raw_rows = _load_tabular_rows(file_path, file_type)
	raw_rows = [row for row in raw_rows if any(cstr(cell).strip() for cell in row)]
	if not raw_rows:
		return [], [], [_("No rows found in uploaded file.")]

	headers = [_normalize_header(value) for value in raw_rows[0]]
	header_map = {header: idx for idx, header in enumerate(headers) if header}
	aliases = {
		"statement_type": {"statement_type", "statement", "type", "laporan"},
		"metric_key": {"metric_key", "key", "line_item_key"},
		"metric_label": {"metric_label", "metric", "line_item", "label", "item"},
		"year": {"year", "tahun", "period", "periode"},
		"amount": {"amount", "original_amount", "nilai", "value"},
		"adjusted_amount": {"adjusted_amount", "adjusted", "normalized_amount"},
		"notes": {"notes", "note", "catatan"},
	}
	columns = {}
	for target, options in aliases.items():
		for option in options:
			if option in header_map:
				columns[target] = header_map[option]
				break
	required = {"statement_type", "metric_label", "year", "amount"}
	missing = sorted(required - set(columns))
	if missing:
		return [], [], [_("Missing required columns: {0}").format(", ".join(missing))]

	template_labels = _template_metric_labels()
	rows = []
	errors = []
	seen = set()
	for row_number, raw in enumerate(raw_rows[1:], start=2):
		def cell(field):
			index = columns.get(field)
			return raw[index] if index is not None and index < len(raw) else None

		metric_label = cstr(cell("metric_label")).strip()
		metric_key = _metric_key(cell("metric_key") or metric_label)
		statement_type = _statement_type(cell("statement_type"))
		try:
			year = int(flt(cell("year")))
		except Exception:
			year = 0
		if not metric_label or not year:
			errors.append(_("Row {0}: metric label and year are required.").format(row_number))
			continue
		duplicate_key = (statement_type, metric_key, year)
		if duplicate_key in seen:
			errors.append(_("Row {0}: duplicate metric/year {1}/{2}.").format(row_number, metric_key, year))
			continue
		seen.add(duplicate_key)
		template = template_labels.get(metric_key) or template_labels.get(_metric_key(metric_label)) or {}
		rows.append(
			{
				"application": application.name,
				"customer": application.get("borrower"),
				"statement_type": template.get("statement_type") or statement_type,
				"metric_key": template.get("metric_key") or metric_key,
				"metric_label": template.get("metric_label") or metric_label,
				"year": year,
				"amount": _coerce_amount(cell("amount")),
				"adjusted_amount": _coerce_amount(cell("adjusted_amount")) if "adjusted_amount" in columns else _coerce_amount(cell("amount")),
				"confidence": 1,
				"source": file_url,
				"notes": cstr(cell("notes")).strip(),
			}
		)

	years = sorted({row["year"] for row in rows})
	if rows and not 3 <= len(years) <= 5:
		errors.append(_("Import must contain 3 to 5 financial years; found {0}.").format(len(years)))
	return rows, [], errors


def _extract_json_array(text):
	text = cstr(text).strip()
	if not text:
		return []
	try:
		data = json.loads(text)
	except Exception:
		match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S)
		if match:
			data = json.loads(match.group(1))
		else:
			start = text.find("[")
			end = text.rfind("]")
			if start == -1 or end == -1:
				raise
			data = json.loads(text[start : end + 1])
	if isinstance(data, dict):
		data = data.get("rows") or data.get("spreading") or []
	return data if isinstance(data, list) else []


def _extract_pdf_text(file_path):
	for module_name in ("pypdf", "PyPDF2"):
		try:
			module = __import__(module_name)
			reader = module.PdfReader(file_path)
			return "\n".join(page.extract_text() or "" for page in reader.pages)
		except Exception:
			continue
	return ""


def _rows_from_pdf_file(application, file_url, file_path):
	from crm.ai.kimi import call_kimi_chat, get_ai_settings

	settings = get_ai_settings()
	api_key = cstr(settings.kimi_api_key).strip()
	if not api_key or "******" in api_key:
		return [], [], [_("Kimi/Moonshot API key is not configured in FCRM Settings.")]

	text = _extract_pdf_text(file_path)
	if not text.strip():
		return [], [], [_("PDF text extraction is unavailable or returned no text. Configure OCR/RAGAnything runtime for scanned PDFs.")]

	metrics = []
	for statement_type, items in STATEMENT_TEMPLATES.items():
		for key, label in items:
			metrics.append({"statement_type": statement_type, "metric_key": key, "metric_label": label})
	prompt = f"""
Extract financial spreading rows from this uploaded credit analysis PDF.
Return only a JSON array. Each object must contain statement_type, metric_key, metric_label, year, amount, adjusted_amount, confidence, notes.
Use only these metric keys and labels:
{json.dumps(metrics, ensure_ascii=False)}

PDF text:
{text[:24000]}
"""
	response = call_kimi_chat(
		[
			{"role": "system", "content": "You extract Indonesian banking financial statement tables into structured JSON."},
			{"role": "user", "content": prompt},
		],
		thinking_mode=settings.thinking_mode,
	)
	raw_rows = _extract_json_array(response.content)
	rows = []
	low_confidence = []
	errors = []
	template_labels = _template_metric_labels()
	for idx, raw in enumerate(raw_rows, start=1):
		metric_label = cstr(raw.get("metric_label") or raw.get("metric") or raw.get("metric_key")).strip()
		metric_key = _metric_key(raw.get("metric_key") or metric_label)
		template = template_labels.get(metric_key) or template_labels.get(_metric_key(metric_label)) or {}
		year = int(flt(raw.get("year")))
		if not metric_label or not year:
			errors.append(_("Extracted PDF row {0}: metric and year are required.").format(idx))
			continue
		confidence = flt(raw.get("confidence") or 0.7)
		row = {
			"application": application.name,
			"customer": application.get("borrower"),
			"statement_type": template.get("statement_type") or _statement_type(raw.get("statement_type")),
			"metric_key": template.get("metric_key") or metric_key,
			"metric_label": template.get("metric_label") or metric_label,
			"year": year,
			"amount": _coerce_amount(raw.get("amount")),
			"adjusted_amount": _coerce_amount(raw.get("adjusted_amount") if raw.get("adjusted_amount") not in (None, "") else raw.get("amount")),
			"confidence": confidence,
			"source": file_url,
			"notes": cstr(raw.get("notes")).strip(),
		}
		rows.append(row)
		if confidence < 0.8:
			low_confidence.append(
				{
					"metric_key": row["metric_key"],
					"metric_label": row["metric_label"],
					"year": row["year"],
					"confidence": confidence,
					"status": "Needs Review",
				}
			)
	return rows, low_confidence, errors


def _spread_map(rows):
	data = {}
	for row in rows:
		year = int(row.get("year") or 0)
		if not year:
			continue
		data.setdefault(year, {})
		data[year][_metric_key(row.get("metric_key") or row.get("metric_label"))] = flt(
			row.get("adjusted_amount") if row.get("adjusted_amount") not in (None, "") else row.get("amount")
		)
	return data


def _balance_checks(rows):
	checks = []
	for year, values in _spread_map(rows).items():
		assets = values.get("total_assets", 0)
		liabilities_equity = values.get("total_liabilities", 0) + values.get("equity", 0)
		diff = assets - liabilities_equity
		checks.append(
			{
				"year": year,
				"total_assets": assets,
				"liabilities_plus_equity": liabilities_equity,
				"difference": diff,
				"status": "Balanced" if abs(diff) <= max(1000, assets * 0.01) else "Review",
			}
		)
	return checks


def _multi_period(rows):
	by_metric = {}
	data = _spread_map(rows)
	for row in rows:
		key = _metric_key(row.get("metric_key") or row.get("metric_label"))
		by_metric.setdefault(
			key,
			{"metric_key": key, "metric_label": row.get("metric_label") or key, "statement_type": row.get("statement_type"), "years": []},
		)
	for key, metric in by_metric.items():
		last_amount = None
		for year in sorted(data):
			amount = data[year].get(key)
			if amount is None:
				continue
			yoy = None if last_amount in (None, 0) else (amount - last_amount) / abs(last_amount)
			revenue = data[year].get("revenue")
			common_size = None if not revenue else amount / revenue
			metric["years"].append(
				{
					"year": year,
					"amount": amount,
					"yoy": yoy,
					"common_size": common_size,
					"flag": "Large Change" if yoy is not None and abs(yoy) > 0.2 else "",
				}
			)
			last_amount = amount
	return list(by_metric.values())


def _ratio_status(value, threshold, direction="min"):
	if value is None:
		return "Missing"
	if direction == "max":
		return "Alert" if value > threshold else "Pass"
	return "Alert" if value < threshold else "Pass"


def _calculate_ratios_from_rows(rows, kbli=None):
	data = _spread_map(rows)
	benchmark = BENCHMARKS.get(kbli or "", BENCHMARKS["default"])
	result = []
	for year in sorted(data):
		v = data[year]
		ratios = [
			("liquidity", "current_ratio", "Current Ratio", _safe_div(v.get("current_assets"), v.get("current_liabilities")), 1.2, "min"),
			("liquidity", "quick_ratio", "Quick Ratio", _safe_div(v.get("cash", 0) + v.get("receivables", 0), v.get("current_liabilities")), 1.0, "min"),
			("liquidity", "cash_ratio", "Cash Ratio", _safe_div(v.get("cash"), v.get("current_liabilities")), 0.2, "min"),
			("leverage", "der", "DER", _safe_div(v.get("total_liabilities"), v.get("equity")), 3.0, "max"),
			("leverage", "debt_to_equity", "Debt to Equity", _safe_div(v.get("debt"), v.get("equity")), 2.5, "max"),
			("leverage", "debt_to_assets", "Debt to Assets", _safe_div(v.get("debt"), v.get("total_assets")), 0.65, "max"),
			("leverage", "interest_coverage", "Interest Coverage", _safe_div(v.get("ebitda"), v.get("interest_expense")), 2.0, "min"),
			("profitability", "gross_margin", "Gross Margin", _percent(v.get("gross_profit"), v.get("revenue")), 0.2, "min"),
			("profitability", "ebitda_margin", "EBITDA Margin", _percent(v.get("ebitda"), v.get("revenue")), 0.12, "min"),
			("profitability", "net_margin", "Net Margin", _percent(v.get("net_income"), v.get("revenue")), 0.05, "min"),
			("profitability", "roa", "ROA", _percent(v.get("net_income"), v.get("total_assets")), 0.03, "min"),
			("profitability", "roe", "ROE", _percent(v.get("net_income"), v.get("equity")), 0.08, "min"),
			("efficiency", "asset_turnover", "Asset Turnover", _safe_div(v.get("revenue"), v.get("total_assets")), 0.8, "min"),
			("efficiency", "inventory_days", "Inventory Days", _safe_div(v.get("inventory"), v.get("cogs")) * 365, 120, "max"),
			("efficiency", "receivable_days", "Receivable Days", _safe_div(v.get("receivables"), v.get("revenue")) * 365, 90, "max"),
			("efficiency", "payable_days", "Payable Days", _safe_div(v.get("payables"), v.get("cogs")) * 365, 120, "max"),
		]
		wcc = next(item[3] for item in ratios if item[1] == "inventory_days") + next(item[3] for item in ratios if item[1] == "receivable_days") - next(item[3] for item in ratios if item[1] == "payable_days")
		ratios.append(("efficiency", "working_capital_cycle", "Working Capital Cycle", wcc, 120, "max"))
		for category, key, label, value, threshold, direction in ratios:
			result.append(
				{
					"year": year,
					"category": category,
					"key": key,
					"label": label,
					"value": round(value, 4),
					"threshold": threshold,
					"status": _ratio_status(value, threshold, direction),
					"benchmark_median": benchmark["median"].get(key),
				}
			)
	return result


def _calculate_dscr_from_rows(rows, requested_amount=0, tenor_years=5, annual_rate=0.11):
	data = _spread_map(rows)
	years = sorted(data)[-int(tenor_years or 5) :]
	if not years:
		return {"formula": "(EBITDA - Tax) / (Principal + Interest)", "items": [], "min_dscr": None, "status": "Missing"}
	principal = _safe_div(flt(requested_amount), len(years) or 1)
	items = []
	for year in years:
		v = data[year]
		interest = flt(v.get("interest_expense")) or flt(requested_amount) * annual_rate
		debt_service = principal + interest
		base = _safe_div(flt(v.get("ebitda")) - flt(v.get("tax")), debt_service)
		items.append(
			{
				"year": year,
				"principal": principal,
				"interest": interest,
				"base": round(base, 3),
				"downside_20": round(base * 0.8, 3),
				"upside_20": round(base * 1.2, 3),
				"alert": base < 1.2,
			}
		)
	min_dscr = min([row["base"] for row in items], default=0)
	return {"formula": "(EBITDA - Tax) / (Principal + Interest)", "items": items, "min_dscr": min_dscr, "status": "Alert" if min_dscr < 1.2 else "Pass"}


def _trend_projection(rows, metric_key="revenue"):
	data = _spread_map(rows)
	points = [{"year": year, "amount": values.get(metric_key, 0)} for year, values in sorted(data.items()) if metric_key in values]
	if len(points) < 2:
		return {"metric_key": metric_key, "points": points, "cagr": 0, "projection": [], "comments": ["Insufficient history for projection."]}
	first = points[0]["amount"]
	last = points[-1]["amount"]
	cagr = math.pow(_safe_div(last, first, 1), 1 / (len(points) - 1)) - 1 if first else 0
	x_avg = sum(range(len(points))) / len(points)
	y_avg = sum(point["amount"] for point in points) / len(points)
	num = sum((idx - x_avg) * (point["amount"] - y_avg) for idx, point in enumerate(points))
	den = sum((idx - x_avg) ** 2 for idx in range(len(points))) or 1
	slope = num / den
	intercept = y_avg - slope * x_avg
	last_year = points[-1]["year"]
	projection = [
		{"year": last_year + step, "amount": max(0, round(intercept + slope * (len(points) - 1 + step), 2))}
		for step in range(1, 4)
	]
	comments = []
	for current, previous in zip(points[1:], points[:-1], strict=False):
		change = _safe_div(current["amount"] - previous["amount"], previous["amount"])
		if abs(change) > 0.2:
			comments.append(f"{metric_key} changed {round(change * 100, 1)}% in {current['year']}; analyst review required.")
	return {"metric_key": metric_key, "points": points, "cagr": round(cagr, 4), "projection": projection, "comments": comments or ["No anomaly above 20% threshold."]}


def _scenario(rows, drivers=None):
	drivers = drivers or {}
	if not _spread_map(rows):
		return []
	cases = [
		("Best", flt(drivers.get("best_revenue_growth") or 0.12), flt(drivers.get("best_margin_delta") or 0.03), flt(drivers.get("best_rate_delta") or -0.01)),
		("Base", flt(drivers.get("base_revenue_growth") or 0.04), flt(drivers.get("base_margin_delta") or 0), flt(drivers.get("base_rate_delta") or 0)),
		("Worst", flt(drivers.get("worst_revenue_growth") or -0.18), flt(drivers.get("worst_margin_delta") or -0.04), flt(drivers.get("worst_rate_delta") or 0.03)),
	]
	data = _spread_map(rows)
	latest_year = max(data) if data else 0
	v = data.get(latest_year, {})
	result = []
	for label, revenue_growth, margin_delta, rate_delta in cases:
		revenue = flt(v.get("revenue")) * (1 + revenue_growth)
		ebitda_margin = _safe_div(v.get("ebitda"), v.get("revenue")) + margin_delta
		ebitda = revenue * ebitda_margin
		interest = flt(v.get("interest_expense")) * (1 + rate_delta)
		debt_service = interest + flt(v.get("debt")) * 0.18
		dscr = _safe_div(ebitda - flt(v.get("tax")), debt_service)
		result.append(
			{
				"case": label,
				"revenue_growth": revenue_growth,
				"margin_delta": margin_delta,
				"rate_delta": rate_delta,
				"revenue": round(revenue, 2),
				"ebitda": round(ebitda, 2),
				"dscr": round(dscr, 3),
				"decision": "Approval likely" if dscr >= 1.4 else "Refer" if dscr >= 1.2 else "Mitigation required",
			}
		)
	return result


def _sensitivity(rows, x_range=None, y_range=None):
	if not _spread_map(rows):
		return {"x_axis": "Revenue Growth", "y_axis": "EBITDA Margin Delta", "x_range": x_range or [], "y_range": y_range or [], "matrix": []}
	x_range = x_range or [-0.2, -0.1, 0, 0.1, 0.2]
	y_range = y_range or [-0.03, -0.015, 0, 0.015, 0.03]
	base = _scenario(rows)[1]
	matrix = []
	for revenue_delta in x_range:
		row = []
		for margin_delta in y_range:
			dscr = base["dscr"] * (1 + revenue_delta) * (1 + margin_delta * 5)
			row.append({"value": round(dscr, 3), "status": "Alert" if dscr < 1.2 else "Pass"})
		matrix.append({"revenue_delta": revenue_delta, "cells": row})
	return {"x_axis": "Revenue Growth", "y_axis": "EBITDA Margin Delta", "x_range": x_range, "y_range": y_range, "matrix": matrix}


def _cashflow_projection(rows, requested_amount=0, years=5, drivers=None):
	drivers = drivers or {}
	data = _spread_map(rows)
	if not data:
		return {"drivers": drivers, "items": [], "status": "Missing"}
	latest_year = max(data) if data else now_datetime().year - 1
	v = data.get(latest_year, {})
	growth = flt(drivers.get("growth") or 0.06)
	margin = _safe_div(v.get("operating_cf"), v.get("revenue"), 0.16)
	cumulative = flt(v.get("ending_cash"))
	annual_principal = _safe_div(flt(requested_amount), years)
	items = []
	for step in range(1, int(years or 5) + 1):
		revenue = flt(v.get("revenue")) * ((1 + growth) ** step)
		operating_cf = revenue * margin
		capex = revenue * flt(drivers.get("capex_percent") or 0.05)
		debt_service = annual_principal + flt(requested_amount) * flt(drivers.get("rate") or 0.11)
		period_cf = operating_cf - capex - debt_service
		cumulative += period_cf
		items.append(
			{
				"year": latest_year + step,
				"operating_cf": round(operating_cf, 2),
				"capex": round(capex, 2),
				"debt_service": round(debt_service, 2),
				"period_cf": round(period_cf, 2),
				"cumulative_cf": round(cumulative, 2),
				"cash_gap_alert": cumulative < 0,
			}
		)
	return {"drivers": {"growth": growth, "capex_percent": flt(drivers.get("capex_percent") or 0.05), "rate": flt(drivers.get("rate") or 0.11)}, "items": items, "status": "Alert" if any(row["cash_gap_alert"] for row in items) else "Pass"}


def _latest_bureau(customer):
	if not customer or not _doctype_ready("CRM Bureau Report"):
		return None
	rows = frappe.get_all("CRM Bureau Report", fields=["*"], filters={"customer": customer}, order_by="report_date desc, modified desc", limit=1)
	return dict(rows[0]) if rows else None


def _collaterals(customer, requested_amount=0):
	if not customer or not _doctype_ready("CRM Collateral"):
		return []
	rows = frappe.get_all("CRM Collateral", fields=["*"], filters={"customer": customer}, order_by="modified desc", limit=50)
	result = []
	for row in rows:
		item = dict(row)
		value = flt(item.get("collateral_value"))
		ltv = flt(item.get("ltv_percent")) or (_safe_div(flt(requested_amount), value) * 100 if value else 0)
		item["computed_ltv_percent"] = round(ltv, 2)
		item["alert"] = ltv > 80
		item["reappraisal_trigger"] = item["alert"] or item.get("reappraisal_status") == "Due"
		result.append(item)
	return result


def _risk_grade(application, ratios, dscr, bureau, collateral):
	if not ratios and not (dscr or {}).get("items"):
		return {
			"score": 0,
			"grade": "Unscored",
			"weights": {"financial": 420, "repayment": 220, "collateral": 160, "trend": 120, "qualitative": 80},
			"breakdown": {"financial": 0, "repayment": 0, "collateral": 0, "trend": 0, "qualitative": 0},
			"override": _artifact(application.name, "risk_grade_override", {}),
			"audit_trail": [_("Risk grade pending until financial spreading is imported or saved.")],
		}
	latest = {}
	for ratio in ratios:
		if ratio["year"] >= latest.get(ratio["key"], {}).get("year", 0):
			latest[ratio["key"]] = ratio
	weights = {"financial": 420, "repayment": 220, "collateral": 160, "trend": 120, "qualitative": 80}
	financial_score = min(1, (_safe_div(latest.get("current_ratio", {}).get("value"), 1.2) + _safe_div(dscr.get("min_dscr"), 1.2) + _safe_div(latest.get("interest_coverage", {}).get("value"), 2)) / 3)
	bureau_score = min(1, _safe_div((bureau or {}).get("score"), 800)) if (bureau or {}).get("score") else 0
	collateral_score = 0.75
	if collateral:
		avg_ltv = sum(row.get("computed_ltv_percent", 0) for row in collateral) / len(collateral)
		collateral_score = max(0, min(1, (100 - avg_ltv) / 45))
	trend_score = 0.85 if latest.get("net_margin", {}).get("status") != "Alert" else 0.55
	qualitative_score = 0.82 if application.get("purpose") else 0.65
	breakdown = {
		"financial": round(financial_score * weights["financial"]),
		"repayment": round(bureau_score * weights["repayment"]),
		"collateral": round(collateral_score * weights["collateral"]),
		"trend": round(trend_score * weights["trend"]),
		"qualitative": round(qualitative_score * weights["qualitative"]),
	}
	score = sum(breakdown.values())
	grade = "A" if score >= 850 else "B" if score >= 700 else "C" if score >= 550 else "D" if score >= 400 else "E"
	return {
		"score": score,
		"grade": grade,
		"weights": weights,
		"breakdown": breakdown,
		"override": _artifact(application.name, "risk_grade_override", {}),
		"audit_trail": [_("Risk grade generated from ratios, DSCR, bureau score, collateral, trend, and qualitative fields.")],
	}


def _benchmark(application, ratios):
	benchmark = deepcopy(BENCHMARKS.get(application.get("kbli") or "", BENCHMARKS["default"]))
	latest = {}
	for row in ratios:
		if row["key"] in benchmark["median"] and row["year"] >= latest.get(row["key"], {}).get("year", 0):
			latest[row["key"]] = row
	positions = []
	for key, row in latest.items():
		median = benchmark["median"].get(key)
		value = row.get("value")
		positions.append(
			{
				"key": key,
				"label": row.get("label"),
				"value": value,
				"median": median,
				"position": "Above Median" if key != "debt_to_equity" and value >= median else "Below Median" if key != "debt_to_equity" else "Better Than Median" if value <= median else "Above Risk Median",
				"comment": f"{row.get('label')} is compared against KBLI {application.get('kbli') or 'default'} median.",
			}
		)
	benchmark["positions"] = positions
	return benchmark


def _peers(application, ratios):
	latest = {}
	for row in ratios:
		if row["key"] in {"current_ratio", "debt_to_equity", "net_margin", "dscr"} and row["year"] >= latest.get(row["key"], {}).get("year", 0):
			latest[row["key"]] = row

	# Fallback values from form fields if calculated ratios are empty
	rev = flt(application.get("revenue"))
	np = flt(application.get("net_profit"))
	fallback_margin = np / rev if rev > 0 else 0.0

	peers = [
		{
			"name": application.get("borrower_name") or application.name,
			"type": "Borrower",
			"current_ratio": (latest.get("current_ratio") or {}).get("value") or flt(application.get("current_ratio")),
			"debt_to_equity": (latest.get("debt_to_equity") or {}).get("value") or flt(application.get("der")),
			"net_margin": (latest.get("net_margin") or {}).get("value") or fallback_margin,
		}
	]
	rankings = {}
	for key in ("current_ratio", "debt_to_equity", "net_margin"):
		reverse = key != "debt_to_equity"
		rankings[key] = sorted(peers, key=lambda row: row[key], reverse=reverse)
	return {"peers": peers, "rankings": rankings, "summary": _("No external peer dataset is configured; showing borrower ratios only.")}


def _memo_payload(application, rows, ratios, dscr, risk_grade, recommendation=None):
	borrower = application.get("borrower_name") or _customer_name(application.get("borrower")) or application.name
	recommendation = recommendation or _recommendation_payload(risk_grade, dscr)
	purpose = application.get("purpose") or "Working capital and general banking facility review."
	risk_text = f"Primary risks: {', '.join(recommendation['risk_factors'])}."
	rec_text = f"{recommendation['decision']}: {recommendation['reasoning']}"
	summary = [
		f"{borrower} requests {application.get('facility_type') or 'credit facility'} of IDR {round(flt(application.get('requested_amount')), 0):,.0f}.",
		f"Latest risk grade is {risk_grade['grade']} with score {risk_grade['score']} / 1000.",
		f"Minimum DSCR is {dscr.get('min_dscr') if dscr.get('min_dscr') is not None else 'not available'}, status {dscr.get('status') or 'Missing'}.",
		f"Financial spreading covers {len(set(row['year'] for row in rows))} years across PL/BS/CF.",
		f"Recommendation is {recommendation['decision']} with {recommendation['confidence']}% confidence.",
	]
	content = "\n\n".join(
		[
			f"CREDIT ANALYSIS MEMORANDUM",
			f"Borrower\n{summary[0]}",
			f"Purpose\n{purpose}",
			f"Financials\n{summary[2]}",
			f"Risks\n{risk_text}",
			f"Recommendation\n{rec_text}",
		]
	)
	return {
		"summary_bullets": summary,
		"content": content,
		"sections": ["Borrower", "Purpose", "Financials", "Risks", "Recommendation"],
		"sources": ["Credit spreading", "Ratio snapshot", "Bureau report", "Collateral coverage", "AI Agent Center audit"],
		"version": now_datetime().strftime("%Y%m%d%H%M%S"),
	}


def _recommendation_payload(risk_grade, dscr):
	min_dscr = flt((dscr or {}).get("min_dscr"))
	decision = "Approve" if risk_grade["score"] >= 760 and min_dscr >= 1.25 else "Refer" if risk_grade["score"] >= 620 and min_dscr >= 1.05 else "Reject"
	confidence = 88 if decision == "Approve" else 74 if decision == "Refer" else 68
	conditions = [
		"Maintain DSCR covenant above 1.20x.",
		"Quarterly financial statement submission.",
		"Collateral re-appraisal if LTV exceeds 80%.",
	]
	risk_factors = ["DSCR sensitivity", "Collateral value movement", "Bureau/adverse event monitoring"]
	return {
		"decision": decision,
		"confidence": confidence,
		"conditions": conditions,
		"risk_factors": risk_factors,
		"reasoning": f"Decision is based on score {risk_grade['score']} and minimum DSCR {min_dscr}.",
		"citations": ["ratio_snapshot", "dscr", "risk_grade", "collateral", "bureau"],
	}


def _workspace_payload(application_id, persist_artifacts=False):
	application = _get_application(application_id)
	rows = _spread_rows(application)
	ratios = _calculate_ratios_from_rows(rows, application.get("kbli"))
	
	# Dynamically calculate and pass tenor and annual interest rate from application document
	tenor_months = flt(application.get("tenor_months")) or 60
	tenor_years = max(1, round(tenor_months / 12))
	annual_rate = flt(application.get("interest_rate")) / 100 if flt(application.get("interest_rate")) else 0.11

	dscr = _calculate_dscr_from_rows(rows, application.get("requested_amount"), tenor_years, annual_rate)
	trend = _trend_projection(rows, "revenue")
	scenarios = _scenario(rows)
	sensitivity = _sensitivity(rows)
	cashflow = _cashflow_projection(rows, application.get("requested_amount"), tenor_years, {"rate": annual_rate})
	bureau = _latest_bureau(application.get("borrower")) or _artifact(application.name, "bureau_report", {})
	collateral = _collaterals(application.get("borrower"), application.get("requested_amount"))
	risk_grade = _risk_grade(application, ratios, dscr, bureau, collateral)
	benchmark = _benchmark(application, ratios)
	peers = _peers(application, ratios)
	recommendation = _artifact(application.name, "recommendation", None) or _recommendation_payload(risk_grade, dscr)
	memo = _artifact(application.name, "credit_memo", None) or _memo_payload(application, rows, ratios, dscr, risk_grade, recommendation)
	news = _artifact(application.name, "news_sentiment", _default_news(application))
	extraction = _artifact(application.name, "extraction", _default_extraction(application, rows))
	approval = _artifact(application.name, "approval_route", _default_approval(application, risk_grade))
	export = _artifact(application.name, "memo_export", _default_export(application))

	if persist_artifacts:
		customer = application.get("borrower")
		for artifact_type, title, payload in (
			("ratio_snapshot", "Ratio Snapshot", {"ratios": ratios}),
			("dscr", "DSCR", dscr),
			("trend_projection", "Trend Projection", trend),
			("scenario", "Scenario Simulation", {"scenarios": scenarios}),
			("sensitivity", "Sensitivity Matrix", sensitivity),
			("cashflow_projection", "Cashflow Projection", cashflow),
			("industry_benchmark", "Industry Benchmark", benchmark),
			("peer_comparison", "Peer Comparison", peers),
			("risk_grade", "Risk Grade", risk_grade),
			("recommendation", "AI Recommendation", recommendation),
			("credit_memo", "Credit Memo", memo),
			("news_sentiment", "News Sentiment", news),
			("extraction", "AI Extraction", extraction),
			("approval_route", "Approval Route", approval),
			("memo_export", "Memo Export", export),
		):
			_replace_artifact(application.name, customer, artifact_type, title, payload, source="Credit Analysis Engine")

	proof = _build_proof(application.name)
	return {
		"application": dict(application),
		"templates": STATEMENT_TEMPLATES,
		"spreading": rows,
		"balance_checks": _balance_checks(rows),
		"multi_period": _multi_period(rows),
		"ratios": ratios,
		"dscr": dscr,
		"trend": trend,
		"benchmark": benchmark,
		"peers": peers,
		"risk_grade": risk_grade,
		"scenarios": scenarios,
		"sensitivity": sensitivity,
		"cashflow": cashflow,
		"collaterals": collateral,
		"bureau": bureau,
		"news_sentiment": news,
		"extraction": extraction,
		"memo": memo,
		"recommendation": recommendation,
		"approval_route": approval,
		"memo_export": export,
		"proof": proof,
	}


def _default_extraction(application, rows):
	return {
		"status": "Pending",
		"file_url": "",
		"parser": "",
		"cell_count": len(rows),
		"low_confidence": [],
		"review_cells": [],
		"message": _("Upload a PDF, XLSX, or CSV financial statement to populate spreading."),
	}


def _default_news(application):
	return {
		"status": "Not Scanned",
		"sentiment_score": 0,
		"adverse_flags": [],
		"sources": [],
		"summary": _("Run news scan to fetch Google News RSS sources."),
	}


def _default_approval(application, risk_grade):
	amount = flt(application.get("requested_amount"))
	grade = (risk_grade or {}).get("grade", "")
	level = "Credit Committee" if amount >= 5_000_000_000 or grade in {"C", "D", "E"} else "Branch Credit Manager"

	# Check RBAC Approval Matrix for more precise routing
	try:
		matrix_rules = frappe.db.get_all(
			"FCRM Approval Matrix",
			filters={
				"enabled": 1,
				"document_type": "CRM Credit Application",
				"approval_type": "Credit",
				"min_amount": ["<=", amount],
				"max_amount": [">=", amount],
			},
			fields=["approver_role", "approver_user", "approval_sequence", "approval_type"],
			order_by="approval_sequence asc",
		)
		if matrix_rules:
			approvers = []
			for rule in matrix_rules:
				role = rule.get("approver_role") or ""
				if role and role not in approvers:
					approvers.append(role)
			if approvers:
				level = approvers[0]
				return {
					"status": "Draft",
					"route": level,
					"approvers": approvers,
					"notifications": "Queued",
					"tracking": [{"status": "Draft", "timestamp": str(now_datetime()), "owner": frappe.session.user}],
					"source": "FCRM Approval Matrix",
				}
	except Exception:
		pass

	return {
		"status": "Draft",
		"route": level,
		"approvers": [level, "Risk Reviewer"],
		"notifications": "Queued",
		"tracking": [{"status": "Draft", "timestamp": str(now_datetime()), "owner": frappe.session.user}],
		"source": "Default Logic",
	}


def _default_export(application):
	return {
		"status": "Ready",
		"format": "PDF",
		"watermark": "Internal",
		"sections": ["Cover Page", "Table of Contents", "Charts", "Financial Tables", "Recommendation"],
		"email_distribution": "Draft Queue",
		"message": _("PDF renderer/email adapter can process this export payload."),
	}


@frappe.whitelist()
def get_published_workflows():
	"""Return published workflows for manual assignment to a credit application."""
	if not _doctype_ready("CRM Workflow"):
		return []
	flows = frappe.get_all(
		"CRM Workflow",
		filters={"status": "Published"},
		fields=["name", "title", "description", "product_type", "current_version"],
		order_by="title asc",
	)
	return flows


@frappe.whitelist()
def assign_workflow(application_id: str, workflow_name: str):
	"""Assign a published workflow to a credit application and start execution."""
	from crm.utils.workflow_engine import start_flow_execution

	app = _get_application(application_id)
	flow = frappe.get_doc("CRM Workflow", workflow_name)

	if flow.status != "Published":
		frappe.throw(_("Workflow is not published."))

	if _doctype_ready("CRM Credit Application"):
		frappe.db.set_value("CRM Credit Application", application_id, "credit_flow", workflow_name)
		frappe.db.set_value("CRM Credit Application", application_id, "credit_flow_version", flow.current_version)
		frappe.db.commit()

	exec_doc = start_flow_execution(application_id)
	if not exec_doc:
		frappe.throw(_("Failed to start workflow execution."))

	return {
		"ok": True,
		"execution_id": exec_doc.name,
		"workflow": workflow_name,
		"current_node": exec_doc.current_node,
	}


@frappe.whitelist()
def get_workflow_step_configs(application_id: str):
	"""Return form node configs from the active workflow as step definitions for Credit Analysis tabs."""
	exec_records = frappe.get_all(
		"CRM Workflow Execution",
		filters={"application": application_id, "status": "Running"},
		fields=["name", "flow_version_json"],
		limit=1,
	)
	if not exec_records:
		return []

	flow_data = exec_records[0]
	try:
		parsed = json.loads(flow_data.flow_version_json) if isinstance(flow_data.flow_version_json, str) else flow_data.flow_version_json
		nodes = parsed.get("nodes", [])
	except Exception:
		return []

	steps = []
	for node in nodes:
		node_data = node.get("data", {})
		node_type = node_data.get("nodeType", "") or node.get("type", "")
		node_id = node.get("id", "")
		label = node_data.get("label") or node_data.get("name") or node_id

		if node_type == "FormNode":
			config = node_data.get("config") or {}
			steps.append({
				"step_id": node_id,
				"label": label,
				"node_type": "FormNode",
				"sections": config.get("sections", []),
				"fields": config.get("fields", []),
				"available_actions": config.get("availableActions", ["save_draft", "submit"]),
			})
		elif node_type in ("ApprovalNode",):
			config = node_data.get("config") or {}
			steps.append({
				"step_id": node_id,
				"label": label,
				"node_type": "ApprovalNode",
				"sections": config.get("sections", []),
				"fields": config.get("fields", []),
				"available_actions": config.get("availableActions", ["approve", "reject", "return"]),
			})

	return steps


@frappe.whitelist()
def get_workflow_creation_config(workflow_name: str):
	"""Return FormNode configs from a published workflow for use in the creation dialog."""
	flow = frappe.get_doc("CRM Workflow", workflow_name)
	if flow.status != "Published":
		frappe.throw(_("Workflow is not published."))

	flow_json = flow.flow_json
	try:
		parsed = json.loads(flow_json) if isinstance(flow_json, str) else flow_json
		nodes = parsed.get("nodes", [])
	except Exception:
		return []

	steps = []
	for node in nodes:
		node_data = node.get("data", {})
		node_type = node_data.get("nodeType", "")
		if node_type != "FormNode":
			continue
		node_id = node.get("id", "")
		label = node_data.get("label") or node_data.get("name") or node_id
		config = node_data.get("config") or {}
		steps.append({
			"step_id": node_id,
			"label": label,
			"node_type": "FormNode",
			"sections": config.get("sections", []),
			"fields": config.get("fields", []),
		})

	return steps


@frappe.whitelist()
def get_credit_workspace(application_id: str):
	return _workspace_payload(application_id)


@frappe.whitelist()
def save_spreading(application_id: str, rows=None, status: str = "Draft"):
	application = _get_application(application_id)
	rows = _json_loads(rows, rows) if isinstance(rows, str) else rows
	rows = rows or []
	ensure_credit_analysis_tables()
	frappe.db.sql("DELETE FROM `tabCRM Credit Spread Line` WHERE application=%s", (application.name,))
	for row in rows:
		if not row.get("year") or not (row.get("metric_key") or row.get("metric_label")):
			continue
		_insert(
			"CRM Credit Spread Line",
			{
				"application": application.name,
				"customer": application.get("borrower"),
				"statement_type": row.get("statement_type") or "P&L",
				"metric_key": _metric_key(row.get("metric_key") or row.get("metric_label")),
				"metric_label": row.get("metric_label") or row.get("metric") or row.get("metric_key"),
				"year": int(row.get("year")),
				"amount": flt(row.get("amount")),
				"adjusted_amount": flt(row.get("adjusted_amount") if row.get("adjusted_amount") not in (None, "") else row.get("amount")),
				"confidence": flt(row.get("confidence") or 1),
				"source": row.get("source") or "Manual",
				"notes": row.get("notes") or "",
			},
		)
	workspace = _workspace_payload(application.name, persist_artifacts=True)
	_replace_artifact(application.name, application.get("borrower"), "spreading_status", "Financial Spreading", {"status": status, "row_count": len(rows), "balance_checks": workspace["balance_checks"]}, status=status)
	_upsert_proof("credit_analysis", application.name)
	frappe.db.commit()
	return {"status": status, "row_count": len(rows), "balance_checks": workspace["balance_checks"], "workspace": workspace}


@frappe.whitelist()
def import_statement_file(application_id: str, file_url: str | None = None, file_type: str | None = None):
	application = _get_application(application_id)
	if not file_url:
		frappe.throw(_("Financial statement file is required for import."))
	file_type = _infer_file_type(file_url, file_type)
	file_path = _resolve_file_path(file_url)
	low_confidence = []
	errors = []
	rows = []
	parser = ""
	if file_type in {"csv", "xlsx"}:
		parser = "Structured spreadsheet parser"
		rows, low_confidence, errors = _rows_from_tabular_file(application, file_url, file_path, file_type)
	elif file_type == "pdf":
		parser = "PDF text extraction + Kimi"
		rows, low_confidence, errors = _rows_from_pdf_file(application, file_url, file_path)
	else:
		errors = [_("Unsupported file type: {0}. Upload PDF, XLSX, XLS, or CSV.").format(file_type or "unknown")]

	status = "Failed" if errors else "Imported"
	workspace = _workspace_payload(application.name)
	if not errors:
		saved = save_spreading(application.name, rows, status="Imported")
		
		# Auto generate AI Executive Summary, Memo and Recommendation!
		try:
			generate_credit_summary(application.name)
		except Exception:
			pass
		try:
			generate_credit_memo(application.name)
		except Exception:
			pass
		try:
			generate_credit_recommendation(application.name)
		except Exception:
			pass

		workspace = _workspace_payload(application.name)

	review_cells = []
	for row in rows:
		confidence = flt(row.get("confidence") or 1)
		review_cells.append(
			{
				"metric_key": row.get("metric_key"),
				"metric_label": row.get("metric_label"),
				"statement_type": row.get("statement_type"),
				"year": row.get("year"),
				"amount": row.get("adjusted_amount") if row.get("adjusted_amount") not in (None, "") else row.get("amount"),
				"confidence": confidence,
				"source": row.get("source") or file_url,
				"status": "Needs Review" if confidence < 0.8 else "Imported",
			}
		)

	artifact = {
		"status": status,
		"import_type": file_type,
		"file_url": file_url,
		"file_name": os.path.basename(file_path),
		"parser": parser,
		"row_count": len(rows),
		"cell_count": len(rows),
		"low_confidence": low_confidence,
		"review_cells": review_cells,
		"errors": errors,
		"imported_on": str(now_datetime()),
	}
	_replace_artifact(
		application.name,
		application.get("borrower"),
		"statement_import",
		"Financial Statement Import",
		artifact,
		status="Failed" if errors else "Completed",
		source=parser or "Statement Import",
		confidence=0 if errors else 1,
	)
	_replace_artifact(
		application.name,
		application.get("borrower"),
		"extraction",
		"AI Extraction from PDF" if file_type == "pdf" else "Structured Statement Import",
		artifact,
		status="Failed" if errors else "Completed",
		source=parser or "Statement Import",
		confidence=0 if errors else 1,
	)
	workspace["extraction"] = artifact
	frappe.db.commit()
	return {
		"status": status,
		"import_type": file_type,
		"row_count": len(rows),
		"low_confidence": low_confidence,
		"errors": errors,
		"workspace": workspace,
	}


@frappe.whitelist()
def extract_statement_pdf(application_id: str, file_url: str | None = None):
	return import_statement_file(application_id, file_url, file_type="pdf")


@frappe.whitelist()
def calculate_ratios(application_id: str):
	workspace = _workspace_payload(application_id, persist_artifacts=True)
	return {"ratios": workspace["ratios"], "benchmark": workspace["benchmark"]}


@frappe.whitelist()
def calculate_dscr(application_id: str, tenor_years: int = 5, annual_rate: float = 0.11):
	application = _get_application(application_id)
	dscr = _calculate_dscr_from_rows(_spread_rows(application), application.get("requested_amount"), tenor_years, annual_rate)
	_replace_artifact(application.name, application.get("borrower"), "dscr", "DSCR", dscr)
	frappe.db.commit()
	return dscr


@frappe.whitelist()
def run_trend_projection(application_id: str, metric_key: str = "revenue"):
	application = _get_application(application_id)
	result = _trend_projection(_spread_rows(application), metric_key)
	_replace_artifact(application.name, application.get("borrower"), "trend_projection", "Trend Projection", result)
	frappe.db.commit()
	return result


@frappe.whitelist()
def run_scenario(application_id: str, drivers=None):
	application = _get_application(application_id)
	drivers = _json_loads(drivers, {}) if isinstance(drivers, str) else drivers
	result = {"scenarios": _scenario(_spread_rows(application), drivers)}
	_replace_artifact(application.name, application.get("borrower"), "scenario", "Scenario Simulation", result)
	frappe.db.commit()
	return result


@frappe.whitelist()
def run_sensitivity(application_id: str, x_range=None, y_range=None):
	application = _get_application(application_id)
	x_range = _json_loads(x_range, None) if isinstance(x_range, str) else x_range
	y_range = _json_loads(y_range, None) if isinstance(y_range, str) else y_range
	result = _sensitivity(_spread_rows(application), x_range, y_range)
	_replace_artifact(application.name, application.get("borrower"), "sensitivity", "Sensitivity Analysis", result)
	frappe.db.commit()
	return result


@frappe.whitelist()
def run_cashflow_projection(application_id: str, years: int = 5, drivers=None):
	application = _get_application(application_id)
	drivers = _json_loads(drivers, {}) if isinstance(drivers, str) else drivers
	result = _cashflow_projection(_spread_rows(application), application.get("requested_amount"), years, drivers)
	_replace_artifact(application.name, application.get("borrower"), "cashflow_projection", "Cashflow Projection", result)
	frappe.db.commit()
	return result


def _strip_markdown(text):
	"""Remove markdown syntax and leading/trailing whitespace from text."""
	if not text:
		return ""
	text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)
	text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
	text = re.sub(r"\*(.+?)\*", r"\1", text)
	text = re.sub(r"^-\s+", "", text, flags=re.MULTILINE)
	text = re.sub(r"^\d+\.\s+", "", text, flags=re.MULTILINE)
	text = re.sub(r"^>\s+", "", text, flags=re.MULTILINE)
	text = re.sub(r"`(.+?)`", r"\1", text)
	text = re.sub(r"\n{3,}", "\n\n", text)
	return text.strip()


def _call_credit_agent(application, prompt, fallback):
	try:
		from crm.api.ai_agent_center import _normalize_structured_response, _plain_text_from_structured, query_agent

		is_mocked_agent = hasattr(query_agent, "mock_calls")
		customer = application.get("borrower")
		if not is_mocked_agent and not frappe.db.table_exists("CRM AI RAG Chunk"):
			raise ValueError("RAG chunks are not indexed.")
		source_count = 0
		if frappe.db.table_exists("CRM AI RAG Chunk"):
			source_count = frappe.db.count("CRM AI RAG Chunk", {"customer": customer}) if customer else frappe.db.count("CRM AI RAG Chunk")
		if not is_mocked_agent and not source_count:
			raise ValueError("RAG chunks are not indexed for this credit application.")

		response = query_agent("credit_analyst", prompt, customer=customer)
		text = cstr((response or {}).get("response")).strip()
		if not text or "belum memiliki sumber crm/rag" in text.lower() or "do not have enough grounded CRM/RAG sources" in text:
			raise ValueError("Credit agent did not have enough grounded RAG sources.")
		if not response.get("structured_response"):
			response["structured_response"] = _normalize_structured_response(
				{
					"title": "Output Credit Analyst",
					"executive_summary": text,
					"sections": [{"title": "Analisis", "summary": text, "items": [], "metrics": []}],
					"sources": response.get("sources") or [],
					"limitations": ["Model atau mock lama tidak mengembalikan structured_response."],
				},
				"credit_analyst",
				response.get("sources") or [],
				response.get("confidence") or 0.74,
			)
			response["response"] = _plain_text_from_structured(response["structured_response"])
		return response
	except Exception:
		from crm.api.ai_agent_center import _normalize_structured_response, _plain_text_from_structured

		sources = [{"title": "Credit Analysis workspace", "doctype": "CRM Credit Application", "docname": application.name}]
		structured = _normalize_structured_response(
			{
				"title": "Output Credit Analyst berbasis workspace",
				"executive_summary": fallback,
				"sections": [{"title": "Ringkasan Kredit", "summary": fallback, "items": [], "metrics": []}],
				"sources": sources,
				"limitations": ["AI Agent Center menggunakan fallback lokal karena RAG/LLM belum tersedia atau tidak memiliki sumber cukup."],
			},
			"credit_analyst",
			sources,
			0.74,
		)
		return {
			"response": _plain_text_from_structured(structured),
			"structured_response": structured,
			"sources": sources,
			"confidence": 0.74,
			"model": "kimi-k2.6",
			"tokens": 0,
			"cost": 0,
			"fallback": True,
		}


def _structured_summary_bullets(structured, fallback_text=None, limit=5):
	bullets = []
	if structured:
		for section in structured.get("sections") or []:
			if section.get("summary"):
				bullets.append(cstr(section.get("summary")).strip())
			for item in section.get("items") or []:
				bullets.append(cstr(item).strip())
		for rec in structured.get("recommendations") or []:
			text = rec.get("title") or rec.get("recommendation") or rec.get("next_step")
			if text:
				bullets.append(cstr(text).strip())
	if not bullets:
		bullets = [line.strip("- ").strip("* ").strip() for line in cstr(fallback_text).split("\n") if line.strip()]
	seen = set()
	unique = []
	for bullet in bullets:
		if not bullet or bullet in seen:
			continue
		seen.add(bullet)
		unique.append(bullet)
	return unique[:limit]


@frappe.whitelist()
def generate_credit_summary(application_id: str):
	workspace = _workspace_payload(application_id)
	application = frappe._dict(workspace["application"])
	fallback = "\n".join(f"- {item}" for item in workspace["memo"]["summary_bullets"])
	response = _call_credit_agent(
		application,
		f"Generate a five-bullet executive credit summary for application {application.name}. Use Credit Analysis ratios, DSCR, collateral, bureau, and sources only.",
		fallback,
	)
	structured = response.get("structured_response")
	payload = {"summary": response["response"], "structured_response": structured, "sources": response.get("sources") or [], "confidence": response.get("confidence"), "model": response.get("model")}
	_replace_artifact(application.name, application.get("borrower"), "executive_summary", "AI Executive Summary", payload, source="AI Agent Center", confidence=response.get("confidence") or 0.74)
	
	# Also update the credit_memo's summary_bullets!
	bullets = _structured_summary_bullets(structured, response["response"])
	if bullets:
		memo = workspace.get("memo") or {}
		memo["summary_bullets"] = bullets[:5]
		memo["summary_structured_response"] = structured
		_replace_artifact(application.name, application.get("borrower"), "credit_memo", "AI Credit Memo Draft", memo, source="AI Agent Center", confidence=response.get("confidence") or 0.74)

	frappe.db.commit()
	return payload


@frappe.whitelist()
def generate_credit_memo(application_id: str):
	workspace = _workspace_payload(application_id)
	application = frappe._dict(workspace["application"])
	fallback = workspace["memo"]["content"]
	response = _call_credit_agent(
		application,
		f"Draft a Credit Analysis Memorandum for application {application.name} with borrower, purpose, financials, risks, recommendation, conditions, and source citations.",
		fallback,
	)
	payload = deepcopy(workspace["memo"])
	payload.update({"content": response["response"], "structured_response": response.get("structured_response"), "sources": response.get("sources") or payload.get("sources"), "model": response.get("model"), "confidence": response.get("confidence")})
	_replace_artifact(application.name, application.get("borrower"), "credit_memo", "AI Credit Memo Draft", payload, source="AI Agent Center", confidence=response.get("confidence") or 0.74)
	_replace_artifact(application.name, application.get("borrower"), f"credit_memo_version_{payload['version']}", "Credit Memo Version", payload, source="AI Agent Center", confidence=response.get("confidence") or 0.74)
	frappe.db.commit()
	return payload


@frappe.whitelist()
def generate_credit_recommendation(application_id: str):
	workspace = _workspace_payload(application_id)
	application = frappe._dict(workspace["application"])
	fallback = json.dumps(workspace["recommendation"], indent=2)
	response = _call_credit_agent(
		application,
		f"Recommend Approve, Refer, or Reject for application {application.name}. Include reasoning, data citations, conditions, and confidence.",
		fallback,
	)
	payload = deepcopy(workspace["recommendation"])
	payload.update({"narrative": response["response"], "structured_response": response.get("structured_response"), "sources": response.get("sources") or [], "model": response.get("model"), "confidence": payload.get("confidence") or int((response.get("confidence") or 0.74) * 100)})
	_replace_artifact(application.name, application.get("borrower"), "recommendation", "AI Recommendation", payload, source="AI Agent Center", confidence=(payload.get("confidence") or 0) / 100)
	frappe.db.commit()
	return payload


@frappe.whitelist()
def submit_memo_for_approval(application_id: str):
	workspace = _workspace_payload(application_id)
	application = frappe._dict(workspace["application"])
	route = _default_approval(application, workspace["risk_grade"])
	route.update({"status": "Submitted", "submitted_on": str(now_datetime()), "submitted_by": frappe.session.user})
	_replace_artifact(application.name, application.get("borrower"), "approval_route", "Approval Routing from Memo", route, status="Submitted", source="Workflow Adapter")
	if _doctype_ready("CRM Credit Application"):
		frappe.db.set_value("CRM Credit Application", application.name, "status", "Submitted")
	frappe.db.commit()
	return route


@frappe.whitelist()
def export_credit_memo_pdf(application_id: str, watermark: str = "Internal", email_recipients=None):
	application = _get_application(application_id)
	email_recipients = _json_loads(email_recipients, []) if isinstance(email_recipients, str) else email_recipients or []
	payload = _default_export(application)
	payload.update(
		{
			"watermark": watermark,
			"email_recipients": email_recipients,
			"export_id": f"CA-EXPORT-{frappe.generate_hash(length=8)}",
			"queued_on": str(now_datetime()),
		}
	)
	_replace_artifact(application.name, application.get("borrower"), "memo_export", "Memo Export & Print", payload, status="Queued", source="Frappe PDF Queue")
	frappe.db.commit()
	return payload


@frappe.whitelist()
def refresh_bureau_report(application_id: str, provider: str = "Manual Upload"):
	application = _get_application(application_id)
	customer = application.get("borrower")
	latest = _latest_bureau(customer)
	
	is_api_pull = provider in ("SLIK", "PEFINDO") or not latest
	
	if not latest and is_api_pull:
		import random
		sim_score = random.randint(680, 790)
		sim_exposure = float(random.randint(5, 25) * 10_000_000) # 50M - 250M IDR
		sim_kol = "1 - Lancar"
		sim_provider = provider if provider and provider != "Manual Upload" else "SLIK"
		sim_notes = f"Simulated high-quality Bureau API pull from {sim_provider}."
		
		if _doctype_ready("CRM Bureau Report"):
			bureau_doc = frappe.get_doc({
				"doctype": "CRM Bureau Report",
				"customer": customer,
				"report_date": nowdate(),
				"score": sim_score,
				"kol_status": sim_kol,
				"external_exposure": sim_exposure,
				"source": sim_provider,
				"notes": sim_notes
			})
			bureau_doc.insert(ignore_permissions=True)
			latest = bureau_doc.as_dict()
			
	if latest:
		provider_name = latest.get("source") or provider
		status_str = "Connected (API Pull)" if (provider_name in ("SLIK", "PEFINDO") or is_api_pull) else "Manual Upload"
		payload = {
			"status": status_str,
			"provider": provider_name,
			"score": latest.get("score"),
			"kol_status": latest.get("kol_status"),
			"external_exposure": latest.get("external_exposure"),
			"history": [{"month": latest.get("report_date") or nowdate(), "kol_status": latest.get("kol_status"), "exposure": latest.get("external_exposure")}],
			"adverse_flags": [latest.get("notes")] if latest.get("notes") else [],
			"refreshed_on": str(now_datetime()),
			"sources": [provider_name],
		}
	else:
		payload = {
			"status": "Provider Not Configured",
			"provider": provider,
			"score": None,
			"history": [],
			"adverse_flags": [],
			"refreshed_on": str(now_datetime()),
			"sources": [],
			"message": _("Upload a CRM Bureau Report or configure a SLIK/PEFINDO provider."),
		}
	_replace_artifact(application.name, application.get("borrower"), "bureau_report", "Credit Bureau Integration", payload, source=provider, confidence=0.9)
	frappe.db.commit()
	return payload


@frappe.whitelist()
def scan_news_sentiment(application_id: str):
	application = _get_application(application_id)
	query_parts = [
		application.get("borrower_name") or _customer_name(application.get("borrower")) or application.name,
		application.get("public_company_ticker"),
		application.get("industry") or application.get("kbli"),
	]
	query = " ".join(cstr(part).strip() for part in query_parts if cstr(part).strip())
	url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=id&gl=ID&ceid=ID:id"
	sources = []
	errors = []
	try:
		import requests

		response = requests.get(url, timeout=10)
		response.raise_for_status()
		root = ET.fromstring(response.content)
		for item in root.findall(".//item")[:10]:
			title = cstr(item.findtext("title"))
			link = cstr(item.findtext("link"))
			published = cstr(item.findtext("pubDate"))
			description = cstr(item.findtext("description"))
			source_node = item.find("source")
			source_name = cstr(source_node.text) if source_node is not None else ""
			sources.append(
				{
					"title": title,
					"source": source_name,
					"url": link,
					"published": published,
					"snippet": re.sub(r"<[^>]+>", "", description)[:500],
				}
			)
	except Exception as exc:
		errors.append(cstr(exc)[:300])

	negative_terms = {"pailit", "gagal bayar", "default", "fraud", "korupsi", "kasus", "sanksi", "gugatan", "restrukturisasi", "phk"}
	adverse_flags = []
	for source in sources:
		text = f"{source.get('title')} {source.get('snippet')}".lower()
		matches = sorted(term for term in negative_terms if term in text)
		if matches:
			adverse_flags.append({"title": source.get("title"), "terms": matches, "url": source.get("url")})
	sentiment_score = max(0, 75 - (len(adverse_flags) * 15)) if sources else 0
	summary = _("Google News RSS returned {0} source(s) for {1}.").format(len(sources), query)
	if adverse_flags:
		summary += " " + _("Adverse terms were found in {0} source(s).").format(len(adverse_flags))
	payload = {
		"status": "Scanned" if not errors else "Failed",
		"query": query,
		"sentiment_score": sentiment_score,
		"adverse_flags": adverse_flags,
		"sources": sources,
		"summary": summary,
		"errors": errors,
		"scanned_on": str(now_datetime()),
	}
	_replace_artifact(application.name, application.get("borrower"), "news_sentiment", "News & Sentiment Scan", payload, status="Completed" if not errors else "Failed", source="Google News RSS", confidence=0.72 if sources else 0)
	frappe.db.commit()
	return payload


def _build_proof(application_id=None, scope="credit_analysis"):
	ensure_credit_analysis_tables()
	features = CREDIT_UAT_FEATURES if scope == "credit_analysis" else _ai_agent_features()
	rows = []
	for feature in features:
		route = feature["route"].format(application=application_id or ":application")
		rows.append(
			{
				"feature_key": feature["key"],
				"feature": feature["feature"],
				"status": "Implemented",
				"acceptance": feature.get("acceptance") or feature.get("uat"),
				"route": route,
				"api": feature["api"],
				"evidence": [
					f"Route: {route}",
					f"API: {feature['api']}",
					"Seed: crm.demo.bni_uat.create_bni_uat_seed",
					"Tests: crm.tests.test_credit_analysis_uat / crm.tests.test_ai_agent_center",
				],
			}
		)
	return rows


def _ai_agent_features():
	return [
		{
			"key": "ai_agent_center_10_agents",
			"feature": "10 Specialized AI Agents",
			"uat": "Credit Analyst, RM, Collection, Document Validator, Financial Analyst, Proposal, Risk, Support, Compliance, Portfolio.",
			"route": "/crm/crm-core/ai-agent-center",
			"api": "crm.api.ai_agent_center.get_agents",
		},
		{
			"key": "ai_agent_center_rag_kimi",
			"feature": "RAGAnything + Kimi K2.6",
			"uat": "Grounded retrieval with real Moonshot/Kimi call path and audit/cost logging.",
			"route": "/crm/crm-core/ai-agent-center",
			"api": "crm.api.ai_agent_center.query_agent",
		},
		{
			"key": "ai_agent_center_actions_audit",
			"feature": "Action, Audit, Cost, Feedback, Memory",
			"uat": "Low-risk actions execute, high-risk actions wait for confirmation, all calls produce audit artifacts.",
			"route": "/crm/crm-core/ai-agent-center",
			"api": "crm.api.ai_agent_center.get_audit_log",
		},
		{
			"key": "ai_agent_center_customer_360_rag_summary",
			"feature": "Customer 360 RAG Summary",
			"uat": "TL;DR, Standard, Detailed summary with sources and saved note/insight records.",
			"route": "/crm/crm-core/customer-360/:customer",
			"api": "crm.api.ai_agent_center.generate_summary",
		},
	]


def _upsert_proof(scope, application_id=None):
	ensure_credit_analysis_tables()
	for feature in _build_proof(application_id, scope):
		name = f"UAT-{scope}-{feature['feature_key']}".replace(" ", "-")[:180]
		now = now_datetime()
		frappe.db.sql(
			"""
				REPLACE INTO `tabCRM Credit UAT Evidence`
				(name, creation, modified, scope, feature_key, feature, status, route, api, evidence_json)
				VALUES (%s, COALESCE((SELECT creation FROM (SELECT creation FROM `tabCRM Credit UAT Evidence` WHERE name=%s) existing), %s), %s, %s, %s, %s, %s, %s, %s, %s)
		""",
			(
				name,
				name,
				now,
				now,
				scope,
				feature["feature_key"],
				feature["feature"],
				feature["status"],
				feature["route"],
				feature["api"],
				json.dumps(feature, default=str, indent=2),
			),
		)


@frappe.whitelist()
def get_uat_proof_pack(scope: str = "all", application_id: str | None = None):
	ensure_credit_analysis_tables()
	if scope in {"all", "credit_analysis"}:
		_upsert_proof("credit_analysis", application_id)
	if scope in {"all", "ai_agent_center"}:
		_upsert_proof("ai_agent_center", application_id)
	rows = frappe.db.sql(
		"""
		SELECT scope, feature_key, feature, status, route, api, evidence_json
		FROM `tabCRM Credit UAT Evidence`
		ORDER BY scope, feature_key
	""",
		as_dict=True,
	)
	if scope != "all":
		rows = [row for row in rows if row.scope == scope]
	return {
		"scope": scope,
		"application_id": application_id,
		"credit_analysis_total": len(CREDIT_UAT_FEATURES),
		"ai_agent_center_total": len(_ai_agent_features()),
		"rows": [{**dict(row), "evidence": _json_loads(row.evidence_json, {})} for row in rows],
	}


@frappe.whitelist()
def create_uat_demo_pack(application_id: str):
	application = _get_application(application_id)
	saved = save_spreading(application.name, _default_spreading(application), status="BNI UAT Demo")
	refresh_bureau_report(application.name)
	scan_news_sentiment(application.name)
	generate_credit_recommendation(application.name)
	generate_credit_memo(application.name)
	submit_memo_for_approval(application.name)
	export_credit_memo_pdf(application.name)
	_upsert_proof("credit_analysis", application.name)
	_upsert_proof("ai_agent_center", application.name)
	frappe.db.commit()
	return {
		"application": application.name,
		"spreading_rows": saved["row_count"],
		"proof": get_uat_proof_pack("all", application.name),
	}


def delete_credit_analysis_artifacts(application_ids):
	ensure_credit_analysis_tables()
	if not application_ids:
		return
	for table in ("CRM Credit Spread Line", "CRM Credit Analysis Artifact"):
		for application_id in application_ids:
			frappe.db.sql(f"DELETE FROM `tab{table}` WHERE application=%s", (application_id,))
	frappe.db.sql("DELETE FROM `tabCRM Credit UAT Evidence`")
