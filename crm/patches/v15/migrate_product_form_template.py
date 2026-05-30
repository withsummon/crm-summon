import frappe


def execute():
	if not frappe.db.table_exists("CRM Product"):
		return
	if not frappe.db.table_exists("CRM Product Form Template"):
		return

	products = frappe.get_all("CRM Product", fields=["name", "form_template"])
	for p in products:
		val = p.form_template
		if not val:
			continue
		if frappe.db.exists("CRM Product Form Template", val):
			continue
		try:
			tmpl = frappe.new_doc("CRM Product Form Template")
			tmpl.template_name = val
			tmpl.status = "Draft"
			tmpl.applies_to_product_type = "Any"
			tmpl.insert(ignore_permissions=True)
		except Exception:
			pass
