from unittest import TestCase

import frappe

from crm.api.portfolio_monitoring import _sync_exposure_accounts, ensure_portfolio_tables


class TestPortfolioLiveSource(TestCase):
	def test_facilities_are_read_without_rewriting_exposures(self):
		ensure_portfolio_tables()
		before = frappe.db.count("CRM Exposure Account")
		expected = frappe.db.count(
			"CRM Credit Facility",
			{"status": ["in", ["Active", "Watchlist", "Restructured"]], "outstanding": [">", 0]},
		)
		self.assertEqual(len(_sync_exposure_accounts()), expected)
		self.assertEqual(frappe.db.count("CRM Exposure Account"), before)
