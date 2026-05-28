import json
from datetime import datetime

import frappe
from frappe.query_builder import Order


@frappe.whitelist()
def list_visits(status=None, date_from=None, date_to=None, limit=50):
    Visit = frappe.qb.DocType("CRM Visit Log")
    query = (
        frappe.qb.from_(Visit)
        .select(
            Visit.name,
            Visit.customer,
            Visit.customer_name,
            Visit.rm,
            Visit.visit_date,
            Visit.purpose,
            Visit.status,
            Visit.check_in_time,
            Visit.check_out_time,
            Visit.gps_latitude,
            Visit.gps_longitude,
            Visit.result,
            Visit.creation,
            Visit.modified,
        )
        .where(Visit.rm == frappe.session.user)
        .orderby("visit_date", order=Order.desc)
        .limit(limit)
    )

    if status:
        query = query.where(Visit.status == status)
    if date_from:
        query = query.where(Visit.visit_date >= date_from)
    if date_to:
        query = query.where(Visit.visit_date <= date_to)

    return query.run(as_dict=True)


@frappe.whitelist()
def get_visit(visit_id):
    visit = frappe.get_doc("CRM Visit Log", visit_id)
    photos = frappe.get_all(
        "CRM Visit Log Photo",
        filters={"parent": visit_id},
        fields=["name", "photo", "caption"],
        order_by="idx",
    )
    action_items = frappe.get_all(
        "CRM Visit Action Item",
        filters={"parent": visit_id},
        fields=["name", "description", "due_date", "assignee", "status"],
        order_by="idx",
    )
    visit_dict = visit.as_dict()
    visit_dict["photos"] = photos
    visit_dict["action_items"] = action_items
    return visit_dict


def resolve_or_create_customer(customer_id_or_name):
    if not customer_id_or_name:
        return None
    
    # 1. Exact match by Customer ID (name field)
    if frappe.db.exists("Customer", customer_id_or_name):
        return customer_id_or_name
        
    # 2. Match by customer_name field
    existing_by_name = frappe.db.get_value("Customer", {"customer_name": customer_id_or_name}, "name")
    if existing_by_name:
        return existing_by_name
        
    # 3. Create a new Customer
    try:
        from crm.api.credit import create_customer_360_customer
        cust_dict = create_customer_360_customer(customer_id_or_name)
        return cust_dict.get("name")
    except Exception:
        # Robust fallback
        try:
            from crm.api.credit import _first_leaf_value
            customer_group = _first_leaf_value("Customer Group", "name") or "All Customer Groups"
            territory = _first_leaf_value("Territory", "name") or "All Territories"
        except Exception:
            customer_group = "All Customer Groups"
            territory = "All Territories"
            
        cust_doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_id_or_name,
            "customer_group": customer_group,
            "territory": territory
        })
        cust_doc.insert(ignore_permissions=True)
        return cust_doc.name


@frappe.whitelist()
def create_visit(customer=None, customer_name=None, visit_date=None, purpose=None, notes=None):
    if not customer and not customer_name:
        frappe.throw("customer or customer_name is required")

    resolved_customer = resolve_or_create_customer(customer or customer_name)
    resolved_customer_name = customer_name or customer or ""
    if resolved_customer:
        resolved_customer_name = frappe.db.get_value("Customer", resolved_customer, "customer_name") or resolved_customer_name

    doc = frappe.get_doc({
        "doctype": "CRM Visit Log",
        "customer": resolved_customer,
        "customer_name": resolved_customer_name,
        "rm": frappe.session.user,
        "visit_date": visit_date or datetime.now().strftime("%Y-%m-%d"),
        "purpose": purpose or "",
        "status": "Planned",
        "check_in_notes": notes or "",
    })
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def check_in(visit_id, latitude, longitude, accuracy=None, notes=None):
    doc = frappe.get_doc("CRM Visit Log", visit_id)
    doc.status = "Checked In"
    doc.check_in_time = datetime.now()
    doc.gps_latitude = float(latitude) if latitude else None
    doc.gps_longitude = float(longitude) if longitude else None
    doc.gps_accuracy = float(accuracy) if accuracy else None
    if notes:
        doc.check_in_notes = notes
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def check_out(visit_id, latitude=None, longitude=None, notes=None):
    doc = frappe.get_doc("CRM Visit Log", visit_id)
    doc.status = "Checked Out"
    doc.check_out_time = datetime.now()
    if latitude:
        doc.gps_latitude = float(latitude)
    if longitude:
        doc.gps_longitude = float(longitude)
    if notes:
        doc.check_out_notes = notes
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def cancel_visit(visit_id):
    doc = frappe.get_doc("CRM Visit Log", visit_id)
    doc.status = "Cancelled"
    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def submit_report(visit_id, result, report_notes=None, photos=None, action_items=None):
    doc = frappe.get_doc("CRM Visit Log", visit_id)
    doc.result = result
    if report_notes:
        doc.report_notes = report_notes

    if photos:
        parsed_photos = json.loads(photos) if isinstance(photos, str) else photos
        for photo in parsed_photos:
            doc.append("photos", {
                "photo": photo.get("file_url") or photo.get("photo"),
                "caption": photo.get("caption", ""),
            })

    if action_items:
        parsed_items = json.loads(action_items) if isinstance(action_items, str) else action_items
        for item in parsed_items:
            doc.append("action_items", {
                "description": item.get("description"),
                "due_date": item.get("due_date"),
                "assignee": item.get("assignee"),
                "status": item.get("status", "Open"),
            })

    doc.save(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def get_customers():
    customers = frappe.get_all(
        "Customer",
        fields=["name", "customer_name", "mobile_no", "email_id"],
        limit=100,
    )
    return customers
