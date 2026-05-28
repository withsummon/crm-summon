import frappe
from frappe.query_builder import Order


@frappe.whitelist()
def list_pending():
    """List pending credit applications for mobile approval."""
    if not frappe.db.table_exists("CRM Credit Application"):
        return []
    Application = frappe.qb.DocType("CRM Credit Application")
    rows = (
        frappe.qb.from_(Application)
        .select(
            Application.name,
            Application.borrower,
            Application.borrower_name,
            Application.borrower_type,
            Application.facility_type,
            Application.requested_amount,
            Application.status,
            Application.risk_grade,
            Application.creation,
        )
        .where(Application.status == "Pending Approval")
        .orderby("creation", order=Order.desc)
        .limit(50)
    ).run(as_dict=True)
    return rows


@frappe.whitelist()
def list_history(limit=20):
    """List approved/rejected applications."""
    if not frappe.db.table_exists("CRM Credit Application"):
        return []
    Application = frappe.qb.DocType("CRM Credit Application")
    rows = (
        frappe.qb.from_(Application)
        .select(
            Application.name,
            Application.borrower,
            Application.borrower_name,
            Application.borrower_type,
            Application.facility_type,
            Application.requested_amount,
            Application.status,
            Application.risk_grade,
            Application.creation,
        )
        .where(Application.status.isin(["Approved", "Rejected"]))
        .orderby("modified", order=Order.desc)
        .limit(limit)
    ).run(as_dict=True)
    return rows


@frappe.whitelist()
def approve_application(application_id):
    doc = frappe.get_doc("CRM Credit Application", application_id)
    doc.status = "Approved"
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "status": doc.status}


@frappe.whitelist()
def reject_application(application_id, reason=None):
    doc = frappe.get_doc("CRM Credit Application", application_id)
    doc.status = "Rejected"
    if reason:
        doc.custom_rejection_reason = reason
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "status": doc.status}
