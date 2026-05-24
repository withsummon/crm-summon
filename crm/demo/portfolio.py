"""Demo data seeding for Portfolio Monitoring module."""

import datetime
import uuid
from decimal import Decimal

import frappe
from frappe.utils import flt, now_datetime, nowdate

from crm.api.portfolio_monitoring import (
	_raw_insert,
	ensure_portfolio_tables,
)


DEMO_EWS_SIGNALS = [
	{
		"customer": "",
		"borrower_name": "Bhakti Nusantara Corp",
		"signal_type": "Payment Delay",
		"severity": "Red",
		"source": "Collections System",
		"signal_text": "Debt Service Coverage Ratio (DSCR) dropped below 1.05x. Debt payment anomaly detected.",
		"detected_at": "2026-05-20",
		"status": "Open",
		"acknowledged": 0,
	},
	{
		"customer": "",
		"borrower_name": "Citra Baru Property",
		"signal_type": "Covenant Near Breach",
		"severity": "Amber",
		"source": "Covenant Engine",
		"signal_text": "Covenant Debt-to-Equity is nearing critical limit. Actual values: 2.85x vs limit threshold: 3.0x.",
		"detected_at": "2026-05-22",
		"status": "Open",
		"acknowledged": 0,
	},
	{
		"customer": "",
		"borrower_name": "Pioneer Logistik Tbk",
		"signal_type": "Negative News",
		"severity": "Amber",
		"source": "News AI Scanner",
		"signal_text": "Adverse local media sentiment detected. Class Action lawsuit filed by logistics partners.",
		"detected_at": "2026-05-23",
		"status": "Open",
		"acknowledged": 0,
	},
]

DEMO_COVENANTS = [
	{
		"customer": "",
		"borrower_name": "Bhakti Nusantara Corp",
		"covenant_type": "Debt-to-Equity",
		"covenant_rule": "Debt-to-Equity ratio must not exceed 2.50x",
		"threshold": "2.50x",
		"actual_value": "2.95x",
		"result": "Breach",
		"tested_at": "2026-05-20",
		"cure_status": "Open",
	},
	{
		"customer": "",
		"borrower_name": "Citra Baru Property",
		"covenant_type": "Current Ratio",
		"covenant_rule": "Current ratio must remain above 1.20x",
		"threshold": "1.20x",
		"actual_value": "1.42x",
		"result": "Compliant",
		"tested_at": "2026-05-22",
		"cure_status": "N/A",
	},
]

DEMO_WATCHLIST = [
	{"customer": "", "borrower_name": "Bhakti Nusantara Corp", "os_amount": 850_000_000_000, "dpd": 15, "reason": "Payment Delay", "trigger_source": "Collections System", "added_by": "System", "approval_status": "Approved"},
	{"customer": "", "borrower_name": "Citra Baru Property", "os_amount": 420_000_000_000, "dpd": 0, "reason": "Ratio Drop", "trigger_source": "Covenant Engine", "added_by": "System", "approval_status": "Approved"},
	{"customer": "", "borrower_name": "Pioneer Logistik Tbk", "os_amount": 310_000_000_000, "dpd": 0, "reason": "Negative News", "trigger_source": "News AI Scanner", "added_by": "System", "approval_status": "Approved"},
	{"customer": "", "borrower_name": "Graha Sentosa Tbk", "os_amount": 150_000_000_000, "dpd": 32, "reason": "DPD > 30", "trigger_source": "Collections System", "added_by": "System", "approval_status": "Approved"},
	{"customer": "", "borrower_name": "Pratama Steel", "os_amount": 95_000_000_000, "dpd": 8, "reason": "Covenant Breach", "trigger_source": "Covenant Engine", "added_by": "System", "approval_status": "Pending"},
]

DEMO_STRESS_SCENARIOS = [
	{"scenario_name": "Mild Market Softening", "severity": "Mild", "rate_shock": 150, "npl_shock": 1.5, "macro_assumption": "GDP growth slows to 4.5%, unemployment rises moderately", "is_preset": 1},
	{"scenario_name": "Severe Economic Crisis", "severity": "Severe", "rate_shock": 350, "npl_shock": 4.5, "macro_assumption": "GDP contraction -2%, sharp rupiah depreciation, commodity price crash", "is_preset": 1},
	{"scenario_name": "Rate Shock Only", "severity": "Moderate", "rate_shock": 250, "npl_shock": 0, "macro_assumption": "BI rate hike cycle, but corporate earnings remain stable", "is_preset": 1},
]

