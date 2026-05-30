import csv
import io
import json

import frappe
from frappe import _
from frappe.utils import cint, flt, getdate, nowdate, today


PRODUCT_DOCTYPE = "CRM Product"
CHILD_FIELDS = ("interest_tiers", "fees", "eligibility_rules", "collateral_rules", "document_requirements", "approval_tiers")
EDITOR_ROLES = {"System Manager", "Sales Manager"}


def _can_edit():
	return bool(set(frappe.get_roles() or []) & EDITOR_ROLES)


def _assert_editor():
	if not _can_edit():
		frappe.throw(_("You do not have permission to modify products."), frappe.PermissionError)


def _serialize_product(doc):
	data = doc.as_dict()
	for key in ("docstatus", "owner", "_user_tags", "_comments", "_assign", "_liked_by"):
		data.pop(key, None)
	return data


def validate_product_before_save(doc, method):
	if doc.form_template:
		applies = frappe.db.get_value("CRM Product Form Template", doc.form_template, "applies_to_product_type")
		if applies and applies != "Any" and applies != doc.product_type:
			frappe.throw(_("Form template applies to {0}, but product type is {1}.").format(applies, doc.product_type))
	if doc.retirement_status == "Scheduled" and doc.retirement_date:
		if getdate(doc.retirement_date) <= getdate(today()):
			frappe.throw(_("Scheduled retirement date must be in the future."))


@frappe.whitelist()
def get_product_catalog(filters=None):
	if isinstance(filters, str):
		filters = json.loads(filters or "{}")
	filters = filters or {}

	where = {}
	if filters.get("status"):
		where["status"] = filters["status"]
	if filters.get("product_type"):
		where["product_type"] = filters["product_type"]
	if filters.get("currency"):
		where["currency"] = filters["currency"]
	if filters.get("disabled") in (0, 1, "0", "1"):
		where["disabled"] = cint(filters["disabled"])

	rows = frappe.get_all(
		PRODUCT_DOCTYPE,
		filters=where,
		fields=[
			"name",
			"product_code",
			"product_name",
			"product_type",
			"status",
			"currency",
			"min_amount",
			"max_amount",
			"min_tenor_months",
			"max_tenor_months",
			"version",
			"effective_date",
			"retirement_date",
			"retirement_status",
			"retirement_reason",
			"replacement_product",
			"modified",
			"marketing_tagline",
		],
		order_by="modified desc",
		limit_page_length=500,
	)

	q = (filters.get("search") or "").strip().lower()
	if q:
		rows = [
			r for r in rows
			if q in (r.get("product_code") or "").lower()
			or q in (r.get("product_name") or "").lower()
			or q in (r.get("marketing_tagline") or "").lower()
		]

	counts = {"total": len(rows), "active": 0, "draft": 0, "pending": 0, "retired": 0}
	for r in rows:
		s = (r.get("status") or "").lower()
		if s == "active":
			counts["active"] += 1
		elif s == "draft":
			counts["draft"] += 1
		elif s == "pending approval":
			counts["pending"] += 1
		elif s == "retired":
			counts["retired"] += 1

	return {"rows": rows, "counts": counts, "can_edit": _can_edit()}


@frappe.whitelist()
def get_product(code):
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	return _serialize_product(doc)


@frappe.whitelist()
def save_product(payload):
	_assert_editor()
	if isinstance(payload, str):
		payload = json.loads(payload)
	payload = payload or {}

	code = (payload.get("product_code") or "").strip()
	if not code:
		frappe.throw(_("Product Code is required."))

	exists = frappe.db.exists(PRODUCT_DOCTYPE, code)
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code) if exists else frappe.new_doc(PRODUCT_DOCTYPE)

	parent_fields = (
		"product_code", "product_name", "product_type", "currency", "status",
		"effective_date", "retirement_date", "marketing_tagline", "description",
		"image", "min_amount", "max_amount", "min_tenor_months", "max_tenor_months",
		"tenor_increment_months", "repayment_frequency", "grace_period_days",
		"allow_balloon", "allow_step_schedule", "workflow", "form_template",
		"form_template_version", "retirement_status", "retirement_scheduled_by",
		"retirement_scheduled_on", "retirement_reason", "replacement_product",
		"migration_plan", "retirement_notes", "disabled",
	)
	for f in parent_fields:
		if f in payload:
			doc.set(f, payload.get(f))

	# Only editors can publish directly. Force back to Draft otherwise.
	if not exists and not doc.status:
		doc.status = "Draft"

	for child_field in CHILD_FIELDS:
		if child_field in payload:
			doc.set(child_field, [])
			for row in payload.get(child_field) or []:
				if isinstance(row, dict):
					doc.append(child_field, row)

	doc.save(ignore_permissions=False)
	frappe.db.commit()
	return _serialize_product(doc)


