import json
from collections import Counter

import frappe
from frappe import _
from frappe.query_builder import Case, DocType
from frappe.query_builder.functions import Avg, Coalesce, Count, Date, DateFormat, IfNull, Sum
from frappe.utils import cstr, flt
from pypika.functions import Function

from crm.fcrm.doctype.crm_dashboard.crm_dashboard import create_default_manager_dashboard
from crm.utils import sales_user_only


# Custom function for TIMESTAMPDIFF (MySQL/MariaDB)
class TimestampDiff(Function):
	def __init__(self, unit, start, end, **kwargs):
		super().__init__("TIMESTAMPDIFF", unit, start, end, **kwargs)


@frappe.whitelist()
def reset_to_default():
	frappe.only_for("System Manager", True)
	create_default_manager_dashboard(force=True)


@frappe.whitelist()
@sales_user_only
def get_dashboard(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get the dashboard data for the CRM dashboard.
	"""

	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	roles = frappe.get_roles(frappe.session.user)
	is_sales_manager = "Sales Manager" in roles or "System Manager" in roles
	is_sales_user = "Sales User" in roles and not is_sales_manager

	if is_sales_user:
		user = frappe.session.user

	dashboard = frappe.db.exists("CRM Dashboard", "Manager Dashboard")

	layout = []

	if not dashboard:
		layout = json.loads(create_default_manager_dashboard())
		frappe.db.commit()
	else:
		layout = json.loads(frappe.db.get_value("CRM Dashboard", "Manager Dashboard", "layout") or "[]")

	for l in layout:
		method_name = f"get_{l['name']}"
		if hasattr(frappe.get_attr("crm.api.dashboard"), method_name):
			method = getattr(frappe.get_attr("crm.api.dashboard"), method_name)
			l["data"] = method(from_date, to_date, user)
		else:
			l["data"] = None

	return layout


@frappe.whitelist()
@sales_user_only
def get_bni_crm_dashboard(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""Return lead-gen-centric dashboard payload for the BNI teal CRM workspace."""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	roles = frappe.get_roles(frappe.session.user)
	if "Sales User" in roles and "Sales Manager" not in roles and "System Manager" not in roles:
		user = frappe.session.user

	lead_gen = _lead_gen_dashboard(from_date, to_date, user)
	lead_count = _count_doctype("CRM Lead", from_date, to_date, "lead_owner", user)
	prev_lead_count = _count_doctype(
		"CRM Lead",
		frappe.utils.add_days(from_date, -max(frappe.utils.date_diff(to_date, from_date), 1)),
		frappe.utils.add_days(from_date, -1),
		"lead_owner",
		user,
	)
	company_count = lead_gen["overview"]["active_banks"]
	prev_company_count = _count_distinct_lead_field(
		"organization",
		frappe.utils.add_days(from_date, -max(frappe.utils.date_diff(to_date, from_date), 1)),
		frappe.utils.add_days(from_date, -1),
		user,
	)
	pending_followups = lead_gen["follow_up_load"]["pending"]
	prev_followups = _count_lead_tasks(
		frappe.utils.add_days(from_date, -max(frappe.utils.date_diff(to_date, from_date), 1)),
		frappe.utils.add_days(from_date, -1),
		user,
		statuses=("Todo", "Backlog", "In Progress"),
	)
	active_pics = lead_gen["overview"]["active_pics"]
	prev_pics = _count_distinct_lead_field(
		"referrer",
		frappe.utils.add_days(from_date, -max(frappe.utils.date_diff(to_date, from_date), 1)),
		frappe.utils.add_days(from_date, -1),
		user,
		extra_filters=[["referrer", "!=", ""]],
	)

	return {
		"last_updated": frappe.utils.now(),
		"metrics": [
			{"label": "Imported Leads", "value": lead_count, "change": _pct_delta(lead_count, prev_lead_count), "caption": "vs periode sebelumnya", "icon": "users"},
			{"label": "Active Banks", "value": company_count, "change": _pct_delta(company_count, prev_company_count), "caption": "company coverage", "icon": "building-2"},
			{"label": "Pending Follow-up", "value": pending_followups, "change": _pct_delta(pending_followups, prev_followups), "caption": "task backlog", "icon": "check-square"},
			{"label": "Active PIC", "value": active_pics, "change": _pct_delta(active_pics, prev_pics), "caption": "referrer / PIC mapped", "icon": "user-check"},
		],
		"revenue": {
			"total": lead_count,
			"change": _pct_delta(lead_count, prev_lead_count),
			"months": lead_gen["company_breakdown"][:12],
		},
		"calendar": _dashboard_events(from_date, to_date),
		"lead_management": _lead_management(from_date, to_date, user),
		"lead_gen": lead_gen,
		"regions": [{"region": row["label"], "customers": row["count"], "percent": row["percent"]} for row in lead_gen["company_breakdown"][:6]],
		"top_branches": [{"branch": row["label"], "percent": row["percent"], "customers": row["count"]} for row in lead_gen["company_breakdown"][:4]],
		"retention": {"months": lead_gen["status_funnel"]["trend"], "segments": lead_gen["follow_up_load"]["status_rows"]},
	}


def _count_distinct_lead_field(fieldname: str, from_date, to_date, user: str | None = None, extra_filters=None):
	if not _table_exists("CRM Lead") or not _meta_has_field("CRM Lead", fieldname):
		return 0
	filters = _date_range_filter(from_date, to_date)
	if user and _meta_has_field("CRM Lead", "lead_owner"):
		filters.append(["lead_owner", "=", user])
	for filter_row in extra_filters or []:
		filters.append(filter_row)
	try:
		rows = frappe.get_all("CRM Lead", fields=[fieldname], filters=filters, limit=0)
	except Exception:
		return 0
	values = {cstr(row.get(fieldname)).strip() for row in rows if cstr(row.get(fieldname)).strip()}
	return len(values)


def _count_lead_tasks(from_date, to_date, user: str | None = None, statuses=None):
	if not _table_exists("CRM Task"):
		return 0
	filters = [
		["creation", ">=", from_date],
		["creation", "<", frappe.utils.add_days(to_date, 1)],
		["reference_doctype", "=", "CRM Lead"],
	]
	if statuses:
		filters.append(["status", "in", list(statuses)])
	if user and _meta_has_field("CRM Task", "assigned_to"):
		filters.append(["assigned_to", "=", user])
	try:
		return frappe.db.count("CRM Task", filters=filters)
	except Exception:
		return 0


def _lead_task_rows(from_date, to_date, user: str | None = None):
	if not _table_exists("CRM Task"):
		return []
	filters = [
		["creation", ">=", from_date],
		["creation", "<", frappe.utils.add_days(to_date, 1)],
		["reference_doctype", "=", "CRM Lead"],
	]
	if user and _meta_has_field("CRM Task", "assigned_to"):
		filters.append(["assigned_to", "=", user])
	try:
		return frappe.get_all(
			"CRM Task",
			fields=["name", "title", "status", "assigned_to", "due_date"],
			filters=filters,
			order_by="modified desc",
			limit=100,
		)
	except Exception:
		return []


def _lead_gen_dashboard(from_date, to_date, user: str | None = None):
	company_breakdown = _group_count("CRM Lead", "organization", from_date, to_date, user, "lead_owner", limit=12)
	pic_ownership = _group_count("CRM Lead", "referrer", from_date, to_date, user, "lead_owner", limit=8)
	funnel = get_lead_funnel(from_date, to_date, user)
	task_rows = _lead_task_rows(from_date, to_date, user)
	task_status_counts = Counter(row.get("status") or _("Unassigned") for row in task_rows)

	return {
		"overview": {
			"active_banks": len(company_breakdown),
			"active_pics": len(pic_ownership),
			"converted": funnel.get("converted", 0),
			"conversion_rate": funnel.get("conversion_rate", 0),
		},
		"company_breakdown": company_breakdown,
		"pic_ownership": pic_ownership,
		"follow_up_load": {
			"pending": sum(task_status_counts.get(status, 0) for status in ("Todo", "Backlog", "In Progress")),
			"completed": task_status_counts.get("Done", 0),
			"status_rows": [
				{"label": label, "count": count, "percent": round((count / (len(task_rows) or 1)) * 100)}
				for label, count in task_status_counts.items()
			],
			"tasks": task_rows[:10],
		},
		"status_funnel": {
			"rows": funnel.get("stages", []),
			"trend": [
				{"label": row.get("status") or _("Unassigned"), "value": row.get("count", 0)}
				for row in funnel.get("stages", [])[:7]
			],
		},
	}


def _table_exists(doctype: str) -> bool:
	try:
		return frappe.db.table_exists(doctype)
	except Exception:
		return False


def _meta_has_field(doctype: str, fieldname: str) -> bool:
	if not _table_exists(doctype):
		return False
	try:
		return frappe.get_meta(doctype).has_field(fieldname)
	except Exception:
		return False


def _date_range_filter(from_date, to_date):
	return [["creation", ">=", from_date], ["creation", "<", frappe.utils.add_days(to_date, 1)]]


def _count_doctype(doctype: str, from_date, to_date, owner_field: str | None = None, user: str | None = None):
	if not _table_exists(doctype):
		return 0
	filters = _date_range_filter(from_date, to_date)
	if user and owner_field and _meta_has_field(doctype, owner_field):
		filters.append([owner_field, "=", user])
	return frappe.db.count(doctype, filters=filters)


def _deal_owner_condition(user):
	if user and _meta_has_field("CRM Deal", "deal_owner"):
		return " AND deal_owner = %(user)s"
	return ""


def _won_deal_sql_fragment():
	return """
		FROM `tabCRM Deal` deal
		LEFT JOIN `tabCRM Deal Status` status ON status.name = deal.status
		WHERE COALESCE(status.type, '') = 'Won'
		AND DATE(COALESCE(deal.closed_date, deal.modified, deal.creation)) BETWEEN %(from_date)s AND %(to_date)s
	"""


def _won_revenue(from_date, to_date, user: str | None = None):
	if not _table_exists("CRM Deal"):
		return 0
	try:
		rows = frappe.db.sql(
			f"""
			SELECT SUM(COALESCE(deal.deal_value, 0) * COALESCE(deal.exchange_rate, 1)) AS total
			{_won_deal_sql_fragment()}
			{_deal_owner_condition(user)}
			""",
			{"from_date": from_date, "to_date": to_date, "user": user},
			as_dict=True,
		)
		return flt(rows[0].total if rows else 0)
	except Exception:
		return 0


def _won_deal_count(from_date, to_date, user: str | None = None):
	if not _table_exists("CRM Deal"):
		return 0
	try:
		rows = frappe.db.sql(
			f"""
			SELECT COUNT(deal.name) AS total
			{_won_deal_sql_fragment()}
			{_deal_owner_condition(user)}
			""",
			{"from_date": from_date, "to_date": to_date, "user": user},
			as_dict=True,
		)
		return int(rows[0].total if rows else 0)
	except Exception:
		return 0


def _average_cycle_days(from_date, to_date, user: str | None = None):
	if not _table_exists("CRM Deal"):
		return 0
	try:
		rows = frappe.db.sql(
			f"""
			SELECT AVG(GREATEST(DATEDIFF(COALESCE(deal.closed_date, deal.modified), deal.creation), 0)) AS average_days
			{_won_deal_sql_fragment()}
			{_deal_owner_condition(user)}
			""",
			{"from_date": from_date, "to_date": to_date, "user": user},
			as_dict=True,
		)
		return flt(rows[0].average_days if rows else 0)
	except Exception:
		return 0


def _conversion_rate(from_date, to_date, user: str | None = None):
	leads = _count_doctype("CRM Lead", from_date, to_date, "lead_owner", user)
	if not leads:
		return 0
	return (_won_deal_count(from_date, to_date, user) / leads) * 100


def _pct_delta(current, previous):
	current = flt(current)
	previous = flt(previous)
	if not previous:
		return 0
	return ((current - previous) / previous) * 100


def _monthly_revenue(user: str | None = None):
	labels = []
	values_by_month = {}
	start = frappe.utils.get_first_day(frappe.utils.add_months(frappe.utils.nowdate(), -11))
	for offset in range(12):
		month_date = frappe.utils.add_months(start, offset)
		key = frappe.utils.formatdate(month_date, "yyyy-MM")
		labels.append({"key": key, "label": frappe.utils.formatdate(month_date, "MMM")})
		values_by_month[key] = 0

	if _table_exists("CRM Deal"):
		try:
			rows = frappe.db.sql(
				f"""
				SELECT DATE_FORMAT(COALESCE(deal.closed_date, deal.modified, deal.creation), '%%Y-%%m') AS month,
					SUM(COALESCE(deal.deal_value, 0) * COALESCE(deal.exchange_rate, 1)) AS total
				{_won_deal_sql_fragment().replace("BETWEEN %(from_date)s AND %(to_date)s", ">= %(from_date)s")}
				{_deal_owner_condition(user)}
				GROUP BY DATE_FORMAT(COALESCE(deal.closed_date, deal.modified, deal.creation), '%%Y-%%m')
				""",
				{"from_date": start, "to_date": frappe.utils.nowdate(), "user": user},
				as_dict=True,
			)
			for row in rows:
				if row.month in values_by_month:
					values_by_month[row.month] = flt(row.total)
		except Exception:
			pass

	max_value = max(values_by_month.values() or [0]) or 1
	return [
		{"label": row["label"], "value": values_by_month[row["key"]], "height": round(values_by_month[row["key"]] / max_value * 100)}
		for row in labels
	]


def _dashboard_events(from_date, to_date):
	if not _table_exists("Event"):
		return []
	fields = ["name", "subject", "starts_on", "ends_on", "event_type"]
	try:
		return frappe.get_all(
			"Event",
			fields=fields,
			filters=[["starts_on", ">=", from_date], ["starts_on", "<", frappe.utils.add_days(to_date, 1)]],
			order_by="starts_on asc",
			limit=8,
		)
	except Exception:
		return []


def _group_count(doctype: str, fieldname: str, from_date, to_date, user: str | None = None, owner_field: str | None = None, limit: int = 6):
	if not _table_exists(doctype) or not _meta_has_field(doctype, fieldname):
		return []
	filters = _date_range_filter(from_date, to_date)
	if user and owner_field and _meta_has_field(doctype, owner_field):
		filters.append([owner_field, "=", user])
	try:
		rows = frappe.get_all(doctype, fields=[fieldname, "count(name) as count"], filters=filters, group_by=fieldname, order_by="count desc", limit=limit)
	except Exception:
		return []
	total = sum(int(row.count or 0) for row in rows) or 1
	return [
		{"label": row.get(fieldname) or _("Unassigned"), "count": int(row.count or 0), "percent": round((int(row.count or 0) / total) * 100)}
		for row in rows
	]


def _lead_management(from_date, to_date, user: str | None = None):
	lead_filters = _date_range_filter(from_date, to_date)
	if user and _meta_has_field("CRM Lead", "lead_owner"):
		lead_filters.append(["lead_owner", "=", user])

	total_leads = _count_doctype("CRM Lead", from_date, to_date, "lead_owner", user)
	converted_leads = 0
	stale_7 = stale_14 = stale_30 = sla_failed = 0
	if _table_exists("CRM Lead"):
		try:
			converted_leads = frappe.db.count("CRM Lead", filters=lead_filters + [["converted", "=", 1]])
			stale_7 = frappe.db.count("CRM Lead", filters=lead_filters + [["converted", "=", 0], ["modified", "<=", frappe.utils.add_days(frappe.utils.nowdate(), -7)]])
			stale_14 = frappe.db.count("CRM Lead", filters=lead_filters + [["converted", "=", 0], ["modified", "<=", frappe.utils.add_days(frappe.utils.nowdate(), -14)]])
			stale_30 = frappe.db.count("CRM Lead", filters=lead_filters + [["converted", "=", 0], ["modified", "<=", frappe.utils.add_days(frappe.utils.nowdate(), -30)]])
			if _meta_has_field("CRM Lead", "sla_status"):
				sla_failed = frappe.db.count("CRM Lead", filters=lead_filters + [["sla_status", "=", "Failed"]])
		except Exception:
			pass

	return {
		"status": _group_count("CRM Lead", "status", from_date, to_date, user, "lead_owner"),
		"source": _group_count("CRM Lead", "source", from_date, to_date, user, "lead_owner"),
		"campaign": _group_count("CRM Lead", "campaign", from_date, to_date, user, "lead_owner"),
		"score_band": _group_count("CRM Lead", "lead_score_band", from_date, to_date, user, "lead_owner"),
		"channel": _group_count("CRM Lead", "capture_channel", from_date, to_date, user, "lead_owner"),
		"assignment_load": _group_count("CRM Lead", "lead_owner", from_date, to_date, user, "lead_owner"),
		"drop_off_reasons": _group_count("CRM Lead", "lost_reason", from_date, to_date, user, "lead_owner"),
		"qualification": _group_count("CRM Lead", "qualification_status", from_date, to_date, user, "lead_owner")
		or _group_count("CRM Lead", "status", from_date, to_date, user, "lead_owner"),
		"funnel": {
			"total": total_leads,
			"converted": converted_leads,
			"conversion_rate": round((converted_leads / total_leads) * 100, 2) if total_leads else 0,
		},
		"aging": {
			"stale_7_days": stale_7,
			"stale_14_days": stale_14,
			"stale_30_days": stale_30,
			"sla_failed": sla_failed,
		},
	}


def _region_rows(from_date, to_date, user: str | None = None):
	if not _table_exists("Customer"):
		return []
	try:
		rows = frappe.get_all(
			"Customer",
			fields=["territory", "count(name) as customers"],
			filters=_date_range_filter(from_date, to_date),
			group_by="territory",
			order_by="customers desc",
			limit=6,
		)
	except Exception:
		return []
	total = sum(int(row.customers or 0) for row in rows) or 1
	return [
		{"region": row.territory or _("Unassigned"), "customers": int(row.customers or 0), "percent": round((int(row.customers or 0) / total) * 100)}
		for row in rows
	]


def _top_branch_rows(from_date, to_date, user: str | None = None):
	rows = _region_rows(from_date, to_date, user)
	if not rows:
		return []
	return [{"branch": row["region"], "percent": row["percent"], "customers": row["customers"]} for row in rows[:4]]


def _retention_rows(from_date, to_date):
	if not _table_exists("Customer"):
		return {"months": [], "segments": []}
	total_customers = frappe.db.count("Customer") or 1
	start = frappe.utils.get_first_day(frappe.utils.add_months(to_date or frappe.utils.nowdate(), -6))
	months = []
	for offset in range(7):
		month_start = frappe.utils.add_months(start, offset)
		month_end = frappe.utils.get_last_day(month_start)
		active = frappe.db.count(
			"Customer",
			filters=[["modified", ">=", month_start], ["modified", "<", frappe.utils.add_days(month_end, 1)]],
		)
		months.append({"label": frappe.utils.formatdate(month_start, "MMM"), "value": round((active / total_customers) * 100)})
	return {
		"months": months,
		"segments": _group_count("Customer", "customer_group", from_date, to_date, limit=5),
	}


@frappe.whitelist()
@sales_user_only
def get_chart(
	name: str, type: str, from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get number chart data for the dashboard.
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	roles = frappe.get_roles(frappe.session.user)
	is_sales_manager = "Sales Manager" in roles or "System Manager" in roles
	is_sales_user = "Sales User" in roles and not is_sales_manager

	if is_sales_user:
		user = frappe.session.user

	method_name = f"get_{name}"
	if hasattr(frappe.get_attr("crm.api.dashboard"), method_name):
		method = getattr(frappe.get_attr("crm.api.dashboard"), method_name)
		return method(from_date, to_date, user)
	else:
		return {"error": _("Invalid chart name")}


def get_total_leads(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get lead count for the dashboard.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	Lead = DocType("CRM Lead")

	# Build conditions for current period
	current_cond = (Lead.creation >= from_date) & (Lead.creation < to_date_plus_one)
	if user:
		current_cond = current_cond & (Lead.lead_owner == user)

	# Build conditions for previous period
	prev_cond = (Lead.creation >= prev_from_date) & (Lead.creation < from_date)
	if user:
		prev_cond = prev_cond & (Lead.lead_owner == user)

	# Build query with CASE expressions
	query = frappe.qb.from_(Lead).select(
		Count(Case().when(current_cond, Lead.name).else_(None)).as_("current_month_leads"),
		Count(Case().when(prev_cond, Lead.name).else_(None)).as_("prev_month_leads"),
	)

	result = query.run(as_dict=True)

	current_month_leads = result[0].current_month_leads or 0
	prev_month_leads = result[0].prev_month_leads or 0

	delta_in_percentage = (
		(current_month_leads - prev_month_leads) / prev_month_leads * 100 if prev_month_leads else 0
	)

	return {
		"title": _("Total leads"),
		"tooltip": _("Total number of leads"),
		"value": current_month_leads,
		"delta": delta_in_percentage,
		"deltaSuffix": "%",
	}

@frappe.whitelist()
def get_ai_usage_cost(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""Get total AI usage cost recorded in the selected date range."""
	if not frappe.db.table_exists("AI Usage Log"):
		return {
			"title": _("AI API Usage Cost (USD)"),
			"tooltip": _("Total AI Cost in USD"),
			"value": 0.0,
			"prefix": "$",
			"delta": 0,
			"deltaSuffix": "%",
		}
		
	# Sum cost from date range
	result = frappe.db.sql('''
		SELECT SUM(cost) as total_cost
		FROM `tabAI Usage Log`
		WHERE DATE(creation) BETWEEN %s AND %s
	''', (from_date, to_date))
	
	cost = float(result[0][0] or 0.0) if result else 0.0
	
	# Format as string with zero-width space \u200b to bypass frontend compact rounding of small floats
	formatted_value = f"{cost:.4f}\u200b" if cost < 1.0 else round(cost, 2)
	
	return {
		"title": _("AI API Usage Cost (USD)"),
		"tooltip": _("Total AI Cost in USD"),
		"value": formatted_value,
		"prefix": "$",
		"delta": 0,
		"deltaSuffix": "%",
	}

@frappe.whitelist()
def get_ai_usage_trend(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""Return daily AI API cost for an axis chart"""
	from frappe.utils import add_days, date_diff, get_datetime
	
	if not frappe.db.table_exists("AI Usage Log"):
		return {
			"data": [],
			"title": _("AI API Cost Trend"),
			"subtitle": _("Daily AI API Cost in USD"),
			"xAxis": {"title": _("Date"), "key": "date", "type": "time", "timeGrain": "day"},
			"yAxis": {"title": _("Cost (USD)")},
			"series": [{"name": "cost", "type": "line", "showDataPoints": True}]
		}
		
	# Setup date range
	diff = date_diff(to_date, from_date)
	if diff < 0:
		return {
			"data": [],
			"title": _("AI API Cost Trend"),
			"subtitle": _("Daily AI API Cost in USD"),
			"xAxis": {"title": _("Date"), "key": "date", "type": "time", "timeGrain": "day"},
			"yAxis": {"title": _("Cost (USD)")},
			"series": [{"name": "cost", "type": "line", "showDataPoints": True}]
		}
		
	dates = [add_days(from_date, i) for i in range(diff + 1)]
	
	# Fetch logs
	logs = frappe.db.sql('''
		SELECT DATE(creation) as date, SUM(cost) as total_cost
		FROM `tabAI Usage Log`
		WHERE DATE(creation) BETWEEN %s AND %s
		GROUP BY DATE(creation)
	''', (from_date, to_date), as_dict=True)
	
	cost_by_date = {str(log.date): log.total_cost for log in logs if log.date}
	
	chart_data = []
	for d in dates:
		date_str = get_datetime(d).strftime("%Y-%m-%d")
		chart_data.append({
			"date": date_str,
			"cost": round(cost_by_date.get(date_str, 0.0), 6)
		})
		
	return {
		"data": chart_data,
		"title": _("AI API Cost Trend"),
		"subtitle": _("Daily AI API Cost in USD"),
		"xAxis": {
			"title": _("Date"),
			"key": "date",
			"type": "time",
			"timeGrain": "day",
		},
		"yAxis": {
			"title": _("Cost (USD)"),
		},
		"series": [
			{"name": "cost", "type": "line", "showDataPoints": True}
		],
	}

@frappe.whitelist()
def get_ai_usage_cost_idr(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""Get total AI usage cost in IDR for the selected date range."""
	if not frappe.db.table_exists("AI Usage Log"):
		return {
			"title": _("AI API Usage Cost (IDR)"),
			"tooltip": _("Total AI Cost in IDR"),
			"value": 0.0,
			"prefix": "Rp",
			"delta": 0,
			"deltaSuffix": "%",
		}
		
	# Sum cost from date range
	result = frappe.db.sql('''
		SELECT SUM(cost) as total_cost
		FROM `tabAI Usage Log`
		WHERE DATE(creation) BETWEEN %s AND %s
	''', (from_date, to_date))
	
	cost = float(result[0][0] or 0.0) if result else 0.0
	idr_value = round(cost * 17602.25, 2)
	
	return {
		"title": _("AI API Usage Cost (IDR)"),
		"tooltip": _("Total AI Cost in IDR"),
		"value": idr_value,
		"prefix": "Rp",
		"delta": 0,
		"deltaSuffix": "%",
	}

@frappe.whitelist()
def get_ai_usage_trend_idr(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""Return daily AI API cost in IDR for an axis chart"""
	usd_trend = get_ai_usage_trend(from_date, to_date, user)
	idr_data = []
	for row in usd_trend.get("data", []):
		idr_data.append({
			"date": row.get("date"),
			"cost": round((row.get("cost") or 0.0) * 17602.25, 2)
		})
		
	return {
		"data": idr_data,
		"title": _("AI API Cost Trend (IDR)"),
		"subtitle": _("Daily AI API Cost in IDR (Rate: 17.602,95)"),
		"xAxis": {
			"title": _("Date"),
			"key": "date",
			"type": "time",
			"timeGrain": "day",
		},
		"yAxis": {
			"title": _("Cost (IDR)"),
		},
		"series": [
			{"name": "cost", "type": "line", "showDataPoints": True}
		],
	}

def get_ongoing_deals(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get ongoing deal count for the dashboard, and also calculate average deal value for ongoing deals.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")

	# Build conditions for current period
	current_cond = (
		(Deal.creation >= from_date)
		& (Deal.creation < to_date_plus_one)
		& (Status.type.notin(["Won", "Lost"]))
	)
	if user:
		current_cond = current_cond & (Deal.deal_owner == user)

	# Build conditions for previous period
	prev_cond = (
		(Deal.creation >= prev_from_date) & (Deal.creation < from_date) & (Status.type.notin(["Won", "Lost"]))
	)
	if user:
		prev_cond = prev_cond & (Deal.deal_owner == user)

	# Build query with CASE expressions
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.select(
			Count(Case().when(current_cond, Deal.name).else_(None)).as_("current_month_deals"),
			Count(Case().when(prev_cond, Deal.name).else_(None)).as_("prev_month_deals"),
		)
	)

	result = query.run(as_dict=True)

	current_month_deals = result[0].current_month_deals or 0
	prev_month_deals = result[0].prev_month_deals or 0

	delta_in_percentage = (
		(current_month_deals - prev_month_deals) / prev_month_deals * 100 if prev_month_deals else 0
	)

	return {
		"title": _("Ongoing deals"),
		"tooltip": _("Total number of non won/lost deals"),
		"value": current_month_deals,
		"delta": delta_in_percentage,
		"deltaSuffix": "%",
	}


def get_average_ongoing_deal_value(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get ongoing deal count for the dashboard, and also calculate average deal value for ongoing deals.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")

	# Build conditions for current period
	current_cond = (
		(Deal.creation >= from_date)
		& (Deal.creation < to_date_plus_one)
		& (Status.type.notin(["Won", "Lost"]))
	)
	if user:
		current_cond = current_cond & (Deal.deal_owner == user)

	# Build conditions for previous period
	prev_cond = (
		(Deal.creation >= prev_from_date) & (Deal.creation < from_date) & (Status.type.notin(["Won", "Lost"]))
	)
	if user:
		prev_cond = prev_cond & (Deal.deal_owner == user)

	# Calculate deal value with exchange rate
	deal_value_expr = Deal.deal_value * IfNull(Deal.exchange_rate, 1)

	# Build query with CASE expressions
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.select(
			Avg(Case().when(current_cond, deal_value_expr).else_(None)).as_("current_month_avg_value"),
			Avg(Case().when(prev_cond, deal_value_expr).else_(None)).as_("prev_month_avg_value"),
		)
	)

	result = query.run(as_dict=True)

	current_month_avg_value = result[0].current_month_avg_value or 0
	prev_month_avg_value = result[0].prev_month_avg_value or 0

	avg_value_delta = current_month_avg_value - prev_month_avg_value if prev_month_avg_value else 0

	return {
		"title": _("Avg. ongoing deal value"),
		"tooltip": _("Average deal value of non won/lost deals"),
		"value": current_month_avg_value,
		"delta": avg_value_delta,
		"prefix": get_base_currency_symbol(),
	}


def get_won_deals(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get won deal count for the dashboard, and also calculate average deal value for won deals.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")

	# Build conditions for current period
	current_cond = (
		(Deal.closed_date >= from_date) & (Deal.closed_date < to_date_plus_one) & (Status.type == "Won")
	)
	if user:
		current_cond = current_cond & (Deal.deal_owner == user)

	# Build conditions for previous period
	prev_cond = (Deal.closed_date >= prev_from_date) & (Deal.closed_date < from_date) & (Status.type == "Won")
	if user:
		prev_cond = prev_cond & (Deal.deal_owner == user)

	# Build query with CASE expressions
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.select(
			Count(Case().when(current_cond, Deal.name).else_(None)).as_("current_month_deals"),
			Count(Case().when(prev_cond, Deal.name).else_(None)).as_("prev_month_deals"),
		)
	)

	result = query.run(as_dict=True)

	current_month_deals = result[0].current_month_deals or 0
	prev_month_deals = result[0].prev_month_deals or 0

	delta_in_percentage = (
		(current_month_deals - prev_month_deals) / prev_month_deals * 100 if prev_month_deals else 0
	)

	return {
		"title": _("Won deals"),
		"tooltip": _("Total number of won deals based on its closure date"),
		"value": current_month_deals,
		"delta": delta_in_percentage,
		"deltaSuffix": "%",
	}


def get_average_won_deal_value(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get won deal count for the dashboard, and also calculate average deal value for won deals.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")

	# Build conditions for current period
	current_cond = (
		(Deal.closed_date >= from_date) & (Deal.closed_date < to_date_plus_one) & (Status.type == "Won")
	)
	if user:
		current_cond = current_cond & (Deal.deal_owner == user)

	# Build conditions for previous period
	prev_cond = (Deal.closed_date >= prev_from_date) & (Deal.closed_date < from_date) & (Status.type == "Won")
	if user:
		prev_cond = prev_cond & (Deal.deal_owner == user)

	# Calculate deal value with exchange rate
	deal_value_expr = Deal.deal_value * IfNull(Deal.exchange_rate, 1)

	# Build query with CASE expressions
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.select(
			Avg(Case().when(current_cond, deal_value_expr).else_(None)).as_("current_month_avg_value"),
			Avg(Case().when(prev_cond, deal_value_expr).else_(None)).as_("prev_month_avg_value"),
		)
	)

	result = query.run(as_dict=True)

	current_month_avg_value = result[0].current_month_avg_value or 0
	prev_month_avg_value = result[0].prev_month_avg_value or 0

	avg_value_delta = current_month_avg_value - prev_month_avg_value if prev_month_avg_value else 0

	return {
		"title": _("Avg. won deal value"),
		"tooltip": _("Average deal value of won deals"),
		"value": current_month_avg_value,
		"delta": avg_value_delta,
		"prefix": get_base_currency_symbol(),
	}


def get_average_deal_value(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get average deal value for the dashboard.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")

	# Build conditions for current period
	current_cond = (Deal.creation >= from_date) & (Deal.creation < to_date_plus_one) & (Status.type != "Lost")
	if user:
		current_cond = current_cond & (Deal.deal_owner == user)

	# Build conditions for previous period
	prev_cond = (Deal.creation >= prev_from_date) & (Deal.creation < from_date) & (Status.type != "Lost")
	if user:
		prev_cond = prev_cond & (Deal.deal_owner == user)

	# Calculate deal value with exchange rate
	deal_value_expr = Deal.deal_value * IfNull(Deal.exchange_rate, 1)

	# Build query with CASE expressions
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.select(
			Avg(Case().when(current_cond, deal_value_expr).else_(None)).as_("current_month_avg"),
			Avg(Case().when(prev_cond, deal_value_expr).else_(None)).as_("prev_month_avg"),
		)
	)

	result = query.run(as_dict=True)

	current_month_avg = result[0].current_month_avg or 0
	prev_month_avg = result[0].prev_month_avg or 0

	delta = current_month_avg - prev_month_avg if prev_month_avg else 0

	return {
		"title": _("Avg. deal value"),
		"tooltip": _("Average deal value of ongoing & won deals"),
		"value": current_month_avg,
		"prefix": get_base_currency_symbol(),
		"delta": delta,
		"deltaSuffix": "%",
	}


def get_average_time_to_close_a_lead(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get average time to close deals for the dashboard.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)
	prev_to_date = from_date

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")
	Lead = DocType("CRM Lead")

	# Base condition: closed_date is not null and status type is Won
	base_cond = (Deal.closed_date.isnotnull()) & (Status.type == "Won")
	if user:
		base_cond = base_cond & (Deal.deal_owner == user)

	# Current period condition
	current_cond = (Deal.closed_date >= from_date) & (Deal.closed_date < to_date_plus_one)

	# Previous period condition
	prev_cond = (Deal.closed_date >= prev_from_date) & (Deal.closed_date < prev_to_date)

	# Calculate time difference from lead/deal creation to deal closure
	time_diff = TimestampDiff(
		frappe.qb.terms.LiteralValue("DAY"), Coalesce(Lead.creation, Deal.creation), Deal.closed_date
	)

	# Build query
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.left_join(Lead)
		.on(Deal.lead == Lead.name)
		.where(base_cond)
		.select(
			Avg(Case().when(current_cond, time_diff).else_(None)).as_("current_avg_lead"),
			Avg(Case().when(prev_cond, time_diff).else_(None)).as_("prev_avg_lead"),
		)
	)

	result = query.run(as_dict=True)

	current_avg_lead = result[0].current_avg_lead or 0
	prev_avg_lead = result[0].prev_avg_lead or 0
	delta_lead = current_avg_lead - prev_avg_lead if prev_avg_lead else 0

	return {
		"title": _("Avg. time to close a lead"),
		"tooltip": _("Average time taken from lead creation to deal closure"),
		"value": current_avg_lead,
		"suffix": " days",
		"delta": delta_lead,
		"deltaSuffix": " days",
		"negativeIsBetter": True,
	}


def get_average_time_to_close_a_deal(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get average time to close deals for the dashboard.
	"""
	diff = frappe.utils.date_diff(to_date, from_date)
	if diff == 0:
		diff = 1

	prev_from_date = frappe.utils.add_days(from_date, -diff)
	to_date_plus_one = frappe.utils.add_days(to_date, 1)
	prev_to_date = from_date

	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")
	Lead = DocType("CRM Lead")

	# Base condition: closed_date is not null and status type is Won
	base_cond = (Deal.closed_date.isnotnull()) & (Status.type == "Won")
	if user:
		base_cond = base_cond & (Deal.deal_owner == user)

	# Current period condition
	current_cond = (Deal.closed_date >= from_date) & (Deal.closed_date < to_date_plus_one)

	# Previous period condition
	prev_cond = (Deal.closed_date >= prev_from_date) & (Deal.closed_date < prev_to_date)

	# Calculate time difference from deal creation to deal closure
	time_diff = TimestampDiff(frappe.qb.terms.LiteralValue("DAY"), Deal.creation, Deal.closed_date)

	# Build query
	query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.left_join(Lead)
		.on(Deal.lead == Lead.name)
		.where(base_cond)
		.select(
			Avg(Case().when(current_cond, time_diff).else_(None)).as_("current_avg_deal"),
			Avg(Case().when(prev_cond, time_diff).else_(None)).as_("prev_avg_deal"),
		)
	)

	result = query.run(as_dict=True)

	current_avg_deal = result[0].current_avg_deal or 0
	prev_avg_deal = result[0].prev_avg_deal or 0
	delta_deal = current_avg_deal - prev_avg_deal if prev_avg_deal else 0

	return {
		"title": _("Avg. time to close a deal"),
		"tooltip": _("Average time taken from deal creation to deal closure"),
		"value": current_avg_deal,
		"suffix": " days",
		"delta": delta_deal,
		"deltaSuffix": " days",
		"negativeIsBetter": True,
	}


def get_sales_trend(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get sales trend data for the dashboard.
	[
		{ date: new Date('2024-05-01'), leads: 45, deals: 23, won_deals: 12 },
		{ date: new Date('2024-05-02'), leads: 50, deals: 30, won_deals: 15 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	Lead = DocType("CRM Lead")
	Deal = DocType("CRM Deal")
	Status = DocType("CRM Deal Status")

	# Build leads query
	leads_query = (
		frappe.qb.from_(Lead)
		.select(
			Date(Lead.creation).as_("date"),
			Count("*").as_("leads"),
			frappe.qb.terms.ValueWrapper(0).as_("deals"),
			frappe.qb.terms.ValueWrapper(0).as_("won_deals"),
		)
		.where(Date(Lead.creation).between(from_date, to_date))
	)

	if user:
		leads_query = leads_query.where(Lead.lead_owner == user)

	leads_query = leads_query.groupby(Date(Lead.creation))

	# Build deals query
	deals_query = (
		frappe.qb.from_(Deal)
		.join(Status)
		.on(Deal.status == Status.name)
		.select(
			Date(Deal.creation).as_("date"),
			frappe.qb.terms.ValueWrapper(0).as_("leads"),
			Count("*").as_("deals"),
			Sum(Case().when(Status.type == "Won", 1).else_(0)).as_("won_deals"),
		)
		.where(Date(Deal.creation).between(from_date, to_date))
	)

	if user:
		deals_query = deals_query.where(Deal.deal_owner == user)

	deals_query = deals_query.groupby(Date(Deal.creation))

	# Combine with UNION ALL and aggregate by date
	union_query = leads_query.union_all(deals_query)

	# Wrap in outer query to aggregate by date
	daily = (
		frappe.qb.from_(union_query)
		.select(
			DateFormat(union_query.date, "%Y-%m-%d").as_("date"),
			Sum(union_query.leads).as_("leads"),
			Sum(union_query.deals).as_("deals"),
			Sum(union_query.won_deals).as_("won_deals"),
		)
		.groupby(union_query.date)
		.orderby(union_query.date)
	)

	result = daily.run(as_dict=True)

	sales_trend = [
		{
			"date": frappe.utils.get_datetime(row.date).strftime("%Y-%m-%d"),
			"leads": row.leads or 0,
			"deals": row.deals or 0,
			"won_deals": row.won_deals or 0,
		}
		for row in result
	]

	return {
		"data": sales_trend,
		"title": _("Sales trend"),
		"subtitle": _("Daily performance of leads, deals, and wins"),
		"xAxis": {
			"title": _("Date"),
			"key": "date",
			"type": "time",
			"timeGrain": "day",
		},
		"yAxis": {
			"title": _("Count"),
		},
		"series": [
			{"name": "leads", "type": "line", "showDataPoints": True},
			{"name": "deals", "type": "line", "showDataPoints": True},
			{"name": "won_deals", "type": "line", "showDataPoints": True},
		],
	}


def get_forecasted_revenue(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get forecasted revenue for the dashboard.
	[
		{ date: new Date('2024-05-01'), forecasted: 1200000, actual: 980000 },
		{ date: new Date('2024-06-01'), forecasted: 1350000, actual: 1120000 },
		{ date: new Date('2024-07-01'), forecasted: 1600000, actual: "" },
		{ date: new Date('2024-08-01'), forecasted: 1500000, actual: "" },
		...
	]
	"""
	# Using Frappe Query Builder with CASE expressions
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	# Calculate the date 12 months ago
	twelve_months_ago = frappe.utils.add_months(frappe.utils.nowdate(), -12)

	forecasted_value = (
		Case()
		.when(CRMDealStatus.type == "Lost", CRMDeal.expected_deal_value * IfNull(CRMDeal.exchange_rate, 1))
		.else_(
			CRMDeal.expected_deal_value
			* IfNull(CRMDeal.probability, 0)
			/ 100
			* IfNull(CRMDeal.exchange_rate, 1)
		)
	)

	actual_value = (
		Case()
		.when(CRMDealStatus.type == "Won", CRMDeal.deal_value * IfNull(CRMDeal.exchange_rate, 1))
		.else_(0)
	)

	query = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(
			DateFormat(CRMDeal.expected_closure_date, "%Y-%m").as_("month"),
			Sum(forecasted_value).as_("forecasted"),
			Sum(actual_value).as_("actual"),
		)
		.where(CRMDeal.expected_closure_date >= twelve_months_ago)
		.groupby(DateFormat(CRMDeal.expected_closure_date, "%Y-%m"))
		.orderby(DateFormat(CRMDeal.expected_closure_date, "%Y-%m"))
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	for row in result:
		row["month"] = frappe.utils.get_datetime(row["month"]).strftime("%Y-%m-01")
		row["forecasted"] = row["forecasted"] or ""
		row["actual"] = row["actual"] or ""

	return {
		"data": result or [],
		"title": _("Forecasted revenue"),
		"subtitle": _("Projected vs actual revenue based on deal probability"),
		"xAxis": {
			"title": _("Month"),
			"key": "month",
			"type": "time",
			"timeGrain": "month",
		},
		"yAxis": {
			"title": _("Revenue") + f" ({get_base_currency_symbol()})",
		},
		"series": [
			{"name": "forecasted", "type": "line", "showDataPoints": True},
			{"name": "actual", "type": "line", "showDataPoints": True},
		],
	}


def get_funnel_conversion(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get funnel conversion data for the dashboard.
	[
		{ stage: 'Leads', count: 120 },
		{ stage: 'Qualification', count: 100 },
		{ stage: 'Negotiation', count: 80 },
		{ stage: 'Ready to Close', count: 60 },
		{ stage: 'Won', count: 30 },
		...
	]
	"""
	lead_conds = ""
	deal_conds = ""

	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	lead_filters = {"from": from_date, "to": to_date}
	deal_filters = {"from": from_date, "to": to_date}

	if user:
		lead_conds += " AND lead_owner = %(user)s"
		deal_conds += " AND deal_owner = %(user)s"
		lead_filters["user"] = user
		deal_filters["user"] = user

	result = []

	# Get total leads using Query Builder
	CRMLead = DocType("CRM Lead")

	query = (
		frappe.qb.from_(CRMLead)
		.select(Count("*").as_("count"))
		.where(Date(CRMLead.creation).between(from_date, to_date))
	)

	if user:
		query = query.where(CRMLead.lead_owner == user)

	total_leads = query.run(as_dict=True)
	total_leads_count = total_leads[0].count if total_leads else 0

	result.append({"stage": "Leads", "count": total_leads_count})

	result += get_deal_status_change_counts(from_date, to_date, deal_conds, deal_filters)

	return {
		"data": result or [],
		"title": _("Funnel conversion"),
		"subtitle": _("Lead to deal conversion pipeline"),
		"xAxis": {
			"title": _("Stage"),
			"key": "stage",
			"type": "category",
		},
		"yAxis": {
			"title": _("Count"),
		},
		"swapXY": True,
		"series": [
			{
				"name": "count",
				"type": "bar",
				"echartOptions": {
					"colorBy": "data",
				},
			},
		],
	}


def get_deals_by_stage_axis(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get deal data by stage for the dashboard.
	[
		{ stage: 'Prospecting', count: 120 },
		{ stage: 'Negotiation', count: 45 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder with NOT IN clause
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	query = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(CRMDeal.status.as_("stage"), Count("*").as_("count"), CRMDealStatus.type.as_("status_type"))
		.where((Date(CRMDeal.creation).between(from_date, to_date)) & (CRMDealStatus.type.notin(["Lost"])))
		.groupby(CRMDeal.status)
		.orderby(Count("*"), order=frappe.qb.desc)
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Deals by ongoing & won stage"),
		"xAxis": {
			"title": _("Stage"),
			"key": "stage",
			"type": "category",
		},
		"yAxis": {"title": _("Count")},
		"series": [
			{"name": "count", "type": "bar"},
		],
	}


def get_deals_by_stage_donut(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get deal data by stage for the dashboard.
	[
		{ stage: 'Prospecting', count: 120 },
		{ stage: 'Negotiation', count: 45 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder with JOIN
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	query = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(CRMDeal.status.as_("stage"), Count("*").as_("count"), CRMDealStatus.type.as_("status_type"))
		.where(Date(CRMDeal.creation).between(from_date, to_date))
		.groupby(CRMDeal.status)
		.orderby(Count("*"), order=frappe.qb.desc)
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Deals by stage"),
		"subtitle": _("Current pipeline distribution"),
		"categoryColumn": "stage",
		"valueColumn": "count",
	}


def get_lost_deal_reasons(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get lost deal reasons for the dashboard.
	[
		{ reason: 'Price too high', count: 20 },
		{ reason: 'Competitor won', count: 15 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder with JOIN
	CRMDeal = DocType("CRM Deal")
	CRMDealStatus = DocType("CRM Deal Status")

	query = (
		frappe.qb.from_(CRMDeal)
		.join(CRMDealStatus)
		.on(CRMDeal.status == CRMDealStatus.name)
		.select(CRMDeal.lost_reason.as_("reason"), Count("*").as_("count"))
		.where((Date(CRMDeal.creation).between(from_date, to_date)) & (CRMDealStatus.type == "Lost"))
		.groupby(CRMDeal.lost_reason)
		.having((CRMDeal.lost_reason.isnotnull()) & (CRMDeal.lost_reason != ""))
		.orderby(Count("*"), order=frappe.qb.desc)
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Lost deal reasons"),
		"subtitle": _("Common reasons for losing deals"),
		"xAxis": {
			"title": _("Reason"),
			"key": "reason",
			"type": "category",
		},
		"yAxis": {
			"title": _("Count"),
		},
		"series": [
			{"name": "count", "type": "bar"},
		],
	}


def get_leads_by_source(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get lead data by source for the dashboard.
	[
		{ source: 'Website', count: 120 },
		{ source: 'Referral', count: 45 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder (safer, more maintainable)
	CRMLead = DocType("CRM Lead")

	query = (
		frappe.qb.from_(CRMLead)
		.select(IfNull(CRMLead.source, "Empty").as_("source"), Count("*").as_("count"))
		.where(Date(CRMLead.creation).between(from_date, to_date))
		.groupby(CRMLead.source)
		.orderby(Count("*"), order=frappe.qb.desc)
	)

	if user:
		query = query.where(CRMLead.lead_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Leads by source"),
		"subtitle": _("Lead generation channel analysis"),
		"categoryColumn": "source",
		"valueColumn": "count",
	}


def get_deals_by_source(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get deal data by source for the dashboard.
	[
		{ source: 'Website', count: 120 },
		{ source: 'Referral', count: 45 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder
	CRMDeal = DocType("CRM Deal")

	query = (
		frappe.qb.from_(CRMDeal)
		.select(IfNull(CRMDeal.source, "Empty").as_("source"), Count("*").as_("count"))
		.where(Date(CRMDeal.creation).between(from_date, to_date))
		.groupby(CRMDeal.source)
		.orderby(Count("*"), order=frappe.qb.desc)
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Deals by source"),
		"subtitle": _("Deal generation channel analysis"),
		"categoryColumn": "source",
		"valueColumn": "count",
	}


def get_deals_by_territory(from_date: str | None = None, to_date: str | None = None, user: str | None = None):
	"""
	Get deal data by territory for the dashboard.
	[
		{ territory: 'North America', deals: 45, value: 2300000 },
		{ territory: 'Europe', deals: 30, value: 1500000 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder with complex aggregations
	CRMDeal = DocType("CRM Deal")

	query = (
		frappe.qb.from_(CRMDeal)
		.select(
			IfNull(CRMDeal.territory, "Empty").as_("territory"),
			Count("*").as_("deals"),
			Sum(Coalesce(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)).as_("value"),
		)
		.where(Date(CRMDeal.creation).between(from_date, to_date))
		.groupby(CRMDeal.territory)
		.orderby(Count("*"), order=frappe.qb.desc)
		.orderby(
			Sum(Coalesce(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)), order=frappe.qb.desc
		)
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Deals by territory"),
		"subtitle": _("Geographic distribution of deals and revenue"),
		"xAxis": {
			"title": _("Territory"),
			"key": "territory",
			"type": "category",
		},
		"yAxis": {
			"title": _("Number of deals"),
		},
		"y2Axis": {
			"title": _("Deal value") + f" ({get_base_currency_symbol()})",
		},
		"series": [
			{"name": "deals", "type": "bar"},
			{"name": "value", "type": "line", "showDataPoints": True, "axis": "y2"},
		],
	}


def get_deals_by_salesperson(
	from_date: str | None = None, to_date: str | None = None, user: str | None = None
):
	"""
	Get deal data by salesperson for the dashboard.
	[
		{ salesperson: 'John Smith', deals: 45, value: 2300000 },
		{ salesperson: 'Jane Doe', deals: 30, value: 1500000 },
		...
	]
	"""
	if not from_date or not to_date:
		from_date = frappe.utils.get_first_day(from_date or frappe.utils.nowdate())
		to_date = frappe.utils.get_last_day(to_date or frappe.utils.nowdate())

	# Using Frappe Query Builder with LEFT JOIN
	CRMDeal = DocType("CRM Deal")
	User = DocType("User")

	query = (
		frappe.qb.from_(CRMDeal)
		.left_join(User)
		.on(User.name == CRMDeal.deal_owner)
		.select(
			IfNull(User.full_name, CRMDeal.deal_owner).as_("salesperson"),
			Count("*").as_("deals"),
			Sum(Coalesce(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)).as_("value"),
		)
		.where(Date(CRMDeal.creation).between(from_date, to_date))
		.groupby(CRMDeal.deal_owner)
		.orderby(Count("*"), order=frappe.qb.desc)
		.orderby(
			Sum(Coalesce(CRMDeal.deal_value, 0) * IfNull(CRMDeal.exchange_rate, 1)), order=frappe.qb.desc
		)
	)

	if user:
		query = query.where(CRMDeal.deal_owner == user)

	result = query.run(as_dict=True)

	return {
		"data": result or [],
		"title": _("Deals by salesperson"),
		"subtitle": _("Number of deals and total value per salesperson"),
		"xAxis": {
			"title": _("Salesperson"),
			"key": "salesperson",
			"type": "category",
		},
		"yAxis": {
			"title": _("Number of deals"),
		},
		"y2Axis": {
			"title": _("Deal value") + f" ({get_base_currency_symbol()})",
		},
		"series": [
			{"name": "deals", "type": "bar"},
			{"name": "value", "type": "line", "showDataPoints": True, "axis": "y2"},
		],
	}


def get_base_currency_symbol():
	"""
	Get the base currency symbol from the system settings.
	"""
	base_currency = (
		frappe.db.get_single_value("FCRM Settings", "currency")
		or frappe.db.get_default("currency")
		or "USD"
	)
	return frappe.db.get_value("Currency", base_currency, "symbol") or ""


def get_deal_status_change_counts(
	from_date: str | None = None,
	to_date: str | None = None,
	deal_conds: str = "",
	filters: dict | None = None,
):
	"""
	Get count of each status change (to) for each deal, excluding deals with current status type 'Lost'.
	Order results by status position.
	Returns:
	[
	  {"status": "Qualification", "count": 120},
	  {"status": "Negotiation", "count": 85},
	  ...
	]
	"""
	# Using Frappe Query Builder with multiple JOINs and table aliases
	CRMStatusChangeLog = DocType("CRM Status Change Log")
	CRMDeal = DocType("CRM Deal")
	CurrentStatus = DocType("CRM Deal Status").as_("s")
	TargetStatus = DocType("CRM Deal Status").as_("st")

	query = (
		frappe.qb.from_(CRMStatusChangeLog)
		.join(CRMDeal)
		.on(CRMStatusChangeLog.parent == CRMDeal.name)
		.join(CurrentStatus)
		.on(CRMDeal.status == CurrentStatus.name)
		.join(TargetStatus)
		.on(CRMStatusChangeLog.to == TargetStatus.name)
		.select(CRMStatusChangeLog.to.as_("stage"), Count("*").as_("count"))
		.where(
			(CRMStatusChangeLog.to.isnotnull())
			& (CRMStatusChangeLog.to != "")
			& (CurrentStatus.type != "Lost")
			& (Date(CRMDeal.creation).between(from_date, to_date))
		)
		.groupby(CRMStatusChangeLog.to, TargetStatus.position)
		.orderby(TargetStatus.position)
	)

	# Handle optional user filter if deal_conds contains user condition
	if filters and filters.get("user"):
		query = query.where(CRMDeal.deal_owner == filters["user"])

	result = query.run(as_dict=True)
	return result or []
