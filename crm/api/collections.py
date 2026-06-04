import json
import re
import uuid

import frappe
from frappe import _
from frappe.utils import flt, now_datetime, nowdate


COLLECTION_TABLES = {
	"CRM Collection Account": """
		CREATE TABLE IF NOT EXISTS `tabCRM Collection Account` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			customer VARCHAR(255) NOT NULL,
			product VARCHAR(255),
			outstanding DECIMAL(21,6),
			dpd INT,
			ai_score DECIMAL(10,4),
			ptp_date DATE,
			last_action DATE,
			officer VARCHAR(255),
			status VARCHAR(80),
			bucket VARCHAR(80),
			notes LONGTEXT,
			UNIQUE KEY uniq_customer (customer),
			INDEX idx_status (status),
			INDEX idx_dpd (dpd),
			INDEX idx_officer (officer)
		)
	""",
	"CRM Collection PTP": """
		CREATE TABLE IF NOT EXISTS `tabCRM Collection PTP` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			account VARCHAR(255),
			customer VARCHAR(255) NOT NULL,
			amount DECIMAL(21,6),
			ptp_date DATE,
			channel VARCHAR(80),
			officer VARCHAR(255),
			status VARCHAR(80),
			notes TEXT,
			INDEX idx_account (account),
			INDEX idx_customer (customer),
			INDEX idx_status (status),
			INDEX idx_ptp_date (ptp_date)
		)
	""",
	"CRM Collection Payment": """
		CREATE TABLE IF NOT EXISTS `tabCRM Collection Payment` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			account VARCHAR(255),
			customer VARCHAR(255) NOT NULL,
			amount DECIMAL(21,6),
			payment_date DATE,
			mode VARCHAR(80),
			principal DECIMAL(21,6),
			interest DECIMAL(21,6),
			charges DECIMAL(21,6),
			receipt_no VARCHAR(80),
			notes TEXT,
			INDEX idx_account (account),
			INDEX idx_customer (customer),
			INDEX idx_payment_date (payment_date)
		)
	""",
	"CRM Collection Legal": """
		CREATE TABLE IF NOT EXISTS `tabCRM Collection Legal` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			account VARCHAR(255),
			customer VARCHAR(255) NOT NULL,
			trigger_condition VARCHAR(255),
			legal_officer VARCHAR(255),
			letter_type VARCHAR(255),
			escalated_date DATE,
			status VARCHAR(80),
			notice_no VARCHAR(80),
			notes TEXT,
			INDEX idx_account (account),
			INDEX idx_customer (customer),
			INDEX idx_status (status)
		)
	""",
	"CRM Collection Action": """
		CREATE TABLE IF NOT EXISTS `tabCRM Collection Action` (
			name VARCHAR(255) PRIMARY KEY,
			creation DATETIME,
			modified DATETIME,
			account VARCHAR(255),
			customer VARCHAR(255) NOT NULL,
			action_type VARCHAR(80),
			action_date DATE,
			outcome VARCHAR(255),
			notes TEXT,
			metadata_json LONGTEXT,
			owner VARCHAR(255),
			INDEX idx_account (account),
			INDEX idx_customer (customer),
			INDEX idx_action_date (action_date),
			INDEX idx_action_type (action_type)
		)
	""",
}