DEMO_PORTFOLIO_ALERTS = [
	{
		"alert_type": "Concentration Risk",
		"severity": "Red",
		"title": "Real Estate sector approaching limit breach",
		"description": "Real Estate exposure at 23.2% of portfolio vs 20% limit. Add 2 more large accounts to trigger breach.",
		"reasoning": "Industry concentration analysis detected Real Estate sector at 115.6% of internal limit. Immediate action recommended.",
		"recommended_action": "Reduce Real Estate exposure by IDR 0.5T or request limit enhancement from Risk Committee.",
		"status": "Open",
		"acknowledged": 0,
	},
	{
		"alert_type": "Deterioration",
		"severity": "Amber",
		"title": "Bhakti Nusantara Corp DSCR below threshold",
		"description": "DSCR dropped to 0.95x, below covenant threshold of 1.05x. Watchlist recommended.",
		"reasoning": "Payment anomaly + DSCR deterioration detected simultaneously. High probability of further downgrade.",
		"recommended_action": "Contact RM to schedule covenant review meeting. Prepare restructuring assessment.",
		"status": "Open",
		"acknowledged": 0,
	},
	{
		"alert_type": "Early Warning",
		"severity": "Amber",
		"title": "Negative news sentiment for Pioneer Logistik",
		"description": "Adverse media coverage detected. Class action lawsuit filed against logistics company.",
		"reasoning": "News AI scanner flagged negative sentiment score of 0.28 (scale 0-1). Legal risk impacts repayment.",
		"recommended_action": "Review legal exposure. Assess potential contingent liability impact on credit quality.",
		"status": "Open",
		"acknowledged": 0,
	},
]

DEMO_CONCENTRATION_LIMITS = [
	{"dimension_type": "industry", "dimension_value": "Food & Beverage", "limit_percent": 25.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "industry", "dimension_value": "Real Estate & Property", "limit_percent": 20.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "industry", "dimension_value": "Wholesale Trade", "limit_percent": 25.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "industry", "dimension_value": "Agriculture", "limit_percent": 25.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "industry", "dimension_value": "Manufacturing", "limit_percent": 25.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "industry", "dimension_value": "Mining", "limit_percent": 20.0, "warning_threshold": 75.0, "breach_threshold": 100.0},
	{"dimension_type": "region", "dimension_value": "Jawa", "limit_percent": 40.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "region", "dimension_value": "Sumatera", "limit_percent": 25.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "region", "dimension_value": "Kalimantan", "limit_percent": 20.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "region", "dimension_value": "Sulawesi", "limit_percent": 15.0, "warning_threshold": 80.0, "breach_threshold": 100.0},
	{"dimension_type": "region", "dimension_value": "Papua", "limit_percent": 10.0, "warning_threshold": 75.0, "breach_threshold": 100.0},
]

DEMO_GRADE_MIGRATIONS = [
	{"customer": "", "borrower_name": "Bhakti Nusantara Corp", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "A", "grade_end": "BB", "migration_direction": "down", "industry_kbli": "Real Estate", "product": "Term Loan"},
	{"customer": "", "borrower_name": "Citra Baru Property", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "AA", "grade_end": "A", "migration_direction": "down", "industry_kbli": "Real Estate", "product": "Revolving"},
	{"customer": "", "borrower_name": "Pioneer Logistik Tbk", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "BBB", "grade_end": "BBB", "migration_direction": "stable", "industry_kbli": "Transportation", "product": "Term Loan"},
	{"customer": "", "borrower_name": "Indofood Sukses Makmur Tbk", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "AAA", "grade_end": "AAA", "migration_direction": "stable", "industry_kbli": "Food & Beverage", "product": "SBL"},
	{"customer": "", "borrower_name": "Sinarmas Group Corporate", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "AA", "grade_end": "AA", "migration_direction": "stable", "industry_kbli": "Real Estate", "product": "Syariah"},
	{"customer": "", "borrower_name": "Astra Group Conglomerate", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "AAA", "grade_end": "AAA", "migration_direction": "stable", "industry_kbli": "Manufacturing", "product": "Term Loan"},
	{"customer": "", "borrower_name": "Djarum Group Conglomerate", "period_start": "2025-06-01", "period_end": "2026-06-01", "grade_start": "AAA", "grade_end": "AA", "migration_direction": "down", "industry_kbli": "Manufacturing", "product": "SBL"},
]

