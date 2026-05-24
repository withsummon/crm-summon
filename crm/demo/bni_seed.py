"""
BNI Comprehensive Seed Data — semua modul terhubung dalam satu ekosistem korporasi BNI.

Modul yang di-seed: Leads, Customer 360, Credit Analysis, Omnichannel, Portfolio Monitoring.
Semua data menggunakan nama debitur korporasi BNI yang realistik dan saling ber-relasi via customer_name.
"""

import datetime
import json
import random
import uuid
from decimal import Decimal

import frappe
from frappe.utils import flt, now_datetime, nowdate, today

from crm.api.portfolio_monitoring import (
	_raw_insert,
	ensure_portfolio_tables,
)

# ─── DATA MASTER: 25 Debitur Korporasi BNI ──────────────────────────
# Setiap debitur punya: segmen, industri, KBLI, provinsi, risk profile, dan fasilitas kredit

BNI_CORPORATE_BORROWERS = [
	# (customer_name, segmen, industri, kbli, provinsi, risk_grade, internal_score, watchlist, npl, fasilitas)
	("PT Indofood Sukses Makmur Tbk", "Korporasi", "Food & Beverage", "10110", "Jawa", "AAA", 92, "No", 0, [
		("KMK Ekspor", "Term Loan", 1_250_000_000_000, 1_500_000_000_000, "Active", 0),
	]),
	("PT Sinarmas Group Corporate", "Konglomerasi", "Real Estate & Property", "41000", "Jawa", "AA", 85, "No", 0, [
		("Project Financing Syariah", "Syariah", 2_410_000_000_000, 2_500_000_000_000, "Active", 0),
		("KMK Konstruksi", "Revolving", 850_000_000_000, 1_000_000_000_000, "Active", 0),
	]),
	("PT Djarum Group Conglomerate", "Konglomerasi", "Manufacturing", "12000", "Jawa", "AA", 82, "No", 0, [
		("SBL Investasi", "SBL", 1_950_000_000_000, 2_500_000_000_000, "Active", 0),
	]),
	("PT Astra Group Conglomerate", "Konglomerasi", "Manufacturing", "28110", "Jawa", "AAA", 91, "No", 0, [
		("Term Loan Alat Berat", "Term Loan", 1_120_000_000_000, 1_800_000_000_000, "Active", 0),
		("KMK Otomotif", "Revolving", 680_000_000_000, 800_000_000_000, "Active", 0),
	]),
	("PT Bhakti Nusantara Corp", "Korporasi", "Real Estate & Property", "41000", "Sumatera", "BB", 45, "Yes", 1, [
		("KMK Konstruksi", "Revolving", 850_000_000_000, 1_000_000_000_000, "Watchlist", 1),
	]),
	("PT Citra Baru Property", "Korporasi", "Real Estate & Property", "41000", "Jawa", "BB", 52, "Yes", 0, [
		("Term Loan Properti", "Term Loan", 420_000_000_000, 500_000_000_000, "Active", 0),
	]),
	("PT Pioneer Logistik Tbk", "Korporasi", "Transportation", "49220", "Sumatera", "BBB", 62, "No", 0, [
		("SBL Logistik", "SBL", 310_000_000_000, 400_000_000_000, "Active", 0),
	]),
	("PT Graha Sentosa Tbk", "Korporasi", "Real Estate & Property", "41000", "Kalimantan", "BB", 48, "Yes", 0, [
		("SBL Konstruksi", "SBL", 150_000_000_000, 200_000_000_000, "Watchlist", 0),
	]),
	("PT Pratama Steel", "UKM", "Manufacturing", "24100", "Jawa", "B", 38, "No", 0, [
		("KMK Working Capital", "Revolving", 95_000_000_000, 150_000_000_000, "Active", 0),
	]),
	("PT Agung Sedayu Perkasa", "Korporasi", "Real Estate & Property", "41000", "Jawa", "A", 72, "No", 0, [
		("Term Loan Properti", "Term Loan", 680_000_000_000, 800_000_000_000, "Active", 0),
	]),
	("PT Sampoerna Agro Tbk", "Korporasi", "Agriculture", "01261", "Sumatera", "AA", 84, "No", 0, [
		("SBL Perkebunan", "SBL", 520_000_000_000, 600_000_000_000, "Active", 0),
	]),
	("PT Bumi Resources Tbk", "Korporasi", "Mining", "05100", "Kalimantan", "BB", 52, "No", 0, [
		("Term Loan Mining", "Term Loan", 890_000_000_000, 1_000_000_000_000, "Active", 0),
	]),
	("PT Pelabuhan Indonesia III", "BUMN", "Transportation", "49111", "Sulawesi", "A", 74, "No", 0, [
		("SBL Infrastruktur", "SBL", 750_000_000_000, 1_200_000_000_000, "Active", 0),
	]),
	("PT Merpati Nusantara", "BUMN", "Transportation", "51101", "Jawa", "CCC", 28, "No", 1, [
		("Term Loan Aviasi", "Term Loan", 280_000_000_000, 350_000_000_000, "Restructured", 1),
	]),
	("PT Jayamas Property Group", "Korporasi", "Real Estate & Property", "41000", "Sulawesi", "BBB", 64, "No", 0, [
		("KMK Konstruksi", "Revolving", 235_000_000_000, 300_000_000_000, "Active", 0),
	]),
	("PT Duta Anggada Realty", "Korporasi", "Real Estate & Property", "41000", "Sumatera", "A", 74, "No", 0, [
		("SBL Properti", "SBL", 540_000_000_000, 700_000_000_000, "Active", 0),
	]),
	("PT Alam Sutera Realty Tbk", "Korporasi", "Real Estate & Property", "41000", "Jawa", "A", 70, "No", 0, [
		("Term Loan Properti", "Term Loan", 460_000_000_000, 550_000_000_000, "Active", 0),
	]),
	("PT Pembangunan Jaya", "Korporasi", "Construction", "41000", "Jawa", "BBB", 62, "No", 0, [
		("SBL Kontraktor", "SBL", 320_000_000_000, 400_000_000_000, "Active", 0),
	]),
	("PT Japfa Comfeed Indonesia Tbk", "Korporasi", "Agriculture", "01261", "Jawa", "A", 76, "No", 0, [
		("SBL Agribisnis", "SBL", 410_000_000_000, 500_000_000_000, "Active", 0),
	]),
	("PT Sentul City Tbk", "Korporasi", "Real Estate & Property", "41000", "Jawa", "BBB", 60, "No", 0, [
		("KMK Properti", "Revolving", 180_000_000_000, 250_000_000_000, "Active", 0),
	]),
	("PT Pabrik Kertas Tjiwi Kimia Tbk", "Korporasi", "Manufacturing", "17010", "Jawa", "A", 72, "No", 0, [
		("Term Loan Manufaktur", "Term Loan", 670_000_000_000, 800_000_000_000, "Active", 0),
	]),
	("PT Indosat Tbk", "Korporasi", "Telecommunication", "61100", "Jawa", "AA", 84, "No", 0, [
		("SBL Telekomunikasi", "SBL", 920_000_000_000, 1_100_000_000_000, "Active", 0),
	]),
	("PT PP London Sumatra Tbk", "Korporasi", "Agriculture", "01261", "Sumatera", "A", 76, "No", 0, [
		("Term Loan Perkebunan", "Term Loan", 380_000_000_000, 450_000_000_000, "Active", 0),
	]),
	("PT Kalbe Farma Tbk", "Korporasi", "Manufacturing", "21000", "Jawa", "AA", 86, "No", 0, [
		("SBL Farmasi", "SBL", 290_000_000_000, 350_000_000_000, "Active", 0),
	]),
	("PT Unilever Indonesia Tbk", "Multinational", "Wholesale Trade", "46900", "Jawa", "AAA", 94, "No", 0, [
		("SBL Consumer Goods", "SBL", 450_000_000_000, 600_000_000_000, "Active", 0),
	]),
	("PT Adaro Energy Tbk", "Korporasi", "Mining", "05100", "Kalimantan", "A", 74, "No", 0, [
		("Term Loan Mining", "Term Loan", 780_000_000_000, 900_000_000_000, "Active", 0),
	]),
	("PT Perusahaan Gas Negara Tbk", "BUMN", "Mining", "06200", "Sumatera", "AA", 82, "No", 0, [
		("SBL Energi", "SBL", 610_000_000_000, 750_000_000_000, "Active", 0),
	]),
	("PT Bukit Asam Tbk", "BUMN", "Mining", "05100", "Sumatera", "A", 78, "No", 0, [
		("Term Loan Mining", "Term Loan", 530_000_000_000, 650_000_000_000, "Active", 0),
	]),
	("PT Ciputra Development Tbk", "Korporasi", "Real Estate & Property", "41000", "Jawa", "A", 72, "No", 0, [
		("KMK Properti", "Revolving", 370_000_000_000, 450_000_000_000, "Active", 0),
	]),
	("PT Lion Air", "Korporasi", "Transportation", "51101", "Jawa", "CCC", 22, "No", 1, [
		("Term Loan Aviasi", "Term Loan", 520_000_000_000, 600_000_000_000, "Restructured", 1),
	]),
]

