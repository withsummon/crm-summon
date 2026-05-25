import hashlib
import json
from datetime import datetime, timedelta

import frappe
from frappe import _
from frappe.utils import cint, get_datetime, now, now_datetime


def _hash_payload(payload: dict, prev_hash: str = "") -> str:
    """Compute a chained SHA-256 hash of the audit payload."""
    data = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(f"{prev_hash}:{data}".encode("utf-8")).hexdigest()


def _get_retention_policies():
    if not frappe.db.table_exists("CRM Audit Retention Policy"):
        return []
    try:
        return frappe.get_all(
            "CRM Audit Retention Policy",
            fields=["category", "days", "storage", "active"],
            filters={"active": 1},
        )
    except Exception:
        return []


def _get_alert_rules():
    if not frappe.db.table_exists("CRM Audit Alert Rule"):
        return []
    try:
        return frappe.get_all(
            "CRM Audit Alert Rule",
            fields=["rule_name as name", "condition", "severity", "channels", "active"],
            filters={"active": 1},
        )
    except Exception:
        return []


@frappe.whitelist()
def get_audit_context():
    """Return overview stats for the audit dashboard."""
    days_30 = now_datetime() - timedelta(days=30)
    activity_count = _safe_count("Activity Log", {"creation": [">=", days_30]})
    version_count = _safe_count("Version", {"creation": [">=", days_30]})
    request_count = _safe_count("Request Log", {"creation": [">=", days_30]})
    failed_logins = _safe_count("Activity Log", {"creation": [">=", days_30], "status": ["like", "%fail%"]})
    overrides = _safe_count("Activity Log", {"creation": [">=", days_30], "subject": ["like", "%override%"]})
    return {
        "activity_count": activity_count,
        "version_count": version_count,
        "request_count": request_count,
        "failed_logins": failed_logins,
        "overrides": overrides,
        "retention_policies": _get_retention_policies(),
        "alert_rules": _get_alert_rules(),
    }


@frappe.whitelist()
def create_audit_entry(category, action, actor, target_doctype, target_name, severity, summary, metadata=None):
    """Manually create an Activity Log entry for custom audit events."""
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    doc = frappe.get_doc({
        "doctype": "Activity Log",
        "subject": summary,
        "content": json.dumps(metadata or {}),
        "operation": action,
        "status": severity,
        "reference_doctype": target_doctype,
        "reference_name": target_name,
        "user": actor,
        "full_name": actor,
    })
    doc.insert(ignore_permissions=True)
    return {"name": doc.name}


@frappe.whitelist()
def seed_audit_sample_data():
    """Create sample Activity Log entries for the audit trail."""
    samples = [
        ("login", "success", "admin@example.com", "User", "admin@example.com", "info", "Successful login from trusted device"),
        ("login", "fail", "intruder@example.com", "User", "intruder@example.com", "critical", "3 failed login attempts"),
        ("approval", "override", "compliance@example.com", "CRM Credit Application", "APP-001", "warning", "Director override approval"),
        ("export", "export", "ops@example.com", "CRM Lead", "Lead CSV", "warning", "Bulk export of 2500 rows"),
        ("view", "view", "reviewer@example.com", "Customer", "CUST-001", "info", "PII record viewed for KYC review"),
        ("api", "post", "integration@example.com", "CRM Deal", "DEAL-001", "info", "Third-party API sync completed"),
        ("ai", "invoke", "analyst@example.com", "CRM Credit Application", "APP-002", "info", "AI risk insight generated"),
        ("api", "get", "mobile@example.com", "CRM Lead", "LEAD-001", "warning", "Rate limit exceeded"),
    ]
    created = 0
    for category, action, actor, target_doctype, target_name, severity, summary in samples:
        doc = frappe.get_doc({
            "doctype": "Activity Log",
            "subject": summary,
            "content": json.dumps({"category": category, "sample": True}),
            "operation": action,
            "status": severity,
            "reference_doctype": target_doctype,
            "reference_name": target_name,
            "user": actor,
            "full_name": actor,
        })
        doc.insert(ignore_permissions=True)
        created += 1
    return {"created": created}


@frappe.whitelist()
def get_audit_events(
    filters=None,
    start=0,
    limit=200,
):
    """Fetch normalized audit events from Activity Log, Version, and Request Log."""
    if isinstance(filters, str):
        filters = json.loads(filters)
    filters = filters or {}
    days = cint(filters.get("days", 30))
    since = now_datetime() - timedelta(days=days)

    activity_fields = [
        "name", "creation", "owner", "subject", "content", "communication_date",
        "operation", "status", "reference_doctype", "reference_name",
        "link_doctype", "link_name", "user", "full_name", "ip_address",
    ]
    version_fields = ["name", "creation", "owner", "ref_doctype", "docname", "data"]
    request_fields = ["name", "creation", "owner", "url", "method", "status", "response", "error", "time", "ip_address"]

    activity = _safe_get_all("Activity Log", activity_fields, since, limit)
    versions = _safe_get_all("Version", version_fields, since, limit)
    requests = _safe_get_all("Request Log", request_fields, since, limit)

    events = []
    prev_hash = ""
    for log in activity:
        event = _normalize_activity(log)
        event["entry_hash"] = _hash_payload(event, prev_hash)
        event["prev_hash"] = prev_hash
        prev_hash = event["entry_hash"]
        events.append(event)

    for log in versions:
        event = _normalize_version(log)
        event["entry_hash"] = _hash_payload(event, prev_hash)
        event["prev_hash"] = prev_hash
        prev_hash = event["entry_hash"]
        events.append(event)

    for log in requests:
        event = _normalize_request(log)
        event["entry_hash"] = _hash_payload(event, prev_hash)
        event["prev_hash"] = prev_hash
        prev_hash = event["entry_hash"]
        events.append(event)

    events.sort(key=lambda x: x["timestamp"], reverse=True)
    return events


