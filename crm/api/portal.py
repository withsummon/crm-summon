import json
import os
import re

import frappe
from frappe import _
from frappe.utils import add_days, cint, flt, getdate, now_datetime, today


STAGES = [
	"Application Received",
	"Document Review",
	"Credit Analysis",
	"Collateral Appraisal",
	"Committee Approval",
	"Legal Documentation",
	"Disbursement",
	"Active",
]

STAGE_DESCRIPTIONS = {
	"Application Received": "Your application has been received and assigned for initial review.",
	"Document Review": "Required documents are being checked. Upload any missing or rejected files.",
	"Credit Analysis": "The credit team is reviewing your business, repayment history, and risk profile.",
	"Collateral Appraisal": "Collateral documents and appraisal activities are being reviewed.",
	"Committee Approval": "Your application is queued for approval decision.",
	"Legal Documentation": "Approved terms are being prepared for signing and completion.",
	"Disbursement": "Final checks are in progress before funds are released.",
	"Active": "The facility is active.",
}


def _doctype_ready(doctype):
	return frappe.db.table_exists(doctype)


def _meta_fields(doctype, fields):
	if not _doctype_ready(doctype):
		return []
	meta = frappe.get_meta(doctype)
	return [fieldname for fieldname in fields if fieldname == "name" or meta.has_field(fieldname)]


def _customer_fields():
	fields = ["name", "customer_name", "customer_type", "customer_group", "territory", "website"]
	return _meta_fields("Customer", fields + ["mobile_no", "email_id", "tax_id"])


def _can_select_customer():
	return bool(set(frappe.get_roles() or []) & {"System Manager", "Sales Manager", "Sales User"})


def _resolve_customer(customer=None):
	if customer and _can_select_customer() and frappe.db.exists("Customer", customer):
		return customer

	user = frappe.session.user
	if user and user != "Guest" and _doctype_ready("Customer") and frappe.get_meta("Customer").has_field("email_id"):
		match = frappe.get_all("Customer", filters={"email_id": user}, pluck="name", limit=1)
		if match:
			return match[0]

	for preferred in ("PT Maju Jaya", "PT Industri Nusantara", "CV Cahaya Terang", "PT Teknologi Maju"):
		if frappe.db.exists("Customer", preferred):
			return preferred

	rows = frappe.get_all("Customer", pluck="name", order_by="modified desc", limit=1)
	return rows[0] if rows else None


def _require_customer(customer=None):
	customer = _resolve_customer(customer)
	if not customer:
		frappe.throw(_("No customer is available for this portal session."))
	return customer


def _stage_index(status):
	legacy = {
		"Submitted": 1,
		"Pending Review": 2,
		"In Progress": 3,
		"Approved": 8,
	}
	if status in legacy:
		return legacy[status]
	return STAGES.index(status) + 1 if status in STAGES else 0


def _eta_for_stage(status):
	offsets = {
		"Submitted": 2,
		"Pending Review": 3,
		"In Progress": 5,
		"Application Received": 2,
		"Document Review": 3,
		"Credit Analysis": 5,
		"Collateral Appraisal": 7,
		"Committee Approval": 4,
		"Legal Documentation": 6,
		"Disbursement": 2,
	}
	return add_days(today(), offsets.get(status, 0)) if status in offsets else None


def _notes_text(value):
	if not value:
		return ""
	if isinstance(value, dict):
		return json.dumps(value)
	return str(value)


def _document_status(row):
	notes = _notes_text(row.get("notes"))
	if "Rejected:" in notes or "Rejected" in notes:
		return "Rejected"
	if "Pending Review" in notes:
		return "Pending Review"
	if row.get("expiry_status") == "Expired":
		return "Rejected"
	if row.get("file"):
		return "Approved"
	if row.get("preview_status") == "Needs Upload":
		return "Pending Upload"
	return "Pending Upload"


def _document_notes(row):
	notes = _notes_text(row.get("notes"))
	notes = notes.replace("portal_demo:", "").strip()
	for prefix in ("Rejected:", "Pending Review:", "Pending Upload:", "Approved:", "Expired:"):
		if notes.startswith(prefix):
			return notes[len(prefix) :].strip()
	return notes


def _normalize_application(row):
	status = row.get("status") or "Draft"
	stage_index = _stage_index(status)
	data = dict(row or {})
	return {
		**data,
		"stage_index": stage_index,
		"stage_label": status,
		"current_stage_detail": STAGE_DESCRIPTIONS.get(status, "Application status is being reviewed."),
		"eta_date": _eta_for_stage(status),
		"required_actions": ["Upload missing or rejected documents"] if status == "Document Review" else [],
	}