# ─── LEAD DATA (prospek yang sedang di pipeline BNI) ───────────────
BNI_LEADS = [
	("PT Erajaya Swasembada Tbk", "Telecommunication", "Distributor smartphone dan aksesoris", "KMK Modal Kerja", 500_000_000_000, "Hot"),
	("PT Gojek Indonesia", "Transportation", "Platform transportasi dan fintech", "SBL Teknologi", 2_000_000_000_000, "Hot"),
	("PT Pertamina Geothermal Energy", "Mining", "Pertambangan dan energi panas bumi", "Term Loan Energi", 5_000_000_000_000, "Warm"),
	("PT Ace Hardware Indonesia Tbk", "Wholesale Trade", "Ritel perlengkapan rumah dan lifestyle", "KMK Ritel", 350_000_000_000, "Cold"),
	("PT Bank Jago Tbk", "Financial Services", "Bank digital dan teknologi finansial", "SBL Perbankan", 1_500_000_000_000, "Warm"),
	("PT Mayora Indah Tbk", "Food & Beverage", "Produsen makanan dan minuman", "KMK Ekspor", 750_000_000_000, "Hot"),
	("PT Semen Indonesia Tbk", "Manufacturing", "Produsen semen terbesar di Indonesia", "Term Loan Manufaktur", 1_800_000_000_000, "Warm"),
	("PT ABC President Indonesia", "Food & Beverage", "Produsen makanan ringan dan minuman", "KMK Working Capital", 250_000_000_000, "Cold"),
	("PT Wings Group", "Manufacturing", "Produsen consumer goods dan sabun", "SBL Consumer Goods", 900_000_000_000, "Warm"),
	("PT Traveloka Indonesia", "Transportation", "Platform pemesanan perjalanan online", "SBL Teknologi", 1_200_000_000_000, "Hot"),
]

