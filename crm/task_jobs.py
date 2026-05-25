import json
from datetime import datetime, timedelta

import frappe
from frappe.utils import add_days, add_months, cint, get_datetime, now, now_datetime, time_diff_in_seconds


def _parse_recurrence_rule(rule):
    """Parse simple recurrence rules like 'daily', 'weekly', 'monthly' or 'every N days'."""
    if not rule:
        return None
    rule = rule.strip().lower()
    if rule == "daily":
        return {"days": 1}
    if rule == "weekly":
        return {"days": 7}
    if rule == "monthly":
        return {"months": 1}
    if rule.startswith("every ") and rule.endswith(" days"):
        try:
            return {"days": int(rule.replace("every ", "").replace(" days", "").strip())}
        except ValueError:
            return None
    if rule.startswith("every ") and rule.endswith(" weeks"):
        try:
            return {"days": int(rule.replace("every ", "").replace(" weeks", "").strip()) * 7}
        except ValueError:
            return None
    return None


def process_recurring_tasks():
    """Create new task instances for recurring tasks whose next occurrence is due."""
    recurring = frappe.get_all(
        "CRM Task",
        filters={"recurring": 1, "status": ["!=", "Cancelled"]},
        fields=["name", "title", "description", "task_type", "priority", "due_date", "recurrence_rule", "owner"],
    )
    now = now_datetime()
    created = 0
    for task in recurring:
        interval = _parse_recurrence_rule(task.recurrence_rule)
        if not interval:
            continue
        last = _get_last_instance_date(task.name) or get_datetime(task.due_date)
        if not last:
            continue
        next_due = _compute_next_due(last, interval)
        if next_due and next_due <= now:
            _create_task_instance(task, next_due)
            created += 1
    if created:
        frappe.logger().info(f"Created {created} recurring task instances")


def _get_last_instance_date(parent_task):
    """Get the most recent instance created from this recurring task."""
    instances = frappe.get_all(
        "CRM Task",
        filters={"parent_task": parent_task},
        fields=["due_date"],
        order_by="creation desc",
        limit_page_length=1,
    )
    if instances:
        return get_datetime(instances[0]["due_date"])
    return None


def _compute_next_due(last_due, interval):
    if "days" in interval:
        return add_days(last_due, interval["days"])
    if "months" in interval:
        return add_months(last_due, interval["months"])
    return None


def _create_task_instance(task, due_date):
    assignees = frappe.get_all(
        "CRM Task Assignee",
        filters={"parent": task.name, "parenttype": "CRM Task"},
        fields=["user"],
    )
    doc = frappe.get_doc({
        "doctype": "CRM Task",
        "title": task.title,
        "description": task.description,
        "task_type": task.task_type,
        "priority": task.priority,
        "due_date": due_date,
        "status": "Todo",
        "parent_task": task.name,
    })
    doc.insert(ignore_permissions=True)
    for a in assignees:
        doc.append("assignees", {"user": a["user"]})
    doc.save(ignore_permissions=True)


def process_escalations():
    """Evaluate SLA breaches and fire escalation rules."""
    now = now_datetime()
    tasks = frappe.get_all(
        "CRM Task",
        filters={
            "status": ["not in", ["Done", "Cancelled"]],
            "sla_due_at": ["<=", now],
        },
        fields=["name", "title", "status", "sla_due_at", "task_type", "priority", "owner"],
    )
    fired = 0
    for task in tasks:
        if _already_escalated(task["name"]):
            continue
        rules = _matching_escalation_rules(task)
        for rule in rules:
            _fire_escalation(task, rule)
            fired += 1
    if fired:
        frappe.logger().info(f"Fired {fired} escalations")


def _already_escalated(task_name):
    return frappe.db.exists("CRM Task Escalation Event", {"task": task_name})


def _matching_escalation_rules(task):
    now = now_datetime()
    rules = frappe.get_all(
        "CRM Task Escalation Rule",
        filters={"active": 1},
        fields=["name", "after_minutes_past_due", "action", "recipient_user", "recipient_role", "level"],
    )
    matched = []
    sla_due = get_datetime(task.get("sla_due_at"))
    minutes_past = 0
    if sla_due:
        minutes_past = time_diff_in_seconds(now, sla_due) / 60
    for rule in rules:
        threshold = cint(rule.get("after_minutes_past_due"))
        if threshold and minutes_past < threshold:
            continue
        matched.append(rule)
    return matched


def _fire_escalation(task, rule):
    event = frappe.get_doc({
        "doctype": "CRM Task Escalation Event",
        "task": task["name"],
        "rule": rule["name"],
        "level": rule.get("level", 1),
        "fired_at": now(),
        "action": rule.get("action", "notify"),
        "recipient_user": rule.get("recipient_user"),
    })
    event.insert(ignore_permissions=True)
    notify_user = rule.get("recipient_user")
    if not notify_user and rule.get("recipient_role"):
        users = frappe.get_all(
            "User",
            filters={"enabled": 1},
            fields=["name"],
            limit=1,
        )
        notify_user = users[0]["name"] if users else None
    if notify_user:
        try:
            frappe.get_doc({
                "doctype": "CRM Notification",
                "from_user": frappe.session.user if frappe.session.user != "Guest" else "Administrator",
                "to_user": notify_user,
                "type": "Task",
                "message": f"Task SLA breached: {task['title']}",
                "notification_text": f"Task SLA breached: {task['title']}",
                "reference_doctype": "CRM Task",
                "reference_name": task["name"],
            }).insert(ignore_permissions=True)
        except Exception:
            pass