@frappe.whitelist()
def submit_for_review(code):
	_assert_editor()
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	if doc.status not in ("Draft", "Pending Approval"):
		frappe.throw(_("Only Draft products can be submitted."))
	doc.status = "Pending Approval"
	doc.save()
	frappe.db.commit()
	return _serialize_product(doc)


@frappe.whitelist()
def approve_product(code):
	_assert_editor()
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	if doc.status != "Pending Approval":
		frappe.throw(_("Only products pending approval can be approved."))
	doc.status = "Active"
	doc.version = cint(doc.version) + 1
	if not doc.effective_date:
		doc.effective_date = nowdate()
	doc.save()
	frappe.db.commit()
	return _serialize_product(doc)


@frappe.whitelist()
def clone_product(code, new_code, new_name=None):
	_assert_editor()
	new_code = (new_code or "").strip()
	if not new_code:
		frappe.throw(_("New product code is required."))
	if frappe.db.exists(PRODUCT_DOCTYPE, new_code):
		frappe.throw(_("Product code {0} already exists.").format(new_code))

	src = frappe.get_doc(PRODUCT_DOCTYPE, code)
	new_doc = frappe.copy_doc(src)
	new_doc.product_code = new_code
	new_doc.product_name = new_name or f"{src.product_name} (Copy)"
	new_doc.status = "Draft"
	new_doc.version = 1
	new_doc.effective_date = None
	new_doc.retirement_date = None
	new_doc.insert(ignore_permissions=False)
	frappe.db.commit()
	return _serialize_product(new_doc)


@frappe.whitelist()
def retire_product(code, retirement_date=None, reason=None, replacement_product=None, migration_plan=None, mode="immediate", notes=None):
	_assert_editor()
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	previous_status = doc.status
	previous_retirement_date = doc.retirement_date
	retirement_date = getdate(retirement_date) if retirement_date else None

	if mode == "schedule":
		if not retirement_date or retirement_date <= getdate(today()):
			frappe.throw(_("Schedule date must be in the future. Use immediate retirement for today."))
		doc.retirement_status = "Scheduled"
		doc.retirement_date = retirement_date
		doc.retirement_scheduled_by = frappe.session.user
		doc.retirement_scheduled_on = frappe.utils.now()
		doc.retirement_reason = reason
		doc.replacement_product = replacement_product
		doc.migration_plan = migration_plan
		if notes:
			doc.retirement_notes = notes
		doc.save()
		_write_retirement_log(doc, "Scheduled", previous_status, doc.status, previous_retirement_date, doc.retirement_date, reason, replacement_product)
	else:
		doc.status = "Retired"
		doc.retirement_status = "Retired"
		doc.retirement_date = retirement_date or nowdate()
		doc.retirement_reason = reason
		doc.replacement_product = replacement_product
		doc.migration_plan = migration_plan
		if notes:
			doc.retirement_notes = notes
		doc.save()
		_write_retirement_log(doc, "Retired", previous_status, doc.status, previous_retirement_date, doc.retirement_date, reason, replacement_product)

	frappe.db.commit()
	return _serialize_product(doc)


