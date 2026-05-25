import json

import frappe
from frappe.utils import add_days, add_to_date, now_datetime, today


COMMITTEE_MARKER = "committee_demo"


def _doctype_ready(doctype):
	return frappe.db.table_exists(doctype)


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


def _users():
	emails = ["sari.demo@example.com", "budi.demo@example.com", "dewi.demo@example.com"]
	users = [e for e in emails if frappe.db.exists("User", e)]
	if frappe.db.exists("User", "Administrator"):
		users.append("Administrator")
	return users


def _full_name(user):
	return frappe.db.get_value("User", user, "full_name") or user


def _seed_committees(users):
	if len(users) < 3:
		return []
	out = []
	if not frappe.db.exists("CRM Committee", "Retail Credit Committee"):
		retail = frappe.get_doc(
			{
				"doctype": "CRM Committee",
				"committee_name": "Retail Credit Committee",
				"active": 1,
				"quorum_pct": 60,
				"majority_rule": "Simple",
				"chairman_tie_break": 1,
				"description": f"{COMMITTEE_MARKER}: Retail and SME committee for facilities under IDR 2B.",
				"members": [
					{"member": users[0], "member_name": _full_name(users[0]), "role": "Chairman", "weight": 1.5},
					{"member": users[1], "member_name": _full_name(users[1]), "role": "Member", "weight": 1},
					{"member": users[2], "member_name": _full_name(users[2]), "role": "Member", "weight": 1},
				],
			}
		)
		if len(users) >= 4:
			retail.append("members", {"member": users[3], "member_name": _full_name(users[3]), "role": "Member", "weight": 1})
		retail.insert(ignore_permissions=True)
		out.append("Retail Credit Committee")
	else:
		out.append("Retail Credit Committee")

	if not frappe.db.exists("CRM Committee", "Corporate Credit Committee"):
		corp = frappe.get_doc(
			{
				"doctype": "CRM Committee",
				"committee_name": "Corporate Credit Committee",
				"active": 1,
				"quorum_pct": 70,
				"majority_rule": "Qualified",
				"chairman_tie_break": 0,
				"description": f"{COMMITTEE_MARKER}: Corporate committee for facilities above IDR 2B.",
				"members": [
					{"member": users[0], "member_name": _full_name(users[0]), "role": "Chairman", "weight": 2},
					{"member": users[1], "member_name": _full_name(users[1]), "role": "Member", "weight": 1.5},
					{"member": users[2], "member_name": _full_name(users[2]), "role": "Member", "weight": 1.5},
				],
			}
		)
		if len(users) >= 4:
			corp.append("members", {"member": users[3], "member_name": _full_name(users[3]), "role": "Observer", "weight": 0})
		corp.insert(ignore_permissions=True)
		out.append("Corporate Credit Committee")
	else:
		out.append("Corporate Credit Committee")
	return out


def _seed_routing_rules():
	rules = [
		{"rule_name": "Retail under 2B", "priority": 10, "min_amount": 0, "max_amount": 2_000_000_000, "committee": "Retail Credit Committee"},
		{"rule_name": "Corporate above 2B", "priority": 20, "min_amount": 2_000_000_000, "max_amount": 0, "committee": "Corporate Credit Committee"},
		{"rule_name": "High-risk override", "priority": 5, "min_amount": 0, "max_amount": 0, "risk_grade": "C", "committee": "Corporate Credit Committee"},
	]
	out = []
	for r in rules:
		if frappe.db.exists("CRM Committee Routing Rule", r["rule_name"]):
			out.append(r["rule_name"])
			continue
		doc = frappe.get_doc(
			{
				"doctype": "CRM Committee Routing Rule",
				"rule_name": r["rule_name"],
				"active": 1,
				"priority": r["priority"],
				"min_amount": r.get("min_amount", 0),
				"max_amount": r.get("max_amount", 0),
				"product_type": r.get("product_type"),
				"risk_grade": r.get("risk_grade"),
				"committee": r["committee"],
			}
		).insert(ignore_permissions=True)
		out.append(doc.name)
	return out


def _allowed_app_status(desired, fallback_map=None):
	if not frappe.db.table_exists("CRM Credit Application"):
		return desired
	meta = frappe.get_meta("CRM Credit Application")
	field = meta.get_field("status")
	if not field:
		return desired
	options = [o.strip() for o in (field.options or "").split("\n") if o.strip()]
	if not options or desired in options:
		return desired
	fb = (fallback_map or {}).get(desired)
	if fb and fb in options:
		return fb
	return options[0]


