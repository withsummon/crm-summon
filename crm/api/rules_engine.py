import frappe
from frappe import _


@frappe.whitelist()
def get_rules_list(
    category: str = "",
    status: str = "",
    module: str = "",
    search: str = "",
) -> list[dict]:
    """Return list of business rules with optional filters.

    For PoC, this returns demo data. In production, this would query
    a Rules Engine DocType.
    """
    rules = _get_demo_rules()

    if category:
        rules = [r for r in rules if r["category"] == category]
    if status:
        rules = [r for r in rules if r["status"] == status]
    if module:
        rules = [r for r in rules if r["module"] == module]
    if search:
        search_lower = search.lower()
        rules = [
            r
            for r in rules
            if search_lower in r["name"].lower()
            or search_lower in r.get("description", "").lower()
        ]

    return rules


@frappe.whitelist()
def get_rule_detail(rule_id: str) -> dict:
    """Return a single rule detail with conditions and actions.

    For PoC, returns demo data matched by rule_id.
    """
    rules = _get_demo_rules()
    for rule in rules:
        if rule["id"] == rule_id:
            return rule
    frappe.throw(_("Rule {0} not found").format(rule_id), frappe.DoesNotExistError)


@frappe.whitelist()
def simulate_rules(rule_ids: str = "", inputs: str = "") -> dict:
    """Run a simulation with given inputs against selected rules.

    For PoC, returns a plausible demo simulation result.
    """
    import json

    parsed_inputs = json.loads(inputs) if isinstance(inputs, str) else inputs
    parsed_rule_ids = (
        json.loads(rule_ids) if isinstance(rule_ids, str) else rule_ids
    )

    # Demo simulation result
    credit_score = parsed_inputs.get("credit_score", 700)
    loan_amount = parsed_inputs.get("loan_amount", 0)

    if credit_score >= 700 and loan_amount <= 5_000_000_000:
        decision = "APPROVED"
        confidence = 92
    elif credit_score >= 500:
        decision = "MANUAL_REVIEW"
        confidence = 65
    else:
        decision = "REJECTED"
        confidence = 88

    return {
        "decision": decision,
        "confidence": confidence,
        "rules_checked": len(parsed_rule_ids) if parsed_rule_ids else 8,
        "rules_passed": 6,
        "rules_failed": 1,
        "rules_skipped": 1,
        "total_time_ms": 12,
        "timeline": [
            {
                "rule": "Auto-Reject: AML/PEP Screening",
                "result": "passed",
                "duration_ms": 2,
            },
            {
                "rule": "Auto-Reject: Minimum Age",
                "result": "passed",
                "duration_ms": 1,
            },
            {
                "rule": "SME Credit Eligibility — Basic",
                "result": "passed",
                "duration_ms": 3,
            },
            {
                "rule": "SLIK Score Risk Grading",
                "result": "passed",
                "duration_ms": 2,
            },
            {
                "rule": "KMK Interest Rate Pricing",
                "result": "passed",
                "duration_ms": 2,
            },
            {
                "rule": "Large Exposure Committee Routing",
                "result": "skipped",
                "duration_ms": 1,
            },
            {
                "rule": "RM Assignment by Region",
                "result": "passed",
                "duration_ms": 1,
            },
        ],
        "outputs": {
            "risk_grade": "B+",
            "interest_rate": 12.5,
            "assigned_rm": "Budi Santoso",
            "approval_path": decision.lower().replace("_", " "),
        },
    }