# ─── OMNICHANNEL CONVERSATIONS ─────────────────────────────────────
BNI_OMNICHANNEL_CONVOS = [
	{"customer": "PT Indofood Sukses Makmur Tbk", "channel": "WhatsApp", "messages": [
		("RM", "Selamat siang Bapak/Ibu dari Indofood. Kami dari BNI ingin menindaklanjuti pengajuan KMK Ekspor Bapak/Ibu."),
		("Customer", "Siang, baik. Apakah ada dokumen tambahan yang diperlukan?"),
		("RM", "Kami membutuhkan laporan keuangan audit 3 tahun terakhir dan NPWP Perusahaan."),
		("Customer", "Baik, akan kami kirimkan minggu ini. Terima kasih."),
		("RM", "Terima kasih. Kami akan proses setelah dokumen lengkap."),
	]},
	{"customer": "PT Sinarmas Group Corporate", "channel": "Email", "messages": [
		("RM", "Kepada Yth. Manajemen Sinarmas Group, Bersama ini kami sampaikan proposal Project Financing Syariah untuk proyek properti Bapak/Ibu."),
		("Customer", "Terima kasih, kami sudah review. Untuk margin syariahnya bisa dinegosiasikan?"),
		("RM", "Tentu, kami bisa diskusikan lebih lanjut. Kami jadwalkan meeting dengan tim treasury pekan depan."),
	]},
	{"customer": "PT Bhakti Nusantara Corp", "channel": "WhatsApp", "messages": [
		("RM", "Yth. Manajemen Bhakti Nusantara, kami mengingatkan bahwa terdapat covenant DSCR yang mendekati batas minimum. Mohon segera dilakukan review."),
		("Customer", "Baik, kami sudah sadar. Kami sedang menyiapkan restructuring proposal."),
		("RM", "Baik, kami tunggu proposalnya. Tim risk BNI akan membantu proses assessment."),
	]},
	{"customer": "PT Pioneer Logistik Tbk", "channel": "WhatsApp", "messages": [
		("RM", "Selamat pagi, Pak. Ada kabar terbaru mengenai gugatan class action yang dilaporkan media? Apakah ada dampak ke operasional?"),
		("Customer", "Pagi, Pak. Saat ini masih dalam proses hukum. Kami yakin tidak ada dampak material ke cashflow."),
		("RM", "Baik, kami monitor terus ya. Jika ada perkembangan, mohon infokan ke kami."),
	]},
	{"customer": "PT Astra Group Conglomerate", "channel": "Email", "messages": [
		("RM", "Yth. Manajemen Astra, Lampiran ini adalah Term Sheet perpanjangan Term Loan Alat Berat yang akan jatuh tempo."),
		("Customer", "Dokumen sudah kami terima. Akan kami review bersama legal dan finance."),
	]},
	{"customer": "PT Indosat Tbk", "channel": "WhatsApp", "messages": [
		("RM", "Selamat siang, Pak. BNI mengucapkan selamat atas pelunasan SBL Telekomunikasi tepat waktu. Kami siap melayani kebutuhan kredit Bapak/Ibu selanjutnya."),
		("Customer", "Terima kasih, Pak. Pelayanan BNI sangat baik. Kami ada rencana ekspansi 5G, mungkin butuh tambahan fasilitas."),
		("RM", "Wah, kabar baik! Kami siap diskusikan kebutuhan pembiayaan 5G Bapak/Ibu."),
	]},
]