def _normalize_facility(row):
	notes = _notes_text(row.get("notes"))
	rate = ""
	tenor = ""
	for part in notes.split(";"):
		part = part.replace("portal_demo:", "").strip()
		if part.lower().startswith("rate"):
			rate = part.replace("Rate", "").strip()
		if part.lower().startswith("tenor"):
			tenor = part.replace("tenor", "").replace("Tenor", "").strip()
	data = dict(row or {})
	return {
		**data,
		"rate": rate,
		"tenor": tenor,
	}


def _get_customer_doc(customer):
	fields = _customer_fields()
	if not fields:
		return {"name": customer, "customer_name": customer}
	return frappe.db.get_value("Customer", customer, fields, as_dict=True)


def _get(row, fieldname, default=None):
	if not row:
		return default
	if isinstance(row, dict):
		return row.get(fieldname, default)
	return getattr(row, fieldname, default)


def _safe_list(value):
	if not value:
		return []
	if isinstance(value, list):
		return value
	return list(value)


def _get_rm_context(customer):
	comm = None
	if _doctype_ready("CRM Customer Communication"):
		rows = frappe.get_all(
			"CRM Customer Communication",
			fields=_meta_fields("CRM Customer Communication", ["name", "channel", "subject", "conversation_link", "message"]),
			filters={"customer": customer},
			order_by="modified desc",
			limit=1,
		)
		comm = rows[0] if rows else None
	# Try to find real RM from site visits or lead assignments
	rm_user = None
	if _doctype_ready("CRM Site Visit"):
		visits = frappe.get_all(
			"CRM Site Visit",
			filters={"customer": customer},
			fields=["rm"],
			order_by="visit_date desc",
			limit_page_length=1,
		)
		if visits and visits[0].get("rm"):
			rm_user = visits[0]["rm"]
	if not rm_user and _doctype_ready("CRM Lead"):
		leads = frappe.get_all(
			"CRM Lead",
			filters={"organization": customer},
			fields=["owner"],
			order_by="modified desc",
			limit_page_length=1,
		)
		if leads and leads[0].get("owner"):
			rm_user = leads[0]["owner"]
	if rm_user:
		user_doc = frappe.db.get_value("User", rm_user, ["full_name", "phone", "mobile_no"], as_dict=True)
		if user_doc:
			initials = "".join([p[0] for p in (user_doc.full_name or "").split() if p])[:2].upper()
			phone = user_doc.mobile_no or user_doc.phone or ""
			return {
				"name": user_doc.full_name or rm_user,
				"role": "Relationship Manager",
				"initials": initials or "RM",
				"phone": phone,
				"wa_link": (comm or {}).get("conversation_link") or (f"https://wa.me/{phone}" if phone else ""),
				"last_message": (comm or {}).get("subject") or "",
			}
	return {
		"name": "Relationship Manager",
		"role": "RM",
		"initials": "RM",
		"phone": "",
		"wa_link": (comm or {}).get("conversation_link") or "",
		"last_message": (comm or {}).get("subject") or "",
	}


@frappe.whitelist()
def get_portal_context(customer=None):
	customer = _require_customer(customer)
	return {
		"customer": _get_customer_doc(customer),
		"rm": _get_rm_context(customer),
		"stages": STAGES,
	}


@frappe.whitelist()
def get_my_applications(customer=None):
	customer = _require_customer(customer)
	if not _doctype_ready("CRM Credit Application"):
		return []
	rows = frappe.get_all(
		"CRM Credit Application",
		fields=_meta_fields(
			"CRM Credit Application",
			["name", "borrower", "borrower_name", "facility_type", "requested_amount", "status", "creation", "purpose", "notes"],
		),
		filters={"borrower": customer},
		order_by="creation desc",
		limit=50,
	)
	return [_normalize_application(row) for row in rows]


@frappe.whitelist()
def get_my_facilities(customer=None):
	customer = _require_customer(customer)
	if not _doctype_ready("CRM Credit Facility"):
		return []
	rows = frappe.get_all(
		"CRM Credit Facility",
		fields=_meta_fields(
			"CRM Credit Facility",
			[
				"name",
				"customer",
				"facility_type",
				"product_type",
				"status",
				"due_date",
				"outstanding",
				"limit_amount",
				"health",
				"repayment_behavior",
				"action_status",
				"notes",
			],
		),
		filters={"customer": customer, "status": "Active"},
		order_by="due_date asc",
		limit=50,
	)
	return [_normalize_facility(row) for row in rows]


