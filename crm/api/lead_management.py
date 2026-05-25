import csv
import io
import json
from difflib import SequenceMatcher
from pathlib import Path

import frappe
from frappe import _
from frappe.desk.form.assign_to import add as assign
from frappe.utils import add_days, cint, flt, get_datetime, now, now_datetime, nowdate
from frappe.utils.file_manager import save_file

from crm.fcrm.doctype.crm_notification.crm_notification import notify_user


LEAD_FIELDS = {
	"first_name",
	"middle_name",
	"last_name",
	"lead_name",
	"email",
	"mobile_no",
	"phone",
	"organization",
	"website",
	"territory",
	"industry",
	"job_title",
	"source",
	"status",
	"lead_owner",
	"capture_channel",
	"campaign",
	"referrer_type",
	"referrer",
	"referral_fee",
	"npwp",
	"utm_source",
	"utm_medium",
	"utm_campaign",
	"utm_content",
	"utm_term",
}


def _as_dict(value):
	if isinstance(value, str):
		return frappe._dict(json.loads(value or "{}"))
	return frappe._dict(value or {})


def _as_list(value):
	if isinstance(value, str):
		return json.loads(value or "[]")
	if isinstance(value, set):
		return list(value)
	return value or []


def _normalize(value):
	return str(value or "").strip()


def _normalize_phone(value):
	value = _normalize(value)
	if "wa.me/" in value:
		value = value.split("wa.me/")[-1]
	return "".join(ch for ch in value if ch.isdigit() or ch == "+")


def _normalize_npwp(value):
	return "".join(ch for ch in _normalize(value) if ch.isdigit())


def _ensure_lead_source(source, group=None):
	source = _normalize(source)
	if not source:
		return None
	if not frappe.db.exists("CRM Lead Source", source):
		doc = frappe.new_doc("CRM Lead Source")
		doc.source_name = source
		if frappe.get_meta("CRM Lead Source").has_field("source_group"):
			doc.source_group = group or "Other"
		if frappe.get_meta("CRM Lead Source").has_field("is_active"):
			doc.is_active = 1
		doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
	return source


def _ensure_lead_campaign(campaign, source=None, payload=None):
	campaign = _normalize(campaign)
	if not campaign:
		return None
	if not frappe.db.table_exists("CRM Lead Campaign"):
		return campaign
	if not frappe.db.exists("CRM Lead Campaign", campaign):
		doc = frappe.new_doc("CRM Lead Campaign")
		doc.campaign_name = campaign
		if doc.meta.has_field("status"):
			doc.status = "Active"
		if source and doc.meta.has_field("source"):
			doc.source = source
		payload = _as_dict(payload)
		for fieldname in ("utm_source", "utm_medium", "utm_campaign"):
			if doc.meta.has_field(fieldname) and payload.get(fieldname):
				doc.set(fieldname, payload.get(fieldname))
		doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
	return campaign


def _lead_status_by_type(status_type, fallback="New"):
	status = frappe.db.get_value("CRM Lead Status", {"type": status_type}, "name")
	return status or (fallback if frappe.db.exists("CRM Lead Status", fallback) else None)


def _lead_lost_reason():
	if frappe.db.exists("CRM Lost Reason", "Auto Closed"):
		return "Auto Closed"
	if frappe.db.exists("CRM Lost Reason", "Other"):
		return "Other"
	try:
		frappe.get_doc({"doctype": "CRM Lost Reason", "lost_reason": "Auto Closed"}).insert(
			ignore_permissions=True, ignore_if_duplicate=True
		)
		return "Auto Closed"
	except Exception:
		return None


def _log_intake(channel, payload=None, lead=None, status="Received", message=None, error=None):
	if not frappe.db.table_exists("CRM Lead Intake Log"):
		return None
	payload = _as_dict(payload)
	doc = frappe.new_doc("CRM Lead Intake Log")
	doc.channel = channel
	doc.status = status
	doc.lead = lead
	doc.source = payload.get("source")
	doc.campaign = payload.get("campaign")
	doc.external_id = payload.get("external_id")
	doc.payload = json.dumps(payload, default=str, indent=2)
	doc.message = message
	doc.error = error
	doc.insert(ignore_permissions=True)
	return doc.name


