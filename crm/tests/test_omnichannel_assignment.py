import unittest
from unittest.mock import patch

from crm.api.omnichannel import bulk_update_conversations


class TestOmnichannelAssignment(unittest.TestCase):
	@patch("crm.api.omnichannel.frappe")
	def test_assign_to_me_uses_authenticated_user(self, frappe):
		frappe.session.user = "Administrator"
		frappe.db.exists.return_value = True
		frappe.get_doc.return_value.name = "CRM-OMNI-CONV-1"

		result = bulk_update_conversations.__wrapped__(["CRM-OMNI-CONV-1"], "assign", "Guest")

		self.assertEqual(result["updated"], ["CRM-OMNI-CONV-1"])
		self.assertEqual(frappe.get_doc.return_value.assigned_to, "Administrator")
		frappe.get_doc.return_value.save.assert_called_once_with(ignore_permissions=True)