# ─── CREDIT APPLICATION DATA (pipeline kredit) ────────────────────
BNI_CREDIT_APPLICATIONS = [
	{"borrower": "PT Gojek Indonesia", "facility": "SBL Teknologi", "amount": 2_000_000_000_000, "status": "In Progress", "grade": "AA-", "tenor": 60},
	{"borrower": "PT Mayora Indah Tbk", "facility": "KMK Ekspor", "amount": 750_000_000_000, "status": "Approved", "grade": "A+", "tenor": 12},
	{"borrower": "PT Erajaya Swasembada Tbk", "facility": "KMK Modal Kerja", "amount": 500_000_000_000, "status": "Credit Analysis", "grade": "BBB+", "tenor": 24},
	{"borrower": "PT Semen Indonesia Tbk", "facility": "Term Loan Manufaktur", "amount": 1_800_000_000_000, "status": "Submitted", "grade": "AA", "tenor": 84},
	{"borrower": "PT Pertamina Geothermal Energy", "facility": "Term Loan Energi", "amount": 5_000_000_000_000, "status": "In Progress", "grade": "AAA", "tenor": 120},
]

# ─── CREDIT SPREAD LINES (financials untuk credit analysis) ──────
BNI_FINANCIAL_STATEMENTS = {
	"PT Indofood Sukses Makmur Tbk": {
		"2023": {"Revenue": 105_000_000_000_000, "COGS": 72_000_000_000_000, "Operating_Income": 18_500_000_000_000, "Net_Income": 12_200_000_000_000, "Total_Assets": 150_000_000_000_000, "Total_Equity": 78_000_000_000_000, "Current_Assets": 55_000_000_000_000, "Current_Liabilities": 28_000_000_000_000, "Total_Liabilities": 72_000_000_000_000, "EBITDA": 25_000_000_000_000},
		"2024": {"Revenue": 112_000_000_000_000, "COGS": 76_000_000_000_000, "Operating_Income": 20_000_000_000_000, "Net_Income": 13_100_000_000_000, "Total_Assets": 158_000_000_000_000, "Total_Equity": 82_000_000_000_000, "Current_Assets": 58_000_000_000_000, "Current_Liabilities": 30_000_000_000_000, "Total_Liabilities": 76_000_000_000_000, "EBITDA": 27_000_000_000_000},
	},
	"PT Astra Group Conglomerate": {
		"2023": {"Revenue": 280_000_000_000_000, "COGS": 200_000_000_000_000, "Operating_Income": 45_000_000_000_000, "Net_Income": 28_000_000_000_000, "Total_Assets": 420_000_000_000_000, "Total_Equity": 210_000_000_000_000, "Current_Assets": 160_000_000_000_000, "Current_Liabilities": 85_000_000_000_000, "Total_Liabilities": 210_000_000_000_000, "EBITDA": 58_000_000_000_000},
		"2024": {"Revenue": 295_000_000_000_000, "COGS": 210_000_000_000_000, "Operating_Income": 48_000_000_000_000, "Net_Income": 30_000_000_000_000, "Total_Assets": 440_000_000_000_000, "Total_Equity": 220_000_000_000_000, "Current_Assets": 170_000_000_000_000, "Current_Liabilities": 88_000_000_000_000, "Total_Liabilities": 220_000_000_000_000, "EBITDA": 62_000_000_000_000},
	},
}

# ─── TRANSACTION HISTORIES (mutasi rekening) ─────────────────────
BNI_TRANSACTIONS = {
	"PT Indofood Sukses Makmur Tbk": [
		{"date": "2026-05-15", "type": "Payment", "amount": 25_000_000_000, "desc": "Pembayaran angsuran KMK Ekspor"},
		{"date": "2026-05-01", "type": "Disbursement", "amount": 50_000_000_000, "desc": "Pencairan KMK tahap 2"},
		{"date": "2026-04-15", "type": "Payment", "amount": 25_000_000_000, "desc": "Pembayaran angsuran KMK Ekspor"},
	],
	"PT Bhakti Nusantara Corp": [
		{"date": "2026-05-10", "type": "Payment", "amount": 5_000_000_000, "desc": "Pembayaran bunga (short payment)"},
		{"date": "2026-04-25", "type": "Payment", "amount": 10_000_000_000, "desc": "Pembayaran angsuran terlambat 15 hari"},
		{"date": "2026-03-20", "type": "Missed Payment", "amount": 15_000_000_000, "desc": "Angsuran Maret tidak dibayar"},
	],
	"PT Lion Air": [
		{"date": "2026-05-01", "type": "Missed Payment", "amount": 20_000_000_000, "desc": "Angsuran Mei tidak dibayar"},
		{"date": "2026-04-01", "type": "Missed Payment", "amount": 20_000_000_000, "desc": "Angsuran April tidak dibayar"},
	],
	"PT Merpati Nusantara": [
		{"date": "2026-05-05", "type": "Payment", "amount": 3_000_000_000, "desc": "Pembayaran bunga restrukturisasi"},
		{"date": "2026-04-05", "type": "Payment", "amount": 3_000_000_000, "desc": "Pembayaran bunga restrukturisasi"},
	],
}


