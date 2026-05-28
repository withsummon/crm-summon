import hashlib
import json
from datetime import timedelta

import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, now, today


CONVERSATION = "CRM Omnichannel Conversation"
MESSAGE = "CRM Omnichannel Message"
CHANNEL_ACCOUNT = "CRM Omnichannel Channel Account"
TEMPLATE = "CRM Omnichannel Template"
ROUTING_RULE = "CRM Omnichannel Routing Rule"
SLA_POLICY = "CRM Omnichannel SLA Policy"
NOTE = "CRM Omnichannel Note"
TRANSFER = "CRM Omnichannel Transfer"
BROADCAST = "CRM Omnichannel Broadcast Campaign"
BROADCAST_RECIPIENT = "CRM Omnichannel Broadcast Recipient"
ARCHIVE = "CRM Omnichannel Compliance Archive"
ANALYTICS = "CRM Omnichannel Analytics Snapshot"

CHANNELS = ["WhatsApp", "Email", "SMS", "In-App", "Voice"]
DEMO_WHATSAPP_RECIPIENTS = {
	"6285591150319": "Demo WhatsApp 0319",
	"6285774240730": "Demo WhatsApp 0730",
}
COUNT_KEYS = {
	"WhatsApp": "whatsapp",
	"Email": "email",
	"SMS": "sms",
	"In-App": "in_app",
	"Voice": "voice",
}


def _ready() -> bool:
	return frappe.db.exists("DocType", CONVERSATION) and frappe.db.exists("DocType", MESSAGE)


def _as_json(value) -> str:
	return json.dumps(value or {}, default=str, ensure_ascii=False)


def _loads(value, fallback=None):
	if not value:
		return fallback if fallback is not None else {}
	try:
		return json.loads(value)
	except Exception:
		return fallback if fallback is not None else {}


def _normalize_channel(channel: str | None) -> str:
	channel_map = {
		"WA": "WhatsApp",
		"Whatsapp": "WhatsApp",
		"whatsapp": "WhatsApp",
		"email": "Email",
		"sms": "SMS",
		"in_app": "In-App",
		"in-app": "In-App",
		"chat": "In-App",
		"call": "Voice",
		"voice": "Voice",
	}
	return channel_map.get(channel or "", channel or "In-App")


def _normalize_direction(direction: str | None) -> str:
	if direction in ("Incoming", "Received", "Inbound"):
		return "Inbound"
	if direction in ("Internal", "Internal Note"):
		return "Internal"
	return "Outbound"


def _normalize_status(status: str | None, direction: str = "Outbound") -> str:
	status_map = {
		"Incoming": "Received",
		"Received": "Received",
		"Open": "Received" if direction == "Inbound" else "Queued",
		"Manual": "Queued",
		"Pending Vendor": "Queued",
		"Unavailable": "Provider Not Configured",
		"Completed": "Sent",
		"Closed": "Sent",
	}
	allowed = {"Queued", "Sent", "Delivered", "Read", "Received", "Failed", "Provider Not Configured"}
	mapped = status_map.get(status or "", status or ("Received" if direction == "Inbound" else "Queued"))
	return mapped if mapped in allowed else ("Received" if direction == "Inbound" else "Queued")


def _provider_message_id(channel: str, source_doctype: str | None, source_name: str | None, raw_id: str | None) -> str:
	base = raw_id or ":".join(part for part in [source_doctype, source_name] if part)
	if not base:
		base = frappe.generate_hash(length=16)
	return f"{_normalize_channel(channel)}:{base}"


def _clean_tags(tags) -> list[str]:
	if isinstance(tags, str):
		return [tag.strip() for tag in tags.split(",") if tag.strip()]
	if isinstance(tags, (list, tuple, set)):
		return [str(tag).strip() for tag in tags if str(tag).strip()]
	return []


def _normalize_demo_phone(value: str | None) -> str:
	digits = "".join(ch for ch in str(value or "") if ch.isdigit())
	if digits.startswith("0"):
		digits = f"62{digits[1:]}"
	return digits


def _default_customer_group() -> str | None:
	return (
		frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
		or frappe.db.get_value("Customer Group", "Commercial", "name")
		or frappe.db.get_value("Customer Group", {"is_group": 1}, "name")
	)


def _default_territory() -> str | None:
	return (
		frappe.db.get_default("territory")
		or frappe.db.get_value("Territory", {"is_group": 0}, "name")
		or frappe.db.get_value("Territory", "All Territories", "name")
	)


def _conversation_doc(name: str):
	if not frappe.db.exists(CONVERSATION, name):
		frappe.throw(_("Conversation {0} does not exist").format(name), frappe.DoesNotExistError)
	return frappe.get_doc(CONVERSATION, name)


def _get_customer_from_reference(reference_doctype=None, reference_name=None, explicit_customer=None):
	if explicit_customer and frappe.db.exists("Customer", explicit_customer):
		return explicit_customer
	if not reference_doctype or not reference_name or not frappe.db.exists(reference_doctype, reference_name):
		return None
	if reference_doctype == "Customer":
		return reference_name
	for fieldname in ("customer", "party_name"):
		if frappe.get_meta(reference_doctype).has_field(fieldname):
			customer = frappe.db.get_value(reference_doctype, reference_name, fieldname)
			if customer and frappe.db.exists("Customer", customer):
				return customer
	return None


def _display_name_for_reference(reference_doctype=None, reference_name=None, customer=None, sender=None):
	if customer and frappe.db.exists("Customer", customer):
		return frappe.db.get_value("Customer", customer, "customer_name") or customer
	if reference_doctype and reference_name and frappe.db.exists(reference_doctype, reference_name):
		meta = frappe.get_meta(reference_doctype)
		for fieldname in ("lead_name", "organization_name", "customer_name", "first_name", "subject"):
			if meta.has_field(fieldname):
				value = frappe.db.get_value(reference_doctype, reference_name, fieldname)
				if value:
					return value
		return reference_name
	return sender or _("Unknown Customer")


def _default_account(channel: str):
	if not frappe.db.exists("DocType", CHANNEL_ACCOUNT):
		return None
	account = frappe.db.get_value(
		CHANNEL_ACCOUNT,
		{"channel": channel, "is_default": 1},
		["name", "status", "credentials_configured", "provider"],
		as_dict=True,
	)
	if account:
		return account
	return frappe.db.get_value(
		CHANNEL_ACCOUNT,
		{"channel": channel},
		["name", "status", "credentials_configured", "provider"],
		as_dict=True,
	)


def _provider_status(channel: str) -> dict:
	channel = _normalize_channel(channel)
	account = _default_account(channel)
	status = "Provider Not Configured"
	provider = None
	if account and account.status == "Active" and account.credentials_configured:
		status = "Active"
		provider = account.provider
	if channel == "WhatsApp":
		try:
			if frappe.get_attr("crm.api.whatsapp.is_whatsapp_enabled")():
				status = "Active"
				provider = provider or "WhatsApp Business"
		except Exception:
			pass
	if channel == "Email" and frappe.db.exists("DocType", "Email Account"):
		if frappe.db.exists("Email Account", {"enable_outgoing": 1}):
			status = "Active"
			provider = provider or "Frappe Email"
	if channel == "Email" and frappe.conf.get("mail_server") and frappe.conf.get("mail_login"):
		status = "Active"
		provider = provider or "SMTP"
	if channel == "In-App":
		status = "Active"
		if not provider:
			provider = "Frappe In-App"
	return {"channel": channel, "status": status, "provider": provider, "account": account.name if account else None}


