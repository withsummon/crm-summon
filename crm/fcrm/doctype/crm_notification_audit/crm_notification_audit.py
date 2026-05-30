# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class CRMNotificationAudit(Document):
	def before_save(self):
		if not self.is_new():
			frappe.throw("Audit rows are immutable.")