@frappe.whitelist()
def get_portal_dashboard(customer=None):
	try:
		customer = _require_customer(customer)
		applications = _safe_list(get_my_applications(customer))
		facilities = _safe_list(get_my_facilities(customer))
		docs = _safe_list(get_document_checklist(customer=customer))
		tickets = _safe_list(get_my_tickets(customer=customer))
		next_facility = next((row for row in facilities if _get(row, "due_date")), None)
		next_payment = None
		if next_facility:
			due_date = _get(next_facility, "due_date")
			days_until = (getdate(due_date) - getdate(today())).days
			next_payment = {
				"date": due_date,
				"days_until": days_until,
				"facility": _get(next_facility, "name"),
			}
		notifications = []
		missing_docs = [row for row in docs if _get(row, "status_label") in ("Pending Upload", "Rejected")]
		if missing_docs:
			notifications.append({"type": "documents", "label": f"{len(missing_docs)} document(s) need attention"})
		if next_payment and next_payment["days_until"] <= 7:
			notifications.append({"type": "payment", "label": "Payment due soon"})
		open_tickets = [row for row in tickets if _get(row, "status") not in ("Resolved", "Closed")]
		if open_tickets:
			notifications.append({"type": "support", "label": f"{len(open_tickets)} open support ticket(s)"})
		return {
			"customer": _get_customer_doc(customer),
			"active_facilities": len(facilities),
			"pending_applications": len([row for row in applications if 0 < cint(_get(row, "stage_index")) < 8]),
			"next_payment": next_payment,
			"notifications": notifications,
			"rm": _get_rm_context(customer),
		}
	except TypeError:
		frappe.log_error(frappe.get_traceback(), "Customer Portal dashboard TypeError")
		customer = _resolve_customer(customer)
		return {
			"customer": _get_customer_doc(customer) if customer else None,
			"active_facilities": 0,
			"pending_applications": 0,
			"next_payment": None,
			"notifications": [{"type": "warning", "label": "Dashboard data is partially unavailable"}],
			"rm": _get_rm_context(customer) if customer else {},
		}


@frappe.whitelist()
def get_facility_detail(facility_name, customer=None):
	customer = _require_customer(customer)
	if not facility_name or not _doctype_ready("CRM Credit Facility"):
		frappe.throw(_("Facility not found"))
	facility = frappe.db.get_value(
		"CRM Credit Facility",
		{"name": facility_name, "customer": customer},
		_meta_fields(
			"CRM Credit Facility",
			["name", "customer", "facility_type", "product_type", "due_date", "outstanding", "limit_amount", "health", "repayment_behavior", "notes"],
		),
		as_dict=True,
	)
	if not facility:
		frappe.throw(_("Facility not found"))
	facility = _normalize_facility(facility)
	transactions = []
	if _doctype_ready("CRM Transaction History"):
		transactions = frappe.get_all(
			"CRM Transaction History",
			fields=_meta_fields(
				"CRM Transaction History",
				["name", "transaction_date", "transaction_type", "amount", "running_balance", "status", "notes"],
			),
			filters={"customer": customer, "facility": facility_name},
			order_by="transaction_date desc",
			limit=12,
		)
	return {
		"facility": facility,
		"schedule": _build_schedule(facility),
		"transactions": transactions,
		"statements": _statement_periods(),
	}


def _build_schedule(facility):
	outstanding = flt(facility.get("outstanding"))
	installment = outstanding / 6 if outstanding else 0
	due = getdate(facility.get("due_date") or today())
	rows = []
	for idx in range(1, 7):
		due_date = add_days(due, 30 * (idx - 1))
		status = "Due" if idx == 1 else "Upcoming"
		if getdate(due_date) < getdate(today()):
			status = "Overdue"
		principal = round(installment * 0.82)
		interest = round(installment * 0.18)
		rows.append(
			{
				"no": idx,
				"due_date": due_date,
				"principal": principal,
				"interest": interest,
				"total": principal + interest,
				"status": status,
			}
		)
	return rows


def _statement_periods():
	current = getdate(today())
	return [{"label": f"{current.year}-{month:02d}", "value": f"{current.year}-{month:02d}"} for month in range(max(1, current.month - 2), current.month + 1)]


