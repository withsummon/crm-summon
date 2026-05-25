# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

from crm.fcrm.doctype.crm_notification.crm_notification import notify_user


class TestCRMNotification(FrappeTestCase):
	def setUp(self):
		self.notif_user = "test_notif@example.com"
		if not frappe.db.exists("User", self.notif_user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": self.notif_user,
					"first_name": "Notification Test",
					"send_welcome_email": 0,
				}
			).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()

	def test_notify_user_creates_notification_doc(self):
		notify_user(
			{
				"owner": "Administrator",
				"assigned_to": self.notif_user,
				"notification_type": "Assignment",
				"message": "<p>You have been assigned a new lead</p>",
				"notification_text": "New Lead Assignment",
			}
		)
		self.assertTrue(
			frappe.db.exists(
				"CRM Notification",
				{
					"to_user": self.notif_user,
					"type": "Assignment",
					"notification_text": "New Lead Assignment",
				},
			)
		)

	def test_notify_user_skips_when_owner_is_assigned_to(self):
		"""Should skip when owner and assigned_to are the same user."""
		notify_user(
			{
				"owner": "Administrator",
				"assigned_to": "Administrator",
				"notification_type": "Assignment",
				"message": "Self-assigned, should not create notification",
				"notification_text": "Self Assignment",
			}
		)
		self.assertFalse(
			frappe.db.exists(
				"CRM Notification",
				{"to_user": "Administrator", "notification_text": "Self Assignment"},
			)
		)

	def test_notify_user_reference_fields_are_optional(self):
		"""Should create notification without reference doctype/docname fields."""
		notify_user(
			{
				"owner": "Administrator",
				"assigned_to": self.notif_user,
				"notification_type": "Task",
				"message": "<p>Simple notification without reference</p>",
				"notification_text": "No Ref Notification",
			}
		)
		names = frappe.get_all(
			"CRM Notification",
			{"to_user": self.notif_user, "notification_text": "No Ref Notification"},
			pluck="name",
		)
		self.assertEqual(len(names), 1)
		notif = frappe.get_doc("CRM Notification", names[0])
		self.assertIsNone(notif.reference_doctype)
		self.assertIsNone(notif.reference_name)
