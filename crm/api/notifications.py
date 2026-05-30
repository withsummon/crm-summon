import json

import frappe
from frappe.query_builder import Order
from frappe.utils import getdate, today


@frappe.whitelist()
def get_notifications():
	Notification = frappe.qb.DocType("CRM Notification")
	query = (
		frappe.qb.from_(Notification)
		.select("*")
		.where(Notification.to_user == frappe.session.user)
		.where(Notification.archived == 0)
		.orderby("creation", order=Order.desc)
	)
	notifications = query.run(as_dict=True)

	_notifications = []
	for notification in notifications:
		_notifications.append(
			{
				"name": notification.name,
				"creation": notification.creation,
				"from_user": {
					"name": notification.from_user,
					"full_name": frappe.get_value("User", notification.from_user, "full_name"),
				},
				"type": notification.type,
				"to_user": notification.to_user,
				"read": notification.read,
				"hash": get_hash(notification),
				"notification_text": notification.notification_text,
				"message": notification.message,
				"notification_type_doctype": notification.notification_type_doctype,
				"notification_type_doc": notification.notification_type_doc,
				"comment": notification.comment,
				"reference_doctype": notification.reference_doctype,
				"reference_name": notification.reference_name,
				"route_name": get_route_name(notification),
				"channel": notification.channel,
				"level": notification.level,
				"delivery_status": notification.delivery_status,
			}
		)

	return _notifications


@frappe.whitelist()
def delete_notification(name):
	if not name or not frappe.db.exists("CRM Notification", name):
		frappe.throw("Notification not found")
	notification = frappe.get_doc("CRM Notification", name)
	write_audit(notification.name, "purged")
	frappe.db.set_value("CRM Notification", name, {"archived": 1})
	frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def archive_all_notifications():
	user = frappe.session.user
	names = frappe.get_all("CRM Notification", filters={"to_user": user, "archived": 0}, pluck="name")
	for name in names:
		write_audit(name, "archived")
	frappe.db.sql(
		"""UPDATE `tabCRM Notification`
		SET `read` = 1, `archived` = 1
		WHERE `to_user` = %s""",
		(user,),
	)
	frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def seed_notification_sample_data():
	user = frappe.session.user
	samples = [
		("Mention", f"<b>{user}</b> mentioned you in a comment"),
		("Task", "A new task <b>Follow-up call</b> has been assigned to you"),
		("Assignment", "<b>Lead-001</b> has been assigned to you"),
		("WhatsApp", "You have a new WhatsApp message from <b>+628123456789</b>"),
		("Mention", "You were mentioned in deal <b>DEAL-002</b>"),
		("Task", "Task <b>Prepare proposal</b> is due tomorrow"),
		("Assignment", "<b>Deal-003</b> has been assigned to you"),
		("WhatsApp", "New WhatsApp template received"),
		("Mention", "Comment reply on <b>Lead-004</b>"),
		("Task", "Task <b>Send reminder</b> updated"),
	]
	created = 0
	for notif_type, message in samples:
		doc = frappe.get_doc({
			"doctype": "CRM Notification",
			"type": notif_type,
			"to_user": user,
			"from_user": "Administrator",
			"message": message,
			"read": 0,
			"archived": 0,
		})
		doc.insert(ignore_permissions=True)
		write_audit(doc.name, "created")
		created += 1
	return {"created": created}


@frappe.whitelist()
def mark_as_read(user: str | None = None, doc: str | None = None):
	user = user or frappe.session.user
	filters = {"to_user": user, "read": False}
	or_filters = []
	if doc:
		or_filters = [
			{"name": doc},
			{"comment": doc},
			{"notification_type_doc": doc},
		]
	names = [n.name for n in frappe.get_all("CRM Notification", filters=filters, or_filters=or_filters)]
	if names:
		for name in names:
			write_audit(name, "read")
		frappe.db.set_value("CRM Notification", {"name": ["in", names]}, "read", True)
		frappe.db.commit()
	return {"status": "ok"}


def get_hash(notification):
	_hash = ""
	if notification.type == "Mention" and notification.notification_type_doc:
		_hash = "#" + notification.notification_type_doc

	if notification.type == "WhatsApp":
		_hash = "#whatsapp"

	if notification.type == "Assignment" and notification.notification_type_doctype == "CRM Task":
		_hash = "#tasks"
		if "has been removed by" in notification.message:
			_hash = ""
	return _hash


def get_route_name(notification):
	routes = {
		"CRM Deal": "Deal",
		"CRM Lead": "Lead",
		"CRM Task": "Tasks",
	}
	return routes.get(notification.reference_doctype or notification.notification_type_doctype)


