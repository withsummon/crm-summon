from frappe.model.document import Document


class FCRMBranch(Document):
    def before_validate(self):
        if self.branch_code:
            self.branch_code = self.branch_code.upper().strip()
