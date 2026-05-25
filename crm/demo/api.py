import json

import frappe
from frappe.utils.telemetry import capture

DEMO_STATE_KEY = "crm_demo_data_created"
DEMO_LEADS_KEY = "crm_demo_leads"
DEMO_NOTES_KEY = "crm_demo_notes"
DEMO_TASKS_KEY = "crm_demo_tasks"
DEMO_CALL_LOGS_KEY = "crm_demo_call_logs"
DEMO_ACTIVITIES_KEY = "crm_demo_activities"
DEMO_DEALS_KEY = "crm_demo_deals"
DEMO_CUSTOMERS_KEY = "crm_demo_customers"
DEMO_C360_KEY = "crm_demo_customer_360"
DEMO_PORTAL_KEY = "crm_demo_portal"
DEMO_COMMITTEE_KEY = "crm_demo_committee"


def create_demo_data(_args: dict | None = None):
	"""Create demo data from the single BNI UAT seed source.

	The old per-module demo seeders are kept only for cleanup compatibility.
	New demo data should be added to crm.demo.bni_uat so PM/UAT demos have one
	source of truth.
	"""
	if _args is not None and not _args.get("setup_demo"):
		return {"created": False, "message": "Demo data was not requested."}

	if frappe.db.get_default(DEMO_STATE_KEY):
		_clear_legacy_demo_data()

	from crm.demo.bni_uat import create_bni_uat_seed

	result = create_bni_uat_seed()
	capture("demo_data_created", "crm")
	return result


@frappe.whitelist()
def clear_demo_data():
	frappe.only_for(["Sales Manager", "System Manager"], True)

	from crm.demo.bni_uat import clear_bni_uat_seed

	bni_result = clear_bni_uat_seed()
	legacy_result = _clear_legacy_demo_data()
	capture("demo_data_cleared", "crm")
	return {"bni_uat": bni_result, "legacy": legacy_result}


@frappe.whitelist()
def get_demo_state():
	from crm.demo.bni_uat import _load_seed_state

	return {
		"demo_data_created": bool(_load_seed_state() or frappe.db.get_default(DEMO_STATE_KEY)),
		"source": "bni_uat",
	}


def _clear_legacy_demo_data():
	"""Clear records created by the pre-BNI demo orchestrator.

	This lets existing local databases move to the BNI UAT seed without keeping
	the old seed flow as an active source.
	"""
	if not frappe.db.get_default(DEMO_STATE_KEY):
		return {"cleared": False, "message": "No legacy demo data found."}

	from crm.demo.activities import delete_demo_activities
	from crm.demo.call_logs import delete_demo_call_logs
	from crm.demo.customer_360 import delete_demo_customer_360
	from crm.demo.customers import delete_demo_customers
	from crm.demo.deals import delete_demo_deals
	from crm.demo.leads import delete_demo_leads
	from crm.demo.notes import delete_demo_notes
	from crm.demo.committee import delete_demo_committee
	from crm.demo.portal import delete_demo_portal
	from crm.demo.tasks import delete_demo_tasks
	from crm.demo.users import DEMO_USER_EMAILS, delete_demo_users

	lead_names = json.loads(frappe.db.get_default(DEMO_LEADS_KEY) or "[]")
	note_names = json.loads(frappe.db.get_default(DEMO_NOTES_KEY) or "[]")
	task_names = json.loads(frappe.db.get_default(DEMO_TASKS_KEY) or "[]")
	call_log_names = json.loads(frappe.db.get_default(DEMO_CALL_LOGS_KEY) or "[]")
	activity_data = json.loads(frappe.db.get_default(DEMO_ACTIVITIES_KEY) or "{}")
	deal_data = json.loads(frappe.db.get_default(DEMO_DEALS_KEY) or "{}")
	customer_names = json.loads(frappe.db.get_default(DEMO_CUSTOMERS_KEY) or "[]")
	c360_data = json.loads(frappe.db.get_default(DEMO_C360_KEY) or "{}")
	portal_data = json.loads(frappe.db.get_default(DEMO_PORTAL_KEY) or "{}")
	committee_data = json.loads(frappe.db.get_default(DEMO_COMMITTEE_KEY) or "{}")

	delete_demo_committee(committee_data)
	delete_demo_portal(portal_data)
	delete_demo_deals(deal_data, lead_names)
	delete_demo_activities(activity_data)
	delete_demo_notes(note_names)
	delete_demo_tasks(task_names)
	delete_demo_call_logs(call_log_names)
	delete_demo_leads(lead_names)
	delete_demo_customers(customer_names)
	delete_demo_customer_360(c360_data)
	delete_demo_users(DEMO_USER_EMAILS)

	for key in (
		DEMO_LEADS_KEY,
		DEMO_NOTES_KEY,
		DEMO_TASKS_KEY,
		DEMO_CALL_LOGS_KEY,
		DEMO_ACTIVITIES_KEY,
		DEMO_DEALS_KEY,
		DEMO_CUSTOMERS_KEY,
		DEMO_C360_KEY,
		DEMO_PORTAL_KEY,
		DEMO_COMMITTEE_KEY,
		DEMO_STATE_KEY,
	):
		frappe.db.set_default(key, None)

	frappe.db.commit()
	return {"cleared": True}
