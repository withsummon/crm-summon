import json
import frappe
from frappe import _
from frappe.utils import now_datetime, flt, add_to_date


def get_doctype_ready(doctype):
	try:
		return frappe.db.table_exists(doctype)
	except Exception:
		return False


def get_target_doctype(docname):
	"""Identify the dynamic doctype of a document by name"""
	if not docname:
		return "CRM Credit Application"
	docname_str = str(docname)
	if docname_str.startswith("CRM-LEAD-") or docname_str.startswith("CRM-LEAD"):
		return "CRM Lead"
	if docname_str.startswith("CRM-DEAL-") or docname_str.startswith("CRM-DEAL"):
		return "CRM Deal"
	if docname_str.startswith("CRM-CA-") or docname_str.startswith("CRM-CA"):
		return "CRM Credit Application"
	
	# Check existence in DB
	for dt in ["CRM Credit Application", "CRM Lead", "CRM Deal"]:
		try:
			if frappe.db.exists(dt, docname):
				return dt
		except Exception:
			pass
	return "CRM Credit Application"


def start_flow_execution(application_id):
	"""Initialize credit flow execution for an application (or generic doctype document)"""
	if not get_doctype_ready("CRM Workflow"):
		return None

	# Check for running execution
	existing = frappe.get_all(
		"CRM Workflow Execution",
		filters={"application": application_id, "status": "Running"},
		limit=1
	)
	if existing:
		return frappe.get_doc("CRM Workflow Execution", existing[0].name)

	doctype = get_target_doctype(application_id)
	app = frappe.get_doc(doctype, application_id)

	# Check if a workflow was manually assigned via credit_flow field
	assigned_workflow = getattr(app, "credit_flow", None) or getattr(app, "workflow", None)
	if assigned_workflow:
		flow_doc = frappe.get_doc("CRM Workflow", assigned_workflow)
		if flow_doc.status == "Published":
			matched_flows = [{
				"name": flow_doc.name,
				"current_version": flow_doc.current_version,
				"flow_json": flow_doc.flow_json,
			}]
		else:
			matched_flows = []
	else:
		# Find matching published flow
		filters = {"status": "Published"}

		facility_type = getattr(app, "facility_type", None) or getattr(app, "product_type", None)
		if facility_type:
			filters["product_type"] = facility_type

		borrower_type = getattr(app, "borrower_type", None) or getattr(app, "applicant_persona", None)
		if borrower_type:
			filters["applicant_persona"] = ["in", ["Any", borrower_type]]

		is_pre_approved = getattr(app, "is_pre_approved", 0)
		filters["is_pre_approved"] = 1 if is_pre_approved else 0

		matched_flows = frappe.get_all(
			"CRM Workflow",
			filters=filters,
			fields=["name", "current_version", "flow_json"],
			order_by="modified desc",
			limit=1
		)

		if not matched_flows:
			matched_flows = frappe.get_all(
				"CRM Workflow",
				filters={"status": "Published", "applicant_persona": "Any"},
				fields=["name", "current_version", "flow_json"],
				order_by="modified desc",
				limit=1
			)

	if not matched_flows:
		return None

	flow_info = matched_flows[0]

	# Create execution doc
	exec_doc = frappe.new_doc("CRM Workflow Execution")
	exec_doc.flow = flow_info["name"]
	exec_doc.flow_version = flow_info["current_version"]
	exec_doc.flow_version_json = flow_info["flow_json"]
	exec_doc.document_type = doctype
	exec_doc.application = application_id
	exec_doc.status = "Running"
	exec_doc.started_at = now_datetime()
	exec_doc.completed_nodes = json.dumps([])
	exec_doc.skipped_nodes = json.dumps([])
	
	exec_doc.execution_data = json.dumps({
		"borrower_type": getattr(app, "borrower_type", "Individual"),
		"requested_amount": flt(getattr(app, "requested_amount", getattr(app, "deal_value", getattr(app, "annual_revenue", 0)))),
		"status": app.status,
		"risk_grade": getattr(app, "risk_grade", "C")
	})
	exec_doc.insert(ignore_permissions=True)

	try:
		flow_data = json.loads(flow_info["flow_json"])
	except Exception:
		flow_data = {"nodes": [], "edges": []}

	nodes = flow_data.get("nodes", [])
	start_node = next((n for n in nodes if n.get("data", {}).get("nodeType") == "StartNode"), None)

	if start_node:
		create_audit_log(exec_doc.name, start_node.get("id"), "StartNode", start_node.get("data", {}).get("label"), "node_enter")
		
		exec_doc.current_node = start_node.get("id")
		exec_doc.current_node_type = "StartNode"
		exec_doc.current_node_label = start_node.get("data", {}).get("label") or "Start"
		exec_doc.save(ignore_permissions=True)

		activate_next_node(exec_doc, start_node.get("id"), "default")
	
	return exec_doc