@frappe.whitelist()
def get_document_checklist(application_name=None, customer=None):
	customer = _require_customer(customer)
	if application_name and _doctype_ready("CRM Credit Application"):
		owner = frappe.db.get_value("CRM Credit Application", application_name, "borrower")
		if owner and owner != customer:
			frappe.throw(_("Application not found"))
	if not _doctype_ready("CRM Customer Document"):
		return []
	rows = frappe.get_all(
		"CRM Customer Document",
		fields=_meta_fields(
			"CRM Customer Document",
			["name", "customer", "document_type", "title", "file", "expiry_status", "preview_status", "notes", "modified"],
		),
		filters={"customer": customer},
		order_by="modified desc",
		limit=50,
	)
	return [_normalize_document(row) for row in rows]


def _normalize_document(row):
	status = _document_status(row)
	data = dict(row or {})
	return {
		**data,
		"status_label": status,
		"notes": _document_notes(row),
		"file_name": (row.get("file") or "").split("/")[-1] if row.get("file") else "",
	}


@frappe.whitelist()
def update_document_file(document_name, file_url, customer=None):
	customer = _require_customer(customer)
	if not document_name or not file_url:
		frappe.throw(_("Document and file are required"))
	doc = frappe.get_doc("CRM Customer Document", document_name)
	if doc.customer != customer:
		frappe.throw(_("Document not found"))
	doc.file = file_url
	if frappe.get_meta("CRM Customer Document").has_field("preview_status"):
		doc.preview_status = "Preview Available"
	doc.notes = "Pending Review: Uploaded from customer portal and awaiting review."
	doc.save(ignore_permissions=True)
	return _normalize_document(doc.as_dict())


@frappe.whitelist()
def get_my_tickets(customer=None):
	customer = _require_customer(customer)
	if not _doctype_ready("HD Ticket"):
		return []
	fields = _meta_fields("HD Ticket", ["name", "subject", "status", "creation", "description", "ticket_type"])
	filters = {}
	if _meta_fields("HD Ticket", ["customer"]):
		filters["customer"] = customer
	elif _meta_fields("HD Ticket", ["raised_by"]):
		filters["raised_by"] = frappe.db.get_value("Customer", customer, "email_id") or frappe.session.user
	else:
		return []
	rows = frappe.get_all("HD Ticket", fields=fields, filters=filters, order_by="creation desc", limit=20)
	for row in rows:
		row["sla"] = "Next response within 1 business day" if row.get("status") not in ("Resolved", "Closed") else "Resolved"
		row["replies"] = []
	return rows


@frappe.whitelist()
def submit_ticket(category, subject, description="", customer=None):
	customer = _require_customer(customer)
	if not subject or not category:
		frappe.throw(_("Category and subject are required"))
	if _doctype_ready("HD Ticket"):
		meta = frappe.get_meta("HD Ticket")
		payload = {"doctype": "HD Ticket"}
		for fieldname, value in {
			"subject": subject,
			"description": description,
			"ticket_type": category,
			"status": "Open",
			"customer": customer,
			"raised_by": frappe.db.get_value("Customer", customer, "email_id") or frappe.session.user,
		}.items():
			if meta.has_field(fieldname):
				payload[fieldname] = value
		return frappe.get_doc(payload).insert(ignore_permissions=True).as_dict()
	if _doctype_ready("CRM Customer Communication"):
		return frappe.get_doc(
			{
				"doctype": "CRM Customer Communication",
				"customer": customer,
				"channel": "Email",
				"direction": "Inbound",
				"subject": subject,
				"communication_time": now_datetime(),
				"compose_status": "Manual",
				"status": "Open",
				"message": f"{category}\n\n{description}",
			}
		).insert(ignore_permissions=True).as_dict()
	frappe.throw(_("Support ticket storage is not available"))


DEFAULT_APPLICATION_DOCUMENTS = [
	{"title": "Company Registration Certificate", "document_type": "Legal"},
	{"title": "Latest Bank Statement (3 months)", "document_type": "Financial"},
	{"title": "Tax Identification Document (NPWP)", "document_type": "KYC"},
	{"title": "Audited Financial Statement", "document_type": "Financial"},
]


def _seed_application_documents(customer, application_name):
	if not _doctype_ready("CRM Customer Document"):
		return []
	meta = frappe.get_meta("CRM Customer Document")
	created = []
	for spec in DEFAULT_APPLICATION_DOCUMENTS:
		payload = {
			"doctype": "CRM Customer Document",
			"customer": customer,
			"title": spec["title"],
		}
		if meta.has_field("document_type"):
			payload["document_type"] = spec["document_type"]
		if meta.has_field("preview_status"):
			payload["preview_status"] = "Needs Upload"
		if meta.has_field("notes"):
			payload["notes"] = f"Pending Upload: required for application {application_name}."
		doc = frappe.get_doc(payload).insert(ignore_permissions=True)
		created.append(doc.name)
	return created