@frappe.whitelist()
def cancel_retirement(code, note=None):
	_assert_editor()
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	if doc.retirement_status != "Scheduled":
		frappe.throw(_("Only scheduled retirements can be cancelled."))
	previous_status = doc.status
	previous_retirement_date = doc.retirement_date
	doc.retirement_status = "None"
	doc.retirement_date = None
	doc.retirement_scheduled_by = None
	doc.retirement_scheduled_on = None
	doc.retirement_reason = None
	doc.replacement_product = None
	doc.migration_plan = None
	doc.save()
	_write_retirement_log(doc, "Cancelled", previous_status, doc.status, previous_retirement_date, None, note=note)
	frappe.db.commit()
	return _serialize_product(doc)


@frappe.whitelist()
def reactivate_product(code, note=None):
	_assert_editor()
	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	if doc.status != "Retired":
		frappe.throw(_("Only retired products can be reactivated."))
	previous_status = doc.status
	doc.status = "Active"
	doc.retirement_status = "None"
	doc.retirement_date = None
	doc.retirement_reason = None
	doc.save()
	_write_retirement_log(doc, "Reactivated", previous_status, doc.status, note=note)
	frappe.db.commit()
	return _serialize_product(doc)


def _write_retirement_log(doc, action, previous_status=None, new_status=None, previous_retirement_date=None, new_retirement_date=None, reason=None, replacement_product=None, note=None):
	if not frappe.db.table_exists("CRM Product Retirement Log"):
		return
	log = frappe.new_doc("CRM Product Retirement Log")
	log.product = doc.name
	log.action = action
	log.previous_status = previous_status
	log.new_status = new_status
	log.previous_retirement_date = previous_retirement_date
	log.new_retirement_date = new_retirement_date
	log.reason = reason or doc.retirement_reason
	log.replacement_product = replacement_product or doc.replacement_product
	log.actor = frappe.session.user
	log.note = note or doc.retirement_notes
	log.insert(ignore_permissions=True)


@frappe.whitelist()
def list_retirements(range="all"):
	if not frappe.db.table_exists("CRM Product Retirement Log"):
		return {"upcoming": [], "past": []}
	if range == "upcoming":
		products = frappe.get_all(
			PRODUCT_DOCTYPE,
			filters={"retirement_status": "Scheduled"},
			fields=["name", "product_code", "product_name", "retirement_date", "retirement_reason", "replacement_product", "retirement_scheduled_on"],
			order_by="retirement_date asc",
		)
		return {"upcoming": products, "past": []}
	logs = frappe.get_all(
		"CRM Product Retirement Log",
		fields=["name", "product", "action", "previous_status", "new_status", "previous_retirement_date", "new_retirement_date", "reason", "replacement_product", "actor", "note", "creation"],
		order_by="creation desc",
		limit=500,
	)
	return {"upcoming": [], "past": logs}


@frappe.whitelist()
def is_product_open_for_new_applications(code):
	status = frappe.db.get_value(PRODUCT_DOCTYPE, code, ["status", "retirement_status", "retirement_date"], as_dict=True)
	if not status:
		return False
	if status.status == "Retired":
		return False
	if status.retirement_status == "Scheduled" and status.retirement_date and getdate(status.retirement_date) <= getdate(today()):
		return False
	return True


def process_scheduled_retirements():
	if not frappe.db.table_exists(PRODUCT_DOCTYPE):
		return
	products = frappe.get_all(
		PRODUCT_DOCTYPE,
		filters={"retirement_status": "Scheduled", "retirement_date": ["<=", today()]},
		fields=["name"],
	)
	for p in products:
		doc = frappe.get_doc(PRODUCT_DOCTYPE, p.name)
		previous_status = doc.status
		doc.status = "Retired"
		doc.retirement_status = "Retired"
		doc.save()
		_write_retirement_log(doc, "Retired", previous_status, doc.status, doc.retirement_date, doc.retirement_date)
		frappe.publish_realtime("product_retired", {"product": doc.name})
	if products:
		frappe.db.commit()


@frappe.whitelist()
def delete_product(code):
	_assert_editor()
	frappe.delete_doc(PRODUCT_DOCTYPE, code, ignore_permissions=False)
	frappe.db.commit()
	return {"deleted": code}


# ── Pricing calculator ────────────────────────────────────────────

