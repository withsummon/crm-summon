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
		score = min(score, 100)
		band = _score_band(score)
		confidence = 85
	else:
		band = ""
		confidence = 0

	score = min(score, 100)
	try:
		from crm.lead_quality_model import predict_quality
		quality = predict_quality(doc)
	except Exception:
		quality = {"probability": score, "confidence": 85 if model else 60}
	doc.db_set(
		{
			"lead_score": score,
			"lead_score_band": _score_band(score),
			"lead_quality_probability": quality["probability"],
			"lead_quality_confidence": quality["confidence"],
		},
		update_modified=False,
	)
	return {
		"lead": lead,
		"score": score,
		"band": _score_band(score),
		"probability": quality["probability"],
		"confidence": quality["confidence"],
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
	format = (format or "CSV").upper()
	hash_id = frappe.generate_hash(length=8)
	if format == "PDF":
		from frappe.utils.pdf import get_pdf
		html = frappe.render_template(
			"crm/templates/exports/lead_list.html",
			{
				"rows": rows,
				"generated_on": frappe.utils.now_datetime().strftime("%Y-%m-%d %H:%M"),
			},
		)
		content = get_pdf(html)
		filename = f"lead-export-{hash_id}.pdf"
		file_doc = save_file(filename, content, "CRM Lead Export Job", "", is_private=1)
		return file_doc.file_url
	output = io.StringIO()
	fields = list(rows[0].keys()) if rows else ["name"]
	writer = csv.DictWriter(output, fieldnames=fields)
	writer.writeheader()
	for row in rows:
		writer.writerow({field: row.get(field) for field in fields})
	content = output.getvalue()
	filename = f"lead-export-{hash_id}.csv"
	file_doc = save_file(filename, content.encode(), "CRM Lead Export Job", "", is_private=1)
	return file_doc.file_url


@frappe.whitelist()
def print_lead(lead):
	if not frappe.db.exists("CRM Lead", lead):
		frappe.throw(_("Lead not found."))
	doc = frappe.get_doc("CRM Lead", lead)
	tags = []
	if frappe.db.table_exists("CRM Lead Tag Link"):
		tags = frappe.get_all(
			"CRM Lead Tag Link",
			filters={"lead": lead},
			fields=["tag", "color"],
		)
	activities = []
	if frappe.db.table_exists("CRM Activity"):
		activities = frappe.get_all(
			"CRM Activity",
			filters={"reference_docname": lead, "reference_doctype": "CRM Lead"},
			fields=["activity_type", "owner", "creation", "message"],
			order_by="creation desc",
			limit=50,
		)
	from frappe.utils.pdf import get_pdf
	html = frappe.render_template(
		"crm/templates/exports/lead_detail.html",
		{
			"lead": doc.as_dict(),
			"tags": tags,
			"activities": activities,
			"generated_on": frappe.utils.now_datetime().strftime("%Y-%m-%d %H:%M"),
			"generated_by": frappe.session.user,
		},
	)
	content = get_pdf(html)
	filename = f"lead-{lead}-{frappe.generate_hash(length=6)}.pdf"
	file_doc = save_file(filename, content, "CRM Lead", lead, is_private=1)
	return {"file_url": file_doc.file_url, "lead": lead}


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


_DEMO_INTAKE = {
	"WhatsApp": [
		{"name": "Andi Putra", "phone": "+62-812-3456-7890", "body": "Halo saya tertarik dengan kredit modal kerja. Bisa info lebih lanjut?"},
		{"name": "Siti Rahayu", "phone": "+62-813-1111-2222", "body": "Tolong info bunga KPR Mei 2026"},
		{"name": "Budi Hartono", "phone": "+62-815-9876-5432", "body": "Saya butuh top-up 500jt"},
	],
	"Email": [
		{"from": "dewi@maju.co.id", "subject": "Inquiry: Working capital loan", "snippet": "Hi, we are PT Maju Bersama and would like to apply for..."},
		{"from": "agus@sukses.com", "subject": "Refinancing question", "snippet": "Can you compare your investment loan rates with..."},
	],
}


def _fill_from_lead(log, payload):
	lead_name = log.get("lead")
	if not lead_name or not frappe.db.exists("CRM Lead", lead_name):
		return {}
	lead = frappe.db.get_value(
		"CRM Lead", lead_name, ["lead_name", "first_name", "email", "mobile_no", "phone"], as_dict=True
	)
	if not lead:
		return {}
	return {
		"lead_name": lead.get("lead_name") or lead.get("first_name") or "",
		"email": lead.get("email") or "",
		"mobile_no": lead.get("mobile_no") or lead.get("phone") or "",
	}


@frappe.whitelist()
def get_lead_ops_intake(channel="WhatsApp", limit=50):
	messages = []
	if frappe.db.table_exists("CRM Lead Intake Log"):
		logs = frappe.get_all(
			"CRM Lead Intake Log",
			filters={"channel": channel, "status": ["!=", "Failed"]},
			fields=["name", "channel", "payload", "message", "creation", "status", "lead"],
			limit=limit,
			order_by="creation desc",
		)
		for log in logs:
			payload = _as_dict(log.payload)
			fill = _fill_from_lead(log, payload)
			msg = {"id": log.name, "channel": log.channel, "received_at": str(log.creation), "status": log.status}
			if channel == "WhatsApp":
				msg.update({
					"name": payload.get("lead_name") or payload.get("first_name") or fill.get("lead_name") or _("Unknown"),
					"phone": payload.get("mobile_no") or payload.get("phone") or fill.get("mobile_no") or "\u2014",
					"body": payload.get("message") or payload.get("body") or log.message or "",
				})
			elif channel == "Email":
				msg.update({
					"from": payload.get("sender") or payload.get("email") or fill.get("email") or fill.get("lead_name") or _("Unknown"),
					"subject": payload.get("subject") or _("Lead Inquiry"),
					"snippet": (payload.get("message") or payload.get("body") or log.message or "")[:200],
					"email": payload.get("email") or fill.get("email") or "",
				})
			messages.append(msg)
	if not messages:
		demo = _DEMO_INTAKE.get(channel, [])
		messages = [
			{
				"id": f"{channel.lower()}-demo-{i}",
				"demo": True,
				"received_at": frappe.utils.now_datetime(),
				**m,
			}
			for i, m in enumerate(demo)
		]
	return {"messages": messages}


@frappe.whitelist()
def create_lead_from_intake(channel="WhatsApp", data=None):
	data = _as_dict(data)
	data["capture_channel"] = channel
	data["source"] = channel
	if not data.get("lead_name") and not data.get("first_name") and not data.get("organization"):
		if data.get("body") or data.get("message"):
			data["lead_name"] = (data.get("body") or data.get("message") or "")[:80]
		elif channel == "Email" and data.get("sender"):
			data["lead_name"] = data.get("sender")
		else:
			data["lead_name"] = _("Intake Lead")
	return capture_lead(data, channel)


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


@frappe.whitelist()
def save_widget_config(fields=None, routing="round_robin"):
	frappe.cache.set_value("crm:lead_ops:widget_config", {"fields": fields or [], "routing": routing})
	return {"saved": True}


@frappe.whitelist()
def get_widget_config():
	return frappe.cache.get_value("crm:lead_ops:widget_config") or {}


@frappe.whitelist()
def save_nurture_sequence(sequence=None):
	if not sequence:
		return {"saved": False}
	sequences = frappe.cache.get_value("crm:lead_ops:nurture_sequences") or []
	updated = False
	for i, s in enumerate(sequences):
		if s.get("id") == sequence.get("id"):
			sequences[i] = sequence
			updated = True
			break
	if not updated:
		sequences.append(sequence)
	frappe.cache.set_value("crm:lead_ops:nurture_sequences", sequences)
	return {"saved": True, "sequences": sequences}


@frappe.whitelist()
def get_nurture_sequences():
	return frappe.cache.get_value("crm:lead_ops:nurture_sequences") or []


@frappe.whitelist()
def save_scoring_rules(rules=None):
	frappe.cache.set_value("crm:lead_ops:scoring_rules", rules or [])
	return {"saved": True}


@frappe.whitelist()
def export_lead_leads_csv(columns=None):
	_known = {
		"name": "name",
		"lead_name": "lead_name",
		"email": "email",
		"phone": "mobile_no",
		"company": "organization",
		"amount": "organization",
		"source": "source",
		"score": "score",
	}
	columns = columns or list(_known.keys())
	field_map = {k: v for k, v in _known.items() if k in columns}
	fields_to_query = list(dict.fromkeys(v for v in field_map.values()))
	safe = []
	for f in fields_to_query:
		if f == "name" or frappe.get_meta("CRM Lead").has_field(f):
			safe.append(f)
	if not safe:
		safe = ["name", "lead_name"]
	leads = frappe.get_all("CRM Lead", fields=safe, limit=500, order_by="creation desc")
	output = io.StringIO()
	header_map = {v: k for k, v in field_map.items()}
	headers = list(field_map.keys())
	writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
	writer.writeheader()
	for lead in leads:
		row = {}
		for col_key in headers:
			field = field_map[col_key]
			row[col_key] = lead.get(field, "")
		writer.writerow(row)
	return {"csv": output.getvalue(), "filename": "lead_pipeline.csv"}


@frappe.whitelist()
def generate_lead_pdf(lead_id):
	from frappe.utils.jinja import get_jenv

	lead = frappe.get_doc("CRM Lead", lead_id)
	html = get_jenv().from_string(
		"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Lead Briefing — {{ doc.lead_name }}</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: system-ui, -apple-system, sans-serif; padding: 48px; color: #1f2937; background: #fff; }
h1 { font-size: 28px; color: #0f766e; border-bottom: 3px solid #14b8a6; padding-bottom: 12px; margin-bottom: 32px; }
table { width: 100%; border-collapse: collapse; }
th { background: #f1f5f9; font-weight: 600; text-align: left; padding: 10px 16px; border: 1px solid #e2e8f0; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; color: #475569; }
td { padding: 10px 16px; border: 1px solid #e2e8f0; font-size: 15px; }
tr:nth-child(even) td { background: #f8fafc; }
.section { margin-top: 36px; }
.section h2 { font-size: 20px; color: #0f766e; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; margin-bottom: 16px; }
.section p { font-size: 14px; line-height: 1.7; color: #374151; }
.footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; text-align: center; }
</style>
</head>
<body>
<h1>Lead Briefing Report</h1>
<table>
<tr><th style="width:200px">Field</th><th>Value</th></tr>
<tr><td>Lead Name</td><td>{{ doc.lead_name or doc.first_name or "" }}</td></tr>
<tr><td>Organization</td><td>{{ doc.organization or "" }}</td></tr>
<tr><td>Email</td><td>{{ doc.email or "" }}</td></tr>
<tr><td>Phone</td><td>{{ doc.mobile_no or doc.phone or "" }}</td></tr>
<tr><td>Source</td><td>{{ doc.source or "" }}</td></tr>
<tr><td>Status</td><td>{{ doc.status or "" }}</td></tr>
<tr><td>Lead Owner</td><td>{{ doc.lead_owner or "" }}</td></tr>
<tr><td>Created</td><td>{{ doc.creation or "" }}</td></tr>
</table>
<div class="section">
<h2>Summary</h2>
<p>This briefing was generated for <strong>{{ doc.lead_name or doc.first_name or "this lead" }}</strong> on {{ frappe.utils.now_datetime().strftime("%d %B %Y %H:%M") }}.</p>
</div>
<div class="footer">CRM Lead Ops — Confidential</div>
</body>
</html>"""
	).render(doc=lead)
	return {"html": html, "filename": f"lead_briefing_{lead_id}.html"}
	return {"processed": True}


TAG_PALETTE = [
	"#0f766e", "#FF6600", "#2563eb", "#9333ea",
	"#dc2626", "#65a30d", "#0891b2", "#a16207",
]


@frappe.whitelist()
def list_tags():

return {"processed": True}


TAG_PALETTE = [
	"#0f766e", "#FF6600", "#2563eb", "#9333ea",
	"#dc2626", "#65a30d", "#0891b2", "#a16207",
]


@frappe.whitelist()
def list_tags():
	if not frappe.db.table_exists("CRM Lead Tag"):
		return {"tags": [], "palette": TAG_PALETTE}
	rows = frappe.get_all(
		"CRM Lead Tag",
		fields=["name", "tag", "color", "is_active", "description", "modified"],
		order_by="tag asc",
	)
	usage = {}
	last_used = {}
	if frappe.db.table_exists("CRM Lead Tag Link"):
		link_rows = frappe.db.sql(
			"""
			select tag, count(name) as count, max(creation) as last_used
			from `tabCRM Lead Tag Link`
			group by tag
			""",
			as_dict=True,
		)
		for r in link_rows:
			usage[r.tag] = cint(r.count)
			last_used[r.tag] = r.last_used
	for r in rows:
		r["usage"] = usage.get(r.tag, 0)
		r["last_used"] = last_used.get(r.tag)
	return {"tags": rows, "palette": TAG_PALETTE}


@frappe.whitelist()
def upsert_tag(payload):
	data = _as_dict(payload)
	tag = _normalize(data.get("tag"))
	if not tag:
		frappe.throw(_("Tag name is required."))
	color = _normalize(data.get("color")) or "#0f766e"
	description = _normalize(data.get("description"))
	is_active = 1 if data.get("is_active", 1) else 0
	if frappe.db.exists("CRM Lead Tag", tag):
		doc = frappe.get_doc("CRM Lead Tag", tag)
		doc.color = color
		doc.description = description
		doc.is_active = is_active
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({
			"doctype": "CRM Lead Tag",
			"tag": tag,
			"color": color,
			"description": description,
			"is_active": is_active,
		})
		doc.insert(ignore_permissions=True)
	return {"tag": doc.name, "color": doc.color}


@frappe.whitelist()
def delete_tag(tag, force=0):
	tag = _normalize(tag)
	if not tag or not frappe.db.exists("CRM Lead Tag", tag):
		return {"deleted": 0}
	usage = 0
	if frappe.db.table_exists("CRM Lead Tag Link"):
		usage = frappe.db.count("CRM Lead Tag Link", {"tag": tag})
	if usage and not cint(force):
		frappe.throw(_("Tag {0} is used by {1} leads. Use force=1 to cascade.").format(tag, usage))
	if usage:
		frappe.db.delete("CRM Lead Tag Link", {"tag": tag})
	frappe.delete_doc("CRM Lead Tag", tag, ignore_permissions=True, force=True)
	return {"deleted": 1, "cascaded": usage}


@frappe.whitelist()
def set_tags_for_lead(lead, tags):
	lead = _normalize(lead)
	if not lead or not frappe.db.exists("CRM Lead", lead):
		frappe.throw(_("Lead not found."))
	wanted = [_normalize(t) for t in _as_list(tags) if _normalize(t)]
	existing = []
	if frappe.db.table_exists("CRM Lead Tag Link"):
		existing = frappe.get_all(
			"CRM Lead Tag Link",
			filters={"lead": lead},
			fields=["name", "tag"],
		)
	existing_tags = {r.tag: r.name for r in existing}
	to_add = [t for t in wanted if t not in existing_tags]
	to_remove = [name for tag, name in existing_tags.items() if tag not in wanted]
	for tag in to_add:
		if not frappe.db.exists("CRM Lead Tag", tag):
			frappe.get_doc({
				"doctype": "CRM Lead Tag",
				"tag": tag,
				"color": TAG_PALETTE[0],
				"is_active": 1,
			}).insert(ignore_permissions=True, ignore_if_duplicate=True)
		color = frappe.db.get_value("CRM Lead Tag", tag, "color") or TAG_PALETTE[0]
		frappe.get_doc({
			"doctype": "CRM Lead Tag Link",
			"lead": lead,
			"tag": tag,
			"color": color,
		}).insert(ignore_permissions=True)
	for name in to_remove:
		frappe.delete_doc("CRM Lead Tag Link", name, ignore_permissions=True, force=True)
	return {"lead": lead, "added": to_add, "removed": list(existing_tags.keys() - set(wanted))}


def _campaign_range_cutoff(range):
	today = nowdate()
	return {
		"month": add_days(today, -30),
		"quarter": add_days(today, -90),
		"year": add_days(today, -365),
		"all": None,
	}.get(range, add_days(today, -30))


@frappe.whitelist()
def list_campaigns(range="month"):
	if not frappe.db.table_exists("CRM Lead Campaign"):
		return {"campaigns": [], "kpis": {"active": 0, "leads": 0, "avg_cpl": 0, "avg_conversion": 0}}
	cutoff = _campaign_range_cutoff(range)
	campaigns = frappe.get_all(
		"CRM Lead Campaign",
		fields=["name", "campaign_name", "status", "source", "start_date", "end_date", "budget", "utm_source", "utm_medium", "utm_campaign"],
		order_by="start_date desc",
		limit=500,
	)
	lead_filters = [["converted", "in", [0, 1]]]
	if cutoff:
		lead_filters.append(["creation", ">=", cutoff])
	leads = frappe.get_all(
		"CRM Lead",
		filters=lead_filters,
		fields=["name", "campaign", "converted", "source"],
		limit=10000,
	)
	by_campaign = {}
	for lead in leads:
		if not lead.campaign:
			continue
		b = by_campaign.setdefault(lead.campaign, {"leads": 0, "converted": 0, "sources": {}})
		b["leads"] += 1
		if lead.converted:
			b["converted"] += 1
		if lead.source:
			b["sources"][lead.source] = b["sources"].get(lead.source, 0) + 1

	out = []
	total_leads = 0
	total_conv_pct = 0.0
	conv_count = 0
	total_cpl = 0.0
	cpl_count = 0
	active_count = 0
	for c in campaigns:
		stats = by_campaign.get(c.name, {"leads": 0, "converted": 0, "sources": {}})
		leads_n = stats["leads"]
		conv_pct = round((stats["converted"] * 100.0) / leads_n, 1) if leads_n else 0
		cpl = round(flt(c.budget) / leads_n, 2) if leads_n and c.budget else 0
		top = sorted(stats["sources"].items(), key=lambda x: x[1], reverse=True)[:3]
		out.append({
			**c,
			"leads_count": leads_n,
			"converted_count": stats["converted"],
			"conversion_pct": conv_pct,
			"cost": flt(c.budget),
			"cost_per_lead": cpl,
			"top_sources": [{"source": s, "count": n} for s, n in top],
		})
		total_leads += leads_n
		if leads_n:
			total_conv_pct += conv_pct
			conv_count += 1
		if cpl:
			total_cpl += cpl
			cpl_count += 1
		if (c.status or "").lower() == "active":
			active_count += 1
	out.sort(key=lambda r: (r["leads_count"], r["converted_count"]), reverse=True)
	return {
		"campaigns": out,
		"kpis": {
			"active": active_count,
			"leads": total_leads,
			"avg_cpl": round(total_cpl / cpl_count, 2) if cpl_count else 0,
			"avg_conversion": round(total_conv_pct / conv_count, 1) if conv_count else 0,
		},
		"range": range,
	}


@frappe.whitelist()
def upsert_campaign(payload):
	data = _as_dict(payload)
	name = _normalize(data.get("name") or data.get("campaign_name"))
	if not name:
		frappe.throw(_("Campaign name is required."))
	values = {
		"campaign_name": name,
		"status": _normalize(data.get("status")) or "Draft",
		"source": _normalize(data.get("source")) or None,
		"start_date": data.get("start_date") or None,
		"end_date": data.get("end_date") or None,
		"budget": flt(data.get("budget")),
		"utm_source": _normalize(data.get("utm_source")),
		"utm_medium": _normalize(data.get("utm_medium")),
		"utm_campaign": _normalize(data.get("utm_campaign")),
		"description": data.get("description") or "",
	}
	if frappe.db.exists("CRM Lead Campaign", name):
		doc = frappe.get_doc("CRM Lead Campaign", name)
		for k, v in values.items():
			if k != "campaign_name":
				doc.set(k, v)
		doc.save(ignore_permissions=True)
	else:
		doc = frappe.get_doc({"doctype": "CRM Lead Campaign", **values})
		doc.insert(ignore_permissions=True)
	return {"name": doc.name}


@frappe.whitelist()
def get_campaign_detail(name, range="month"):
	if not frappe.db.exists("CRM Lead Campaign", name):
		frappe.throw(_("Campaign not found."))
	c = frappe.get_doc("CRM Lead Campaign", name)
	cutoff = _campaign_range_cutoff(range)
	lead_filters = [["campaign", "=", name]]
	if cutoff:
		lead_filters.append(["creation", ">=", cutoff])
	leads = frappe.get_all(
		"CRM Lead",
		filters=lead_filters,
		fields=["name", "creation", "converted", "source", "utm_source", "utm_medium", "utm_campaign"],
		order_by="creation asc",
		limit=10000,
	)
	by_day = {}
	utm_breakdown = {}
	source_counts = {}
	converted = 0
	for lead in leads:
		day = str(lead.creation)[:10]
		by_day.setdefault(day, {"date": day, "leads": 0, "converted": 0})
		by_day[day]["leads"] += 1
		if lead.converted:
			by_day[day]["converted"] += 1
			converted += 1
		key = "|".join([lead.utm_source or "—", lead.utm_medium or "—", lead.utm_campaign or "—"])
		utm = utm_breakdown.setdefault(key, {
			"utm_source": lead.utm_source or "—",
			"utm_medium": lead.utm_medium or "—",
			"utm_campaign": lead.utm_campaign or "—",
			"leads": 0,
			"converted": 0,
		})
		utm["leads"] += 1
		if lead.converted:
			utm["converted"] += 1
		if lead.source:
			source_counts[lead.source] = source_counts.get(lead.source, 0) + 1
	per_day = sorted(by_day.values(), key=lambda r: r["date"])
	leads_count = len(leads)
	cpl = round(flt(c.budget) / leads_count, 2) if leads_count and c.budget else 0
	return {
		"campaign": {
			"name": c.name,
			"campaign_name": c.campaign_name,
			"status": c.status,
			"source": c.source,
			"start_date": c.start_date,
			"end_date": c.end_date,
			"budget": flt(c.budget),
			"utm_source": c.utm_source,
			"utm_medium": c.utm_medium,
			"utm_campaign": c.utm_campaign,
			"description": c.description,
		},
		"kpis": {
			"leads": leads_count,
			"converted": converted,
			"conversion_pct": round((converted * 100.0) / leads_count, 1) if leads_count else 0,
			"cost_per_lead": cpl,
		},
		"per_day": per_day,
		"utm_breakdown": sorted(utm_breakdown.values(), key=lambda r: r["leads"], reverse=True),
		"top_sources": sorted(
			[{"source": s, "count": n} for s, n in source_counts.items()],
			key=lambda r: r["count"], reverse=True,
		)[:10],
	}


REFERRAL_FEE_DEFAULTS = {
	"Customer": {"amount": 250000, "pct": 0},
	"RM": {"amount": 0, "pct": 0.5},
	"Partner": {"amount": 500000, "pct": 1.0},
	"Other": {"amount": 100000, "pct": 0},
}


def _referral_fee_config(referrer_type):
	try:
		amount = frappe.db.get_single_value("CRM Settings", "referral_fee_amount")
		pct = frappe.db.get_single_value("CRM Settings", "referral_fee_pct")
		if amount or pct:
			return {"amount": flt(amount), "pct": flt(pct)}
	except Exception:
		pass
	return REFERRAL_FEE_DEFAULTS.get(referrer_type or "Other", REFERRAL_FEE_DEFAULTS["Other"])


def compute_referral_fee(doc, method=None):
	if not doc or not doc.get("referrer"):
		return
	if doc.get("referral_fee"):
		return
	cfg = _referral_fee_config(doc.get("referrer_type"))
	flat = flt(cfg.get("amount"))
	pct = flt(cfg.get("pct"))
	expected_value = flt(doc.get("expected_deal_value") or 0)
	fee = flat + (expected_value * pct / 100.0)
	doc.referral_fee = round(fee, 2)


def notify_referrer(doc, method=None):
	if not doc or not doc.get("referrer") or not doc.get("referrer_type"):
		return
	if doc.referrer_type != "RM":
		return
	user = doc.referrer if frappe.db.exists("User", doc.referrer) else None
	if not user:
		return
	try:
		_notify_lead_user(
			user,
			doc.name,
			_("Referral received"),
			_("A lead you referred ({0}) has been captured.").format(doc.lead_name or doc.name),
		)
	except Exception:
		pass


def auto_link_campaign(doc, method=None):
	if not doc or not doc.get("utm_campaign") or doc.get("campaign"):
		return
	utm = _normalize(doc.utm_campaign)
	if not utm:
		return
	if not frappe.db.table_exists("CRM Lead Campaign"):
		return
	match = frappe.db.get_value(
		"CRM Lead Campaign",
		filters={"utm_campaign": utm},
		fieldname="name",
	)
	if not match:
		match = frappe.db.get_value("CRM Lead Campaign", utm, "name")
	if match:
		doc.campaign = match


@frappe.whitelist()
def list_referrer_leaderboard(range="month", type="all"):
	if not frappe.db.table_exists("CRM Lead"):
		return {"rows": [], "range": range, "type": type}
	today = nowdate()
	cutoffs = {
		"month": add_days(today, -30),
		"quarter": add_days(today, -90),
		"year": add_days(today, -365),
		"all": None,
	}
	cutoff = cutoffs.get(range, cutoffs["month"])
	filters = [["referrer", "!=", ""]]
	if cutoff:
		filters.append(["creation", ">=", cutoff])
	if type and type != "all":
		filters.append(["referrer_type", "=", type])
	rows = frappe.get_all(
		"CRM Lead",
		filters=filters,
		fields=["referrer", "referrer_type", "converted", "referral_fee"],
		limit=5000,
	)
	agg = {}
	for r in rows:
		key = (r.referrer_type or "Other", r.referrer or "(unknown)")
		bucket = agg.setdefault(key, {
			"referrer": r.referrer,
			"referrer_type": r.referrer_type or "Other",
			"leads_count": 0,
			"converted_count": 0,
			"total_referral_fee": 0.0,
		})
		bucket["leads_count"] += 1
		bucket["converted_count"] += 1 if r.converted else 0
		bucket["total_referral_fee"] += flt(r.referral_fee)
	out = list(agg.values())
	for b in out:
		b["conversion_pct"] = round((b["converted_count"] * 100.0) / b["leads_count"], 1) if b["leads_count"] else 0
	out.sort(key=lambda b: (b["converted_count"], b["leads_count"]), reverse=True)
	for i, b in enumerate(out, 1):
		b["rank"] = i
	return {"rows": out, "range": range, "type": type}


@frappe.whitelist()
def snapshot_lead_aging():
	if not frappe.db.table_exists("CRM Lead") or not frappe.db.table_exists("CRM Lead Aging Snapshot"):
		return {"snapshot": None}
	meta = frappe.get_meta("CRM Lead")
	aging_field = "last_activity_on" if meta.has_field("last_activity_on") else "modified"
	leads = frappe.get_all(
		"CRM Lead",
		filters=[["converted", "=", 0]],
		fields=[aging_field + " as last_activity"],
		limit=10000,
	)
	today = get_datetime()
	bands = {"fresh": 0, "warm": 0, "stale": 0, "frozen": 0}
	for lead in leads:
		last = lead.get("last_activity")
		if not last:
			continue
		days = max(0, (today - get_datetime(last)).days)
		bands[_aging_band(days)] += 1
	snapshot_date = nowdate()
	existing = frappe.db.get_value("CRM Lead Aging Snapshot", {"snapshot_date": snapshot_date}, "name")
	values = {
		"snapshot_date": snapshot_date,
		"fresh": bands["fresh"],
		"warm": bands["warm"],
		"stale": bands["stale"],
		"frozen": bands["frozen"],
		"total": sum(bands.values()),
	}
	if existing:
		doc = frappe.get_doc("CRM Lead Aging Snapshot", existing)
		for k, v in values.items():
			if k != "snapshot_date":
				doc.set(k, v)
		doc.save(ignore_permissions=True)
		name = doc.name
	else:
		doc = frappe.get_doc({"doctype": "CRM Lead Aging Snapshot", **values})
		doc.insert(ignore_permissions=True)
		name = doc.name
	return {"snapshot": name, **values}


def _aging_band(days):
	if days <= 7:
		return "fresh"
	if days <= 14:
		return "warm"
	if days <= 30:
		return "stale"
	return "frozen"


@frappe.whitelist()
def get_aging_report(range="30d", owner=None, source=None):
	if not frappe.db.table_exists("CRM Lead"):
		return {
			"bands_count": {"fresh": 0, "warm": 0, "stale": 0, "frozen": 0},
			"by_owner": [],
			"by_source": [],
			"trend": [],
			"top_stale": [],
		}
	meta = frappe.get_meta("CRM Lead")
	aging_field = "last_activity_on" if meta.has_field("last_activity_on") else "modified"
	days_back = {"7d": 7, "30d": 30, "90d": 90}.get(range, 30)
	cutoff = add_days(nowdate(), -days_back)
	filters = [["converted", "=", 0], [aging_field, ">=", cutoff]]
	if owner:
		filters.append(["lead_owner", "=", owner])
	if source:
		filters.append(["source", "=", source])
	leads = frappe.get_all(
		"CRM Lead",
		filters=filters,
		fields=["name", "lead_name", "lead_owner", "source", "lead_score", "lead_score_band", aging_field + " as last_activity"],
		limit=2000,
	)
	today = get_datetime()
	bands = {"fresh": 0, "warm": 0, "stale": 0, "frozen": 0}
	owner_map = {}
	source_map = {}
	enriched = []
	for lead in leads:
		last = lead.get("last_activity")
		if not last:
			continue
		days = max(0, (today - get_datetime(last)).days)
		band = _aging_band(days)
		bands[band] += 1
		owner_key = lead.lead_owner or "(unassigned)"
		owner_map.setdefault(owner_key, {"owner": owner_key, "fresh": 0, "warm": 0, "stale": 0, "frozen": 0})[band] += 1
		source_key = lead.source or "(unknown)"
		source_map.setdefault(source_key, {"source": source_key, "fresh": 0, "warm": 0, "stale": 0, "frozen": 0})[band] += 1
		enriched.append({
			"name": lead.name,
			"lead_name": lead.lead_name,
			"lead_owner": lead.lead_owner,
			"source": lead.source,
			"score": lead.lead_score or 0,
			"score_band": lead.lead_score_band,
			"days_inactive": days,
			"band": band,
		})
	by_owner = sorted(owner_map.values(), key=lambda r: r["frozen"] + r["stale"], reverse=True)[:20]
	by_source = sorted(source_map.values(), key=lambda r: r["frozen"] + r["stale"], reverse=True)[:20]
	top_stale = sorted(enriched, key=lambda r: r["days_inactive"], reverse=True)[:20]
	trend = []
	if frappe.db.table_exists("CRM Lead Aging Snapshot"):
		rows = frappe.get_all(
			"CRM Lead Aging Snapshot",
			filters=[["snapshot_date", ">=", cutoff]],
			fields=["snapshot_date as date", "fresh", "warm", "stale", "frozen"],
			order_by="snapshot_date asc",
			limit=days_back + 1,
		)
		trend = rows
	if not trend:
		trend = [{
			"date": nowdate(),
			"fresh": bands["fresh"],
			"warm": bands["warm"],
			"stale": bands["stale"],
			"frozen": bands["frozen"],
		}]
	return {
		"bands_count": bands,
		"by_owner": by_owner,
		"by_source": by_source,
		"trend": trend,
		"top_stale": top_stale,
	}


SCORING_OPERATORS = ["is set", "equals", "contains", "greater than", "less than"]
SCORING_FIELDS = [
	"email", "mobile_no", "organization", "job_title", "source", "campaign",
	"annual_revenue", "npwp", "lead_score", "industry", "territory", "status",
	"capture_channel", "referrer_type", "expected_deal_value",
]


@frappe.whitelist()
def list_scoring_models():
	if not frappe.db.table_exists("CRM Lead Scoring Model"):
		return {"models": [], "fields": SCORING_FIELDS, "operators": SCORING_OPERATORS}
	models = frappe.get_all(
		"CRM Lead Scoring Model",
		fields=["name", "model_name", "version", "is_active", "description", "trained_on", "modified"],
		order_by="modified desc",
	)
	for m in models:
		try:
			doc = frappe.get_doc("CRM Lead Scoring Model", m.name)
			m["rule_count"] = len(doc.rules or [])
		except Exception:
			m["rule_count"] = 0
	return {"models": models, "fields": SCORING_FIELDS, "operators": SCORING_OPERATORS}


@frappe.whitelist()
def get_scoring_model(name):
	doc = frappe.get_doc("CRM Lead Scoring Model", name)
	rules = []
	for rule in doc.rules or []:
		rules.append({
			"name": rule.name,
			"fieldname": rule.fieldname,
			"operator": rule.operator,
			"value": rule.value,
			"weight": rule.weight,
			"description": rule.description,
		})
	return {
		"name": doc.name,
		"model_name": doc.model_name,
		"version": doc.version,
		"is_active": bool(doc.is_active),
		"description": doc.description,
		"trained_on": doc.trained_on,
		"rules": rules,
	}


@frappe.whitelist()
def clone_scoring_model_version(model):
	src = frappe.get_doc("CRM Lead Scoring Model", model)
	new_version = cint(src.version) + 1
	new_name = f"{src.model_name} v{new_version}"
	while frappe.db.exists("CRM Lead Scoring Model", new_name):
		new_version += 1
		new_name = f"{src.model_name} v{new_version}"
	clone = frappe.new_doc("CRM Lead Scoring Model")
	clone.model_name = new_name
	clone.version = new_version
	clone.is_active = 0
	clone.description = src.description
	for rule in src.rules or []:
		clone.append("rules", {
			"fieldname": rule.fieldname,
			"operator": rule.operator,
			"value": rule.value,
			"weight": rule.weight,
			"description": rule.description,
		})
	clone.insert(ignore_permissions=True)
	return {"name": clone.name, "version": new_version}


@frappe.whitelist()
def activate_scoring_model(model):
	if not frappe.db.exists("CRM Lead Scoring Model", model):
		frappe.throw(_("Model not found."))
	frappe.db.sql("update `tabCRM Lead Scoring Model` set is_active=0")
	frappe.db.set_value("CRM Lead Scoring Model", model, "is_active", 1)
	frappe.db.commit()
	return {"active": model}


@frappe.whitelist()
def upsert_scoring_rule(model, payload):
	data = _as_dict(payload)
	doc = frappe.get_doc("CRM Lead Scoring Model", model)
	rule_name = _normalize(data.get("name"))
	row = None
	if rule_name:
		for r in doc.rules:
			if r.name == rule_name:
				row = r
				break
	if row is None:
		row = doc.append("rules", {})
	row.fieldname = _normalize(data.get("fieldname"))
	row.operator = _normalize(data.get("operator")) or "is set"
	row.value = _normalize(data.get("value"))
	row.weight = cint(data.get("weight") or 10)
	row.description = data.get("description") or ""
	doc.save(ignore_permissions=True)
	return {"model": model, "rule": row.name}


@frappe.whitelist()
def delete_scoring_rule(model, rule):
	doc = frappe.get_doc("CRM Lead Scoring Model", model)
	doc.rules = [r for r in doc.rules if r.name != rule]
	doc.save(ignore_permissions=True)
	return {"deleted": rule}


def _sample_lead(name=None):
	if name and frappe.db.exists("CRM Lead", name):
		return frappe.get_doc("CRM Lead", name)
	pick = frappe.db.get_value("CRM Lead", {}, "name", order_by="modified desc")
	if pick:
		return frappe.get_doc("CRM Lead", pick)
	return None


@frappe.whitelist()
def test_scoring_rule(model, rule, sample_lead=None):
	doc = frappe.get_doc("CRM Lead Scoring Model", model)
	row = next((r for r in doc.rules if r.name == rule), None)
	if not row:
		frappe.throw(_("Rule not found."))
	sample = _sample_lead(sample_lead)
	if not sample:
		return {"matched": False, "contribution": 0, "sample": None}
	matched = _evaluate_rule(sample, row)
	return {
		"matched": matched,
		"contribution": cint(row.weight) if matched else 0,
		"sample": sample.name,
	}


@frappe.whitelist()
def test_scoring_model(model, sample_lead=None):
	doc = frappe.get_doc("CRM Lead Scoring Model", model)
	sample = _sample_lead(sample_lead)
	if not sample:
		return {"total": 0, "band": "Cold", "breakdown": [], "sample": None}
	total = 0
	breakdown = []
	for row in doc.rules or []:
		matched = _evaluate_rule(sample, row)
		contrib = cint(row.weight) if matched else 0
		total += contrib
		breakdown.append({
			"rule": row.name,
			"fieldname": row.fieldname,
			"operator": row.operator,
			"value": row.value,
			"weight": cint(row.weight),
			"matched": matched,
			"contribution": contrib,
		})
	total = min(total, 100)
	return {
		"total": total,
		"band": _score_band(total),
		"breakdown": breakdown,
		"sample": sample.name,
	}


@frappe.whitelist()
def list_quality_models():
	if not frappe.db.table_exists("CRM Lead Quality Model"):
		return {"models": []}
	models = frappe.get_all(
		"CRM Lead Quality Model",
		fields=["name", "model_name", "version", "is_active", "trained_on", "sample_size", "baseline_accuracy", "baseline_auc"],
		order_by="version desc",
		limit=10,
	)
	return {"models": models}


@frappe.whitelist()
def activate_quality_model(model):
	if not frappe.db.exists("CRM Lead Quality Model", model):
		frappe.throw(_("Model not found."))
	frappe.db.sql("update `tabCRM Lead Quality Model` set is_active=0")
	frappe.db.set_value("CRM Lead Quality Model", model, "is_active", 1)
	frappe.db.commit()
	return {"active": model}


WEBFORM_DEFAULT_FIELDS = [
	{"fieldname": "first_name", "label": "First Name", "required": 1},
	{"fieldname": "last_name", "label": "Last Name", "required": 0},
	{"fieldname": "email", "label": "Email", "required": 1},
	{"fieldname": "mobile_no", "label": "Mobile Number", "required": 1},
	{"fieldname": "organization", "label": "Organization", "required": 0},
	{"fieldname": "job_title", "label": "Job Title", "required": 0},
	{"fieldname": "annual_revenue", "label": "Annual Revenue", "required": 0},
	{"fieldname": "npwp", "label": "NPWP", "required": 0},
]


@frappe.whitelist(allow_guest=True)
def get_webform_config(form):
	if not frappe.db.table_exists("CRM Lead Web Form"):
		frappe.throw(_("Web form not configured."))
	doc = frappe.get_doc("CRM Lead Web Form", form)
	if not doc.active:
		frappe.throw(_("This form is not active."))
	fields = doc.fields_json
	try:
		fields = json.loads(fields) if fields else None
	except Exception:
		fields = None
	if not fields:
		fields = WEBFORM_DEFAULT_FIELDS
	return {
		"form_name": doc.form_name,
		"slug": doc.slug,
		"fields": fields,
		"captcha_enabled": bool(doc.captcha_enabled),
		"redirect_url": doc.redirect_url or "/thank-you",
	}


@frappe.whitelist(allow_guest=True)
def submit_webform(form, payload, utm=None):
	utm = _as_dict(utm)
	_rate_limit_webform()
	config = get_webform_config(form)
	data = _as_dict(payload)
	data.update({
		"utm_source": utm.get("utm_source") or data.get("utm_source"),
		"utm_medium": utm.get("utm_medium") or data.get("utm_medium"),
		"utm_campaign": utm.get("utm_campaign") or data.get("utm_campaign"),
	})
	return capture_lead(data=data, channel="WebForm")


def _rate_limit_webform():
	key = f"webform_submit:{frappe.local.request_ip or 'unknown'}"
	count = cint(frappe.cache.get_value(key) or 0)
	if count >= 10:
		frappe.throw(_("Rate limit exceeded. Please try again later."), frappe.RateLimitExceededError)
	frappe.cache.set_value(key, count + 1, expires_in_sec=60)


@frappe.whitelist()
def list_webforms():
	if not frappe.db.table_exists("CRM Lead Web Form"):
		return {"forms": []}
	forms = frappe.get_all(
		"CRM Lead Web Form",
		fields=["name", "form_name", "slug", "active", "captcha_enabled", "redirect_url", "embed_token"],
		order_by="modified desc",
	)
	return {"forms": forms}


@frappe.whitelist()
def upsert_webform(payload):
	data = _as_dict(payload)
	slug = _normalize(data.get("slug"))
	name = _normalize(data.get("name"))
	if not slug:
		frappe.throw(_("Slug is required."))
	if not name and frappe.db.exists("CRM Lead Web Form", slug):
		frappe.throw(_("Slug already exists."))
	if name:
		doc = frappe.get_doc("CRM Lead Web Form", name)
	else:
		doc = frappe.new_doc("CRM Lead Web Form")
		doc.slug = slug
		doc.embed_token = frappe.generate_hash(length=16)
	doc.form_name = data.get("form_name") or doc.form_name or slug
	doc.active = cint(data.get("active", 1))
	doc.captcha_enabled = cint(data.get("captcha_enabled", 0))
	doc.redirect_url = data.get("redirect_url") or doc.redirect_url or ""
	if data.get("fields_json") is not None:
		doc.fields_json = data.get("fields_json") if isinstance(data.get("fields_json"), str) else json.dumps(data.get("fields_json"))
	doc.save(ignore_permissions=True)
	return {"name": doc.name, "slug": doc.slug, "embed_token": doc.embed_token}
