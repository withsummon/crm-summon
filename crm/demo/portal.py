import frappe
from frappe.utils import add_days, now_datetime, today


PORTAL_MARKER = "portal_demo"


def _doctype_ready(doctype):
	return frappe.db.table_exists(doctype)


def _meta_has(doctype, fieldname):
	return _doctype_ready(doctype) and frappe.get_meta(doctype).has_field(fieldname)


def _select_value(doctype, fieldname, value, fallback_map=None):
	if not _meta_has(doctype, fieldname):
		return value
	options = [
		option.strip()
		for option in (frappe.get_meta(doctype).get_field(fieldname).options or "").split("\n")
		if option.strip()
	]
	if not options or value in options:
		return value
	fallback = (fallback_map or {}).get(value)
	if fallback in options:
		return fallback
	return options[0]


def _insert_once(doctype, filters, payload):
	if not _doctype_ready(doctype):
		return None
	existing = frappe.get_all(doctype, filters=filters, pluck="name", limit=1)
	if existing:
		return existing[0]
	doc = frappe.get_doc(payload).insert(ignore_permissions=True)
	return doc.name


def _portal_note(text):
	return f"{PORTAL_MARKER}: {text}"


def _create_application(customer, status, facility_type, amount, purpose, risk_grade="B+"):
	status = _select_value(
		"CRM Credit Application",
		"status",
		status,
		{
			"Application Received": "Submitted",
			"Document Review": "Pending Review",
			"Credit Analysis": "In Progress",
			"Collateral Appraisal": "In Progress",
			"Committee Approval": "In Progress",
			"Legal Documentation": "In Progress",
			"Disbursement": "In Progress",
			"Active": "Approved",
		},
	)
	return _insert_once(
		"CRM Credit Application",
		{"borrower": customer, "status": status, "facility_type": facility_type, "purpose": ["like", f"%{PORTAL_MARKER}%"]},
		{
			"doctype": "CRM Credit Application",
			"borrower": customer,
			"borrower_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
			"borrower_type": "Company",
			"status": status,
			"facility_type": facility_type,
			"requested_amount": amount,
			"industry": frappe.db.get_value("Customer", customer, "industry"),
			"risk_grade": risk_grade,
			"purpose": _portal_note(purpose),
			"notes": _portal_note(f"Expected next update: {add_days(today(), 5)}"),
		},
	)


def _create_facility(customer, facility_type, product_type, outstanding, limit_amount, due_in_days, health, notes):
	return _insert_once(
		"CRM Credit Facility",
		{"customer": customer, "facility_type": facility_type, "notes": ["like", f"%{PORTAL_MARKER}%"]},
		{
			"doctype": "CRM Credit Facility",
			"customer": customer,
			"facility_type": facility_type,
			"product_type": product_type,
			"status": "Active",
			"due_date": add_days(today(), due_in_days),
			"outstanding": outstanding,
			"limit_amount": limit_amount,
			"health": health,
			"repayment_behavior": "On-time payments for the last 6 months" if due_in_days >= 0 else "Payment follow-up required",
			"notes": _portal_note(notes),
		},
	)


def _create_document(customer, title, document_type, status, notes="", file_url=None, expiry_status="Valid"):
	preview_status = "Preview Available" if file_url else "Needs Upload"
	if status == "Rejected":
		preview_status = "Unavailable"
	return _insert_once(
		"CRM Customer Document",
		{"customer": customer, "title": title, "notes": ["like", f"%{PORTAL_MARKER}%"]},
		{
			"doctype": "CRM Customer Document",
			"customer": customer,
			"document_type": document_type,
			"title": title,
			"folder": "Customer Portal",
			"file": file_url,
			"version": "1",
			"expiry_date": add_days(today(), 180) if expiry_status == "Valid" else add_days(today(), -30),
			"expiry_status": expiry_status,
			"tags": "portal,required",
			"preview_status": preview_status,
			"notes": _portal_note(f"{status}: {notes}".strip()),
		},
	)


def _create_transaction(customer, facility, transaction_type, amount, running_balance, days_ago, status="Posted", notes=""):
	return _insert_once(
		"CRM Transaction History",
		{
			"customer": customer,
			"facility": facility,
			"transaction_type": transaction_type,
			"transaction_date": add_days(today(), -days_ago),
			"notes": ["like", f"%{PORTAL_MARKER}%"],
		},
		{
			"doctype": "CRM Transaction History",
			"customer": customer,
			"facility": facility,
			"transaction_date": add_days(today(), -days_ago),
			"transaction_type": transaction_type,
			"amount": amount,
			"running_balance": running_balance,
			"status": status,
			"notes": _portal_note(notes or transaction_type),
		},
	)


def _create_communication(customer, channel, direction, subject, message):
	return _insert_once(
		"CRM Customer Communication",
		{"customer": customer, "subject": subject, "message": ["like", f"%{PORTAL_MARKER}%"]},
		{
			"doctype": "CRM Customer Communication",
			"customer": customer,
			"channel": channel,
			"direction": direction,
			"subject": subject,
			"communication_time": now_datetime(),
			"conversation_link": "https://wa.me/628110001234",
			"compose_status": "Sent",
			"status": "Open",
			"message": _portal_note(message),
		},
	)


