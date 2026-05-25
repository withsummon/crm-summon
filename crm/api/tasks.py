"""Tasks & SLA workbench API.

Mirrors the helper pattern of `crm/api/committee.py`: small whitelisted
endpoints, server-resolved current user, idempotent transitions, and a
single `_compute_sla` helper that derives the live SLA state from stored
timestamps. We compute SLA state on read (and on transition) rather than
running a background job — this keeps the demo self-contained.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.utils import (
	add_to_date,
	flt,
	get_datetime,
	getdate,
	now_datetime,
	time_diff_in_seconds,
)


# ---------- helpers ----------

OPEN_STATUSES = ("Backlog", "Todo", "In Progress", "Blocked")
ACTIVE_STATUSES = ("Todo", "In Progress")
CLOSED_STATUSES = ("Done", "Canceled")
DEFAULT_SLA_MINUTES = {"Critical": 240, "High": 1440, "Medium": 4320, "Low": 10080}


def _doctype_ready(doctype):
	return frappe.db.table_exists(doctype)


def _now():
	return now_datetime()


def _to_dt(value):
	if not value:
		return None
	if isinstance(value, datetime):
		return value
	return get_datetime(value)


def _user_full_name(user):
	if not user:
		return ""
	return frappe.db.get_value("User", user, "full_name") or user


def _user_brief(user):
	if not user:
		return None
	row = frappe.db.get_value("User", user, ["name", "full_name", "user_image"], as_dict=True)
	if not row:
		return {"name": user, "full_name": user, "user_image": None}
	return row


def _resolve_type_sla(task_type, priority):
	"""Return SLA minutes for a (type, priority) pair.

	Looks up the type's `sla_matrix_json` first, falls back to the default
	priority ladder if no type or no entry.
	"""
	if task_type and _doctype_ready("CRM Task Type"):
		raw = frappe.db.get_value("CRM Task Type", task_type, "sla_matrix_json")
		if raw:
			try:
				matrix = json.loads(raw)
				if priority and matrix.get(priority):
					return int(matrix[priority])
			except Exception:
				pass
	return DEFAULT_SLA_MINUTES.get(priority or "Medium", DEFAULT_SLA_MINUTES["Medium"])


def _compute_sla(task):
	"""Compute the current SLA state for an in-memory task dict.

	Sets/updates: sla_minutes, sla_due_at, sla_state.
	Does not persist — caller decides.
	"""
	status = task.get("status")
	if status in CLOSED_STATUSES:
		task["sla_state"] = "Completed"
		return task

	created = _to_dt(task.get("started_at") or task.get("creation"))
	if not created:
		task["sla_state"] = "OK"
		return task

	minutes = int(task.get("sla_minutes") or 0)
	if not minutes:
		minutes = _resolve_type_sla(task.get("task_type"), task.get("priority"))
		task["sla_minutes"] = minutes

	paused = int(task.get("sla_paused_minutes") or 0)
	due = task.get("sla_due_at")
	if not due:
		due = add_to_date(created, minutes=minutes + paused)
		task["sla_due_at"] = due
	due_dt = _to_dt(due)

	if status == "Blocked":
		task["sla_state"] = "Paused"
		return task

	now = _now()
	remaining_seconds = time_diff_in_seconds(due_dt, now)
	total_seconds = minutes * 60.0 or 1.0
	consumed_pct = max(0.0, 1.0 - (remaining_seconds / total_seconds))

	if remaining_seconds <= 0:
		task["sla_state"] = "Breached"
	elif consumed_pct >= 0.8:
		task["sla_state"] = "Approaching"
	else:
		task["sla_state"] = "OK"
	task["sla_remaining_seconds"] = max(0, int(remaining_seconds))
	task["sla_consumed_pct"] = round(consumed_pct * 100, 1)
	return task


def _sla_persist(task_doc):
	"""Compute SLA fields and persist them with db_set."""
	snap = task_doc.as_dict()
	_compute_sla(snap)
	if snap.get("sla_minutes") != task_doc.sla_minutes:
		task_doc.db_set("sla_minutes", snap["sla_minutes"], update_modified=False)
	if snap.get("sla_due_at") and snap.get("sla_due_at") != task_doc.sla_due_at:
		task_doc.db_set("sla_due_at", snap["sla_due_at"], update_modified=False)
	if snap.get("sla_state") != task_doc.sla_state:
		task_doc.db_set("sla_state", snap["sla_state"], update_modified=False)


def _reference_label(doctype):
	if not doctype:
		return None
	return {
		"CRM Lead": "Lead",
		"CRM Deal": "Deal",
		"CRM Credit Application": "Credit",
		"CRM Committee Item": "Committee",
		"CRM Customer 360": "Customer",
	}.get(doctype, doctype)


def _list_assignees(task_name):
	if not _doctype_ready("CRM Task Assignee"):
		return []
	rows = frappe.get_all(
		"CRM Task Assignee",
		filters={"parent": task_name, "parenttype": "CRM Task"},
		fields=["user", "user_name", "role", "primary"],
		order_by="idx asc",
	)
	for r in rows:
		brief = _user_brief(r["user"]) or {}
		r["full_name"] = r.get("user_name") or brief.get("full_name") or r["user"]
		r["user_image"] = brief.get("user_image")
	return rows


def _task_row(task, include_extras=True):
	row = dict(task)
	_compute_sla(row)
	row["reference_label"] = _reference_label(task.get("reference_doctype"))
	if include_extras:
		row["assignees"] = _list_assignees(task["name"])
		if not row["assignees"] and task.get("assigned_to"):
			brief = _user_brief(task["assigned_to"]) or {}
			row["assignees"] = [{
				"user": task["assigned_to"],
				"full_name": brief.get("full_name") or task["assigned_to"],
				"user_image": brief.get("user_image"),
				"role": "Assignee",
				"primary": 1,
			}]
	return row


def _task_fields():
	return [
		"name",
		"title",
		"priority",
		"status",
		"task_type",
		"assigned_to",
		"due_date",
		"start_date",
		"started_at",
		"completed_at",
		"blocked_at",
		"blocked_reason",
		"sla_minutes",
		"sla_due_at",
		"sla_paused_at",
		"sla_paused_minutes",
		"sla_state",
		"reference_doctype",
		"reference_docname",
		"parent_task",
		"template_used",
		"time_logged_minutes",
		"is_billable",
		"is_milestone",
		"creation",
		"modified",
		"owner",
	]


# ---------- whitelisted endpoints ----------


@frappe.whitelist()
def get_context():
	"""Inbox header context: user, KPIs, list of team users for filters."""
	user = frappe.session.user
	tasks = frappe.get_all(
		"CRM Task",
		filters=[["status", "in", list(OPEN_STATUSES)]],
		or_filters=[["assigned_to", "=", user], ["owner", "=", user]],
		fields=_task_fields(),
		limit_page_length=500,
	)
	today = getdate()
	week_end = today + timedelta(days=7)
	counters = {"open": 0, "due_today": 0, "overdue": 0, "blocked": 0, "this_week": 0}
	for t in tasks:
		counters["open"] += 1
		if t["status"] == "Blocked":
			counters["blocked"] += 1
		if t["due_date"]:
			due = getdate(t["due_date"])
			if due == today:
				counters["due_today"] += 1
			elif due < today:
				counters["overdue"] += 1
			if today <= due <= week_end:
				counters["this_week"] += 1
	team_users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User"},
		fields=["name", "full_name", "user_image"],
		limit_page_length=50,
	)
	types = []
	if _doctype_ready("CRM Task Type"):
		types = frappe.get_all(
			"CRM Task Type",
			filters={"active": 1},
			fields=["name", "type_name", "color"],
			order_by="type_name asc",
		)
	return {
		"user": user,
		"user_full_name": _user_full_name(user),
		"user_image": frappe.db.get_value("User", user, "user_image"),
		"counters": counters,
		"team_users": team_users,
		"task_types": types,
	}


@frappe.whitelist()
def get_inbox(scope="me", task_type=None, priority=None, status=None, search=None, sort_by="sla"):
	"""List inbox tasks for the current user (or wider scope)."""
	user = frappe.session.user
	filters = []
	or_filters = []
	if scope == "me":
		or_filters = [["assigned_to", "=", user], ["owner", "=", user]]
	elif scope == "team":
		pass  # admin sees all
	elif scope == "following":
		or_filters = [["owner", "=", user]]
	if task_type:
		filters.append(["task_type", "=", task_type])
	if priority:
		filters.append(["priority", "=", priority])
	if status:
		filters.append(["status", "=", status])
	else:
		filters.append(["status", "in", list(OPEN_STATUSES)])
	if search:
		filters.append(["title", "like", f"%{search}%"])

	tasks = frappe.get_all(
		"CRM Task",
		filters=filters,
		or_filters=or_filters or None,
		fields=_task_fields(),
		order_by="modified desc",
		limit_page_length=300,
	)
	rows = [_task_row(t) for t in tasks]
	if sort_by == "due":
		rows.sort(key=lambda r: (r["due_date"] or "9999-12-31"))
	elif sort_by == "priority":
		order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
		rows.sort(key=lambda r: order.get(r.get("priority"), 9))
	elif sort_by == "updated":
		rows.sort(key=lambda r: r.get("modified") or "", reverse=True)
	else:
		# SLA urgency: breached > approaching > ok, then by remaining seconds asc
		state_order = {"Breached": 0, "Approaching": 1, "Paused": 2, "OK": 3, "Completed": 4}
		rows.sort(key=lambda r: (state_order.get(r.get("sla_state"), 9), r.get("sla_remaining_seconds", 1_000_000_000)))
	return rows


@frappe.whitelist()
def get_task(name):
	"""Full task detail for the drawer."""
	doc = frappe.get_doc("CRM Task", name)
	row = _task_row(doc.as_dict())
	checklist = []
	if _doctype_ready("CRM Task Checklist Item"):
		checklist = frappe.get_all(
			"CRM Task Checklist Item",
			filters={"parent": name, "parenttype": "CRM Task"},
			fields=["name", "label", "done", "done_at", "done_by", "position", "idx"],
			order_by="position asc, idx asc",
		)
	deps_out = []
	deps_in = []
	if _doctype_ready("CRM Task Dependency"):
		for d in frappe.get_all(
			"CRM Task Dependency",
			filters={"parent": name, "parenttype": "CRM Task"},
			fields=["name", "depends_on", "kind"],
		):
			t = frappe.db.get_value(
				"CRM Task", d["depends_on"], ["name", "title", "status", "priority"], as_dict=True
			)
			if not t:
				continue
			(deps_out if d["kind"] == "blocks" else deps_in).append({**d, "task": t})
	time_logs = []
	if _doctype_ready("CRM Task Time Log"):
		time_logs = frappe.get_all(
			"CRM Task Time Log",
			filters={"task": name},
			fields=["name", "user", "started_at", "ended_at", "duration_minutes", "billable", "note"],
			order_by="started_at desc",
		)
		for tl in time_logs:
			brief = _user_brief(tl["user"]) or {}
			tl["user_name"] = brief.get("full_name") or tl["user"]
	escalations = []
	if _doctype_ready("CRM Task Escalation Event"):
		escalations = frappe.get_all(
			"CRM Task Escalation Event",
			filters={"task": name},
			fields=["name", "level", "fired_at", "action", "recipient_user", "acknowledged_at", "acknowledged_by", "rule"],
			order_by="fired_at desc",
		)
	comments = []
	if _doctype_ready("Comment"):
		comments = frappe.get_all(
			"Comment",
			filters={"reference_doctype": "CRM Task", "reference_name": name, "comment_type": "Comment"},
			fields=["name", "content", "comment_email", "comment_by", "creation"],
			order_by="creation asc",
		)
	return {
		"task": row,
		"checklist": checklist,
		"dependencies": {"blocks": deps_out, "blocked_by": deps_in},
		"time_logs": time_logs,
		"escalations": escalations,
		"comments": comments,
	}


@frappe.whitelist()
def create_task(payload):
	"""Quick-create with sensible defaults; returns the created task name."""
	if isinstance(payload, str):
		payload = json.loads(payload)
	doc = frappe.new_doc("CRM Task")
	doc.title = payload.get("title") or _("Untitled task")
	doc.priority = payload.get("priority") or "Medium"
	doc.status = payload.get("status") or "Todo"
	doc.task_type = payload.get("task_type")
	doc.assigned_to = payload.get("assigned_to") or frappe.session.user
	if payload.get("due_date"):
		doc.due_date = payload["due_date"]
	doc.description = payload.get("description")
	doc.reference_doctype = payload.get("reference_doctype")
	doc.reference_docname = payload.get("reference_docname")
	doc.parent_task = payload.get("parent_task")
	doc.started_at = _now() if doc.status == "In Progress" else None
	doc.insert(ignore_permissions=True)
	# Mirror primary into assignees table
	if doc.assigned_to:
		_replace_assignees(doc, [doc.assigned_to])
	_sla_persist(doc)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def transition(task, new_status, blocked_reason=None):
	"""Single entry point for status change; handles SLA + lifecycle stamps."""
	doc = frappe.get_doc("CRM Task", task)
	if new_status not in ("Backlog", "Todo", "In Progress", "Blocked", "Done", "Canceled"):
		frappe.throw(_("Invalid status"))
	now = _now()
	old = doc.status
	if new_status == "Blocked":
		if not (blocked_reason or "").strip():
			frappe.throw(_("A blocked reason is required."))
		doc.blocked_reason = blocked_reason
		doc.blocked_at = now
		doc.sla_paused_at = now
	if old == "Blocked" and new_status != "Blocked" and doc.sla_paused_at:
		paused_min = max(0, int(time_diff_in_seconds(now, _to_dt(doc.sla_paused_at)) / 60))
		doc.sla_paused_minutes = int(doc.sla_paused_minutes or 0) + paused_min
		if doc.sla_due_at:
			doc.sla_due_at = add_to_date(_to_dt(doc.sla_due_at), minutes=paused_min)
		doc.sla_paused_at = None
		doc.blocked_reason = None
	if new_status == "In Progress" and not doc.started_at:
		doc.started_at = now
	if new_status == "Done":
		doc.completed_at = now
		doc.sla_state = "Completed"
	doc.status = new_status
	doc.save(ignore_permissions=True)
	_sla_persist(doc)
	frappe.db.commit()
	return get_task(task)


@frappe.whitelist()
def bulk_complete(task_ids):
	if isinstance(task_ids, str):
		task_ids = json.loads(task_ids)
	for tid in task_ids:
		try:
			transition(tid, "Done")
		except Exception:
			frappe.log_error(frappe.get_traceback(), "bulk_complete failure")
	return len(task_ids)


def _replace_assignees(doc, users):
	doc.set("assignees", [])
	for i, u in enumerate(users):
		doc.append("assignees", {
			"user": u,
			"user_name": _user_full_name(u),
			"role": "Assignee",
			"primary": 1 if i == 0 else 0,
		})
	if users:
		doc.assigned_to = users[0]
	doc.save(ignore_permissions=True)


@frappe.whitelist()
def set_assignees(task, users):
	if isinstance(users, str):
		users = json.loads(users)
	doc = frappe.get_doc("CRM Task", task)
	_replace_assignees(doc, users)
	frappe.db.commit()
	return get_task(task)


@frappe.whitelist()
def upsert_checklist(task, items):
	if isinstance(items, str):
		items = json.loads(items)
	doc = frappe.get_doc("CRM Task", task)
	doc.set("checklist", [])
	for i, it in enumerate(items):
		doc.append("checklist", {
			"label": it.get("label"),
			"done": 1 if it.get("done") else 0,
			"done_at": it.get("done_at") or (_now() if it.get("done") else None),
			"done_by": it.get("done_by") or (frappe.session.user if it.get("done") else None),
			"position": it.get("position", i),
		})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return get_task(task)


@frappe.whitelist()
def add_dependency(task, depends_on, kind="blocked_by"):
	doc = frappe.get_doc("CRM Task", task)
	if depends_on == task:
		frappe.throw(_("A task cannot depend on itself."))
	doc.append("depends_on", {"depends_on": depends_on, "kind": kind})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return get_task(task)


@frappe.whitelist()
def remove_dependency(task, row_name):
	doc = frappe.get_doc("CRM Task", task)
	doc.depends_on = [d for d in doc.depends_on if d.name != row_name]
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return get_task(task)


@frappe.whitelist()
def start_timer(task):
	"""Start a timer for the current user. Stops any other open timer for them."""
	if not _doctype_ready("CRM Task Time Log"):
		frappe.throw(_("Time logs unavailable"))
	user = frappe.session.user
	open_logs = frappe.get_all(
		"CRM Task Time Log",
		filters={"user": user, "ended_at": ["is", "not set"]},
		fields=["name", "task"],
	)
	for o in open_logs:
		stop_timer(o["name"])
	tl = frappe.get_doc({
		"doctype": "CRM Task Time Log",
		"task": task,
		"user": user,
		"started_at": _now(),
		"billable": 0,
	}).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"time_log": tl.name}


@frappe.whitelist()
def stop_timer(time_log, note=None, billable=0):
	if not _doctype_ready("CRM Task Time Log"):
		frappe.throw(_("Time logs unavailable"))
	tl = frappe.get_doc("CRM Task Time Log", time_log)
	if tl.ended_at:
		return tl.name
	tl.ended_at = _now()
	tl.duration_minutes = max(0, time_diff_in_seconds(tl.ended_at, _to_dt(tl.started_at)) / 60.0)
	tl.note = note
	tl.billable = int(billable or 0)
	tl.save(ignore_permissions=True)
	_recompute_time_total(tl.task)
	frappe.db.commit()
	return tl.name


@frappe.whitelist()
def log_time(task, minutes, billable=0, note=None, started_at=None):
	if not _doctype_ready("CRM Task Time Log"):
		frappe.throw(_("Time logs unavailable"))
	started = _to_dt(started_at) if started_at else _now()
	ended = add_to_date(started, minutes=int(minutes))
	tl = frappe.get_doc({
		"doctype": "CRM Task Time Log",
		"task": task,
		"user": frappe.session.user,
		"started_at": started,
		"ended_at": ended,
		"duration_minutes": float(minutes),
		"billable": int(billable or 0),
		"note": note,
	}).insert(ignore_permissions=True)
	_recompute_time_total(task)
	frappe.db.commit()
	return tl.name


def _recompute_time_total(task):
	total = frappe.db.sql(
		"SELECT COALESCE(SUM(duration_minutes),0) FROM `tabCRM Task Time Log` WHERE task=%s",
		(task,),
	)[0][0]
	frappe.db.set_value("CRM Task", task, "time_logged_minutes", float(total or 0), update_modified=False)


# ---------- templates / types / escalations ----------


@frappe.whitelist()
def list_templates():
	if not _doctype_ready("CRM Task Template"):
		return []
	rows = frappe.get_all(
		"CRM Task Template",
		fields=["name", "template_name", "active", "default_type", "default_priority", "version", "description"],
		order_by="template_name asc",
	)
	for r in rows:
		raw_c = frappe.db.get_value("CRM Task Template", r["name"], "default_checklist_json")
		raw_s = frappe.db.get_value("CRM Task Template", r["name"], "default_subtasks_json")
		try:
			r["checklist"] = json.loads(raw_c) if raw_c else []
		except Exception:
			r["checklist"] = []
		try:
			r["subtasks"] = json.loads(raw_s) if raw_s else []
		except Exception:
			r["subtasks"] = []
	return rows


@frappe.whitelist()
def upsert_template(payload):
	if isinstance(payload, str):
		payload = json.loads(payload)
	name = payload.get("template_name")
	if not name:
		frappe.throw(_("Template name required."))
	if frappe.db.exists("CRM Task Template", name):
		doc = frappe.get_doc("CRM Task Template", name)
		doc.version = int(doc.version or 1) + 1
	else:
		doc = frappe.new_doc("CRM Task Template")
		doc.template_name = name
		doc.version = 1
	doc.active = int(payload.get("active", 1))
	doc.default_type = payload.get("default_type")
	doc.default_priority = payload.get("default_priority") or "Medium"
	doc.description = payload.get("description")
	doc.default_checklist_json = json.dumps(payload.get("checklist") or [])
	doc.default_subtasks_json = json.dumps(payload.get("subtasks") or [])
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def apply_template(template, target_doctype=None, target_name=None, due_in_days=7):
	if not _doctype_ready("CRM Task Template"):
		frappe.throw(_("Templates not enabled"))
	tpl = frappe.get_doc("CRM Task Template", template)
	try:
		checklist = json.loads(tpl.default_checklist_json or "[]")
	except Exception:
		checklist = []
	try:
		subtasks = json.loads(tpl.default_subtasks_json or "[]")
	except Exception:
		subtasks = []
	due = add_to_date(_now(), days=int(due_in_days))
	parent = frappe.new_doc("CRM Task")
	parent.title = f"{tpl.template_name}"
	parent.priority = tpl.default_priority or "Medium"
	parent.status = "Todo"
	parent.task_type = tpl.default_type
	parent.due_date = due
	parent.assigned_to = frappe.session.user
	parent.reference_doctype = target_doctype
	parent.reference_docname = target_name
	parent.template_used = tpl.name
	parent.description = tpl.description
	parent.insert(ignore_permissions=True)
	for i, label in enumerate(checklist):
		parent.append("checklist", {"label": label if isinstance(label, str) else label.get("label"), "position": i})
	parent.save(ignore_permissions=True)
	_replace_assignees(parent, [frappe.session.user])
	created = [parent.name]
	for i, st in enumerate(subtasks):
		child = frappe.new_doc("CRM Task")
		child.title = st.get("title") if isinstance(st, dict) else str(st)
		child.priority = (st.get("priority") if isinstance(st, dict) else None) or parent.priority
		child.status = "Backlog"
		child.task_type = parent.task_type
		child.parent_task = parent.name
		child.assigned_to = frappe.session.user
		child.due_date = add_to_date(due, days=-1 * (len(subtasks) - i))
		child.reference_doctype = target_doctype
		child.reference_docname = target_name
		child.insert(ignore_permissions=True)
		created.append(child.name)
	_sla_persist(parent)
	frappe.db.commit()
	return created


@frappe.whitelist()
def list_task_types():
	if not _doctype_ready("CRM Task Type"):
		return []
	rows = frappe.get_all(
		"CRM Task Type",
		fields=["name", "type_name", "active", "business_hours_only", "color", "default_template"],
		order_by="type_name asc",
	)
	for r in rows:
		raw = frappe.db.get_value("CRM Task Type", r["name"], "sla_matrix_json")
		try:
			r["sla_matrix"] = json.loads(raw) if raw else {}
		except Exception:
			r["sla_matrix"] = {}
	return rows


@frappe.whitelist()
def upsert_task_type(payload):
	if isinstance(payload, str):
		payload = json.loads(payload)
	name = payload.get("type_name")
	if not name:
		frappe.throw(_("Type name required"))
	if frappe.db.exists("CRM Task Type", name):
		doc = frappe.get_doc("CRM Task Type", name)
	else:
		doc = frappe.new_doc("CRM Task Type")
		doc.type_name = name
	doc.active = int(payload.get("active", 1))
	doc.business_hours_only = int(payload.get("business_hours_only", 1))
	doc.color = payload.get("color")
	doc.sla_matrix_json = json.dumps(payload.get("sla_matrix") or {})
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def list_escalation_rules():
	if not _doctype_ready("CRM Task Escalation Rule"):
		return []
	return frappe.get_all(
		"CRM Task Escalation Rule",
		fields=["name", "rule_name", "active", "task_type", "level", "after_minutes_past_due", "action", "recipient_user", "recipient_role"],
		order_by="task_type asc, level asc",
	)


@frappe.whitelist()
def upsert_escalation_rule(payload):
	if isinstance(payload, str):
		payload = json.loads(payload)
	name = payload.get("rule_name")
	if not name:
		frappe.throw(_("Rule name required"))
	if frappe.db.exists("CRM Task Escalation Rule", name):
		doc = frappe.get_doc("CRM Task Escalation Rule", name)
	else:
		doc = frappe.new_doc("CRM Task Escalation Rule")
		doc.rule_name = name
	doc.active = int(payload.get("active", 1))
	doc.task_type = payload.get("task_type")
	doc.level = int(payload.get("level", 1))
	doc.after_minutes_past_due = int(payload.get("after_minutes_past_due", 0))
	doc.action = payload.get("action") or "notify"
	doc.recipient_user = payload.get("recipient_user")
	doc.recipient_role = payload.get("recipient_role")
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


# ---------- views: calendar / gantt / workload / analytics ----------


@frappe.whitelist()
def calendar_feed(start=None, end=None):
	filters = []
	if start and end:
		filters.append(["due_date", "between", [start, end]])
	tasks = frappe.get_all(
		"CRM Task",
		filters=filters,
		fields=["name", "title", "due_date", "priority", "status", "assigned_to", "task_type"],
		limit_page_length=500,
	)
	for t in tasks:
		t["assignee_name"] = _user_full_name(t["assigned_to"]) if t.get("assigned_to") else ""
	return tasks


@frappe.whitelist()
def gantt_feed():
	tasks = frappe.get_all(
		"CRM Task",
		filters=[["status", "in", list(OPEN_STATUSES) + ["Done"]]],
		fields=_task_fields() + ["start_date"],
		order_by="due_date asc",
		limit_page_length=200,
	)
	deps = []
	if _doctype_ready("CRM Task Dependency"):
		deps = frappe.get_all(
			"CRM Task Dependency",
			filters={"parenttype": "CRM Task"},
			fields=["parent", "depends_on", "kind"],
		)
	for t in tasks:
		_compute_sla(t)
	return {"tasks": tasks, "dependencies": deps}


@frappe.whitelist()
def workload():
	users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User"},
		fields=["name", "full_name", "user_image"],
		limit_page_length=50,
	)
	rows = []
	for u in users:
		open_tasks = frappe.get_all(
			"CRM Task",
			filters=[["assigned_to", "=", u["name"]], ["status", "in", list(OPEN_STATUSES)]],
			fields=["name", "priority", "due_date", "status", "sla_state"],
			limit_page_length=200,
		)
		for t in open_tasks:
			_compute_sla(t)
		overdue = sum(1 for t in open_tasks if t.get("sla_state") == "Breached")
		blocked = sum(1 for t in open_tasks if t.get("status") == "Blocked")
		capacity = 8  # static demo default
		by_day = defaultdict(int)
		for t in open_tasks:
			if t.get("due_date"):
				d = getdate(t["due_date"])
				by_day[d.isoformat()] += 1
		rows.append({
			"user": u["name"],
			"full_name": u["full_name"] or u["name"],
			"user_image": u["user_image"],
			"open": len(open_tasks),
			"overdue": overdue,
			"blocked": blocked,
			"capacity": capacity,
			"by_day": dict(by_day),
		})
	return rows


@frappe.whitelist()
def sla_analytics(days=30, group_by="type"):
	days = int(days)
	since = add_to_date(_now(), days=-days)
	tasks = frappe.get_all(
		"CRM Task",
		filters=[["modified", ">=", since]],
		fields=_task_fields(),
		limit_page_length=2000,
	)
	for t in tasks:
		_compute_sla(t)
	total = len(tasks) or 1
	breached = sum(1 for t in tasks if t.get("sla_state") == "Breached")
	completed = [t for t in tasks if t.get("status") == "Done"]
	resolved_minutes = []
	for t in completed:
		if t.get("started_at") and t.get("completed_at"):
			mins = time_diff_in_seconds(_to_dt(t["completed_at"]), _to_dt(t["started_at"])) / 60.0
			if mins > 0:
				resolved_minutes.append(mins)
	avg_resolve = round(sum(resolved_minutes) / len(resolved_minutes), 1) if resolved_minutes else 0
	compliance = round((1 - breached / total) * 100, 1)

	groups = defaultdict(lambda: {"total": 0, "breached": 0, "completed": 0})
	for t in tasks:
		key = t.get(group_by) or t.get("priority") or "—"
		groups[key]["total"] += 1
		if t.get("sla_state") == "Breached":
			groups[key]["breached"] += 1
		if t.get("status") == "Done":
			groups[key]["completed"] += 1
	group_rows = []
	for k, v in groups.items():
		comp = round((1 - v["breached"] / v["total"]) * 100, 1) if v["total"] else 100
		group_rows.append({"key": k, "total": v["total"], "breached": v["breached"], "completed": v["completed"], "compliance": comp})
	group_rows.sort(key=lambda r: r["compliance"])

	# Trend: per-day breach count + completion count, last `days` days
	trend = []
	day_breach = defaultdict(int)
	day_complete = defaultdict(int)
	for t in tasks:
		if t.get("completed_at") and t["status"] == "Done":
			day_complete[str(getdate(t["completed_at"]))] += 1
		if t.get("sla_state") == "Breached" and t.get("modified"):
			day_breach[str(getdate(t["modified"]))] += 1
	for i in range(days, -1, -1):
		d = str(getdate(add_to_date(_now(), days=-i)))
		trend.append({"date": d, "breached": day_breach.get(d, 0), "completed": day_complete.get(d, 0)})

	escalation_count = 0
	if _doctype_ready("CRM Task Escalation Event"):
		escalation_count = frappe.db.count(
			"CRM Task Escalation Event", filters=[["fired_at", ">=", since]]
		)

	return {
		"total": total,
		"breached": breached,
		"compliance_pct": compliance,
		"avg_resolve_minutes": avg_resolve,
		"escalation_count": escalation_count,
		"groups": group_rows,
		"trend": trend,
	}


@frappe.whitelist()
def export_analytics_csv(days=30, group_by="type"):
	data = sla_analytics(days=days, group_by=group_by)
	import csv
	import io

	buf = io.StringIO()
	w = csv.writer(buf)
	w.writerow(["Group", "Total", "Breached", "Completed", "Compliance %"])
	for r in data["groups"]:
		w.writerow([r["key"], r["total"], r["breached"], r["completed"], r["compliance"]])
	return buf.getvalue()


@frappe.whitelist()
def add_comment(task, content):
	if not content or not content.strip():
		frappe.throw(_("Empty comment"))
	c = frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": "CRM Task",
		"reference_name": task,
		"comment_email": frappe.session.user,
		"comment_by": _user_full_name(frappe.session.user),
		"content": content,
	}).insert(ignore_permissions=True)
	frappe.db.commit()
	return c.name


@frappe.whitelist()
def acknowledge_escalation(event):
	if not _doctype_ready("CRM Task Escalation Event"):
		frappe.throw(_("Not enabled"))
	doc = frappe.get_doc("CRM Task Escalation Event", event)
	doc.acknowledged_at = _now()
	doc.acknowledged_by = frappe.session.user
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def delete_task(name):
	if not _doctype_ready("CRM Task"):
		frappe.throw(_("Tasks not enabled"))
	doc = frappe.get_doc("CRM Task", name)
	if doc.status == "Canceled":
		frappe.throw(_("Task already canceled"))
	doc.status = "Canceled"
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def delete_template(name):
	if not _doctype_ready("CRM Task Template"):
		frappe.throw(_("Templates not enabled"))
	frappe.delete_doc("CRM Task Template", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def delete_task_type(name):
	if not _doctype_ready("CRM Task Type"):
		frappe.throw(_("Task types not enabled"))
	frappe.delete_doc("CRM Task Type", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def delete_escalation_rule(name):
	if not _doctype_ready("CRM Task Escalation Rule"):
		frappe.throw(_("Escalation rules not enabled"))
	frappe.delete_doc("CRM Task Escalation Rule", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def update_task(name, fields):
	if not _doctype_ready("CRM Task"):
		frappe.throw(_("Tasks not enabled"))
	if isinstance(fields, str):
		fields = json.loads(fields)
	doc = frappe.get_doc("CRM Task", name)
	allowed = {"title", "description", "due_date", "priority", "task_type"}
	for k, v in fields.items():
		if k in allowed:
			setattr(doc, k, v)
	doc.save(ignore_permissions=True)
	_sla_persist(doc)
	frappe.db.commit()
	return get_task(name)


@frappe.whitelist()
def seed_task_sample_data():
	if not _doctype_ready("CRM Task"):
		frappe.throw(_("Tasks not enabled"))
	existing = frappe.get_all("CRM Task", limit=1)
	if existing:
		return {"created": False, "message": "Tasks already exist"}

	user = frappe.session.user

	tt = None
	if _doctype_ready("CRM Task Type"):
		tt = frappe.new_doc("CRM Task Type")
		tt.type_name = "Credit Review"
		tt.active = 1
		tt.business_hours_only = 1
		tt.color = "#008C95"
		tt.sla_matrix_json = json.dumps({"Critical": 240, "High": 1440, "Medium": 4320, "Low": 10080})
		tt.insert(ignore_permissions=True)

	tpl = None
	if _doctype_ready("CRM Task Template"):
		tpl = frappe.new_doc("CRM Task Template")
		tpl.template_name = "KYC Onboarding"
		tpl.active = 1
		tpl.default_type = tt.name if tt else None
		tpl.default_priority = "High"
		tpl.version = 1
		tpl.description = "Standard KYC onboarding checklist"
		tpl.default_checklist_json = json.dumps(["Verify ID", "Check blacklist", "Assign RM"])
		tpl.default_subtasks_json = json.dumps([{"title": "Collect documents"}, {"title": "Validate address"}])
		tpl.insert(ignore_permissions=True)

	if _doctype_ready("CRM Task Escalation Rule"):
		rule = frappe.new_doc("CRM Task Escalation Rule")
		rule.rule_name = "Overdue Notify"
		rule.active = 1
		rule.task_type = tt.name if tt else None
		rule.level = 1
		rule.after_minutes_past_due = 60
		rule.action = "notify"
		rule.recipient_user = user
		rule.insert(ignore_permissions=True)

	task1 = frappe.new_doc("CRM Task")
	task1.title = "Review credit application"
	task1.priority = "High"
	task1.status = "Todo"
	task1.task_type = tt.name if tt else None
	task1.assigned_to = user
	task1.due_date = add_to_date(_now(), days=2)
	task1.description = "Initial review of submitted credit application"
	task1.insert(ignore_permissions=True)
	if task1.assigned_to:
		_replace_assignees(task1, [task1.assigned_to])
	_sla_persist(task1)

	task2 = frappe.new_doc("CRM Task")
	task2.title = "Follow up with borrower"
	task2.priority = "Medium"
	task2.status = "In Progress"
	task2.task_type = tt.name if tt else None
	task2.assigned_to = user
	task2.due_date = add_to_date(_now(), days=5)
	task2.description = "Call borrower for missing documents"
	task2.started_at = _now()
	task2.insert(ignore_permissions=True)
	if task2.assigned_to:
		_replace_assignees(task2, [task2.assigned_to])
	_sla_persist(task2)

	frappe.db.commit()
	return {"created": True, "tasks": [task1.name, task2.name]}