@frappe.whitelist()
def get_execution_logs(
    date_range: str = "7d",
    rule_name: str = "",
    status: str = "",
    search: str = "",
) -> list[dict]:
    """Return demo execution logs.

    For PoC, returns hardcoded log entries.
    """
    logs = [
        {
            "id": f"LOG-{i:04d}",
            "timestamp": f"2026-05-24 {10 + (i % 12):02d}:{(i * 7) % 60:02d}:00",
            "rule_name": rule,
            "trigger": trigger,
            "input_summary": summary,
            "decision": decision,
            "duration_ms": duration,
            "status": log_status,
        }
        for i, (rule, trigger, summary, decision, duration, log_status) in enumerate(
            [
                ("SME Credit Eligibility", "LOS Application", "PT Maju Bersama, Rp 8.5B", "Approved", 8, "Passed"),
                ("Auto-Reject: AML/PEP", "New Lead", "Ahmad Faisal", "Passed", 3, "Passed"),
                ("KMK Interest Rate Pricing", "Credit Analysis", "CV Berkah Jaya, Rp 2B", "Rate: 11.5%", 5, "Passed"),
                ("RM Assignment by Region", "Lead Intake", "PT Nusa Indah", "RM: Budi S.", 2, "Passed"),
                ("SLIK Score Risk Grading", "Credit Check", "Siti Rahayu", "Grade: A", 4, "Passed"),
                ("Large Exposure Routing", "LOS Application", "PT Global Energi, Rp 50B", "Committee CC-2", 6, "Passed"),
                ("Collection Escalation", "DPD Update", "CV Mandiri, DPD 45", "Escalate L2", 3, "Passed"),
                ("Covenant Breach Alert", "Covenant Check", "PT Sentosa, DSCR 0.9", "Alert Sent", 7, "Passed"),
                ("NPL Early Warning", "Portfolio Scan", "PT Delta Corp, DPD 62", "Flag NPL", 5, "Passed"),
                ("Auto-Reject: Min Age", "Lead Intake", "Andi Pratama, Age 19", "Rejected", 1, "Passed"),
                ("SME Credit Eligibility", "LOS Application", "PT Karya Utama, Rp 1.2B", "Error", 15, "Error"),
                ("KPR Eligibility", "LOS Application", "Dewi Safitri, Rp 800M", "Approved", 9, "Passed"),
                ("Branch Routing Jakarta", "Lead Intake", "PT Metro Jaya", "Branch: Sudirman", 2, "Passed"),
                ("Restructuring Eligibility", "Collection Review", "CV Prima, DPD 95", "Eligible", 6, "Passed"),
                ("Dynamic Pricing Collateral", "Credit Analysis", "PT Abadi, SHM Rp 5B", "Adj: -0.5%", 4, "Passed"),
            ]
        )
    ]

    if status and status != "All":
        logs = [l for l in logs if l["status"] == status]
    if rule_name:
        logs = [l for l in logs if rule_name.lower() in l["rule_name"].lower()]

    return logs


@frappe.whitelist()
def get_rules_analytics() -> dict:
    """Return analytics data for the Rules Engine dashboard.

    For PoC, returns hardcoded analytics.
    """
    return {
        "kpis": {
            "active_rules": 38,
            "avg_hit_rate": 73.2,
            "avg_latency_ms": 8,
            "exception_rate": 2.4,
        },
        "execution_volume": [
            {"rule": "RM Assignment by Region", "count": 456, "pct": 100},
            {"rule": "SME Credit Eligibility", "count": 398, "pct": 87},
            {"rule": "Auto-Reject: AML/PEP", "count": 387, "pct": 85},
            {"rule": "SLIK Score Risk Grading", "count": 345, "pct": 76},
            {"rule": "KMK Interest Rate Pricing", "count": 312, "pct": 68},
            {"rule": "KPR Eligibility", "count": 278, "pct": 61},
            {"rule": "Branch Routing Jakarta", "count": 234, "pct": 51},
            {"rule": "Collection Escalation", "count": 189, "pct": 41},
            {"rule": "Large Exposure Routing", "count": 156, "pct": 34},
            {"rule": "NPL Early Warning", "count": 98, "pct": 21},
        ],
        "hit_rate_by_category": [
            {"category": "Routing", "rate": 91, "color": "purple"},
            {"category": "Eligibility", "rate": 82, "color": "green"},
            {"category": "Credit Risk", "rate": 79, "color": "red"},
            {"category": "Pricing", "rate": 76, "color": "blue"},
            {"category": "Exception", "rate": 45, "color": "orange"},
            {"category": "Rejection", "rate": 12, "color": "red"},
        ],
        "decision_distribution": {
            "approved": 62,
            "manual_review": 24,
            "rejected": 11,
            "error": 3,
        },
        "monthly_trend": [
            {"month": "Dec", "count": 3420},
            {"month": "Jan", "count": 3890},
            {"month": "Feb", "count": 4120},
            {"month": "Mar", "count": 4560},
            {"month": "Apr", "count": 4890},
            {"month": "May", "count": 5234},
        ],
    }


