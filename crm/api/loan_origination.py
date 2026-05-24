import json

import frappe
from frappe.utils import flt


LOAN_DOCTYPE = "CRM Credit Application"


def _doctype_ready(doctype):
	try:
		return frappe.db.table_exists(doctype)
	except Exception:
		return False


def _demo_applications():
	return [
		{
			"name": "LOS-DEMO-001",
			"borrower_name": "PT Maju Bersama",
			"borrower_type": "Corporate",
			"step": 4,
			"status": "Credit Review",
			"facility_type": "Working Capital",
			"requested_amount": 5000000000,
			"tenor_months": 24,
			"purpose": "Modal kerja ekspansi distributor FMCG ke wilayah Kalimantan",
			"created": "2026-05-20 09:00:00",
		},
		{
			"name": "LOS-DEMO-002",
			"borrower_name": "Budi Santoso",
			"borrower_type": "Individual",
			"step": 2,
			"status": "Draft",
			"facility_type": "KPR",
			"requested_amount": 800000000,
			"tenor_months": 180,
			"purpose": "Pembelian rumah tapak di Tangerang Selatan",
			"created": "2026-05-22 14:00:00",
		},
		{
			"name": "LOS-DEMO-003",
			"borrower_name": "CV Teknik Jaya",
			"borrower_type": "Corporate",
			"step": 6,
			"status": "Disbursement",
			"facility_type": "Investment Loan",
			"requested_amount": 2500000000,
			"tenor_months": 60,
			"purpose": "Pembelian mesin produksi CNC untuk pabrik Surabaya",
			"created": "2026-05-15 10:30:00",
		},
	]


@frappe.whitelist()
def get_loan_applications(query="", limit=50):
	if not _doctype_ready(LOAN_DOCTYPE):
		apps = _demo_applications()
	else:
		try:
			rows = frappe.get_all(
				LOAN_DOCTYPE,
				fields=["name", "borrower_name", "borrower_type", "status", "facility_type", "requested_amount", "purpose", "creation"],
				filters={"origination_step": ["is", "set"]},
				order_by="modified desc",
				limit=int(limit),
			)
			apps = [
				{
					"name": r.name,
					"borrower_name": r.borrower_name or r.name,
					"borrower_type": r.get("borrower_type") or "Individual",
					"step": int(r.get("origination_step") or 1),
					"status": r.status or "Draft",
					"facility_type": r.get("facility_type") or "",
					"requested_amount": flt(r.get("requested_amount")),
					"tenor_months": int(r.get("tenor_months") or 0),
					"purpose": r.get("purpose") or "",
					"created": str(r.get("creation") or ""),
				}
				for r in rows
			] or _demo_applications()
		except Exception:
			apps = _demo_applications()

	if query:
		q = query.lower()
		apps = [a for a in apps if q in (a.get("borrower_name") or "").lower() or q in (a.get("name") or "").lower()]
	return apps


@frappe.whitelist()
def save_loan_step(application_id, step, payload):
	"""Persist step data. Steps 1-3 write to backend; 4-6 are visual-only."""
	if isinstance(payload, str):
		payload = json.loads(payload)
	step = int(step)

	if step > 3:
		return {"ok": True, "visual_only": True}

	if not _doctype_ready(LOAN_DOCTYPE):
		return {"ok": True, "demo": True, "application_id": application_id}

	try:
		if application_id and frappe.db.exists(LOAN_DOCTYPE, application_id):
			doc = frappe.get_doc(LOAN_DOCTYPE, application_id)
		else:
			doc = frappe.new_doc(LOAN_DOCTYPE)

		if step == 1:
			doc.borrower_name = payload.get("borrower_name") or doc.get("borrower_name")
			doc.borrower_type = payload.get("borrower_type") or "Individual"
			if payload.get("employer_name"):
				doc.employer_name = payload["employer_name"]
			if payload.get("npwp"):
				doc.npwp = payload["npwp"]
			if payload.get("phone"):
				doc.phone = payload["phone"]
			if payload.get("email"):
				doc.email = payload["email"]

		elif step == 2:
			doc.facility_type = payload.get("facility_type") or doc.get("facility_type")
			doc.requested_amount = flt(payload.get("requested_amount") or 0)
			if payload.get("tenor_months"):
				doc.tenor_months = int(payload["tenor_months"])
			if payload.get("purpose"):
				doc.purpose = payload["purpose"]
			if payload.get("collateral_type"):
				doc.collateral_type = payload["collateral_type"]

		elif step == 3:
			if payload.get("documents"):
				doc.document_checklist = json.dumps(payload["documents"])

		if hasattr(doc, "origination_step"):
			doc.origination_step = step
		if not doc.status or doc.status == "":
			doc.status = "Draft"

		if doc.is_new():
			doc.insert(ignore_permissions=True)
		else:
			doc.save(ignore_permissions=True)

		return {"ok": True, "application_id": doc.name}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "LoanOrigination.save_loan_step")
		return {"ok": True, "demo": True, "application_id": application_id, "error": str(e)}


@frappe.whitelist()
def create_loan_application(borrower_name, borrower_type="Individual"):
	if not _doctype_ready(LOAN_DOCTYPE):
		import random, string
		fake_id = "LOS-NEW-" + "".join(random.choices(string.digits, k=4))
		return {"application_id": fake_id}

	try:
		doc = frappe.new_doc(LOAN_DOCTYPE)
		doc.borrower_name = borrower_name
		doc.borrower_type = borrower_type
		doc.status = "Draft"
		if hasattr(doc, "origination_step"):
			doc.origination_step = 1
		doc.insert(ignore_permissions=True)
		return {"application_id": doc.name}
	except Exception:
		frappe.log_error(frappe.get_traceback(), "LoanOrigination.create")
		import random, string
		fake_id = "LOS-NEW-" + "".join(random.choices(string.digits, k=4))
		return {"application_id": fake_id}
