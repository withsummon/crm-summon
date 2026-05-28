import frappe
from frappe.tests.utils import FrappeTestCase

from crm.api.rbac import (
	check_sod_conflict,
	get_branch_filter_condition,
	get_user_branches,
	log_permission_audit,
	mask_field_value,
	seed_default_roles,
)


class TestRBACBranchIsolation(FrappeTestCase):
	def setUp(self):
		self.test_user = "rbac_branch_test@example.com"
		self.branch = None
		if not frappe.db.exists("User", self.test_user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": self.test_user,
					"first_name": "RBAC Branch Test",
					"send_welcome_email": 0,
					"roles": [{"role": "FCRM RM"}],
				}
			).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()

	def _create_branch(self):
		if not frappe.db.exists("FCRM Branch", "RBAC-TEST-BR"):
			branch = frappe.get_doc(
				{
					"doctype": "FCRM Branch",
					"branch_code": "RBAC-TEST-BR",
					"branch_name": "RBAC Test Branch",
					"branch_type": "Sub Branch",
					"region": "Test Region",
					"city": "Test City",
					"is_active": 1,
				}
			).insert(ignore_permissions=True)
			self.branch = branch.name
		else:
			self.branch = "RBAC-TEST-BR"

	def test_get_user_branches_returns_empty_for_unassigned(self):
		branches = get_user_branches(self.test_user)
		self.assertEqual(branches, [])

	def test_get_user_branches_after_assignment(self):
		self._create_branch()
		frappe.get_doc(
			{
				"doctype": "FCRM User Branch",
				"user": self.test_user,
				"branch": self.branch,
				"branch_name": "RBAC Test Branch",
				"is_primary": 1,
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
		branches = get_user_branches(self.test_user)
		self.assertEqual(len(branches), 1)
		self.assertEqual(branches[0]["branch"], self.branch)
		self.assertEqual(branches[0]["is_primary"], 1)

	def test_branch_filter_condition_returns_empty_for_admin(self):
		frappe.set_user("Administrator")
		condition = get_branch_filter_condition("CRM Lead")
		self.assertEqual(condition, "")

	def test_branch_filter_condition_blocks_when_no_branches(self):
		frappe.set_user(self.test_user)
		condition = get_branch_filter_condition("CRM Lead")
		self.assertEqual(condition, "1=0")

	def test_branch_filter_condition_filters_by_branch(self):
		self._create_branch()
		frappe.set_user(self.test_user)
		frappe.get_doc(
			{
				"doctype": "FCRM User Branch",
				"user": self.test_user,
				"branch": self.branch,
				"branch_name": "RBAC Test Branch",
				"is_primary": 1,
				"is_active": 1,
			}
		).insert(ignore_permissions=True)
		condition = get_branch_filter_condition("CRM Lead")
		self.assertIn("custom_branch", condition)
		self.assertIn(self.branch, condition)


class TestRBACSodConflict(FrappeTestCase):
	def setUp(self):
		self.test_user = "rbac_sod_test@example.com"
		if not frappe.db.exists("User", self.test_user):
			frappe.get_doc(
				{
					"doctype": "User",
					"email": self.test_user,
					"first_name": "RBAC SoD Test",
					"send_welcome_email": 0,
					"roles": [{"role": "FCRM Credit Analyst"}],
				}
			).insert(ignore_permissions=True)

	def tearDown(self):
		frappe.db.rollback()

	def _ensure_sod_rule(self):
		if not frappe.db.exists("FCRM SOD Rule", "FCRM Credit Analyst-FCRM RM"):
			frappe.get_doc(
				{
					"doctype": "FCRM SOD Rule",
					"role_a": "FCRM Credit Analyst",
					"role_b": "FCRM RM",
					"conflict_type": "Hard",
					"description": "Credit Analyst cannot also be RM",
					"enabled": 1,
				}
			).insert(ignore_permissions=True)

	def test_no_conflict_for_unrelated_role(self):
		conflicts = check_sod_conflict(self.test_user, "FCRM Collection Officer")
		for c in conflicts:
			self.assertNotIn("Collection Officer", (c["role_a"], c["role_b"]))

	def test_detects_sod_conflict(self):
		self._ensure_sod_rule()
		conflicts = check_sod_conflict(self.test_user, "FCRM RM")
		self.assertGreaterEqual(len(conflicts), 1)
		match = any(
			c["role_a"] == "FCRM Credit Analyst" and c["role_b"] == "FCRM RM"
			for c in conflicts
		)
		self.assertTrue(match, "Expected SoD conflict between Credit Analyst and RM")

	def test_no_conflict_for_same_role(self):
		conflicts = check_sod_conflict(self.test_user, "FCRM Credit Analyst")
		for c in conflicts:
			self.assertFalse(
				c["role_a"] == c["role_b"] == "FCRM Credit Analyst",
				"Same role should not conflict with itself",
			)


class TestRBACFieldMasking(FrappeTestCase):
	def test_mask_field_value_full(self):
		result = mask_field_value("1234567890", "Full", "*")
		self.assertEqual(result, "**********")

	def test_mask_field_value_prefix(self):
		result = mask_field_value("1234567890", "Prefix", "*")
		self.assertEqual(result, "****567890")

	def test_mask_field_value_suffix(self):
		result = mask_field_value("1234567890", "Suffix", "*")
		self.assertEqual(result, "123456****")

	def test_mask_field_value_none_for_empty(self):
		result = mask_field_value(None, "Full", "*")
		self.assertIsNone(result)

	def test_mask_field_value_middle(self):
		result = mask_field_value("1234567890", "Middle", "*")
		self.assertEqual(result, "12*****90")


class TestRBACPermissionAudit(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_log_permission_audit_creates_entry(self):
		log_permission_audit(
			"Role Added",
			target_doctype="CRM Lead",
			target_docname="TEST-LEAD",
			details="RBAC test audit entry",
		)
		self.assertTrue(
			frappe.db.exists(
				"FCRM Permission Audit",
				{"event_type": "Role Added", "details": "RBAC test audit entry"},
			)
		)

	def test_log_permission_audit_records_user(self):
		log_permission_audit(
			"Role Removed",
			target_doctype="CRM Lead",
			details="Check user recording",
		)
		self.assertTrue(
			frappe.db.exists(
				"FCRM Permission Audit",
				{"event_type": "Role Removed", "user": "Administrator"},
			)
		)

	def test_log_permission_audit_records_timestamp(self):
		log_permission_audit(
			"SOD Check Triggered",
			target_doctype="CRM Lead",
			details="Check timestamp recording",
		)
		entry = frappe.get_last_doc(
			"FCRM Permission Audit", filters={"event_type": "SOD Check Triggered"}
		)
		self.assertIsNotNone(entry.timestamp)


class TestRBACSeedRoles(FrappeTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_seed_default_roles_is_idempotent(self):
		result1 = seed_default_roles()
		result2 = seed_default_roles()
		self.assertEqual(result1["total"], result2["total"])
		self.assertIn("created", result1)
		self.assertIn("total", result1)