@frappe.whitelist()
def submit_new_application(facility_type, requested_amount, purpose, borrower_type="Company", notes=None, customer=None):
	customer = _require_customer(customer)
	amount = flt(requested_amount)
	if not facility_type or amount <= 0 or not purpose:
		frappe.throw(_("Facility type, amount, and purpose are required"))
	if not _doctype_ready("CRM Credit Application"):
		frappe.throw(_("Credit application storage is not available"))
	borrower_name = frappe.db.get_value("Customer", customer, "customer_name") or customer
	app = frappe.get_doc(
		{
			"doctype": "CRM Credit Application",
			"borrower": customer,
			"borrower_name": borrower_name,
			"borrower_type": borrower_type or "Company",
			"status": "Application Received",
			"facility_type": facility_type,
			"requested_amount": amount,
			"purpose": purpose,
			"notes": notes or f"New application submitted via customer portal by {borrower_name}.",
		}
	).insert(ignore_permissions=True)
	created_docs = _seed_application_documents(customer, app.name)
	return {
		"application_name": app.name,
		"application": _normalize_application(app.as_dict()),
		"documents_created": created_docs,
	}


@frappe.whitelist()
def upload_document(title, document_type, file_url, customer=None, application_name=None):
	customer = _require_customer(customer)
	if not title or not file_url:
		frappe.throw(_("Title and file are required"))
	if not _doctype_ready("CRM Customer Document"):
		frappe.throw(_("Document storage is not available"))
	meta = frappe.get_meta("CRM Customer Document")
	payload = {
		"doctype": "CRM Customer Document",
		"customer": customer,
		"title": title,
		"file": file_url,
	}
	if meta.has_field("document_type") and document_type:
		payload["document_type"] = document_type
	if meta.has_field("preview_status"):
		payload["preview_status"] = "Preview Available"
	note = "Pending Review: Uploaded from customer portal and awaiting review."
	if application_name:
		note += f" (for application {application_name})"
	if meta.has_field("notes"):
		payload["notes"] = note
	doc = frappe.get_doc(payload).insert(ignore_permissions=True)
	return _normalize_document(doc.as_dict())


def _format_rp(amount):
	try:
		return f"Rp {int(round(flt(amount))):,}".replace(",", ".")
	except Exception:
		return str(amount)


def _assistant_context(customer):
	customer_doc = _get_customer_doc(customer) or {}
	applications = _safe_list(get_my_applications(customer))
	facilities = _safe_list(get_my_facilities(customer))
	documents = _safe_list(get_document_checklist(customer=customer))
	rm = _get_rm_context(customer)
	pending_docs = [d for d in documents if _get(d, "status_label") in ("Pending Upload", "Rejected")]
	in_progress = [a for a in applications if 0 < cint(_get(a, "stage_index")) < 8]
	next_facility = next((f for f in facilities if _get(f, "due_date")), None)
	return {
		"customer": customer_doc,
		"applications": applications,
		"facilities": facilities,
		"documents": documents,
		"pending_documents": pending_docs,
		"in_progress_applications": in_progress,
		"next_facility": next_facility,
		"rm": rm,
	}


def _summarize_context_for_llm(ctx):
	lines = []
	cust = ctx.get("customer") or {}
	lines.append(f"Customer: {cust.get('customer_name') or cust.get('name')}")
	for f in ctx.get("facilities") or []:
		lines.append(
			f"- Facility {f.get('name')}: type={f.get('facility_type')}, outstanding={_format_rp(f.get('outstanding'))}, "
			f"limit={_format_rp(f.get('limit_amount'))}, due={f.get('due_date')}, health={f.get('health')}"
		)
	for a in ctx.get("applications") or []:
		lines.append(
			f"- Application {a.get('name')}: {a.get('facility_type')} {_format_rp(a.get('requested_amount'))} "
			f"stage {a.get('stage_index')}/8 ({a.get('stage_label')})"
		)
	for d in ctx.get("pending_documents") or []:
		lines.append(f"- Document needed: {d.get('title')} ({d.get('status_label')})")
	rm = ctx.get("rm") or {}
	if rm.get("name"):
		lines.append(f"Relationship Manager: {rm.get('name')} ({rm.get('phone')})")
	return "\n".join(lines)


