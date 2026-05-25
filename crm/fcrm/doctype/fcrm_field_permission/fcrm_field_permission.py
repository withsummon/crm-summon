import frappe
from frappe.model.document import Document


class FCRMFieldPermission(Document):
    def validate(self):
        if self.permission_type == "Masked" and not self.mask_type:
            frappe.throw("Mask Type is required when Permission Type is Masked")