def _ensure_master_data():
	"""Create required master data (Customer Groups, Territories, Industries)."""
	groups_created = 0
	for group_name in set(row[1] for row in BNI_CORPORATE_BORROWERS):
		if group_name and not frappe.db.exists("Customer Group", group_name):
			frappe.get_doc({
				"doctype": "Customer Group",
				"customer_group_name": group_name,
			}).insert(ignore_permissions=True)
			groups_created += 1

	territories_created = 0
	for provinsi in set(row[4] for row in BNI_CORPORATE_BORROWERS):
		if provinsi and not frappe.db.exists("Territory", provinsi):
			frappe.get_doc({
				"doctype": "Territory",
				"territory_name": provinsi,
			}).insert(ignore_permissions=True)
			territories_created += 1

	industries_created = 0
	industries = set(row[2] for row in BNI_CORPORATE_BORROWERS if row[2])
	for lead in BNI_LEADS:
		if lead[1]:
			industries.add(lead[1])

	# Find the actual doctype that Customer.industry links to
	industry_doctype = None
	try:
		meta = frappe.get_meta("Customer")
		field = meta.get_field("industry")
		if field and field.fieldtype == "Link":
			industry_doctype = field.options
	except Exception:
		pass

	if industry_doctype and frappe.db.exists("DocType", industry_doctype):
		for ind in sorted(industries):
			if not frappe.db.exists(industry_doctype, ind):
				try:
					frappe.get_doc({
						"doctype": industry_doctype,
						"industry": ind,
					}).insert(ignore_permissions=True)
					industries_created += 1
				except Exception as e:
					print(f"  [SKIP] Industry '{ind}' in {industry_doctype}: {e}")
	else:
		# Fallback: try both common doctypes
		for dt in ("CRM Industry", "Industry Type"):
			if frappe.db.exists("DocType", dt):
				for ind in sorted(industries):
					if not frappe.db.exists(dt, ind):
						try:
							frappe.get_doc({
								"doctype": dt,
								"industry": ind,
							}).insert(ignore_permissions=True)
							industries_created += 1
						except Exception:
							pass

	# Create CRM Lead Status records needed by seed_leads
	if frappe.db.exists("DocType", "CRM Lead Status"):
		for ls in ("Hot", "Warm", "Cold"):
			if not frappe.db.exists("CRM Lead Status", ls):
				try:
					_type = "Ongoing" if ls in ("Hot", "Warm") else "Open"
					frappe.get_doc({
						"doctype": "CRM Lead Status",
						"lead_status": ls,
						"type": _type,
						"color": "red" if ls == "Hot" else ("orange" if ls == "Warm" else "blue"),
					}).insert(ignore_permissions=True)
				except Exception:
					pass

	# Create CRM Lead Source record for BNI Referral
	if frappe.db.exists("DocType", "CRM Lead Source"):
		if not frappe.db.exists("CRM Lead Source", "BNI Referral"):
			try:
				frappe.get_doc({
					"doctype": "CRM Lead Source",
					"source_name": "BNI Referral",
					"source_group": "Referral",
					"is_active": 1,
				}).insert(ignore_permissions=True)
			except Exception:
				pass

	if groups_created or territories_created or industries_created:
		print(f"  [MASTER] Created {groups_created} groups, {territories_created} territories, {industries_created} industries")


def seed_customers():
	"""Seed Customer records for all BNI corporate borrowers."""
	_ensure_master_data()
	created = []
	for name, segmen, industri, kbli, provinsi, grade, score, watchlist, npl, _fasilitas in BNI_CORPORATE_BORROWERS:
		if frappe.db.exists("Customer", name):
			created.append(name)
			continue
		try:
			doc = frappe.get_doc({
				"doctype": "Customer",
				"customer_name": name,
				"customer_type": "Company",
				"customer_group": segmen or "Corporate",
				"territory": provinsi,
				"industry": industri,
			})
			doc.insert(ignore_permissions=True)
			created.append(name)
		except Exception as e:
			print(f"  [SKIP] Customer {name}: {e}")
	return created


