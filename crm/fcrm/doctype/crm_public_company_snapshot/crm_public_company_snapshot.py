from frappe.model.document import Document


class CRMPublicCompanySnapshot(Document):
	def validate(self):
		if self.ticker:
			self.ticker = self.ticker.upper().strip()
		if not self.source:
			self.source = "IDX XBRL / PEFINDO"