def _match_conversation(
	channel: str,
	customer=None,
	reference_doctype=None,
	reference_name=None,
	provider_conversation_id=None,
	sender=None,
):
	filters = {"channel": channel}
	if provider_conversation_id:
		filters["provider_conversation_id"] = provider_conversation_id
		found = frappe.db.get_value(CONVERSATION, filters, "name")
		if found:
			return found
	if reference_doctype and reference_name:
		found = frappe.db.get_value(
			CONVERSATION,
			{"channel": channel, "reference_doctype": reference_doctype, "reference_name": reference_name, "status": ["!=", "Archived"]},
			"name",
		)
		if found:
			return found
	if customer:
		found = frappe.db.get_value(
			CONVERSATION,
			{"channel": channel, "customer": customer, "status": ["!=", "Archived"]},
			"name",
		)
		if found:
			return found
	if sender:
		found = frappe.db.sql(
			"""
			SELECT c.name
			FROM `tabCRM Omnichannel Conversation` c
			INNER JOIN `tabCRM Omnichannel Message` m ON m.conversation = c.name
			WHERE c.channel = %s AND (m.from_party = %s OR m.to_party = %s)
			ORDER BY c.modified DESC
			LIMIT 1
			""",
			(channel, sender, sender),
			as_dict=True,
		)
		if found:
			return found[0].name
	return None


def _ensure_conversation(
	channel: str,
	subject=None,
	customer=None,
	reference_doctype=None,
	reference_name=None,
	contact=None,
	provider_conversation_id=None,
	sender=None,
	priority="Normal",
	payload=None,
):
	channel = _normalize_channel(channel)
	customer = _get_customer_from_reference(reference_doctype, reference_name, customer)
	existing = _match_conversation(channel, customer, reference_doctype, reference_name, provider_conversation_id, sender)
	if existing:
		return frappe.get_doc(CONVERSATION, existing)
	display_name = _display_name_for_reference(reference_doctype, reference_name, customer, sender)
	account = _default_account(channel)
	doc = frappe.get_doc(
		{
			"doctype": CONVERSATION,
			"subject": subject or f"{channel} - {display_name}",
			"channel": channel,
			"status": "Open",
			"priority": priority or "Normal",
			"customer": customer,
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"contact": contact,
			"channel_account": account.name if account else None,
			"provider_conversation_id": provider_conversation_id,
			"assigned_to": frappe.session.user if frappe.session.user != "Guest" else None,
			"payload_json": _as_json(payload),
		}
	)
	_apply_sla(doc)
	doc.insert(ignore_permissions=True)
	evaluate_routing(doc.name)
	return frappe.get_doc(CONVERSATION, doc.name)


def _apply_sla(doc):
	if not frappe.db.exists("DocType", SLA_POLICY):
		return
	filters = {"enabled": 1}
	if doc.channel:
		filters["channel"] = ["in", [doc.channel, ""]]
	policy = frappe.db.get_value(
		SLA_POLICY,
		filters,
		["first_response_minutes"],
		as_dict=True,
		order_by="modified desc",
	)
	minutes = int(policy.first_response_minutes) if policy and policy.first_response_minutes else 60
	doc.sla_status = "Running"
	doc.first_response_due_on = add_to_date(now(), minutes=minutes, as_string=True)


def _touch_conversation(conversation, message_doc=None):
	if isinstance(conversation, str):
		conversation = frappe.get_doc(CONVERSATION, conversation)
	if message_doc:
		conversation.last_message_at = message_doc.sent_or_received_on or now()
		conversation.last_message_preview = frappe.utils.strip_html(message_doc.content or "")[:180]
		if message_doc.direction == "Inbound":
			conversation.unread_count = (conversation.unread_count or 0) + 1
			if conversation.channel == "WhatsApp":
				conversation.reply_window_ends_on = add_to_date(
					message_doc.sent_or_received_on or now(), hours=24, as_string=True
				)
		if message_doc.direction == "Outbound" and not conversation.first_responded_on:
			conversation.first_responded_on = message_doc.sent_or_received_on or now()
			conversation.sla_status = "Fulfilled"
	conversation.save(ignore_permissions=True)


def _create_message(conversation, payload: dict):
	channel = _normalize_channel(payload.get("channel") or conversation.channel)
	provider_id = _provider_message_id(
		channel,
		payload.get("source_doctype"),
		payload.get("source_name"),
		payload.get("provider_message_id"),
	)
	existing = frappe.db.get_value(MESSAGE, {"provider_message_id": provider_id}, "name")
	if existing:
		return frappe.get_doc(MESSAGE, existing), False
	doc = frappe.get_doc(
		{
			"doctype": MESSAGE,
			"conversation": conversation.name,
			"channel": channel,
			"direction": _normalize_direction(payload.get("direction")),
			"message_type": payload.get("message_type") or "Text",
			"status": _normalize_status(
				payload.get("status"), _normalize_direction(payload.get("direction"))
			),
			"sent_or_received_on": payload.get("sent_or_received_on") or now(),
			"from_party": payload.get("from_party"),
			"to_party": payload.get("to_party"),
			"content": payload.get("content"),
			"attachment": payload.get("attachment"),
			"template": payload.get("template"),
			"provider_message_id": provider_id,
			"reply_to_provider_message_id": payload.get("reply_to_provider_message_id"),
			"delivered_on": payload.get("delivered_on"),
			"read_on": payload.get("read_on"),
			"failed_reason": payload.get("failed_reason"),
			"confidence": payload.get("confidence"),
			"is_internal": 1 if _normalize_direction(payload.get("direction")) == "Internal" else 0,
			"payload_json": _as_json(payload.get("payload")),
		}
	)
	doc.insert(ignore_permissions=True)
	_touch_conversation(conversation, doc)
	frappe.publish_realtime(
		"omnichannel_message",
		{
			"conversation": conversation.name,
			"message": doc.name,
			"direction": doc.direction,
			"channel": doc.channel,
			"content": doc.content,
			"from_party": doc.from_party,
		},
		after_commit=True,
	)
	return doc, True


def _row(doc) -> dict:
	return {
		"name": doc.name,
		"subject": doc.subject,
		"channel": doc.channel,
		"status": doc.status,
		"priority": doc.priority,
		"customer": doc.customer,
		"customer_name": frappe.db.get_value("Customer", doc.customer, "customer_name") if doc.customer else None,
		"reference_doctype": doc.reference_doctype,
		"reference_name": doc.reference_name,
		"last_message_at": doc.last_message_at,
		"last_message_preview": doc.last_message_preview,
		"unread_count": doc.unread_count or 0,
		"assigned_to": doc.assigned_to,
		"sla_status": doc.sla_status,
		"first_response_due_on": doc.first_response_due_on,
		"reply_window_ends_on": doc.reply_window_ends_on,
		"tags": _clean_tags(doc.tags),
		"provider_status": _provider_status(doc.channel),
	}