def _rule_based_answer(message, ctx):
	q = (message or "").lower().strip()
	facilities = ctx.get("facilities") or []
	apps = ctx.get("applications") or []
	pending_docs = ctx.get("pending_documents") or []
	next_facility = ctx.get("next_facility")
	rm = ctx.get("rm") or {}

	if any(k in q for k in ("payment", "due", "installment", "bayar", "tagihan", "cicilan")):
		if next_facility:
			due = next_facility.get("due_date")
			days = (getdate(due) - getdate(today())).days if due else None
			when = f"on {due}" + (f" (in {days} days)" if days is not None and days >= 0 else " (overdue)" if days is not None else "")
			return (
				f"Your next payment for {next_facility.get('facility_type')} ({next_facility.get('name')}) is due {when}. "
				f"Outstanding balance is {_format_rp(next_facility.get('outstanding'))}. "
				"You can view the full schedule in the Facilities tab."
			)
		return "I don't see any active facility with an upcoming payment in your portal right now."

	if any(k in q for k in ("document", "dokumen", "upload", "missing", "kurang")):
		if pending_docs:
			titles = ", ".join(d.get("title") for d in pending_docs[:5])
			return (
				f"You have {len(pending_docs)} document(s) that need attention: {titles}. "
				"Open the Documents tab and use the Upload button to submit them."
			)
		return "All your documents are up to date — nothing pending review or upload right now."

	if any(k in q for k in ("application", "status", "pengajuan", "progress", "stage")):
		in_progress = ctx.get("in_progress_applications") or []
		if in_progress:
			parts = [f"{a.get('facility_type')} ({a.get('name')}) — stage {a.get('stage_index')}/8: {a.get('stage_label')}" for a in in_progress[:3]]
			return "Your in-progress applications:\n• " + "\n• ".join(parts)
		if apps:
			return f"You have {len(apps)} past application(s) and none currently in progress. You can submit a new one from the Applications tab."
		return "You don't have any applications yet. Click 'New Application' in the Applications tab to start one."

	if any(k in q for k in ("facility", "fasilitas", "loan", "credit", "limit", "outstanding")):
		if facilities:
			parts = [
				f"{f.get('facility_type')} ({f.get('name')}): {_format_rp(f.get('outstanding'))} of {_format_rp(f.get('limit_amount'))} used"
				for f in facilities[:3]
			]
			return "Here's a snapshot of your active facilities:\n• " + "\n• ".join(parts)
		return "You don't have any active facilities right now."

	if any(k in q for k in ("rm", "manager", "contact", "hubungi", "support", "help", "bantuan")):
		return (
			f"Your relationship manager is {rm.get('name', 'your RM')} ({rm.get('phone', '-')}). "
			"You can also open a support ticket from the Support tab and our team will respond within 1 business day."
		)

	if any(k in q for k in ("top-up", "topup", "tambah", "tambahan", "increase")):
		return "To request additional funding on an existing facility, open the Facilities tab, click a facility, then use 'Request Top-Up'."

	if any(k in q for k in ("hi", "hello", "halo", "hai", "assalam")):
		name = (ctx.get("customer") or {}).get("customer_name") or "there"
		return f"Hi {name}! I can help with payment schedules, document checklists, application status, or contacting your RM. What would you like to know?"

	return (
		"I can help with: upcoming payments, document checklist, application status, facility details, top-up requests, or contacting your RM. "
		"Try asking 'when is my next payment?' or 'what documents do I still need?'."
	)


def _llm_answer(message, ctx):
	api_key = os.environ.get("OPENROUTER_API_KEY") or frappe.conf.get("openrouter_api_key")
	if not api_key:
		return None
	try:
		import requests
	except ImportError:
		return None
	system_prompt = (
		"You are an assistant for a credit/lending customer portal. "
		"Answer in 2-4 short sentences. Use only the data provided. "
		"If asked about something outside the provided data, say you don't have that information and suggest contacting their relationship manager.\n\n"
		f"Customer portal data:\n{_summarize_context_for_llm(ctx)}"
	)
	try:
		res = requests.post(
			"https://openrouter.ai/api/v1/chat/completions",
			headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
			json={
				"model": frappe.conf.get("openrouter_model") or "anthropic/claude-3.5-haiku",
				"messages": [
					{"role": "system", "content": system_prompt},
					{"role": "user", "content": message},
				],
				"max_tokens": 400,
			},
			timeout=20,
		)
		if res.status_code != 200:
			return None
		data = res.json()
		return (data.get("choices") or [{}])[0].get("message", {}).get("content")
	except Exception:
		return None


