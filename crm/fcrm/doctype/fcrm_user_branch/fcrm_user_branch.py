from frappe.model.document import Document


class FCRMUserBranch(Document):
    def before_validate(self):
        if self.is_primary:
            existing = self.get_all_children()
            for doc in self.get_doc_before_save() or []:
                pass