SAMPLE_ACCOUNTS = [
	{"name": "a1", "customer": "PT Nusantara Jaya", "product": "Working Capital Loan", "outstanding": 8_200_000_000, "dpd": 47, "ai_score": 78, "ptp_date": "2026-05-28", "last_action": "2026-05-22", "officer": "Rina Susilawati", "status": "PTP"},
	{"name": "a2", "customer": "Sari Logistics", "product": "Revolving Credit", "outstanding": 5_100_000_000, "dpd": 62, "ai_score": 42, "ptp_date": "2026-05-15", "last_action": "2026-05-20", "officer": "Bagas Nugroho", "status": "Active"},
	{"name": "a3", "customer": "CV Arjuna Perkasa", "product": "Invoice Financing", "outstanding": 3_400_000_000, "dpd": 33, "ai_score": 65, "ptp_date": "2026-05-30", "last_action": "2026-05-23", "officer": "Desi Fitriani", "status": "PTP"},
	{"name": "a4", "customer": "Mega Teknik Group", "product": "Term Loan", "outstanding": 2_800_000_000, "dpd": 29, "ai_score": 81, "ptp_date": None, "last_action": "2026-05-24", "officer": "Yusuf Pratama", "status": "Active"},
	{"name": "a5", "customer": "Berkah Abadi", "product": "KPR Korporat", "outstanding": 1_900_000_000, "dpd": 91, "ai_score": 18, "ptp_date": None, "last_action": "2026-05-10", "officer": "Eka Wulandari", "status": "Legal"},
	{"name": "a6", "customer": "PT Global Makmur", "product": "Working Capital Loan", "outstanding": 12_400_000_000, "dpd": 95, "ai_score": 12, "ptp_date": None, "last_action": "2026-05-05", "officer": "Rina Susilawati", "status": "Legal"},
	{"name": "a7", "customer": "Maju Sejahtera", "product": "Term Loan", "outstanding": 1_200_000_000, "dpd": 18, "ai_score": 87, "ptp_date": "2026-05-25", "last_action": "2026-05-23", "officer": "Bagas Nugroho", "status": "PTP"},
]


SAMPLE_PTPS = [
	{"name": "ptp1", "customer": "PT Nusantara Jaya", "amount": 500_000_000, "ptp_date": "2026-05-28", "channel": "Phone Call", "officer": "Rina Susilawati", "status": "Pending", "notes": "Dijanjikan transfer sebelum jam 15.00"},
	{"name": "ptp2", "customer": "CV Arjuna Perkasa", "amount": 200_000_000, "ptp_date": "2026-05-30", "channel": "WhatsApp", "officer": "Desi Fitriani", "status": "Pending", "notes": ""},
	{"name": "ptp3", "customer": "Maju Sejahtera", "amount": 120_000_000, "ptp_date": "2026-05-25", "channel": "Visit", "officer": "Bagas Nugroho", "status": "Kept", "notes": "Sudah transfer pukul 10.30"},
	{"name": "ptp4", "customer": "Sari Logistics", "amount": 350_000_000, "ptp_date": "2026-05-15", "channel": "Email", "officer": "Bagas Nugroho", "status": "Broken", "notes": "Tidak ada transfer sesuai janji"},
	{"name": "ptp5", "customer": "Mega Teknik Group", "amount": 800_000_000, "ptp_date": "2026-05-26", "channel": "Phone Call", "officer": "Yusuf Pratama", "status": "Pending", "notes": "Konfirmasi via telepon pukul 11.00"},
]


SAMPLE_ACTIONS = [
	{"name": "n1", "customer": "PT Nusantara Jaya", "action_type": "PTP", "action_date": "2026-05-22", "outcome": "Contacted - Promised", "notes": "Customer contacted, promised to pay by end of May."},
	{"name": "n2", "customer": "Sari Logistics", "action_type": "Note", "action_date": "2026-05-20", "outcome": "No Answer", "notes": "No answer. Left voicemail."},
	{"name": "n3", "customer": "Berkah Abadi", "action_type": "Legal", "action_date": "2026-05-10", "outcome": "Legal Notice Sent", "notes": "SP2 sudah dikirim. Tidak ada respon."},
]


def ensure_collection_tables():
	for table, statement in COLLECTION_TABLES.items():
		if frappe.db.table_exists(table):
			continue
		try:
			frappe.db.sql_ddl(statement)
		except Exception:
			frappe.log_error(frappe.get_traceback(), f"Collections - create table {table}")


def _insert(table, values):
	ensure_collection_tables()
	now = now_datetime()
	payload = {"name": values.get("name") or str(uuid.uuid4()), "creation": now, "modified": now, **values}
	columns = list(payload.keys())
	frappe.db.sql(
		f"INSERT INTO `tab{table}` ({', '.join('`' + col + '`' for col in columns)}) "
		f"VALUES ({', '.join(['%s'] * len(columns))})",
		[payload[col] for col in columns],
	)
	return payload["name"]


def _update(table, name, values):
	if not values:
		return
	values = {"modified": now_datetime(), **values}
	assignments = ", ".join(f"`{key}`=%s" for key in values)
	frappe.db.sql(
		f"UPDATE `tab{table}` SET {assignments} WHERE name=%s",
		list(values.values()) + [name],
	)


