import json
import re

import frappe
from frappe import _
from frappe.utils import cstr, date_diff, flt, getdate, now_datetime, nowdate


PUBLIC_SOURCE_URLS = {
	"idx_xbrl": "https://www.idx.id/en/listed-companies/xbrl/",
	"pefindo": "https://www.pefindo.com/id/rating-action-reports/rating-report",
	"ojk_slik": "https://www.ojk.go.id/id/kanal/perbankan/Pages/Sistem-Layanan-Informasi-Keuangan-SLIK.aspx",
	"idebku": "https://idebku.ojk.go.id/",
}

CREDIT_DOCTYPES = {
	"CRM Credit Application",
	"CRM Public Company Snapshot",
	"CRM Bureau Report",
	"CRM Credit Facility",
	"CRM Collateral",
	"CRM KYC Review",
	"CRM Relationship",
	"CRM Financial Statement",
	"CRM Credit Spread Line",
	"CRM Credit Analysis Artifact",
	"CRM Credit UAT Evidence",
	"CRM Site Visit",
	"CRM Bank Account",
	"CRM Customer Document",
	"CRM Customer Communication",
	"CRM Transaction History",
	"CRM Risk Profile",
	"CRM AI Insight",
	"CRM Customer Tag",
	"CRM Customer Merge Audit",
}

CUSTOMER_360_INSERT_DOCTYPES = CREDIT_DOCTYPES | {"CRM Task", "FCRM Note", "Event"}
CUSTOMER_360_CUSTOMER_FIELD_DOCTYPES = {
	"CRM KYC Review",
	"CRM Credit Facility",
	"CRM Collateral",
	"CRM Bureau Report",
	"CRM Relationship",
	"CRM Financial Statement",
	"CRM Site Visit",
	"CRM Bank Account",
	"CRM Customer Document",
	"CRM Customer Communication",
	"CRM Transaction History",
	"CRM Risk Profile",
	"CRM AI Insight",
	"CRM Customer Tag",
}
LARGE_CURRENCY_SQL_TYPE = "decimal(30,9)"
CUSTOMER_360_ADAPTERS = {
	"ekyc": {
		"label": "Dukcapil / e-KYC",
		"required_configuration": "Configure an official Dukcapil/e-KYC provider credential and consent workflow.",
	},
	"aml_pep": {
		"label": "AML / PEP Screening",
		"required_configuration": "Configure an AML/PEP screening provider and match review queue.",
	},
	"bureau": {
		"label": "SLIK / Pefindo Bureau",
		"required_configuration": "Configure SLIK/Pefindo sandbox or production credential with borrower consent storage.",
	},
	"core_banking": {
		"label": "Core Banking Facility Feed",
		"required_configuration": "Configure core banking account, facility, repayment, and outstanding balance feed.",
	},
	"account_otp": {
		"label": "Bank Account OTP Verification",
		"required_configuration": "Configure bank account verification or OTP provider.",
	},
	"collateral_registry": {
		"label": "Collateral Registry / Appraisal Feed",
		"required_configuration": "Configure collateral registry, appraisal, and insurance validation provider.",
	},
}


def _doctype_ready(doctype: str) -> bool:
	try:
		return frappe.db.table_exists(doctype)
	except Exception:
		return False


def _get_customer_label(customer: str | None) -> str:
	if not customer:
		return ""
	return frappe.db.get_value("Customer", customer, "customer_name") or customer


def _ensure_large_currency_columns(doctype: str):
	if not _doctype_ready(doctype):
		return
	meta = frappe.get_meta(doctype)
	currency_fields = [field.fieldname for field in meta.fields if field.fieldtype == "Currency" and field.fieldname]
	if not currency_fields:
		return
	for fieldname in currency_fields:
		column = frappe.db.sql(f"SHOW COLUMNS FROM `tab{doctype}` LIKE %s", fieldname, as_dict=True)
		if not column:
			continue
		column_type = cstr(column[0].get("Type")).lower()
		if column_type != LARGE_CURRENCY_SQL_TYPE:
			frappe.db.change_column_type(doctype, fieldname, LARGE_CURRENCY_SQL_TYPE)


def _valid_link_value(link_doctype: str | None, value) -> bool:
	if not link_doctype or not value:
		return True
	try:
		return bool(frappe.db.exists(link_doctype, value))
	except Exception:
		return False


def _normalize_link_values(doctype: str, doc):
	meta = frappe.get_meta(doctype)
	for field in meta.fields:
		fieldname = field.fieldname
		if not fieldname or not doc.get(fieldname):
			continue
		value = doc.get(fieldname)
		if isinstance(value, str):
			value = re.sub(r"\s+", " ", value.strip())
			doc[fieldname] = value
		if not value:
			continue
		if field.fieldtype == "Link":
			if _valid_link_value(field.options, value):
				continue
			if field.reqd:
				frappe.throw(_("{0} not found: {1}").format(field.label or fieldname, value))
			doc[fieldname] = None
		elif field.fieldtype == "Dynamic Link":
			reference_field = field.options
			reference_doctype = doc.get(reference_field)
			if _valid_link_value(reference_doctype, value):
				continue
			if field.reqd:
				frappe.throw(_("{0} not found: {1}").format(field.label or fieldname, value))
			doc[fieldname] = None


def _normalize_numeric_values(doctype: str, doc):
	meta = frappe.get_meta(doctype)
	for field in meta.fields:
		fieldname = field.fieldname
		if not fieldname or fieldname not in doc:
			continue
		value = doc.get(fieldname)
		if value == "":
			doc[fieldname] = 0
			continue
		if field.fieldtype in {"Currency", "Float", "Percent"}:
			doc[fieldname] = flt(value)
		elif field.fieldtype == "Int":
			doc[fieldname] = int(flt(value))


def _json_loads(value):
	if not value:
		return {}
	if isinstance(value, dict):
		return value
	try:
		return json.loads(value)
	except Exception:
		return {}


@frappe.whitelist()
def ensure_credit_doctype_modules():
	"""Repair local DB rows created with the wrong module before inserting records."""
	updated = []
	for doctype in CREDIT_DOCTYPES:
		if frappe.db.exists("DocType", doctype) and frappe.db.get_value("DocType", doctype, "module") != "FCRM":
			frappe.db.set_value("DocType", doctype, "module", "FCRM", update_modified=False)
			frappe.clear_cache(doctype=doctype)
			updated.append(doctype)
	return {"updated": updated}


@frappe.whitelist()
def create_customer_360_record(doctype: str, doc: dict):
	return create_or_update_customer360_record(doctype, doc)


@frappe.whitelist()
def create_or_update_customer360_record(doctype: str, doc: dict):
	if doctype not in CUSTOMER_360_INSERT_DOCTYPES:
		frappe.throw(_("Cannot create records for {0} from Customer 360").format(doctype))

	ensure_credit_doctype_modules()
	_ensure_large_currency_columns(doctype)
	doc = frappe._dict(doc or {})
	doc.doctype = doctype
	_normalize_numeric_values(doctype, doc)
	_normalize_select_values(doctype, doc)
	_normalize_link_values(doctype, doc)
	_validate_customer360_doc(doctype, doc)
	if doc.get("name") and frappe.db.exists(doctype, doc.name):
		existing = frappe.get_doc(doctype, doc.name)
		existing.update(doc)
		existing.save()
		return existing.as_dict()
	return frappe.get_doc(doc).insert().as_dict()


@frappe.whitelist()
def update_customer_profile(customer: str, payload: dict):
	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer not found"))
	payload = frappe._dict(payload or {})
	allowed_fields = {"customer_name", "customer_type", "customer_group", "territory", "website", "tax_id"}
	for fieldname, value in payload.items():
		if fieldname in allowed_fields:
			frappe.db.set_value("Customer", customer, fieldname, value)
	return frappe.get_doc("Customer", customer).as_dict()


