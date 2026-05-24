import json
from collections import Counter

import frappe
from frappe import _
from frappe.utils import add_days, nowdate

from crm.api.credit import create_customer_360_customer, create_or_update_customer360_record
from crm.api.lead_gen import DEFAULT_IMPORT_OPTIONS, _build_workbook_payload_from_path, _bundled_workbook_path, _import_rows


BNI_UAT_SEED_STATE_KEY = "crm_bni_uat_seed_created"
BNI_UAT_SEED_RECORDS_KEY = "crm_bni_uat_seed_records"
BANK_KEYWORDS = ("bank", "bni", "bri", "bca", "danamon", "cimb", "ocbc", "dbs", "uob", "permata")


def _load_seed_state():
	return bool(frappe.db.get_default(BNI_UAT_SEED_STATE_KEY))


def _load_seed_records():
	return json.loads(frappe.db.get_default(BNI_UAT_SEED_RECORDS_KEY) or "{}")


def _store_seed_records(records):
	frappe.db.set_default(BNI_UAT_SEED_RECORDS_KEY, json.dumps(records, indent=2))
	frappe.db.set_default(BNI_UAT_SEED_STATE_KEY, "1")


def _assert_seed_permissions():
	frappe.only_for(["System Manager", "Sales Manager"], True)


def _append_record(records, doctype, name):
	if not name:
		return
	records.setdefault(doctype, [])
	if name not in records[doctype]:
		records[doctype].append(name)


def _select_seed_companies(row_objects, limit=4):
	counts = Counter()
	samples = {}
	for row in row_objects:
		company = (row.get("company") or "").strip()
		if not company:
			continue
		if not any(keyword in company.lower() for keyword in BANK_KEYWORDS):
			continue
		counts[company] += 1
		samples.setdefault(company, row)
	return [(company, samples[company]) for company, _count in counts.most_common(limit)]


def _create_customer_records(customer, sample_row, index, records):
	customer_name = customer["name"]
	display_name = customer["customer_name"]
	application = create_or_update_customer360_record(
		"CRM Credit Application",
		{
			"borrower": customer_name,
			"borrower_name": display_name,
			"borrower_type": "Company",
			"status": "In Progress" if index % 2 == 0 else "Pending Review",
			"facility_type": "Working Capital",
			"requested_amount": 5000000000 + (index * 750000000),
			"employer_name": display_name,
			"public_company_ticker": display_name.split()[0][:4].upper(),
			"industry": sample_row.get("industry") or "Banking",
			"kbli": "6419",
			"risk_grade": "A-" if index == 0 else "B+",
			"purpose": f"BNI UAT seeded pipeline for {display_name}.",
		},
	)
	_append_record(records, "CRM Credit Application", application.get("name"))

	facility = create_or_update_customer360_record(
		"CRM Credit Facility",
		{
			"customer": customer_name,
			"facility_type": "Working Capital",
			"product_type": "Revolving",
			"status": "Active",
			"due_date": add_days(nowdate(), 90 + (index * 15)),
			"outstanding": 2200000000 + (index * 250000000),
			"limit_amount": 4000000000 + (index * 500000000),
			"health": "KOL-1",
			"repayment_behavior": "Stable repayment history with monthly review cadence.",
		},
	)
	_append_record(records, "CRM Credit Facility", facility.get("name"))

	bureau = create_or_update_customer360_record(
		"CRM Bureau Report",
		{
			"customer": customer_name,
			"source": "SLIK/OJK Manual Upload",
			"report_date": nowdate(),
			"kol_status": "KOL-1",
			"score": 760 + (index * 5),
			"external_exposure": 850000000 + (index * 50000000),
			"notes": "Seeded for BNI UAT dashboard verification.",
		},
	)
	_append_record(records, "CRM Bureau Report", bureau.get("name"))

	kyc = create_or_update_customer360_record(
		"CRM KYC Review",
		{
			"customer": customer_name,
			"status": "Verified",
			"review_date": nowdate(),
			"next_review_date": add_days(nowdate(), 180),
			"renewal_workflow_status": "Completed",
			"npwp": f"12345678901234{index + 1}",
			"nik": f"317509120101000{index + 1}",
			"employee_count": 1000 + (index * 250),
			"registered_address": f"{display_name} HQ, Jakarta",
			"ekyc_result": "Verified",
			"watchlist": 1 if index == 0 else 0,
			"watchlist_reason": "Strategic review account." if index == 0 else "",
			"notes": "BNI teal UAT seeded profile.",
		},
	)
	_append_record(records, "CRM KYC Review", kyc.get("name"))

	for relationship in (
		{
			"customer": customer_name,
			"related_party": f"{display_name} Holdings",
			"relationship_type": "Shareholder",
			"ownership_percent": 60,
			"is_ubo": 1,
			"exposure": 3000000000,
		},
		{
			"customer": customer_name,
			"related_party": f"{display_name} Pension Fund",
			"relationship_type": "Shareholder",
			"ownership_percent": 40,
			"exposure": 1250000000,
		},
		{
			"customer": customer_name,
			"related_party": sample_row.get("name") or "Assigned RM",
			"relationship_type": "RM",
			"position": sample_row.get("position") or "Relationship Manager",
			"linkedin_url": sample_row.get("linkedin"),
			"aml_pep_status": "Clear",
			"background_check_status": "Clear",
		},
	):
		record = create_or_update_customer360_record("CRM Relationship", relationship)
		_append_record(records, "CRM Relationship", record.get("name"))

	account = create_or_update_customer360_record(
		"CRM Bank Account",
		{
			"customer": customer_name,
			"bank": display_name,
			"account_number": f"8800{index + 1:04d}{index + 7:04d}",
			"account_name": display_name,
			"is_primary": 1,
			"verification_status": "Verified",
			"otp_status": "Verified",
		},
	)
	_append_record(records, "CRM Bank Account", account.get("name"))

	document = create_or_update_customer360_record(
		"CRM Customer Document",
		{
			"customer": customer_name,
			"document_type": "KYC",
			"title": f"{display_name} Corporate KYC Pack",
			"folder": "KYC",
			"version": "1",
			"expiry_status": "Valid",
			"preview_status": "Preview Available",
			"tags": "uat,kyc,bni",
		},
	)
	_append_record(records, "CRM Customer Document", document.get("name"))

	communication = create_or_update_customer360_record(
		"CRM Customer Communication",
		{
			"customer": customer_name,
			"channel": "Email",
			"subject": f"{display_name} lending review",
			"summary": "Seeded relationship follow-up for UAT walk-through.",
		},
	)
	_append_record(records, "CRM Customer Communication", communication.get("name"))

	transaction = create_or_update_customer360_record(
		"CRM Transaction History",
		{
			"customer": customer_name,
			"transaction_type": "Repayment",
			"amount": 175000000 + (index * 10000000),
			"status": "Posted",
		},
	)
	_append_record(records, "CRM Transaction History", transaction.get("name"))

	risk = create_or_update_customer360_record(
		"CRM Risk Profile",
		{
			"customer": customer_name,
			"risk_grade": "A-" if index == 0 else "B+",
			"internal_score": 760 + (index * 5),
			"watchlist_status": "Yes" if index == 0 else "No",
			"early_warning_triggers": "Monitor utilization and renewal timing.",
		},
	)
	_append_record(records, "CRM Risk Profile", risk.get("name"))

	insight = create_or_update_customer360_record(
		"CRM AI Insight",
		{
			"customer": customer_name,
			"title": f"Cross-sell for {display_name}",
			"insight_type": "Cross-sell",
			"confidence_score": 82 - (index * 3),
			"status": "Open",
			"summary": "Seeded AI insight for Customer 360 validation.",
		},
	)
	_append_record(records, "CRM AI Insight", insight.get("name"))

	tag = create_or_update_customer360_record(
		"CRM Customer Tag",
		{"customer": customer_name, "tag": "BNI UAT", "color": "#008C95"},
	)
	_append_record(records, "CRM Customer Tag", tag.get("name"))

	task = create_or_update_customer360_record(
		"CRM Task",
		{
			"title": f"{display_name} covenant review",
			"priority": "High",
			"status": "Todo",
			"assigned_to": frappe.session.user,
			"due_date": f"{add_days(nowdate(), 7)} 09:00:00",
			"reference_doctype": "Customer",
			"reference_docname": customer_name,
			"description": "Seeded follow-up task for Customer 360 and dashboard UAT.",
		},
	)
	_append_record(records, "CRM Task", task.get("name"))

	note = create_or_update_customer360_record(
		"FCRM Note",
		{
			"title": "AI Customer Summary",
			"content": f"- {display_name} seeded for BNI teal UAT\n- Linked lead workbook context and credit artifacts are available.",
			"reference_doctype": "Customer",
			"reference_docname": customer_name,
		},
	)
	_append_record(records, "FCRM Note", note.get("name"))


