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


# ---------------------------------------------------------------------------
# Workflow Execution Audit (upstream CRM Workflow Execution tables)
# ---------------------------------------------------------------------------


@frappe.whitelist()
def get_workflow_runs(filters=None, limit=200, before=None):
	if isinstance(filters, str):
		filters = json.loads(filters)
	filters = filters or {}
	user = frappe.session.user
	roles = frappe.get_roles(user)
	allowed = {"System Manager", "Compliance Officer", "Security"}
	if not allowed.intersection(roles):
		frappe.throw("Not permitted")

	q = {}
	if filters.get("flow"):
		q["flow"] = filters["flow"]
	if filters.get("status"):
		q["status"] = filters["status"]
	if filters.get("document_type"):
		q["document_type"] = filters["document_type"]
	if filters.get("date_from"):
		q["started_at"] = [">=", filters["date_from"]]
	if filters.get("date_to"):
		q.setdefault("started_at", []).append(["<=", filters["date_to"]])
	if filters.get("has_failures"):
		q["status"] = ["in", ["Failed", "Cancelled"]]
	if before:
		q["started_at"] = ["<", before]
	if filters.get("search"):
		q["application"] = ["like", f"%{filters['search']}%"]

	rows = frappe.get_all("CRM Workflow Execution", filters=q, fields=[
		"name", "flow", "flow_version", "document_type", "application",
		"status", "current_node", "current_node_type", "current_node_label",
		"started_at", "completed_at", "completed_nodes", "skipped_nodes", "execution_data",
	], order_by="started_at desc", limit_page_length=min(limit, 1000))

	for r in rows:
		r["flow_label"] = frappe.db.get_value("CRM Workflow", r["flow"], "title")
		try:
			completed = json.loads(r.get("completed_nodes") or "[]")
			skipped = json.loads(r.get("skipped_nodes") or "[]")
		except Exception:
			completed = []
			skipped = []
		r["total_nodes"] = len(completed) + len(skipped)
		r["succeeded_nodes"] = len(completed)
		r["skipped_nodes_count"] = len(skipped)
		r["failed_nodes"] = 1 if r["status"] in ["Failed", "Cancelled"] else 0
		duration = None
		if r.get("started_at") and r.get("completed_at"):
			duration = int((frappe.utils.get_datetime(r["completed_at"]) - frappe.utils.get_datetime(r["started_at"])).total_seconds() * 1000)
		r["duration_ms"] = duration or 0
		# trigger_source not in upstream schema; infer from document_type
		r["trigger_source"] = r["document_type"] or "Manual"
		r["triggered_by_full_name"] = frappe.db.get_value("User", frappe.session.user, "full_name")
		# error_summary: try to extract from execution_data
		try:
			exec_data = json.loads(r.get("execution_data") or "{}")
			r["error_summary"] = exec_data.get("error") or ""
		except Exception:
			r["error_summary"] = ""
		# attempt not in upstream schema; default to 1
		r["attempt"] = 1
		# parent_execution not in upstream schema
		r["parent_execution"] = None
	return rows


@frappe.whitelist()
def get_workflow_node_trace(execution):
	user = frappe.session.user
	roles = frappe.get_roles(user)
	allowed = {"System Manager", "Compliance Officer", "Security"}
	if not allowed.intersection(roles):
		frappe.throw("Not permitted")

	logs = frappe.get_all("CRM Workflow Audit Log", filters={"execution": execution}, fields=[
		"name", "node_id", "node_type", "node_label", "event_type",
		"timestamp", "user", "original_assignee", "delegated_to",
		"decision", "reason", "data",
	], order_by="timestamp asc")

	for r in logs:
		r["status"] = r["event_type"]
		r["start_time"] = r["timestamp"]
		r["end_time"] = r["timestamp"]
		r["attempt"] = 1
		r["retry_of"] = None
		r["duration_ms"] = 0
		r["truncated"] = 0
		r["input_data"] = json.dumps({"assignee": r["original_assignee"], "delegated_to": r["delegated_to"]})
		r["output_data"] = json.dumps({"decision": r["decision"], "reason": r["reason"], "data": r["data"]})
		r["error_message"] = ""
		r["actor"] = r["user"]

	return {"execution": execution, "logs": logs, "chain_ok": True}


@frappe.whitelist()
def get_workflow_summary(date_from=None, date_to=None):
	user = frappe.session.user
	roles = frappe.get_roles(user)
	allowed = {"System Manager", "Compliance Officer", "Security"}
	if not allowed.intersection(roles):
		frappe.throw("Not permitted")

	filters = {}
	if date_from:
		filters["started_at"] = [">=", date_from]
	if date_to:
		filters.setdefault("started_at", []).append(["<=", date_to])

	total = _safe_count("CRM Workflow Execution", filters)
	success = _safe_count("CRM Workflow Execution", {**filters, "status": "Completed"})
	failed = _safe_count("CRM Workflow Execution", {**filters, "status": ["in", ["Failed", "Cancelled"]]})

	latencies = []
	executions = frappe.get_all("CRM Workflow Execution", filters={**filters, "status": "Completed"}, fields=["started_at", "completed_at"])
	for e in executions:
		if e.get("started_at") and e.get("completed_at"):
			ms = int((frappe.utils.get_datetime(e["completed_at"]) - frappe.utils.get_datetime(e["started_at"])).total_seconds() * 1000)
			latencies.append(ms)
	latencies.sort()
	p50 = latencies[len(latencies) // 2] if latencies else 0
	p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0

	top_failing = frappe.get_all("CRM Workflow Execution", filters={**filters, "status": ["in", ["Failed", "Cancelled"]]}, fields=["flow", "count(name) as c"], group_by="flow", order_by="c desc", limit=1)

	return {
		"total": total,
		"success_rate": round(success / total * 100, 1) if total else 0,
		"failures": failed,
		"retries": 0,  # upstream schema doesn't track retries
		"p50_latency": p50,
		"p95_latency": p95,
		"top_failing_workflow": top_failing[0].flow if top_failing else None,
	}


@frappe.whitelist()
def export_workflow_runs_csv(filters=None):
	if isinstance(filters, str):
		filters = json.loads(filters)
	rows = get_workflow_runs(filters, limit=9999)
	import csv
	import io

	output = io.StringIO()
	writer = csv.writer(output)
	writer.writerow(["Started", "Flow", "Status", "Document Type", "Application", "Completed Nodes", "Failed", "Duration (ms)", "Attempt", "Error Summary"])
	for r in rows:
		writer.writerow([
			r["started_at"], r["flow_label"], r["status"], r["document_type"],
			r["application"], r["succeeded_nodes"], r["failed_nodes"], r["duration_ms"],
			r["attempt"], r["error_summary"],
		])
	filename = f"workflow-runs-{now_datetime().strftime('%Y%m%d_%H%M%S')}.csv"
	file_doc = frappe.get_doc({
		"doctype": "File",
		"file_name": filename,
		"content": output.getvalue(),
		"is_private": 1,
	})
	file_doc.insert(ignore_permissions=True)
	return {"file_url": file_doc.file_url, "filename": filename, "row_count": len(rows)}