@frappe.whitelist()
def save_customer_summary(customer: str, summary: str, structured_response=None, sources=None, confidence=None, limitations=None):
	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer not found"))
	summary = cstr(summary).strip()
	if not summary:
		frappe.throw(_("Summary is required"))
	structured_response = _json_loads(structured_response) if isinstance(structured_response, str) else structured_response or {}
	sources = _json_loads(sources) if isinstance(sources, str) else sources or []
	limitations = _json_loads(limitations) if isinstance(limitations, str) else limitations or []
	existing = None
	if _doctype_ready("FCRM Note"):
		rows = frappe.get_all(
			"FCRM Note",
			fields=["name"],
			filters={
				"reference_doctype": "Customer",
				"reference_docname": customer,
				"title": "AI Customer Summary",
			},
			order_by="modified desc",
			limit=1,
		)
		existing = rows[0].name if rows else None
	if existing:
		doc = frappe.get_doc("FCRM Note", existing)
		doc.content = summary
		doc.save()
	else:
		doc = frappe.get_doc(
			{
				"doctype": "FCRM Note",
				"title": "AI Customer Summary",
				"content": summary,
				"reference_doctype": "Customer",
				"reference_docname": customer,
		}
	).insert()
	if structured_response:
		_save_customer_summary_insights(customer, structured_response, sources, confidence, limitations)
	return doc.as_dict()


def _save_customer_summary_insights(customer: str, structured_response: dict, sources=None, confidence=None, limitations=None):
	if not _doctype_ready("CRM AI Insight"):
		return []
	created = []
	recommendations = structured_response.get("recommendations") or []
	actions = structured_response.get("actions") or []
	items = recommendations if isinstance(recommendations, list) else []
	for action in actions if isinstance(actions, list) else []:
		if isinstance(action, dict):
			items.append(
				{
					"title": action.get("title") or action.get("label") or action.get("action_key") or "AI next action",
					"detail": action.get("description") or action.get("reason") or "",
					"priority": action.get("priority") or "",
				}
			)
	for index, item in enumerate(items[:5], start=1):
		if isinstance(item, str):
			title = item[:140]
			detail = item
		else:
			title = cstr(item.get("title") or item.get("recommendation") or f"AI recommendation {index}")[:140]
			detail = cstr(item.get("detail") or item.get("description") or item.get("rationale") or item)
		doc = frappe.get_doc(
			{
				"doctype": "CRM AI Insight",
				"customer": customer,
				"insight_type": "Cross-sell" if "cross" in title.lower() else "Risk",
				"title": title or f"AI recommendation {index}",
				"confidence_score": flt(confidence or structured_response.get("confidence") or 0) * 100
				if flt(confidence or structured_response.get("confidence") or 0) <= 1
				else flt(confidence or structured_response.get("confidence") or 0),
				"status": "Open",
				"suggested_action": detail[:1000],
				"notes": json.dumps(
					{
						"source": "AI Customer Summary",
						"sources": sources or structured_response.get("sources") or [],
						"limitations": limitations or structured_response.get("limitations") or [],
						"generated_at": now_datetime(),
					},
					default=str,
					indent=2,
				),
			}
		).insert(ignore_permissions=True)
		created.append(doc.name)
	return created


@frappe.whitelist()
def global_customer_search(query: str = "", limit: int = 20):
	query = cstr(query).strip()
	if not query:
		return []
	limit = int(limit or 20)
	customer_fields = _customer_fields()
	customers = frappe.get_all("Customer", fields=customer_fields, limit=200, order_by="modified desc")
	kyc_by_customer = {}
	if _doctype_ready("CRM KYC Review"):
		for row in frappe.get_all("CRM KYC Review", fields=["customer", "npwp", "nik", "registered_address"], limit=500):
			kyc_by_customer.setdefault(row.customer, row)
	query_folded = query.lower()
	results = []
	for customer in customers:
		kyc = kyc_by_customer.get(customer.name, {})
		haystack = [
			customer.get("name"),
			customer.get("customer_name"),
			customer.get("customer_type"),
			customer.get("territory"),
			customer.get("tax_id"),
			customer.get("mobile_no"),
			customer.get("email_id"),
			kyc.get("npwp"),
			kyc.get("nik"),
			kyc.get("registered_address"),
		]
		score = _fuzzy_score(query_folded, haystack)
		if score:
			results.append(
				{
					**customer,
					"npwp": kyc.get("npwp"),
					"nik": kyc.get("nik"),
					"preview": _("{0} - {1} - {2}").format(
						customer.get("customer_name") or customer.name,
						kyc.get("npwp") or customer.get("tax_id") or "No NPWP",
						kyc.get("nik") or customer.get("mobile_no") or "No KTP/Phone",
					),
					"score": score,
				}
			)
	return sorted(results, key=lambda row: row["score"], reverse=True)[:limit]


@frappe.whitelist()
def get_customer_360_table(query: str = "", filters=None, limit: int = 100):
	query = cstr(query).strip().lower()
	limit = int(limit or 100)
	customers = frappe.get_all("Customer", fields=_customer_fields(), limit=limit, order_by="modified desc")
	rows = []
	for customer in customers:
		if query:
			searchable = " ".join(
				cstr(customer.get(fieldname))
				for fieldname in ("name", "customer_name", "customer_type", "customer_group", "territory", "tax_id")
			).lower()
			if query not in searchable:
				kyc_search = _latest_record("CRM KYC Review", customer.name) or {}
				searchable = f"{searchable} {kyc_search.get('npwp') or ''} {kyc_search.get('nik') or ''}".lower()
				if query not in searchable:
					continue
		profile = get_customer_360(customer.name)
		summary = profile.get("summary") or {}
		kyc = profile.get("kyc") or {}
		tags = ", ".join(row.get("tag") for row in profile.get("tags", []) if row.get("tag"))
		rows.append(
			{
				"name": customer.name,
				"customer_name": customer.get("customer_name") or customer.name,
				"customer_type": customer.get("customer_type") or "",
				"customer_group": customer.get("customer_group") or "",
				"territory": customer.get("territory") or "",
				"npwp": kyc.get("npwp") or customer.get("tax_id") or "",
				"nik": kyc.get("nik") or "",
				"kyc_status": summary.get("kyc_status") or "Pending",
				"risk_grade": summary.get("risk_grade") or "Unrated",
				"score": summary.get("score") or 0,
				"total_outstanding": summary.get("total_outstanding") or 0,
				"active_facilities": summary.get("active_facilities") or 0,
				"watchlist": summary.get("watchlist") or False,
				"tags": tags,
				"modified": customer.get("modified"),
			}
		)
	return rows


@frappe.whitelist()
def get_credit_analysis_table(query: str = "", limit: int = 100):
	query = cstr(query).strip().lower()
	rows = get_credit_application_queue()[: int(limit or 100)]
	if not query:
		return rows
	return [
		row
		for row in rows
		if query
		in " ".join(
			cstr(row.get(fieldname))
			for fieldname in (
				"name",
				"borrower_name",
				"borrower_type",
				"status",
				"facility_type",
				"employer_name",
				"public_company_ticker",
				"risk_grade",
			)
		).lower()
	]


@frappe.whitelist()
def export_customer_profile(customer: str, scope: str = "Full Profile", watermark: str = "", password: str = ""):
	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer not found"))
	payload = {
		"doctype": "CRM Customer Document",
		"customer": customer,
		"document_type": "Other",
		"title": _("Customer 360 Export - {0}").format(scope or "Full Profile"),
		"folder": "Exports",
		"version": "1",
		"expiry_status": "Not Applicable",
		"preview_status": "Unavailable",
		"tags": "export,pdf",
		"notes": json.dumps(
			{
				"scope": scope,
				"watermark": watermark,
				"password_protected": bool(password),
				"status": "Export request captured. PDF renderer/email adapter can process this record.",
			},
			indent=2,
		),
	}
	if _doctype_ready("CRM Customer Document"):
		return frappe.get_doc(payload).insert().as_dict()
	return payload


