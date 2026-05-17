import frappe
frappe.init(site='crm.summon.localhost')
frappe.connect()
leads = frappe.db.sql("SELECT name, lead_name, status, creation FROM `tabCRM Lead` WHERE status = 'Qualified'", as_dict=True)
for l in leads:
    print(f"- {l.lead_name} (Status: {l.status})")
