# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMNotification(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		comment: DF.Link | None
		from_user: DF.Link | None
		message: DF.HTMLEditor | None
		notification_text: DF.Text | None
		notification_type_doc: DF.DynamicLink | None
		notification_type_doctype: DF.Link | None
		read: DF.Check
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		to_user: DF.Link
		type: DF.Literal["Mention", "Task", "Assignment", "WhatsApp"]
	# end: auto-generated types

	def on_update(self):
		if self.to_user:
			frappe.publish_realtime("crm_notification", user=self.to_user)


def notify_user(notification):
	"""
	Notify the assigned user via in-app and email
	"""
	notification = frappe._dict(notification)
	if notification.owner == notification.assigned_to:
		return

	values = frappe._dict(
		doctype="CRM Notification",
		from_user=notification.owner,
		to_user=notification.assigned_to,
		type=notification.notification_type,
		message=notification.message,
		notification_text=notification.notification_text,
		notification_type_doctype=notification.reference_doctype,
		notification_type_doc=notification.reference_docname,
		reference_doctype=notification.redirect_to_doctype,
		reference_name=notification.redirect_to_docname,
	)

	if frappe.db.exists("CRM Notification", values):
		return
	notif_doc = frappe.get_doc(values)
	notif_doc.insert(ignore_permissions=True)

	# Email delivery
	if _should_email(notification.notification_type, notification.assigned_to):
		try:
			frappe.sendmail(
				recipients=notification.assigned_to,
				subject=notification.notification_text or f"CRM {notification.notification_type}",
				message=notification.message or notification.notification_text,
				reference_doctype="CRM Notification",
				reference_name=notif_doc.name,
			)
		except Exception:
			pass


def _should_email(notification_type, user):
	pref = frappe.db.get_value("CRM Notification Preference", {"user": user, "type": notification_type}, "email")
	if pref is not None:
		return bool(pref)
	# Default: email for all except WhatsApp
	return notification_type != "WhatsApp"