def _ensure_demo_whatsapp_conversations():
	"""Ensure the two allowlisted demo WhatsApp numbers have active conversation history."""
	for recipient, customer_name in DEMO_WHATSAPP_RECIPIENTS.items():
		normalized = _normalize_demo_phone(recipient)
		# Check if conversation already exists
		existing = frappe.db.get_value(
			CONVERSATION,
			{"channel": "WhatsApp", "provider_conversation_id": normalized},
			"name"
		)
		if existing:
			continue

		# Create/Get Customer
		customer = ensure_demo_whatsapp_customer(normalized)
		customer_id = customer.get("name")

		# Create conversation
		conv = _ensure_conversation(
			channel="WhatsApp",
			subject=f"WhatsApp Demo - {customer_name}",
			customer=customer_id,
			reference_doctype="Customer",
			reference_name=customer_id,
			provider_conversation_id=normalized,
		)

		# Generate messages
		if normalized == "6285591150319":
			messages = [
				("Inbound", "Halo BNI, saya tertarik dengan Kredit Modal Kerja BNI. Bagaimana persyaratannya?", -30),
				("Outbound", "Halo Pak! Terima kasih telah menghubungi BNI. Persyaratannya cukup mudah, salah satunya melampirkan NPWP dan laporan keuangan audit. Apakah Bapak sudah memiliki dokumen tersebut?", -25),
				("Inbound", "NPWP sudah ada, laporan keuangan juga ada. Nanti saya kirimkan lewat sini ya.", -20),
				("Outbound", "Baik Pak, siap kami terima dan proses segera.", -15),
				("Inbound", "Oke siap Pak RM!", -10),
			]
		else:
			messages = [
				("Inbound", "Siang Pak, permohonan restructuring untuk PT Bhakti Nusantara apakah sudah disetujui?", -30),
				("Outbound", "Selamat siang Pak. Restructuring proposal saat ini sedang dalam proses review oleh komite kredit BNI. Kami targetkan selesai akhir minggu ini.", -25),
				("Inbound", "Baik Pak, tolong dibantu ya karena cashflow kami agak ketat bulan ini.", -20),
				("Outbound", "Tentu Pak, kami upayakan solusi terbaik untuk menjaga DSCR perusahaan Bapak.", -15),
				("Inbound", "Terima kasih banyak atas dukungannya!", -10),
			]

		for direction, content, offset_minutes in messages:
			msg_time = add_to_date(now(), minutes=offset_minutes, as_string=True)
			# Create mock message doc
			_create_message(
				conv,
				{
					"channel": "WhatsApp",
					"direction": direction,
					"message_type": "Text",
					"status": "Received" if direction == "Inbound" else "Sent",
					"sent_or_received_on": msg_time,
					"from_party": normalized if direction == "Inbound" else frappe.session.user,
					"to_party": frappe.session.user if direction == "Inbound" else normalized,
					"provider_message_id": f"demo:{normalized}:{hashlib.md5(content.encode()).hexdigest()[:8]}",
					"content": content,
				}
			)


@frappe.whitelist()
def get_conversations(
	channel: str | None = None,
	search: str | None = None,
	status: str | None = None,
	assigned_to: str | None = None,
	tag: str | None = None,
	sort: str = "recent",
	unread_only: bool = False,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	limit: int = 50,
	offset: int = 0,
):
	if not _ready():
		return {"rows": [], "counts": {"all": 0, "whatsapp": 0, "email": 0, "sms": 0, "in_app": 0, "voice": 0}, "has_more": False}

	try:
		_ensure_demo_whatsapp_conversations()
	except Exception:
		pass
	filters = {}
	if channel and channel != "All":
		filters["channel"] = _normalize_channel(channel)
	if status:
		filters["status"] = status
	else:
		filters["status"] = ["!=", "Archived"]
	if assigned_to:
		filters["assigned_to"] = assigned_to
	if reference_doctype:
		filters["reference_doctype"] = reference_doctype
	if reference_name:
		filters["reference_name"] = reference_name
	if unread_only in (True, "true", "1", 1):
		filters["unread_count"] = [">", 0]
	if tag:
		filters["tags"] = ["like", f"%{tag}%"]
	or_filters = None
	if search:
		or_filters = {
			"subject": ["like", f"%{search}%"],
			"last_message_preview": ["like", f"%{search}%"],
			"reference_name": ["like", f"%{search}%"],
		}
	order_by = "last_message_at desc"
	if sort == "unread":
		order_by = "unread_count desc, last_message_at desc"
	elif sort == "priority":
		order_by = "priority desc, last_message_at desc"
	rows = frappe.get_all(
		CONVERSATION,
		filters=filters,
		or_filters=or_filters,
		fields=["*"],
		order_by=order_by,
		limit_start=int(offset or 0),
		limit_page_length=int(limit or 50) + 1,
	)
	counts = {"all": frappe.db.count(CONVERSATION, {"status": ["!=", "Archived"]})}
	for channel_name, key in COUNT_KEYS.items():
		counts[key] = frappe.db.count(CONVERSATION, {"channel": channel_name, "status": ["!=", "Archived"]})
	has_more = len(rows) > int(limit or 50)
	return {"rows": [_row(row) for row in rows[: int(limit or 50)]], "counts": counts, "has_more": has_more}


@frappe.whitelist()
def get_conversation(conversation_id: str):
	if not _ready():
		frappe.throw(_("Omnichannel workspace is not migrated yet"))
	conversation = _conversation_doc(conversation_id)
	messages = frappe.get_all(
		MESSAGE,
		filters={"conversation": conversation.name},
		fields=["*"],
		order_by="sent_or_received_on asc, creation asc",
	)
	notes = frappe.get_all(NOTE, filters={"conversation": conversation.name}, fields=["*"], order_by="creation asc") if frappe.db.exists("DocType", NOTE) else []
	transfers = frappe.get_all(TRANSFER, filters={"conversation": conversation.name}, fields=["*"], order_by="creation desc") if frappe.db.exists("DocType", TRANSFER) else []
	customer_context = {}
	if conversation.customer:
		try:
			customer_context = frappe.get_attr("crm.api.credit.get_customer_360")(conversation.customer)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Omnichannel Customer 360 context failed")
			customer_context = {"error": _("Customer 360 context unavailable")}
	return {
		"conversation": _row(conversation),
		"messages": messages,
		"participants": _participants(conversation, messages),
		"notes": notes,
		"transfers": transfers,
		"customer_context": customer_context,
		"sla": _sla_payload(conversation),
		"routing": {"assigned_to": conversation.assigned_to, "owner_team": conversation.owner_team},
		"provider_status": _provider_status(conversation.channel),
	}