def _ensure_application(customer, facility_type, amount, purpose, risk_grade):
	if not frappe.db.exists("Customer", customer):
		return None
	existing = frappe.get_all(
		"CRM Credit Application",
		filters={
			"borrower": customer,
			"facility_type": facility_type,
			"purpose": ["like", f"%{COMMITTEE_MARKER}%"],
		},
		pluck="name",
		limit=1,
	)
	if existing:
		return existing[0]
	status = _allowed_app_status(
		"Committee Approval",
		{"Committee Approval": "In Progress"},
	)
	doc = frappe.get_doc(
		{
			"doctype": "CRM Credit Application",
			"borrower": customer,
			"borrower_name": frappe.db.get_value("Customer", customer, "customer_name") or customer,
			"borrower_type": "Company",
			"status": status,
			"facility_type": facility_type,
			"requested_amount": amount,
			"risk_grade": risk_grade,
			"purpose": f"{COMMITTEE_MARKER}: {purpose}",
			"notes": f"{COMMITTEE_MARKER}: Routed to credit committee.",
		}
	).insert(ignore_permissions=True)
	return doc.name


def _ensure_item(application, committee, sla_days, memo, ai_insights):
	if not application:
		return None
	existing = frappe.get_all(
		"CRM Committee Item", filters={"application": application}, pluck="name", limit=1
	)
	if existing:
		return existing[0]
	app_row = frappe.db.get_value(
		"CRM Credit Application",
		application,
		["borrower_name", "facility_type", "requested_amount", "risk_grade"],
		as_dict=True,
	)
	doc = frappe.get_doc(
		{
			"doctype": "CRM Committee Item",
			"application": application,
			"applicant_name": app_row.borrower_name if app_row else application,
			"committee": committee,
			"status": "Pending",
			"facility_type": app_row.facility_type if app_row else None,
			"requested_amount": app_row.requested_amount if app_row else None,
			"risk_grade": app_row.risk_grade if app_row else None,
			"submitted_at": add_to_date(now_datetime(), days=-2),
			"sla_due": add_to_date(now_datetime(), days=sla_days),
			"memo": memo,
			"ai_insights": ai_insights,
		}
	).insert(ignore_permissions=True)
	return doc.name


def _cast_vote(item, member, decision, comment=None, conditions=None, weight=1):
	if not item or not member:
		return None
	existing = frappe.get_all(
		"CRM Committee Vote",
		filters={"item": item, "member": member},
		pluck="name",
		limit=1,
	)
	if existing:
		return existing[0]
	doc = frappe.get_doc(
		{
			"doctype": "CRM Committee Vote",
			"item": item,
			"member": member,
			"member_name": _full_name(member),
			"decision": decision,
			"weight": weight,
			"comment": comment,
			"conditions": json.dumps(conditions or []),
			"signed_at": now_datetime(),
		}
	).insert(ignore_permissions=True)
	return doc.name


def _recompute_item_status(item_name):
	from crm.api.committee import _tally

	item = frappe.get_doc("CRM Committee Item", item_name)
	t = _tally(item.name, item.committee)
	if t["outcome"]:
		if not frappe.db.exists("CRM Committee Decision", {"item": item.name}):
			frappe.get_doc(
				{
					"doctype": "CRM Committee Decision",
					"item": item.name,
					"outcome": t["outcome"],
					"approve_count": t["approve"],
					"reject_count": t["reject"],
					"abstain_count": t["abstain"],
					"decided_at": now_datetime(),
					"decided_by": "Administrator",
					"tally_json": json.dumps(t, default=str),
					"minutes_text": f"<p>{COMMITTEE_MARKER}: Auto-finalized by demo seed.</p>",
				}
			).insert(ignore_permissions=True)
		item.db_set("status", "Decided")
	elif t["quorum_met"]:
		item.db_set("status", "Quorum Reached")


