import json
import frappe
from frappe import _
from frappe.utils import flt
from crm.utils.workflow_engine import start_flow_execution, submit_node_action


@frappe.whitelist()
def start_execution(application_id):
	"""API endpoint to start visual flow execution for a credit application"""
	try:
		exec_doc = start_flow_execution(application_id)
		if not exec_doc:
			return {"ok": False, "message": _("No matching published Workflow found for this application.")}
		return {"ok": True, "execution_id": exec_doc.name, "current_node": exec_doc.current_node}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "WorkflowExecution.start_execution")
		frappe.throw(str(e))


@frappe.whitelist()
def submit_action(application_id, action_name, form_data=None, reason=None):
	"""API endpoint to submit an RM / Approver action and advance the flow"""
	try:
		success = submit_node_action(application_id, action_name, form_data, reason=reason)
		if not success:
			return {"ok": False, "message": _("No active flow execution found for this application.")}
		return {"ok": True}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "WorkflowExecution.submit_action")
		frappe.throw(str(e))


@frappe.whitelist()
def get_current_state(application_id):
	"""Get current active node state and flow options for an application"""
	exec_records = frappe.get_all(
		"CRM Workflow Execution",
		filters={"application": application_id, "status": "Running"},
		limit=1
	)
	if not exec_records:
		return {"ok": False, "message": _("No active execution found.")}

	exec_doc = frappe.get_doc("CRM Workflow Execution", exec_records[0].name)
	active_states = frappe.get_all(
		"CRM Workflow Node State",
		filters={"execution": exec_doc.name, "status": "active"},
		limit=1
	)
	if not active_states:
		return {
			"ok": True,
			"execution_id": exec_doc.name,
			"status": exec_doc.status,
			"current_node": exec_doc.current_node,
			"current_node_type": exec_doc.current_node_type,
			"current_node_label": exec_doc.current_node_label,
			"form_config": {},
			"available_actions": []
		}

	state_doc = frappe.get_doc("CRM Workflow Node State", active_states[0].name)

	# Extract config details from frozen flow json
	form_config = {}
	available_actions = []
	
	try:
		flow_data = json.loads(exec_doc.flow_version_json) if isinstance(exec_doc.flow_version_json, str) else exec_doc.flow_version_json
		nodes = flow_data.get("nodes", [])
		active_node = next((n for n in nodes if n.get("id") == state_doc.node_id), None)
		if active_node:
			config = active_node.get("data", {}).get("config", {})
			if state_doc.node_type == "FormNode":
				form_config = {
					"sections": config.get("sections", []),
					"fields": config.get("fields", []),
					"availableActions": config.get("availableActions", ["save_draft", "submit"])
				}
				available_actions = config.get("availableActions", ["save_draft", "submit"])
			elif state_doc.node_type == "ApprovalNode":
				form_config = {
					"sections": [],
					"fields": [],
					"availableActions": config.get("availableActions", ["approve", "reject", "return"])
				}
				available_actions = config.get("availableActions", ["approve", "reject", "return"])
	except Exception:
		pass

	return {
		"ok": True,
		"execution_id": exec_doc.name,
		"status": exec_doc.status,
		"current_node": state_doc.node_id,
		"current_node_type": state_doc.node_type,
		"current_node_label": exec_doc.current_node_label,
		"entered_at": state_doc.entered_at,
		"sla_deadline": state_doc.sla_deadline,
		"form_config": form_config,
		"available_actions": available_actions
	}


@frappe.whitelist()
def get_execution_history(execution_id):
	"""Get complete visual audit trail transition log for a flow execution"""
	logs = frappe.get_all(
		"CRM Workflow Audit Log",
		filters={"execution": execution_id},
		fields=["name", "node_id", "node_type", "node_label", "event_type", "timestamp", "user", "original_assignee", "delegated_to", "decision", "reason", "data"],
		order_by="timestamp asc"
	)
	return logs


@frappe.whitelist()
def get_execution_stats(flow_id):
	"""Calculate metric counts and averages for a credit flow designer"""
	executions = frappe.get_all(
		"CRM Workflow Execution",
		filters={"flow": flow_id},
		fields=["status", "started_at", "completed_at"]
	)
	
	total = len(executions)
	completed = len([e for e in executions if e.status == "Completed"])
	running = len([e for e in executions if e.status == "Running"])
	failed = len([e for e in executions if e.status in ["Failed", "Cancelled"]])
	
	# Average completion time in hours
	durations = []
	for exec_item in executions:
		if exec_item.completed_at and exec_item.started_at:
			delta = exec_item.completed_at - exec_item.started_at
			durations.append(delta.total_seconds() / 3600.0)
			
	avg_hours = flt(sum(durations) / len(durations)) if durations else 0.0

	return {
		"total": total,
		"completed": completed,
		"running": running,
		"failed": failed,
		"average_completion_hours": avg_hours
	}