@frappe.whitelist()
def merge_customers(source: str, target: str, field_map=None, confirm: int = 0):
	if not source or not target or source == target:
		frappe.throw(_("Select two different customers to merge."))
	if not frappe.db.exists("Customer", source) or not frappe.db.exists("Customer", target):
		frappe.throw(_("Source or target customer not found."))
	field_map = field_map or {}
	if isinstance(field_map, str):
		field_map = _json_loads(field_map)
	reassigned = []
	status = "Preview"
	if int(confirm or 0):
		for doctype in CUSTOMER_360_CUSTOMER_FIELD_DOCTYPES:
			if not _doctype_ready(doctype):
				continue
			for row in frappe.get_all(doctype, fields=["name"], filters={"customer": source}, limit=500):
				frappe.db.set_value(doctype, row.name, "customer", target)
				reassigned.append(f"{doctype}:{row.name}")
		if _doctype_ready("CRM Credit Application"):
			for row in frappe.get_all("CRM Credit Application", fields=["name"], filters={"borrower": source}, limit=500):
				frappe.db.set_value("CRM Credit Application", row.name, "borrower", target)
				reassigned.append(f"CRM Credit Application:{row.name}")
		for doctype in ("CRM Task", "FCRM Note", "Event"):
			if not _doctype_ready(doctype):
				continue
			for row in frappe.get_all(
				doctype,
				fields=["name"],
				filters={"reference_doctype": "Customer", "reference_docname": source},
				limit=500,
			):
				frappe.db.set_value(doctype, row.name, "reference_docname", target)
				reassigned.append(f"{doctype}:{row.name}")
		for fieldname, winner in field_map.items():
			if winner == "source" and frappe.get_meta("Customer").has_field(fieldname):
				frappe.db.set_value("Customer", target, fieldname, frappe.db.get_value("Customer", source, fieldname))
		status = "Merged"

	audit_payload = {
		"doctype": "CRM Customer Merge Audit",
		"source_customer": source,
		"target_customer": target,
		"status": status,
		"field_map_json": json.dumps(field_map, indent=2),
		"reassigned_doctypes": "\n".join(reassigned) if reassigned else "Preview only",
		"old_ids": source,
		"notes": _("Merge {0}. Source customer is retained for audit traceability.").format(status.lower()),
	}
	if _doctype_ready("CRM Customer Merge Audit"):
		return frappe.get_doc(audit_payload).insert().as_dict()
	return audit_payload


def _fuzzy_score(query: str, values):
	score = 0
	query_digits = _only_digits(query)
	for value in values:
		value = cstr(value).lower()
		if not value:
			continue
		if query in value:
			score = max(score, 100 if value == query else 80)
		else:
			parts = [part for part in query.split() if part]
			if parts and all(part in value for part in parts):
				score = max(score, 60)
		if query_digits and query_digits in _only_digits(value):
			score = max(score, 90)
	return score


@frappe.whitelist()
def create_customer_360_customer(customer_name: str, customer_type: str = "Company"):
	if not customer_name:
		frappe.throw(_("Customer name is required"))

	customer_group = _first_leaf_value("Customer Group", "customer_group_name") or _first_leaf_value(
		"Customer Group", "name"
	)
	territory = _first_leaf_value("Territory", "territory_name") or _first_leaf_value("Territory", "name")

	if not customer_group:
		frappe.throw(_("Create at least one non-group Customer Group before adding customers."))

	doc = {
		"doctype": "Customer",
		"customer_name": customer_name,
		"customer_type": customer_type or "Company",
		"customer_group": customer_group,
	}
	if territory:
		doc["territory"] = territory

	return frappe.get_doc(doc).insert().as_dict()


@frappe.whitelist()
def create_credit_application(payload=None):
	payload = frappe._dict(_json_loads(payload) if isinstance(payload, str) else payload or {})
	_ensure_large_currency_columns("CRM Credit Application")
	borrower = payload.get("borrower")
	borrower_name = cstr(payload.get("borrower_name")).strip()
	borrower_type = payload.get("borrower_type") or "Company"

	if borrower and not frappe.db.exists("Customer", borrower):
		frappe.throw(_("Borrower customer not found."))
	if not borrower:
		if not borrower_name:
			frappe.throw(_("Borrower name is required."))
		customer = create_customer_360_customer(borrower_name, customer_type=borrower_type)
		borrower = customer.get("name")
	else:
		borrower_name = borrower_name or _get_customer_label(borrower)

	if not payload.get("facility_type"):
		frappe.throw(_("Facility type is required."))
	if flt(payload.get("requested_amount")) <= 0:
		frappe.throw(_("Requested amount must be greater than zero."))

	app_fields = {
		"borrower": borrower,
		"borrower_name": borrower_name,
		"borrower_type": borrower_type,
		"status": payload.get("status") or "Draft",
		"facility_type": payload.get("facility_type"),
		"requested_amount": flt(payload.get("requested_amount")),
		"employer_name": payload.get("employer_name"),
		"public_company_ticker": cstr(payload.get("public_company_ticker")).upper(),
		"industry": payload.get("industry"),
		"kbli": payload.get("kbli"),
		"risk_grade": payload.get("risk_grade"),
		"purpose": payload.get("purpose"),
		# Facility Fields
		"credit_limit": flt(payload.get("credit_limit")),
		"plafond": flt(payload.get("plafond")),
		"tenor_months": int(payload.get("tenor_months") or 0),
		"interest_rate": flt(payload.get("interest_rate")),
		"repayment_scheme": payload.get("repayment_scheme"),
		"submission_date": payload.get("submission_date"),
		# Collateral Fields
		"collateral_type": payload.get("collateral_type"),
		"collateral_value": flt(payload.get("collateral_value")),
		"ltv_percent": flt(payload.get("ltv_percent")),
		"coverage_ratio": flt(payload.get("coverage_ratio")),
		"collateral_description": payload.get("collateral_description"),
		# Financial Summary Fields
		"financial_year": int(payload.get("financial_year") or 0),
		"revenue": flt(payload.get("revenue")),
		"ebitda": flt(payload.get("ebitda")),
		"net_profit": flt(payload.get("net_profit")),
		"total_assets": flt(payload.get("total_assets")),
		"total_liabilities": flt(payload.get("total_liabilities")),
		"equity": flt(payload.get("equity")),
		"der": flt(payload.get("der")),
		"current_ratio": flt(payload.get("current_ratio")),
		"auditor": payload.get("auditor"),
		"audit_status": payload.get("audit_status"),
		# Analyst Fields
		"relationship_manager": payload.get("relationship_manager"),
		"analyst": payload.get("analyst"),
		"branch": payload.get("branch"),
		"segment": payload.get("segment"),
		"priority": payload.get("priority"),
		"target_date": payload.get("target_date"),
		"internal_notes": payload.get("internal_notes"),
		"npwp": payload.get("npwp"),
	}

	application = create_or_update_customer360_record("CRM Credit Application", app_fields)

	# Auto-populate linked records
	if borrower:
		# 1. Create linked Collateral record if user filled it
		if payload.get("collateral_type") and flt(payload.get("collateral_value")) > 0:
			try:
				collateral_doc = frappe.get_doc({
					"doctype": "CRM Collateral",
					"customer": borrower,
					"asset": f"{payload.get('collateral_type')} - {borrower_name}",
					"collateral_type": payload.get("collateral_type"),
					"collateral_value": flt(payload.get("collateral_value")),
					"ltv_percent": flt(payload.get("ltv_percent")),
					"status": "Active",
					"notes": payload.get("collateral_description") or ""
				})
				collateral_doc.insert()
			except Exception:
				frappe.log_error(frappe.get_traceback(), "Credit Application Collateral Init Failed")

		# 2. Create linked Credit Facility record if user filled it
		if payload.get("facility_type") and flt(payload.get("credit_limit")) > 0:
			try:
				facility_doc = frappe.get_doc({
					"doctype": "CRM Credit Facility",
					"customer": borrower,
					"facility_type": payload.get("facility_type"),
					"limit_amount": flt(payload.get("credit_limit")),
					"outstanding": flt(payload.get("requested_amount")),
					"status": "Active",
					"notes": f"Tenor: {payload.get('tenor_months')} months, Rate: {payload.get('interest_rate')}%, Scheme: {payload.get('repayment_scheme')}"
				})
				facility_doc.insert()
			except Exception:
				frappe.log_error(frappe.get_traceback(), "Credit Application Facility Init Failed")

	# Initialize spreading workspace / data
	try:
		from crm.api.credit_analysis import ensure_credit_analysis_tables, _replace_artifact, _insert, _workspace_payload

		ensure_credit_analysis_tables()
		
		# 3. Create spreading lines only for financial values explicitly entered in the form.
		if payload.get("financial_year"):
			year = int(payload.get("financial_year"))
			input_metrics = [
				("P&L", "revenue", "Pendapatan / Sales", "revenue"),
				("P&L", "ebitda", "EBITDA", "ebitda"),
				("P&L", "net_income", "Laba Bersih", "net_profit"),
				("Balance Sheet", "total_assets", "Total Aset", "total_assets"),
				("Balance Sheet", "total_liabilities", "Total Liabilitas", "total_liabilities"),
				("Balance Sheet", "equity", "Ekuitas", "equity"),
			]
			inserted_rows = 0
			for statement_type, metric_key, metric_label, payload_key in input_metrics:
				if payload.get(payload_key) in (None, ""):
					continue
				amount = flt(payload.get(payload_key))
				_insert(
					"CRM Credit Spread Line",
					{
						"application": application.get("name"),
						"customer": borrower,
						"statement_type": statement_type,
						"metric_key": metric_key,
						"metric_label": metric_label,
						"year": year,
						"amount": amount,
						"adjusted_amount": amount,
						"confidence": 1.0,
						"source": "User Input",
						"notes": f"Initial form input for FY {year}",
					}
				)
				inserted_rows += 1
			
			# Recalculate workspace parameters
			workspace = _workspace_payload(application.get("name"), persist_artifacts=True)
			
			# Auto generate AI Executive Summary, Memo and Recommendation!
			try:
				from crm.api.credit_analysis import generate_credit_summary, generate_credit_memo, generate_credit_recommendation
				generate_credit_summary(application.get("name"))
				generate_credit_memo(application.get("name"))
				generate_credit_recommendation(application.get("name"))
			except Exception:
				pass

			_replace_artifact(
				application.get("name"),
				borrower,
				"spreading_status",
				"Financial Spreading",
				{
					"status": "Draft",
					"row_count": inserted_rows,
					"balance_checks": workspace["balance_checks"]
				},
				status="Draft",
			)
		else:
			# Initialize an empty workspace artifact (no demo data)
			_replace_artifact(
				application.get("name"),
				borrower,
				"spreading_status",
				"Financial Spreading",
				{"status": "Draft", "row_count": 0, "balance_checks": [], "message": "No financial data yet. Upload a PDF or enter data manually in the Financial Spreading tab."},
				status="Draft",
			)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Credit Application Workspace Init Failed")
	
	frappe.db.commit()
	return application