def seed_risk_profiles(customer_names):
	"""Seed CRM Risk Profile untuk setiap debitur."""
	for name, _segmen, _industri, _kbli, _provinsi, grade, score, watchlist, npl, _fasilitas in BNI_CORPORATE_BORROWERS:
		if name not in customer_names:
			continue
		existing = frappe.db.exists("CRM Risk Profile", {"customer": name})
		if existing:
			continue
		try:
			doc = frappe.get_doc({
				"doctype": "CRM Risk Profile",
				"customer": name,
				"risk_grade": grade,
				"watchlist_status": "Yes" if watchlist == "Yes" else "No",
				"npl_flag": npl,
				"internal_score": score,
				"grade_date": today(),
				"risk_factors": _generate_risk_factors(grade, industri := _industri),
			})
			doc.insert(ignore_permissions=True)
		except Exception as e:
			print(f"  [SKIP] RiskProfile {name}: {e}")


def _generate_risk_factors(grade, industri):
	if grade in ("AAA", "AA"):
		return "Strong capital structure, consistent profitability, low leverage, market leader in " + industri
	if grade in ("A", "BBB"):
		return "Adequate financial metrics, moderate leverage, stable industry position in " + industri
	if grade in ("BB", "B"):
		return "Elevated leverage, declining margin, covenant headroom tight in " + industri
	return "Distressed financial condition, covenant breach risk, negative outlook in " + industri


def _max_currency_value(table, column):
	"""Check the DB column type and return max safe value."""
	try:
		col_info = frappe.db.sql(f"SHOW COLUMNS FROM `tab{table}` WHERE Field = '{column}'", as_dict=True)
		if col_info:
			col_type = col_info[0]["Type"].lower()
			if col_type.startswith("decimal"):
				# DECIMAL(M,D) → max integer digits = M - D
				parts = col_type.replace("decimal(", "").replace(")", "").split(",")
				total_digits = int(parts[0])
				decimal_digits = int(parts[1])
				max_int_digits = total_digits - decimal_digits
				return 10 ** max_int_digits - 1
			if col_type.startswith("int") or col_type.startswith("bigint"):
				import re
				m = re.search(r"\((\d+)\)", col_type)
				if m:
					bits = int(m.group(1)) if "bigint" not in col_type else 64
					return 2 ** (bits - 1) - 1 if "unsigned" not in col_type else 2 ** bits - 1
				return 2147483647  # default INT fallback
			if "double" in col_type or "float" in col_type:
				return 999999999999999
	except Exception:
		pass
	return 999999999999999  # safe default


def seed_credit_facilities(customer_names):
	"""Seed CRM Credit Facility untuk setiap debitur."""
	max_os = _max_currency_value("CRM Credit Facility", "outstanding")
	max_lim = _max_currency_value("CRM Credit Facility", "limit_amount")
	max_safe = min(max_os, max_lim)
	scale_factor = 1
	if max_safe < 1_000_000_000_000:
		scale_factor = 1_000_000  # convert IDR → millions if column can't hold trillions
		print(f"  [FACILITY] Column max ~{max_safe:,}, scaling values by 1/{scale_factor:,}")

	for name, _segmen, _industri, _kbli, provinsi, _grade, _score, _watchlist, _npl, fasilitas in BNI_CORPORATE_BORROWERS:
		if name not in customer_names:
			continue
		for facility_type, product_type, outstanding, limit_amount, status, default_flag in fasilitas:
			existing = frappe.db.exists("CRM Credit Facility", {"customer": name, "facility_type": facility_type})
			if existing:
				continue
			try:
				os_val = outstanding // scale_factor
				lim_val = limit_amount // scale_factor
				doc = frappe.get_doc({
					"doctype": "CRM Credit Facility",
					"customer": name,
					"facility_type": facility_type,
					"product_type": product_type,
					"status": status,
					"outstanding": os_val,
					"limit_amount": lim_val,
					"default_flag": default_flag,
					"health": provinsi,
				})
				doc.insert(ignore_permissions=True)
			except Exception as e:
				print(f"  [SKIP] Facility {facility_type} for {name}: {e}")


def seed_transaction_histories(customer_names):
	"""Seed CRM Transaction History untuk mutasi rekening."""
	if not frappe.db.table_exists("CRM Transaction History"):
		return
	for name, txs in BNI_TRANSACTIONS.items():
		if name not in customer_names:
			continue
		for tx in txs:
			try:
				doc = frappe.get_doc({
					"doctype": "CRM Transaction History",
					"customer": name,
					"transaction_date": tx["date"],
					"transaction_type": tx["type"],
					"amount": tx["amount"],
					"description": tx["desc"],
					"docstatus": 0,
				})
				doc.insert(ignore_permissions=True)
			except Exception as e:
				pass


