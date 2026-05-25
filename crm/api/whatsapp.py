import json
import re
from urllib.parse import urlparse

import frappe
from frappe import _
from frappe.utils import cstr
from frappe.permissions import add_permission, update_permission_property

from crm.api.doc import get_assigned_users
from crm.fcrm.doctype.crm_notification.crm_notification import notify_user
from crm.integrations.api import get_contact_lead_or_deal_from_number

ALLOWED_WHATSAPP_ROLES = ["System Manager", "Sales Manager", "Sales User"]
MAX_FREE_TEXT_LENGTH = 4096
MAX_SENDS_PER_USER_PER_MINUTE = 20


def validate_access(reference_doctype=None, reference_name=None, permtype="read"):
	if not any(role in ALLOWED_WHATSAPP_ROLES for role in frappe.get_roles()):
		frappe.throw(_("Only sales users can access WhatsApp features."), frappe.PermissionError)

	if reference_doctype and reference_name:
		if not frappe.db.exists(reference_doctype, reference_name):
			frappe.throw(
				_("Reference document {0} {1} does not exist.").format(reference_doctype, reference_name),
				frappe.DoesNotExistError,
			)
		reference_doc = frappe.get_doc(reference_doctype, reference_name)
		if not reference_doc.has_permission(permtype):
			frappe.throw(
				_("Not permitted to access reference document {0} {1}.").format(
					reference_doctype, reference_name
				),
				frappe.PermissionError,
			)
		return reference_doc

	return None


def validate(doc, method):
	phone_number = doc.get("from") if doc.type == "Incoming" else doc.get("to")
	if phone_number:
		try:
			name, doctype = get_contact_lead_or_deal_from_number(phone_number)
			if doctype and name is not None:
				doc.reference_doctype = doctype
				doc.reference_name = name
		except Exception:
			frappe.log_error(frappe.get_traceback(), "CRM WhatsApp: failed to resolve contact from number")


def on_update(doc, method):
	frappe.publish_realtime(
		"whatsapp_message",
		{
			"reference_doctype": doc.reference_doctype,
			"reference_name": doc.reference_name,
		},
	)

	notify_agent(doc)


def notify_agent(doc):
	if doc.type == "Incoming":
		if not doc.reference_doctype or not doc.reference_name:
			return
		doctype = doc.reference_doctype
		if doctype and doctype.startswith("CRM "):
			doctype = doctype[4:].lower()
		safe_reference_name = frappe.utils.escape_html(doc.reference_name)
		notification_text = f"""
            <div class="mb-2 leading-5 text-ink-gray-5">
                <span class="font-medium text-ink-gray-9">{_("You")}</span>
                <span>{_("received a whatsapp message in {0}").format(doctype)}</span>
                <span class="font-medium text-ink-gray-9">{safe_reference_name}</span>
            </div>
        """
		assigned_users = get_assigned_users(doc.reference_doctype, doc.reference_name)
		for user in assigned_users:
			notify_user(
				{
					"owner": doc.owner,
					"assigned_to": user,
					"notification_type": "WhatsApp",
					"message": doc.message,
					"notification_text": notification_text,
					"reference_doctype": "WhatsApp Message",
					"reference_docname": doc.name,
					"redirect_to_doctype": doc.reference_doctype,
					"redirect_to_docname": doc.reference_name,
				}
			)


@frappe.whitelist()
def is_whatsapp_enabled():
	return bool(_get_whatsapp_js_url() or _has_active_whatsapp_account())


@frappe.whitelist()
def is_whatsapp_installed():
	return bool(_get_whatsapp_js_url() or frappe.db.exists("DocType", "WhatsApp Message"))


def _has_active_whatsapp_account():
	if not frappe.db.exists("DocType", "CRM Omnichannel Channel Account"):
		return False
	return bool(
		frappe.db.exists(
			"CRM Omnichannel Channel Account",
			{"channel": "WhatsApp", "status": "Active", "credentials_configured": 1},
		)
	)


def _get_whatsapp_js_url():
	return (frappe.conf.get("whatsapp_api_url") or "").strip().rstrip("/")


def _get_whatsapp_js_headers():
	token = (frappe.conf.get("whatsapp_api_token") or "").strip()
	headers = {"Content-Type": "application/json"}
	if token:
		headers["Authorization"] = f"Bearer {token}"
		headers["X-API-Key"] = token
	return headers


def _validate_whatsapp_js_url(url):
	if not url:
		frappe.throw(_("WhatsAppWebJS API URL is not configured. Set whatsapp_api_url in site_config.json."))
	parsed = urlparse(url)
	if parsed.scheme not in {"http", "https"} or not parsed.netloc:
		frappe.throw(_("WhatsAppWebJS API URL must be a valid http(s) URL."))
	host = (parsed.hostname or "").lower()
	is_local = host in {"localhost", "127.0.0.1", "::1"}
	if parsed.scheme != "https" and not is_local:
		frappe.throw(_("WhatsAppWebJS API URL must use HTTPS outside localhost."))