def _seed_meetings(committees, users):
	now = now_datetime()
	scenarios = [
		{
			"title": "Retail Weekly Standing Committee",
			"committee": committees[0] if committees else None,
			"scheduled_at": add_to_date(now, days=2),
			"status": "Scheduled",
			"agenda": [
				{"item": "Review PT Maju Jaya top-up", "minutes": 15},
				{"item": "Review PT Industri Nusantara", "minutes": 20},
				{"item": "Policy review", "minutes": 10},
			],
		},
		{
			"title": "Corporate Monthly Committee",
			"committee": committees[1] if len(committees) > 1 else committees[0] if committees else None,
			"scheduled_at": add_to_date(now, days=10),
			"status": "Scheduled",
			"agenda": [
				{"item": "PT Teknologi Maju expansion loan", "minutes": 30},
				{"item": "Sector exposure review", "minutes": 20},
			],
		},
		{
			"title": "Retail Committee Recap",
			"committee": committees[0] if committees else None,
			"scheduled_at": add_to_date(now, days=-7),
			"status": "Completed",
			"agenda": [{"item": "Prior week's pipeline", "minutes": 30}],
		},
	]
	out = []
	for s in scenarios:
		if not s["committee"]:
			continue
		existing = frappe.get_all(
			"CRM Committee Meeting",
			filters={"title": s["title"], "committee": s["committee"]},
			pluck="name",
			limit=1,
		)
		if existing:
			out.append(existing[0])
			continue
		attendees = [
			{"user": u, "name": _full_name(u), "response": "yes"} for u in users[:3]
		]
		doc = frappe.get_doc(
			{
				"doctype": "CRM Committee Meeting",
				"title": s["title"],
				"committee": s["committee"],
				"scheduled_at": s["scheduled_at"],
				"duration_minutes": 60,
				"status": s["status"],
				"location": "Board Room A / Zoom",
				"agenda_json": json.dumps(s["agenda"]),
				"attendees_json": json.dumps(attendees),
			}
		).insert(ignore_permissions=True)
		out.append(doc.name)
	return out


def seed_default():
	"""No-arg wrapper for bench execute — seeds against the standard demo customers."""
	defaults = ["PT Maju Jaya", "PT Industri Nusantara", "CV Cahaya Terang", "PT Teknologi Maju"]
	return create_demo_committee(defaults)


