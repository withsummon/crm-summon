import frappe
from frappe import _
from frappe.utils import add_days, add_to_date, get_datetime, now_datetime, nowdate, time_diff_in_seconds


def _doctype_ready(doctype):
	return frappe.db.table_exists(doctype)


def recompute_lead_sla():
	"""Recompute sla_status for open leads based on response_by deadline."""
	if not _doctype_ready("CRM Lead"):
		return
	meta = frappe.get_meta("CRM Lead")
	if not meta.has_field("response_by") or not meta.has_field("sla_status"):
		return
	now = now_datetime()
	at_risk_window = add_to_date(now, hours=4)
	leads = frappe.get_all(
		"CRM Lead",
		filters=[["converted", "=", 0], ["response_by", "is", "set"]],
		fields=["name", "response_by", "sla_status"],
		limit=500,
	)
	for lead in leads:
		rb = get_datetime(lead.response_by)
		if rb < now:
			if lead.sla_status not in ("Failed", "Breached"):
				frappe.db.set_value("CRM Lead", lead.name, "sla_status", "Breached", update_modified=False)
		elif rb <= at_risk_window:
			if lead.sla_status not in ("At Risk", "Breached", "Failed"):
				frappe.db.set_value("CRM Lead", lead.name, "sla_status", "At Risk", update_modified=False)
	frappe.db.commit()


def fire_sla_alerts():
	"""Notify owners + managers when leads are at risk or breached."""
	if not _doctype_ready("CRM Lead"):
		return
	from crm.fcrm.doctype.crm_notification.crm_notification import notify_user

	now = now_datetime()

	at_risk = frappe.get_all(
		"CRM Lead",
		filters=[["converted", "=", 0], ["sla_status", "=", "At Risk"]],
		fields=["name", "lead_name", "lead_owner"],
		limit=100,
	)
	for lead in at_risk:
		if lead.lead_owner:
			notify_user({
				"owner": frappe.session.user,
				"assigned_to": lead.lead_owner,
				"notification_type": "SLA",
				"message": _("Lead SLA at risk"),
				"notification_text": _("Lead {0} SLA is approaching breach.").format(lead.lead_name or lead.name),
				"reference_doctype": "CRM Lead",
				"reference_docname": lead.name,
				"redirect_to_doctype": "CRM Lead",
				"redirect_to_docname": lead.name,
			})

	breached = frappe.get_all(
		"CRM Lead",
		filters=[["converted", "=", 0], ["sla_status", "in", ["Breached", "Failed"]]],
		fields=["name", "lead_name", "lead_owner"],
		limit=100,
	)
	for lead in breached:
		if lead.lead_owner:
			notify_user({
				"owner": frappe.session.user,
				"assigned_to": lead.lead_owner,
				"notification_type": "SLA",
				"message": _("Lead SLA breached"),
				"notification_text": _("Lead {0} SLA has breached.").format(lead.lead_name or lead.name),
				"reference_doctype": "CRM Lead",
				"reference_docname": lead.name,
			})
		managers = frappe.get_all("User", filters={"enabled": 1}, fields=["name"])
		for mgr in managers:
			if "Sales Manager" in frappe.get_roles(mgr.name):
				notify_user({
					"owner": frappe.session.user,
					"assigned_to": mgr.name,
					"notification_type": "SLA",
					"message": _("Lead SLA breached"),
					"notification_text": _("Lead {0} SLA has breached.").format(lead.lead_name or lead.name),
					"reference_doctype": "CRM Lead",
					"reference_docname": lead.name,
				})

	frappe.db.commit()


def compute_lead_aging():
	"""Compute aging_band for open leads based on last_activity_on."""
	if not _doctype_ready("CRM Lead"):
		return
	meta = frappe.get_meta("CRM Lead")
	if not meta.has_field("last_activity_on"):
		return
	for days, band in ((7, "Fresh"), (14, "Warm"), (30, "Stale"), (60, "Frozen")):
		cutoff = add_days(nowdate(), -days)
		leads = frappe.get_all(
			"CRM Lead",
			filters=[["converted", "=", 0], ["last_activity_on", "<=", cutoff]],
			fields=["name"],
			limit=200,
		)
		for lead in leads:
			frappe.db.set_value("CRM Lead", lead.name, "aging_band", band, update_modified=False)
	frappe.db.commit()


def fire_aging_alerts():
	"""Delegate to the existing aging processor for 7/14/30/60-day alerts."""
	from crm.api.lead_management import process_lead_aging
	process_lead_aging()


def run_nurture_sequences():
	"""Stub for nurture sequence runner."""
	if not _doctype_ready("CRM Lead Nurture Sequence"):
		return
	sequences = frappe.get_all(
		"CRM Lead Nurture Sequence",
		filters={"active": 1},
		fields=["name"],
	)
	for seq in sequences:
		doc = frappe.get_doc("CRM Lead Nurture Sequence", seq.name)
		# Placeholder: actual runner deferred to Phase 2 sub-page work.
		_ = doc