def _duplicate_score(candidate, data):
	score = 0
	basis = []
	email = _normalize(data.get("email")).lower()
	phone = _normalize_phone(data.get("mobile_no") or data.get("phone"))
	npwp = _normalize_npwp(data.get("npwp"))

	if email and _normalize(candidate.get("email")).lower() == email:
		score = max(score, 100)
		basis.append("email")
	if phone and phone in {
		_normalize_phone(candidate.get("mobile_no")),
		_normalize_phone(candidate.get("phone")),
	}:
		score = max(score, 100)
		basis.append("phone")
	if npwp and _normalize_npwp(candidate.get("npwp")) == npwp:
		score = max(score, 100)
		basis.append("npwp")

	name_ratio = SequenceMatcher(
		None,
		_normalize(candidate.get("lead_name")).lower(),
		_normalize(data.get("lead_name") or data.get("first_name")).lower(),
	).ratio()
	org_ratio = SequenceMatcher(
		None,
		_normalize(candidate.get("organization")).lower(),
		_normalize(data.get("organization")).lower(),
	).ratio()
	fuzzy_score = int(max(name_ratio, org_ratio) * 85)
	if fuzzy_score >= 70:
		score = max(score, fuzzy_score)
		basis.append("fuzzy")

	return score, ", ".join(dict.fromkeys(basis))


@frappe.whitelist()
def preview_duplicates(data=None, lead=None, limit=5):
	data = _as_dict(data)
	if lead:
		data.update(frappe.db.get_value("CRM Lead", lead, list(LEAD_FIELDS), as_dict=True) or {})

	or_filters = []
	if data.get("email"):
		or_filters.append(["email", "=", _normalize(data.get("email")).lower()])
	phone = _normalize_phone(data.get("mobile_no") or data.get("phone"))
	if phone:
		or_filters.extend([["mobile_no", "=", phone], ["phone", "=", phone]])
	npwp = _normalize_npwp(data.get("npwp"))
	if npwp and frappe.get_meta("CRM Lead").has_field("npwp"):
		or_filters.append(["npwp", "=", npwp])

	fields = ["name", "lead_name", "email", "mobile_no", "phone", "organization"]
	if frappe.get_meta("CRM Lead").has_field("npwp"):
		fields.append("npwp")
	candidates = []
	seen = set()

	if or_filters:
		for row in frappe.get_all("CRM Lead", fields=fields, or_filters=or_filters, limit=limit * 2):
			if row.name == lead or row.name in seen:
				continue
			seen.add(row.name)
			score, basis = _duplicate_score(row, data)
			if score >= 70:
				candidates.append({**row, "score": score, "match_basis": basis})

	if len(candidates) < cint(limit):
		text = _normalize(data.get("lead_name") or data.get("organization") or data.get("first_name"))
		search_filters = []
		if text:
			search_filters.append(["lead_name", "like", f"%{text[:20]}%"])
		if data.get("organization"):
			search_filters.append(["organization", "like", f"%{_normalize(data.get('organization'))[:20]}%"])
		for search_filter in search_filters:
			for row in frappe.get_all("CRM Lead", fields=fields, filters=[search_filter], limit=limit * 2):
				if row.name == lead or row.name in seen:
					continue
				seen.add(row.name)
				score, basis = _duplicate_score(row, data)
				if score >= 70:
					candidates.append({**row, "score": score, "match_basis": basis})

	candidates = sorted(candidates, key=lambda row: row["score"], reverse=True)[: cint(limit)]
	if lead and frappe.db.table_exists("CRM Lead Duplicate Candidate"):
		for row in candidates:
			if not frappe.db.exists(
				"CRM Lead Duplicate Candidate",
				{"lead": lead, "duplicate_lead": row["name"], "status": "Open"},
			):
				frappe.get_doc(
					{
						"doctype": "CRM Lead Duplicate Candidate",
						"lead": lead,
						"duplicate_lead": row["name"],
						"score": row["score"],
						"match_basis": row["match_basis"],
					}
				).insert(ignore_permissions=True)
	return candidates


def _score_band(score):
	if score >= 75:
		return "Hot"
	if score >= 40:
		return "Warm"
	return "Cold"