def _first_leaf_value(doctype: str, value_field: str):
	if not frappe.db.table_exists(doctype):
		return None
	fields = ["name"]
	if frappe.get_meta(doctype).has_field(value_field):
		fields.append(value_field)
	rows = frappe.get_all(doctype, fields=fields, filters={"is_group": 0}, order_by="lft asc", limit=1)
	if not rows:
		return None
	return rows[0].get(value_field) or rows[0].name


def _normalize_select_values(doctype: str, doc):
	meta = frappe.get_meta(doctype)
	status_aliases = {
		"application received": ["Application Received", "Draft"],
		"document review": ["Document Review", "Pending Review", "In Progress"],
		"credit analysis": ["Credit Analysis", "In Progress"],
		"collateral appraisal": ["Collateral Appraisal", "In Progress"],
		"committee approval": ["Committee Approval", "Pending Review", "Submitted"],
		"legal documentation": ["Legal Documentation", "Approved", "In Progress"],
		"disbursement": ["Disbursement", "Approved"],
		"active": ["Active", "Approved"],
		"in progress": ["In Progress", "Credit Analysis"],
		"pending review": ["Pending Review", "Document Review", "Committee Approval"],
		"submitted": ["Submitted", "Committee Approval", "Pending Review"],
		"approved": ["Approved", "Active"],
	}
	for field in meta.fields:
		if field.fieldtype != "Select" or not field.options or not doc.get(field.fieldname):
			continue
		value = str(doc.get(field.fieldname))
		options = [option.strip() for option in field.options.split("\n") if option.strip()]
		if value in options:
			continue
		lower_value = value.lower()
		match = next((option for option in options if option.lower() == lower_value), None)
		if not match and doctype == "CRM Credit Application" and field.fieldname == "status":
			match = next((candidate for candidate in status_aliases.get(lower_value, []) if candidate in options), None)
		if not match:
			match = next((option for option in options if option.lower().endswith(lower_value)), None)
		if not match:
			match = next((option for option in options if lower_value.endswith(option.lower())), None)
		if match:
			doc[field.fieldname] = match


def _only_digits(value: str | None) -> str:
	return re.sub(r"\D", "", cstr(value or ""))


def _validate_customer360_doc(doctype: str, doc):
	if doctype == "CRM KYC Review":
		nik = _only_digits(doc.get("nik"))
		npwp = _only_digits(doc.get("npwp"))
		if nik and len(nik) != 16:
			frappe.throw(_("NIK / KTP must contain exactly 16 digits."))
		if npwp and len(npwp) not in (15, 16):
			frappe.throw(_("NPWP must contain 15 or 16 digits."))
		if doc.get("watchlist") and not cstr(doc.get("watchlist_reason")).strip():
			frappe.throw(_("Watchlist reason is required."))
		if doc.get("next_review_date") and _is_past_date(doc.get("next_review_date")) and not doc.get("renewal_workflow_status"):
			doc.renewal_workflow_status = "Triggered"
	if doctype == "CRM Relationship" and doc.get("customer") and doc.get("relationship_type") == "Shareholder":
		rows = _list_records("CRM Relationship", doc.customer)
		total = sum(
			flt(row.get("ownership_percent"))
			for row in rows
			if row.get("relationship_type") == "Shareholder" and row.get("name") != doc.get("name")
		)
		total += flt(doc.get("ownership_percent"))
		if total > 100:
			frappe.throw(_("Shareholder ownership cannot exceed 100%. Current total would be {0}%.").format(total))
	if doctype == "CRM Bank Account" and doc.get("customer") and doc.get("is_primary"):
		rows = _list_records("CRM Bank Account", doc.customer)
		existing_primary = next((row for row in rows if row.get("is_primary") and row.get("name") != doc.get("name")), None)
		if existing_primary:
			frappe.throw(_("Only one primary bank account is allowed per customer. Existing primary: {0}").format(existing_primary.get("account_number") or existing_primary.get("name")))
	if doctype == "CRM Customer Document" and doc.get("expiry_date"):
		doc.expiry_status = _document_expiry_status(doc.get("expiry_date"))
	if doctype == "CRM Collateral" and flt(doc.get("ltv_percent")) > 100:
		frappe.throw(_("Collateral LTV cannot exceed 100%."))
	if doctype == "CRM Bureau Report" and doc.get("score") not in (None, ""):
		_validate_range("Bureau score", flt(doc.get("score")), 0, 1000)
	if doctype == "CRM Risk Profile" and doc.get("internal_score") not in (None, ""):
		_validate_range("Internal score", flt(doc.get("internal_score")), 0, 1000)
	if doctype == "CRM AI Insight" and doc.get("confidence_score") not in (None, ""):
		_validate_range("Confidence score", flt(doc.get("confidence_score")), 0, 100)


def _validate_range(label: str, value: float, minimum: float, maximum: float):
	if value < minimum or value > maximum:
		frappe.throw(_("{0} must be between {1} and {2}.").format(label, minimum, maximum))


def _is_past_date(value) -> bool:
	try:
		return bool(value and getdate(value) < getdate(nowdate()))
	except Exception:
		return False


def _days_until(value):
	try:
		return date_diff(getdate(value), getdate(nowdate()))
	except Exception:
		return None


def _document_expiry_status(expiry_date):
	days = _days_until(expiry_date)
	if days is None:
		return "Not Applicable"
	if days < 0:
		return "Expired"
	if days <= 30:
		return "Expiring Soon"
	return "Valid"


