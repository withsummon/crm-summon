import json
import frappe
from frappe import _
from frappe.utils import now_datetime


@frappe.whitelist()
def get_flow(flow_id=None):
	"""Get single flow definition"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")

	if not flow_id or flow_id == "new":
		return {
			"name": "new",
			"title": _("New Workflow"),
			"description": "",
			"status": "Draft",
			"product_type": "",
			"applicant_persona": "Any",
			"is_pre_approved": 0,
			"flow_json": json.dumps({"nodes": [], "edges": []}),
			"current_version": 1
		}

	if not frappe.db.exists("CRM Workflow", flow_id):
		frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

	doc = frappe.get_doc("CRM Workflow", flow_id)
	return doc.as_dict()


@frappe.whitelist()
def save_flow_draft(flow_id=None, title=None, description=None, product_type=None, applicant_persona="Any", is_pre_approved=0, flow_json=None):
	"""Create or update draft credit flow definition"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")
	if not title:
		title = frappe.form_dict.get("title")
	if not description:
		description = frappe.form_dict.get("description")
	if not product_type:
		product_type = frappe.form_dict.get("product_type")
	if not applicant_persona or applicant_persona == "Any":
		applicant_persona = frappe.form_dict.get("applicant_persona") or "Any"
	if is_pre_approved in [0, "0", None]:
		is_pre_approved = frappe.form_dict.get("is_pre_approved") or 0
	if not flow_json:
		flow_json = frappe.form_dict.get("flow_json")

	if not title:
		frappe.throw(_("Title is required"))

	is_pre_approved_val = 1 if is_pre_approved in [1, "1", True, "True"] else 0

	if not flow_id or flow_id == "new":
		doc = frappe.new_doc("CRM Workflow")
		doc.title = title
		doc.description = description or ""
		doc.product_type = product_type
		doc.applicant_persona = applicant_persona or "Any"
		doc.is_pre_approved = is_pre_approved_val
		doc.flow_json = flow_json or json.dumps({"nodes": [], "edges": []})
		doc.status = "Draft"
		doc.current_version = 1
		doc.created_by = frappe.session.user
		doc.insert(ignore_permissions=True)
	else:
		if not frappe.db.exists("CRM Workflow", flow_id):
			frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

		doc = frappe.get_doc("CRM Workflow", flow_id)
		doc.title = title
		doc.description = description or ""
		doc.product_type = product_type
		doc.applicant_persona = applicant_persona or "Any"
		doc.is_pre_approved = is_pre_approved_val
		if flow_json:
			doc.flow_json = flow_json
		doc.status = "Draft"  # Reverts to draft on save
		doc.save(ignore_permissions=True)

	return doc.as_dict()


@frappe.whitelist()
def publish_flow(flow_id=None, change_note=""):
	"""Publish draft → creates new version"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")
	if not change_note:
		change_note = frappe.form_dict.get("change_note") or ""

	if not frappe.db.exists("CRM Workflow", flow_id):
		frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

	doc = frappe.get_doc("CRM Workflow", flow_id)

	# Validate before publishing
	validation_result = validate_flow_logic(doc.flow_json)
	if not validation_result.get("valid"):
		errors_str = "; ".join([e.get("message") for e in validation_result.get("errors", [])])
		frappe.throw(_("Validation errors found: {0}").format(errors_str))

	# Determine version number
	existing_versions = frappe.db.count("CRM Workflow Version", {"flow": flow_id})
	next_version = existing_versions + 1

	# Archive previous versions
	frappe.db.set_value("CRM Workflow Version", {"flow": flow_id, "status": "Published"}, "status", "Archived")

	# Create version record
	version_doc = frappe.new_doc("CRM Workflow Version")
	version_doc.flow = flow_id
	version_doc.version = next_version
	version_doc.flow_json = doc.flow_json
	version_doc.status = "Published"
	version_doc.change_note = change_note or _("Published version {0}").format(next_version)
	version_doc.published_by = frappe.session.user
	version_doc.published_at = now_datetime()
	version_doc.insert(ignore_permissions=True)

	# Update flow doc
	doc.status = "Published"
	doc.current_version = next_version
	doc.published_by = frappe.session.user
	doc.published_at = now_datetime()
	doc.save(ignore_permissions=True)

	return doc.as_dict()


@frappe.whitelist()
def clone_flow(flow_id=None):
	"""Clone flow definition"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")

	if not frappe.db.exists("CRM Workflow", flow_id):
		frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

	source_doc = frappe.get_doc("CRM Workflow", flow_id)
	new_doc = frappe.copy_doc(source_doc)
	new_doc.title = _("Copy of {0}").format(source_doc.title)
	new_doc.status = "Draft"
	new_doc.current_version = 1
	new_doc.published_by = None
	new_doc.published_at = None
	new_doc.created_by = frappe.session.user
	new_doc.insert(ignore_permissions=True)

	return new_doc.as_dict()