def activate_next_node(exec_doc, source_node_id, source_handle="default"):
	"""Transition along the outgoing edge from source_node_id through source_handle"""
	try:
		flow_data = json.loads(exec_doc.flow_version_json) if isinstance(exec_doc.flow_version_json, str) else exec_doc.flow_version_json
	except Exception:
		return

	nodes = flow_data.get("nodes", [])
	edges = flow_data.get("edges", [])

	edge = next((e for e in edges if e.get("source") == source_node_id and e.get("sourceHandle", "default") == source_handle), None)
	if not edge:
		outgoing = [e for e in edges if e.get("source") == source_node_id]
		if len(outgoing) == 1:
			edge = outgoing[0]

	if not edge:
		return

	target_node_id = edge.get("target")
	target_node = next((n for n in nodes if n.get("id") == target_node_id), None)
	if not target_node:
		return

	node_type = target_node.get("data", {}).get("nodeType")
	node_label = target_node.get("data", {}).get("label") or node_type
	config = target_node.get("data", {}).get("config", {})

	# Log source node exit & target node entry
	create_audit_log(exec_doc.name, source_node_id, "", "", "node_exit")
	create_audit_log(exec_doc.name, target_node_id, node_type, node_label, "node_enter")

	# Close previous Node State if active
	active_states = frappe.get_all(
		"CRM Workflow Node State",
		filters={"execution": exec_doc.name, "node_id": source_node_id, "status": "active"},
		limit=1
	)
	if active_states:
		state_doc = frappe.get_doc("CRM Workflow Node State", active_states[0].name)
		state_doc.status = "completed"
		state_doc.exited_at = now_datetime()
		state_doc.save(ignore_permissions=True)

	# Handle cascading delegation resolver for assignee
	assigned_user = None
	assigned_role = None
	if node_type in ["AssignmentNode", "ApprovalNode", "CommitteeNode"]:
		role_target = config.get("assignTo") or config.get("approvers", [{}])[0].get("role") if config.get("approvers") else None
		user_target = config.get("approvers", [{}])[0].get("user") if config.get("approvers") else None
		
		# Resolve delegation & HR availability checker
		assigned_user, resolved_via = resolve_delegation(user_target, role_target)
		assigned_role = role_target

		if resolved_via:
			# Log delegation event in Audit Log
			create_audit_log(
				exec_doc.name,
				target_node_id,
				node_type,
				node_label,
				"delegation",
				original_assignee=user_target or role_target,
				delegated_to=assigned_user,
				reason=_("HR Availability check - substitution enqueued.")
			)

	# Save target node state
	new_state = frappe.new_doc("CRM Workflow Node State")
	new_state.execution = exec_doc.name
	new_state.node_id = target_node_id
	new_state.node_type = node_type
	new_state.status = "active"
	new_state.entered_at = now_datetime()
	new_state.assigned_to = assigned_user
	new_state.assigned_role = assigned_role
	
	if config.get("timeoutHours"):
		new_state.sla_deadline = add_to_date(now_datetime(), hours=flt(config.get("timeoutHours")))
	new_state.insert(ignore_permissions=True)

	# Update Execution status & Current Node
	exec_doc.current_node = target_node_id
	exec_doc.current_node_type = node_type
	exec_doc.current_node_label = node_label
	
	completed_list = json.loads(exec_doc.completed_nodes or "[]")
	if source_node_id not in completed_list:
		completed_list.append(source_node_id)
	exec_doc.completed_nodes = json.dumps(completed_list)
	exec_doc.save(ignore_permissions=True)

	# Sync back to target document dynamically
	doctype = get_target_doctype(exec_doc.application)
	app = frappe.get_doc(doctype, exec_doc.application)
	
	if app.meta.has_field("workflow"): app.workflow = exec_doc.flow
	if app.meta.has_field("workflow_version"): app.workflow_version = exec_doc.flow_version
	if app.meta.has_field("workflow_execution"): app.workflow_execution = exec_doc.name
	if app.meta.has_field("current_flow_node"): app.current_flow_node = target_node_id
	if app.meta.has_field("current_flow_node_label"): app.current_flow_node_label = node_label

	if node_type == "FormNode":
		config_val = json.dumps({
			"sections": config.get("sections", []),
			"fields": config.get("fields", []),
			"availableActions": config.get("availableActions", ["save_draft", "submit"])
		})
		actions_val = json.dumps(config.get("availableActions", ["save_draft", "submit"]))
	elif node_type == "ApprovalNode":
		config_val = json.dumps({
			"sections": [],
			"fields": [],
			"availableActions": config.get("availableActions", ["approve", "reject", "return"])
		})
		actions_val = json.dumps(config.get("availableActions", ["approve", "reject", "return"]))
	else:
		config_val = json.dumps({})
		actions_val = json.dumps([])

	if app.meta.has_field("flow_form_config"): app.flow_form_config = config_val
	if app.meta.has_field("flow_available_actions"): app.flow_available_actions = actions_val

	# Execute immediate automated transitions
	if node_type == "EndNode":
		exec_doc.status = "Completed"
		exec_doc.completed_at = now_datetime()
		exec_doc.save(ignore_permissions=True)

		new_state.status = "completed"
		new_state.exited_at = now_datetime()
		new_state.save(ignore_permissions=True)

		outcome = config.get("outcome", "approved")
		if app.doctype == "CRM Credit Application":
			app.status = "Active" if outcome == "approved" else ("Rejected" if outcome == "rejected" else "Closed")
		elif app.doctype == "CRM Lead":
			app.status = "Won" if outcome == "approved" else "Lost"
		elif app.doctype == "CRM Deal":
			app.status = "Won" if outcome == "approved" else "Lost"
		app.save(ignore_permissions=True)

	elif node_type == "DecisionNode":
		result = evaluate_conditions(exec_doc.application, config.get("conditions", []))
		handle = "true" if result else "false"
		
		new_state.status = "completed"
		new_state.exited_at = now_datetime()
		new_state.action_taken = handle
		new_state.save(ignore_permissions=True)
		
		activate_next_node(exec_doc, target_node_id, handle)

	elif node_type == "SkipNode":
		result = evaluate_conditions(exec_doc.application, config.get("skipConditions", []))
		handle = "skip" if result else "continue"
		
		if result:
			skipped_list = json.loads(exec_doc.skipped_nodes or "[]")
			skipped_list.append(target_node_id)
			exec_doc.skipped_nodes = json.dumps(skipped_list)
			exec_doc.save(ignore_permissions=True)

		new_state.status = "skipped" if result else "completed"
		new_state.exited_at = now_datetime()
		new_state.action_taken = handle
		new_state.save(ignore_permissions=True)
		
		activate_next_node(exec_doc, target_node_id, handle)

	elif node_type == "NotificationNode":
		channels = config.get("channels", ["in_app"])
		create_audit_log(exec_doc.name, target_node_id, "NotificationNode", node_label, "notification_sent", data={"channels": channels})
		
		new_state.status = "completed"
		new_state.exited_at = now_datetime()
		new_state.save(ignore_permissions=True)
		
		activate_next_node(exec_doc, target_node_id, "default")

	elif node_type == "IntegrationNode":
		create_audit_log(exec_doc.name, target_node_id, "IntegrationNode", node_label, "integration_call", data={"endpoint": config.get("endpoint")})
		
		new_state.status = "completed"
		new_state.exited_at = now_datetime()
		new_state.action_taken = "success"
		new_state.save(ignore_permissions=True)
		
		activate_next_node(exec_doc, target_node_id, "success")

	elif node_type == "SLANode":
		new_state.status = "completed"
		new_state.exited_at = now_datetime()
		new_state.save(ignore_permissions=True)
		
		activate_next_node(exec_doc, target_node_id, "on-time")

	app.save(ignore_permissions=True)


