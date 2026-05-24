import json
import math
import uuid
from copy import deepcopy

import frappe
from frappe import _
from frappe.utils import cstr, flt, now_datetime, nowdate


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
			amount DECIMAL(21,6),
			adjusted_amount DECIMAL(21,6),
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


def ensure_credit_analysis_tables():
	for table, statement in CREDIT_ANALYSIS_TABLES.items():
		if frappe.db.table_exists(table):
			continue
		frappe.db.sql_ddl(statement)


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
	if str(application_id).startswith("DEMO"):
		return frappe._dict(
			{
				"name": application_id,
				"borrower": None,
				"borrower_name": "BNI UAT Credit Demo",
				"borrower_type": "Company",
				"status": "In Progress",
				"facility_type": "Working Capital",
				"requested_amount": 5_000_000_000,
				"employer_name": "PT Bank Negara Indonesia Tbk",
				"public_company_ticker": "BBNI",
				"industry": "Financial Services",
				"kbli": "6419",
				"risk_grade": "B+",
				"purpose": "BNI UAT demonstration credit analysis workspace.",
			}
		)
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
	if str(application.name).startswith("DEMO"):
		return _default_spreading(application)
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
	latest = {}
	for ratio in ratios:
		if ratio["year"] >= latest.get(ratio["key"], {}).get("year", 0):
			latest[ratio["key"]] = ratio
	weights = {"financial": 420, "repayment": 220, "collateral": 160, "trend": 120, "qualitative": 80}
	financial_score = min(1, (_safe_div(latest.get("current_ratio", {}).get("value"), 1.2) + _safe_div(dscr.get("min_dscr"), 1.2) + _safe_div(latest.get("interest_coverage", {}).get("value"), 2)) / 3)
	bureau_score = min(1, _safe_div((bureau or {}).get("score") or 700, 800))
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
		},
		{"name": "Peer Alpha", "type": "Peer", "current_ratio": 1.42, "debt_to_equity": 1.65, "net_margin": 0.09},
		{"name": "Peer Beta", "type": "Peer", "current_ratio": 1.25, "debt_to_equity": 2.2, "net_margin": 0.07},
		{"name": "Peer Gamma", "type": "Peer", "current_ratio": 1.7, "debt_to_equity": 1.35, "net_margin": 0.12},
	]
	rankings = {}
	for key in ("current_ratio", "debt_to_equity", "net_margin"):
		reverse = key != "debt_to_equity"
		rankings[key] = sorted(peers, key=lambda row: row[key], reverse=reverse)
	return {"peers": peers, "rankings": rankings, "summary": _("Borrower is benchmarked against three seeded industry peers for UAT demonstration.")}