DEMO_ECL_CALCULATIONS = [
	{"customer": "", "borrower_name": "Indofood Sukses Makmur Tbk", "os_amount": 1_250_000_000_000, "pd": 0.3, "lgd": 40.0, "ead": 1_250_000_000_000, "stage": 1, "ecl_amount": 1_500_000_000, "macro_overlay": 1.05, "period": "2026-06-01"},
	{"customer": "", "borrower_name": "Sinarmas Group Corporate", "os_amount": 2_410_000_000_000, "pd": 0.5, "lgd": 45.0, "ead": 2_410_000_000_000, "stage": 1, "ecl_amount": 5_422_500_000, "macro_overlay": 1.05, "period": "2026-06-01"},
	{"customer": "", "borrower_name": "Bhakti Nusantara Corp", "os_amount": 850_000_000_000, "pd": 5.0, "lgd": 55.0, "ead": 850_000_000_000, "stage": 2, "ecl_amount": 23_375_000_000, "macro_overlay": 1.10, "period": "2026-06-01"},
	{"customer": "", "borrower_name": "Citra Baru Property", "os_amount": 420_000_000_000, "pd": 2.5, "lgd": 50.0, "ead": 420_000_000_000, "stage": 2, "ecl_amount": 5_250_000_000, "macro_overlay": 1.08, "period": "2026-06-01"},
	{"customer": "", "borrower_name": "Dummy Default Corp", "os_amount": 350_000_000_000, "pd": 100.0, "lgd": 70.0, "ead": 350_000_000_000, "stage": 3, "ecl_amount": 245_000_000_000, "macro_overlay": 1.0, "period": "2026-06-01"},
]

