import frappe
from frappe.model.document import Document


class CRMCommitteeItem(Document):
	def validate(self):
		if not self.status:
			self.status = "Pending"
		if self.application and not self.applicant_name:
			borrower_name = frappe.db.get_value(
				"CRM Credit Application", self.application, "borrower_name"
			)
			if borrower_name:
				self.applicant_name = borrower_name
