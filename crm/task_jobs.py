import json
from datetime import datetime, timedelta

import frappe
from frappe.utils import add_days, get_datetime, now, now_datetime


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
        fields=["name", "title", "description", "type", "priority", "due_date", "recurrence_rule", "owner"],
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
        # Approximate: add 30 days per month
        return add_days(last_due, interval["months"] * 30)
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
        "type": task.type,
        "priority": task.priority,
        "due_date": due_date,
        "status": "Not Started",
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
            "sla_due": ["<=", now],
        },
        fields=["name", "title", "status", "sla_due", "type", "priority", "owner"],
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
    rules = frappe.get_all(
        "CRM Task Escalation Rule",
        filters={"active": 1},
        fields=["name", "trigger_condition", "notify_users", "escalate_to", "message_template"],
    )
    matched = []
    for rule in rules:
        condition = (rule.get("trigger_condition") or "").lower()
        if "breach" in condition or "overdue" in condition:
            matched.append(rule)
        elif task.get("priority") == "Critical" and "critical" in condition:
            matched.append(rule)
    return matched


def _fire_escalation(task, rule):
    event = frappe.get_doc({
        "doctype": "CRM Task Escalation Event",
        "task": task["name"],
        "escalation_rule": rule["name"],
        "triggered_at": now(),
        "status": "Open",
        "message": (rule.get("message_template") or "Task SLA breached").format(**task),
    })
    event.insert(ignore_permissions=True)
    notify_users = json.loads(rule.get("notify_users") or "[]")
    if not notify_users and rule.get("escalate_to"):
        notify_users = [rule["escalate_to"]]
    for user in notify_users:
        try:
            frappe.get_doc({
                "doctype": "CRM Notification",
                "from_user": frappe.session.user if frappe.session.user != "Guest" else "Administrator",
                "to_user": user,
                "type": "Task",
                "message": event.message,
                "notification_text": event.message,
                "reference_doctype": "CRM Task",
                "reference_name": task["name"],
            }).insert(ignore_permissions=True)
        except Exception:
            pass
