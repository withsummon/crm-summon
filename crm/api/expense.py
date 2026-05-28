import frappe
from frappe.query_builder import Order


@frappe.whitelist()
def list_expenses(limit=50):
    if not frappe.db.table_exists("CRM Expense Entry"):
        return []
    Expense = frappe.qb.DocType("CRM Expense Entry")
    rows = (
        frappe.qb.from_(Expense)
        .select(Expense.name, Expense.category, Expense.description, Expense.amount,
                Expense.expense_date, Expense.status, Expense.notes, Expense.creation)
        .where(Expense.rm == frappe.session.user)
        .orderby("expense_date", order=Order.desc)
        .limit(limit)
    ).run(as_dict=True)
    return rows


@frappe.whitelist()
def create_expense(category, description, amount, expense_date, notes=None):
    doc = frappe.get_doc({
        "doctype": "CRM Expense Entry",
        "rm": frappe.session.user,
        "category": category,
        "description": description,
        "amount": float(amount),
        "expense_date": expense_date,
        "status": "Pending",
        "notes": notes or "",
    })
    doc.insert(ignore_permissions=True)
    return doc.as_dict()


@frappe.whitelist()
def list_mileage_trips(limit=50):
    if not frappe.db.table_exists("CRM Mileage Trip"):
        return []
    Trip = frappe.qb.DocType("CRM Mileage Trip")
    rows = (
        frappe.qb.from_(Trip)
        .select(Trip.name, Trip.start_location, Trip.end_location,
                Trip.distance_km, Trip.trip_date, Trip.cost, Trip.notes, Trip.creation)
        .where(Trip.rm == frappe.session.user)
        .orderby("trip_date", order=Order.desc)
        .limit(limit)
    ).run(as_dict=True)
    return rows


@frappe.whitelist()
def create_mileage_trip(start_location, end_location, distance_km, trip_date, notes=None):
    rate_per_km = 4500
    cost = float(distance_km) * rate_per_km
    doc = frappe.get_doc({
        "doctype": "CRM Mileage Trip",
        "rm": frappe.session.user,
        "start_location": start_location,
        "end_location": end_location,
        "distance_km": float(distance_km),
        "trip_date": trip_date,
        "cost": cost,
        "notes": notes or "",
    })
    doc.insert(ignore_permissions=True)
    return doc.as_dict()
