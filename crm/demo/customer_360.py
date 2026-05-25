"""
Demo data for Customer 360: individual borrowers with varied risk profiles,
KYC records, bureau scores, credit facilities, and transaction histories.
"""

from datetime import date, timedelta

import frappe

TODAY = date.today()


def _d(days_ago):
    return str(TODAY - timedelta(days=days_ago))


# 8 individual customers — varied score range, demographics, and risk profiles
DEMO_C360_CUSTOMERS = [
    {
        "customer_name": "Anisa Putri",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 812 1001 0001",
        "email_id": "anisa.putri@example.com",
        # KYC
        "nik": "3175015504900001",
        "npwp": "12.345.678.9-001.000",
        "date_of_birth": "1990-04-15",
        "registered_address": "Jl. Sudirman No. 12, Jakarta Pusat, DKI Jakarta 10220",
        "kyc_status": "Verified",
        "next_review_date": _d(-120),  # overdue
        "ekyc_result": "Verified",
        "watchlist": False,
        # Bureau
        "bureau_score": 810,
        "bureau_kol": "Lancar",
        "bureau_source": "PEFINDO",
        # Risk
        "risk_grade": "A",
        "internal_score": 820,
        "risk_factors": "Stable employment; low DTI ratio; consistent repayment record.",
        # Facilities
        "facilities": [
            {
                "facility_type": "KPR (Home Mortgage)",
                "product_type": "Retail Mortgage",
                "status": "Active",
                "outstanding": 450_000_000,
                "limit_amount": 600_000_000,
                "ltv_percent": 75,
                "health": "Good",
                "due_date": _d(-365 * -3),
                "repayment_behavior": "Always on time",
            },
            {
                "facility_type": "Kartu Kredit",
                "product_type": "Consumer Credit",
                "status": "Active",
                "outstanding": 8_500_000,
                "limit_amount": 50_000_000,
                "ltv_percent": 17,
                "health": "Good",
                "due_date": _d(-365 * -2),
                "repayment_behavior": "Fully paid monthly",
            },
        ],
        "missed_payments": 0,
        "documents": [
            {"document_type": "KTP", "title": "KTP Anisa Putri", "expiry_status": "Valid"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Valid"},
            {"document_type": "Slip Gaji", "title": "Payslip Q1 2025", "expiry_status": "Valid"},
        ],
        "ai_summary": "Anisa Putri is a premium borrower with an A-grade risk profile and bureau score of 810. Active KPR (Rp 450M outstanding) and credit card facility are both performing well. KYC is overdue for renewal — initiate review. No watchlist flags.",
    },
    {
        "customer_name": "Budi Hermawan",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 813 1002 0002",
        "email_id": "budi.hermawan@example.com",
        "nik": "3578021203850002",
        "npwp": "23.456.789.0-002.000",
        "date_of_birth": "1985-03-12",
        "registered_address": "Jl. Gatot Subroto No. 45, Jakarta Selatan, DKI Jakarta 12930",
        "kyc_status": "Verified",
        "next_review_date": _d(-180),
        "ekyc_result": "Verified",
        "watchlist": False,
        "bureau_score": 740,
        "bureau_kol": "Lancar",
        "bureau_source": "SLIK/OJK Manual Upload",
        "risk_grade": "A-",
        "internal_score": 745,
        "risk_factors": "Long credit history; minor late payment 18 months ago (self-corrected).",
        "facilities": [
            {
                "facility_type": "Kredit Modal Kerja",
                "product_type": "Working Capital",
                "status": "Active",
                "outstanding": 200_000_000,
                "limit_amount": 250_000_000,
                "ltv_percent": 80,
                "health": "Good",
                "due_date": _d(-365 * -1),
                "repayment_behavior": "Mostly on time; 1 late in 2023",
            },
        ],
        "missed_payments": 0,
        "documents": [
            {"document_type": "KTP", "title": "KTP Budi Hermawan", "expiry_status": "Valid"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Valid"},
            {"document_type": "Rekening Koran", "title": "Bank Statement 6 months", "expiry_status": "Valid"},
        ],
        "ai_summary": "Budi Hermawan holds a working capital facility in good standing. Risk grade A- with a minor repayment blemish in 2023 that has since self-corrected. KYC requires renewal — overdue by 6 months.",
    },
    {
        "customer_name": "Citra Lestari",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 821 1003 0003",
        "email_id": "citra.lestari@example.com",
        "nik": "3374056706920003",
        "npwp": "34.567.890.1-003.000",
        "date_of_birth": "1992-06-07",
        "registered_address": "Jl. Pemuda No. 88, Semarang, Jawa Tengah 50132",
        "kyc_status": "Pending",
        "next_review_date": _d(-30),
        "ekyc_result": "Manual",
        "watchlist": False,
        "bureau_score": 670,
        "bureau_kol": "Dalam Perhatian Khusus",
        "bureau_source": "PEFINDO",
        "risk_grade": "B+",
        "internal_score": 665,
        "risk_factors": "Increasing utilization on revolving facility; income seasonality noted.",
        "facilities": [
            {
                "facility_type": "KTA (Personal Loan)",
                "product_type": "Unsecured Personal",
                "status": "Active",
                "outstanding": 75_000_000,
                "limit_amount": 100_000_000,
                "ltv_percent": 75,
                "health": "Watch",
                "due_date": _d(-365 * -1),
                "repayment_behavior": "Occasional delays of 5-10 days",
            },
        ],
        "missed_payments": 1,
        "documents": [
            {"document_type": "KTP", "title": "KTP Citra Lestari", "expiry_status": "Valid"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Expired"},
            {"document_type": "Slip Gaji", "title": "Payslip Q3 2024", "expiry_status": "Expired"},
        ],
        "ai_summary": "Citra Lestari's profile shows increasing risk — bureau status has moved to 'Dalam Perhatian Khusus' and KYC renewal is overdue by 30 days. Two expired documents on file. One missed payment recorded. Recommend proactive outreach and facility review.",
    },
    {
        "customer_name": "Dimas Pratama",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 878 1004 0004",
        "email_id": "dimas.pratama@example.com",
        "nik": "3578031501870004",
        "npwp": "45.678.901.2-004.000",
        "date_of_birth": "1987-01-15",
        "registered_address": "Jl. Asia Afrika No. 5, Bandung, Jawa Barat 40111",
        "kyc_status": "Verified",
        "next_review_date": _d(-365 * -1),
        "ekyc_result": "Verified",
        "watchlist": False,
        "bureau_score": 780,
        "bureau_kol": "Lancar",
        "bureau_source": "SLIK/OJK Manual Upload",
        "risk_grade": "A",
        "internal_score": 775,
        "risk_factors": "Strong cash flow; diversified income streams; fully collateralized.",
        "facilities": [
            {
                "facility_type": "KPR (Home Mortgage)",
                "product_type": "Retail Mortgage",
                "status": "Active",
                "outstanding": 850_000_000,
                "limit_amount": 1_000_000_000,
                "ltv_percent": 85,
                "health": "Good",
                "due_date": _d(-365 * -5),
                "repayment_behavior": "Perfect payment history",
            },
            {
                "facility_type": "Kredit Investasi",
                "product_type": "Investment Loan",
                "status": "Active",
                "outstanding": 300_000_000,
                "limit_amount": 400_000_000,
                "ltv_percent": 75,
                "health": "Good",
                "due_date": _d(-365 * -2),
                "repayment_behavior": "Always on time",
            },
        ],
        "missed_payments": 0,
        "documents": [
            {"document_type": "KTP", "title": "KTP Dimas Pratama", "expiry_status": "Valid"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Valid"},
            {"document_type": "Akta Nikah", "title": "Marriage Certificate", "expiry_status": "Valid"},
            {"document_type": "Rekening Koran", "title": "Bank Statement 12 months", "expiry_status": "Valid"},
        ],
        "ai_summary": "Dimas Pratama is a high-value customer with two active facilities totalling Rp 1.15B outstanding. Perfect repayment record and A-grade risk profile. KYC is current. Strong candidate for cross-selling additional products.",
    },
    {
        "customer_name": "Eka Susanti",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 856 1005 0005",
        "email_id": "eka.susanti@example.com",
        "nik": "3578056208950005",
        "npwp": "56.789.012.3-005.000",
        "date_of_birth": "1995-08-22",
        "registered_address": "Jl. Malioboro No. 33, Yogyakarta, DIY 55271",
        "kyc_status": "Verified",
        "next_review_date": _d(-365 * -2),
        "ekyc_result": "Verified",
        "watchlist": False,
        "bureau_score": 720,
        "bureau_kol": "Lancar",
        "bureau_source": "PEFINDO",
        "risk_grade": "B+",
        "internal_score": 715,
        "risk_factors": "Young borrower; limited credit history; stable employment as civil servant.",
        "facilities": [
            {
                "facility_type": "KTA (Personal Loan)",
                "product_type": "Unsecured Personal",
                "status": "Active",
                "outstanding": 40_000_000,
                "limit_amount": 50_000_000,
                "ltv_percent": 80,
                "health": "Good",
                "due_date": _d(-365 * -1),
                "repayment_behavior": "Always on time",
            },
        ],
        "missed_payments": 0,
        "documents": [
            {"document_type": "KTP", "title": "KTP Eka Susanti", "expiry_status": "Valid"},
            {"document_type": "SK PNS", "title": "Civil Servant Decree", "expiry_status": "Valid"},
        ],
        "ai_summary": "Eka Susanti is a young civil servant borrower with a solid repayment record. Limited credit history contributes to B+ rating; expected to improve over time. Current KTA facility is healthy. No outstanding issues.",
    },
    {
        "customer_name": "Fajar Nugroho",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 877 1006 0006",
        "email_id": "fajar.nugroho@example.com",
        "nik": "3578041209820006",
        "npwp": "67.890.123.4-006.000",
        "date_of_birth": "1982-09-12",
        "registered_address": "Jl. Ahmad Yani No. 78, Surabaya, Jawa Timur 60171",
        "kyc_status": "Expired",
        "next_review_date": _d(60),  # overdue past
        "ekyc_result": "Manual",
        "watchlist": True,
        "watchlist_reason": "Flagged in OJK SLIK for prior NPL — currently under monitoring.",
        "bureau_score": 490,
        "bureau_kol": "Macet",
        "bureau_source": "SLIK/OJK Manual Upload",
        "risk_grade": "C",
        "internal_score": 480,
        "risk_factors": "Prior NPL on consumer loan (settled 2022). Watchlist flag. KYC expired. Employment status unverified.",
        "early_warning": "OJK SLIK NPL flag; KYC expired >60 days; 3 missed payments in trailing 12 months.",
        "facilities": [
            {
                "facility_type": "KTA (Personal Loan)",
                "product_type": "Unsecured Personal",
                "status": "Restructured",
                "outstanding": 95_000_000,
                "limit_amount": 100_000_000,
                "ltv_percent": 95,
                "health": "Substandard",
                "due_date": _d(-365 * -1),
                "default_flag": True,
                "repayment_behavior": "3 missed payments; restructured in Q3 2024",
            },
        ],
        "missed_payments": 3,
        "documents": [
            {"document_type": "KTP", "title": "KTP Fajar Nugroho", "expiry_status": "Expired"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Expired"},
        ],
        "ai_summary": "Fajar Nugroho is a high-risk borrower flagged on the watchlist due to a prior NPL and OJK SLIK flag. KYC is expired. Facility has been restructured with 3 missed payments recorded. Immediate action required: KYC renewal, account review, and escalation to risk committee.",
    },
    {
        "customer_name": "Gita Maharani",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 811 1007 0007",
        "email_id": "gita.maharani@example.com",
        "nik": "3175065507880007",
        "npwp": "78.901.234.5-007.000",
        "date_of_birth": "1988-07-15",
        "registered_address": "Jl. Diponegoro No. 22, Medan, Sumatera Utara 20151",
        "kyc_status": "Verified",
        "next_review_date": _d(-365 * -1),
        "ekyc_result": "Verified",
        "watchlist": False,
        "bureau_score": 575,
        "bureau_kol": "Kurang Lancar",
        "bureau_source": "PEFINDO",
        "risk_grade": "B",
        "internal_score": 570,
        "risk_factors": "Moderate utilization; two facilities with overlapping repayment schedules; income documentation incomplete.",
        "facilities": [
            {
                "facility_type": "Kartu Kredit",
                "product_type": "Consumer Credit",
                "status": "Active",
                "outstanding": 18_000_000,
                "limit_amount": 25_000_000,
                "ltv_percent": 72,
                "health": "Watch",
                "due_date": _d(-365 * -1),
                "repayment_behavior": "Minimum payments only; high utilization",
            },
            {
                "facility_type": "KTA (Personal Loan)",
                "product_type": "Unsecured Personal",
                "status": "Active",
                "outstanding": 55_000_000,
                "limit_amount": 60_000_000,
                "ltv_percent": 91,
                "health": "Watch",
                "due_date": _d(-365 * -1),
                "repayment_behavior": "Occasional 5-15 day delays",
            },
        ],
        "missed_payments": 1,
        "documents": [
            {"document_type": "KTP", "title": "KTP Gita Maharani", "expiry_status": "Valid"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Valid"},
            {"document_type": "Slip Gaji", "title": "Payslip Q2 2024", "expiry_status": "Expired"},
        ],
        "ai_summary": "Gita Maharani carries two facilities with high utilization and overlapping repayment schedules. Bureau status 'Kurang Lancar' indicates emerging risk. One missed payment and one expired document. Recommend income documentation update and debt consolidation discussion.",
    },
    {
        "customer_name": "Hendra Wijaya",
        "customer_type": "Individual",
        "customer_group": "Commercial",
        "territory": "Indonesia",
        "mobile_no": "+62 852 1008 0008",
        "email_id": "hendra.wijaya@example.com",
        "nik": "3578031008780008",
        "npwp": "89.012.345.6-008.000",
        "date_of_birth": "1978-08-10",
        "registered_address": "Jl. Pahlawan No. 15, Makassar, Sulawesi Selatan 90111",
        "kyc_status": "Verified",
        "next_review_date": _d(-365 * -1),
        "ekyc_result": "Verified",
        "watchlist": False,
        "bureau_score": 850,
        "bureau_kol": "Lancar",
        "bureau_source": "PEFINDO",
        "risk_grade": "AAA",
        "internal_score": 855,
        "risk_factors": "Excellent credit history; fully collateralized; low DTI; senior management profile.",
        "facilities": [
            {
                "facility_type": "KPR (Home Mortgage)",
                "product_type": "Retail Mortgage",
                "status": "Active",
                "outstanding": 1_200_000_000,
                "limit_amount": 1_500_000_000,
                "ltv_percent": 80,
                "health": "Excellent",
                "due_date": _d(-365 * -7),
                "repayment_behavior": "Perfect — auto-debit for 7 years",
            },
            {
                "facility_type": "Kredit Investasi",
                "product_type": "Investment Loan",
                "status": "Active",
                "outstanding": 500_000_000,
                "limit_amount": 600_000_000,
                "ltv_percent": 83,
                "health": "Excellent",
                "due_date": _d(-365 * -3),
                "repayment_behavior": "Always on time",
            },
            {
                "facility_type": "Kredit Modal Kerja",
                "product_type": "Working Capital",
                "status": "Active",
                "outstanding": 250_000_000,
                "limit_amount": 300_000_000,
                "ltv_percent": 83,
                "health": "Good",
                "due_date": _d(-365 * -1),
                "repayment_behavior": "Always on time",
            },
        ],
        "missed_payments": 0,
        "documents": [
            {"document_type": "KTP", "title": "KTP Hendra Wijaya", "expiry_status": "Valid"},
            {"document_type": "NPWP", "title": "NPWP Certificate", "expiry_status": "Valid"},
            {"document_type": "Akta Pendirian", "title": "Business Registration", "expiry_status": "Valid"},
            {"document_type": "Rekening Koran", "title": "Bank Statement 12 months", "expiry_status": "Valid"},
            {"document_type": "Laporan Keuangan", "title": "Audited Financials 2024", "expiry_status": "Valid"},
        ],
        "ai_summary": "Hendra Wijaya is the highest-rated borrower in the portfolio with AAA risk grade and bureau score of 850. Three active facilities totalling Rp 1.95B outstanding — all performing perfectly. Prime candidate for relationship deepening and premium product offers.",
    },
]

DEMO_C360_CUSTOMER_NAMES = [c["customer_name"] for c in DEMO_C360_CUSTOMERS]


def _insert_if_doctype_ready(data):
    doctype = data["doctype"]
    if not frappe.db.table_exists(doctype):
        return None
    return frappe.get_doc(data).insert(ignore_permissions=True)


def create_demo_customer_360():
    created_customers = []
    created_kyc = []
    created_bureaus = []
    created_risks = []
    created_facilities = []
    created_transactions = []
    created_documents = []
    created_ai_insights = []

    for p in DEMO_C360_CUSTOMERS:
        # Customer
        if not frappe.db.exists("Customer", p["customer_name"]):
            cust = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": p["customer_name"],
                "customer_type": p["customer_type"],
                "customer_group": p.get("customer_group", "Commercial"),
                "territory": p.get("territory", "Indonesia"),
                "mobile_no": p.get("mobile_no"),
                "email_id": p.get("email_id"),
            }).insert(ignore_permissions=True)
            cname = cust.name
        else:
            cname = p["customer_name"]
        created_customers.append(cname)

        # KYC Review
        doc = _insert_if_doctype_ready({
            "doctype": "CRM KYC Review",
            "customer": cname,
            "status": p.get("kyc_status", "Pending"),
            "review_date": _d(180),
            "next_review_date": p.get("next_review_date"),
            "npwp": p.get("npwp"),
            "nik": p.get("nik"),
            "date_of_birth": p.get("date_of_birth"),
            "registered_address": p.get("registered_address"),
            "ekyc_result": p.get("ekyc_result", "Manual"),
            "watchlist": 1 if p.get("watchlist") else 0,
            "watchlist_reason": p.get("watchlist_reason"),
        })
        if doc:
            created_kyc.append(doc.name)

        # Bureau Report
        doc = _insert_if_doctype_ready({
            "doctype": "CRM Bureau Report",
            "customer": cname,
            "source": p.get("bureau_source", "PEFINDO"),
            "report_date": _d(30),
            "kol_status": p.get("bureau_kol", "Lancar"),
            "score": p.get("bureau_score", 0),
            "notes": f"Bureau report for {p['customer_name']}. KOL: {p.get('bureau_kol')}.",
        })
        if doc:
            created_bureaus.append(doc.name)

        # Risk Profile
        doc = _insert_if_doctype_ready({
            "doctype": "CRM Risk Profile",
            "customer": cname,
            "risk_grade": p.get("risk_grade", "Unrated"),
            "internal_score": p.get("internal_score", 0),
            "watchlist_status": "Yes" if p.get("watchlist") else "No",
            "npl_flag": 1 if p.get("bureau_kol") == "Macet" else 0,
            "grade_date": _d(14),
            "risk_factors": p.get("risk_factors"),
            "early_warning_triggers": p.get("early_warning"),
        })
        if doc:
            created_risks.append(doc.name)

        # Credit Facilities + Transactions
        for fac_data in p.get("facilities", []):
            fac_doc = _insert_if_doctype_ready({
                "doctype": "CRM Credit Facility",
                "customer": cname,
                "facility_type": fac_data["facility_type"],
                "product_type": fac_data.get("product_type"),
                "status": fac_data.get("status", "Active"),
                "due_date": fac_data.get("due_date"),
                "outstanding": fac_data.get("outstanding", 0),
                "limit_amount": fac_data.get("limit_amount", 0),
                "ltv_percent": fac_data.get("ltv_percent", 0),
                "health": fac_data.get("health", "Good"),
                "default_flag": 1 if fac_data.get("default_flag") else 0,
                "repayment_behavior": fac_data.get("repayment_behavior"),
            })
            if fac_doc:
                created_facilities.append(fac_doc.name)

                # Transactions: 3 on-time repayments, then missed if applicable
                for i in range(3):
                    tx_doc = _insert_if_doctype_ready({
                        "doctype": "CRM Transaction History",
                        "customer": cname,
                        "facility": fac_doc.name,
                        "transaction_date": _d(30 * (i + 1)),
                        "transaction_type": "Repayment",
                        "amount": round(fac_data.get("outstanding", 0) / 24),
                        "running_balance": round(fac_data.get("outstanding", 0) * (1 - (i + 1) * 0.04)),
                        "status": "Posted",
                    })
                    if tx_doc:
                        created_transactions.append(tx_doc.name)

                for _ in range(p.get("missed_payments", 0)):
                    tx_doc = _insert_if_doctype_ready({
                        "doctype": "CRM Transaction History",
                        "customer": cname,
                        "facility": fac_doc.name,
                        "transaction_date": _d(7),
                        "transaction_type": "Missed Payment",
                        "amount": round(fac_data.get("outstanding", 0) / 24),
                        "running_balance": fac_data.get("outstanding", 0),
                        "status": "Failed",
                        "notes": "Payment not received by due date.",
                    })
                    if tx_doc:
                        created_transactions.append(tx_doc.name)

        # Documents — document_type must be one of: KYC, Financial, Collateral, Legal, Visit, Other
        _doc_type_map = {
            "KTP": "KYC", "NPWP": "KYC", "SK PNS": "KYC", "Akta Nikah": "Legal",
            "Akta Pendirian": "Legal", "Slip Gaji": "Financial", "Rekening Koran": "Financial",
            "Laporan Keuangan": "Financial",
        }
        for doc_data in p.get("documents", []):
            raw_type = doc_data.get("document_type", "Other")
            mapped_type = _doc_type_map.get(raw_type, "Other")
            doc = _insert_if_doctype_ready({
                "doctype": "CRM Customer Document",
                "customer": cname,
                "document_type": mapped_type,
                "title": doc_data.get("title"),
                "expiry_status": doc_data.get("expiry_status", "Valid"),
                "expiry_date": _d(-30) if doc_data.get("expiry_status") == "Expired" else _d(-365 * -2),
            })
            if doc:
                created_documents.append(doc.name)

        # AI Insight note (saved summary)
        if p.get("ai_summary"):
            note_doc = frappe.get_doc({
                "doctype": "FCRM Note",
                "title": "AI Customer Summary",
                "content": p["ai_summary"],
                "reference_doctype": "Customer",
                "reference_docname": cname,
            }).insert(ignore_permissions=True)
            created_ai_insights.append(note_doc.name)

    frappe.db.commit()
    return {
        "customers": created_customers,
        "kyc": created_kyc,
        "bureaus": created_bureaus,
        "risks": created_risks,
        "facilities": created_facilities,
        "transactions": created_transactions,
        "documents": created_documents,
        "notes": created_ai_insights,
    }


def delete_demo_customer_360(data):
    for name in data.get("notes", []):
        if frappe.db.exists("FCRM Note", name):
            frappe.delete_doc("FCRM Note", name, ignore_permissions=True, force=True)

    for doctype, key in [
        ("CRM Transaction History", "transactions"),
        ("CRM Customer Document", "documents"),
        ("CRM Credit Facility", "facilities"),
        ("CRM Risk Profile", "risks"),
        ("CRM Bureau Report", "bureaus"),
        ("CRM KYC Review", "kyc"),
    ]:
        if not frappe.db.table_exists(doctype):
            continue
        for name in data.get(key, []):
            if frappe.db.exists(doctype, name):
                frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)

    for name in data.get("customers", []):
        if frappe.db.exists("Customer", name):
            frappe.delete_doc("Customer", name, ignore_permissions=True, force=True)

    frappe.db.commit()