def _seed_collection_data():
	if frappe.db.count("CRM Collection Account"):
		return

	for account in SAMPLE_ACCOUNTS:
		_insert(
			"CRM Collection Account",
			{**account, "bucket": _bucket_for_dpd(account["dpd"]), "notes": ""},
		)

	for ptp in SAMPLE_PTPS:
		account = _account_by_customer(ptp["customer"])
		_insert("CRM Collection PTP", {**ptp, "account": account.name if account else None})

	for action in SAMPLE_ACTIONS:
		account = _account_by_customer(action["customer"])
		_insert("CRM Collection Action", {**action, "account": account.name if account else None, "owner": frappe.session.user})

	frappe.db.commit()


def _ensure_ready():
	ensure_collection_tables()
	_seed_collection_data()


def _bucket_for_dpd(dpd):
	dpd = int(dpd or 0)
	if dpd <= 0:
		return "Current (0d)"
	if dpd <= 30:
		return "DPD 1-30"
	if dpd <= 60:
		return "DPD 31-60"
	if dpd <= 90:
		return "DPD 61-90"
	if dpd <= 180:
		return "DPD 91-180"
	return "DPD 180+"


def _fmt_idr(value):
	value = flt(value)
	if value >= 1_000_000_000_000:
		return f"IDR {value / 1_000_000_000_000:.1f}T"
	if value >= 1_000_000_000:
		return f"IDR {value / 1_000_000_000:.1f}B"
	if value >= 1_000_000:
		return f"IDR {value / 1_000_000:.0f}M"
	return f"IDR {value:,.0f}"


def _parse_amount(value):
	if value is None:
		return 0
	if isinstance(value, (int, float)):
		return flt(value)
	text = str(value).strip().upper().replace("IDR", "").replace("RP", "").strip()
	multiplier = 1
	if text.endswith("T"):
		multiplier = 1_000_000_000_000
		text = text[:-1]
	elif text.endswith("B"):
		multiplier = 1_000_000_000
		text = text[:-1]
	elif text.endswith("M"):
		multiplier = 1_000_000
		text = text[:-1]
	text = re.sub(r"[^0-9.]", "", text)
	return flt(text) * multiplier if text else 0


def _account_by_customer(customer):
	rows = frappe.db.sql(
		"SELECT * FROM `tabCRM Collection Account` WHERE customer=%s LIMIT 1",
		(customer,),
		as_dict=True,
	)
	return rows[0] if rows else None


def _account_by_name_or_customer(account=None, customer=None):
	if account:
		rows = frappe.db.sql(
			"SELECT * FROM `tabCRM Collection Account` WHERE name=%s LIMIT 1",
			(account,),
			as_dict=True,
		)
		if rows:
			return rows[0]
	if customer:
		return _account_by_customer(customer)
	return None


def _collection_notes():
	rows = frappe.db.sql(
		"""
		SELECT name, account, customer, action_date, outcome, notes, action_type
		FROM `tabCRM Collection Action`
		ORDER BY action_date DESC, creation DESC
		""",
		as_dict=True,
	)
	notes = {}
	for row in rows:
		notes.setdefault(row.account, []).append({
			"id": row.name,
			"date": str(row.action_date or ""),
			"body": row.notes or "",
			"outcome": row.outcome or row.action_type or "",
		})
	return notes


def _serialize_account(row, notes_by_account=None):
	notes_by_account = notes_by_account or {}
	return {
		"id": row.name,
		"customer": row.customer,
		"product": row.product or "",
		"outstanding": _fmt_idr(row.outstanding or 0),
		"outstandingRaw": flt(row.outstanding or 0),
		"dpd": int(row.dpd or 0),
		"aiScore": int(row.ai_score or 0),
		"ptpDate": str(row.ptp_date or ""),
		"lastAction": str(row.last_action or ""),
		"officer": row.officer or "",
		"status": row.status or "Active",
		"bucket": row.bucket or _bucket_for_dpd(row.dpd),
		"notes": notes_by_account.get(row.name, []),
	}