def _demo_credit_applications():
	return [
		{
			"name": "DEMO-IND-001",
			"id": "DEMO-IND-001",
			"borrower": None,
			"borrower_name": "Andi Pratama",
			"borrower_type": "Individual",
			"status": "Credit Analysis",
			"facility_type": "Working Capital Top-up",
			"requested_amount": 750000000,
			"employer_name": "PT Bank Mandiri Tbk",
			"public_company_ticker": "BMRI",
			"industry": "Financial Services",
			"kbli": "6419",
			"risk_grade": "B+",
			"purpose": "Personal productive credit backed by verified employment income.",
		},
		{
			"name": "DEMO-IND-002",
			"id": "DEMO-IND-002",
			"borrower": None,
			"borrower_name": "Rina Wijaya",
			"borrower_type": "Individual",
			"status": "Document Review",
			"facility_type": "Investment Loan",
			"requested_amount": 450000000,
			"employer_name": "",
			"public_company_ticker": "",
			"industry": "Retail",
			"kbli": "4711",
			"risk_grade": "B",
			"purpose": "Individual borrower with manual bureau review pending.",
		},
	]


def _normalize_application(row):
	return {
		"name": row.get("name"),
		"id": row.get("name"),
		"borrower": row.get("borrower"),
		"borrower_name": row.get("borrower_name") or _get_customer_label(row.get("borrower")),
		"borrower_type": row.get("borrower_type") or "Individual",
		"status": row.get("status") or "Draft",
		"facility_type": row.get("facility_type") or "",
		"requested_amount": flt(row.get("requested_amount")),
		"employer_name": row.get("employer_name") or "",
		"public_company_ticker": (row.get("public_company_ticker") or "").upper(),
		"industry": row.get("industry") or "",
		"kbli": row.get("kbli") or "",
		"risk_grade": row.get("risk_grade") or "",
		"purpose": row.get("purpose") or "",
		"public_snapshot": row.get("public_snapshot"),
		"creation": row.get("creation"),
		"modified": row.get("modified"),
	}


@frappe.whitelist()
def get_credit_application_queue():
	"""Return credit applications for the Credit Analysis queue."""
	if not _doctype_ready("CRM Credit Application"):
		return []

	rows = frappe.get_all(
		"CRM Credit Application",
		fields=[
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
			"creation",
			"modified",
		],
		order_by="modified desc",
		limit=100,
	)
	return [_normalize_application(row) for row in rows]


def _get_public_snapshot(ticker: str | None = None, snapshot_name: str | None = None):
	if not _doctype_ready("CRM Public Company Snapshot"):
		return None

	filters = {}
	if snapshot_name:
		filters["name"] = snapshot_name
	elif ticker:
		filters["ticker"] = ticker.upper()
	else:
		return None

	rows = frappe.get_all(
		"CRM Public Company Snapshot",
		fields=[
			"name",
			"ticker",
			"company_name",
			"source",
			"status",
			"fetched_at",
			"source_url",
			"rating",
			"financial_year",
			"normalized_json",
		],
		filters=filters,
		limit=1,
	)
	if not rows:
		return None
	snapshot = dict(rows[0])
	snapshot["normalized"] = _json_loads(snapshot.pop("normalized_json", None))
	return snapshot


@frappe.whitelist()
def get_credit_analysis(application_id: str):
	applications = get_credit_application_queue()
	app = next((row for row in applications if row.get("name") == application_id), None)
	if not app and _doctype_ready("CRM Credit Application"):
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
			app = _normalize_application(row)
	if not app:
		frappe.throw(_("Credit application not found"))

	payload = {
		"application": app,
		"public_snapshot": _get_public_snapshot(app.get("public_company_ticker"), app.get("public_snapshot")),
		"bureau": _latest_bureau_report(app.get("borrower")),
		"facilities": _list_records("CRM Credit Facility", app.get("borrower")),
		"collaterals": _list_records("CRM Collateral", app.get("borrower")),
		"financials": _list_records("CRM Financial Statement", app.get("borrower")),
		"source_policy": {
			"public_company_data": _("PT Tbk public data is enrichment only."),
			"personal_credit_data": _("Individual SLIK/OJK data requires authorization or manual upload."),
			"sources": PUBLIC_SOURCE_URLS,
		},
	}
	try:
		from crm.api.credit_analysis import get_credit_workspace

		workspace = get_credit_workspace.__wrapped__(application_id)
		payload.update(workspace)
		payload["legacy"] = {
			"financials": payload.get("financials") or [],
			"facilities": payload.get("facilities") or [],
			"collaterals": payload.get("collaterals") or [],
			"bureau": payload.get("bureau"),
		}
	except Exception:
		pass
	return payload


@frappe.whitelist()
def refresh_public_company_snapshot(ticker: str):
	ticker = (ticker or "").upper().strip()
	if not ticker:
		frappe.throw(_("Ticker is required"))

	normalized = {
		"status": "source_unavailable",
		"message": _("Official IDX/XBRL or vendor API credentials are not configured. Attach a public report or configure an adapter to populate financials."),
		"official_sources": [PUBLIC_SOURCE_URLS["idx_xbrl"], PUBLIC_SOURCE_URLS["pefindo"]],
		"financials": [],
		"ratings": [],
	}
	payload = {
		"ticker": ticker,
		"company_name": f"{ticker} - PT Tbk",
		"source": "IDX XBRL / PEFINDO",
		"status": "Source Unavailable",
		"fetched_at": now_datetime(),
		"source_url": PUBLIC_SOURCE_URLS["idx_xbrl"],
		"rating": "",
		"financial_year": now_datetime().year,
		"normalized_json": json.dumps(normalized, default=str, indent=2),
		"raw_json": json.dumps({"adapter": "not_configured", "ticker": ticker}, indent=2),
	}

	if not _doctype_ready("CRM Public Company Snapshot"):
		return {**payload, "normalized": normalized, "name": ticker}

	existing = frappe.db.exists("CRM Public Company Snapshot", ticker)
	if existing:
		doc = frappe.get_doc("CRM Public Company Snapshot", existing)
		doc.update(payload)
	else:
		doc = frappe.get_doc({"doctype": "CRM Public Company Snapshot", **payload})
	doc.save(ignore_permissions=False)
	return {**payload, "normalized": normalized, "name": doc.name}


@frappe.whitelist()
def check_customer360_adapter(customer: str, adapter_key: str):
	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer not found"))
	statuses = _build_external_adapters(customer)
	for status in statuses:
		if status.get("key") == adapter_key:
			return status
	frappe.throw(_("Unknown Customer 360 adapter: {0}").format(adapter_key))


@frappe.whitelist()
def get_customer_360(customer: str, filters=None):
	if not customer:
		frappe.throw(_("Customer is required"))
	customer_doc = frappe.db.get_value("Customer", customer, _customer_fields(), as_dict=True)
	if not customer_doc:
		frappe.throw(_("Customer not found"))

	kyc = _latest_record("CRM KYC Review", customer)
	facilities = _list_records("CRM Credit Facility", customer)
	collaterals = _list_records("CRM Collateral", customer)
	bureau_reports = _list_records("CRM Bureau Report", customer)
	relationships = _list_records("CRM Relationship", customer)
	financials = _list_records("CRM Financial Statement", customer)
	site_visits = _list_records("CRM Site Visit", customer)
	bank_accounts = _list_records("CRM Bank Account", customer)
	documents = _list_records("CRM Customer Document", customer)
	communications = _list_records("CRM Customer Communication", customer)
	transactions = _list_records("CRM Transaction History", customer)
	risk_profiles = _list_records("CRM Risk Profile", customer)
	ai_insights = _list_records("CRM AI Insight", customer)
	tags = _list_records("CRM Customer Tag", customer)
	merge_audits = _list_merge_audits(customer)
	credit_applications = _list_records("CRM Credit Application", customer, customer_field="borrower")
	tasks = _list_reference_records("CRM Task", customer)
	notes = _list_reference_records("FCRM Note", customer)
	events = _list_reference_records("Event", customer)
	saved_summary = _get_saved_customer_summary(notes)
	summary = _build_customer_summary(
		customer_doc,
		kyc,
		facilities,
		bureau_reports,
		relationships,
		risk_profiles,
		bank_accounts,
		documents,
		transactions,
		ai_insights,
		tags,
		saved_summary,
	)
	relationship_graph = _build_relationship_graph(customer_doc, relationships, facilities, collaterals, bank_accounts, risk_profiles, tags)
	risk_controls = _build_risk_controls(kyc, relationships, documents, transactions, risk_profiles, bank_accounts, collaterals)
	data_quality = _build_data_quality(customer_doc, kyc, relationships, bank_accounts, documents, facilities, risk_controls)
	external_adapters = _build_external_adapters(customer, kyc, bureau_reports, bank_accounts, collaterals)
	compliance_status = _build_compliance_status(kyc, relationships, bureau_reports, risk_controls, external_adapters)
	next_actions = _build_next_actions(data_quality, risk_controls, ai_insights, external_adapters)
	audit_summary = _build_audit_summary(customer_doc, kyc, notes, CUSTOMER_360_CUSTOMER_FIELD_DOCTYPES)

	return {
		"customer": customer_doc,
		"summary": summary,
		"kyc": kyc,
		"facilities": facilities,
		"collaterals": collaterals,
		"bureau_reports": bureau_reports,
		"relationships": relationships,
		"shareholders": [row for row in relationships if row.get("relationship_type") == "Shareholder"],
		"directors": [row for row in relationships if row.get("relationship_type") in ("Director", "Commissioner")],
		"related_entities": [row for row in relationships if row.get("relationship_type") in ("Group Company", "UBO", "RM", "Other")],
		"financials": financials,
		"site_visits": site_visits,
		"bank_accounts": bank_accounts,
		"documents": documents,
		"communications": communications,
		"transactions": transactions,
		"risk_profiles": risk_profiles,
		"latest_risk": risk_profiles[0] if risk_profiles else None,
		"ai_insights": ai_insights,
		"tags": tags,
		"merge_audits": merge_audits,
		"credit_applications": credit_applications,
		"tasks": tasks,
		"notes": notes,
		"events": events,
		"timeline": _build_timeline(
			credit_applications,
			bureau_reports,
			site_visits,
			tasks,
			notes,
			events,
			communications,
			transactions,
			risk_profiles,
		),
		"relationship_graph": relationship_graph,
		"data_quality": data_quality,
		"external_adapters": external_adapters,
		"risk_controls": risk_controls,
		"compliance_status": compliance_status,
		"next_actions": next_actions,
		"audit_summary": audit_summary,
	}


