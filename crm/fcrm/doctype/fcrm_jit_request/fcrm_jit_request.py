import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class FCRMJITRequest(Document):
    def before_insert(self):
        self.requester = frappe.session.user

    def after_insert(self):
        if self.status == "Approved":
            self._activate_role()

    def on_update(self):
        before = self.get_doc_before_save()
        if before and before.status != self.status:
            if self.status == "Approved":
                self._activate_role()
            elif self.status in ("Revoked", "Expired"):
                self._deactivate_role()

    def _activate_role(self):
        from frappe.utils import add_to_datetime
        self.expires_at = add_to_datetime(now_datetime(), hours=self.duration_hours or 4)
        self.approved_at = now_datetime()
        self.approved_by = frappe.session.user

        if not frappe.db.exists("Has Role", {"parent": self.requester, "role": self.requested_role}):
            user = frappe.get_doc("User", self.requester)
            user.append("roles", {"role": self.requested_role})
            user.save(ignore_permissions=True)

    def _deactivate_role(self):
        roles = frappe.db.get_all("Has Role", {
            "parent": self.requester,
            "role": self.requested_role,
        })
        for r in roles:
            frappe.db.delete("Has Role", {"name": r.name})
        frappe.db.commit()