def _create_ticket(customer, subject, status, description):
	if not _doctype_ready("HD Ticket"):
		return None
	meta = frappe.get_meta("HD Ticket")
	payload = {"doctype": "HD Ticket"}
	for fieldname, value in {
		"subject": subject,
		"status": status,
		"description": _portal_note(description),
		"ticket_type": "Customer Portal",
		"customer": customer,
		"raised_by": frappe.db.get_value("Customer", customer, "email_id") or frappe.session.user,
	}.items():
		if meta.has_field(fieldname):
			payload[fieldname] = value
	try:
		return _insert_once("HD Ticket", {"subject": subject}, payload)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Portal demo ticket creation failed")
		return None


def create_demo_portal(customer_names):
	created = {
		"applications": [],
		"facilities": [],
		"documents": [],
		"transactions": [],
		"communications": [],
		"tickets": [],
	}
	customers = [name for name in customer_names or [] if frappe.db.exists("Customer", name)]
	customer_set = set(customers)

	def has_customer(name):
		return name in customer_set

	if has_customer("PT Maju Jaya"):
		customer = "PT Maju Jaya"
		app = _create_application(customer, "Active", "Working Capital", 1200000000, "Completed portal demo application for working capital renewal.", "A-")
		fac = _create_facility(customer, "Working Capital", "KMK Revolving", 780000000, 1500000000, 18, "Good", "Rate 10.25% p.a.; tenor 36 months; top-up eligible.")
		if app:
			created["applications"].append(app)
		if fac:
			created["facilities"].append(fac)
			for days, amount, balance in ((90, 42500000, 870000000), (60, 42500000, 825000000), (30, 42500000, 780000000)):
				tx = _create_transaction(customer, fac, "Repayment", amount, balance, days)
				if tx:
					created["transactions"].append(tx)
		for doc in (
			_create_document(customer, "NPWP Company", "KYC", "Approved", "Verified by credit operations.", "/files/demo-npwp-maju-jaya.pdf"),
			_create_document(customer, "Latest Financial Statement", "Financial", "Approved", "FY2025 audited statement.", "/files/demo-financial-maju-jaya.pdf"),
		):
			if doc:
				created["documents"].append(doc)
		comm = _create_communication(customer, "WA", "Outbound", "Top-up eligibility shared", "RM shared top-up eligibility and next steps.")
		if comm:
			created["communications"].append(comm)

	if has_customer("PT Industri Nusantara"):
		customer = "PT Industri Nusantara"
		app = _create_application(customer, "Credit Analysis", "Investment Loan", 2500000000, "Portal demo application under credit analysis for machinery expansion.", "B+")
		if app:
			created["applications"].append(app)
		for doc in (
			_create_document(customer, "Company Deed", "Legal", "Approved", "Legal document accepted.", "/files/demo-deed-industri.pdf"),
			_create_document(customer, "Six Month Bank Statement", "Financial", "Pending Review", "Uploaded and awaiting analyst review.", "/files/demo-bank-statement-industri.pdf"),
			_create_document(customer, "Collateral Certificate", "Collateral", "Pending Upload", "Required before appraisal can start."),
		):
			if doc:
				created["documents"].append(doc)
		comm = _create_communication(customer, "Email", "Outbound", "Credit analysis update", "Credit analyst requested collateral certificate upload.")
		if comm:
			created["communications"].append(comm)

	if has_customer("CV Cahaya Terang"):
		customer = "CV Cahaya Terang"
		app = _create_application(customer, "Document Review", "Invoice Financing", 650000000, "Portal demo application waiting for corrected supporting documents.", "B")
		if app:
			created["applications"].append(app)
		for doc in (
			_create_document(customer, "Owner KTP", "KYC", "Rejected", "Rejected: image is blurred. Please re-upload a clear photo.", "/files/demo-ktp-cahaya.jpg"),
			_create_document(customer, "Recent Bank Statement", "Financial", "Pending Upload", "Last 3 months statement is required."),
			_create_document(customer, "Business License", "Legal", "Expired", "Expired document must be renewed.", "/files/demo-license-cahaya.pdf", "Expired"),
		):
			if doc:
				created["documents"].append(doc)
		ticket = _create_ticket(customer, "Document upload clarification", "Open", "Customer asked why KTP document was rejected.")
		if ticket:
			created["tickets"].append(ticket)
		comm = _create_communication(customer, "WA", "Outbound", "Document correction reminder", "RM reminded customer to upload a clearer KTP photo.")
		if comm:
			created["communications"].append(comm)

	if has_customer("PT Teknologi Maju"):
		customer = "PT Teknologi Maju"
		fac = _create_facility(customer, "Term Loan", "Investment Loan", 980000000, 1200000000, 5, "Watchlist", "Rate 11.75% p.a.; tenor 48 months; payment due soon.")
		if fac:
			created["facilities"].append(fac)
			for payload in (
				("Repayment", 36000000, 1016000000, 65, "Posted", "Regular installment posted."),
				("Missed Payment", 36000000, 980000000, 5, "Failed", "Payment not received by due date."),
			):
				tx = _create_transaction(customer, fac, *payload)
				if tx:
					created["transactions"].append(tx)

	frappe.db.commit()
	return created


def delete_demo_portal(data):
	for doctype, key in (
		("HD Ticket", "tickets"),
		("CRM Customer Communication", "communications"),
		("CRM Transaction History", "transactions"),
		("CRM Customer Document", "documents"),
		("CRM Credit Application", "applications"),
		("CRM Credit Facility", "facilities"),
	):
		if not _doctype_ready(doctype):
			continue
		for name in data.get(key, []) if isinstance(data, dict) else []:
			if frappe.db.exists(doctype, name):
				frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
	frappe.db.commit()