def submit_node_action(application_id, action_name, form_data=None, user_id=None, reason=None):
	"""Submit active manual state node action and transition the execution engine forward"""
	exec_records = frappe.get_all(
		"CRM Workflow Execution",
		filters={"application": application_id, "status": "Running"},
		limit=1
	)
	if not exec_records:
		return False

	exec_doc = frappe.get_doc("CRM Workflow Execution", exec_records[0].name)
	active_states = frappe.get_all(
		"CRM Workflow Node State",
		filters={"execution": exec_doc.name, "status": "active"},
		limit=1
	)
	if not active_states:
		return False

	state_doc = frappe.get_doc("CRM Workflow Node State", active_states[0].name)
	user = user_id or frappe.session.user

	# Log action details
	create_audit_log(
		exec_doc.name,
		state_doc.node_id,
		state_doc.node_type,
		exec_doc.current_node_label,
		"action_taken",
		user=user,
		decision="approved" if action_name in ["submit", "approve", "continue"] else ("rejected" if action_name == "reject" else "returned"),
		reason=reason,
		data={"action": action_name}
	)

	# Save captured form data if FormNode
	if state_doc.node_type == "FormNode" and form_data:
		state_doc.form_data = form_data if isinstance(form_data, str) else json.dumps(form_data)
		
		try:
			data = json.loads(form_data) if isinstance(form_data, str) else form_data
			doctype = get_target_doctype(application_id)
			app = frappe.get_doc(doctype, application_id)
			for k, v in data.items():
				if hasattr(app, k) or app.meta.has_field(k):
					app.set(k, v)
			app.save(ignore_permissions=True)
		except Exception:
			pass

	# Handle complex BNI 12-rule approval matrix aggregation
	if state_doc.node_type in ["ApprovalNode", "CommitteeNode"]:
		# Submit individual vote
		vote_doc = frappe.new_doc("CRM Workflow Approval Vote")
		vote_doc.execution = exec_doc.name
		vote_doc.node_id = state_doc.node_id
		vote_doc.approver = user
		vote_doc.decision = "approved" if action_name in ["approve", "submit"] else ("rejected" if action_name == "reject" else "returned")
		vote_doc.reason = reason or ""
		vote_doc.voted_at = now_datetime()
		vote_doc.weight = 1.0
		
		# Set is_delegated flag if voted user is different from assigned_to
		if state_doc.assigned_to and state_doc.assigned_to != user:
			vote_doc.original_approver = state_doc.assigned_to
			vote_doc.is_delegate = 1
		vote_doc.insert(ignore_permissions=True)

		# Evaluate aggregate outcome based on 12-approval rule matrices
		outcome = evaluate_approval_outcome(exec_doc, state_doc.node_id)
		if not outcome:
			# Not yet resolved (e.g. waiting for other parallel voters), do not transition
			return True
		
		handle = outcome
	else:
		# For non-approval stages, advance along matching handles
		handle = "default"
		if action_name == "reject":
			handle = "rejected"
		elif action_name in ["return", "return_to_rm"]:
			handle = "returned"

	state_doc.status = "completed"
	state_doc.exited_at = now_datetime()
	state_doc.action_taken = action_name
	state_doc.save(ignore_permissions=True)

	activate_next_node(exec_doc, state_doc.node_id, handle)
	return True


