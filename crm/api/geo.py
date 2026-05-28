import frappe
from frappe.query_builder import Order


@frappe.whitelist()
def list_reminders():
    if not frappe.db.table_exists("CRM Geo Fence Reminder"):
        return []
    Reminder = frappe.qb.DocType("CRM Geo Fence Reminder")
    rows = (
        frappe.qb.from_(Reminder)
        .select(Reminder.name, Reminder.location_name, Reminder.address,
                Reminder.latitude, Reminder.longitude,
                Reminder.radius_meters, Reminder.note, Reminder.is_active, Reminder.creation)
        .where(Reminder.rm == frappe.session.user)
        .orderby("creation", order=Order.desc)
    ).run(as_dict=True)
    return rows


@frappe.whitelist()
def create_reminder(location_name, address=None, latitude=None, longitude=None, radius_meters=500, note=None):
    doc = frappe.get_doc({
        "doctype": "CRM Geo Fence Reminder",
        "rm": frappe.session.user,
        "location_name": location_name,
        "address": address or "",
        "latitude": float(latitude) if latitude else None,
        "longitude": float(longitude) if longitude else None,
        "radius_meters": int(radius_meters),
        "note": note or "",
        "is_active": 1,
    })
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def toggle_reminder(reminder_id, is_active):
    doc = frappe.get_doc("CRM Geo Fence Reminder", reminder_id)
    doc.is_active = 1 if is_active in (True, 1, "1", "true") else 0
    doc.save(ignore_permissions=True)
    return {"name": doc.name, "is_active": doc.is_active}


@frappe.whitelist()
def delete_reminder(reminder_id):
    frappe.delete_doc("CRM Geo Fence Reminder", reminder_id, ignore_permissions=True)
    return {"ok": True}