def _normalize_whatsapp_number(number):
	value = re.sub(r"[\s().-]", "", cstr(number or ""))
	if value.startswith("00"):
		value = "+" + value[2:]
	if not re.fullmatch(r"\+?\d{10,15}", value or ""):
		frappe.throw(_("WhatsApp recipient must be a single phone number with 10-15 digits."))
	return value


def _enforce_whatsapp_rate_limit():
	try:
		key = f"crm:wawebjs:send:{frappe.session.user}:{frappe.utils.now_datetime().strftime('%Y%m%d%H%M')}"
		cache = frappe.cache()
		redis_key = cache.make_key(key)
		count = cache.incr(redis_key)
		cache.expire(redis_key, 90)
		if int(count or 0) > MAX_SENDS_PER_USER_PER_MINUTE:
			frappe.throw(_("WhatsApp send rate limit exceeded. Try again in a minute."))
	except frappe.ValidationError:
		raise
	except Exception:
		pass


def _post_whatsapp_js(payload):
	_get_whatsapp_js_url()
	whatsapp_url = _get_whatsapp_js_url()
	_validate_whatsapp_js_url(whatsapp_url)
	_enforce_whatsapp_rate_limit()
	import requests

	response = requests.post(whatsapp_url, json=payload, headers=_get_whatsapp_js_headers(), timeout=15)
	if response.ok:
		try:
			res_json = response.json()
			return res_json.get("id") or res_json.get("messageId") or res_json.get("whatsapp_message_id") or f"wa_js:{frappe.generate_hash(length=12)}"
		except Exception:
			return f"wa_js:{frappe.generate_hash(length=12)}"
	frappe.log_error(f"WhatsAppWebJS API Error ({response.status_code}): {response.text}", "WhatsAppWebJS Send Error")
	frappe.throw(_("Failed to send WhatsApp message via WhatsAppWebJS: {0}").format(response.text[:300]))


@frappe.whitelist()
def get_whatsapp_messages(reference_doctype: str, reference_name: str):
	reference_doc = validate_access(reference_doctype, reference_name)
	# twilio integration app is not compatible with crm app
	# crm has its own twilio integration in built
	if "twilio_integration" in frappe.get_installed_apps():
		return []
	if not frappe.db.exists("DocType", "WhatsApp Message"):
		return []
	messages = []

	if reference_doctype == "CRM Deal":
		lead = reference_doc.get("lead")
		if lead:
			validate_access("CRM Lead", lead)
			messages = frappe.get_all(
				"WhatsApp Message",
				filters={
					"reference_doctype": "CRM Lead",
					"reference_name": lead,
				},
				fields=[
					"name",
					"type",
					"to",
					"from",
					"content_type",
					"message_type",
					"attach",
					"template",
					"use_template",
					"message_id",
					"is_reply",
					"reply_to_message_id",
					"creation",
					"message",
					"status",
					"reference_doctype",
					"reference_name",
					"template_parameters",
					"template_header_parameters",
				],
			)

	messages += frappe.get_all(
		"WhatsApp Message",
		filters={
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
		},
		fields=[
			"name",
			"type",
			"to",
			"from",
			"content_type",
			"message_type",
			"attach",
			"template",
			"use_template",
			"message_id",
			"is_reply",
			"reply_to_message_id",
			"creation",
			"message",
			"status",
			"reference_doctype",
			"reference_name",
			"template_parameters",
			"template_header_parameters",
		],
	)

	# Filter messages to get only Template messages
	template_messages = [message for message in messages if message["message_type"] == "Template"]

	# Iterate through template messages
	for template_message in template_messages:
		# Find the template that this message is using
		if not frappe.db.exists("WhatsApp Templates", template_message["template"]):
			continue
		template = frappe.get_doc("WhatsApp Templates", template_message["template"])

		if template:
			template_message["template_name"] = template.template_name
			if template_message["template_parameters"]:
				parameters = json.loads(template_message["template_parameters"])
				template.template = parse_template_parameters(template.template, parameters)

			template_message["template"] = template.template
			if template_message["template_header_parameters"]:
				header_parameters = json.loads(template_message["template_header_parameters"])
				template.header = parse_template_parameters(template.header, header_parameters)
			template_message["header"] = template.header
			template_message["footer"] = template.footer

	# Filter messages to get only reaction messages
	reaction_messages = [message for message in messages if message["content_type"] == "reaction"]
	reaction_messages.reverse()

	# Iterate through reaction messages
	for reaction_message in reaction_messages:
		# Find the message that this reaction is reacting to
		reacted_message = next(
			(m for m in messages if m["message_id"] == reaction_message["reply_to_message_id"]),
			None,
		)

		# If the reacted message is found, add the reaction to it
		if reacted_message:
			reacted_message["reaction"] = reaction_message["message"]

	for message in messages:
		from_name = get_from_name(message) if message["from"] else _("You")
		message["from_name"] = from_name
	# Filter messages to get only replies
	reply_messages = [message for message in messages if message["is_reply"]]

	# Iterate through reply messages
	for reply_message in reply_messages:
		# Find the message that this message is replying to
		replied_message = next(
			(m for m in messages if m["message_id"] == reply_message["reply_to_message_id"]),
			None,
		)

		# If the replied message is found, add the reply details to the reply message
		if replied_message:
			from_name = get_from_name(reply_message) if replied_message["from"] else _("You")
			message = replied_message["message"]
			if replied_message["message_type"] == "Template":
				message = replied_message["template"]
			reply_message["reply_message"] = message
			reply_message["header"] = replied_message.get("header") or ""
			reply_message["footer"] = replied_message.get("footer") or ""
			reply_message["reply_to"] = replied_message["name"]
			reply_message["reply_to_type"] = replied_message["type"]
			reply_message["reply_to_from"] = from_name

	return [message for message in messages if message["content_type"] != "reaction"]