def _evaluate_rule(lead, rule):
	value = lead.get(rule.fieldname)
	expected = rule.value
	operator = rule.operator or "is set"
	if operator == "is set":
		return bool(value)
	if operator == "equals":
		return _normalize(value).lower() == _normalize(expected).lower()
	if operator == "contains":
		return _normalize(expected).lower() in _normalize(value).lower()
	if operator == "greater than":
		return flt(value) > flt(expected)
	if operator == "less than":
		return flt(value) < flt(expected)
	return False


@frappe.whitelist()
def score_lead(lead):
	doc = frappe.get_doc("CRM Lead", lead)
	score = 0
	model = frappe.db.get_value("CRM Lead Scoring Model", {"is_active": 1}, "name")
	if model:
		model_doc = frappe.get_doc("CRM Lead Scoring Model", model)
		for rule in model_doc.rules:
			if _evaluate_rule(doc, rule):
				score += cint(rule.weight)
	else:
		default_weights = {
			"email": 15,
			"mobile_no": 15,
			"organization": 10,
			"job_title": 10,
			"source": 10,
			"campaign": 10,
			"annual_revenue": 15,
			"npwp": 15,
		}
		for fieldname, weight in default_weights.items():
			if doc.get(fieldname):
				score += weight

	score = min(score, 100)
	doc.db_set(
		{
			"lead_score": score,
			"lead_score_band": _score_band(score),
			"lead_quality_probability": score,
			"lead_quality_confidence": 85 if model else 60,
		},
		update_modified=False,
	)
	return {
		"lead": lead,
		"score": score,
		"band": _score_band(score),
		"probability": score,
		"confidence": 85 if model else 60,
	}


def _choose_assignment_user(lead):
	if lead.get("lead_owner"):
		return lead.get("lead_owner")
	users = frappe.get_all(
		"Has Role",
		filters={"role": "Sales User", "parenttype": "User"},
		pluck="parent",
		limit=20,
	)
	users = [user for user in users if frappe.db.get_value("User", user, "enabled")]
	if not users:
		return frappe.session.user

	counts = {
		user: frappe.db.count("CRM Lead", {"lead_owner": user, "converted": 0})
		for user in users
	}
	return min(counts, key=counts.get)


def _log_assignment(lead, from_user=None, to_user=None, reason=None, assignment_type="Manual", idle_hours=None):
	if not frappe.db.table_exists("CRM Lead Assignment Log"):
		return
	frappe.get_doc(
		{
			"doctype": "CRM Lead Assignment Log",
			"lead": lead,
			"from_user": from_user,
			"to_user": to_user,
			"reason": reason,
			"assignment_type": assignment_type,
			"idle_hours": idle_hours,
		}
	).insert(ignore_permissions=True)


@frappe.whitelist()
def route_lead(lead, strategy="Round Robin", reason=None):
	doc = frappe.get_doc("CRM Lead", lead)
	to_user = _choose_assignment_user(doc)
	if not to_user:
		return {"lead": lead, "assigned_to": None}
	from_user = doc.lead_owner
	doc.db_set(
		{
			"lead_owner": to_user,
			"first_assigned_on": doc.first_assigned_on or now(),
			"reassignment_reason": reason,
		}
	)
	assign({"assign_to": [to_user], "doctype": "CRM Lead", "name": lead}, ignore_permissions=True)
	_log_assignment(lead, from_user, to_user, reason or strategy, strategy)
	return {"lead": lead, "assigned_to": to_user}