def _participants(conversation, messages) -> list[dict]:
	seen = {}
	if conversation.assigned_to:
		seen[conversation.assigned_to] = {"type": "Agent", "name": conversation.assigned_to}
	for msg in messages:
		for key in ("from_party", "to_party"):
			value = msg.get(key)
			if value and value not in seen:
				seen[value] = {"type": "Contact", "name": value}
	return list(seen.values())


def _sla_payload(conversation) -> dict:
	due_on = get_datetime(conversation.first_response_due_on) if conversation.first_response_due_on else None
	is_breached = bool(due_on and not conversation.first_responded_on and get_datetime(now()) > due_on)
	return {
		"status": "Breached" if is_breached else conversation.sla_status,
		"first_response_due_on": conversation.first_response_due_on,
		"first_responded_on": conversation.first_responded_on,
		"breached_on": conversation.breached_on,
		"is_breached": is_breached,
	}


def _last_counterparty(conversation) -> str | None:
	row = frappe.get_all(
		MESSAGE,
		filters={"conversation": conversation.name, "direction": "Inbound"},
		fields=["from_party"],
		order_by="sent_or_received_on desc, creation desc",
		limit=1,
	)
	return row[0].from_party if row else None


def _send_to_provider(conversation, content=None, template=None, attachment=None, recipient=None) -> dict:
	to_party = recipient or _last_counterparty(conversation)
	if conversation.channel == "WhatsApp":
		if not to_party:
			to_party = frappe.db.get_value("Customer", conversation.customer, "mobile_no") or conversation.customer
		if not conversation.reference_doctype or not conversation.reference_name or not to_party:
			return {"status": "Failed", "failed_reason": _("WhatsApp reference and recipient are required")}
		if template:
			name = frappe.get_attr("crm.api.whatsapp.send_whatsapp_template")(
				conversation.reference_doctype, conversation.reference_name, template, to_party
			)
		else:
			name = frappe.get_attr("crm.api.whatsapp.create_whatsapp_message")(
				conversation.reference_doctype,
				conversation.reference_name,
				content,
				to_party,
				attachment,
				"",
			)
		return {"status": "Queued", "provider_message_id": name, "to_party": to_party}
	if conversation.channel == "Email":
		if not to_party:
			to_party = frappe.db.get_value("Customer", conversation.customer, "email_id") or conversation.customer
		if not to_party:
			return {"status": "Failed", "failed_reason": _("Email recipient is required")}
		try:
			frappe.sendmail(
				recipients=to_party,
				subject=conversation.subject or _("Omnichannel Reply"),
				content=content or "",
				reference_doctype=conversation.reference_doctype,
				reference_name=conversation.reference_name,
				now=True,
			)
		except Exception:
			frappe.log_error(frappe.get_traceback(), "Omnichannel sendmail native fallback failed")
			return {"status": "Failed", "failed_reason": _("SMTP send failed. Check outgoing Email Account or SMTP site config."), "to_party": to_party}
		doc = frappe.get_doc(
			{
				"doctype": "Communication",
				"communication_type": "Communication",
				"sent_or_received": "Sent",
				"subject": conversation.subject or _("Omnichannel Reply"),
				"content": content or "",
				"recipients": to_party,
				"reference_doctype": conversation.reference_doctype,
				"reference_name": conversation.reference_name,
			}
		)
		doc.insert(ignore_permissions=True)
		return {"status": "Sent", "provider_message_id": doc.name, "to_party": to_party}
	if conversation.channel in ["SMS", "Voice"]:
		if not to_party:
			to_party = frappe.db.get_value("Customer", conversation.customer, "mobile_no") or conversation.customer
	return {"status": "Sent", "provider_message_id": None, "to_party": to_party}


@frappe.whitelist(allow_guest=True)
def upsert_inbound_message(
	channel: str,
	content: str | None = None,
	provider_message_id: str | None = None,
	sender: str | None = None,
	recipient: str | None = None,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	customer: str | None = None,
	subject: str | None = None,
	status: str | None = None,
	message_type: str = "Text",
	attachment: str | None = None,
	payload=None,
):
	if frappe.session.user == "Guest":
		token = (frappe.get_request_header("X-Webhook-Token") or "").strip()
		expected_token = (frappe.conf.get("whatsapp_api_token") or "").strip()
		if not expected_token or token != expected_token:
			frappe.throw(_("Unauthorized access"), frappe.PermissionError)

	if not _ready():
		frappe.throw(_("Omnichannel workspace is not migrated yet"))
	channel = _normalize_channel(channel)
	conversation = _ensure_conversation(
		channel=channel,
		subject=subject,
		customer=customer,
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		sender=sender,
		provider_conversation_id=(payload or {}).get("provider_conversation_id") if isinstance(payload, dict) else None,
		payload=payload,
	)
	message, created = _create_message(
		conversation,
		{
			"channel": channel,
			"direction": "Inbound",
			"message_type": message_type,
			"status": status or "Received",
			"content": content,
			"attachment": attachment,
			"from_party": sender,
			"to_party": recipient,
			"provider_message_id": provider_message_id,
			"payload": payload,
		},
	)
	return {"status": "Created" if created else "Duplicate", "conversation": conversation.name, "message": message.name}


@frappe.whitelist()
def send_message(
	conversation_id: str,
	content: str | None = None,
	template: str | None = None,
	attachments=None,
	scheduled_at: str | None = None,
	metadata=None,
	recipient: str | None = None,
):
	conversation = _conversation_doc(conversation_id)
	metadata = _loads(metadata, {}) if isinstance(metadata, str) else (metadata or {})
	if not content and not template and not attachments:
		frappe.throw(_("Message content, template, or attachment is required"))
	if metadata.get("internal_note"):
		note = frappe.get_doc(
			{
				"doctype": NOTE,
				"conversation": conversation.name,
				"note": content,
				"created_by": frappe.session.user,
			}
		)
		note.insert(ignore_permissions=True)
		message, _created = _create_message(
			conversation,
			{
				"channel": conversation.channel,
				"direction": "Internal",
				"message_type": "Internal Note",
				"status": "Sent",
				"content": content,
				"from_party": frappe.session.user,
				"provider_message_id": f"internal:{conversation.name}:{note.name}",
			},
		)
		return {"status": "Sent", "message": message.name, "note": note.name, "provider_status": {"status": "Internal"}}
	provider = _provider_status(conversation.channel)
	status = "Queued"
	failed_reason = None
	provider_result = {}
	attachment = (attachments or [None])[0] if isinstance(attachments, list) else attachments
	if provider["status"] != "Active":
		status = "Provider Not Configured"
		failed_reason = _("Provider Not Configured")
	elif conversation.channel == "WhatsApp" and conversation.reply_window_ends_on:
		if get_datetime(now()) > get_datetime(conversation.reply_window_ends_on) and not template:
			status = "Failed"
			failed_reason = _("WhatsApp free-text reply window has expired. Use an approved template.")
	if provider["status"] == "Active" and status == "Queued":
		provider_result = _send_to_provider(conversation, content, template, attachment, recipient=recipient)
		status = provider_result.get("status") or status
		failed_reason = provider_result.get("failed_reason")
	message, _created = _create_message(
		conversation,
		{
			"channel": conversation.channel,
			"direction": "Outbound",
			"message_type": "Template" if template else "Text",
			"status": status,
			"content": content,
			"template": template,
			"attachment": attachment,
			"from_party": frappe.session.user,
			"to_party": provider_result.get("to_party") or recipient or conversation.reference_name or conversation.customer,
			"provider_message_id": provider_result.get("provider_message_id") or f"outbound:{conversation.name}:{frappe.generate_hash(length=10)}",
			"failed_reason": failed_reason,
			"payload": {"scheduled_at": scheduled_at, "metadata": metadata, "provider": provider},
		},
	)
	return {"status": message.status, "message": message.name, "provider_status": provider, "failed_reason": failed_reason}


