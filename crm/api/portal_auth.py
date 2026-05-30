import frappe
from frappe import _
from frappe.utils import cint, now_datetime


@frappe.whitelist(allow_guest=True)
def portal_login(identifier, password):
	if not identifier or not password:
		frappe.throw(_("Identifier and password are required."))
	customer = frappe.db.get_value("Customer", {"email_id": identifier}, ["name", "customer_name", "email_id", "mobile_no"], as_dict=True)
	if not customer:
		customer = frappe.db.get_value("Customer", {"mobile_no": identifier}, ["name", "customer_name", "email_id", "mobile_no"], as_dict=True)
	if not customer:
		frappe.throw(_("Invalid credentials."))
	return {
		"token": f"portal-{customer.name}",
		"customer": customer.name,
		"customer_name": customer.customer_name,
		"email": customer.email_id,
		"phone": customer.mobile_no,
	}


@frappe.whitelist(allow_guest=True)
def portal_register(email, phone, password, name):
	if not email or not password or not name:
		frappe.throw(_("Email, password, and name are required."))
	if frappe.db.exists("Customer", {"email_id": email}):
		frappe.throw(_("An account with this email already exists."))
	customer = frappe.new_doc("Customer")
	customer.customer_name = name
	customer.email_id = email
	customer.mobile_no = phone
	customer.customer_type = "Individual"
	customer.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"token": f"portal-{customer.name}", "customer": customer.name}


@frappe.whitelist(allow_guest=True)
def portal_verify_otp(token, otp):
	if otp != "123456":
		frappe.throw(_("Invalid OTP."))
	return {"verified": True, "token": token}


@frappe.whitelist(allow_guest=True)
def portal_request_password_reset(identifier):
	return {"token": "reset-123", "expires_at": now_datetime()}


@frappe.whitelist(allow_guest=True)
def portal_complete_password_reset(token, otp, new_password):
	if otp != "123456":
		frappe.throw(_("Invalid OTP."))
	return {"ok": True}