def evaluate_approval_outcome(exec_doc, node_id):
	"""Evaluate BNI 12-approval rules aggregate vote status"""
	try:
		flow_data = json.loads(exec_doc.flow_version_json) if isinstance(exec_doc.flow_version_json, str) else exec_doc.flow_version_json
		nodes = flow_data.get("nodes", [])
		node = next((n for n in nodes if n.get("id") == node_id), None)
		if not node:
			return "approved"
		
		config = node.get("data", {}).get("config", {})
		approval_type = config.get("approvalType", "single")
	except Exception:
		return "approved"

	# Get all votes cast for this node
	votes = frappe.get_all(
		"CRM Workflow Approval Vote",
		filters={"execution": exec_doc.name, "node_id": node_id},
		fields=["decision", "weight"]
	)

	approved_cnt = len([v for v in votes if v.decision == "approved"])
	rejected_cnt = len([v for v in votes if v.decision == "rejected"])
	returned_cnt = len([v for v in votes if v.decision == "returned"])
	total_votes = len(votes)

	# 1. Single Approver
	if approval_type == "single":
		if approved_cnt >= 1: return "approved"
		if rejected_cnt >= 1: return "rejected"
		if returned_cnt >= 1: return "returned"

	# 2. Sequential & 3. Parallel & 4. AND Gate (requires all)
	elif approval_type in ["sequential", "parallel", "and"]:
		total_required = len(config.get("approvers", [])) or 1
		if rejected_cnt >= 1: return "rejected"
		if returned_cnt >= 1: return "returned"
		if approved_cnt >= total_required: return "approved"

	# 5. OR Gate (any one can approve)
	elif approval_type == "or":
		if approved_cnt >= 1: return "approved"
		if rejected_cnt >= 1: return "rejected"
		if returned_cnt >= 1: return "returned"

	# 6. N-of-M voting
	elif approval_type == "n_of_m":
		n_req = int(config.get("nRequired") or 1)
		m_tot = int(config.get("mTotal") or 1)
		if approved_cnt >= n_req: return "approved"
		if rejected_cnt > (m_tot - n_req): return "rejected"
		if returned_cnt >= 1: return "returned"

	# 7. Quorum & Majority / Committee decisions
	elif approval_type in ["quorum", "majority", "committee"]:
		quorum_req = int(config.get("quorumN") or 1)
		if total_votes >= quorum_req:
			# Evaluate majority consensus
			if approved_cnt > (total_votes / 2.0): return "approved"
			if rejected_cnt >= (total_votes / 2.0): return "rejected"
		return None

	# 8. Weighted authority
	elif approval_type == "weighted":
		total_weight = sum([flt(v.weight) for v in votes])
		approved_weight = sum([flt(v.weight) for v in votes if v.decision == "approved"])
		rejected_weight = sum([flt(v.weight) for v in votes if v.decision == "rejected"])
		
		if approved_weight > (total_weight / 2.0): return "approved"
		if rejected_weight >= (total_weight / 2.0): return "rejected"

	# Fallback amount/risk grades tiers (simulated dynamically)
	elif approval_type in ["amount_based", "risk_based"]:
		if approved_cnt >= 1: return "approved"
		if rejected_cnt >= 1: return "rejected"
		if returned_cnt >= 1: return "returned"

	return None


