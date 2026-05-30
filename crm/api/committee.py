import hashlib
import json
from collections import defaultdict

import frappe
from frappe import _
from frappe.utils import add_to_date, flt, getdate, now_datetime


def _compute_vote_hash(item, member, decision, signed_at):
    payload = f"{item}:{member}:{decision}:{signed_at}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _verify_vote_hash(vote_name):
    vote = frappe.get_doc("CRM Committee Vote", vote_name)
    expected = _compute_vote_hash(vote.item, vote.member, vote.decision, str(vote.signed_at))
    return vote.signature_hash == expected


# ---------- helpers ----------


def _doctype_ready(doctype):
	return frappe.db.table_exists(doctype)


def _allowed_app_status(desired, fallback_map=None):
	if not _doctype_ready("CRM Credit Application"):
		return desired
	field = frappe.get_meta("CRM Credit Application").get_field("status")
	if not field:
		return desired
	options = [o.strip() for o in (field.options or "").split("\n") if o.strip()]
	if not options or desired in options:
		return desired
	fb = (fallback_map or {}).get(desired)
	if fb and fb in options:
		return fb
	return options[0]


def _all_ready():
	for dt in (
		"CRM Committee",
		"CRM Committee Item",
		"CRM Committee Vote",
		"CRM Committee Decision",
		"CRM Committee Meeting",
		"CRM Committee Routing Rule",
	):
		if not _doctype_ready(dt):
			return False
	return True


def _user_committees(user=None):
	user = user or frappe.session.user
	if not _doctype_ready("CRM Committee"):
		return []
	rows = frappe.get_all(
		"CRM Committee Member",
		filters={"member": user, "parenttype": "CRM Committee"},
		fields=["parent", "role", "weight"],
	)
	out = []
	for r in rows:
		if not frappe.db.exists("CRM Committee", r.parent):
			continue
		committee = frappe.db.get_value(
			"CRM Committee", r.parent, ["name", "committee_name", "active", "quorum_pct", "majority_rule"], as_dict=True
		)
		if not committee or not committee.active:
			continue
		out.append({**committee, "my_role": r.role, "my_weight": r.weight or 1})
	return out


def _log_audit(item, event, payload=None, actor=None):
	if not _doctype_ready("CRM Committee Audit Event"):
		return
	try:
		actor = actor or frappe.session.user
		committee = frappe.db.get_value("CRM Committee Item", item, "committee")
		latest = frappe.get_all(
			"CRM Committee Audit Event",
			filters={"item": item},
			fields=["event_hash"],
			order_by="creation desc",
			limit=1,
		)
		prev_hash = latest[0].event_hash if latest else ""
		payload_json = json.dumps(payload, default=str) if payload else ""
		data = f"{prev_hash}|{actor}|{event}|{now_datetime()}|{payload_json}"
		event_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
		log = frappe.new_doc("CRM Committee Audit Event")
		log.item = item
		log.committee = committee
		log.actor = actor
		log.actor_name = frappe.db.get_value("User", actor, "full_name") or actor
		log.event_at = now_datetime()
		log.event = event
		log.payload_json = payload_json
		log.ip_address = frappe.local.request_ip if hasattr(frappe.local, "request_ip") else ""
		log.user_agent = frappe.local.request.headers.get("User-Agent", "") if hasattr(frappe.local, "request") and hasattr(frappe.local.request, "headers") else ""
		log.prev_hash = prev_hash
		log.event_hash = event_hash
		log.insert(ignore_permissions=True)
	except Exception:
		pass


def _committee_doc(name):
	return frappe.get_doc("CRM Committee", name)


def _votes_for_item(item):
	rows = frappe.get_all(
		"CRM Committee Vote",
		filters={"item": item},
		fields=["name", "member", "member_name", "decision", "weight", "comment", "conditions", "signed_at", "ip_address"],
		order_by="signed_at asc",
	)
	for r in rows:
		try:
			r["conditions"] = json.loads(r.get("conditions") or "[]")
		except Exception:
			r["conditions"] = []
	return rows