@frappe.whitelist()
def deactivate_flow(flow_id=None):
	"""Deactivate/reactivate flow"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")

	if not frappe.db.exists("CRM Workflow", flow_id):
		frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

	doc = frappe.get_doc("CRM Workflow", flow_id)
	if doc.status == "Deactivated":
		doc.status = "Published" if doc.published_at else "Draft"
	else:
		doc.status = "Deactivated"
	doc.save(ignore_permissions=True)

	return doc.as_dict()


@frappe.whitelist()
def validate_flow(flow_id=None):
	"""Server-side flow validation wrapper"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")

	if not frappe.db.exists("CRM Workflow", flow_id):
		frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

	flow_json = frappe.db.get_value("CRM Workflow", flow_id, "flow_json")
	return validate_flow_logic(flow_json)


@frappe.whitelist()
def get_flow_versions(flow_id=None):
	"""Get version history for a flow"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")

	versions = frappe.get_all(
		"CRM Workflow Version",
		fields=["name", "flow", "version", "status", "change_note", "published_by", "published_at"],
		filters={"flow": flow_id},
		order_by="version desc"
	)
	return versions


@frappe.whitelist()
def rollback_flow(flow_id=None, version=None):
	"""Rollback to previous version (creates new draft)"""
	if not flow_id:
		flow_id = frappe.form_dict.get("flow_id")
	if not version:
		version = frappe.form_dict.get("version")

	if not frappe.db.exists("CRM Workflow", flow_id):
		frappe.throw(_("Workflow {0} not found").format(flow_id), frappe.DoesNotExistError)

	version_records = frappe.get_all(
		"CRM Workflow Version",
		filters={"flow": flow_id, "version": int(version)},
		fields=["flow_json"]
	)
	if not version_records:
		frappe.throw(_("Version {0} not found for this flow").format(version))

	flow_json = version_records[0].flow_json

	doc = frappe.get_doc("CRM Workflow", flow_id)
	doc.flow_json = flow_json
	doc.status = "Draft"
	doc.save(ignore_permissions=True)

	return doc.as_dict()


def validate_flow_logic(flow_json_str):
	"""Core validation logic matching frontend graph rules"""
	errors = []
	warnings = []

	if not flow_json_str:
		errors.append({
			"type": "error",
			"code": "NO_NODES",
			"message": _("Flow has no nodes. Add at least a Start and End node.")
		})
		return {"valid": False, "errors": errors, "warnings": warnings}

	try:
		flow_data = json.loads(flow_json_str) if isinstance(flow_json_str, str) else flow_json_str
	except Exception:
		errors.append({
			"type": "error",
			"code": "INVALID_JSON",
			"message": _("Failed to parse flow definition JSON.")
		})
		return {"valid": False, "errors": errors, "warnings": warnings}

	nodes = flow_data.get("nodes", [])
	edges = flow_data.get("edges", [])

	if not nodes:
		errors.append({
			"type": "error",
			"code": "NO_NODES",
			"message": _("Flow has no nodes. Add at least a Start and End node.")
		})
		return {"valid": False, "errors": errors, "warnings": warnings}

	# Check for exactly one StartNode
	start_nodes = [n for n in nodes if n.get("data", {}).get("nodeType") == "StartNode"]
	if not start_nodes:
		errors.append({
			"type": "error",
			"code": "NO_START",
			"message": _("Flow must have exactly one Start node.")
		})
	elif len(start_nodes) > 1:
		errors.append({
			"type": "error",
			"code": "MULTIPLE_STARTS",
			"message": _("Flow must have exactly one Start node. Found {0}.").format(len(start_nodes)),
			"nodeIds": [n.get("id") for n in start_nodes]
		})

	# Check for at least one EndNode
	end_nodes = [n for n in nodes if n.get("data", {}).get("nodeType") == "EndNode"]
	if not end_nodes:
		errors.append({
			"type": "error",
			"code": "NO_END",
			"message": _("Flow must have at least one End node.")
		})

	# Check for disconnected nodes
	connected_node_ids = set()
	for edge in edges:
		if edge.get("source"):
			connected_node_ids.add(edge.get("source"))
		if edge.get("target"):
			connected_node_ids.add(edge.get("target"))

	if len(nodes) > 1:
		for node in nodes:
			n_id = node.get("id")
			if n_id not in connected_node_ids:
				errors.append({
					"type": "error",
					"code": "DISCONNECTED",
					"message": _("Node \"{0}\" is not connected to any other node.").format(node.get("data", {}).get("label") or n_id),
					"nodeIds": [n_id]
				})

	# Check reachability from Start
	if len(start_nodes) == 1:
		reachable = get_reachable_nodes(start_nodes[0].get("id"), edges)
		for node in nodes:
			n_id = node.get("id")
			if n_id not in reachable and node.get("data", {}).get("nodeType") != "StartNode":
				warnings.append({
					"type": "warning",
					"code": "UNREACHABLE",
					"message": _("Node \"{0}\" is not reachable from the Start node.").format(node.get("data", {}).get("label") or n_id),
					"nodeIds": [n_id]
				})

	return {
		"valid": len(errors) == 0,
		"errors": errors,
		"warnings": warnings
	}


def get_reachable_nodes(start_id, edges):
	"""BFS reachability check"""
	reachable = {start_id}
	queue = [start_id]

	while queue:
		node_id = queue.pop(0)
		outgoing = [e for e in edges if e.get("source") == node_id]
		for edge in outgoing:
			target = edge.get("target")
			if target and target not in reachable:
				reachable.add(target)
				queue.append(target)

	return reachable


@frappe.whitelist()
def get_form_config_templates(doctype_target="CRM Credit Application"):
	"""Get reusable form configuration templates"""
	templates = frappe.get_all(
		"CRM Workflow Form Config",
		fields=["name", "title", "doctype_target", "is_template", "description", "sections", "fields", "validation_rules"],
		filters={"doctype_target": doctype_target, "is_template": 1},
		order_by="title asc"
	)
	return templates


@frappe.whitelist()
def save_form_config_template(title, doctype_target, sections, fields, validation_rules=None, description=None, template_id=None):
	"""Create or update a reusable form config template"""
	if not title:
		frappe.throw(_("Title is required"))

	if template_id and template_id != "new":
		if not frappe.db.exists("CRM Workflow Form Config", template_id):
			frappe.throw(_("Form configuration template {0} not found").format(template_id), frappe.DoesNotExistError)
		doc = frappe.get_doc("CRM Workflow Form Config", template_id)
	else:
		doc = frappe.new_doc("CRM Workflow Form Config")
		doc.is_template = 1

	doc.title = title
	doc.doctype_target = doctype_target or "CRM Credit Application"
	doc.sections = sections if isinstance(sections, str) else json.dumps(sections)
	doc.fields = fields if isinstance(fields, str) else json.dumps(fields)
	if validation_rules:
		doc.validation_rules = validation_rules if isinstance(validation_rules, str) else json.dumps(validation_rules)
	doc.description = description or ""
	doc.save(ignore_permissions=True)

	return doc.as_dict()
