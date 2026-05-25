import frappe
from frappe import _
from frappe.utils import now_datetime, nowdate, getdate
from pydantic import BaseModel
from typing import Optional


# ─── Role Definitions (matching Excel 15_RBAC Section A) ───

FCRM_ROLES = {
    "FCRM Super Admin": {
        "description": "Full system access, tenant management, min 2FA required",
        "is_saas_role": 0,
    },
    "FCRM Director": {
        "description": "Strategic view + final approvals, override authority, executive dashboard",
        "is_saas_role": 0,
    },
    "FCRM Credit Analyst": {
        "description": "Credit module access, CRUD applications/spreading/memo, no disbursement rights",
        "is_saas_role": 0,
    },
    "FCRM RM": {
        "description": "CRM + customer access, lead/opportunity CRUD, submit applications, limited to own branch + assigned customers",
        "is_saas_role": 0,
    },
    "FCRM Collection Officer": {
        "description": "Collection module access, view overdue accounts, log calls/visits/PTPs, limited to assigned accounts",
        "is_saas_role": 0,
    },
    "FCRM Legal Officer": {
        "description": "Agreement + collateral access, manage legal docs, trigger litigation, no financial approval",
        "is_saas_role": 0,
    },
    "FCRM Operations": {
        "description": "Disbursement + ops module, document handling, verification checklists, no credit decision rights",
        "is_saas_role": 0,
    },
    "FCRM Committee Member": {
        "description": "Approval interface, vote (Approve/Reject/Abstain), add notes, cannot edit application data",
        "is_saas_role": 0,
    },
    "FCRM Customer": {
        "description": "Self-service portal access, view own applications/facilities only, upload documents, make payments",
        "is_saas_role": 0,
    },
}


# ─── Permission Matrix Defaults (Excel 15_RBAC Section B) ───
# Maps FCRM roles -> CRM doctypes -> CRUD permissions

PERMISSION_MATRIX = {
    "FCRM Super Admin": {
        "default": {"read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1, "import": 1, "share": 1, "print": 1, "email": 1},
    },
    "FCRM Director": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0, "report": 1, "export": 1, "share": 0, "print": 1, "email": 1},
        "CRM Credit Application": {"read": 1, "write": 1, "create": 0, "delete": 0, "submit": 1, "report": 1, "export": 1},
    },
    "FCRM Credit Analyst": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0, "report": 1, "export": 1},
        "CRM Credit Application": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1},
        "CRM Credit Analysis Artifact": {"read": 1, "write": 1, "create": 1, "delete": 1},
        "CRM Financial Statement": {"read": 1, "write": 1, "create": 1, "delete": 1},
        "CRM Risk Profile": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "CRM Collateral": {"read": 1, "write": 0, "create": 0, "delete": 0},
    },
    "FCRM RM": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0, "report": 1},
        "CRM Lead": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Deal": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Contact": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Organization": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Customer 360": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Credit Application": {"read": 1, "write": 1, "create": 1, "delete": 0, "submit": 1},
    },
    "FCRM Collection Officer": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "CRM Lead": {"read": 1, "write": 1, "create": 0, "delete": 0},
        "CRM Call Log": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Task": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Site Visit": {"read": 1, "write": 1, "create": 1, "delete": 0},
    },
    "FCRM Legal Officer": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "CRM Collateral": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Customer Document": {"read": 1, "write": 1, "create": 1, "delete": 0},
        "CRM Credit Facility": {"read": 1, "write": 0, "create": 0, "delete": 0},
    },
    "FCRM Operations": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "CRM Credit Facility": {"read": 1, "write": 1, "create": 0, "delete": 0},
        "CRM Customer Document": {"read": 1, "write": 1, "create": 0, "delete": 0},
        "CRM Credit Application": {"read": 1, "write": 1, "create": 0, "delete": 0},
    },
    "FCRM Committee Member": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "CRM Credit Application": {"read": 1, "write": 0, "create": 0, "delete": 0},
    },
    "FCRM Customer": {
        "default": {"read": 1, "write": 0, "create": 0, "delete": 0},
        "CRM Lead": {"read": 1, "write": 0, "create": 1, "delete": 0},
        "CRM Credit Application": {"read": 1, "write": 0, "create": 0, "delete": 0},
    },
}