def resolve_delegation(user_id, role_name):
	"""Delegation handler resolving substitution when user is on leave or resigned"""
	if not user_id:
		return None, False

	# Verify user availability status
	is_available = True
	try:
		# standard user profile HR check
		user_doc = frappe.get_doc("User", user_id)
		# Checks if user is suspended, disabled, or on holiday
		if not user_doc.enabled:
			is_available = False
	except Exception:
		pass

	# Check active HR leave block
	if is_available:
		active_leaves = frappe.get_all(
			"CRM Holiday", # fallback holiday/leave lists in FCRM Branch
			filters={"owner": user_id, "is_active": 1},
			limit=1
		)
		if active_leaves:
			is_available = False

	if is_available:
		return user_id, False

	# Locate visual CRM delegation rules matching original user/role
	delegations = frappe.get_all(
		"CRM Workflow Delegation Rule",
		filters={"original_user": user_id, "is_active": 1},
		fields=["name", "delegate_user", "max_depth"],
		limit=1
	)
	
	if not delegations and role_name:
		delegations = frappe.get_all(
			"CRM Workflow Delegation Rule",
			filters={"original_role": role_name, "is_active": 1},
			fields=["name", "delegate_user", "max_depth"],
			limit=1
		)

	if delegations:
		delegate = delegations[0]
		# Cascade check up to maximum depth of 3
		depth = int(delegate.max_depth or 3)
		resolved, _ = resolve_delegation_chain(delegate.delegate_user, depth - 1)
		return resolved, True

	# If no delegate configured, return default system Administrator override
	return "Administrator", True