def _serialize_ptp(row):
	return {
		"id": row.name,
		"account": row.account,
		"customer": row.customer,
		"amount": _fmt_idr(row.amount or 0),
		"amountRaw": flt(row.amount or 0),
		"date": str(row.ptp_date or ""),
		"channel": row.channel or "",
		"officer": row.officer or "",
		"status": row.status or "Pending",
		"notes": row.notes or "",
	}


def _add_action(account, action_type, outcome, notes="", metadata=None, action_date=None):
	_insert(
		"CRM Collection Action",
		{
			"account": account.name,
			"customer": account.customer,
			"action_type": action_type,
			"action_date": action_date or nowdate(),
			"outcome": outcome,
			"notes": notes or "",
			"metadata_json": json.dumps(metadata or {}, default=str),
			"owner": frappe.session.user,
		},
	)


def _sync_account_ptp_state(account_name):
	account = _account_by_name_or_customer(account=account_name)
	if not account:
		return
	pending = frappe.db.sql(
		"""
		SELECT ptp_date
		FROM `tabCRM Collection PTP`
		WHERE account=%s AND status='Pending'
		ORDER BY ptp_date ASC
		LIMIT 1
		""",
		(account_name,),
		as_dict=True,
	)
	values = {"ptp_date": pending[0].ptp_date if pending else None}
	if account.status not in ("Closed", "Legal"):
		values["status"] = "PTP" if pending else "Active"
	_update("CRM Collection Account", account_name, values)


@frappe.whitelist()
def get_collection_state():
	_ensure_ready()
	notes = _collection_notes()
	accounts = frappe.db.sql(
		"SELECT * FROM `tabCRM Collection Account` ORDER BY dpd DESC, outstanding DESC",
		as_dict=True,
	)
	ptps = frappe.db.sql(
		"SELECT * FROM `tabCRM Collection PTP` ORDER BY ptp_date DESC, creation DESC",
		as_dict=True,
	)
	return {
		"accounts": [_serialize_account(row, notes) for row in accounts],
		"ptps": [_serialize_ptp(row) for row in ptps],
	}


@frappe.whitelist()
def record_ptp(customer, amount=None, date=None, channel="Phone Call", notes="", account=None):
	_ensure_ready()
	if not customer:
		frappe.throw(_("Customer is required"))
	if not date:
		frappe.throw(_("PTP date is required"))

	account_row = _account_by_name_or_customer(account=account, customer=customer)
	if not account_row:
		frappe.throw(_("Collection account not found for {0}").format(customer))

	amount_value = _parse_amount(amount)
	_insert(
		"CRM Collection PTP",
		{
			"account": account_row.name,
			"customer": account_row.customer,
			"amount": amount_value,
			"ptp_date": date,
			"channel": channel,
			"officer": account_row.officer,
			"status": "Pending",
			"notes": notes or "",
		},
	)
	_update(
		"CRM Collection Account",
		account_row.name,
		{"ptp_date": date, "last_action": nowdate(), "status": "PTP"},
	)
	_add_action(
		account_row,
		"PTP",
		"PTP Recorded",
		notes or f"Promise to pay {_fmt_idr(amount_value)} on {date}.",
		{"amount": amount_value, "date": date, "channel": channel},
	)
	frappe.db.commit()
	return get_collection_state()


@frappe.whitelist()
def update_ptp(ptp, status):
	_ensure_ready()
	if status not in ("Pending", "Kept", "Broken"):
		frappe.throw(_("Invalid PTP status"))

	rows = frappe.db.sql("SELECT * FROM `tabCRM Collection PTP` WHERE name=%s LIMIT 1", (ptp,), as_dict=True)
	if not rows:
		frappe.throw(_("PTP record not found"))
	row = rows[0]
	_update("CRM Collection PTP", row.name, {"status": status})
	account = _account_by_name_or_customer(account=row.account, customer=row.customer)
	if account:
		_update("CRM Collection Account", account.name, {"last_action": nowdate()})
		_add_action(account, "PTP", f"PTP {status}", row.notes or f"PTP marked {status}.", {"ptp": row.name})
		_sync_account_ptp_state(account.name)
	frappe.db.commit()
	return get_collection_state()


