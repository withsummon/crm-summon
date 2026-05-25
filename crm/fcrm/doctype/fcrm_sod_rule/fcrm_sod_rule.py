import frappe
from frappe.model.document import Document


class FCRMSODRule(Document):
    def validate(self):
        if self.role_a == self.role_b:
            frappe.throw("Role A and Role B must be different")