@frappe.whitelist()
def upload_message_attachment(conversation_id: str, file_url: str, file_name: str | None = None):
	conversation = _conversation_doc(conversation_id)
	message, _created = _create_message(
		conversation,
		{
			"channel": conversation.channel,
			"direction": "Outbound",
			"message_type": "Document",
			"status": _provider_status(conversation.channel)["status"] if _provider_status(conversation.channel)["status"] != "Active" else "Queued",
			"content": file_name or file_url,
			"attachment": file_url,
			"from_party": frappe.session.user,
			"provider_message_id": f"attachment:{conversation.name}:{frappe.generate_hash(length=10)}",
		},
	)
	return {"status": message.status, "message": message.name}


@frappe.whitelist()
def bulk_update_conversations(conversation_ids, action: str, value=None):
	if isinstance(conversation_ids, str):
		conversation_ids = _loads(conversation_ids, []) if conversation_ids.startswith("[") else [conversation_ids]
	updated = []
	for conversation_id in conversation_ids or []:
		if not frappe.db.exists(CONVERSATION, conversation_id):
			continue
		doc = frappe.get_doc(CONVERSATION, conversation_id)
		if action == "tag":
			tags = set(_clean_tags(doc.tags))
			tags.update(_clean_tags(value))
			doc.tags = ", ".join(sorted(tags))
		elif action == "assign":
			doc.assigned_to = value
		elif action == "close":
			doc.status = "Closed"
			doc.closed_on = now()
			doc.closed_by = frappe.session.user
		elif action == "archive":
			archive_conversation(doc.name)
			doc.status = "Archived"
			doc.archived = 1
		else:
			frappe.throw(_("Unsupported bulk action {0}").format(action))
		doc.save(ignore_permissions=True)
		updated.append(doc.name)
	return {"status": "Updated", "updated": updated}


@frappe.whitelist()
def evaluate_routing(conversation_id: str):
	conversation = _conversation_doc(conversation_id)
	if not frappe.db.exists("DocType", ROUTING_RULE):
		return {"status": "No Rules", "assigned_to": conversation.assigned_to, "owner_team": conversation.owner_team}
	rules = frappe.get_all(
		ROUTING_RULE,
		filters={"enabled": 1},
		fields=["*"],
		order_by="priority asc, modified asc",
	)
	for rule in rules:
		if rule.channel and rule.channel != conversation.channel:
			continue
		haystack = " ".join([conversation.subject or "", conversation.last_message_preview or ""]).lower()
		if rule.keyword and rule.keyword.lower() not in haystack:
			continue
		if rule.sender_contains and rule.sender_contains.lower() not in haystack:
			continue
		if rule.assign_to:
			conversation.assigned_to = rule.assign_to
		if rule.assign_team:
			conversation.owner_team = rule.assign_team
		conversation.save(ignore_permissions=True)
		return {"status": "Matched", "rule": rule.name, "assigned_to": conversation.assigned_to, "owner_team": conversation.owner_team}
	return {"status": "Fallback", "assigned_to": conversation.assigned_to, "owner_team": conversation.owner_team}


@frappe.whitelist()
def get_templates(channel: str | None = None, language: str | None = None):
	if not frappe.db.exists("DocType", TEMPLATE):
		return []
	filters = {"is_active": 1}
	if channel:
		filters["channel"] = _normalize_channel(channel)
	if language:
		filters["language"] = language
	return frappe.get_all(TEMPLATE, filters=filters, fields=["*"], order_by="modified desc")


@frappe.whitelist()
def save_template(payload):
	payload = _loads(payload, {}) if isinstance(payload, str) else payload
	if not payload.get("template_code") or not payload.get("body"):
		frappe.throw(_("Template code and body are required"))
	name = frappe.db.get_value(TEMPLATE, {"template_code": payload["template_code"]}, "name")
	doc = frappe.get_doc(TEMPLATE, name) if name else frappe.new_doc(TEMPLATE)
	for field in ["template_code", "template_name", "channel", "language", "version", "status", "whatsapp_approved", "subject", "body", "merge_fields", "is_active"]:
		if field in payload:
			doc.set(field, payload.get(field))
	doc.channel = _normalize_channel(doc.channel)
	doc.insert(ignore_permissions=True) if doc.is_new() else doc.save(ignore_permissions=True)
	return {"status": "Saved", "template": doc.name}


@frappe.whitelist()
def generate_reply_suggestions(conversation_id: str, tone: str = "Formal"):
	detail = get_conversation(conversation_id)
	provider = {"status": "Provider Not Configured"}

	def _template_suggestions():
		last_msg = (detail.get("messages") or [None])[-1]
		last_content = (last_msg.get("content") or "").lower() if last_msg else ""
		if any(w in last_content for w in ["price", "cost", "rate", "biaya", "bunga", "tarif", "berapa"]):
			return [
				"Terima kasih atas pertanyaan Anda. Kami akan menyampaikan informasi pricing yang kompetitif sesuai kebutuhan Anda.",
				"Untuk detail pricing, kami sarankan diskusi lebih lanjut dengan relationship manager kami.",
				"Kami dapat mengirimkan proposal penawaran khusus untuk Anda. Apakah berminat?",
			]
		if any(w in last_content for w in ["status", "progress", "update", "dimana", "kapan", "proses"]):
			return [
				"Terima kasih atas kesabarannya. Saat ini aplikasi Anda sedang dalam proses review.",
				"Kami akan mengupdate status aplikasi Anda dalam 1-2 hari kerja.",
				"Silakan hubungi kami kembali jika tidak ada perkembangan dalam 3 hari.",
			]
		if any(w in last_content for w in ["complaint", "keluhan", "masalah", "error", "gagal", "rusak"]):
			return [
				"Kami mohon maaf atas ketidaknyamanan yang Anda alami. Tim kami akan segera menindaklanjuti.",
				"Kami mencatat keluhan Anda dan akan memprioritaskan penyelesaiannya.",
				"Terima kasih atas laporannya. Kami akan menghubungi Anda dalam 1x24 jam.",
			]
		return [
			"Terima kasih telah menghubungi BNI. Ada yang bisa kami bantu lebih lanjut?",
			"Kami akan menindaklanjuti permintaan Anda dan menghubungi kembali segera.",
			"Silakan informasikan jika ada kebutuhan lain yang dapat kami bantu.",
		]

	try:
		prompt = (
			f"Generate 3 {tone} reply suggestions for this customer conversation. "
			"Return concise actionable options.\n\n"
			f"Conversation: {json.dumps(detail['conversation'], default=str)}\n"
			f"Messages: {json.dumps(detail['messages'][-10:], default=str)}\n"
			f"Customer context: {json.dumps(detail.get('customer_context') or {}, default=str)[:5000]}"
		)
		response = frappe.get_attr("crm.api.ai_agent_center.query_agent")("general", prompt, customer=detail["conversation"].get("customer"))
		text = response.get("response") if isinstance(response, dict) else str(response)

		# Guardrail-blocked responses (no indexed data) should not appear as suggestions
		guardrail_indicators = [
			"belum memiliki sumber", "tidak memiliki sumber", "cukup untuk menjawab",
			"cukup untuk dianalisis", "tidak cukup data", "belum cukup",
			"do not have enough", "insufficient data", "cannot answer"
		]
		is_blocked = any(indicator in text.lower() for indicator in guardrail_indicators)
		if is_blocked:
			return {"status": "Fallback", "tone": tone, "suggestions": _template_suggestions(), "provider_status": provider}

		options = [line.strip(" -0123456789.") for line in text.splitlines() if line.strip()]
		options = [item for item in options if item][:3]
		return {"status": "Generated", "tone": tone, "suggestions": options or [text], "provider_status": {"status": "Active"}}
	except Exception:
		return {"status": "Fallback", "tone": tone, "suggestions": _template_suggestions(), "provider_status": provider}