def _list_records(doctype: str, customer: str | None, customer_field: str = "customer", limit: int = 50):
	if not customer or not _doctype_ready(doctype):
		return []
	return frappe.get_all(
		doctype,
		fields=["*"],
		filters={customer_field: customer},
		order_by="modified desc",
		limit=limit,
	)


def _customer_fields():
	fields = ["name", "customer_name", "customer_type", "customer_group", "territory", "website", "tax_id", "modified"]
	meta = frappe.get_meta("Customer")
	for fieldname in ("mobile_no", "email_id"):
		if meta.has_field(fieldname):
			fields.append(fieldname)
	return fields


def _list_merge_audits(customer: str):
	if not _doctype_ready("CRM Customer Merge Audit"):
		return []
	rows = frappe.get_all("CRM Customer Merge Audit", fields=["*"], filters={"source_customer": customer}, limit=20)
	rows.extend(frappe.get_all("CRM Customer Merge Audit", fields=["*"], filters={"target_customer": customer}, limit=20))
	seen = set()
	unique = []
	for row in rows:
		if row.name in seen:
			continue
		seen.add(row.name)
		unique.append(row)
	return sorted(unique, key=lambda row: cstr(row.get("modified") or ""), reverse=True)[:20]


def _latest_record(doctype: str, customer: str | None):
	records = _list_records(doctype, customer, limit=1)
	return records[0] if records else None


def _latest_bureau_report(customer: str | None):
	return _latest_record("CRM Bureau Report", customer)


def _build_external_adapters(customer: str, kyc=None, bureau_reports=None, bank_accounts=None, collaterals=None):
	manual_signals = {
		"ekyc": (kyc or {}).get("ekyc_result"),
		"aml_pep": None,
		"bureau": (bureau_reports or [{}])[0].get("source") if bureau_reports else None,
		"core_banking": None,
		"account_otp": next((row.get("otp_status") for row in bank_accounts or [] if row.get("otp_status")), None),
		"collateral_registry": next((row.get("reappraisal_status") for row in collaterals or [] if row.get("reappraisal_status")), None),
	}
	statuses = []
	for key, config in CUSTOMER_360_ADAPTERS.items():
		manual_signal = manual_signals.get(key)
		statuses.append(
			{
				"key": key,
				"label": config["label"],
				"status": "Not Configured",
				"message": _("No official provider is configured. Existing values are manual review data only.") if manual_signal else _("Official provider is not configured."),
				"required_configuration": config["required_configuration"],
				"last_checked": now_datetime(),
				"manual_signal": manual_signal or "",
				"customer": customer,
			}
		)
	return statuses


def _build_relationship_graph(customer, relationships, facilities, collaterals, bank_accounts, risk_profiles, tags):
	customer_id = f"customer:{customer.name}"
	nodes = [
		{
			"id": customer_id,
			"label": customer.get("customer_name") or customer.name,
			"type": "Customer",
			"customer": customer.name,
			"status": customer.get("customer_type") or "",
		}
	]
	edges = []
	filters = {"Customer"}

	def add_node(node):
		if not any(existing["id"] == node["id"] for existing in nodes):
			nodes.append(node)
			filters.add(node["type"])

	def add_edge(source, target, relation, value=0):
		edges.append({"source": source, "target": target, "relation": relation, "value": flt(value)})

	for rel in relationships:
		rel_type = rel.get("relationship_type") or "Relationship"
		node_id = f"customer:{rel.get('related_customer')}" if rel.get("related_customer") else f"relationship:{rel.get('name')}"
		add_node(
			{
				"id": node_id,
				"label": rel.get("related_party") or rel.get("related_customer") or rel_type,
				"type": rel_type,
				"customer": rel.get("related_customer") or "",
				"status": rel.get("aml_pep_status") or rel.get("background_check_status") or "",
				"exposure": flt(rel.get("exposure")),
				"ownership_percent": flt(rel.get("ownership_percent")),
				"is_ubo": bool(rel.get("is_ubo")),
				"source_name": rel.get("name"),
			}
		)
		add_edge(customer_id, node_id, rel_type, rel.get("exposure") or rel.get("ownership_percent"))

	for row in facilities:
		node_id = f"facility:{row.get('name')}"
		add_node({"id": node_id, "label": row.get("facility_type") or row.get("product_type") or "Facility", "type": "Facility", "status": row.get("status") or "", "exposure": flt(row.get("outstanding")), "source_name": row.get("name")})
		add_edge(customer_id, node_id, "Facility", row.get("outstanding"))

	for row in collaterals:
		node_id = f"collateral:{row.get('name')}"
		add_node({"id": node_id, "label": row.get("asset") or row.get("collateral_type") or "Collateral", "type": "Collateral", "status": row.get("status") or "", "exposure": flt(row.get("collateral_value")), "source_name": row.get("name")})
		target = f"facility:{row.get('linked_facility')}" if row.get("linked_facility") else customer_id
		add_edge(target if any(node["id"] == target for node in nodes) else customer_id, node_id, "Secured By", row.get("collateral_value"))

	for row in bank_accounts:
		node_id = f"bank:{row.get('name')}"
		add_node({"id": node_id, "label": row.get("bank") or "Bank Account", "type": "Bank Account", "status": row.get("verification_status") or "", "source_name": row.get("name")})
		add_edge(customer_id, node_id, "Bank Account")

	for row in risk_profiles[:1]:
		node_id = f"risk:{row.get('name')}"
		add_node({"id": node_id, "label": row.get("risk_grade") or "Risk Profile", "type": "Risk", "status": "NPL" if row.get("npl_flag") else row.get("watchlist_status") or "", "source_name": row.get("name")})
		add_edge(customer_id, node_id, "Risk Profile")

	for row in tags:
		node_id = f"tag:{row.get('tag')}"
		add_node({"id": node_id, "label": row.get("tag") or "Tag", "type": "Tag", "status": row.get("color") or "", "source_name": row.get("name")})
		add_edge(customer_id, node_id, "Tagged")

	return {"nodes": nodes, "edges": edges, "filters": sorted(filters)}