def _pick_tier(tiers, tenor, segment=None):
	tenor = cint(tenor)
	candidates = []
	for t in tiers or []:
		tf = cint(t.get("tenor_from") or 0)
		tt = cint(t.get("tenor_to") or 0) or 10**9
		if tf <= tenor <= tt:
			seg_match = 2 if (segment and (t.get("segment") or "").lower() == segment.lower()) else 1
			candidates.append((seg_match, t))
	if not candidates:
		return None
	candidates.sort(key=lambda x: -x[0])
	return candidates[0][1]


def _emi(principal, annual_rate_pct, months, rate_type="Effective"):
	principal = flt(principal)
	r = flt(annual_rate_pct) / 100.0
	n = cint(months)
	if n <= 0:
		return 0.0
	if rate_type == "Flat":
		total = principal + principal * r * (n / 12.0)
		return total / n
	monthly = r / 12.0
	if monthly == 0:
		return principal / n
	return principal * monthly * ((1 + monthly) ** n) / (((1 + monthly) ** n) - 1)


@frappe.whitelist()
def calculate_quote(payload):
	if isinstance(payload, str):
		payload = json.loads(payload)
	payload = payload or {}

	code = payload.get("product_code")
	amount = flt(payload.get("amount"))
	tenor = cint(payload.get("tenor"))
	segment = payload.get("segment")

	doc = frappe.get_doc(PRODUCT_DOCTYPE, code)
	tiers = [t.as_dict() for t in (doc.interest_tiers or [])]
	tier = _pick_tier(tiers, tenor, segment) or {}

	rate_pct = flt(tier.get("rate_pct")) + flt(tier.get("risk_premium_pct"))
	rate_type = tier.get("rate_type") or "Effective"
	emi = _emi(amount, rate_pct, tenor, rate_type)
	total_payable = emi * tenor
	total_interest = max(0.0, total_payable - amount)

	fee_rows = []
	total_fees = 0.0
	for f in doc.fees or []:
		mode = f.calc_mode or "Fixed"
		val = flt(f.value)
		charge = val if mode == "Fixed" else amount * (val / 100.0)
		if f.min_cap:
			charge = max(charge, flt(f.min_cap))
		if f.max_cap:
			charge = min(charge, flt(f.max_cap))
		fee_rows.append({
			"fee_type": f.fee_type,
			"trigger_event": f.trigger_event,
			"mode": mode,
			"value": val,
			"charge": charge,
		})
		total_fees += charge

	apr = 0.0
	if amount > 0 and tenor > 0:
		apr = ((total_interest + total_fees) / amount) * (12.0 / tenor) * 100.0

	return {
		"product_code": code,
		"product_name": doc.product_name,
		"rate_pct": rate_pct,
		"rate_type": rate_type,
		"tier_used": tier,
		"emi": emi,
		"total_interest": total_interest,
		"total_payable": total_payable,
		"total_fees": total_fees,
		"apr": apr,
		"currency": doc.currency or "IDR",
		"fees": fee_rows,
	}


# ── Analytics ─────────────────────────────────────────────────────

@frappe.whitelist()
def get_product_analytics():
	products = frappe.get_all(
		PRODUCT_DOCTYPE,
		fields=["name", "product_code", "product_name", "product_type", "status", "min_amount", "max_amount"],
		order_by="modified desc",
	)

	app_doctype = "CRM Credit Application"
	if frappe.db.table_exists(app_doctype):
		fields_meta = frappe.get_meta(app_doctype)
	else:
		fields_meta = None

	per_product = []
	for p in products:
		row = {
			"name": p.name,
			"product_code": p.product_code,
			"product_name": p.product_name,
			"status": p.status,
			"applications": 0,
			"approvals": 0,
			"disbursements": 0,
			"avg_ticket": 0.0,
			"npl_pct": 0.0,
		}
		if fields_meta and fields_meta.has_field("facility_type"):
			apps = frappe.get_all(
				app_doctype,
				filters={"facility_type": p.product_name or p.product_code},
				fields=["status", "requested_amount"],
			) or []
			row["applications"] = len(apps)
			row["approvals"] = sum(1 for a in apps if (a.get("status") or "").lower() in ("approved", "active"))
			row["disbursements"] = sum(1 for a in apps if (a.get("status") or "").lower() == "active")
			amounts = [flt(a.get("requested_amount")) for a in apps if a.get("requested_amount")]
			row["avg_ticket"] = (sum(amounts) / len(amounts)) if amounts else 0.0
		per_product.append(row)

	totals = {
		"products": len(per_product),
		"active": sum(1 for p in products if (p.status or "").lower() == "active"),
		"draft": sum(1 for p in products if (p.status or "").lower() == "draft"),
		"pending": sum(1 for p in products if (p.status or "").lower() == "pending approval"),
		"retired": sum(1 for p in products if (p.status or "").lower() == "retired"),
		"applications": sum(p["applications"] for p in per_product),
	}
	return {"totals": totals, "per_product": per_product}