@frappe.whitelist()
def capture_lead(data=None, channel="Manual", allow_duplicate=False):
	data = _as_dict(data)
	channel = channel or data.get("capture_channel") or "Manual"
	try:
		source = _ensure_lead_source(data.get("source") or channel, _source_group_for_channel(channel))
		if source:
			data["source"] = source
		if data.get("campaign"):
			data["campaign"] = _ensure_lead_campaign(data.get("campaign"), source, data)

		if data.get("mobile_no") or data.get("phone"):
			data["mobile_no"] = _normalize_phone(data.get("mobile_no") or data.get("phone"))
		if data.get("npwp"):
			data["npwp"] = _normalize_npwp(data.get("npwp"))

		duplicates = preview_duplicates(data=data)
		exact_duplicate = next((row for row in duplicates if cint(row.get("score")) >= 100), None)
		if exact_duplicate and not allow_duplicate:
			_log_intake(channel, data, exact_duplicate.get("name"), "Duplicate", _("Exact duplicate blocked"))
			return {"created": False, "duplicate": exact_duplicate, "duplicates": duplicates}

		lead_data = {"doctype": "CRM Lead", "capture_channel": channel}
		lead_data.update({key: value for key, value in data.items() if key in LEAD_FIELDS and value not in (None, "")})
		if not lead_data.get("first_name") and lead_data.get("lead_name"):
			name_parts = str(lead_data["lead_name"]).split()
			lead_data["first_name"] = name_parts[0]
			if len(name_parts) > 1 and not lead_data.get("last_name"):
				lead_data["last_name"] = " ".join(name_parts[1:])
		if not lead_data.get("lead_owner"):
			lead_data["lead_owner"] = _choose_assignment_user(lead_data)

		doc = frappe.get_doc(lead_data)
		doc.flags.allow_duplicate = allow_duplicate
		doc.flags.enforce_duplicate_check = True
		doc.insert(ignore_permissions=True, ignore_links=True)
		score_lead(doc.name)
		route_lead(doc.name, "Initial", _("Auto-assigned on capture"))
		duplicates = preview_duplicates(data=data, lead=doc.name)
		if duplicates and frappe.get_meta("CRM Lead").has_field("duplicate_of"):
			doc.db_set(
				{"duplicate_of": duplicates[0]["name"], "duplicate_score": duplicates[0]["score"]},
				update_modified=False,
			)
		_log_intake(channel, data, doc.name, "Created", _("Lead created"))
		return {"created": True, "lead": doc.name, "duplicates": duplicates, "score": score_lead(doc.name)}
	except Exception as exc:
		_log_intake(channel, data, None, "Failed", error=str(exc))
		raise


def _source_group_for_channel(channel):
	if channel in {"Walk-in", "Manual"}:
		return "Offline"
	if channel == "Referral":
		return "Referral"
	if channel == "Partner":
		return "Partner"
	return "Digital"


@frappe.whitelist()
def merge_leads(primary, duplicate):
	if not frappe.has_permission("CRM Lead", "write", primary):
		frappe.throw(_("Not allowed to merge Lead"), frappe.PermissionError)
	primary_doc = frappe.get_doc("CRM Lead", primary)
	duplicate_doc = frappe.get_doc("CRM Lead", duplicate)
	for fieldname in LEAD_FIELDS:
		if frappe.get_meta("CRM Lead").has_field(fieldname) and not primary_doc.get(fieldname) and duplicate_doc.get(fieldname):
			primary_doc.set(fieldname, duplicate_doc.get(fieldname))
	primary_doc.save(ignore_permissions=True)
	frappe.db.set_value("CRM Lead", duplicate, {"duplicate_of": primary, "converted": 1})
	frappe.db.set_value(
		"CRM Lead Duplicate Candidate",
		{"lead": primary, "duplicate_lead": duplicate, "status": "Open"},
		{"status": "Merged", "resolved_by": frappe.session.user, "resolved_on": now()},
	)
	return {"primary": primary, "duplicate": duplicate, "merged": True}


@frappe.whitelist()
def reassign_leads(leads, to_user, reason):
	leads = _as_list(leads)
	if not reason:
		frappe.throw(_("Reassignment reason is mandatory."))
	for lead in leads:
		if not frappe.has_permission("CRM Lead", "write", lead):
			frappe.throw(_("Not allowed to reassign Lead {0}").format(lead), frappe.PermissionError)
		from_user = frappe.db.get_value("CRM Lead", lead, "lead_owner")
		frappe.db.set_value(
			"CRM Lead",
			lead,
			{
				"lead_owner": to_user,
				"first_assigned_on": frappe.db.get_value("CRM Lead", lead, "first_assigned_on") or now(),
				"reassignment_reason": reason,
			},
		)
		assign({"assign_to": [to_user], "doctype": "CRM Lead", "name": lead}, ignore_permissions=True)
		_log_assignment(lead, from_user, to_user, reason, "Bulk" if len(leads) > 1 else "Manual")
		_notify_lead_user(to_user, lead, _("Lead reassigned"), _("Lead {0} has been assigned to you.").format(lead))
	return {"updated": len(leads)}