@frappe.whitelist()
def record_payment(customer, amount, date=None, mode="Transfer Bank", principal=None, interest=None, charges=None, account=None):
	_ensure_ready()
	if not customer:
		frappe.throw(_("Customer is required"))
	if not amount:
		frappe.throw(_("Payment amount is required"))

	account_row = _account_by_name_or_customer(account=account, customer=customer)
	if not account_row:
		frappe.throw(_("Collection account not found for {0}").format(customer))

	payment_amount = _parse_amount(amount)
	payment_date = date or nowdate()
	receipt_no = f"COL-PAY-{now_datetime().strftime('%Y%m%d%H%M%S')}"
	_insert(
		"CRM Collection Payment",
		{
			"account": account_row.name,
			"customer": account_row.customer,
			"amount": payment_amount,
			"payment_date": payment_date,
			"mode": mode,
			"principal": _parse_amount(principal),
			"interest": _parse_amount(interest),
			"charges": _parse_amount(charges),
			"receipt_no": receipt_no,
			"notes": "",
		},
	)

	new_outstanding = max(flt(account_row.outstanding or 0) - payment_amount, 0)
	values = {"outstanding": new_outstanding, "last_action": payment_date}
	if new_outstanding <= 0:
		values.update({"status": "Closed", "dpd": 0, "ptp_date": None, "bucket": _bucket_for_dpd(0)})
	else:
		values["bucket"] = _bucket_for_dpd(account_row.dpd)
		if account_row.status != "Legal":
			values["status"] = "Active"

	_update("CRM Collection Account", account_row.name, values)
	pending = frappe.db.sql(
		"""
		SELECT name
		FROM `tabCRM Collection PTP`
		WHERE account=%s AND status='Pending'
		ORDER BY ptp_date ASC
		LIMIT 1
		""",
		(account_row.name,),
		as_dict=True,
	)
	if pending:
		_update("CRM Collection PTP", pending[0].name, {"status": "Kept"})

	_add_action(
		account_row,
		"Payment",
		"Payment Logged",
		f"Payment received via {mode}: {_fmt_idr(payment_amount)}. Receipt {receipt_no}.",
		{"amount": payment_amount, "receipt_no": receipt_no, "mode": mode},
		payment_date,
	)
	if new_outstanding > 0:
		_sync_account_ptp_state(account_row.name)
	frappe.db.commit()
	return get_collection_state()


@frappe.whitelist()
def escalate_legal(customer, trigger=None, officer=None, letter_type=None, notes="", account=None):
	_ensure_ready()
	if not customer:
		frappe.throw(_("Customer is required"))

	account_row = _account_by_name_or_customer(account=account, customer=customer)
	if not account_row:
		frappe.throw(_("Collection account not found for {0}").format(customer))

	notice_no = f"LEGAL-{now_datetime().strftime('%Y%m%d%H%M%S')}"
	_insert(
		"CRM Collection Legal",
		{
			"account": account_row.name,
			"customer": account_row.customer,
			"trigger_condition": trigger or "Manual escalation",
			"legal_officer": officer or "",
			"letter_type": letter_type or "",
			"escalated_date": nowdate(),
			"status": "Open",
			"notice_no": notice_no,
			"notes": notes or "",
		},
	)
	_update(
		"CRM Collection Account",
		account_row.name,
		{"status": "Legal", "last_action": nowdate(), "ptp_date": None},
	)
	_add_action(
		account_row,
		"Legal",
		"Legal Notice Sent",
		notes or f"{letter_type or 'Legal notice'} generated and assigned to {officer or 'Legal Officer'}.",
		{"trigger": trigger, "officer": officer, "letter_type": letter_type, "notice_no": notice_no},
	)
	frappe.db.commit()
	return get_collection_state()


@frappe.whitelist()
def add_collection_note(customer, outcome, notes, follow_up=None, account=None):
	_ensure_ready()
	if not customer:
		frappe.throw(_("Customer is required"))
	if not notes:
		frappe.throw(_("Notes are required"))

	account_row = _account_by_name_or_customer(account=account, customer=customer)
	if not account_row:
		frappe.throw(_("Collection account not found for {0}").format(customer))

	_update("CRM Collection Account", account_row.name, {"last_action": nowdate()})
	_add_action(
		account_row,
		"Note",
		outcome or "Collection Note",
		notes,
		{"follow_up": follow_up},
	)
	frappe.db.commit()
	return get_collection_state()
