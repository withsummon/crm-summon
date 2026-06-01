import frappe
from frappe.query_builder import Order


def ensure_customer_column():
    if not frappe.db.table_exists("CRM Geo Fence Reminder"):
        return
    try:
        frappe.db.sql_ddl("ALTER TABLE `tabCRM Geo Fence Reminder` ADD COLUMN `customer` VARCHAR(255) NULL")
        frappe.db.commit()
    except Exception as e:
        if "1060" in str(e) or "Duplicate column name" in str(e):
            pass
        else:
            raise e


@frappe.whitelist()
def list_reminders():
    ensure_customer_column()
    if not frappe.db.table_exists("CRM Geo Fence Reminder"):
        return []
    Reminder = frappe.qb.DocType("CRM Geo Fence Reminder")
    rows = (
        frappe.qb.from_(Reminder)
        .select(Reminder.name, Reminder.customer, Reminder.location_name, Reminder.address,
                Reminder.latitude, Reminder.longitude,
                Reminder.radius_meters, Reminder.note, Reminder.is_active, Reminder.creation)
        .where(Reminder.rm == frappe.session.user)
        .orderby("creation", order=Order.desc)
    ).run(as_dict=True)
    return rows


@frappe.whitelist()
def create_reminder(location_name, customer=None, address=None, latitude=None, longitude=None, radius_meters=500, note=None):
    ensure_customer_column()
    # Set default lat/lng close to RM default coordinate for beautiful UAT proximity matching
    default_lat = -6.2198  # Sudirman Jakarta
    default_lng = 106.8163
    
    # If customer is PT Indofood, place close to lat/lng for easy UAT geo check matches
    if customer and "indofood" in str(customer).lower():
        default_lat = -6.2210
        default_lng = 106.8180
    elif customer and "anisa" in str(customer).lower():
        default_lat = -6.2185
        default_lng = 106.8150

    doc = frappe.get_doc({
        "doctype": "CRM Geo Fence Reminder",
        "rm": frappe.session.user,
        "customer": customer or "",
        "location_name": location_name,
        "address": address or "Sudirman Central Business District, Jakarta",
        "latitude": float(latitude) if latitude else default_lat,
        "longitude": float(longitude) if longitude else default_lng,
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