@frappe.whitelist()
def bulk_tag_leads(leads, tag, color="#0f766e", notes=None):
	leads = _as_list(leads)
	tag = _normalize(tag)
	if not tag:
		frappe.throw(_("Tag is required."))
	if not frappe.db.exists("CRM Lead Tag", tag):
		frappe.get_doc({"doctype": "CRM Lead Tag", "tag": tag, "color": color, "is_active": 1}).insert(
			ignore_permissions=True, ignore_if_duplicate=True
		)
	created = 0
	for lead in leads:
		if not frappe.db.exists("CRM Lead Tag Link", {"lead": lead, "tag": tag}):
			frappe.get_doc(
				{
					"doctype": "CRM Lead Tag Link",
					"lead": lead,
					"tag": tag,
					"color": color,
					"notes": notes,
				}
			).insert(ignore_permissions=True)
			created += 1
	return {"tag": tag, "updated": created}


@frappe.whitelist()
def get_lead_summary(lead):
	doc = frappe.get_doc("CRM Lead", lead)
	duplicates = preview_duplicates(lead=lead)
	tags = frappe.get_all(
		"CRM Lead Tag Link",
		filters={"lead": lead},
		fields=["tag", "color", "creation"],
		order_by="creation desc",
	) if frappe.db.table_exists("CRM Lead Tag Link") else []
	assignments = frappe.get_all(
		"CRM Lead Assignment Log",
		filters={"lead": lead},
		fields=["from_user", "to_user", "reason", "assignment_type", "creation"],
		order_by="creation desc",
		limit=10,
	) if frappe.db.table_exists("CRM Lead Assignment Log") else []
	return {
		"score": {
			"value": doc.get("lead_score") or 0,
			"band": doc.get("lead_score_band") or _score_band(doc.get("lead_score") or 0),
			"probability": doc.get("lead_quality_probability") or 0,
			"confidence": doc.get("lead_quality_confidence") or 0,
		},
		"attribution": {
			"channel": doc.get("capture_channel"),
			"source": doc.get("source"),
			"campaign": doc.get("campaign"),
			"utm_source": doc.get("utm_source"),
			"utm_medium": doc.get("utm_medium"),
			"utm_campaign": doc.get("utm_campaign"),
			"referrer_type": doc.get("referrer_type"),
			"referrer": doc.get("referrer"),
		},
		"duplicates": duplicates,
		"tags": tags,
		"assignments": assignments,
	}


@frappe.whitelist()
def get_lead_uat_summary(lead):
	"""Backward-compatible alias for older frontend bundles."""
	return get_lead_summary(lead)


@frappe.whitelist()
def get_lead_funnel(from_date=None, to_date=None, user=None):
	from_date = from_date or add_days(nowdate(), -30)
	to_date = to_date or nowdate()
	filters = [["creation", ">=", from_date], ["creation", "<", add_days(to_date, 1)]]
	if user:
		filters.append(["lead_owner", "=", user])
	status_rows = frappe.get_all(
		"CRM Lead",
		fields=["status", "count(name) as count"],
		filters=filters,
		group_by="status",
		order_by="count desc",
	)
	total = sum(cint(row.count) for row in status_rows) or 1
	converted = frappe.db.count("CRM Lead", filters=filters + [["converted", "=", 1]])
	lost_statuses = frappe.get_all("CRM Lead Status", filters={"type": "Lost"}, pluck="name")
	lost = frappe.db.count("CRM Lead", filters=filters + [["status", "in", lost_statuses]]) if lost_statuses else 0
	return {
		"total": total,
		"converted": converted,
		"lost": lost,
		"conversion_rate": round((converted / total) * 100, 2),
		"stages": [
			{"status": row.status or _("Unassigned"), "count": cint(row.count), "percent": round((cint(row.count) / total) * 100, 2)}
			for row in status_rows
		],
	}


