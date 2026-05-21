from frappe.model.document import Document


class CRMCreditFacility(Document):
	def validate(self):
		if self.limit_amount and self.outstanding is not None:
			self.ltv_percent = (self.outstanding / self.limit_amount) * 100