def _safe_count(doctype, filters):
    if not frappe.db.table_exists(doctype):
        return 0
    try:
        return frappe.db.count(doctype, filters)
    except Exception:
        return 0


def _safe_get_all(doctype, fields, since, limit):
    if not frappe.db.table_exists(doctype):
        return []
    try:
        return frappe.get_all(
            doctype,
            fields=fields,
            filters={"creation": [">=", since]},
            order_by="creation desc",
            limit_page_length=limit,
        )
    except Exception:
        return []


@frappe.whitelist()
def verify_hash_chain(events):
    """Verify the integrity of a list of audit events by recomputing hashes."""
    if isinstance(events, str):
        events = json.loads(events)
    if not events:
        return {"valid": True, "broken_at": None, "message": "No events to verify"}

    prev_hash = ""
    for i, ev in enumerate(events):
        payload = {k: v for k, v in ev.items() if k not in ("entry_hash", "prev_hash")}
        computed = _hash_payload(payload, prev_hash)
        if computed != ev.get("entry_hash"):
            return {
                "valid": False,
                "broken_at": i,
                "event_name": ev.get("name"),
                "message": f"Hash mismatch at event {i} ({ev.get('name', 'unknown')})",
            }
        prev_hash = computed

    return {"valid": True, "broken_at": None, "message": "All events verified"}


@frappe.whitelist()
def export_evidence(format="CSV", filters=None):
    """Export audit evidence to CSV/Excel."""
    if isinstance(filters, str):
        filters = json.loads(filters)
    events = get_audit_events(filters=filters, limit=5000)
    if format.upper() == "CSV":
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["timestamp", "category", "action", "actor", "target_doctype", "target_name", "severity", "ip", "summary", "entry_hash", "prev_hash"])
        for ev in events:
            writer.writerow([
                ev["timestamp"], ev["category"], ev["action"], ev["actor"],
                ev["target_doctype"], ev["target_name"], ev["severity"],
                ev["ip"], ev["summary"], ev["entry_hash"], ev["prev_hash"],
            ])
        filename = f"audit-evidence-{now_datetime().strftime('%Y%m%d_%H%M%S')}.csv"
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": filename,
            "content": output.getvalue(),
            "is_private": 1,
        })
        file_doc.insert(ignore_permissions=True)
        return {"file_url": file_doc.file_url, "filename": filename, "row_count": len(events)}
    return {"message": "Only CSV export is supported at this time."}


def _normalize_activity(log):
    operation = str(log.get("operation") or log.get("status") or log.get("subject") or "").lower()
    login = "login" in operation or "login" in str(log.get("subject") or "").lower()
    return {
        "name": log["name"],
        "timestamp": log.get("communication_date") or log["creation"],
        "category": "login" if login else "activity",
        "action": _normalize_action(log.get("operation") or log.get("status") or "activity"),
        "actor": log.get("full_name") or log.get("user") or log["owner"],
        "target_doctype": log.get("reference_doctype") or log.get("link_doctype") or "Activity Log",
        "target_name": log.get("reference_name") or log.get("link_name") or log["name"],
        "severity": "warning" if ("fail" in operation or "error" in operation) else "info",
        "ip": log.get("ip_address") or "",
        "geo": "",
        "summary": frappe.utils.strip_html(log.get("subject") or log.get("content") or "Activity Log entry"),
        "metadata": log,
    }


def _normalize_version(log):
    diff = _parse_version_diff(log.get("data"))
    return {
        "name": log["name"],
        "timestamp": log["creation"],
        "category": "field_change",
        "action": "update",
        "actor": log["owner"],
        "target_doctype": log.get("ref_doctype") or "Document",
        "target_name": log.get("docname") or log["name"],
        "severity": "info",
        "ip": "",
        "geo": "",
        "summary": f"{len(diff) or 1} field changes captured",
        "metadata": log,
        "diff_preview": diff,
    }


def _normalize_request(log):
    status = str(log.get("status") or log.get("response") or "")
    return {
        "name": log["name"],
        "timestamp": log["creation"],
        "category": "api",
        "action": str(log.get("method") or "request").lower(),
        "actor": log["owner"],
        "target_doctype": "Request Log",
        "target_name": log.get("url") or log["name"],
        "severity": "critical" if (status.startswith("5") or log.get("error")) else "warning" if status.startswith("4") else "info",
        "ip": log.get("ip_address") or "",
        "geo": "",
        "summary": f"Status {log.get('status') or 'recorded'} · {log.get('time') or '-'} ms",
        "metadata": log,
    }


def _normalize_action(value):
    normalized = str(value or "").lower()
    if "fail" in normalized:
        return "fail"
    if "success" in normalized:
        return "success"
    if "delete" in normalized:
        return "delete"
    if "create" in normalized or "insert" in normalized:
        return "create"
    if "update" in normalized or "edit" in normalized:
        return "update"
    if "login" in normalized:
        return "success"
    return normalized.replace(r"\s+", "_") or "activity"


def _parse_version_diff(data):
    try:
        parsed = json.loads(data) if isinstance(data, str) else data
        changed = parsed.get("changed", [])
        return [{"field": c[0], "old": str(c[1] or ""), "new": str(c[2] or "")} for c in changed[:4]]
    except Exception:
        return []