def create_demo_committee(customer_names):
	created = {
		"committees": [],
		"routing_rules": [],
		"applications": [],
		"items": [],
		"votes": [],
		"decisions": [],
		"meetings": [],
	}
	if not _all_ready():
		return created
	users = _users()
	if len(users) < 3:
		return created

	created["committees"] = _seed_committees(users)
	created["routing_rules"] = _seed_routing_rules()
	created["meetings"] = _seed_meetings(created["committees"], users)

	customers = set(customer_names or [])
	retail = "Retail Credit Committee"
	corp = "Corporate Credit Committee"

	# Scenario 1: PT Maju Jaya — quorum reached, awaiting last vote
	if "PT Maju Jaya" in customers:
		app = _ensure_application(
			"PT Maju Jaya",
			"Working Capital Top-Up",
			1_800_000_000,
			"Working capital top-up for inventory expansion.",
			"A-",
		)
		if app:
			created["applications"].append(app)
			item = _ensure_item(
				app,
				retail,
				sla_days=2,
				memo="<p>Healthy customer with 18-month repayment history. Requested IDR 1.8B top-up against current IDR 1.5B facility. Cash conversion cycle stable.</p>",
				ai_insights="Risk score: 82/100. DSCR: 1.45. Recommend approval with standard CP.",
			)
			if item:
				created["items"].append(item)
				created["votes"].append(_cast_vote(item, users[0], "Approve", "Strong fundamentals.", ["Quarterly financial submission"], 1.5))
				created["votes"].append(_cast_vote(item, users[1], "Approve", "Agree, low risk.", [], 1))
				_recompute_item_status(item)

	# Scenario 2: PT Industri Nusantara — SLA breaching, only 1 vote
	if "PT Industri Nusantara" in customers:
		app = _ensure_application(
			"PT Industri Nusantara",
			"Investment Loan",
			3_500_000_000,
			"Investment loan for machinery expansion (corporate).",
			"B+",
		)
		if app:
			created["applications"].append(app)
			item = _ensure_item(
				app,
				corp,
				sla_days=0,
				memo="<p>Manufacturing expansion; collateral covers 130% LTV. Bureau report clean.</p>",
				ai_insights="Risk score: 68/100. DSCR: 1.18. Recommend conditional approval.",
			)
			if item:
				# backdate sla_due to be breached
				frappe.db.set_value("CRM Committee Item", item, "sla_due", add_to_date(now_datetime(), days=-1))
				created["items"].append(item)
				created["votes"].append(_cast_vote(item, users[1], "Approve", "Acceptable with conditions.", ["Independent valuer report", "Personal guarantee from director"], 1.5))
				_recompute_item_status(item)

	# Scenario 3: CV Cahaya Terang — referred back once
	if "CV Cahaya Terang" in customers:
		app = _ensure_application(
			"CV Cahaya Terang",
			"Invoice Financing",
			800_000_000,
			"Invoice financing for retail buyer concentration.",
			"B",
		)
		if app:
			created["applications"].append(app)
			item = _ensure_item(
				app,
				retail,
				sla_days=5,
				memo="<p>Buyer concentration risk: 60% from a single buyer. Re-tabled after CFO submitted diversification plan.</p>",
				ai_insights="Risk score: 58/100. Concentration risk flag. Recommend deeper analysis.",
			)
			if item:
				frappe.db.set_value("CRM Committee Item", item, "status", "Referred Back")
				created["items"].append(item)
				created["votes"].append(_cast_vote(item, users[1], "Refer Back", "Need updated buyer diversification plan and aging report.", [], 1))

	# Scenario 4: PT Teknologi Maju — corporate, weighted votes mid-flight
	if "PT Teknologi Maju" in customers:
		app = _ensure_application(
			"PT Teknologi Maju",
			"Investment Loan",
			5_200_000_000,
			"Large corporate facility for tech infrastructure rollout.",
			"B+",
		)
		if app:
			created["applications"].append(app)
			item = _ensure_item(
				app,
				corp,
				sla_days=3,
				memo="<p>Tech sector facility; 48-month tenor. Sponsors are reputable. Existing facility in good standing.</p>",
				ai_insights="Risk score: 71/100. Strong sponsors offset sector volatility.",
			)
			if item:
				created["items"].append(item)
				created["votes"].append(_cast_vote(item, users[0], "Approve", "Sponsor strength sufficient.", ["Negative pledge on group assets"], 2))
				_recompute_item_status(item)

	# Optional scenario: finalized decisions for the audit log
	# Create a small finalized item to populate the decisions tab
	if "PT Maju Jaya" in customers and len(users) >= 3:
		app = _ensure_application(
			"PT Maju Jaya",
			"Bridging Loan",
			500_000_000,
			"Short-term bridging while waiting for export receivables.",
			"A",
		)
		if app:
			created["applications"].append(app)
			item = _ensure_item(
				app,
				retail,
				sla_days=-10,
				memo="<p>Approved last month. Already disbursed.</p>",
				ai_insights="Auto-finalized example.",
			)
			if item:
				created["items"].append(item)
				created["votes"].append(_cast_vote(item, users[0], "Approve", "OK", [], 1.5))
				created["votes"].append(_cast_vote(item, users[1], "Approve", "OK", [], 1))
				created["votes"].append(_cast_vote(item, users[2], "Approve", "OK", [], 1))
				_recompute_item_status(item)
				dec = frappe.db.exists("CRM Committee Decision", {"item": item})
				if dec:
					created["decisions"].append(dec)

	frappe.db.commit()
	return created


def delete_demo_committee(data):
	if not isinstance(data, dict):
		return
	for doctype, key in (
		("CRM Committee Decision", "decisions"),
		("CRM Committee Vote", "votes"),
		("CRM Committee Item", "items"),
		("CRM Credit Application", "applications"),
		("CRM Committee Meeting", "meetings"),
		("CRM Committee Routing Rule", "routing_rules"),
		("CRM Committee", "committees"),
	):
		if not _doctype_ready(doctype):
			continue
		for name in data.get(key, []) or []:
			if frappe.db.exists(doctype, name):
				try:
					frappe.delete_doc(doctype, name, ignore_permissions=True, force=True)
				except Exception:
					pass
	# Also sweep any orphaned decisions/votes left over (defensive)
	if _doctype_ready("CRM Committee Vote"):
		for v in frappe.get_all("CRM Committee Vote", filters={"item": ["in", data.get("items", []) or [""]]}, pluck="name"):
			if frappe.db.exists("CRM Committee Vote", v):
				frappe.delete_doc("CRM Committee Vote", v, ignore_permissions=True, force=True)
	frappe.db.commit()