def resolve_delegation_chain(user_id, depth):
	if depth <= 0:
		return user_id, False
	# Recursive validator
	resolved, chain = resolve_delegation(user_id, None)
	return resolved, chain


def evaluate_conditions(application_id, condition_list):
	"""Evaluate logic rules against credit application data values"""
	if not condition_list:
		return True

	doctype = get_target_doctype(application_id)
	app = frappe.get_doc(doctype, application_id)
	
	overall_match = True
	for idx, rule in enumerate(condition_list):
		field = rule.get("field")
		if not field:
			continue

		operator = rule.get("operator", "==")
		rule_value = rule.get("value")
		join = rule.get("join", "AND")

		app_val = app.get(field)
		
		match = False
		try:
			if operator == "==":
				match = str(app_val) == str(rule_value)
			elif operator == "!=":
				match = str(app_val) != str(rule_value)
			elif operator == ">":
				match = flt(app_val) > flt(rule_value)
			elif operator == ">=":
				match = flt(app_val) >= flt(rule_value)
			elif operator == "<":
				match = flt(app_val) < flt(rule_value)
			elif operator == "<=":
				match = flt(app_val) <= flt(rule_value)
			elif operator == "contains":
				match = str(rule_value).lower() in str(app_val).lower()
			elif operator == "is_empty":
				match = not app_val
			elif operator == "is_not_empty":
				match = bool(app_val)
		except Exception:
			match = False

		if idx == 0:
			overall_match = match
		else:
			if join == "AND":
				overall_match = overall_match and match
			else:
				overall_match = overall_match or match

	return overall_match


def create_audit_log(execution_id, node_id, node_type, node_label, event_type, user=None, original_assignee=None, delegated_to=None, decision=None, reason=None, data=None):
	"""Create a standardized execution audit log entry"""
	log = frappe.new_doc("CRM Workflow Audit Log")
	log.execution = execution_id
	log.node_id = node_id
	log.node_type = node_type
	log.node_label = node_label or node_id
	log.event_type = event_type
	log.timestamp = now_datetime()
	log.user = user or frappe.session.user
	log.original_assignee = original_assignee
	log.delegated_to = delegated_to
	log.decision = decision
	log.reason = reason
	if data:
		log.data = data if isinstance(data, str) else json.dumps(data)
	log.insert(ignore_permissions=True)