@frappe.whitelist()
def get_kpi_ribbon():
	today_str = nowdate()
	new_today = 0
	aging_stale = 0
	sla_breaching = 0
	dedupe_pending = 0

	if frappe.db.table_exists("CRM Lead"):
		new_today = frappe.db.count("CRM Lead", {"converted": 0, "creation": [">=", today_str]})
		aging_cutoff = add_days(today_str, -14)
		aging_field = "last_activity_on" if frappe.get_meta("CRM Lead").has_field("last_activity_on") else "modified"
		aging_stale = frappe.db.count("CRM Lead", {"converted": 0, aging_field: ["<=", aging_cutoff]})

		breach_statuses = ["At Risk", "Breached", "Failed"]
		meta = frappe.get_meta("CRM Lead")
		if meta.has_field("sla_status"):
			sla_breaching = frappe.db.count("CRM Lead", {
				"converted": 0,
				"sla_status": ["in", breach_statuses],
			})

	if frappe.db.table_exists("CRM Lead Duplicate Candidate"):
		dedupe_pending = frappe.db.count("CRM Lead Duplicate Candidate", {"status": "Open"})

	return {
		"new_today": new_today,
		"aging_stale": aging_stale,
		"sla_breaching": sla_breaching,
		"dedupe_pending": dedupe_pending,
	}


@frappe.whitelist()
def export_leads(filters=None, format="CSV", email_to=None):
	filters = _as_dict(filters)
	format = (format or "CSV").upper()
	rows = frappe.get_all(
		"CRM Lead",
		filters=filters,
		fields=[
			"name",
			"lead_name",
			"organization",
			"email",
			"mobile_no",
			"status",
			"source",
			"campaign",
			"lead_score",
			"lead_score_band",
			"lead_owner",
			"creation",
		],
		order_by="modified desc",
		limit=0,
	)
	job = None
	if frappe.db.table_exists("CRM Lead Export Job"):
		job = frappe.get_doc(
			{
				"doctype": "CRM Lead Export Job",
				"status": "Processing",
				"format": format,
				"row_count": len(rows),
				"filters_json": json.dumps(filters),
				"email_to": email_to,
			}
		).insert(ignore_permissions=True)
	if len(rows) > 1000 and job:
		frappe.enqueue(
			"crm.api.lead_management._complete_export_job",
			queue="long",
			job_name=f"lead-export-{job.name}",
			job=job.name,
			rows=[dict(row) for row in rows],
			format=format,
			email_to=email_to,
		)
		job.db_set("status", "Queued")
		return {"async": True, "job": job.name, "row_count": len(rows)}
	file_url = _write_export_file(rows, format)
	if job:
		job.db_set({"status": "Completed", "file_url": file_url})
	if email_to:
		frappe.sendmail(recipients=[email_to], subject=_("Lead export is ready"), message=file_url)
	return {"async": False, "file_url": file_url, "row_count": len(rows), "job": job.name if job else None}


def _complete_export_job(job, rows, format="CSV", email_to=None):
	try:
		file_url = _write_export_file(rows, format)
		frappe.db.set_value("CRM Lead Export Job", job, {"status": "Completed", "file_url": file_url})
		if email_to:
			frappe.sendmail(recipients=[email_to], subject=_("Lead export is ready"), message=file_url)
	except Exception as exc:
		frappe.db.set_value("CRM Lead Export Job", job, {"status": "Failed", "error": str(exc)})
		raise


def _write_export_file(rows, format="CSV"):
	output = io.StringIO()
	fields = list(rows[0].keys()) if rows else ["name"]
	writer = csv.DictWriter(output, fieldnames=fields)
	writer.writeheader()
	for row in rows:
		writer.writerow({field: row.get(field) for field in fields})
	content = output.getvalue()
	extension = "csv" if format in {"CSV", "XLSX"} else "pdf"
	filename = f"lead-export-{frappe.generate_hash(length=8)}.{extension}"
	if format == "PDF":
		content = "Lead Export\n\n" + content
	file_doc = save_file(filename, content.encode(), "CRM Lead Export Job", "", is_private=1)
	return file_doc.file_url


