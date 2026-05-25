import frappe
from unittest import TestCase

from crm.api.portfolio_monitoring import (
	ensure_portfolio_tables,
	get_portfolio_overview,
	get_trend_chart,
	get_industry_exposure,
	get_geographic_exposure,
	get_sbl_monitoring,
	get_top_exposures,
	get_concentration_matrix,
	get_ews_signals,
	get_covenant_breaches,
	get_stress_test_scenarios,
	run_stress_test,
	get_ecl_summary,
	get_watchlist,
	get_ai_portfolio_alerts,
	acknowledge_ews_signal,
	cure_covenant,
	add_to_watchlist,
	request_watchlist_removal,
	generate_report,
	get_risk_heatmap,
	get_npl_trend,
	get_vintage_analysis,
	get_grade_migration,
	get_portfolio_dashboard,
	verify_uat_feature,
	get_uat_summary,
)


class TestPortfolioMonitoringUAT(TestCase):
	"""UAT test suite for Portfolio Monitoring module — verifies every P0-P2 feature end-to-end."""

	@classmethod
	def setUpClass(cls):
		if not frappe.db.table_exists("CRM Credit Facility"):
			raise cls.skipTest("CRM Credit Facility doctype not installed")

	@classmethod
	def tearDownClass(cls):
		pass

	def setUp(self):
		ensure_portfolio_tables()
		self._clean_tables()

	def tearDown(self):
		self._clean_tables()

	def _clean_tables(self):
		tables = [
			"tabCRM EWS Signal", "tabCRM Covenant Test Result",
			"tabCRM Watchlist Case", "tabCRM Stress Test Scenario",
			"tabCRM Portfolio Alert", "tabCRM Concentration Limit",
			"tabCRM Risk Grade Migration", "tabCRM ECL Calculation",
			"tabCRM Exposure Account", "tabCRM Portfolio Snapshot",
		]
		for t in tables:
			try:
				frappe.db.sql(f"DELETE FROM `{t}`")
			except Exception:
				pass

	# ─── 1.0 Portfolio Overview (P0) ──────────────────
	def test_01_portfolio_overview(self):
		result = get_portfolio_overview()
		self.assertIsInstance(result, dict)
		self.assertIn("total_os", result)
		self.assertIn("npl_rate", result)
		self.assertIn("watchlist_count", result)
		self.assertIn("total_account", result)
		self.assertIn("total_os_display", result)
		self.assertIsInstance(result["npl_rate"], (int, float))
		self.assertIsInstance(result["total_account"], (int, float))
		print(f"[UAT] 1.0 Portfolio Overview: OS={result['total_os_display']}, "
			f"NPL={result['npl_rate']}%, Accounts={result['total_account']}")

	def test_02_trend_chart(self):
		result = get_trend_chart()
		self.assertIsInstance(result, dict)
		self.assertIn("labels", result)
		self.assertIn("os_trend", result)
		self.assertIn("npl_trend", result)
		self.assertIsInstance(result["labels"], list)
		self.assertIsInstance(result["os_trend"], list)
		self.assertEqual(len(result["labels"]), len(result["os_trend"]))
		print(f"[UAT] 1.0 Trend Chart: {len(result['labels'])} months loaded")

	# ─── 2.0 Industry Exposure (P0) ───────────────────
	def test_03_industry_exposure(self):
		result = get_industry_exposure()
		self.assertIsInstance(result, dict)
		self.assertIn("industries", result)
		self.assertIn("breach_count", result)
		self.assertIn("warning_count", result)
		self.assertIsInstance(result["industries"], list)
		for ind in result["industries"]:
			self.assertIn("name", ind)
			self.assertIn("os", ind)
			self.assertIn("pct", ind)
			self.assertIn("usage", ind)
		print(f"[UAT] 2.0 Industry Exposure: {len(result['industries'])} sectors, "
			f"{result['breach_count']} breaches, {result['warning_count']} warnings")

	# ─── 3.0 Geographic Exposure (P0) ─────────────────
	def test_04_geographic_exposure(self):
		result = get_geographic_exposure()
		self.assertIsInstance(result, dict)
		self.assertIn("regions", result)
		self.assertIsInstance(result["regions"], list)
		for reg in result["regions"]:
			self.assertIn("province", reg)
			self.assertIn("os", reg)
			self.assertIn("npl", reg)
			self.assertIsInstance(reg["npl"], (int, float))
		print(f"[UAT] 3.0 Geographic Exposure: {len(result['regions'])} regions tracked")

	# ─── 4.0 SBL Monitoring (P1) ─────────────────────
	def test_05_sbl_monitoring(self):
		result = get_sbl_monitoring()
		self.assertIsInstance(result, dict)
		self.assertIn("borrowers", result)
		self.assertIn("breach_count", result)
		self.assertIn("warning_count", result)
		self.assertIn("core_capital", result)
		self.assertIsInstance(result["borrowers"], list)
		for b in result["borrowers"]:
			self.assertIn("name", b)
			self.assertIn("usage", b)
			self.assertIn("pctCapital", b)
		print(f"[UAT] 4.0 SBL: {len(result['borrowers'])} borrowers tracked, "
			f"{result['breach_count']} breaches")

	# ─── 5.0 Top 20 Exposures (P0) ───────────────────
	def test_06_top_exposures(self):
		result = get_top_exposures(limit=20)
		self.assertIsInstance(result, dict)
		self.assertIn("exposures", result)
		self.assertIsInstance(result["exposures"], list)
		self.assertLessEqual(len(result["exposures"]), 20)
		for exp in result["exposures"]:
			self.assertIn("name", exp)
			self.assertIn("os", exp)
			self.assertIn("grade", exp)
			self.assertIn("dpd", exp)
		# Verify sorted descending
		if len(result["exposures"]) >= 2:
			self.assertGreaterEqual(
				result["exposures"][0]["os_raw"],
				result["exposures"][-1]["os_raw"],
			)
		print(f"[UAT] 5.0 Top 20 Exposures: {len(result['exposures'])} exposures listed")

	# ─── 6.0 Concentration Risk Matrix (P2) ──────────
	def test_07_concentration_matrix(self):
		result = get_concentration_matrix()
		self.assertIsInstance(result, dict)
		self.assertIn("rows", result)
		self.assertIn("industries", result)
		self.assertIn("regions", result)
		if result["rows"]:
			self.assertIn("industry", result["rows"][0])
			self.assertIn("cells", result["rows"][0])
			if result["rows"][0]["cells"]:
				self.assertIn("intensity", result["rows"][0]["cells"][0])
		print(f"[UAT] 6.0 Concentration Matrix: {len(result['rows'])} rows x "
			f"{len(result.get('regions', []))} cols")

	# ─── 7.0 EWS Signals (P0) ────────────────────────
	def test_08_ews_signals(self):
		result = get_ews_signals()
		self.assertIsInstance(result, dict)
		self.assertIn("signals", result)
		self.assertIn("count", result)
		self.assertIsInstance(result["signals"], list)
		for s in result["signals"]:
			self.assertIn("severity", s)
			self.assertIn("signal_text", s)
			self.assertIn("borrower_name", s)
		print(f"[UAT] 7.0 EWS Signals: {result['count']} active signals")

	# ─── 8.0 Covenant Breach Detection (P0) ──────────
	def test_09_covenant_breaches(self):
		result = get_covenant_breaches()
		self.assertIsInstance(result, dict)
		self.assertIn("covenants", result)
		self.assertIn("count", result)
		for c in result["covenants"]:
			self.assertIn("result", c)
			self.assertIn("covenant_rule", c)
			self.assertIn("threshold", c)
			self.assertIn("actual_value", c)
		print(f"[UAT] 8.0 Covenant Breach: {result['count']} tests, "
			f"{sum(1 for c in result['covenants'] if c['result'] == 'Breach')} breaches")

	# ─── 14.0 Watchlist Management (P1) ──────────────
	def test_10_watchlist(self):
		result = get_watchlist()
		self.assertIsInstance(result, dict)
		self.assertIn("watchlist", result)
		self.assertIn("count", result)
		self.assertIsInstance(result["watchlist"], list)

		# Test add to watchlist
		add_result = add_to_watchlist("UAT Test Corp", 500_000_000_000, 15, "Payment Delay")
		self.assertIn("watch_id", add_result)
		self.assertEqual(add_result["status"], "ok")

		# Verify added
		result2 = get_watchlist()
		self.assertGreaterEqual(result2["count"], 1)

		# Test removal request
		rem_result = request_watchlist_removal(add_result["watch_id"], "Loan restructured")
		self.assertEqual(rem_result["status"], "ok")

		print(f"[UAT] 14.0 Watchlist: {result['count']} items, add+removal OK")

	# ─── 16.0 Stress Testing (P2) ────────────────────
	def test_11_stress_testing(self):
		scenarios = get_stress_test_scenarios()
		self.assertIsInstance(scenarios, dict)
		self.assertIn("scenarios", scenarios)
		self.assertIn("base_car", scenarios)

		# Custom stress test
		result = run_stress_test(rate_shock=200, npl_shock=3.0)
		self.assertIn("car_after", result)
		self.assertIn("car_impact", result)
		self.assertIn("ecl_amount", result)
		self.assertIn("threshold_breached", result)
		self.assertIn("recommendation", result)
		print(f"[UAT] 16.0 Stress Test: {len(scenarios['scenarios'])} presets, "
			f"custom CAR impact: {result['car_impact']}%")

	# ─── 17.0 ECL / PSAK 71 (P2) ─────────────────────
	def test_12_ecl_calculation(self):
		result = get_ecl_summary()
		self.assertIsInstance(result, dict)
		self.assertIn("stages", result)
		self.assertIn("total_ecl", result)
		self.assertIn("total_os", result)
		self.assertEqual(len(result["stages"]), 3)
		for s in result["stages"]:
			self.assertIn("stage", s)
			self.assertIn("os", s)
			self.assertIn("ecl", s)
		print(f"[UAT] 17.0 ECL: {len(result['stages'])} stages, "
			f"total ECL={result['total_ecl']}")

	# ─── 10.0 AI Portfolio Alerts ────────────────────
	def test_13_ai_portfolio_alerts(self):
		result = get_ai_portfolio_alerts()
		self.assertIsInstance(result, dict)
		self.assertIn("alerts", result)
		self.assertIsInstance(result["alerts"], list)
		for a in result["alerts"]:
			self.assertIn("alert_type", a)
			self.assertIn("severity", a)
			self.assertIn("title", a)
			self.assertIn("recommended_action", a)
		print(f"[UAT] 10.0 AI Alerts: {len(result['alerts'])} alerts generated")

	# ─── 11.0 Risk Heatmap (P1) ──────────────────────
	def test_14_risk_heatmap(self):
		result = get_risk_heatmap()
		self.assertIsInstance(result, dict)
		self.assertIn("dimensions", result)
		self.assertIn("industry", result["dimensions"])
		self.assertIn("region", result["dimensions"])
		self.assertIn("grade", result["dimensions"])
		for dim_key, items in result["dimensions"].items():
			self.assertIsInstance(items, list)
			if items:
				self.assertIn("label", items[0])
				self.assertIn("npl_rate", items[0])
				self.assertIn("intensity", items[0])
		print(f"[UAT] 11.0 Risk Heatmap: 3 dimensions x "
			f"{sum(len(v) for v in result['dimensions'].values())} cells")

	# ─── 12.0 NPL Trend Analysis (P1) ────────────────
	def test_15_npl_trend(self):
		result = get_npl_trend()
		self.assertIsInstance(result, dict)
		self.assertIn("trend", result)
		self.assertIn("roll_rates", result)
		self.assertIn("cure_rate", result)
		self.assertIn("current_npl_rate", result)
		self.assertIsInstance(result["trend"], list)
		self.assertIn("current_to_30", result["roll_rates"])
		self.assertIn("30_to_60", result["roll_rates"])
		self.assertIn("60_to_90plus", result["roll_rates"])
		print(f"[UAT] 12.0 NPL Trend: {len(result['trend'])} months, "
			f"current NPL={result['current_npl_rate']}%, "
			f"roll rate 0-30dpd={result['roll_rates']['current_to_30']}%")

	# ─── 13.0 Vintage Analysis (P2) ──────────────────
	def test_16_vintage_analysis(self):
		result = get_vintage_analysis()
		self.assertIsInstance(result, dict)
		self.assertIn("vintages", result)
		self.assertIn("max_mob", result)
		self.assertIn("heatmap", result)
		self.assertIsInstance(result["heatmap"], list)
		if result["heatmap"]:
			self.assertIn("vintage", result["heatmap"][0])
			self.assertIn("month_of_life", result["heatmap"][0])
			self.assertIn("default_pct", result["heatmap"][0])
		print(f"[UAT] 13.0 Vintage Analysis: {len(result['vintages'])} vintages, "
			f"{len(result['heatmap'])} heatmap cells")

	# ─── 15.0 Risk Grade Migration (P2) ──────────────
	def test_17_grade_migration(self):
		result = get_grade_migration()
		self.assertIsInstance(result, dict)
		self.assertIn("grades", result)
		self.assertIn("rows", result)
		self.assertIsInstance(result["rows"], list)
		if result["rows"]:
			self.assertIn("grade", result["rows"][0])
			self.assertIn("cells", result["rows"][0])
			self.assertIn("migrated_up_pct", result["rows"][0])
			self.assertIn("migrated_down_pct", result["rows"][0])
		print(f"[UAT] 15.0 Grade Migration: {len(result['rows'])} grades tracked")

	# ─── 18.0 Portfolio Reports ──────────────────────
	def test_18_generate_report(self):
		result = generate_report(
			template="Committee Meeting Summary Package (PDF)",
			send_email=False,
		)
		self.assertIn("status", result)
		self.assertIn("report_name", result)
		self.assertIn("data", result)
		self.assertEqual(result["status"], "ok")
		print(f"[UAT] 18.0 Portfolio Report: {result['report_name']} generated")

	# ─── Stress Test Acknowledge & Cure Workflows ────
	def test_19_acknowledge_workflow(self):
		# Ensure there's a signal to acknowledge
		get_ews_signals()
		signals = get_ews_signals()["signals"]
		if signals:
			sig = signals[0]
			result = acknowledge_ews_signal(sig["name"], "Reviewed by UAT")
			self.assertEqual(result["status"], "ok")
			self.assertEqual(result["signal_id"], sig["name"])
			print(f"[UAT] 7.0 EWS Acknowledge: signal {sig['name'][:12]}... acknowledged")

	def test_20_covenant_cure_workflow(self):
		get_covenant_breaches()
		covenants = get_covenant_breaches()["covenants"]
		breaches = [c for c in covenants if c["result"] == "Breach"]
		if breaches:
			cov = breaches[0]
			result = cure_covenant(cov["name"], "Test cure via UAT")
			self.assertEqual(result["status"], "ok")
			self.assertEqual(result["covenant_id"], cov["name"])
			print(f"[UAT] 8.0 Covenant Cure: {cov['name'][:12]}... cured")

	# ─── Composite Dashboard ─────────────────────────
	def test_21_portfolio_dashboard(self):
		result = get_portfolio_dashboard()
		self.assertIsInstance(result, dict)
		self.assertIn("overview", result)
		self.assertIn("trend", result)
		self.assertIn("industry", result)
		self.assertIn("geographic", result)
		self.assertIn("top_exposures", result)
		self.assertIn("ews", result)
		self.assertIn("covenants", result)
		self.assertIn("ecl", result)
		self.assertIn("watchlist", result)
		self.assertIn("fetched_at", result)
		print(f"[UAT] Composite Dashboard: all sections loaded at {result['fetched_at']}")

	# ─── UAT Feature Verification ────────────────────
	def test_22_uat_verification(self):
		features = [
			"portfolio_overview", "industry_exposure", "geographic_exposure",
			"sbl_monitoring", "top_exposures", "concentration_matrix",
			"ews", "covenant_breach", "watchlist", "stress_testing", "ecl",
			"risk_heatmap", "npl_trend", "vintage_analysis", "grade_migration",
			"portfolio_simulation", "ai_alerts", "reports",
		]
		for f in features:
			result = verify_uat_feature(f)
			self.assertEqual(result["status"], "available")
			self.assertIn("feature", result)
			self.assertIn("checks", result)
			self.assertIsInstance(result["checks"], list)
			self.assertGreater(len(result["checks"]), 0)
		print(f"[UAT] Verification: {len(features)} features verified as available")

	# ─── UAT Summary ─────────────────────────────────
	def test_23_uat_summary(self):
		result = get_uat_summary()
		self.assertIn("features", result)
		self.assertIn("total", result)
		self.assertIn("status", result)
		self.assertEqual(result["status"], "production_ready")
		self.assertGreater(result["total"], 0)
		print(f"[UAT] Summary: {result['total']} features, status={result['status']}")

	# ─── EWS Signal Data Integrity ───────────────────
	def test_24_ews_integrity(self):
		result = get_ews_signals()
		for s in result["signals"]:
			self.assertIn(s["severity"], ("Red", "Amber", "Green"))
			self.assertIsNotNone(s.get("signal_text"))

	# ─── SBL Data Integrity ──────────────────────────
	def test_25_sbl_integrity(self):
		result = get_sbl_monitoring()
		for b in result["borrowers"]:
			self.assertGreaterEqual(b["usage"], 0)
			self.assertGreaterEqual(b["pctCapital"], 0)

	# ─── ECL Stage Sum Check ─────────────────────────
	def test_26_ecl_stage_sum(self):
		result = get_ecl_summary()
		total_os_raw = sum(s["os_raw"] for s in result["stages"])
		self.assertAlmostEqual(total_os_raw, result["total_os_raw"], delta=1)