@frappe.whitelist()
def save_preferences(preferences, digest=None):
	if isinstance(preferences, str):
		preferences = json.loads(preferences)
	if isinstance(digest, str):
		digest = json.loads(digest)
	user = frappe.session.user
	for pref in preferences:
		name = frappe.db.get_value("CRM Notification Preference", {"user": user, "type": pref.get("type")}, "name")
		data = {
			"email": 1 if pref.get("email") else 0,
			"in_app": 1 if pref.get("in_app") else 0,
			"sms": 1 if pref.get("sms") else 0,
			"push": 1 if pref.get("push") else 0,
			"sound_enabled": 1 if pref.get("sound_enabled") else 0,
		}
		if name:
			frappe.db.set_value("CRM Notification Preference", name, data)
		else:
			doc_data = {"doctype": "CRM Notification Preference", "user": user, "type": pref.get("type")}
			doc_data.update(data)
			frappe.get_doc(doc_data).insert(ignore_permissions=True)
	if digest:
		frappe.db.set_value("CRM Notification Preference", {"user": user}, {
			"digest_mode": digest.get("mode", "off"),
			"digest_time": digest.get("time", ""),
			"quiet_hours_start": digest.get("quiet_start", ""),
			"quiet_hours_end": digest.get("quiet_end", ""),
			"timezone": digest.get("timezone", "Asia/Jakarta"),
			"critical_bypass": 1 if digest.get("critical_bypass") else 0,
		})
	frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def get_preferences():
	user = frappe.session.user
	rows = frappe.get_all("CRM Notification Preference", filters={"user": user}, fields=[
		"type", "email", "in_app", "sms", "push", "sound_enabled",
		"digest_mode", "digest_time", "quiet_hours_start", "quiet_hours_end",
		"timezone", "critical_bypass", "last_digest_at",
	])
	result = {"preferences": {r["type"]: r for r in rows}}
	if rows:
		first = rows[0]
		result["digest"] = {
			"mode": first.get("digest_mode", "off"),
			"time": first.get("digest_time", ""),
			"quiet_start": first.get("quiet_hours_start", ""),
			"quiet_end": first.get("quiet_hours_end", ""),
			"timezone": first.get("timezone", "Asia/Jakarta"),
			"critical_bypass": first.get("critical_bypass", 1),
		}
	return result


# ---------------------------------------------------------------------------
# Push notifications
# ---------------------------------------------------------------------------