def _build_risk_controls(kyc, relationships, documents, transactions, risk_profiles, bank_accounts, collaterals):
	shareholders = [row for row in relationships if row.get("relationship_type") == "Shareholder"]
	shareholder_total = sum(flt(row.get("ownership_percent")) for row in shareholders)
	latest_risk = risk_profiles[0] if risk_profiles else {}
	expired_documents = [row for row in documents if row.get("expiry_status") == "Expired" or _is_past_date(row.get("expiry_date"))]
	missed_payments = [row for row in transactions if row.get("transaction_type") == "Missed Payment"]
	expiring_insurance = [
		row
		for row in collaterals
		if row.get("insurance_expiry") and _days_until(row.get("insurance_expiry")) is not None and _days_until(row.get("insurance_expiry")) <= 30
	]
	primary_account = next((row for row in bank_accounts if row.get("is_primary")), None)
	return {
		"watchlist": bool((kyc or {}).get("watchlist")) or latest_risk.get("watchlist_status") == "Yes",
		"npl_flag": bool(latest_risk.get("npl_flag")),
		"overdue_kyc": bool((kyc or {}).get("next_review_date") and _is_past_date((kyc or {}).get("next_review_date"))),
		"expired_documents": len(expired_documents),
		"missed_payments": len(missed_payments),
		"ownership_balanced": round(shareholder_total, 2) == 100 if shareholders else False,
		"shareholder_total": shareholder_total,
		"primary_account_verified": bool(primary_account and primary_account.get("verification_status") == "Verified"),
		"collateral_insurance_expiring": len(expiring_insurance),
	}


def _build_data_quality(customer, kyc, relationships, bank_accounts, documents, facilities, risk_controls):
	missing = []
	warnings = []

	def require(condition, field, label, severity="High"):
		if not condition:
			missing.append({"field": field, "label": label, "severity": severity})

	require(customer.get("customer_name"), "customer_name", _("Customer name"))
	require(customer.get("customer_type"), "customer_type", _("Customer type"))
	require((kyc or {}).get("npwp") or customer.get("tax_id"), "npwp", _("NPWP"))
	require((kyc or {}).get("registered_address"), "registered_address", _("Registered address"))
	require((kyc or {}).get("nik") or customer.get("customer_type") != "Individual", "nik", _("NIK / KTP"), "Medium")
	require(bank_accounts, "bank_accounts", _("At least one bank account"), "Medium")
	require(facilities, "facilities", _("At least one credit facility"), "Medium")

	if relationships and not risk_controls.get("ownership_balanced"):
		warnings.append(_("Shareholder ownership is not balanced to 100%."))
	if risk_controls.get("overdue_kyc"):
		warnings.append(_("KYC review is overdue."))
	if risk_controls.get("expired_documents"):
		warnings.append(_("{0} customer document(s) expired.").format(risk_controls.get("expired_documents")))
	if risk_controls.get("missed_payments"):
		warnings.append(_("{0} missed payment transaction(s) found.").format(risk_controls.get("missed_payments")))
	if risk_controls.get("collateral_insurance_expiring"):
		warnings.append(_("{0} collateral insurance record(s) expire within 30 days.").format(risk_controls.get("collateral_insurance_expiring")))

	stale_records = []
	for rowset, label in ((documents, "Documents"), (facilities, "Facilities"), (bank_accounts, "Bank accounts")):
		for row in rowset:
			if row.get("modified") and date_diff(getdate(nowdate()), getdate(row.get("modified"))) > 365:
				stale_records.append({"doctype": label, "name": row.get("name"), "modified": row.get("modified")})

	score = max(0, 100 - len(missing) * 8 - len(warnings) * 5 - len(stale_records) * 2)
	return {
		"score": score,
		"missing_required_fields": missing,
		"stale_records": stale_records[:20],
		"expired_documents": [row for row in documents if row.get("expiry_status") == "Expired" or _is_past_date(row.get("expiry_date"))],
		"warnings": warnings,
	}


def _build_compliance_status(kyc, relationships, bureau_reports, risk_controls, external_adapters):
	aml_rows = [row for row in relationships if row.get("relationship_type") in ("Director", "Commissioner", "UBO", "Shareholder")]
	return {
		"kyc_status": (kyc or {}).get("status") or "Pending",
		"ekyc_result": (kyc or {}).get("ekyc_result") or "Manual Review",
		"next_review_date": (kyc or {}).get("next_review_date"),
		"overdue_kyc": risk_controls.get("overdue_kyc"),
		"aml_pep_clear": len([row for row in aml_rows if row.get("aml_pep_status") == "Clear"]),
		"aml_pep_pending": len([row for row in aml_rows if row.get("aml_pep_status") in ("Manual", "Pending Vendor", "Potential Match", "Unavailable", None)]),
		"bureau_status": (bureau_reports[0].get("kol_status") if bureau_reports else "Not Available"),
		"bureau_source": (bureau_reports[0].get("source") if bureau_reports else ""),
		"watchlist": risk_controls.get("watchlist"),
		"adapter_blockers": [row for row in external_adapters if row.get("status") == "Not Configured"],
	}


def _build_next_actions(data_quality, risk_controls, ai_insights, external_adapters):
	actions = []
	for missing in data_quality.get("missing_required_fields", [])[:5]:
		actions.append({"type": "data_quality", "title": _("Complete {0}").format(missing.get("label")), "priority": "P1", "source": "Data Quality", "action_key": "open_profile", "payload": missing})
	if risk_controls.get("overdue_kyc"):
		actions.append({"type": "compliance", "title": _("Renew overdue KYC review"), "priority": "P0", "source": "KYC", "action_key": "open_kyc", "payload": {}})
	if risk_controls.get("expired_documents"):
		actions.append({"type": "document", "title": _("Replace expired customer documents"), "priority": "P0", "source": "Documents", "action_key": "open_documents", "payload": {"count": risk_controls.get("expired_documents")}})
	if risk_controls.get("missed_payments"):
		actions.append({"type": "risk", "title": _("Review missed payment behavior"), "priority": "P0", "source": "Transactions", "action_key": "open_transactions", "payload": {"count": risk_controls.get("missed_payments")}})
	if not risk_controls.get("ownership_balanced"):
		actions.append({"type": "ownership", "title": _("Complete shareholder ownership to 100%"), "priority": "P1", "source": "Ownership", "action_key": "open_ownership", "payload": {"shareholder_total": risk_controls.get("shareholder_total")}})
	for insight in [row for row in ai_insights if row.get("status") == "Open"][:3]:
		actions.append({"type": "ai_insight", "title": insight.get("title"), "priority": "P1", "source": "AI Insight", "action_key": "open_ai_insight", "payload": {"name": insight.get("name")}})
	for adapter in external_adapters[:2]:
		actions.append({"type": "adapter", "title": _("Configure {0}").format(adapter.get("label")), "priority": "P2", "source": "External Adapter", "action_key": "check_adapter", "payload": {"adapter_key": adapter.get("key")}})
	return actions[:12]


def _build_audit_summary(customer, kyc, notes, tracked_doctypes):
	tracked = []
	for doctype in sorted(tracked_doctypes):
		if not _doctype_ready(doctype):
			continue
		tracked.append({"doctype": doctype, "count": frappe.db.count(doctype, {"customer": customer.name}) if frappe.get_meta(doctype).has_field("customer") else 0})
	latest_summary = next((note for note in notes or [] if note.get("title") == "AI Customer Summary"), None)
	return {
		"last_profile_update": customer.get("modified"),
		"last_kyc_update": (kyc or {}).get("modified"),
		"last_summary_update": (latest_summary or {}).get("modified"),
		"tracked_doctypes": tracked,
	}


def _list_reference_records(doctype: str, customer: str, limit: int = 20):
	if not _doctype_ready(doctype):
		return []
	fields_by_doctype = {
		"CRM Task": ["name", "title", "priority", "status", "due_date", "assigned_to", "recurring", "recurrence_rule", "description", "creation", "modified"],
		"FCRM Note": ["name", "title", "content", "creation", "modified"],
		"Event": ["name", "subject", "description", "starts_on", "ends_on", "status", "creation", "modified"],
	}
	return frappe.get_all(
		doctype,
		fields=fields_by_doctype.get(doctype, ["*"]),
		filters={"reference_doctype": "Customer", "reference_docname": customer},
		order_by="modified desc",
		limit=limit,
	)


