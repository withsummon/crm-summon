import json

import frappe
from frappe.query_builder import Order


@frappe.whitelist()
def get_notifications():
	Notification = frappe.qb.DocType("CRM Notification")
	query = (
		frappe.qb.from_(Notification)
		.select("*")
		.where(Notification.to_user == frappe.session.user)
		.where(Notification.archived == 0)
		.orderby("creation", order=Order.desc)
	)
	notifications = query.run(as_dict=True)

	_notifications = []
	for notification in notifications:
		_notifications.append(
			{
				"name": notification.name,
				"creation": notification.creation,
				"from_user": {
					"name": notification.from_user,
					"full_name": frappe.get_value("User", notification.from_user, "full_name"),
				},
				"type": notification.type,
				"to_user": notification.to_user,
				"read": notification.read,
				"hash": get_hash(notification),
				"notification_text": notification.notification_text,
				"message": notification.message,
				"notification_type_doctype": notification.notification_type_doctype,
				"notification_type_doc": notification.notification_type_doc,
				"comment": notification.comment,
				"reference_doctype": notification.reference_doctype,
				"reference_name": notification.reference_name,
				"route_name": get_route_name(notification),
			}
		)

	return _notifications


@frappe.whitelist()
def delete_notification(name):
	if not name or not frappe.db.exists("CRM Notification", name):
		frappe.throw("Notification not found")
	frappe.delete_doc("CRM Notification", name, ignore_permissions=True)
	return {"status": "ok"}


@frappe.whitelist()
def archive_all_notifications():
	user = frappe.session.user
	frappe.db.sql(
		"""UPDATE `tabCRM Notification`
		SET `read` = 1, `archived` = 1
		WHERE `to_user` = %s""",
		(user,),
	)
	frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def seed_notification_sample_data():
	user = frappe.session.user
	samples = [
		("Mention", f"<b>{user}</b> mentioned you in a comment"),
		("Task", "A new task <b>Follow-up call</b> has been assigned to you"),
		("Assignment", "<b>Lead-001</b> has been assigned to you"),
		("WhatsApp", "You have a new WhatsApp message from <b>+628123456789</b>"),
		("Mention", "You were mentioned in deal <b>DEAL-002</b>"),
		("Task", "Task <b>Prepare proposal</b> is due tomorrow"),
		("Assignment", "<b>Deal-003</b> has been assigned to you"),
		("WhatsApp", "New WhatsApp template received"),
		("Mention", "Comment reply on <b>Lead-004</b>"),
		("Task", "Task <b>Send reminder</b> updated"),
	]
	created = 0
	for notif_type, message in samples:
		doc = frappe.get_doc({
			"doctype": "CRM Notification",
			"type": notif_type,
			"to_user": user,
			"from_user": "Administrator",
			"message": message,
			"read": 0,
			"archived": 0,
		})
		doc.insert(ignore_permissions=True)
		created += 1
	return {"created": created}


@frappe.whitelist()
def mark_as_read(user: str | None = None, doc: str | None = None):
	user = user or frappe.session.user
	filters = {"to_user": user, "read": False}
	or_filters = []
	if doc:
		or_filters = [
			{"name": doc},
			{"comment": doc},
			{"notification_type_doc": doc},
		]
	names = [n.name for n in frappe.get_all("CRM Notification", filters=filters, or_filters=or_filters)]
	if names:
		frappe.db.set_value("CRM Notification", {"name": ["in", names]}, "read", True)
		frappe.db.commit()
	return {"status": "ok"}


def get_hash(notification):
	_hash = ""
	if notification.type == "Mention" and notification.notification_type_doc:
		_hash = "#" + notification.notification_type_doc

	if notification.type == "WhatsApp":
		_hash = "#whatsapp"

	if notification.type == "Assignment" and notification.notification_type_doctype == "CRM Task":
		_hash = "#tasks"
		if "has been removed by" in notification.message:
			_hash = ""
	return _hash


def get_route_name(notification):
	routes = {
		"CRM Deal": "Deal",
		"CRM Lead": "Lead",
		"CRM Task": "Tasks",
	}
	return routes.get(notification.reference_doctype or notification.notification_type_doctype)


@frappe.whitelist()
def save_preferences(preferences):
	if isinstance(preferences, str):
		preferences = json.loads(preferences)
	user = frappe.session.user
	for pref in preferences:
		name = frappe.db.get_value("CRM Notification Preference", {"user": user, "type": pref.get("type")}, "name")
		if name:
			frappe.db.set_value("CRM Notification Preference", name, {
				"email": 1 if pref.get("email") else 0,
				"in_app": 1 if pref.get("in_app") else 0,
			})
		else:
			frappe.get_doc({
				"doctype": "CRM Notification Preference",
				"user": user,
				"type": pref.get("type"),
				"email": 1 if pref.get("email") else 0,
				"in_app": 1 if pref.get("in_app") else 0,
			}).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def get_preferences():
	user = frappe.session.user
	rows = frappe.get_all("CRM Notification Preference", filters={"user": user}, fields=["type", "email", "in_app"])
	return {r["type"]: r for r in rows}