@frappe.whitelist()
def recalculate_sla(conversation_id: str):
	conversation = _conversation_doc(conversation_id)
	sla = _sla_payload(conversation)
	if sla["is_breached"]:
		conversation.sla_status = "Breached"
		conversation.breached_on = conversation.breached_on or now()
		conversation.save(ignore_permissions=True)
	return {"status": conversation.sla_status, **_sla_payload(conversation)}


def process_sla_breaches():
	if not _ready():
		return
	rows = frappe.get_all(
		CONVERSATION,
		filters={
			"status": ["in", ["Open", "Pending"]],
			"sla_status": ["in", ["Running", "Not Started"]],
			"first_response_due_on": ["<", now()],
			"first_responded_on": ["is", "not set"],
		},
		fields=["name"],
		limit_page_length=500,
	)
	for row in rows:
		doc = frappe.get_doc(CONVERSATION, row.name)
		doc.sla_status = "Breached"
		doc.breached_on = doc.breached_on or now()
		doc.save(ignore_permissions=True)


@frappe.whitelist()
def create_broadcast(payload):
	payload = _loads(payload, {}) if isinstance(payload, str) else payload
	doc = frappe.get_doc(
		{
			"doctype": BROADCAST,
			"campaign_name": payload.get("campaign_name") or _("Untitled Broadcast"),
			"channel": _normalize_channel(payload.get("channel") or "WhatsApp"),
			"template": payload.get("template"),
			"status": "Scheduled" if payload.get("scheduled_at") else "Draft",
			"scheduled_at": payload.get("scheduled_at"),
			"throttle_per_minute": payload.get("throttle_per_minute") or 30,
			"segment_json": _as_json(payload.get("segment")),
			"total_recipients": len(payload.get("recipients") or []),
		}
	)
	doc.insert(ignore_permissions=True)
	for recipient in payload.get("recipients") or []:
		frappe.get_doc(
			{
				"doctype": BROADCAST_RECIPIENT,
				"campaign": doc.name,
				"customer": recipient.get("customer"),
				"recipient": recipient.get("recipient") or recipient.get("phone") or recipient.get("email"),
				"status": "Queued",
			}
		).insert(ignore_permissions=True)
	return {"status": doc.status, "campaign": doc.name, "recipient_count": doc.total_recipients}


@frappe.whitelist()
def get_broadcast_report(campaign_id: str):
	if not frappe.db.exists(BROADCAST, campaign_id):
		frappe.throw(_("Broadcast campaign {0} does not exist").format(campaign_id), frappe.DoesNotExistError)
	campaign = frappe.get_doc(BROADCAST, campaign_id)
	recipients = frappe.get_all(BROADCAST_RECIPIENT, filters={"campaign": campaign_id}, fields=["*"])
	counts = {}
	for row in recipients:
		counts[row.status] = counts.get(row.status, 0) + 1
	return {"campaign": campaign.as_dict(), "recipients": recipients, "counts": counts}


@frappe.whitelist()
def get_channel_kpis(filters=None):
	if not _ready():
		return []
	result = []
	for channel in CHANNELS:
		total = frappe.db.count(CONVERSATION, {"channel": channel})
		inbound = frappe.db.count(MESSAGE, {"channel": channel, "direction": "Inbound"})
		outbound = frappe.db.count(MESSAGE, {"channel": channel, "direction": "Outbound"})
		breached = frappe.db.count(CONVERSATION, {"channel": channel, "sla_status": "Breached"})
		result.append({"channel": channel, "volume": total, "inbound_count": inbound, "outbound_count": outbound, "breach_count": breached})
	return result