@frappe.whitelist()
def register_push_device(token, platform="Web", label=None, endpoint=None, p256dh=None, auth=None):
	user = frappe.session.user
	existing = frappe.db.get_value("CRM Notification Device", {"user": user, "token": token}, "name")
	if existing:
		frappe.db.set_value("CRM Notification Device", existing, {
			"platform": platform,
			"label": label,
			"endpoint": endpoint,
			"p256dh": p256dh,
			"auth": auth,
			"last_used_at": frappe.utils.now(),
			"active": 1,
		})
	else:
		frappe.get_doc({
			"doctype": "CRM Notification Device",
			"user": user,
			"token": token,
			"platform": platform,
			"label": label,
			"endpoint": endpoint,
			"p256dh": p256dh,
			"auth": auth,
			"last_used_at": frappe.utils.now(),
			"active": 1,
		}).insert(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def unregister_push_device(token):
	user = frappe.session.user
	name = frappe.db.get_value("CRM Notification Device", {"user": user, "token": token}, "name")
	if name:
		frappe.db.set_value("CRM Notification Device", name, {"active": 0})
		frappe.db.commit()
	return {"status": "ok"}


@frappe.whitelist()
def list_push_devices():
	user = frappe.session.user
	devices = frappe.get_all("CRM Notification Device", filters={"user": user}, fields=[
		"name", "token", "platform", "label", "last_used_at", "active"
	])
	return devices


@frappe.whitelist()
def send_test_push(token):
	user = frappe.session.user
	device = frappe.db.get_value("CRM Notification Device", {"user": user, "token": token}, "name")
	if not device:
		frappe.throw("Device not found")
	return {"status": "ok", "message": "Push notification dispatched (stub)"}


# ---------------------------------------------------------------------------
# Digest
# ---------------------------------------------------------------------------

@frappe.whitelist()
def preview_digest():
	user = frappe.session.user
	pref = frappe.get_all("CRM Notification Preference", filters={"user": user}, fields=["digest_mode", "last_digest_at"], limit=1)
	if not pref or pref[0].digest_mode == "off":
		return {"body": "", "count": 0}
	last_digest = pref[0].last_digest_at
	filters = {"to_user": user, "archived": 0, "read": 0, "level": ["!=", "critical"]}
	if last_digest:
		filters["creation"] = [">", last_digest]
	items = frappe.get_all("CRM Notification", filters=filters, fields=["name", "type", "message"], limit=20)
	if len(items) < 2:
		return {"body": "", "count": len(items)}
	body = f"You have {len(items)} notifications: " + ", ".join([i.type for i in items[:3]]) + ("..." if len(items) > 3 else "")
	return {"body": body, "count": len(items)}


def run_digests():
	users = frappe.get_all("CRM Notification Preference", filters={"digest_mode": ["!=", "off"]}, fields=["user", "digest_mode", "digest_time", "quiet_hours_start", "quiet_hours_end", "timezone", "critical_bypass", "last_digest_at"])
	for pref in users:
		user = pref.user
		last_digest = pref.last_digest_at
		filters = {"to_user": user, "archived": 0, "read": 0, "level": ["!=", "critical"]}
		if last_digest:
			filters["creation"] = [">", last_digest]
		items = frappe.get_all("CRM Notification", filters=filters, fields=["name", "type", "message"], limit=100)
		if len(items) < 2:
			continue
		body = f"Digest: {len(items)} notifications — " + ", ".join([i.type for i in items[:3]]) + ("..." if len(items) > 3 else "")
		parent = frappe.get_doc({
			"doctype": "CRM Notification",
			"type": "Digest",
			"to_user": user,
			"from_user": "Administrator",
			"message": body,
			"read": 0,
			"archived": 0,
			"level": "info",
			"channel": "In-app",
		})
		parent.insert(ignore_permissions=True)
		for item in items:
			frappe.db.set_value("CRM Notification", item.name, {"digest_id": parent.name, "delivery_status": "Delivered"})
		frappe.db.set_value("CRM Notification Preference", {"user": user}, "last_digest_at", frappe.utils.now())
		write_audit(parent.name, "created")
	frappe.db.commit()


# ---------------------------------------------------------------------------
# Audit
# ---------------------------------------------------------------------------

def write_audit(notification, action, channel=None, recipient=None, payload=None):
	frappe.get_doc({
		"doctype": "CRM Notification Audit",
		"timestamp": frappe.utils.now(),
		"actor": frappe.session.user or "Administrator",
		"action": action,
		"notification": notification,
		"channel": channel,
		"recipient": recipient,
		"ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None,
		"payload_json": json.dumps(payload) if payload else None,
	}).insert(ignore_permissions=True)


@frappe.whitelist()
def get_audit_log(filters=None, limit=50, offset=0):
	if isinstance(filters, str):
		filters = json.loads(filters)
	filters = filters or {}
	user = frappe.session.user
	is_admin = "System Manager" in frappe.get_roles(user)
	q_filters = {}
	if not is_admin:
		q_filters["actor"] = user
	if filters.get("action"):
		q_filters["action"] = ["in", filters["action"]] if isinstance(filters["action"], list) else filters["action"]
	if filters.get("channel"):
		q_filters["channel"] = ["in", filters["channel"]] if isinstance(filters["channel"], list) else filters["channel"]
	if filters.get("actor"):
		q_filters["actor"] = filters["actor"]
	if filters.get("notification"):
		q_filters["notification"] = filters["notification"]
	if filters.get("date_from"):
		q_filters["timestamp"] = [">=", filters["date_from"]]
	if filters.get("date_to"):
		q_filters.setdefault("timestamp", []).append(["<=", filters["date_to"]])
	rows = frappe.get_all("CRM Notification Audit", filters=q_filters, fields=[
		"name", "timestamp", "actor", "action", "notification", "channel", "recipient", "ip_address", "payload_json"
	], limit_page_length=limit, limit_start=offset, order_by="timestamp desc")
	return {"rows": rows, "total": frappe.db.count("CRM Notification Audit", filters=q_filters)}


@frappe.whitelist()
def export_audit_csv(filters=None):
	if isinstance(filters, str):
		filters = json.loads(filters)
	result = get_audit_log(filters, limit=9999, offset=0)
	rows = result["rows"]
	data = [["Timestamp", "Actor", "Action", "Notification", "Channel", "Recipient", "IP Address", "Payload"]]
	for r in rows:
		data.append([
			r["timestamp"], r["actor"], r["action"], r["notification"],
			r["channel"], r["recipient"], r["ip_address"], r["payload_json"]
		])
	csv = "\n".join([",".join([str(c) if c else "" for c in row]) for row in data])
	frappe.local.response.filename = "notification_audit.csv"
	frappe.local.response.filecontent = csv
	frappe.local.response.type = "csv"


@frappe.whitelist()
def purge_audit_log(before_date):
	if "System Manager" not in frappe.get_roles():
		frappe.throw("Only System Manager can purge audit logs")
	count = frappe.db.delete("CRM Notification Audit", {"timestamp": ["<", before_date]})
	frappe.db.commit()
	return {"purged": count}


def enforce_audit_retention():
	retention = frappe.db.get_single_value("CRM Settings", "notification_audit_retention_days") or 2555
	cutoff = frappe.utils.add_days(today(), -retention)
	frappe.db.delete("CRM Notification Audit", {"timestamp": ["<", cutoff]})
	frappe.db.commit()