@frappe.whitelist()
def get_pending_approvals():
	rows = frappe.get_all(
		PRODUCT_DOCTYPE,
		filters={"status": "Pending Approval"},
		fields=["name", "product_code", "product_name", "product_type", "currency", "modified", "owner", "version"],
		order_by="modified desc",
	)
	return rows


@frappe.whitelist()
def export_catalog_csv(filters=None):
	data = get_product_catalog(filters=filters)
	buf = io.StringIO()
	writer = csv.writer(buf)
	writer.writerow([
		"Code", "Name", "Type", "Status", "Currency",
		"Min Amount", "Max Amount", "Min Tenor", "Max Tenor",
		"Version", "Effective Date", "Retirement Date", "Has Collateral",
	])
	for r in data["rows"]:
		writer.writerow([
			r.get("product_code"), r.get("product_name"), r.get("product_type"), r.get("status"),
			r.get("currency"),
			r.get("min_amount"), r.get("max_amount"),
			r.get("min_tenor_months"), r.get("max_tenor_months"),
			r.get("version"), r.get("effective_date"), r.get("retirement_date"),
			"Y" if frappe.db.count("CRM Product Collateral Rule", {"parent": r.get("name")}) > 0 else "N",
		])
	return {"filename": f"products-{nowdate()}.csv", "content": buf.getvalue()}


@frappe.whitelist()
def list_form_templates(product_type=None, status=None):
	if not frappe.db.table_exists("CRM Product Form Template"):
		return {"templates": []}
	filters = {}
	if status:
		filters["status"] = status
	if product_type:
		filters["applies_to_product_type"] = ["in", [product_type, "Any"]]
	templates = frappe.get_all(
		"CRM Product Form Template",
		filters=filters,
		fields=["name", "template_name", "applies_to_product_type", "status", "modified"],
		order_by="modified desc",
	)
	for t in templates:
		t["field_count"] = frappe.db.count("CRM Product Form Template Field", {"parent": t.name})
		t["product_usage"] = frappe.db.count(PRODUCT_DOCTYPE, {"form_template": t.name})
	return {"templates": templates}


@frappe.whitelist()
def get_form_template(name):
	doc = frappe.get_doc("CRM Product Form Template", name)
	fields = []
	for f in doc.fields or []:
		fields.append({
			"name": f.name,
			"label": f.label,
			"fieldname": f.fieldname,
			"fieldtype": f.fieldtype,
			"options": f.options,
			"mandatory": f.mandatory,
			"default_value": f.default_value,
			"placeholder": f.placeholder,
			"visible_if": f.visible_if,
			"validation_regex": f.validation_regex,
			"help_text": f.help_text,
		})
	products = frappe.get_all(PRODUCT_DOCTYPE, filters={"form_template": name}, fields=["product_code", "product_name"])
	return {
		"name": doc.name,
		"template_name": doc.template_name,
		"applies_to_product_type": doc.applies_to_product_type,
		"status": doc.status,
		"description": doc.description,
		"fields": fields,
		"products": products,
	}


