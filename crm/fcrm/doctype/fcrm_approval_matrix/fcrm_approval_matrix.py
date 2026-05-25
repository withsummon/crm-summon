import frappe
from frappe.model.document import Document


class FCRMApprovalMatrix(Document):
    def validate(self):
        if self.min_amount and self.max_amount and self.min_amount > self.max_amount:
            frappe.throw("Min Amount cannot be greater than Max Amount")