@frappe.whitelist()
def create_bni_uat_seed():
	_assert_seed_permissions()
	if _load_seed_state():
		records = _load_seed_records()
		return {
			"created": False,
			"status": "already_seeded",
			"records": records,
			"message": _("BNI UAT seed already exists. Clear it before reseeding."),
		}

	workbook_path = _bundled_workbook_path()
	payload = _build_workbook_payload_from_path(workbook_path)
	import_result = _import_rows(payload["row_objects"], DEFAULT_IMPORT_OPTIONS)

	records = {
		"CRM Lead": import_result.get("lead_names", []),
		"FCRM Note": import_result.get("note_names", []),
		"CRM Task": import_result.get("task_names", []),
	}

	for index, (company, sample_row) in enumerate(_select_seed_companies(payload["row_objects"])):
		customer = create_customer_360_customer(company, customer_type="Company")
		_append_record(records, "Customer", customer.get("name"))
		_create_customer_records(customer, sample_row, index, records)

	_store_seed_records(records)
	frappe.db.commit()
	return {
		"created": True,
		"lead_import": {
			"created": import_result.get("created", 0),
			"skipped": import_result.get("skipped", 0),
			"follow_ups_created": import_result.get("follow_ups_created", 0),
			"notes_created": import_result.get("notes_created", 0),
		},
		"customers_seeded": len(records.get("Customer", [])),
		"records": records,
	}


@frappe.whitelist()
def clear_bni_uat_seed():
	_assert_seed_permissions()
	records = _load_seed_records()
	if not records:
		return {"cleared": False, "message": _("No BNI UAT seed data found.")}

	delete_order = [
		"CRM Credit Application",
		"CRM Bureau Report",
		"CRM Credit Facility",
		"CRM KYC Review",
		"CRM Relationship",
		"CRM Bank Account",
		"CRM Customer Document",
		"CRM Customer Communication",
		"CRM Transaction History",
		"CRM Risk Profile",
		"CRM AI Insight",
		"CRM Customer Tag",
		"CRM Task",
		"FCRM Note",
		"CRM Lead",
		"Customer",
	]

	for doctype in delete_order:
		for name in records.get(doctype, []):
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)

	frappe.db.set_default(BNI_UAT_SEED_RECORDS_KEY, None)
	frappe.db.set_default(BNI_UAT_SEED_STATE_KEY, None)
	frappe.db.commit()
	return {"cleared": True, "records": records}