@frappe.whitelist()
def upsert_form_template(payload):
	_assert_editor()
	if isinstance(payload, str):
		payload = json.loads(payload)
	name = (payload.get("name") or "").strip()
	template_name = (payload.get("template_name") or "").strip()
	if not template_name:
		frappe.throw(_("Template name is required."))
	if name:
		doc = frappe.get_doc("CRM Product Form Template", name)
	else:
		if frappe.db.exists("CRM Product Form Template", template_name):
			frappe.throw(_("Template name already exists."))
		doc = frappe.new_doc("CRM Product Form Template")
		doc.template_name = template_name
	doc.applies_to_product_type = payload.get("applies_to_product_type") or doc.applies_to_product_type or "Any"
	doc.status = payload.get("status") or doc.status or "Draft"
	doc.description = payload.get("description") or doc.description or ""
	if "fields" in payload:
		doc.set("fields", [])
		for row in payload.get("fields") or []:
			if isinstance(row, dict):
				doc.append("fields", row)
	doc.save(ignore_permissions=False)
	frappe.db.commit()
	return get_form_template(doc.name)


@frappe.whitelist()
def clone_form_template(name, new_name):
	_assert_editor()
	if not new_name:
		frappe.throw(_("New name is required."))
	if frappe.db.exists("CRM Product Form Template", new_name):
		frappe.throw(_("Name already exists."))
	src = frappe.get_doc("CRM Product Form Template", name)
	clone = frappe.copy_doc(src)
	clone.template_name = new_name
	clone.status = "Draft"
	clone.insert(ignore_permissions=False)
	frappe.db.commit()
	return get_form_template(clone.name)


@frappe.whitelist()
def activate_form_template(name):
	_assert_editor()
	doc = frappe.get_doc("CRM Product Form Template", name)
	if not doc.fields:
		frappe.throw(_("A template must have at least one field to be activated."))
	doc.status = "Active"
	doc.save()
	frappe.db.commit()
	return {"status": "Active"}


@frappe.whitelist()
def retire_form_template(name):
	_assert_editor()
	doc = frappe.get_doc("CRM Product Form Template", name)
	doc.status = "Retired"
	doc.save()
	frappe.db.commit()
	return {"status": "Retired"}


@frappe.whitelist()
def preview_form_template(name, sample_payload=None):
	if isinstance(sample_payload, str):
		sample_payload = json.loads(sample_payload)
	sample = sample_payload or {}
	template = get_form_template(name)
	rendered = []
	for f in template.get("fields") or []:
		visible = True
		vif = f.get("visible_if") or ""
		if vif:
			parts = vif.split()
			if len(parts) == 3:
				ref_val = sample.get(parts[0])
				operator = parts[1]
				expected = parts[2]
				if operator == "==":
					visible = str(ref_val) == expected
				elif operator == "!=":
					visible = str(ref_val) != expected
				elif operator == "set":
					visible = bool(ref_val)
			err = None
			regex = f.get("validation_regex") or ""
			if regex:
				import re
				try:
					if not re.match(regex, str(sample.get(f["fieldname"]) or "")):
						err = "Validation failed"
				except Exception:
					pass
		rendered.append({**f, "visible": visible, "error": err})
	return {"fields": rendered}


@frappe.whitelist()
def evaluate_collateral_requirement(product_code, facility_amount, collaterals):
	if isinstance(collaterals, str):
		collaterals = json.loads(collaterals)
	collaterals = collaterals or []
	product = frappe.get_doc(PRODUCT_DOCTYPE, product_code)
	facility_amount = flt(facility_amount)
	gaps = []
	if not product.collateral_rules:
		return {"satisfied": True, "gaps": []}
	for rule in product.collateral_rules:
		rule = rule.as_dict()
		matches = [c for c in collaterals if (c.get("collateral_type") or "").lower() == (rule.get("collateral_type") or "").lower()]
		total_coverage = sum(flt(c.get("value") or 0) for c in matches)
		if rule.get("mandatory") and not matches:
			gaps.append({"type": rule.get("collateral_type"), "reason": "Mandatory collateral missing"})
			continue
		if rule.get("min_coverage_pct") and facility_amount > 0:
			coverage_pct = (total_coverage / facility_amount) * 100
			if coverage_pct < flt(rule.get("min_coverage_pct")):
				gaps.append({"type": rule.get("collateral_type"), "reason": f"Coverage {coverage_pct:.1f}% < required {rule.get('min_coverage_pct')}%"})
	return {"satisfied": len(gaps) == 0, "gaps": gaps}
