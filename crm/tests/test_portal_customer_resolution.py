import unittest
from unittest.mock import patch

from crm.api.portal import _resolve_customer


class TestPortalCustomerResolution(unittest.TestCase):
	@patch("crm.api.portal.frappe")
	def test_staff_preview_uses_customer_with_active_facilities(self, frappe):
		frappe.get_roles.return_value = ["System Manager"]
		frappe.db.table_exists.return_value = True
		frappe.db.sql.return_value = [{"customer": "PT Astra Group Conglomerate"}]

		self.assertEqual(_resolve_customer(), "PT Astra Group Conglomerate")
		frappe.db.sql.assert_called_once()

	@patch("crm.api.portal.frappe")
	def test_customer_account_cannot_switch_to_another_customer(self, frappe):
		frappe.get_roles.return_value = ["Customer"]
		frappe.session.user = "customer@example.com"
		frappe.db.table_exists.return_value = True
		frappe.get_meta.return_value.has_field.return_value = True
		frappe.get_all.return_value = ["Own Customer"]

		self.assertEqual(_resolve_customer("Another Customer"), "Own Customer")
		frappe.db.sql.assert_not_called()