def _get_saved_customer_summary(notes):
	for note in notes or []:
		if note.get("title") == "AI Customer Summary" and note.get("content"):
			return note.get("content")
	return None


def _summary_bullets(customer, kyc, facilities, bureau_reports, relationships, risk_profiles, transactions, ai_insights):
	active_count = len([row for row in facilities if row.get("status") == "Active"])
	latest_bureau = bureau_reports[0] if bureau_reports else {}
	latest_risk = risk_profiles[0] if risk_profiles else {}
	missed = len([row for row in transactions if row.get("transaction_type") == "Missed Payment"])
	open_insights = len([row for row in ai_insights if row.get("status") == "Open"])
	return [
		_("{0} has {1} active facilities and total outstanding of {2}.").format(
			customer.get("customer_name") or customer.get("name"),
			active_count,
			flt(sum(flt(row.get("outstanding")) for row in facilities)),
		),
		_("Latest bureau status is {0} with score {1}.").format(
			latest_bureau.get("kol_status") or "not available",
			latest_bureau.get("score") or 0,
		),
		_("KYC status is {0}; next review is {1}.").format(
			(kyc or {}).get("status") or "Pending",
			(kyc or {}).get("next_review_date") or "not scheduled",
		),
		_("Risk grade is {0}; watchlist is {1}.").format(
			latest_risk.get("risk_grade") or latest_bureau.get("kol_status") or "Unrated",
			"active" if (kyc or {}).get("watchlist") or latest_risk.get("watchlist_status") == "Yes" else "not active",
		),
		_("{0} missed payments and {1} open AI insights require follow-up.").format(missed, open_insights),
	]


def _build_customer_summary(
	customer,
	kyc,
	facilities,
	bureau_reports,
	relationships,
	risk_profiles=None,
	bank_accounts=None,
	documents=None,
	transactions=None,
	ai_insights=None,
	tags=None,
	saved_summary=None,
):
	risk_profiles = risk_profiles or []
	bank_accounts = bank_accounts or []
	documents = documents or []
	transactions = transactions or []
	ai_insights = ai_insights or []
	tags = tags or []
	total_outstanding = sum(flt(row.get("outstanding")) for row in facilities)
	total_limit = sum(flt(row.get("limit_amount")) for row in facilities)
	group_exposure = sum(flt(row.get("exposure")) for row in relationships)
	latest_bureau = bureau_reports[0] if bureau_reports else {}
	latest_risk = risk_profiles[0] if risk_profiles else {}
	shareholders = [row for row in relationships if row.get("relationship_type") == "Shareholder"]
	shareholder_total = sum(flt(row.get("ownership_percent")) for row in shareholders)
	summary_bullets = _summary_bullets(customer, kyc, facilities, bureau_reports, relationships, risk_profiles, transactions, ai_insights)
	confidence = min(0.95, 0.35 + (0.08 * len([rows for rows in (facilities, bureau_reports, relationships, risk_profiles, transactions, ai_insights) if rows])))
	structured_response = {
		"schema_version": "1.0",
		"agent_key": "customer_insight",
		"title": _("Customer 360 Summary"),
		"executive_summary": saved_summary or " ".join(summary_bullets[:2]),
		"confidence": round(confidence, 2),
		"sections": [
			{"title": _("Exposure"), "items": [summary_bullets[0]]},
			{"title": _("Compliance"), "items": [summary_bullets[2], summary_bullets[3]]},
			{"title": _("Follow-up"), "items": [summary_bullets[4]]},
		],
		"recommendations": [
			{
				"title": row.get("title"),
				"detail": row.get("suggested_action") or row.get("notes") or "",
				"confidence": flt(row.get("confidence_score")),
			}
			for row in ai_insights[:3]
		],
		"risks": [
			{"title": _("Watchlist"), "severity": "High" if (kyc or {}).get("watchlist") else "Low"},
			{"title": _("Missed payments"), "severity": "High" if any(row.get("transaction_type") == "Missed Payment" for row in transactions) else "Low"},
		],
		"actions": [],
		"sources": [
			{"id": "S1", "title": _("Customer profile"), "doctype": "Customer", "docname": customer.get("name"), "excerpt": customer.get("customer_name") or customer.get("name")},
			{"id": "S2", "title": _("Customer 360 linked records"), "doctype": "Customer", "docname": customer.get("name"), "excerpt": _("Facilities, KYC, bureau, relationship, transaction, and insight records.")},
		],
		"limitations": [_("External verification adapters are not configured unless explicitly shown as configured.")],
	}
	return {
		"total_outstanding": total_outstanding,
		"active_facilities": len([row for row in facilities if row.get("status") == "Active"]),
		"total_limit": total_limit,
		"risk_grade": latest_risk.get("risk_grade") or latest_bureau.get("kol_status") or "Unrated",
		"score": latest_risk.get("internal_score") or latest_bureau.get("score") or 0,
		"group_exposure": group_exposure,
		"related_entities": len(relationships),
		"kyc_status": (kyc or {}).get("status") or "Pending",
		"next_review_date": (kyc or {}).get("next_review_date"),
		"watchlist": bool((kyc or {}).get("watchlist")) or latest_risk.get("watchlist_status") == "Yes",
		"shareholder_total": shareholder_total,
		"shareholder_balanced": round(shareholder_total, 2) == 100 if shareholders else False,
		"bank_accounts": len(bank_accounts),
		"documents": len(documents),
		"expired_documents": len([row for row in documents if row.get("expiry_status") == "Expired"]),
		"transactions": len(transactions),
		"missed_payments": len([row for row in transactions if row.get("transaction_type") == "Missed Payment"]),
		"open_ai_insights": len([row for row in ai_insights if row.get("status") == "Open"]),
		"tags": len(tags),
		"summary_bullets": summary_bullets,
		"summary_text": saved_summary or "\n".join(f"- {row}" for row in summary_bullets),
		"structured_response": structured_response,
	}


def _timeline_item(kind, title, description, modified, icon, doctype=None, name=None, color="slate"):
	return {
		"kind": kind,
		"title": title,
		"description": description or "",
		"modified": modified,
		"icon": icon,
		"doctype": doctype,
		"name": name,
		"color": color,
	}


def _build_timeline(
	credit_applications,
	bureau_reports,
	site_visits,
	tasks,
	notes,
	events,
	communications=None,
	transactions=None,
	risk_profiles=None,
):
	items = []
	for row in credit_applications:
		items.append(_timeline_item("Credit Application", row.get("facility_type") or row.get("name"), row.get("purpose"), row.get("modified"), "file-text", "CRM Credit Application", row.get("name"), "blue"))
	for row in bureau_reports:
		items.append(_timeline_item("Bureau Report", row.get("kol_status") or row.get("source"), row.get("notes"), row.get("modified"), "shield", "CRM Bureau Report", row.get("name"), "teal"))
	for row in site_visits:
		items.append(_timeline_item("Site Visit", row.get("visit_date") or row.get("name"), row.get("notes"), row.get("modified"), "camera", "CRM Site Visit", row.get("name"), "emerald"))
	for row in tasks:
		items.append(_timeline_item("Task", row.get("title"), row.get("status"), row.get("modified"), "check-circle", "CRM Task", row.get("name"), "amber"))
	for row in notes:
		items.append(_timeline_item("Note", row.get("title"), row.get("content"), row.get("modified"), "file", "FCRM Note", row.get("name"), "slate"))
	for row in events:
		items.append(_timeline_item("Event", row.get("subject"), row.get("description"), row.get("modified"), "calendar", "Event", row.get("name"), "purple"))
	for row in communications or []:
		items.append(_timeline_item("Communication", row.get("subject"), row.get("channel"), row.get("modified"), "message-square", "CRM Customer Communication", row.get("name"), "cyan"))
	for row in transactions or []:
		items.append(_timeline_item("Transaction", row.get("transaction_type"), row.get("status"), row.get("modified"), "repeat", "CRM Transaction History", row.get("name"), "orange"))
	for row in risk_profiles or []:
		items.append(_timeline_item("Risk Event", row.get("risk_grade"), row.get("early_warning_triggers"), row.get("modified"), "alert-triangle", "CRM Risk Profile", row.get("name"), "red"))
	return sorted(items, key=lambda row: cstr(row.get("modified") or ""), reverse=True)[:20]