@frappe.whitelist()
def process_sla_background_job():
	"""Background job running every 5 minutes to detect SLA breaches and execute escalations"""
	if not get_doctype_ready("CRM Workflow Node State"):
		return

	# Retrieve active states where deadline has passed and not breached
	active_breached_states = frappe.get_all(
		"CRM Workflow Node State",
		filters={
			"status": "active",
			"sla_deadline": ["<", now_datetime()],
			"sla_status": ["!="], # in Python, we will query where it's not breached
		},
		fields=["name", "execution", "node_id", "node_type", "assigned_to", "assigned_role", "sla_status"]
	)

	# filter out breached manually to be safe or refine query
	active_breached_states = [s for s in active_breached_states if s.sla_status != "breached"]

	for state_info in active_breached_states:
		try:
			state = frappe.get_doc("CRM Workflow Node State", state_info.name)
			exec_doc = frappe.get_doc("CRM Workflow Execution", state.execution)
			
			# Parse config from frozen version JSON
			flow_data = {}
			if exec_doc.flow_version_json:
				try:
					flow_data = json.loads(exec_doc.flow_version_json) if isinstance(exec_doc.flow_version_json, str) else exec_doc.flow_version_json
				except Exception:
					pass
			
			nodes = flow_data.get("nodes", [])
			node = next((n for n in nodes if n.get("id") == state.node_id), None)
			config = {}
			if node:
				config = node.get("data", {}).get("config", {})

			# Check SLA/Escalation fields
			escalation_target = config.get("escalationTarget")
			escalation_action = config.get("escalationAction") or "notify"
			
			# 1. Update SLA Status to breached
			state.sla_status = "breached"
			state.save(ignore_permissions=True)

			# 2. Log standard SLA Breach Event
			create_audit_log(
				execution_id=state.execution,
				node_id=state.node_id,
				node_type=state.node_type,
				node_label=exec_doc.current_node_label,
				event_type="sla_breach",
				reason=f"SLA deadline breached. Action: {escalation_action}. Target: {escalation_target or 'None'}"
			)

			# 3. Process Escalation Action
			if escalation_action in ["reassign", "escalate"] and escalation_target:
				old_assignee = state.assigned_to
				old_role = state.assigned_role
				
				# If target is a User
				if frappe.db.exists("User", escalation_target):
					state.assigned_to = escalation_target
					state.assigned_role = None
				else:
					# Target is a Role
					state.assigned_role = escalation_target
					# Resolve default delegate for this role if any
					resolved_user, _ = resolve_delegation(None, escalation_target)
					state.assigned_to = resolved_user or "Administrator"
				
				state.save(ignore_permissions=True)
				
				# Log escalation delegation event
				create_audit_log(
					execution_id=state.execution,
					node_id=state.node_id,
					node_type=state.node_type,
					node_label=exec_doc.current_node_label,
					event_type="delegation",
					original_assignee=old_assignee or old_role,
					delegated_to=state.assigned_to,
					reason=f"SLA reassignment escalation to {escalation_target}"
				)

				# Also notify supervisor/assignee via system/in-app alert
				try:
					if get_doctype_ready("fcrm_note"):
						note = frappe.new_doc("fcrm_note")
						note.title = f"Escalated: {exec_doc.current_node_label} SLA Breach"
						note.content = f"Credit Application {exec_doc.application} has been escalated to you due to SLA breach on stage {exec_doc.current_node_label}."
						note.owner = state.assigned_to
						note.insert(ignore_permissions=True)
				except Exception:
					pass

			elif escalation_action == "notify" and escalation_target:
				# Log notification dispatched
				create_audit_log(
					execution_id=state.execution,
					node_id=state.node_id,
					node_type=state.node_type,
					node_label=exec_doc.current_node_label,
					event_type="notification_sent",
					reason=f"SLA breach notification dispatched to supervisor {escalation_target}",
					data={"escalation_target": escalation_target}
				)
				
				try:
					if get_doctype_ready("fcrm_note"):
						note = frappe.new_doc("fcrm_note")
						note.title = f"Alert: {exec_doc.current_node_label} SLA Breach"
						note.content = f"Credit Application {exec_doc.application} has breached its SLA at stage {exec_doc.current_node_label}."
						note.owner = escalation_target if frappe.db.exists("User", escalation_target) else "Administrator"
						note.insert(ignore_permissions=True)
				except Exception:
					pass

			frappe.db.commit()
		except Exception:
			frappe.log_error(frappe.get_traceback(), "process_sla_background_job.breach_state")
			frappe.db.rollback()