def _get_demo_rules() -> list[dict]:
    """Internal helper returning demo rules data."""
    return [
        {
            "id": "RULE-001",
            "name": "SME Credit Eligibility — Basic",
            "category": "Eligibility",
            "module": "LOS",
            "status": "Active",
            "version": "v3.2",
            "lastModified": "2026-05-20",
            "hitRate": 89,
            "priority": 1,
            "description": "Basic eligibility check for SME credit applications including age, credit score, income, and loan amount thresholds.",
        },
        {
            "id": "RULE-002",
            "name": "KMK Interest Rate Pricing",
            "category": "Pricing",
            "module": "LOS",
            "status": "Active",
            "version": "v2.1",
            "lastModified": "2026-05-18",
            "hitRate": 76,
            "priority": 2,
            "description": "Determines interest rate for Kredit Modal Kerja based on risk grade, collateral coverage, and tenor.",
        },
        {
            "id": "RULE-003",
            "name": "Auto-Reject: AML/PEP Screening",
            "category": "Rejection",
            "module": "CRM",
            "status": "Active",
            "version": "v1.5",
            "lastModified": "2026-05-15",
            "hitRate": 12,
            "priority": 0,
            "description": "Automatically rejects leads/applications flagged by AML/PEP screening databases.",
        },
        {
            "id": "RULE-004",
            "name": "RM Assignment by Region",
            "category": "Routing",
            "module": "CRM",
            "status": "Active",
            "version": "v4.0",
            "lastModified": "2026-05-22",
            "hitRate": 94,
            "priority": 3,
            "description": "Routes incoming leads to Relationship Managers based on geographic region and product specialization.",
        },
        {
            "id": "RULE-005",
            "name": "Large Exposure Committee Routing",
            "category": "Routing",
            "module": "LOS",
            "status": "Active",
            "version": "v2.3",
            "lastModified": "2026-05-19",
            "hitRate": 34,
            "priority": 2,
            "description": "Routes applications exceeding credit authority thresholds to the appropriate committee level.",
        },
        {
            "id": "RULE-006",
            "name": "KPR Eligibility — Employee",
            "category": "Eligibility",
            "module": "LOS",
            "status": "Active",
            "version": "v1.8",
            "lastModified": "2026-05-17",
            "hitRate": 82,
            "priority": 2,
            "description": "Eligibility criteria for KPR (housing loan) applications from salaried employees.",
        },
        {
            "id": "RULE-007",
            "name": "Collection Escalation Trigger",
            "category": "Exception",
            "module": "Collections",
            "status": "Active",
            "version": "v2.0",
            "lastModified": "2026-05-21",
            "hitRate": 45,
            "priority": 1,
            "description": "Triggers escalation workflow when collection DPD thresholds are breached.",
        },
        {
            "id": "RULE-008",
            "name": "Covenant Breach Auto-Alert",
            "category": "Exception",
            "module": "LOS",
            "status": "Active",
            "version": "v1.2",
            "lastModified": "2026-05-14",
            "hitRate": 18,
            "priority": 1,
            "description": "Sends automated alerts when financial covenant ratios (DSCR, DER) breach thresholds.",
        },
        {
            "id": "RULE-009",
            "name": "SLIK Score Risk Grading",
            "category": "Credit Risk",
            "module": "LOS",
            "status": "Active",
            "version": "v3.0",
            "lastModified": "2026-05-23",
            "hitRate": 91,
            "priority": 1,
            "description": "Maps SLIK (OJK credit bureau) scores to internal risk grades (A through E).",
        },
        {
            "id": "RULE-010",
            "name": "Personal Loan Quick Approval",
            "category": "Eligibility",
            "module": "LOS",
            "status": "Pending Approval",
            "version": "v1.0",
            "lastModified": "2026-05-24",
            "hitRate": None,
            "priority": 2,
            "description": "Fast-track approval for personal loans under Rp 200M for existing customers with good history.",
        },
        {
            "id": "RULE-011",
            "name": "NPL Early Warning Detection",
            "category": "Credit Risk",
            "module": "Collections",
            "status": "Active",
            "version": "v2.5",
            "lastModified": "2026-05-16",
            "hitRate": 67,
            "priority": 1,
            "description": "Detects early warning signals for potential NPL based on payment patterns and financial indicators.",
        },
        {
            "id": "RULE-012",
            "name": "Dynamic Pricing — Collateral Adj",
            "category": "Pricing",
            "module": "LOS",
            "status": "Draft",
            "version": "v0.3",
            "lastModified": "2026-05-24",
            "hitRate": None,
            "priority": 3,
            "description": "Adjusts interest rate based on collateral type and loan-to-value ratio.",
        },
        {
            "id": "RULE-013",
            "name": "Branch Routing — Jakarta",
            "category": "Routing",
            "module": "CRM",
            "status": "Active",
            "version": "v1.1",
            "lastModified": "2026-05-13",
            "hitRate": 88,
            "priority": 4,
            "description": "Routes Jakarta-area leads to specific branch offices based on sub-region mapping.",
        },
        {
            "id": "RULE-014",
            "name": "Restructuring Eligibility Check",
            "category": "Eligibility",
            "module": "Collections",
            "status": "Active",
            "version": "v1.4",
            "lastModified": "2026-05-12",
            "hitRate": 55,
            "priority": 2,
            "description": "Evaluates whether a delinquent borrower qualifies for loan restructuring based on OJK guidelines.",
        },
        {
            "id": "RULE-015",
            "name": "Auto-Reject: Minimum Age",
            "category": "Rejection",
            "module": "LOS",
            "status": "Archived",
            "version": "v1.0",
            "lastModified": "2026-04-01",
            "hitRate": 8,
            "priority": 0,
            "description": "Rejects applicants under minimum age threshold (superseded by SME Credit Eligibility rule).",
        },
    ]
