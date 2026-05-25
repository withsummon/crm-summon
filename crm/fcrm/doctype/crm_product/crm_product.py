# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

from frappe.model.document import Document


class CRMProduct(Document):
	def validate(self):
		if not self.product_name:
			self.product_name = self.product_code
		else:
			self.product_name = self.product_name.strip()
		if not self.status:
			self.status = "Draft"
		if not self.version:
			self.version = 1