# ─── Permission Helper Functions ───

def get_user_fcrm_roles(user: str | None = None) -> list[str]:
    """Get FCRM-specific roles for a user."""
    if not user:
        user = frappe.session.user
    roles = frappe.get_roles(user)
    return [r for r in roles if r.startswith("FCRM")]


def has_fcrm_role(user: str | None = None) -> bool:
    """Check if user has any FCRM role."""
    return len(get_user_fcrm_roles(user)) > 0


def get_user_branches(user: str | None = None) -> list[dict]:
    """Get branches assigned to a user via FCRM User Branch."""
    if not user:
        user = frappe.session.user
    return frappe.db.get_all(
        "FCRM User Branch",
        filters={"user": user, "is_active": 1},
        fields=["branch", "branch_name", "is_primary"],
    )


def get_user_primary_branch(user: str | None = None) -> str | None:
    """Get user's primary branch."""
    branches = get_user_branches(user)
    primary = [b for b in branches if b.get("is_primary")]
    if primary:
        return primary[0]["branch"]
    return branches[0]["branch"] if branches else None


def get_branch_filter_condition(doctype: str) -> str:
    """Generate SQL condition for branch-level filtering."""
    user = frappe.session.user
    if user == "Administrator":
        return ""

    fcrm_roles = get_user_fcrm_roles(user)
    if not fcrm_roles:
        return ""

    # Super Admin and Director see all
    if any(r in ("FCRM Super Admin", "FCRM Director") for r in fcrm_roles):
        return ""

    branches = get_user_branches(user)
    if not branches:
        return "1=0"

    branch_names = [frappe.db.escape(b["branch"]) for b in branches]
    branch_field = _get_branch_field(doctype)
    if branch_field:
        return f"`tab{doctype}`.`{branch_field}` in ({','.join(branch_names)})"
    return ""


def _get_branch_field(doctype: str) -> str | None:
    """Map doctype to their branch/cabang field name."""
    branch_fields = {
        "CRM Lead": "custom_branch",
        "CRM Deal": "custom_branch",
        "CRM Credit Application": "branch",
        "CRM Credit Facility": "branch",
        "CRM Organization": "custom_branch",
        "CRM Customer 360": "custom_branch",
        "Contact": "custom_branch",
    }
    return branch_fields.get(doctype)


def get_field_permissions(doctype: str, role: str | None = None) -> list[dict]:
    """Get field-level permission rules for a doctype & role."""
    filters = {"target_doctype": doctype, "enabled": 1}
    if role:
        filters["role"] = role

    rules = frappe.db.get_all(
        "FCRM Field Permission",
        filters=filters,
        fields=["fieldname", "permission_type", "mask_type", "mask_character"],
    )
    return rules or []


