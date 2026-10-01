import frappe
from unittest import TestCase
from unittest.mock import patch

from crm.api.lead_gen import (
	DEFAULT_IMPORT_OPTIONS,
	_build_workbook_payload_from_path,
	_bundled_workbook_path,
	_import_rows,
	mock_lead_scraping,
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

	def test_search_without_matches_does_not_import_other_leads(self):
		rows = [{"company": "Jakarta Software"}, {"company": "Bali Hotel"}]
		with (
			patch("crm.api.lead_gen.os.path.exists", return_value=True),
			patch("crm.api.lead_gen._build_workbook_payload_from_path", return_value={"row_objects": rows, "warnings": []}),
			patch("crm.api.lead_gen._import_rows", return_value={"created": 0, "skipped": 0, "warnings": []}) as import_rows,
			patch("crm.api.lead_gen.frappe.publish_realtime"),
			patch("crm.api.lead_gen.frappe.clear_cache"),
		):
			result = mock_lead_scraping("Carikan 10 nonexistentsector")
		self.assertEqual(result["created"], 0)
		self.assertEqual(import_rows.call_args.args[0], [])