def seed_omnichannel(customer_names):
	"""Seed Omnichannel conversations antara RM dan Customer."""
	if not frappe.db.table_exists("CRM Omnichannel Conversation") or not frappe.db.table_exists("CRM Customer Communication"):
		return
	for conv in BNI_OMNICHANNEL_CONVOS:
		if conv["customer"] not in customer_names:
			continue
		try:
			comms = frappe.get_doc({
				"doctype": "CRM Customer Communication",
				"customer": conv["customer"],
				"channel": conv["channel"],
				"direction": "Inbound",
				"subject": f"Komunikasi dengan {conv['customer']} via {conv['channel']}",
				"message": conv["messages"][0][1] if conv["messages"] else "",
				"status": "Open",
				"compose_status": "Manual",
			})
			comms.insert(ignore_permissions=True)
		except Exception as e:
			pass


def seed_credit_applications(customer_names):
	"""Seed CRM Credit Application untuk pipeline kredit."""
	if not frappe.db.table_exists("CRM Credit Application"):
		return
	for app in BNI_CREDIT_APPLICATIONS:
		if frappe.db.exists("CRM Credit Application", {"borrower": app["borrower"]}):
			continue
		try:
			doc = frappe.get_doc({
				"doctype": "CRM Credit Application",
				"borrower": app["borrower"],
				"borrower_name": app["borrower"],
				"borrower_type": "Company",
				"status": app["status"],
				"facility_type": app["facility"],
				"requested_amount": app["amount"],
				"risk_grade": app["grade"],
				"tenor_months": app["tenor"],
				"industry": "Financial Services",
				"kbli": "6419",
				"purpose": f"Permohonan {app['facility']} sebesar Rp{app['amount']/1_000_000_000:.0f} Miliar",
			})
			doc.insert(ignore_permissions=True)
		except Exception as e:
			pass


def seed_credit_analysis_data():
	"""Seed CRM Credit Spread Line untuk financial spreading."""
	if not frappe.db.table_exists("CRM Credit Spread Line"):
		return
	for customer_name, statements in BNI_FINANCIAL_STATEMENTS.items():
		if not frappe.db.exists("Customer", customer_name):
			continue
		for year, metrics in statements.items():
			for metric_key, amount in metrics.items():
				existing = frappe.db.exists("CRM Credit Spread Line", {
					"customer": customer_name,
					"metric_key": metric_key,
					"year": year,
				})
				if existing:
					continue
				try:
					doc = frappe.get_doc({
						"doctype": "CRM Credit Spread Line",
						"customer": customer_name,
						"statement_type": "Audited",
						"metric_key": metric_key,
						"metric_label": metric_key.replace("_", " "),
						"year": year,
						"amount": amount,
						"source": "BNI Annual Report",
					})
					doc.insert(ignore_permissions=True)
				except Exception:
					pass


def seed_leads():
	"""Seed CRM Lead untuk prospek BNI."""
	if not frappe.db.table_exists("CRM Lead"):
		return 0
	count = 0
	for _i, (name, industry, desc, facility, amount, status) in enumerate(BNI_LEADS, start=1):
		existing = frappe.db.exists("CRM Lead", {"organization": name})
		if existing:
			continue
		try:
			lead = frappe.get_doc({
				"doctype": "CRM Lead",
				"first_name": f"Lead {_i}",
				"organization": name,
				"industry": industry,
				"website": f"https://www.{name.lower().replace(' ', '').replace('pt', '').replace('tbk', '').strip()}.com" if "pt" in name.lower() else "",
				"source": "BNI Referral",
				"status": status,
				"notes": desc + f" | Potensi fasilitas: {facility} Rp{amount/1_000_000_000:.0f} Miliar",
			})
			lead.insert(ignore_permissions=True)
			count += 1
		except Exception as e:
			pass
	return count


def seed_portfolio_tables():
	"""Seed portfolio monitoring custom tables."""
	ensure_portfolio_tables()
	from crm.demo.portfolio import (
		DEMO_EWS_SIGNALS, DEMO_COVENANTS, DEMO_WATCHLIST,
		DEMO_STRESS_SCENARIOS, DEMO_PORTFOLIO_ALERTS, DEMO_CONCENTRATION_LIMITS,
		DEMO_GRADE_MIGRATIONS, DEMO_ECL_CALCULATIONS,
	)

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