@frappe.whitelist()
def create_whatsapp_message(
	reference_doctype: str,
	reference_name: str,
	message: str,
	to: str,
	attach: str,
	reply_to: str,
	content_type: str = "text",
):
	validate_access(reference_doctype, reference_name)
	to = _normalize_whatsapp_number(to)
	message = cstr(message or "")
	if len(message) > MAX_FREE_TEXT_LENGTH:
		frappe.throw(_("WhatsApp message is too long. Keep it under {0} characters.").format(MAX_FREE_TEXT_LENGTH))
	
	payload = {
		"to": to,
		"phone": to,
		"number": to,
		"message": message,
		"text": message,
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
	}
	
	if attach:
		file_url = attach
		if file_url.startswith("/"):
			base_url = frappe.utils.get_url()
			file_url = f"{base_url}{file_url}"
		payload["attachment"] = file_url
		payload["mediaUrl"] = file_url
		payload["fileUrl"] = file_url

	try:
		return _post_whatsapp_js(payload)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "WhatsAppWebJS Send Exception")
		frappe.throw(_("Error connecting to WhatsAppWebJS server: {0}").format(str(e)))


@frappe.whitelist()
def send_whatsapp_template(reference_doctype: str, reference_name: str, template: str, to: str):
	validate_access(reference_doctype, reference_name)
	to = _normalize_whatsapp_number(to)
	
	payload = {
		"to": to,
		"phone": to,
		"number": to,
		"template": template,
		"message": f"Template message: {template}",
		"text": f"Template message: {template}",
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
	}

	try:
		return _post_whatsapp_js(payload)
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "WhatsAppWebJS Template Send Exception")
		frappe.throw(_("Error connecting to WhatsAppWebJS server: {0}").format(str(e)))


@frappe.whitelist()
def react_on_whatsapp_message(emoji: str, reply_to_name: str):
	validate_access()
	if not frappe.db.exists("WhatsApp Message", reply_to_name):
		frappe.throw(_("Referenced WhatsApp message does not exist."), frappe.DoesNotExistError)
	reply_to_doc = frappe.get_doc("WhatsApp Message", reply_to_name)

	if not reply_to_doc.has_permission("read"):
		frappe.throw(_("Not permitted to access the referenced WhatsApp message."), frappe.PermissionError)

	validate_access(reply_to_doc.reference_doctype, reply_to_doc.reference_name)

	to = (reply_to_doc.type == "Incoming" and reply_to_doc.get("from")) or reply_to_doc.to
	doc = frappe.new_doc("WhatsApp Message")
	doc.update(
		{
			"reference_doctype": reply_to_doc.reference_doctype,
			"reference_name": reply_to_doc.reference_name,
			"message": emoji,
			"to": to,
			"reply_to_message_id": reply_to_doc.message_id,
			"content_type": "reaction",
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


def parse_template_parameters(string, parameters):
	for i, parameter in enumerate(parameters, start=1):
		placeholder = "{{" + str(i) + "}}"
		string = string.replace(placeholder, str(parameter))

	return string


def get_from_name(message):
	doc = frappe.get_doc(message["reference_doctype"], message["reference_name"])
	from_name = ""
	if message["reference_doctype"] == "CRM Deal":
		if doc.get("contacts"):
			for c in doc.get("contacts"):
				if c.is_primary:
					from_name = c.full_name or c.mobile_no
					break
		else:
			from_name = doc.get("lead_name")
	else:
		from_name = " ".join(name for name in [doc.get("first_name"), doc.get("last_name")] if name)
	return from_name


def add_roles():
	if "frappe_whatsapp" not in frappe.get_installed_apps():
		return

	role_list = ["Sales Manager", "Sales User"]
	doctypes = ["WhatsApp Message", "WhatsApp Templates", "WhatsApp Settings"]
	for doctype in doctypes:
		for role in role_list:
			if frappe.db.exists("Custom DocPerm", {"parent": doctype, "role": role}):
				continue
			add_permission(doctype, role, 0, "write")
			update_permission_property(doctype, role, 0, "create", 1)
			update_permission_property(doctype, role, 0, "delete", 1)
			update_permission_property(doctype, role, 0, "share", 1)
			update_permission_property(doctype, role, 0, "email", 1)
			update_permission_property(doctype, role, 0, "print", 1)
			update_permission_property(doctype, role, 0, "report", 1)
			update_permission_property(doctype, role, 0, "export", 1)