def archive_conversation(conversation_id: str):
	detail = get_conversation(conversation_id)
	snapshot = _as_json(detail)
	archive_hash = hashlib.sha256(snapshot.encode()).hexdigest()
	existing = frappe.db.get_value(ARCHIVE, {"archive_hash": archive_hash}, "name")
	if existing:
		return existing
	doc = frappe.get_doc(
		{
			"doctype": ARCHIVE,
			"conversation": conversation_id,
			"channel": detail["conversation"].get("channel"),
			"customer": detail["conversation"].get("customer"),
			"archive_hash": archive_hash,
			"retention_until": (get_datetime(today()) + timedelta(days=365 * 7)).date(),
			"snapshot_json": snapshot,
			"archived_by": frappe.session.user,
		}
	)
	doc.insert(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def search_archive(filters=None):
	filters = _loads(filters, {}) if isinstance(filters, str) else (filters or {})
	query_filters = {}
	for key in ("conversation", "channel", "customer"):
		if filters.get(key):
			query_filters[key] = filters[key]
	return frappe.get_all(ARCHIVE, filters=query_filters, fields=["name", "conversation", "channel", "customer", "archive_hash", "retention_until", "creation"], order_by="creation desc")


@frappe.whitelist()
def export_archive(filters=None):
	rows = search_archive(filters)
	return {"status": "Exported", "format": "json", "rows": rows}


@frappe.whitelist()
def search_users(query: str = "") -> list[dict]:
	"""Search Frappe users for in-app chat."""
	filters = {"enabled": 1}
	if query:
		filters["full_name"] = ["like", f"%{query}%"]
	users = frappe.get_all("User", filters=filters, fields=["name", "full_name", "user_image", "email"], limit_page_length=20)
	return users


@frappe.whitelist()
def start_inapp_chat(user_email: str, subject: str | None = None) -> dict:
	"""Create or get an in-app conversation between current user and another user."""
	current = frappe.session.user
	if current == "Guest":
		frappe.throw(_("Authentication required"))
	if user_email == current:
		frappe.throw(_("Cannot start a chat with yourself"))
	# Check if a conversation already exists
	existing = frappe.db.get_all(
		CONVERSATION,
		filters={
			"channel": "In-App",
			"reference_doctype": "User",
			"reference_name": user_email,
			"assigned_to": current,
			"status": ["!=", "Archived"],
		},
		limit=1,
	)
	if existing:
		return {"conversation_id": existing[0].name, "created": False}
	other = frappe.db.get_value("User", user_email, "full_name")
	conv = frappe.get_doc({
		"doctype": CONVERSATION,
		"subject": subject or f"Chat with {other or user_email}",
		"channel": "In-App",
		"status": "Open",
		"reference_doctype": "User",
		"reference_name": user_email,
		"assigned_to": current,
	})
	conv.insert(ignore_permissions=True)
	# Add a system message
	frappe.get_doc({
		"doctype": "CRM Omnichannel Message",
		"conversation": conv.name,
		"channel": "In-App",
		"direction": "Internal",
		"message_type": "System",
		"status": "Sent",
		"content": _("Chat started by {0} with {1}").format(
			frappe.db.get_value("User", current, "full_name") or current,
			other or user_email,
		),
		"from_party": current,
	}).insert(ignore_permissions=True)
	return {"conversation_id": conv.name, "created": True}


@frappe.whitelist()
def search_customers(query: str = "") -> list[dict]:
	"""Search Customers for external Omnichannel conversations."""
	fields = ["name", "customer_name"]
	meta = frappe.get_meta("Customer")
	for fieldname in ("mobile_no", "email_id"):
		if meta.has_field(fieldname):
			fields.append(fieldname)
	
	if query:
		or_filters = {
			"customer_name": ["like", f"%{query}%"],
		}
		if "email_id" in fields:
			or_filters["email_id"] = ["like", f"%{query}%"]
		if "mobile_no" in fields:
			or_filters["mobile_no"] = ["like", f"%{query}%"]
		customers = frappe.get_all("Customer", filters=or_filters, fields=fields, limit_page_length=20)
	else:
		customers = frappe.get_all("Customer", fields=fields, limit_page_length=20)
	return customers


@frappe.whitelist()
def ensure_demo_whatsapp_customer(recipient: str) -> dict:
	"""Create or reuse a demo Customer for the allowlisted WhatsApp test numbers."""
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required"))

	normalized = _normalize_demo_phone(recipient)
	customer_name = DEMO_WHATSAPP_RECIPIENTS.get(normalized)
	if not customer_name:
		frappe.throw(_("This WhatsApp demo recipient is not allowlisted"))

	meta = frappe.get_meta("Customer")
	fields = ["name", "customer_name"]
	if meta.has_field("mobile_no"):
		fields.append("mobile_no")
	customer = None
	if meta.has_field("mobile_no"):
		customer = frappe.db.get_value("Customer", {"mobile_no": ["in", [normalized, f"+{normalized}"]]}, fields, as_dict=True)
	if not customer:
		customer = frappe.db.get_value("Customer", {"customer_name": customer_name}, fields, as_dict=True)

	if customer:
		if meta.has_field("mobile_no") and customer.get("mobile_no") != normalized:
			frappe.db.set_value("Customer", customer.name, "mobile_no", normalized, update_modified=False)
			customer.mobile_no = normalized
		return customer

	doc = frappe.new_doc("Customer")
	doc.customer_name = customer_name
	if meta.has_field("customer_type"):
		doc.customer_type = "Individual"
	if meta.has_field("customer_group"):
		doc.customer_group = _default_customer_group()
	if meta.has_field("territory"):
		doc.territory = _default_territory()
	if meta.has_field("mobile_no"):
		doc.mobile_no = normalized
	doc.insert(ignore_permissions=True)
	return {fieldname: doc.get(fieldname) for fieldname in fields}


@frappe.whitelist()
def ensure_custom_customer(customer_name: str, mobile_no: str) -> dict:
	if frappe.session.user == "Guest":
		frappe.throw(_("Authentication required"))

	if not customer_name:
		customer_name = f"WA Customer - {mobile_no}"

	# Clean and normalize phone number
	digits = "".join(ch for ch in mobile_no if ch.isdigit())
	if digits.startswith("0"):
		digits = f"62{digits[1:]}"

	# Check if customer already exists with this mobile number
	meta = frappe.get_meta("Customer")
	fields = ["name", "customer_name"]
	if meta.has_field("mobile_no"):
		fields.append("mobile_no")
		existing = frappe.db.get_value("Customer", {"mobile_no": ["in", [digits, f"+{digits}"]]}, fields, as_dict=True)
		if existing:
			return existing

	existing_by_name = frappe.db.get_value("Customer", {"customer_name": customer_name}, fields, as_dict=True)
	if existing_by_name:
		if meta.has_field("mobile_no"):
			frappe.db.set_value("Customer", existing_by_name.name, "mobile_no", digits, update_modified=False)
			existing_by_name.mobile_no = digits
		return existing_by_name

	# Create a new Customer
	doc = frappe.new_doc("Customer")
	doc.customer_name = customer_name
	if meta.has_field("customer_type"):
		doc.customer_type = "Individual"
	if meta.has_field("customer_group"):
		doc.customer_group = _default_customer_group()
	if meta.has_field("territory"):
		doc.territory = _default_territory()
	if meta.has_field("mobile_no"):
		doc.mobile_no = digits
	doc.insert(ignore_permissions=True)
	return {fieldname: doc.get(fieldname) for fieldname in fields}


@frappe.whitelist(allow_guest=True)
def is_valid_whatsapp_sender(sender: str) -> bool:
	# Authentication check if X-Webhook-Token is set
	if frappe.session.user == "Guest":
		token = (frappe.get_request_header("X-Webhook-Token") or "").strip()
		expected_token = (frappe.conf.get("whatsapp_api_token") or "").strip()
		if expected_token and token != expected_token:
			frappe.throw(_("Unauthorized access"), frappe.PermissionError)

	if not sender:
		return False

	digits = "".join(ch for ch in sender if ch.isdigit())
	if digits.startswith("0"):
		digits = f"62{digits[1:]}"

	# Check if customer exists with this mobile number
	if frappe.db.exists("Customer", {"mobile_no": ["in", [digits, f"+{digits}"]]}):
		return True

	# Check if lead exists with this mobile number
	if frappe.db.exists("CRM Lead", {"mobile_no": ["in", [digits, f"+{digits}"]]}):
		return True

	# Check if conversation exists with this phone number as provider_conversation_id
	if frappe.db.exists("CRM Omnichannel Conversation", {"provider_conversation_id": digits}):
		return True

	return False


@frappe.whitelist()
def start_external_conversation(
	channel: str,
	customer: str,
	recipient: str,
	subject: str | None = None,
	content: str | None = None,
) -> dict:
	"""Create a new external conversation and send the first message."""
	current = frappe.session.user
	if current == "Guest":
		frappe.throw(_("Authentication required"))

	channel = _normalize_channel(channel)
	if channel not in ["WhatsApp", "Email", "SMS", "Voice"]:
		frappe.throw(_("Invalid external channel {0}").format(channel))

	if not customer or not frappe.db.exists("Customer", customer):
		frappe.throw(_("Customer not found"))

	if not recipient:
		frappe.throw(_("Recipient address/number is required"))

	# Create conversation
	conv = _ensure_conversation(
		channel=channel,
		subject=subject or f"{channel} Conversation - {customer}",
		customer=customer,
		reference_doctype="Customer",
		reference_name=customer,
	)

	# If there is initial content, send it!
	message_id = None
	if content:
		res = send_message(
			conversation_id=conv.name,
			content=content,
			recipient=recipient,
		)
		message_id = res.get("message")

	return {"conversation_id": conv.name, "message_id": message_id, "created": True}


def sync_whatsapp_message(doc, method: str | None = None):
	if not _ready():
		return
	reference_doctype = getattr(doc, "reference_doctype", None)
	reference_name = getattr(doc, "reference_name", None)
	upsert_inbound_message(
		channel="WhatsApp",
		content=getattr(doc, "message", None),
		provider_message_id=getattr(doc, "message_id", None) or doc.name,
		sender=getattr(doc, "from", None),
		recipient=getattr(doc, "to", None),
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		status="Received" if getattr(doc, "type", None) == "Incoming" else getattr(doc, "status", None),
		message_type=getattr(doc, "message_type", None) or "Text",
		attachment=getattr(doc, "attach", None),
		payload=doc.as_dict(),
	)


@frappe.whitelist()
def create_or_get_conversation(
	reference_doctype: str,
	reference_name: str,
	subject: str | None = None,
) -> dict:
	"""Find or create an In-App conversation for a doctype record."""
	if not _ready():
		frappe.throw(_("Omnichannel workspace is not migrated yet"))
	existing = frappe.db.get_all(
		CONVERSATION,
		filters={
			"channel": "In-App",
			"reference_doctype": reference_doctype,
			"reference_name": reference_name,
			"status": ["!=", "Archived"],
		},
		limit=1,
	)
	if existing:
		return get_conversation(existing[0].name)
	title_field = frappe.get_meta(reference_doctype).title_field or "name"
	display = frappe.db.get_value(reference_doctype, reference_name, title_field) or reference_name
	conv = frappe.get_doc({
		"doctype": CONVERSATION,
		"subject": subject or f"In-App Chat - {display}",
		"channel": "In-App",
		"status": "Open",
		"reference_doctype": reference_doctype,
		"reference_name": reference_name,
		"assigned_to": frappe.session.user,
	})
	conv.insert(ignore_permissions=True)
	return get_conversation(conv.name)


def sync_communication(doc, method: str | None = None):
	if not _ready() or getattr(doc, "doctype", None) != "Communication":
		return
	reference_doctype = getattr(doc, "reference_doctype", None)
	reference_name = getattr(doc, "reference_name", None)
	direction = _normalize_direction(getattr(doc, "sent_or_received", None))
	customer = _get_customer_from_reference(reference_doctype, reference_name)
	conversation = _ensure_conversation(
		channel="Email",
		subject=getattr(doc, "subject", None) or "Email",
		customer=customer,
		reference_doctype=reference_doctype,
		reference_name=reference_name,
		sender=getattr(doc, "sender", None),
		provider_conversation_id=getattr(doc, "email_account", None) or reference_name,
		payload=doc.as_dict(),
	)
	_create_message(
		conversation,
		{
			"channel": "Email",
			"direction": direction,
			"status": "Received" if direction == "Inbound" else "Sent",
			"content": getattr(doc, "content", None),
			"from_party": getattr(doc, "sender", None),
			"to_party": getattr(doc, "recipients", None),
			"provider_message_id": getattr(doc, "message_id", None) or doc.name,
			"source_doctype": "Communication",
			"source_name": doc.name,
			"payload": doc.as_dict(),
		},
	)


def sync_customer_communication(doc, method: str | None = None):
	if not _ready():
		return
	channel = _normalize_channel(getattr(doc, "channel", None))
	conversation = _ensure_conversation(
		channel=channel,
		subject=getattr(doc, "subject", None),
		customer=getattr(doc, "customer", None),
		provider_conversation_id=getattr(doc, "conversation_link", None) or doc.name,
		payload=doc.as_dict(),
	)
	_create_message(
		conversation,
		{
			"channel": channel,
			"direction": getattr(doc, "direction", None),
			"status": getattr(doc, "compose_status", None) or getattr(doc, "status", None),
			"content": getattr(doc, "message", None),
			"provider_message_id": doc.name,
			"source_doctype": "CRM Customer Communication",
			"source_name": doc.name,
			"payload": doc.as_dict(),
		},
	)


@frappe.whitelist()
def send_lead_email(lead: str, recipients: str, subject: str, content: str, attachments=None):
	"""Send email from a lead context using configured SMTP immediately."""
	if not recipients:
		frappe.throw(_("Recipient email is required"))
	try:
		frappe.sendmail(
			recipients=recipients,
			subject=subject,
			content=content or "",
			reference_doctype="CRM Lead",
			reference_name=lead,
			now=True,
		)
	except Exception:
		frappe.log_error(frappe.get_traceback(), "Lead email send failed")
		frappe.throw(_("Failed to send email. Check SMTP configuration."))
	comm = frappe.get_doc({
		"doctype": "Communication",
		"communication_type": "Communication",
		"sent_or_received": "Sent",
		"subject": subject,
		"content": content or "",
		"recipients": recipients,
		"reference_doctype": "CRM Lead",
		"reference_name": lead,
	})
	comm.insert(ignore_permissions=True)
	return {"status": "Sent", "communication": comm.name}


def sync_call_log(doc, method: str | None = None):
	if not _ready():
		return
	conversation = _ensure_conversation(
		channel="Voice",
		subject=f"Call - {getattr(doc, 'from', '')} to {getattr(doc, 'to', '')}",
		reference_doctype=getattr(doc, "reference_doctype", None),
		reference_name=getattr(doc, "reference_docname", None),
		sender=getattr(doc, "from", None),
		payload=doc.as_dict(),
	)
	_create_message(
		conversation,
		{
			"channel": "Voice",
			"direction": "Inbound" if getattr(doc, "type", None) == "Incoming" else "Outbound",
			"message_type": "Call",
			"status": getattr(doc, "status", None) or "Queued",
			"content": getattr(doc, "recording_url", None) or getattr(doc, "status", None),
			"from_party": getattr(doc, "from", None),
			"to_party": getattr(doc, "to", None),
			"provider_message_id": getattr(doc, "id", None) or doc.name,
			"source_doctype": "CRM Call Log",
			"source_name": doc.name,
			"payload": doc.as_dict(),
		},
	)