def mask_field_value(value: str, mask_type: str, mask_char: str = "*") -> str:
    """Mask sensitive field values based on mask type."""
    if not value:
        return value
    s = str(value)
    if mask_type == "Full":
        return mask_char * len(s)
    elif mask_type == "Prefix":
        return mask_char * min(4, len(s)) + s[4:]
    elif mask_type == "Suffix":
        return s[:-4] + mask_char * min(4, len(s))
    elif mask_type == "Middle":
        if len(s) <= 4:
            return mask_char * len(s)
        half = len(s) // 2
        return s[:half//2] + mask_char * (len(s) - half) + s[-(half//2):]
    return value


def check_sod_conflict(user: str, new_role: str) -> list[dict]:
    """Check if adding a role would create an SoD conflict."""
    user_roles = set(frappe.get_roles(user))
    conflicts = frappe.db.get_all(
        "FCRM SOD Rule",
        filters={"enabled": 1},
        fields=["role_a", "role_b", "conflict_type", "description"],
    )
    results = []
    for c in conflicts:
        if (new_role == c["role_a"] and c["role_b"] in user_roles) or \
           (new_role == c["role_b"] and c["role_a"] in user_roles):
            results.append(c)
    return results


def get_approval_matrix(doctype: str, amount: float, role: str, branch: str | None = None) -> list[dict]:
    """Get matching approval authority matrix rules."""
    filters = {
        "enabled": 1,
        "document_type": doctype,
        "approver_role": role,
        "min_amount": ["<=", amount],
        "max_amount": [">=", amount],
    }
    if branch:
        filters["branch"] = ["in", [branch, ""]]

    rules = frappe.db.get_all(
        "FCRM Approval Matrix",
        filters=filters,
        fields=["approval_sequence", "approver_user", "approval_type",
                "parallel_approval", "quorum_rule", "can_override"],
        order_by="approval_sequence asc",
    )
    return rules or []


def log_permission_audit(event_type: str, **kwargs):
    """Create a permission audit log entry."""
    doc = frappe.get_doc({
        "doctype": "FCRM Permission Audit",
        "user": frappe.session.user,
        "event_type": event_type,
        "timestamp": now_datetime(),
        "ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else "",
        **kwargs,
    })
    doc.insert(ignore_permissions=True)


def on_user_branch_after_insert(doc, method):
    """Hook: log audit + create User Permission when branch assigned."""
    log_permission_audit("Branch Assignment",
        target_doctype="FCRM User Branch",
        target_docname=doc.name,
        user=doc.user,
        new_value=f"Branch: {doc.branch}",
        details=f"Assigned user {doc.user} to branch {doc.branch}")


def on_user_branch_on_trash(doc, method):
    """Hook: log audit + cleanup User Permission when branch removed."""
    perms = frappe.db.get_all("User Permission", {
        "user": doc.user,
        "allow": "FCRM Branch",
        "for_value": doc.branch,
    })
    for p in perms:
        frappe.delete_doc("User Permission", p.name, ignore_permissions=True)

    log_permission_audit("Branch Assignment",
        target_doctype="FCRM User Branch",
        user=doc.user,
        new_value=f"Removed User {doc.user} from Branch {doc.branch}")


def validate_sod_on_save(doc, method):
    """Validate SoD rules when user saves sensitive CRM documents."""
    user = frappe.session.user
    if user == "Administrator":
        return

    fcrm_roles = get_user_fcrm_roles(user)
    if len(fcrm_roles) < 2:
        return

    conflicts = frappe.db.get_all(
        "FCRM SOD Rule",
        filters={"enabled": 1},
        fields=["role_a", "role_b", "conflict_type", "description"],
    )

    user_role_set = set(fcrm_roles)
    for c in conflicts:
        if c["role_a"] in user_role_set and c["role_b"] in user_role_set:
            desc = c["description"] or f"{c['role_a']} & {c['role_b']}"
            frappe.throw(_(
                f"SoD Conflict: {desc}. "
                "You cannot perform this action with your current role assignment."
            ))


@frappe.whitelist()
def get_field_permissions_map(doctype: str):
    """Get field permission map for current user & doctype (frontend consumption)."""
    user = frappe.session.user
    if user == "Administrator":
        return {}

    fcrm_roles = get_user_fcrm_roles(user)
    if not fcrm_roles:
        return {}

    rules = frappe.db.get_all(
        "FCRM Field Permission",
        filters={
            "target_doctype": doctype,
            "enabled": 1,
            "role": ["in", fcrm_roles],
        },
        fields=["fieldname", "permission_type", "mask_type", "mask_character"],
    )

    result = {}
    for r in rules:
        fn = r["fieldname"]
        if fn not in result:
            result[fn] = {"permission_type": r["permission_type"], "mask_type": r.get("mask_type")}
        else:
            # Most restrictive wins: Hidden > ReadOnly > ReadWrite
            current = result[fn]["permission_type"]
            incoming = r["permission_type"]
            priority = {"Hidden": 0, "ReadOnly": 1, "ReadWrite": 2, "Masked": 3}
            if priority.get(incoming, 99) < priority.get(current, 99):
                result[fn] = {"permission_type": incoming, "mask_type": r.get("mask_type")}

    return result


# ─── Whitelisted API Methods ───

@frappe.whitelist()
def get_roles():
    """Get all FCRM custom roles plus standard roles."""
    standard = frappe.db.get_all(
        "Role",
        fields=["name", "is_custom", "disabled"],
        order_by="name asc",
    )
    return standard


@frappe.whitelist()
def create_fcrm_role(role_name: str, description: str = ""):
    """Create a new FCRM role."""
    if not role_name.startswith("FCRM "):
        role_name = f"FCRM {role_name}"

    if frappe.db.exists("Role", role_name):
        frappe.throw(_(f"Role {role_name} already exists"))

    role = frappe.get_doc({
        "doctype": "Role",
        "role_name": role_name,
        "description": description or f"{role_name} role for BNI CRM",
        "is_custom": 1,
    })
    role.insert(ignore_permissions=True)

    log_permission_audit("Permission Created",
        target_doctype="Role",
        target_docname=role_name,
        details=f"Created new role: {role_name}")

    return role


@frappe.whitelist()
def seed_default_roles():
    """Create all 9 FCRM default roles with permissions."""
    created = []
    for role_name, info in FCRM_ROLES.items():
        if not frappe.db.exists("Role", role_name):
            role = frappe.get_doc({
                "doctype": "Role",
                "role_name": role_name,
                "description": info["description"],
                "is_custom": 1,
            })
            role.insert(ignore_permissions=True)
            created.append(role_name)

    # Apply default permission matrix
    _apply_permission_matrix()

    return {"created": created, "total": len(created)}


def _apply_permission_matrix():
    """Apply the default permission matrix to CRM doctypes."""
    from frappe.core.page.permission_manager.permission_manager import get_permissions, update

    for role_name, doctype_perms in PERMISSION_MATRIX.items():
        if not frappe.db.exists("Role", role_name):
            continue

        default_perms = doctype_perms.pop("default", {})
        for doctype, perms in doctype_perms.items():
            if not frappe.db.exists("DocType", doctype):
                continue

            merged = {**default_perms, **perms}
            for perm_type, value in merged.items():
                try:
                    update(doctype, role_name, 0, perm_type, str(value))
                except Exception:
                    pass


@frappe.whitelist()
def get_user_permissions(user: str | None = None):
    """Get all User Permission records for a user."""
    filters = {}
    if user:
        filters["user"] = user

    return frappe.db.get_all(
        "User Permission",
        filters=filters,
        fields=["name", "user", "allow", "for_value", "applicable_for",
                "is_default", "creation", "modified"],
        order_by="user asc",
        limit_page_length=500,
    )


@frappe.whitelist()
def get_branches():
    """Get all branches (active)."""
    return frappe.db.get_all(
        "FCRM Branch",
        filters={"is_active": 1},
        fields=["name", "branch_code", "branch_name", "branch_type", "region", "city"],
        order_by="branch_name asc",
    )


@frappe.whitelist()
def get_user_branch_assignments(user: str | None = None):
    """Get branch assignments for a user."""
    filters = {"is_active": 1}
    if user:
        filters["user"] = user

    return frappe.db.get_all(
        "FCRM User Branch",
        filters=filters,
        fields=["name", "user", "full_name", "branch", "branch_name", "is_primary", "is_active"],
        order_by="user asc",
    )


@frappe.whitelist()
def assign_user_branch(user: str, branch: str, is_primary: bool = False):
    """Assign a user to a branch."""
    existing = frappe.db.get_value("FCRM User Branch",
        {"user": user, "branch": branch, "is_active": 1}, "name")

    if existing:
        return {"message": _("Already assigned"), "name": existing}

    doc = frappe.get_doc({
        "doctype": "FCRM User Branch",
        "user": user,
        "branch": branch,
        "is_primary": is_primary,
        "is_active": 1,
    })
    doc.insert(ignore_permissions=True)

    # Also create Frappe User Permission for automatic filtering
    _ensure_user_permission(user, "FCRM Branch", branch)

    log_permission_audit("Branch Assignment",
        target_doctype="FCRM User Branch",
        new_value=f"User {user} -> Branch {branch}",
        details=f"Primary: {is_primary}")

    return doc


@frappe.whitelist()
def remove_user_branch(name: str):
    """Remove a user-branch assignment."""
    doc = frappe.get_doc("FCRM User Branch", name)
    user = doc.user
    branch = doc.branch
    frappe.delete_doc("FCRM User Branch", name, ignore_permissions=True)

    # Clean up User Permission
    perms = frappe.db.get_all("User Permission", {
        "user": user,
        "allow": "FCRM Branch",
        "for_value": branch,
    })
    for p in perms:
        frappe.delete_doc("User Permission", p.name, ignore_permissions=True)

    log_permission_audit("Branch Assignment",
        target_doctype="FCRM User Branch",
        new_value=f"Removed User {user} from Branch {branch}")

    return {"message": _("Assignment removed")}


def _ensure_user_permission(user: str, allow: str, for_value: str):
    """Ensure a Frappe User Permission exists for automatic filtering."""
    if not frappe.db.exists("User Permission", {
        "user": user,
        "allow": allow,
        "for_value": for_value,
    }):
        doc = frappe.get_doc({
            "doctype": "User Permission",
            "user": user,
            "allow": allow,
            "for_value": for_value,
            "is_default": 0,
        })
        doc.insert(ignore_permissions=True)


@frappe.whitelist()
def get_approval_matrices(doctype: str | None = None, role: str | None = None):
    """Get approval authority matrix rules."""
    filters = {}
    if doctype:
        filters["document_type"] = doctype
    if role:
        filters["approver_role"] = role

    return frappe.db.get_all(
        "FCRM Approval Matrix",
        filters=filters,
    fields=["name", "approval_type", "document_type", "min_amount", "max_amount",
            "approver_role", "approver_user", "approval_sequence",
            "approval_flow", "branch", "enabled", "effective_from", "effective_to"],
        order_by="approval_type asc, approval_sequence asc",
        limit_page_length=500,
    )


@frappe.whitelist()
def get_field_permissions_list(doctype: str | None = None, role: str | None = None):
    """Get field permission rules."""
    filters = {}
    if doctype:
        filters["target_doctype"] = doctype
    if role:
        filters["role"] = role

    return frappe.db.get_all(
        "FCRM Field Permission",
        filters=filters,
        fields=["name", "target_doctype", "fieldname", "field_label", "role",
                "permission_type", "mask_type", "enabled", "effective_from", "effective_to"],
        order_by="target_doctype asc, fieldname asc",
        limit_page_length=500,
    )


@frappe.whitelist()
def get_delegations(user: str | None = None, status: str = "Active"):
    """Get delegation records."""
    filters = {"status": status}
    if user:
        filters["delegator"] = user

    return frappe.db.get_all(
        "FCRM Delegation",
        filters=filters,
        fields=["name", "delegator", "delegate", "role", "from_date", "to_date",
                "status", "reason", "max_amount", "branch_only"],
        order_by="from_date desc",
        limit_page_length=200,
    )


@frappe.whitelist()
def get_sod_rules():
    """Get Segregation of Duties rules."""
    return frappe.db.get_all(
        "FCRM SOD Rule",
        filters={"enabled": 1},
        fields=["name", "role_a", "role_b", "conflict_type", "description", "allow_override"],
        order_by="conflict_type asc",
    )


@frappe.whitelist()
def check_sod_for_user(user: str, role: str):
    """Check SoD conflict for a user+role combination."""
    conflicts = check_sod_conflict(user, role)
    return {
        "has_conflict": len(conflicts) > 0,
        "conflicts": conflicts,
    }


@frappe.whitelist()
def create_jit_request(role: str, reason: str, duration_hours: int = 4):
    """Request Just-in-Time elevated access."""
    doc = frappe.get_doc({
        "doctype": "FCRM JIT Request",
        "requested_role": role,
        "reason": reason,
        "duration_hours": duration_hours,
        "status": "Pending",
    })
    doc.insert(ignore_permissions=True)

    log_permission_audit("JIT Requested",
        target_doctype="FCRM JIT Request",
        target_docname=doc.name,
        role=role,
        details=f"JIT access requested for role {role} for {duration_hours}h")

    return doc


@frappe.whitelist()
def approve_jit_request(name: str):
    """Approve a pending JIT request."""
    frappe.only_for(["System Manager", "Sales Manager"])

    doc = frappe.get_doc("FCRM JIT Request", name)
    if doc.status != "Pending":
        frappe.throw(_("Request is not in Pending status"))

    doc.status = "Approved"
    doc.save(ignore_permissions=True)

    log_permission_audit("JIT Approved",
        target_doctype="FCRM JIT Request",
        target_docname=name,
        role=doc.requested_role,
        details=f"JIT approved by {frappe.session.user}")

    return doc


@frappe.whitelist()
def reject_jit_request(name: str, reason: str = ""):
    """Reject a pending JIT request."""
    frappe.only_for(["System Manager", "Sales Manager"])

    doc = frappe.get_doc("FCRM JIT Request", name)
    doc.status = "Rejected"
    doc.save(ignore_permissions=True)

    return doc


@frappe.whitelist()
def get_jit_requests(status: str | None = None):
    """Get JIT access requests."""
    filters = {}
    if status:
        filters["status"] = status

    return frappe.db.get_all(
        "FCRM JIT Request",
        filters=filters,
        fields=["name", "requester", "requested_role", "reason", "duration_hours",
                "status", "approved_by", "approved_at", "expires_at", "creation"],
        order_by="creation desc",
        limit_page_length=200,
    )


@frappe.whitelist()
def get_permission_audit_log(user: str | None = None,
                              event_type: str | None = None,
                              from_date: str | None = None,
                              to_date: str | None = None):
    """Get permission audit log with filters."""
    filters = {}
    if user:
        filters["user"] = user
    if event_type:
        filters["event_type"] = event_type

    log = frappe.db.get_all(
        "FCRM Permission Audit",
        filters=filters,
        fields=["name", "user", "event_type", "target_doctype", "target_docname",
                "role", "old_value", "new_value", "ip_address", "timestamp"],
        order_by="timestamp desc",
        limit_page_length=500,
    )
    return log


@frappe.whitelist()
def get_user_roles_detailed(user: str):
    """Get detailed user info with roles and branch assignments."""
    user_doc = frappe.get_doc("User", user)
    roles = [r.role for r in user_doc.roles]
    branches = get_user_branches(user)

    return {
        "user": user,
        "full_name": user_doc.full_name,
        "email": user_doc.email,
        "enabled": user_doc.enabled,
        "user_type": user_doc.user_type,
        "roles": roles,
        "fcrm_roles": [r for r in roles if r.startswith("FCRM")],
        "branches": branches,
        "last_active": user_doc.last_active,
        "last_login": user_doc.last_login,
    }


@frappe.whitelist()
def get_permission_summary():
    """Get a summary of all permissions for dashboard."""
    total_roles = frappe.db.count("Role", {"disabled": 0})
    fcrm_roles = len(frappe.db.get_all("Role", {"role_name": ["like", "FCRM %"], "disabled": 0}))
    total_users = frappe.db.count("User", {"enabled": 1, "name": ["not in", ["Guest", "Administrator"]]})
    total_user_perms = frappe.db.count("User Permission")
    total_branches = frappe.db.count("FCRM Branch", {"is_active": 1})
    total_branch_assignments = frappe.db.count("FCRM User Branch", {"is_active": 1})
    total_approval_rules = frappe.db.count("FCRM Approval Matrix", {"enabled": 1})
    total_field_perms = frappe.db.count("FCRM Field Permission", {"enabled": 1})
    total_delegations = frappe.db.count("FCRM Delegation", {"status": "Active"})

    pending_jit = frappe.db.count("FCRM JIT Request", {"status": "Pending"})
    recent_audit = frappe.db.get_all(
        "FCRM Permission Audit",
        fields=["user", "event_type", "timestamp", "target_doctype"],
        order_by="timestamp desc",
        limit=10,
    )

    return {
        "roles": {"total": total_roles, "fcrm": fcrm_roles},
        "users": total_users,
        "user_permissions": total_user_perms,
        "branches": {"total": total_branches, "assignments": total_branch_assignments},
        "approval_rules": total_approval_rules,
        "field_permissions": total_field_perms,
        "delegations": total_delegations,
        "pending_jit_requests": pending_jit,
        "recent_audit_entries": recent_audit,
    }


@frappe.whitelist()
def permission_query_conditions(user: str | None = None):
	"""Hook for Frappe's permission_query_conditions to enforce branch isolation."""
	if not user:
		user = frappe.session.user
	if user == "Administrator":
		return ""

	fcrm_roles = get_user_fcrm_roles(user)
	if not fcrm_roles:
		return ""

	if any(r in ("FCRM Super Admin", "FCRM Director") for r in fcrm_roles):
		return ""

	branches = get_user_branches(user)
	if not branches:
		return "1=0"

	branch_names = [frappe.db.escape(b["branch"]) for b in branches]
	clauses = []
	for dt, field in [
		("CRM Lead", "custom_branch"),
		("CRM Deal", "custom_branch"),
		("CRM Credit Application", "branch"),
		("CRM Credit Facility", "branch"),
		("CRM Organization", "custom_branch"),
		("CRM Customer 360", "custom_branch"),
		("Contact", "custom_branch"),
	]:
		clauses.append(f"`tab{dt}`.`{field}` in ({','.join(branch_names)})")
	return " or ".join(clauses)


@frappe.whitelist()
def has_permission(
    doctype: str | None = None,
    docname: str | None = None,
    ptype: str | None = "read",
    doc=None,
    user: str | None = None,
    debug: bool = False,
) -> bool:
    """Check if user has specific permission on a document.
    Called either via the API (doctype+docname) or by Frappe's permission
    system (doc)."""
    if doc is not None:
        if not isinstance(doc, str):
            doctype = doc.doctype
            docname = doc.name
    if not doctype or not docname:
        return True
    user = user or frappe.session.user
    if user == "Administrator":
        return True
    return frappe.has_permission(doctype, ptype or "read", doc=docname)


def expire_jit_requests():
    """Scheduled job: expire JIT requests whose time is up."""
    expired = frappe.db.get_all(
        "FCRM JIT Request",
        filters={
            "status": "Approved",
            "expires_at": ["<=", now_datetime()],
        },
        pluck="name",
    )
    for name in expired:
        doc = frappe.get_doc("FCRM JIT Request", name)
        doc.status = "Expired"
        doc.save(ignore_permissions=True)
        log_permission_audit("JIT Expired",
            target_doctype="FCRM JIT Request",
            target_docname=name,
            details="JIT access expired automatically")


def expire_delegations():
    """Scheduled job: expire delegations past their end date."""
    expired = frappe.db.get_all(
        "FCRM Delegation",
        filters={
            "status": "Active",
            "to_date": ["<=", now_datetime()],
        },
        pluck="name",
    )
    for name in expired:
        doc = frappe.get_doc("FCRM Delegation", name)
        doc.status = "Expired"
        doc.save(ignore_permissions=True)
        log_permission_audit("Delegation Created",
            target_doctype="FCRM Delegation",
            target_docname=name,
            details="Delegation expired automatically")