def _notify_lead_user(user, lead, title, text):
	if not user:
		return
	notify_user(
		{
			"owner": frappe.session.user,
			"assigned_to": user,
			"notification_type": "Assignment",
			"message": title,
			"notification_text": text,
			"reference_doctype": "CRM Lead",
			"reference_docname": lead,
			"redirect_to_doctype": "CRM Lead",
			"redirect_to_docname": lead,
		}
	)


@frappe.whitelist()
def mock_whatsapp_intake(payload=None):
	payload = _as_dict(payload)
	payload.setdefault("capture_channel", "WhatsApp")
	payload.setdefault("source", "WhatsApp")
	if payload.get("message") and not payload.get("lead_name"):
		payload["lead_name"] = payload["message"][:80]
	return capture_lead(payload, "WhatsApp")


@frappe.whitelist()
def mock_email_intake(payload=None):
	payload = _as_dict(payload)
	payload.setdefault("capture_channel", "Email")
	payload.setdefault("source", "Email")
	payload.setdefault("lead_name", payload.get("subject") or payload.get("sender") or _("Email Lead"))
	return capture_lead(payload, "Email")


@frappe.whitelist()
def mock_widget_intake(payload=None):
	payload = _as_dict(payload)
	payload.setdefault("capture_channel", "Widget")
	payload.setdefault("source", "Web Widget")
	return capture_lead(payload, "Widget")


@frappe.whitelist()
def mock_mobile_intake(payload=None):
	payload = _as_dict(payload)
	payload.setdefault("capture_channel", "Mobile")
	payload.setdefault("source", "Mobile App")
	return capture_lead(payload, "Mobile")


@frappe.whitelist()
def mock_ocr_intake(payload=None):
	payload = _as_dict(payload)
	payload.setdefault("capture_channel", "OCR")
	payload.setdefault("source", "Walk-in OCR")
	if payload.get("id_number") and not payload.get("npwp"):
		payload["npwp"] = payload["id_number"]
	return capture_lead(payload, "OCR")


@frappe.whitelist()
def delete_lead(name):
	if not frappe.has_permission("CRM Lead", "write", name):
		frappe.throw(_("Not allowed to delete Lead"), frappe.PermissionError)
	try:
		frappe.delete_doc("CRM Lead", name, ignore_permissions=True)
		return {"name": name, "deleted": True, "hard_deleted": True}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "CRM Lead hard delete failed; applying soft delete")
	lost_status = _lead_status_by_type("Lost", "Lost")
	closed_status = _lead_status_by_type("Closed", "Closed")
	status = lost_status or closed_status or "Closed"
	reason = _lead_lost_reason() or "Auto Closed"
	updates = {"status": status, "converted": 1}
	if lost_status:
		updates["lost_reason"] = reason
		updates["lost_notes"] = _("Soft-deleted by user.")
	if frappe.get_meta("CRM Lead").has_field("is_deleted"):
		updates["is_deleted"] = 1
	frappe.db.set_value("CRM Lead", name, updates)
	return {"name": name, "deleted": True, "status": status}


@frappe.whitelist()
def close_lead(name, reason):
	if not reason:
		frappe.throw(_("Reason is required."))
	if not frappe.has_permission("CRM Lead", "write", name):
		frappe.throw(_("Not allowed to close Lead"), frappe.PermissionError)
	closed_status = _lead_status_by_type("Closed", "Closed")
	status = closed_status or "Closed"
	frappe.db.set_value("CRM Lead", name, {"status": status, "reassignment_reason": reason})
	_log_assignment(name, None, None, reason, "Close")
	return {"name": name, "status": status, "reason": reason}


