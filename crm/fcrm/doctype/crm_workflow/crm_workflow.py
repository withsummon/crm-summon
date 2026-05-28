import frappe
from frappe.model.document import Document


class CRMWorkflow(Document):
	def validate(self):
		if not self.status:
			self.status = "Draft"
		if not self.current_version:
			self.current_version = 1
		if not self.created_by:
			self.created_by = frappe.session.user
