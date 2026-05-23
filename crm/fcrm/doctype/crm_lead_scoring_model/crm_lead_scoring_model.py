import frappe
from frappe import _
from frappe.model.document import Document


class CRMLeadScoringModel(Document):
	def validate(self):
		if self.is_active:
			active_models = frappe.get_all(
				"CRM Lead Scoring Model",
				filters={"is_active": 1, "name": ["!=", self.name]},
				pluck="name",
			)
			if active_models:
				frappe.throw(_("Only one lead scoring model can be active at a time."))