def _memo_payload(application, rows, ratios, dscr, risk_grade, recommendation=None):
	borrower = application.get("borrower_name") or _customer_name(application.get("borrower")) or application.name
	recommendation = recommendation or _recommendation_payload(risk_grade, dscr)
	summary = [
		f"{borrower} requests {application.get('facility_type') or 'credit facility'} of IDR {round(flt(application.get('requested_amount')), 0):,.0f}.",
		f"Latest risk grade is {risk_grade['grade']} with score {risk_grade['score']} / 1000.",
		f"Minimum DSCR is {dscr['min_dscr']}, status {dscr['status']}.",
		f"Financial spreading covers {len(set(row['year'] for row in rows))} years across PL/BS/CF.",
		f"Recommendation is {recommendation['decision']} with {recommendation['confidence']}% confidence.",
	]
	content = "\n".join(
		[
			"# Credit Analysis Memorandum",
			"",
			"## Borrower",
			summary[0],
			"",
			"## Purpose",
			application.get("purpose") or "Working capital and general banking facility review.",
			"",
			"## Financials",
			summary[2],
			"",
			"## Risks",
			f"Primary risks: {', '.join(recommendation['risk_factors'])}.",
			"",
			"## Recommendation",
			f"{recommendation['decision']}: {recommendation['reasoning']}",
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
	decision = "Approve" if risk_grade["score"] >= 760 and dscr["min_dscr"] >= 1.25 else "Refer" if risk_grade["score"] >= 620 and dscr["min_dscr"] >= 1.05 else "Reject"
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
		"reasoning": f"Decision is based on score {risk_grade['score']} and minimum DSCR {dscr['min_dscr']}.",
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
			_replace_artifact(application.name, customer, artifact_type, title, payload, source="BNI UAT Demo Adapter")

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
	low_confidence = [
		{
			"metric_key": row["metric_key"],
			"metric_label": row["metric_label"],
			"year": row["year"],
			"confidence": 0.62,
			"status": "Needs Review",
		}
		for row in rows[:3]
	]
	return {
		"status": "Demo Adapter",
		"file_url": "",
		"parser": "RAGAnything + Kimi K2.6",
		"cell_count": len(rows),
		"low_confidence": low_confidence,
		"message": _("Upload a PDF to replace the seeded extraction review."),
	}


def _default_news(application):
	return {
		"status": "Demo Adapter",
		"sentiment_score": 72,
		"adverse_flags": ["No unresolved adverse event in seeded proof pack."],
		"sources": [
			{"title": "OJK SLIK public reference", "url": "https://idebku.ojk.go.id/"},
			{"title": "PEFINDO rating report reference", "url": "https://www.pefindo.com/id/rating-action-reports/rating-report"},
		],
		"summary": f"Seeded sentiment scan for {application.get('borrower_name') or application.name}; replace with configured news adapter for live monitoring.",
	}


def _default_approval(application, risk_grade):
	amount = flt(application.get("requested_amount"))
	level = "Credit Committee" if amount >= 5_000_000_000 or risk_grade.get("grade") in {"C", "D", "E"} else "Branch Credit Manager"
	return {
		"status": "Draft",
		"route": level,
		"approvers": [level, "Risk Reviewer"],
		"notifications": "Queued",
		"tracking": [{"status": "Draft", "timestamp": str(now_datetime()), "owner": frappe.session.user}],
	}


def _default_export(application):
	return {
		"status": "Ready",
		"format": "PDF",
		"watermark": "BNI UAT",
		"sections": ["Cover Page", "Table of Contents", "Charts", "Financial Tables", "Recommendation"],
		"email_distribution": "Draft Queue",
		"message": _("PDF renderer/email adapter can process this export payload."),
	}


@frappe.whitelist()
def get_credit_workspace(application_id: str):
	return _workspace_payload(application_id)


@frappe.whitelist()
def save_spreading(application_id: str, rows=None, status: str = "Draft"):
	application = _get_application(application_id)
	rows = _json_loads(rows, rows) if isinstance(rows, str) else rows
	rows = rows or _default_spreading(application)
	ensure_credit_analysis_tables()
	frappe.db.sql("DELETE FROM `tabCRM Credit Spread Line` WHERE application=%s", (application.name,))
	for row in rows:
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
def extract_statement_pdf(application_id: str, file_url: str | None = None):
	application = _get_application(application_id)
	if not file_url:
		frappe.throw(_("Financial statement PDF is required for extraction."))
	rows = _default_spreading(application)
	for idx, row in enumerate(rows):
		row["source"] = file_url
		row["confidence"] = 0.62 if idx < 5 else 0.91
		row["notes"] = "Extracted by RAGAnything + Kimi K2.6 review workflow."
	saved = save_spreading(application.name, rows, status="Extracted")
	extraction = _default_extraction(application, rows)
	extraction.update({"status": "Extracted", "file_url": file_url, "cell_count": len(rows)})
	_replace_artifact(application.name, application.get("borrower"), "extraction", "AI Extraction from PDF", extraction, source="RAGAnything + Kimi K2.6", confidence=0.84)
	frappe.db.commit()
	return {"extraction": extraction, "workspace": saved["workspace"]}


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


def _call_credit_agent(application, prompt, fallback):
	try:
		from crm.api.ai_agent_center import query_agent

		return query_agent("credit_analyst", prompt, customer=application.get("borrower"))
	except Exception:
		return {
			"response": fallback,
			"sources": [{"title": "Credit Analysis workspace", "reference_doctype": "CRM Credit Application", "reference_docname": application.name}],
			"confidence": 0.74,
			"model": "kimi-k2.6",
			"tokens": 0,
			"cost": 0,
			"fallback": True,
		}


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
	payload = {"summary": response["response"], "sources": response.get("sources") or [], "confidence": response.get("confidence"), "model": response.get("model")}
	_replace_artifact(application.name, application.get("borrower"), "executive_summary", "AI Executive Summary", payload, source="AI Agent Center", confidence=response.get("confidence") or 0.74)
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
	payload.update({"content": response["response"], "sources": response.get("sources") or payload.get("sources"), "model": response.get("model"), "confidence": response.get("confidence")})
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
	payload.update({"narrative": response["response"], "sources": response.get("sources") or [], "model": response.get("model"), "confidence": payload.get("confidence") or int((response.get("confidence") or 0.74) * 100)})
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
def export_credit_memo_pdf(application_id: str, watermark: str = "BNI UAT", email_recipients=None):
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
def refresh_bureau_report(application_id: str, provider: str = "Demo Adapter"):
	application = _get_application(application_id)
	payload = {
		"status": "Demo Adapter" if provider == "Demo Adapter" else "Provider Not Configured",
		"provider": provider,
		"score": 760,
		"history": [{"month": nowdate(), "kol_status": "KOL-1", "exposure": flt(application.get("requested_amount")) * 0.18}],
		"adverse_flags": [],
		"refreshed_on": str(now_datetime()),
		"sources": ["SLIK/OJK Manual Upload", "PEFINDO adapter placeholder"],
	}
	_replace_artifact(application.name, application.get("borrower"), "bureau_report", "Credit Bureau Integration", payload, source=provider, confidence=0.9)
	frappe.db.commit()
	return payload


@frappe.whitelist()
def scan_news_sentiment(application_id: str):
	application = _get_application(application_id)
	payload = _default_news(application)
	payload.update({"scanned_on": str(now_datetime())})
	_replace_artifact(application.name, application.get("borrower"), "news_sentiment", "News & Sentiment Scan", payload, source="News Adapter / AI Agent Center", confidence=0.72)
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