def _tally(item_name, committee_name):
	votes = _votes_for_item(item_name)
	committee = _committee_doc(committee_name)
	total_members = len([m for m in committee.members if m.role != "Observer"])
	approve = sum(1 for v in votes if v["decision"] == "Approve")
	reject = sum(1 for v in votes if v["decision"] == "Reject")
	abstain = sum(1 for v in votes if v["decision"] == "Abstain")
	refer = sum(1 for v in votes if v["decision"] == "Refer Back")
	voted = approve + reject + abstain + refer
	quorum_pct = committee.quorum_pct or 60
	need_to_quorum = max(0, int(-(-total_members * quorum_pct // 100)) - voted)
	quorum_met = voted >= int(-(-total_members * quorum_pct // 100))
	decided_count = approve + reject
	outcome = None
	if quorum_met and decided_count > 0:
		if committee.majority_rule == "Unanimous":
			if reject == 0 and approve == decided_count:
				outcome = "Approved"
			elif approve == 0 and reject == decided_count:
				outcome = "Rejected"
		elif committee.majority_rule == "Qualified":
			if approve * 3 >= decided_count * 2:
				outcome = "Approved"
			elif reject * 3 >= decided_count * 2:
				outcome = "Rejected"
		elif committee.majority_rule == "Weighted":
			w_app = sum((v["weight"] or 1) for v in votes if v["decision"] == "Approve")
			w_rej = sum((v["weight"] or 1) for v in votes if v["decision"] == "Reject")
			if w_app > w_rej:
				outcome = "Approved"
			elif w_rej > w_app:
				outcome = "Rejected"
		else:
			if approve > reject:
				outcome = "Approved"
			elif reject > approve:
				outcome = "Rejected"
			elif committee.chairman_tie_break:
				chair_vote = next(
					(v for v in votes if any(m.member == v["member"] and m.role == "Chairman" for m in committee.members)),
					None,
				)
				if chair_vote:
					outcome = "Approved" if chair_vote["decision"] == "Approve" else "Rejected"
	return {
		"approve": approve,
		"reject": reject,
		"abstain": abstain,
		"refer_back": refer,
		"voted": voted,
		"total": total_members,
		"quorum_pct": quorum_pct,
		"quorum_met": quorum_met,
		"need_to_quorum": need_to_quorum,
		"majority_rule": committee.majority_rule,
		"outcome": outcome,
		"votes": votes,
	}


def _sla_state(sla_due):
	if not sla_due:
		return "ok"
	due = getdate(sla_due)
	today = getdate()
	delta = (due - today).days
	if delta < 0:
		return "breached"
	if delta <= 1:
		return "amber"
	return "ok"


def _item_row(item, my_vote_only=False, user=None):
	t = _tally(item.name, item.committee)
	user = user or frappe.session.user
	my_vote = next((v for v in t["votes"] if v["member"] == user), None)
	if my_vote_only and my_vote:
		return None
	return {
		"name": item.name,
		"application": item.application,
		"applicant_name": item.applicant_name,
		"committee": item.committee,
		"status": item.status,
		"facility_type": item.facility_type,
		"requested_amount": item.requested_amount,
		"risk_grade": item.risk_grade,
		"submitted_at": item.submitted_at,
		"sla_due": item.sla_due,
		"sla_state": _sla_state(item.sla_due),
		"tally": t,
		"my_vote": my_vote,
	}


# ---------- whitelisted endpoints ----------


@frappe.whitelist()
def get_context():
	if not _all_ready():
		return {"committees": [], "ready": False}
	user = frappe.session.user
	committees = _user_committees(user)
	return {
		"ready": True,
		"user": user,
		"user_full_name": frappe.db.get_value("User", user, "full_name") or user,
		"committees": committees,
	}


@frappe.whitelist()
def get_queue(committee=None, my_pending_only=0, sort_by="sla"):
	if not _all_ready():
		return []
	user = frappe.session.user
	my_committees = [c["name"] for c in _user_committees(user)]
	roles = set(frappe.get_roles())
	is_admin = bool(roles & {"System Manager", "Sales Manager"})
	filters = {"status": ["in", ["Pending", "Quorum Reached"]]}
	if not is_admin:
		if not my_committees:
			return []
		filters["committee"] = ["in", my_committees]
	elif committee:
		filters["committee"] = committee
	items = frappe.get_all(
		"CRM Committee Item",
		filters=filters,
		fields=[
			"name",
			"application",
			"applicant_name",
			"committee",
			"status",
			"facility_type",
			"requested_amount",
			"risk_grade",
			"submitted_at",
			"sla_due",
		],
		order_by="sla_due asc",
		limit_page_length=200,
	)
	rows = []
	for it in items:
		row = _item_row(frappe._dict(it), my_vote_only=int(my_pending_only) == 1, user=user)
		if row:
			rows.append(row)
	if sort_by == "amount":
		rows.sort(key=lambda r: r["requested_amount"] or 0, reverse=True)
	elif sort_by == "submitted":
		rows.sort(key=lambda r: r["submitted_at"] or "", reverse=True)
	else:
		rows.sort(key=lambda r: (r["sla_due"] or "9999-12-31", r["submitted_at"] or ""))
	return rows


@frappe.whitelist()
def get_review(item):
	if not _all_ready():
		frappe.throw(_("Committee module is not initialized."))
	item_doc = frappe.get_doc("CRM Committee Item", item)
	app = None
	if item_doc.application and frappe.db.exists("CRM Credit Application", item_doc.application):
		app = frappe.db.get_value(
			"CRM Credit Application",
			item_doc.application,
			[
				"name",
				"borrower",
				"borrower_name",
				"borrower_type",
				"status",
				"facility_type",
				"requested_amount",
				"risk_grade",
				"purpose",
				"industry",
				"notes",
			],
			as_dict=True,
		)
	docs = []
	if frappe.db.table_exists("CRM Customer Document") and app and app.get("borrower"):
		docs = frappe.get_all(
			"CRM Customer Document",
			filters={"customer": app.get("borrower")},
			fields=[
				"name",
				"title as document_title",
				"document_type",
				"expiry_status as status",
				"file as file_url",
			],
			order_by="document_type asc",
			limit_page_length=50,
		)
	committee = _committee_doc(item_doc.committee)
	members = [
		{"member": m.member, "name": m.member_name, "role": m.role, "weight": m.weight}
		for m in committee.members
	]
	t = _tally(item_doc.name, item_doc.committee)
	decision = None
	dec_name = frappe.db.exists("CRM Committee Decision", {"item": item_doc.name})
	if dec_name:
		decision = frappe.get_doc("CRM Committee Decision", dec_name).as_dict()
	return {
		"item": item_doc.as_dict(),
		"application": app,
		"documents": docs,
		"committee": {
			"name": committee.name,
			"committee_name": committee.committee_name,
			"quorum_pct": committee.quorum_pct,
			"majority_rule": committee.majority_rule,
			"chairman_tie_break": committee.chairman_tie_break,
			"members": members,
		},
		"tally": t,
		"my_vote": next((v for v in t["votes"] if v["member"] == frappe.session.user), None),
		"decision": decision,
	}


def _finalize_if_ready(item_doc):
	t = _tally(item_doc.name, item_doc.committee)
	if t["quorum_met"]:
		item_doc.db_set("status", "Quorum Reached")
	if t["outcome"]:
		if not frappe.db.exists("CRM Committee Decision", {"item": item_doc.name}):
			dec = frappe.get_doc(
				{
					"doctype": "CRM Committee Decision",
					"item": item_doc.name,
					"outcome": t["outcome"],
					"decided_at": now_datetime(),
					"decided_by": frappe.session.user,
					"approve_count": t["approve"],
					"reject_count": t["reject"],
					"abstain_count": t["abstain"],
					"tally_json": json.dumps(t, default=str),
				}
			)
			dec.insert(ignore_permissions=True)
			item_doc.db_set("status", "Decided")
			_log_audit(item_doc.name, "Decision Final", payload={"outcome": t["outcome"], "tally": t})
			if item_doc.application and frappe.db.exists("CRM Credit Application", item_doc.application):
				next_stage = "Legal Documentation" if t["outcome"] == "Approved" else "Rejected"
				frappe.db.set_value("CRM Credit Application", item_doc.application, "status", next_stage)


@frappe.whitelist()
def create_committee_item(committee, applicant_name, facility_type, requested_amount, risk_grade, description=None, application=None):
	if not _all_ready():
		frappe.throw(_("Committee module is not initialized."))
	if not frappe.db.exists("CRM Committee", committee):
		frappe.throw(_("Committee not found."))
	item = frappe.get_doc({
		"doctype": "CRM Committee Item",
		"committee": committee,
		"application": application,
		"applicant_name": applicant_name,
		"facility_type": facility_type,
		"requested_amount": flt(requested_amount),
		"risk_grade": risk_grade,
		"memo": description or "",
		"status": "Pending",
		"sla_due": add_to_date(now_datetime(), days=3),
		"submitted_at": now_datetime(),
	})
	item.insert(ignore_permissions=True)
	_log_audit(item.name, "Item Routed", payload={"committee": committee, "application": application})
	frappe.db.commit()
	return {"name": item.name, "message": "Committee item created"}


@frappe.whitelist()
def submit_vote(item, decision, comment=None, conditions=None, signature_ack=0):
	if not _all_ready():
		frappe.throw(_("Committee module is not initialized."))
	if int(signature_ack or 0) != 1:
		frappe.throw(_("E-signature acknowledgement is required."))
	if decision not in ("Approve", "Reject", "Abstain", "Refer Back"):
		frappe.throw(_("Invalid decision."))
	if decision in ("Reject", "Refer Back") and not (comment or "").strip():
		frappe.throw(_("A comment is required when rejecting or referring back."))
	item_doc = frappe.get_doc("CRM Committee Item", item)
	if item_doc.status == "Decided":
		frappe.throw(_("This item has already been decided."))
	user = frappe.session.user
	committee = _committee_doc(item_doc.committee)
	member_row = next((m for m in committee.members if m.member == user), None)
	if not member_row:
		frappe.throw(_("You are not a member of this committee."))
	if member_row.role == "Observer":
		frappe.throw(_("Observers cannot vote."))
	existing = frappe.db.exists("CRM Committee Vote", {"item": item, "member": user})
	if existing:
		frappe.throw(_("You have already voted on this item."))
	conds = []
	if conditions:
		conds = conditions if isinstance(conditions, list) else json.loads(conditions)
	signed_at = now_datetime()
	sig_hash = _compute_vote_hash(item, user, decision, str(signed_at))
	vote = frappe.get_doc(
		{
			"doctype": "CRM Committee Vote",
			"item": item,
			"member": user,
			"member_name": member_row.member_name or frappe.db.get_value("User", user, "full_name"),
			"decision": decision,
			"weight": member_row.weight or 1,
			"comment": comment,
			"conditions": json.dumps(conds),
			"signed_at": signed_at,
			"signature_hash": sig_hash,
			"ip_address": frappe.local.request_ip if hasattr(frappe.local, "request_ip") else None,
		}
	)
	vote.insert(ignore_permissions=True)
	_log_audit(item, "Vote Cast", payload={"decision": decision, "member": user})
	_log_audit(item, "Signature Verified", payload={"signature_hash": sig_hash, "member": user})
	if decision == "Refer Back":
		item_doc.db_set("status", "Referred Back")
		if item_doc.application:
			ca = _allowed_app_status("Credit Analysis", {"Credit Analysis": "In Progress"})
			if ca:
				frappe.db.set_value("CRM Credit Application", item_doc.application, "status", ca)
	else:
		_finalize_if_ready(item_doc)
	frappe.db.commit()
	return get_review(item)


@frappe.whitelist()
def refer_back(item, questions):
	_log_audit(item, "Refer Back", payload={"questions": questions})
	return submit_vote(item=item, decision="Refer Back", comment=questions, signature_ack=1)


@frappe.whitelist()
def get_decisions(limit=100):
	if not _all_ready():
		return []
	user = frappe.session.user
	roles = set(frappe.get_roles())
	my_committees = [c["name"] for c in _user_committees(user)]
	is_admin = bool(roles & {"System Manager", "Sales Manager"})
	decisions = frappe.get_all(
		"CRM Committee Decision",
		fields=["name", "item", "outcome", "decided_at", "decided_by", "approve_count", "reject_count", "abstain_count"],
		order_by="decided_at desc",
		limit_page_length=int(limit),
	)
	out = []
	for d in decisions:
		item = frappe.db.get_value(
			"CRM Committee Item",
			d.item,
			["name", "application", "applicant_name", "committee", "requested_amount", "facility_type"],
			as_dict=True,
		)
		if not item:
			continue
		if not is_admin and item.committee not in my_committees:
			continue
		out.append({**d, "item_detail": item})
	return out


@frappe.whitelist()
def export_decisions_csv():
	rows = get_decisions(limit=1000)
	import csv
	import io

	buf = io.StringIO()
	w = csv.writer(buf)
	w.writerow(
		["Decision ID", "Item", "Application", "Applicant", "Committee", "Outcome", "Approve", "Reject", "Abstain", "Amount", "Decided At", "Decided By"]
	)
	for r in rows:
		it = r["item_detail"]
		w.writerow(
			[
				r["name"],
				r["item"],
				it.get("application"),
				it.get("applicant_name"),
				it.get("committee"),
				r["outcome"],
				r["approve_count"],
				r["reject_count"],
				r["abstain_count"],
				it.get("requested_amount"),
				r["decided_at"],
				r["decided_by"],
			]
		)
	return buf.getvalue()


@frappe.whitelist()
def list_committees():
	if not _doctype_ready("CRM Committee"):
		return []
	committees = frappe.get_all(
		"CRM Committee",
		fields=["name", "committee_name", "active", "quorum_pct", "majority_rule", "chairman_tie_break"],
		order_by="committee_name asc",
	)
	for c in committees:
		c["members"] = frappe.get_all(
			"CRM Committee Member",
			filters={"parent": c["name"], "parenttype": "CRM Committee"},
			fields=["member", "member_name", "role", "weight", "effective_from", "effective_to", "substitute"],
		)
	return committees


@frappe.whitelist()
def upsert_committee(committee_name, quorum_pct=60, majority_rule="Simple", chairman_tie_break=0, active=1, description=None, members=None):
	doc = None
	if frappe.db.exists("CRM Committee", committee_name):
		doc = frappe.get_doc("CRM Committee", committee_name)
	else:
		doc = frappe.new_doc("CRM Committee")
		doc.committee_name = committee_name
	doc.quorum_pct = int(quorum_pct)
	doc.majority_rule = majority_rule
	doc.chairman_tie_break = int(chairman_tie_break)
	doc.active = int(active)
	doc.description = description
	if members is not None:
		members = members if isinstance(members, list) else json.loads(members)
		doc.set("members", [])
		for m in members:
			if not m.get("member"):
				continue
			doc.append(
				"members",
				{
					"member": m["member"],
					"member_name": m.get("member_name") or frappe.db.get_value("User", m["member"], "full_name"),
					"role": m.get("role") or "Member",
					"weight": m.get("weight") or 1,
					"effective_from": m.get("effective_from"),
					"effective_to": m.get("effective_to"),
					"substitute": m.get("substitute"),
				},
			)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def list_meetings():
	if not _doctype_ready("CRM Committee Meeting"):
		return []
	meetings = frappe.get_all(
		"CRM Committee Meeting",
		fields=["name", "title", "committee", "scheduled_at", "duration_minutes", "status", "location"],
		order_by="scheduled_at asc",
	)
	for m in meetings:
		raw_agenda = frappe.db.get_value("CRM Committee Meeting", m["name"], "agenda_json")
		try:
			m["agenda"] = json.loads(raw_agenda) if raw_agenda else []
		except Exception:
			m["agenda"] = []
		raw_att = frappe.db.get_value("CRM Committee Meeting", m["name"], "attendees_json")
		try:
			m["attendees"] = json.loads(raw_att) if raw_att else []
		except Exception:
			m["attendees"] = []
	return meetings


@frappe.whitelist()
def rsvp_meeting(meeting, response):
	if not _doctype_ready("CRM Committee Meeting"):
		frappe.throw(_("Meetings not enabled."))
	if response not in ("yes", "no", "maybe"):
		frappe.throw(_("Invalid response."))
	doc = frappe.get_doc("CRM Committee Meeting", meeting)
	try:
		attendees = json.loads(doc.attendees_json or "[]")
	except Exception:
		attendees = []
	user = frappe.session.user
	attendees = [a for a in attendees if a.get("user") != user]
	attendees.append(
		{"user": user, "name": frappe.db.get_value("User", user, "full_name") or user, "response": response}
	)
	doc.attendees_json = json.dumps(attendees)
	doc.save(ignore_permissions=True)
	return attendees


@frappe.whitelist()
def create_meeting(title, committee, scheduled_at, duration_minutes=60, location=None):
	if not _doctype_ready("CRM Committee Meeting"):
		frappe.throw(_("Meetings not enabled."))
	if not frappe.db.exists("CRM Committee", committee):
		frappe.throw(_("Committee not found."))
	mt = frappe.get_doc({
		"doctype": "CRM Committee Meeting",
		"title": title,
		"committee": committee,
		"scheduled_at": scheduled_at,
		"duration_minutes": int(duration_minutes),
		"location": location or "",
		"status": "Scheduled",
		"attendees_json": "[]",
	})
	mt.insert(ignore_permissions=True)
	frappe.db.commit()
	return {"name": mt.name, "message": "Meeting scheduled"}


@frappe.whitelist()
def list_routing_rules():
	if not _doctype_ready("CRM Committee Routing Rule"):
		return []
	return frappe.get_all(
		"CRM Committee Routing Rule",
		fields=["name", "rule_name", "active", "priority", "committee", "min_amount", "max_amount", "product_type", "risk_grade"],
		order_by="priority asc",
	)


@frappe.whitelist()
def upsert_routing_rule(rule_name, committee, min_amount=0, max_amount=0, product_type=None, risk_grade=None, priority=10, active=1):
	if frappe.db.exists("CRM Committee Routing Rule", rule_name):
		doc = frappe.get_doc("CRM Committee Routing Rule", rule_name)
	else:
		doc = frappe.new_doc("CRM Committee Routing Rule")
		doc.rule_name = rule_name
	doc.committee = committee
	doc.min_amount = float(min_amount or 0)
	doc.max_amount = float(max_amount or 0)
	doc.product_type = product_type
	doc.risk_grade = risk_grade
	doc.priority = int(priority)
	doc.active = int(active)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return doc.name


@frappe.whitelist()
def voting_history(user=None):
	if not _all_ready():
		return []
	user = user or frappe.session.user
	votes = frappe.get_all(
		"CRM Committee Vote",
		filters={"member": user},
		fields=["name", "item", "decision", "signed_at", "comment", "signature_hash"],
		order_by="signed_at desc",
		limit_page_length=200,
	)
	for v in votes:
		v["verified"] = _verify_vote_hash(v["name"]) if v.get("signature_hash") else None
	tally = defaultdict(int)
	for v in votes:
		tally[v["decision"]] += 1
	return {"votes": votes, "summary": dict(tally)}


@frappe.whitelist()
def verify_vote(vote_name):
	if not _all_ready():
		return {"valid": False, "message": "Module not initialized"}
	valid = _verify_vote_hash(vote_name)
	return {"valid": valid, "message": "Signature verified" if valid else "Signature mismatch"}


@frappe.whitelist()
def delete_committee(name):
	if not _doctype_ready("CRM Committee"):
		frappe.throw(_("Committee module not initialized"))
	doc = frappe.get_doc("CRM Committee", name)
	doc.db_set("active", 0)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def delete_routing_rule(name):
	if not _doctype_ready("CRM Committee Routing Rule"):
		frappe.throw(_("Routing rules not enabled"))
	frappe.delete_doc("CRM Committee Routing Rule", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def delete_meeting(name):
	if not _doctype_ready("CRM Committee Meeting"):
		frappe.throw(_("Meetings not enabled"))
	frappe.delete_doc("CRM Committee Meeting", name, ignore_permissions=True)
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def seed_committee_sample_data():
	if not _all_ready():
		frappe.throw(_("Committee module is not initialized."))
	existing = frappe.get_all("CRM Committee", limit=1)
	if existing:
		return {"created": False, "message": "Committees already exist"}

	user = frappe.session.user
	users = frappe.get_all(
		"User",
		filters={"enabled": 1, "user_type": "System User"},
		fields=["name", "full_name"],
		limit_page_length=3,
	)
	if not users:
		users = [{"name": user, "full_name": frappe.db.get_value("User", user, "full_name") or user}]

	# Committee 1
	c1 = frappe.new_doc("CRM Committee")
	c1.committee_name = "Credit Committee A"
	c1.quorum_pct = 60
	c1.majority_rule = "Simple"
	c1.chairman_tie_break = 1
	c1.active = 1
	c1.description = "Primary credit approval committee"
	for i, u in enumerate(users[:2]):
		c1.append(
			"members",
			{
				"member": u["name"],
				"member_name": u["full_name"] or u["name"],
				"role": "Chairman" if i == 0 else "Member",
				"weight": 2 if i == 0 else 1,
			},
		)
	c1.insert(ignore_permissions=True)

	# Committee 2
	c2 = frappe.new_doc("CRM Committee")
	c2.committee_name = "Risk Committee B"
	c2.quorum_pct = 70
	c2.majority_rule = "Qualified"
	c2.chairman_tie_break = 0
	c2.active = 1
	c2.description = "Secondary risk review committee"
	for i, u in enumerate(users[:2]):
		c2.append(
			"members",
			{
				"member": u["name"],
				"member_name": u["full_name"] or u["name"],
				"role": "Member",
				"weight": 1,
			},
		)
	c2.insert(ignore_permissions=True)

	# Routing rule
	rule = frappe.new_doc("CRM Committee Routing Rule")
	rule.rule_name = "Auto-Route Working Capital"
	rule.committee = c1.name
	rule.min_amount = 0
	rule.max_amount = 500000000
	rule.product_type = "Working Capital"
	rule.priority = 10
	rule.active = 1
	rule.insert(ignore_permissions=True)

	# Meeting
	mt = frappe.new_doc("CRM Committee Meeting")
	mt.title = "Weekly Credit Review"
	mt.committee = c1.name
	mt.scheduled_at = add_to_date(now_datetime(), days=2)
	mt.duration_minutes = 60
	mt.status = "Scheduled"
	mt.location = "Conference Room A"
	mt.agenda_json = json.dumps(
		[
			{"item": "Review pending applications", "minutes": 30},
			{"item": "Risk updates", "minutes": 20},
		]
	)
	mt.attendees_json = json.dumps([])
	mt.insert(ignore_permissions=True)

	# Committee item
	app = None
	if _doctype_ready("CRM Credit Application"):
		app_candidates = frappe.get_all(
			"CRM Credit Application",
			fields=["name", "borrower_name", "facility_type", "requested_amount", "risk_grade"],
			limit=1,
		)
		if app_candidates:
			app = app_candidates[0]

	item = frappe.new_doc("CRM Committee Item")
	item.committee = c1.name
	item.application = app["name"] if app else None
	item.applicant_name = app["borrower_name"] if app else "Sample Applicant"
	item.facility_type = app["facility_type"] if app else "Working Capital"
	item.requested_amount = app["requested_amount"] if app else 250000000
	item.risk_grade = app["risk_grade"] if app else "B"
	item.status = "Pending"
	item.sla_due = add_to_date(now_datetime(), days=3)
	item.submitted_at = now_datetime()
	item.insert(ignore_permissions=True)

	# Sample vote + decision
	member = c1.members[0].member if c1.members else user
	member_name = c1.members[0].member_name if c1.members else (frappe.db.get_value("User", user, "full_name") or user)
	signed_at = now_datetime()
	sig_hash = _compute_vote_hash(item.name, member, "Approve", str(signed_at))
	vote = frappe.new_doc("CRM Committee Vote")
	vote.item = item.name
	vote.member = member
	vote.member_name = member_name
	vote.decision = "Approve"
	vote.weight = c1.members[0].weight if c1.members else 1
	vote.signed_at = signed_at
	vote.signature_hash = sig_hash
	vote.insert(ignore_permissions=True)

	# tally
	dec = frappe.new_doc("CRM Committee Decision")
	dec.item = item.name
	dec.outcome = "Approved"
	dec.decided_at = now_datetime()
	dec.decided_by = user
	dec.approve_count = 1
	dec.reject_count = 0
	dec.abstain_count = 0
	dec.tally_json = json.dumps({"approve": 1, "reject": 0, "abstain": 0, "total": 1}, default=str)
	dec.insert(ignore_permissions=True)
	item.db_set("status", "Decided")

	# Create a second item that stays Pending for queue demonstration
	item2 = frappe.new_doc("CRM Committee Item")
	item2.committee = c1.name
	item2.application = None
	item2.applicant_name = "PT Maju Bersama"
	item2.facility_type = "Invoice Financing"
	item2.requested_amount = 125000000
	item2.risk_grade = "A"
	item2.status = "Pending"
	item2.sla_due = add_to_date(now_datetime(), days=5)
	item2.submitted_at = now_datetime()
	item2.memo = "Sample pending item for demonstration"
	item2.insert(ignore_permissions=True)

	frappe.db.commit()
	return {"created": True, "committees": [c1.name, c2.name]}


@frappe.whitelist()
def get_audit_trail(item=None, committee=None, actor=None, event=None, date_from=None, date_to=None, search=None, limit=200):
	if not _doctype_ready("CRM Committee Audit Event"):
		return {"events": [], "chain_ok": True}
	filters = {}
	if item:
		filters["item"] = item
	if committee:
		filters["committee"] = committee
	if actor:
		filters["actor"] = actor
	if event:
		filters["event"] = event
	if date_from or date_to:
		filters["event_at"] = ["between", [date_from or "1900-01-01", date_to or "2999-12-31"]]
	q = (search or "").strip()
	if q:
		filters["_liked_by"] = ["like", f"%{q}%"]
	events = frappe.get_all(
		"CRM Committee Audit Event",
		filters=filters,
		fields=["name", "item", "committee", "actor", "actor_name", "event_at", "event", "payload_json", "ip_address", "event_hash", "prev_hash", "creation"],
		order_by="creation desc",
		limit=limit,
	)
	chain_ok = True
	broken_at = None
	for i in range(len(events) - 1, 0, -1):
		if events[i].prev_hash != events[i - 1].event_hash:
			chain_ok = False
			broken_at = events[i].event_at
			break
	return {"events": events, "chain_ok": chain_ok, "broken_at": broken_at}


@frappe.whitelist()
def verify_audit_chain(item):
	if not _doctype_ready("CRM Committee Audit Event"):
		return {"ok": True}
	events = frappe.get_all(
		"CRM Committee Audit Event",
		filters={"item": item},
		fields=["event_hash", "prev_hash", "event_at"],
		order_by="creation asc",
	)
	for i in range(1, len(events)):
		if events[i].prev_hash != events[i - 1].event_hash:
			return {"ok": False, "broken_at": events[i].event_at}
	return {"ok": True}


@frappe.whitelist()
def record_item_view(item):
	_log_audit(item, "Item Viewed")
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def add_comment(item, text):
	if not text:
		frappe.throw(_("Comment is required."))
	frappe.get_doc({
		"doctype": "Comment",
		"comment_type": "Comment",
		"reference_doctype": "CRM Committee Item",
		"reference_name": item,
		"comment_email": frappe.session.user,
		"comment_by": frappe.db.get_value("User", frappe.session.user, "full_name") or frappe.session.user,
		"content": text,
	}).insert(ignore_permissions=True)
	_log_audit(item, "Comment Added", payload={"text": text[:200]})
	frappe.db.commit()
	return {"ok": True}


@frappe.whitelist()
def apply_override(item, decision, reason):
	if not _doctype_ready("CRM Committee Item"):
		frappe.throw(_("Committee module is not initialized."))
	roles = set(frappe.get_roles())
	if not (roles & {"System Manager", "Sales Manager"}):
		frappe.throw(_("Only managers can override decisions."))
	item_doc = frappe.get_doc("CRM Committee Item", item)
	if item_doc.status != "Decided":
		frappe.throw(_("Only decided items can be overridden."))
	item_doc.db_set("status", "Overridden")
	_log_audit(item, "Override Applied", payload={"decision": decision, "reason": reason})
	frappe.db.commit()
	return {"ok": True}