DEMO_CREDIT_FACILITIES = [
	{"customer": "Indofood Sukses Makmur Tbk", "facility_type": "SBL - Investment", "product_type": "Term Loan", "status": "Active", "outstanding": 1_250_000_000_000, "limit_amount": 1_500_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Sinarmas Group Corporate", "facility_type": "Syariah - Project Financing", "product_type": "Syariah", "status": "Active", "outstanding": 2_410_000_000_000, "limit_amount": 2_500_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Djarum Group Conglomerate", "facility_type": "SBL - Working Capital", "product_type": "SBL", "status": "Active", "outstanding": 1_950_000_000_000, "limit_amount": 2_500_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Astra Group Conglomerate", "facility_type": "Term Loan - Heavy Equipment", "product_type": "Term Loan", "status": "Active", "outstanding": 1_120_000_000_000, "limit_amount": 1_800_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Bhakti Nusantara Corp", "facility_type": "Revolving - Construction", "product_type": "Revolving", "status": "Watchlist", "outstanding": 850_000_000_000, "limit_amount": 1_000_000_000_000, "health": "Sumatera", "default_flag": 1},
	{"customer": "Citra Baru Property", "facility_type": "Term Loan - Property Dev", "product_type": "Term Loan", "status": "Active", "outstanding": 420_000_000_000, "limit_amount": 500_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Pioneer Logistik Tbk", "facility_type": "SBL - Logistics", "product_type": "SBL", "status": "Active", "outstanding": 310_000_000_000, "limit_amount": 400_000_000_000, "health": "Sumatera", "default_flag": 0},
	{"customer": "Graha Sentosa Tbk", "facility_type": "SBL - Construction", "product_type": "SBL", "status": "Watchlist", "outstanding": 150_000_000_000, "limit_amount": 200_000_000_000, "health": "Kalimantan", "default_flag": 0},
	{"customer": "Pratama Steel", "facility_type": "Revolving - Working Capital", "product_type": "Revolving", "status": "Active", "outstanding": 95_000_000_000, "limit_amount": 150_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Agung Sedayu Perkasa", "facility_type": "Term Loan - Property", "product_type": "Term Loan", "status": "Active", "outstanding": 680_000_000_000, "limit_amount": 800_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Sampoerna Agro Tbk", "facility_type": "SBL - Plantation", "product_type": "SBL", "status": "Active", "outstanding": 520_000_000_000, "limit_amount": 600_000_000_000, "health": "Sumatera", "default_flag": 0},
	{"customer": "Bumi Resources Tbk", "facility_type": "Term Loan - Mining", "product_type": "Term Loan", "status": "Active", "outstanding": 890_000_000_000, "limit_amount": 1_000_000_000_000, "health": "Kalimantan", "default_flag": 0},
	{"customer": "Pelindo III", "facility_type": "SBL - Infrastructure", "product_type": "SBL", "status": "Active", "outstanding": 750_000_000_000, "limit_amount": 1_200_000_000_000, "health": "Sulawesi", "default_flag": 0},
	{"customer": "Merpati Nusantara", "facility_type": "Term Loan - Aviation", "product_type": "Term Loan", "status": "Restructured", "outstanding": 280_000_000_000, "limit_amount": 350_000_000_000, "health": "Jawa", "default_flag": 1},
	{"customer": "Jayamas Property Group", "facility_type": "Revolving - Construction", "product_type": "Revolving", "status": "Active", "outstanding": 235_000_000_000, "limit_amount": 300_000_000_000, "health": "Sulawesi", "default_flag": 0},
	{"customer": "Duta Anggada", "facility_type": "SBL - Property", "product_type": "SBL", "status": "Active", "outstanding": 540_000_000_000, "limit_amount": 700_000_000_000, "health": "Sumatera", "default_flag": 0},
	{"customer": "Alam Sutera Realty", "facility_type": "Term Loan - Property Dev", "product_type": "Term Loan", "status": "Active", "outstanding": 460_000_000_000, "limit_amount": 550_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Pembangunan Jaya", "facility_type": "SBL - General Contractor", "product_type": "SBL", "status": "Active", "outstanding": 320_000_000_000, "limit_amount": 400_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Japfa Comfeed", "facility_type": "SBL - Agribusiness", "product_type": "SBL", "status": "Active", "outstanding": 410_000_000_000, "limit_amount": 500_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Sentul City Tbk", "facility_type": "Revolving - Property Dev", "product_type": "Revolving", "status": "Active", "outstanding": 180_000_000_000, "limit_amount": 250_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Pabrik Kertas Tjiwi Kimia", "facility_type": "Term Loan - Manufacturing", "product_type": "Term Loan", "status": "Active", "outstanding": 670_000_000_000, "limit_amount": 800_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Indosat Tbk", "facility_type": "SBL - Telecom", "product_type": "SBL", "status": "Active", "outstanding": 920_000_000_000, "limit_amount": 1_100_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "PP London Sumatra", "facility_type": "Term Loan - Plantation", "product_type": "Term Loan", "status": "Active", "outstanding": 380_000_000_000, "limit_amount": 450_000_000_000, "health": "Sumatera", "default_flag": 0},
	{"customer": "Kalbe Farma Tbk", "facility_type": "SBL - Pharmaceutical", "product_type": "SBL", "status": "Active", "outstanding": 290_000_000_000, "limit_amount": 350_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Unilever Indonesia Tbk", "facility_type": "SBL - Consumer Goods", "product_type": "SBL", "status": "Active", "outstanding": 450_000_000_000, "limit_amount": 600_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "Adaro Energy Tbk", "facility_type": "Term Loan - Mining", "product_type": "Term Loan", "status": "Active", "outstanding": 780_000_000_000, "limit_amount": 900_000_000_000, "health": "Kalimantan", "default_flag": 0},
	{"customer": "Perusahaan Gas Negara", "facility_type": "SBL - Energy", "product_type": "SBL", "status": "Active", "outstanding": 610_000_000_000, "limit_amount": 750_000_000_000, "health": "Sumatera", "default_flag": 0},
	{"customer": "Bukit Asam Tbk", "facility_type": "Term Loan - Mining", "product_type": "Term Loan", "status": "Active", "outstanding": 530_000_000_000, "limit_amount": 650_000_000_000, "health": "Sumatera", "default_flag": 0},
	{"customer": "Ciputra Development Tbk", "facility_type": "Revolving - Property", "product_type": "Revolving", "status": "Active", "outstanding": 370_000_000_000, "limit_amount": 450_000_000_000, "health": "Jawa", "default_flag": 0},
	{"customer": "PT Lion Air", "facility_type": "Term Loan - Aviation", "product_type": "Term Loan", "status": "Restructured", "outstanding": 520_000_000_000, "limit_amount": 600_000_000_000, "health": "Jawa", "default_flag": 1},
]

DEMO_RISK_PROFILES = [
	{"customer": "Indofood Sukses Makmur Tbk", "risk_grade": "AAA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 92},
	{"customer": "Sinarmas Group Corporate", "risk_grade": "AA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 85},
	{"customer": "Djarum Group Conglomerate", "risk_grade": "AA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 82},
	{"customer": "Astra Group Conglomerate", "risk_grade": "AAA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 91},
	{"customer": "Bhakti Nusantara Corp", "risk_grade": "BB", "watchlist_status": "Yes", "npl_flag": 1, "internal_score": 45},
	{"customer": "Citra Baru Property", "risk_grade": "BB", "watchlist_status": "Yes", "npl_flag": 0, "internal_score": 52},
	{"customer": "Pioneer Logistik Tbk", "risk_grade": "BBB", "watchlist_status": "No", "npl_flag": 0, "internal_score": 62},
	{"customer": "Graha Sentosa Tbk", "risk_grade": "BB", "watchlist_status": "Yes", "npl_flag": 0, "internal_score": 48},
	{"customer": "Pratama Steel", "risk_grade": "B", "watchlist_status": "No", "npl_flag": 0, "internal_score": 38},
	{"customer": "Agung Sedayu Perkasa", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 72},
	{"customer": "Sampoerna Agro Tbk", "risk_grade": "AA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 84},
	{"customer": "Bumi Resources Tbk", "risk_grade": "BB", "watchlist_status": "No", "npl_flag": 0, "internal_score": 52},
	{"customer": "Pelindo III", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 74},
	{"customer": "Merpati Nusantara", "risk_grade": "CCC", "watchlist_status": "No", "npl_flag": 1, "internal_score": 28},
	{"customer": "Jayamas Property Group", "risk_grade": "BBB", "watchlist_status": "No", "npl_flag": 0, "internal_score": 64},
	{"customer": "Duta Anggada", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 74},
	{"customer": "Alam Sutera Realty", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 70},
	{"customer": "Pembangunan Jaya", "risk_grade": "BBB", "watchlist_status": "No", "npl_flag": 0, "internal_score": 62},
	{"customer": "Japfa Comfeed", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 76},
	{"customer": "Sentul City Tbk", "risk_grade": "BBB", "watchlist_status": "No", "npl_flag": 0, "internal_score": 60},
	{"customer": "Pabrik Kertas Tjiwi Kimia", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 72},
	{"customer": "Indosat Tbk", "risk_grade": "AA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 84},
	{"customer": "PP London Sumatra", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 76},
	{"customer": "Kalbe Farma Tbk", "risk_grade": "AA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 86},
	{"customer": "Unilever Indonesia Tbk", "risk_grade": "AAA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 94},
	{"customer": "Adaro Energy Tbk", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 74},
	{"customer": "Perusahaan Gas Negara", "risk_grade": "AA", "watchlist_status": "No", "npl_flag": 0, "internal_score": 82},
	{"customer": "Bukit Asam Tbk", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 78},
	{"customer": "Ciputra Development Tbk", "risk_grade": "A", "watchlist_status": "No", "npl_flag": 0, "internal_score": 72},
	{"customer": "PT Lion Air", "risk_grade": "CCC", "watchlist_status": "No", "npl_flag": 1, "internal_score": 22},
]


def seed_portfolio_demo_data():
	"""Seed portfolio monitoring demo data into custom tables."""
	ensure_portfolio_tables()

	for signal in DEMO_EWS_SIGNALS:
		_raw_insert("CRM EWS Signal", signal)

	for covenant in DEMO_COVENANTS:
		_raw_insert("CRM Covenant Test Result", covenant)

	for watch in DEMO_WATCHLIST:
		_raw_insert("CRM Watchlist Case", watch)

	for scenario in DEMO_STRESS_SCENARIOS:
		_raw_insert("CRM Stress Test Scenario", scenario)

	for alert in DEMO_PORTFOLIO_ALERTS:
		_raw_insert("CRM Portfolio Alert", alert)

	for limit_row in DEMO_CONCENTRATION_LIMITS:
		_raw_insert("CRM Concentration Limit", limit_row)

	for migration in DEMO_GRADE_MIGRATIONS:
		_raw_insert("CRM Risk Grade Migration", migration)

	for ecl in DEMO_ECL_CALCULATIONS:
		_raw_insert("CRM ECL Calculation", ecl)

	frappe.db.commit()
	return {
		"signals": len(DEMO_EWS_SIGNALS),
		"covenants": len(DEMO_COVENANTS),
		"watchlist": len(DEMO_WATCHLIST),
		"scenarios": len(DEMO_STRESS_SCENARIOS),
		"alerts": len(DEMO_PORTFOLIO_ALERTS),
		"limits": len(DEMO_CONCENTRATION_LIMITS),
		"migrations": len(DEMO_GRADE_MIGRATIONS),
		"ecl": len(DEMO_ECL_CALCULATIONS),
	}


def seed_portfolio_credit_facilities():
	"""Seed demo CRM Credit Facility records for portfolio data."""
	for cf in DEMO_CREDIT_FACILITIES:
		existing = frappe.db.exists("CRM Credit Facility", {"customer": cf["customer"], "facility_type": cf["facility_type"]})
		if existing:
			continue
		doc = frappe.get_doc({
			"doctype": "CRM Credit Facility",
			"customer": cf["customer"],
			"facility_type": cf["facility_type"],
			"product_type": cf["product_type"],
			"status": cf["status"],
			"outstanding": cf["outstanding"],
			"limit_amount": cf["limit_amount"],
			"health": cf["health"],
			"default_flag": cf["default_flag"],
		})
		doc.insert(ignore_permissions=True)


def seed_portfolio_risk_profiles():
	"""Seed demo CRM Risk Profile records."""
	for rp in DEMO_RISK_PROFILES:
		existing = frappe.db.exists("CRM Risk Profile", {"customer": rp["customer"]})
		if existing:
			continue
		doc = frappe.get_doc({
			"doctype": "CRM Risk Profile",
			"customer": rp["customer"],
			"risk_grade": rp["risk_grade"],
			"watchlist_status": rp["watchlist_status"],
			"npl_flag": rp["npl_flag"],
			"internal_score": rp["internal_score"],
		})
		doc.insert(ignore_permissions=True)


def clear_portfolio_demo_data():
	"""Clear all portfolio monitoring demo data."""
	tables = [
		"CRM EWS Signal",
		"Covenant Test Result",
		"Watchlist Case",
		"Stress Test Scenario",
		"Portfolio Alert",
		"Concentration Limit",
		"Risk Grade Migration",
		"ECL Calculation",
		"Exposure Account",
		"Portfolio Snapshot",
		"Portfolio Simulation",
	]
	for table in tables:
		full_name = f"tabCRM {table}"
		if frappe.db.table_exists(f"CRM {table}"):
			frappe.db.sql(f"DELETE FROM `{full_name}`")
	frappe.db.commit()


@frappe.whitelist()
def seed_all_portfolio_demo():
	"""Seed all portfolio demo data in one call."""
	seed_portfolio_credit_facilities()
	seed_portfolio_risk_profiles()
	result = seed_portfolio_demo_data()
	return {"status": "ok", "seeded": result}


@frappe.whitelist()
def clear_all_portfolio_demo():
	"""Clear all portfolio demo data."""
	clear_portfolio_demo_data()
	return {"status": "ok"}