def clear_all():
	"""Bersihkan semua data seed BNI."""
	# Hapus portfolio tables
	tables = [
		"CRM EWS Signal", "CRM Covenant Test Result", "CRM Watchlist Case",
		"CRM Stress Test Scenario", "CRM Portfolio Alert", "CRM Concentration Limit",
		"CRM Risk Grade Migration", "CRM ECL Calculation", "CRM Exposure Account",
		"CRM Portfolio Snapshot", "CRM Portfolio Simulation",
	]
	for table in tables:
		if frappe.db.table_exists(table):
			frappe.db.sql(f"DELETE FROM `tab{table}`")

	# Hapus transaction histories
	if frappe.db.table_exists("CRM Transaction History"):
		for name, _txs in BNI_TRANSACTIONS.items():
			frappe.db.sql("DELETE FROM `tabCRM Transaction History` WHERE customer=%s", name)

	# Hapus credit spread lines
	if frappe.db.table_exists("CRM Credit Spread Line"):
		for name in BNI_FINANCIAL_STATEMENTS:
			frappe.db.sql("DELETE FROM `tabCRM Credit Spread Line` WHERE customer=%s", name)

	# Hapus credit applications
	if frappe.db.table_exists("CRM Credit Application"):
		for app in BNI_CREDIT_APPLICATIONS:
			existing = frappe.db.exists("CRM Credit Application", {"borrower": app["borrower"]})
			if existing:
				try:
					frappe.delete_doc("CRM Credit Application", existing, ignore_permissions=True, force=True)
				except Exception:
					pass

	# Hapus facilities
	for name, _segmen, _industri, _kbli, _provinsi, _grade, _score, _watchlist, _npl, fasilitas in BNI_CORPORATE_BORROWERS:
		for facility_type, _pt, _os, _limit, _status, _df in fasilitas:
			existing = frappe.db.exists("CRM Credit Facility", {"customer": name, "facility_type": facility_type})
			if existing:
				try:
					frappe.delete_doc("CRM Credit Facility", existing, ignore_permissions=True, force=True)
				except Exception:
					pass

	# Hapus risk profiles
	for name, _segmen, _industri, _kbli, _provinsi, _grade, _score, _watchlist, _npl, _fasilitas in BNI_CORPORATE_BORROWERS:
		existing = frappe.db.exists("CRM Risk Profile", {"customer": name})
		if existing:
			try:
				frappe.delete_doc("CRM Risk Profile", existing, ignore_permissions=True, force=True)
			except Exception:
				pass

	# Hapus omnichannel communications
	if frappe.db.table_exists("CRM Customer Communication"):
		for conv in BNI_OMNICHANNEL_CONVOS:
			frappe.db.sql("DELETE FROM `tabCRM Customer Communication` WHERE customer=%s", conv["customer"])

	# Hapus leads
	if frappe.db.table_exists("CRM Lead"):
		for name, _ind, _desc, _fac, _amt, _status in BNI_LEADS:
			existing = frappe.db.exists("CRM Lead", {"company_name": name})
			if existing:
				try:
					frappe.delete_doc("CRM Lead", existing, ignore_permissions=True, force=True)
				except Exception:
					pass

	# Hapus customers (last, karena semua relasi harus sudah dihapus)
	for name, _segmen, _industri, _kbli, _provinsi, _grade, _score, _watchlist, _npl, _fasilitas in BNI_CORPORATE_BORROWERS:
		if frappe.db.exists("Customer", name):
			try:
				frappe.delete_doc("Customer", name, ignore_permissions=True, force=True)
			except Exception:
				pass

	frappe.db.commit()


@frappe.whitelist()
def seed_all():
	"""Seed semua data BNI — semua modul terhubung."""
	clear_all()
	frappe.db.commit()

	customers = seed_customers()
	print(f"[BNI SEED] {len(customers)} customers created")

	seed_risk_profiles(customers)
	print(f"[BNI SEED] Risk profiles seeded")

	seed_credit_facilities(customers)
	print(f"[BNI SEED] Credit facilities seeded")

	seed_transaction_histories(customers)
	print(f"[BNI SEED] Transaction histories seeded")

	seed_omnichannel(customers)
	print(f"[BNI SEED] Omnichannel conversations seeded")

	seed_credit_applications(customers)
	print(f"[BNI SEED] Credit applications seeded")

	seed_credit_analysis_data()
	print(f"[BNI SEED] Credit analysis data seeded")

	lead_count = seed_leads()
	print(f"[BNI SEED] {lead_count} leads created")

	seed_portfolio_tables()
	print(f"[BNI SEED] Portfolio monitoring tables seeded")

	frappe.db.commit()
	return {
		"status": "ok",
		"customers": len(customers),
		"leads": lead_count,
		"total_borrowers": len(BNI_CORPORATE_BORROWERS),
		"message": f"BNI seed data berhasil: {len(customers)} debitur, {lead_count} leads, semua modul terhubung",
	}


@frappe.whitelist()
def seed_full():
	"""Alias untuk seed_all — panggil via bench."""
	return seed_all()