@frappe.whitelist()
def ask_assistant(message, customer=None):
	customer = _require_customer(customer)
	message = (message or "").strip()
	if not message:
		frappe.throw(_("Message is required"))
	ctx = _assistant_context(customer)
	llm_answer = _llm_answer(message, ctx)
	answer = llm_answer or _rule_based_answer(message, ctx)
	return {
		"answer": answer,
		"source": "llm" if llm_answer else "rules",
	}


@frappe.whitelist()
def submit_topup_request(facility_name, amount, purpose, customer=None):
	customer = _require_customer(customer)
	amount = flt(amount)
	if not facility_name or amount <= 0 or not purpose:
		frappe.throw(_("Facility, amount, and purpose are required"))
	facility = frappe.db.get_value("CRM Credit Facility", {"name": facility_name, "customer": customer}, ["name", "facility_type"], as_dict=True)
	if not facility:
		frappe.throw(_("Facility not found"))
	app = frappe.get_doc(
		{
			"doctype": "CRM Credit Application",
			"borrower": customer,
			"borrower_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
			"borrower_type": "Company",
			"status": "Application Received",
			"facility_type": f"Top-Up - {facility.facility_type}",
			"requested_amount": amount,
			"purpose": purpose,
			"notes": f"Top-up request from facility {facility.name}.",
		}
	).insert(ignore_permissions=True)
	if _meta_fields("CRM Credit Facility", ["action_status"]):
		frappe.db.set_value("CRM Credit Facility", facility.name, "action_status", "Top-up Requested")
	return {"application_name": app.name, "application": _normalize_application(app.as_dict())}


@frappe.whitelist()
def update_application(name, fields, customer=None):
	customer = _require_customer(customer)
	fields = _as_dict(fields)
	if not frappe.db.exists("CRM Credit Application", name):
		frappe.throw(_("Application not found"))
	owner = frappe.db.get_value("CRM Credit Application", name, "borrower")
	if owner != customer:
		frappe.throw(_("Application not found"))
	allowed = {"requested_amount", "purpose", "notes"}
	updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
	if not updates:
		frappe.throw(_("No valid fields to update"))
	if "requested_amount" in updates:
		updates["requested_amount"] = flt(updates["requested_amount"])
	frappe.db.set_value("CRM Credit Application", name, updates)
	return _normalize_application(frappe.db.get_value("CRM Credit Application", name, "*", as_dict=True) or {})


@frappe.whitelist()
def cancel_application(name, customer=None):
	customer = _require_customer(customer)
	if not frappe.db.exists("CRM Credit Application", name):
		frappe.throw(_("Application not found"))
	owner = frappe.db.get_value("CRM Credit Application", name, "borrower")
	if owner != customer:
		frappe.throw(_("Application not found"))
	frappe.db.set_value("CRM Credit Application", name, {"status": "Cancelled"})
	return {"name": name, "status": "Cancelled"}


@frappe.whitelist()
def delete_document(name, customer=None):
	customer = _require_customer(customer)
	if not frappe.db.exists("CRM Customer Document", name):
		frappe.throw(_("Document not found"))
	doc_customer = frappe.db.get_value("CRM Customer Document", name, "customer")
	if doc_customer != customer:
		frappe.throw(_("Document not found"))
	frappe.delete_doc("CRM Customer Document", name, ignore_permissions=True)
	return {"deleted": True}


@frappe.whitelist()
def close_ticket(name, customer=None):
	customer = _require_customer(customer)
	if _doctype_ready("HD Ticket") and frappe.db.exists("HD Ticket", name):
		ticket_customer = frappe.db.get_value("HD Ticket", name, "customer")
		if ticket_customer and ticket_customer != customer:
			frappe.throw(_("Ticket not found"))
		frappe.db.set_value("HD Ticket", name, {"status": "Closed"})
		return {"name": name, "status": "Closed"}
	if _doctype_ready("CRM Customer Communication") and frappe.db.exists("CRM Customer Communication", name):
		comm_customer = frappe.db.get_value("CRM Customer Communication", name, "customer")
		if comm_customer != customer:
			frappe.throw(_("Ticket not found"))
		frappe.db.set_value("CRM Customer Communication", name, {"status": "Closed"})
		return {"name": name, "status": "Closed"}
	frappe.throw(_("Ticket not found"))


