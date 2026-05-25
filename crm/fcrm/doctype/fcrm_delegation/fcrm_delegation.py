import frappe
from frappe.model.document import Document


class FCRMDelegation(Document):
    def validate(self):
        if self.delegator == self.delegate:
            frappe.throw("Delegator and Delegate cannot be the same user")

        if self.from_date and self.to_date and self.from_date >= self.to_date:
            frappe.throw("To Date must be after From Date")

    def on_update(self):
        if self.status == "Active":
            self._create_user_permissions()
        elif self.status == "Revoked":
            self._remove_user_permissions()

    def _create_user_permissions(self):
        if not frappe.db.exists("User Permission", {
            "user": self.delegate,
            "allow": "Role",
            "for_value": self.role,
        }):
            doc = frappe.get_doc({
                "doctype": "User Permission",
                "user": self.delegate,
                "allow": "Role",
                "for_value": self.role,
                "applicable_for": "",
                "is_default": 0,
            })
            doc.insert(ignore_permissions=True)

    def _remove_user_permissions(self):
        perms = frappe.db.get_all("User Permission", {
            "user": self.delegate,
            "allow": "Role",
            "for_value": self.role,
        })
        for p in perms:
            frappe.delete_doc("User Permission", p.name, ignore_permissions=True)
