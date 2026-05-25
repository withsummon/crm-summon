from frappe.model.document import Document


class CRMCommittee(Document):
	def validate(self):
		if self.quorum_pct is None:
			self.quorum_pct = 60
		if self.quorum_pct < 1:
			self.quorum_pct = 1
		if self.quorum_pct > 100:
			self.quorum_pct = 100
		if not self.majority_rule:
			self.majority_rule = "Simple"
