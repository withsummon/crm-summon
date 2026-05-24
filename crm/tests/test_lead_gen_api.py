import frappe
from unittest import TestCase

from crm.api.lead_gen import (
	DEFAULT_IMPORT_OPTIONS,
	_build_workbook_payload_from_path,
	_bundled_workbook_path,
	_import_rows,
)


class TestLeadGenAPI(TestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_workbook_payload_maps_expected_columns(self):
		payload = _build_workbook_payload_from_path(_bundled_workbook_path())
		mapping = {row["field"]: row for row in payload["column_mapping"]}

		self.assertGreater(payload["normalized_row_count"], 0)
		self.assertTrue(mapping["company"]["mapped"])
		self.assertTrue(mapping["name"]["mapped"])
		self.assertTrue(mapping["email"]["mapped"])
		self.assertTrue(mapping["follow_up"]["mapped"])
		self.assertTrue(
			any("leading blank helper column" in row["message"].lower() for row in payload["warnings"])
		)

	def test_import_rows_returns_tracking_metadata(self):
		if not frappe.db.table_exists("CRM Lead"):
			self.skipTest("CRM Lead doctype is not installed")

		payload = _build_workbook_payload_from_path(_bundled_workbook_path())
		result = _import_rows(payload["row_objects"], DEFAULT_IMPORT_OPTIONS, limit=1)

		self.assertIn("lead_names", result)
		self.assertIn("note_names", result)
		self.assertIn("task_names", result)
		self.assertGreaterEqual(result["total"], 1)
