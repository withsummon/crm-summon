from frappe.model.document import Document


class CRMCreditApplication(Document):
	def validate(self):
		if not self.borrower_name and self.borrower:
			self.borrower_name = self.borrower
		if not self.borrower_type:
			self.borrower_type = "Individual"
		if not self.status:
			self.status = "Draft"
		else:
			status_aliases = {
				"In Progress": "Credit Analysis",
				"Pending Review": "Document Review",
				"Submitted": "Committee Approval",
				"Approved": "Active",
				"Cancelled": "Closed",
			}
			self.status = status_aliases.get(self.status, self.status)

		# Auto-initiate visual credit flow execution on first save
		if not self.credit_flow_execution:
			from crm.utils.workflow_engine import start_flow_execution
			try:
				start_flow_execution(self.name)
			except Exception:
				pass