@frappe.whitelist()
def update_ticket(name, fields, customer=None):
	customer = _require_customer(customer)
	fields = _as_dict(fields)
	if _doctype_ready("HD Ticket") and frappe.db.exists("HD Ticket", name):
		ticket_customer = frappe.db.get_value("HD Ticket", name, "customer")
		if ticket_customer and ticket_customer != customer:
			frappe.throw(_("Ticket not found"))
		allowed = {"subject", "description"}
		updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
		if updates:
			frappe.db.set_value("HD Ticket", name, updates)
		return frappe.db.get_value("HD Ticket", name, ["name", "subject", "status", "description"], as_dict=True)
	if _doctype_ready("CRM Customer Communication") and frappe.db.exists("CRM Customer Communication", name):
		comm_customer = frappe.db.get_value("CRM Customer Communication", name, "customer")
		if comm_customer != customer:
			frappe.throw(_("Ticket not found"))
		allowed = {"subject"}
		updates = {k: v for k, v in fields.items() if k in allowed and v is not None}
		if "subject" in updates:
			updates["message"] = updates.pop("subject")
		if updates:
			frappe.db.set_value("CRM Customer Communication", name, updates)
		return frappe.db.get_value("CRM Customer Communication", name, ["name", "subject", "status", "message as description"], as_dict=True)
	frappe.throw(_("Ticket not found"))


@frappe.whitelist()
def seed_portal_sample_data(customer=None):
	customer = _require_customer(customer)
	created = {"applications": [], "documents": [], "tickets": [], "facilities": []}

	if _doctype_ready("CRM Credit Application"):
		for spec in [
			{"facility_type": "Working Capital Loan", "requested_amount": 500000000, "purpose": "Increase inventory for Q4", "status": "Application Received"},
			{"facility_type": "Investment Loan", "requested_amount": 1200000000, "purpose": "Expand production line", "status": "Document Review"},
			{"facility_type": "Term Loan", "requested_amount": 800000000, "purpose": "Refinance existing debt", "status": "Credit Analysis"},
		]:
			app = frappe.get_doc(
				{
					"doctype": "CRM Credit Application",
					"borrower": customer,
					"borrower_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
					"borrower_type": "Company",
					"status": spec["status"],
					"facility_type": spec["facility_type"],
					"requested_amount": spec["requested_amount"],
					"purpose": spec["purpose"],
					"notes": f"Sample application created via seed data.",
				}
			).insert(ignore_permissions=True)
			created["applications"].append(app.name)
			_seed_application_documents(customer, app.name)

	if _doctype_ready("CRM Credit Facility"):
		for spec in [
			{"facility_type": "Working Capital Loan", "product_type": "Revolving", "outstanding": 250000000, "limit_amount": 500000000, "due_date": add_days(today(), 14)},
			{"facility_type": "Term Loan", "product_type": "Fixed", "outstanding": 600000000, "limit_amount": 800000000, "due_date": add_days(today(), 30)},
		]:
			facility = frappe.get_doc(
				{
					"doctype": "CRM Credit Facility",
					"customer": customer,
					"facility_type": spec["facility_type"],
					"product_type": spec["product_type"],
					"status": "Active",
					"outstanding": spec["outstanding"],
					"limit_amount": spec["limit_amount"],
					"due_date": spec["due_date"],
					"health": "Good",
					"notes": "portal_demo: Rate 8.5% p.a.; Tenor 36 months",
				}
			).insert(ignore_permissions=True)
			created["facilities"].append(facility.name)

	if _doctype_ready("HD Ticket"):
		for spec in [
			{"subject": "Question about payment schedule", "description": "When is my next installment due?", "ticket_type": "Installment Payment"},
			{"subject": "Document upload issue", "description": "I cannot upload my bank statement.", "ticket_type": "Documents"},
		]:
			ticket = frappe.get_doc(
				{
					"doctype": "HD Ticket",
					"subject": spec["subject"],
					"description": spec["description"],
					"ticket_type": spec["ticket_type"],
					"status": "Open",
					"customer": customer,
					"raised_by": frappe.db.get_value("Customer", customer, "email_id") or frappe.session.user,
				}
			).insert(ignore_permissions=True)
			created["tickets"].append(ticket.name)

	if _doctype_ready("CRM Customer Communication") and not created["tickets"]:
		for spec in [
			{"subject": "Question about payment schedule", "message": "When is my next installment due?", "channel": "Email"},
			{"subject": "Document upload issue", "message": "I cannot upload my bank statement.", "channel": "Email"},
		]:
			comm = frappe.get_doc(
				{
					"doctype": "CRM Customer Communication",
					"customer": customer,
					"channel": spec["channel"],
					"direction": "Inbound",
					"subject": spec["subject"],
					"communication_time": now_datetime(),
					"compose_status": "Manual",
					"status": "Open",
					"message": spec["message"],
				}
			).insert(ignore_permissions=True)
			created["tickets"].append(comm.name)

	return created