@frappe.whitelist()
def seed_lead_sample_data():
	created = []
	statuses = ["New", "Open", "Replied", "Opportunity", "Quotation", "Converted", "Do Not Contact"]
	if frappe.db.table_exists("CRM Lead Status"):
		status_docs = frappe.get_all("CRM Lead Status", fields=["name", "type"])
		if status_docs:
			statuses = [s["name"] for s in status_docs if s.get("type") != "Lost"]
		if not statuses:
			statuses = ["New", "Open", "Replied", "Opportunity", "Quotation", "Converted", "Do Not Contact"]
	sources = ["Web Form", "Walk-in", "Referral", "Email", "WhatsApp", "Manual", "Campaign"]
	score_bands = ["Cold", "Warm", "Hot"]
	orgs = [
		"PT Maju Jaya", "CV Cahaya Terang", "PT Teknologi Maju", "PT Industri Nusantara",
		"PT Sinar Abadi", "CV Delta Mandiri", "PT Pratama Sejahtera", "PT Global Vision",
		"PT Mitra Solusi", "CV Karya Bersama", "PT Bangun Negeri", "PT Sejahtera Mandiri",
		"CV Harapan Jaya", "PT Lestari Abadi", "PT Nusa Indah", "PT Sumber Rejeki",
		"CV Sukses Selalu", "PT Berkah Abadi", "PT Sentosa Makmur", "CV Citra Nusantara",
	]
	for i in range(18):
		first = f"Sample{i+1}"
		if frappe.db.exists("CRM Lead", {"first_name": first}):
			continue
		score = min(100, max(10, (i % 5) * 20 + (i % 3) * 10))
		last = f"User{i+1}"
		data = {
			"doctype": "CRM Lead",
			"first_name": first,
			"last_name": last,
			"organization": orgs[i % len(orgs)],
			"email": f"sample{i+1}@example.com",
			"mobile_no": f"0812{i+1:04d}{i+1:04d}",
			"source": sources[i % len(sources)],
			"status": statuses[i % len(statuses)],
			"lead_score": score,
			"lead_score_band": score_bands[i % len(score_bands)],
			"lead_owner": _choose_assignment_user({}),
			"capture_channel": sources[i % len(sources)],
		}
		doc = frappe.get_doc(data)
		doc.flags.allow_duplicate = True
		doc.insert(ignore_permissions=True, ignore_links=True)
		created.append(doc.name)
	return {"created": len(created), "leads": created}


@frappe.whitelist()
def process_idle_reassignments():
	if not frappe.db.table_exists("CRM Lead"):
		return
	cutoff = add_days(now_datetime(), -1)
	leads = frappe.get_all(
		"CRM Lead",
		filters=[
			["converted", "=", 0],
			["modified", "<", cutoff],
			["lead_owner", "!=", ""],
		],
		fields=["name", "lead_owner", "modified"],
		limit=100,
	)
	for lead in leads:
		idle_hours = round((now_datetime() - get_datetime(lead.modified)).total_seconds() / 3600, 2)
		new_owner = _choose_assignment_user({"lead_owner": None})
		if new_owner and new_owner != lead.lead_owner:
			frappe.db.set_value(
				"CRM Lead",
				lead.name,
				{"lead_owner": new_owner, "reassignment_reason": _("Idle more than 24 hours")},
			)
			assign({"assign_to": [new_owner], "doctype": "CRM Lead", "name": lead.name}, ignore_permissions=True)
			_log_assignment(lead.name, lead.lead_owner, new_owner, _("Idle more than 24 hours"), "Idle Reassignment", idle_hours)
	return {"reassigned": len(leads)}


@frappe.whitelist()
def process_lead_aging():
	if not frappe.db.table_exists("CRM Lead"):
		return
	for days in (7, 14, 30, 60):
		target_date = add_days(nowdate(), -days)
		leads = frappe.get_all(
			"CRM Lead",
			filters=[
				["converted", "=", 0],
				["creation", "<=", target_date],
			],
			fields=["name", "lead_owner", "creation", "status"],
			limit=200,
		)
		for lead in leads:
			if days == 60:
				lost_status = _lead_status_by_type("Lost", "Lost")
				lost_reason = _lead_lost_reason()
				if lost_status:
					frappe.db.set_value(
						"CRM Lead",
						lead.name,
						{
							"status": lost_status,
							"lost_reason": lost_reason,
							"lost_notes": _("Auto-closed after 60 days without conversion."),
							"dropped_off_on": now(),
						},
					)
				continue
			if lead.lead_owner:
				_notify_lead_user(
					lead.lead_owner,
					lead.name,
					_("Lead aging alert"),
					_("Lead {0} has had no conversion for {1} days.").format(lead.name, days),
				)
	return {"processed": True}
