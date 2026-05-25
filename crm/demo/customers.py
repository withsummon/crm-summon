import frappe

DEMO_CUSTOMERS = [
	{
		"customer_name": "PT Maju Jaya",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Technology",
		"website": "https://majujaya.example.com",
		"mobile_no": "+62 812 0001 0001",
		"email_id": "info@majujaya.example.com",
	},
	{
		"customer_name": "PT Industri Nusantara",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Manufacturing",
		"website": "https://industrinusantara.example.com",
		"mobile_no": "+62 813 0002 0002",
		"email_id": "info@industrinusantara.example.com",
	},
	{
		"customer_name": "CV Cahaya Terang",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Consulting",
		"website": "https://cahayaterang.example.com",
		"mobile_no": "+62 821 0003 0003",
		"email_id": "info@cahayaterang.example.com",
	},
	{
		"customer_name": "PT Teknologi Maju",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Technology",
		"website": "https://teknologimaju.example.com",
		"mobile_no": "+62 878 0004 0004",
		"email_id": "info@teknologimaju.example.com",
	},
	{
		"customer_name": "PT Awan Digital",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Technology",
		"website": "https://awandigital.example.com",
		"mobile_no": "+62 856 0005 0005",
		"email_id": "info@awandigital.example.com",
	},
	{
		"customer_name": "PT Gelombang Baru",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Telecommunications",
		"website": "https://gelombangbaru.example.com",
		"mobile_no": "+62 877 0006 0006",
		"email_id": "info@gelombangbaru.example.com",
	},
	{
		"customer_name": "PT Solusi Pivotindo",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Technology",
		"website": "https://solusipivotindo.example.com",
		"mobile_no": "+62 811 0007 0007",
		"email_id": "info@solusipivotindo.example.com",
	},
	{
		"customer_name": "PT Sistem Meridian",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Financial Services",
		"website": "https://sistemmeridian.example.com",
		"mobile_no": "+62 852 0008 0008",
		"email_id": "info@sistemmeridian.example.com",
	},
	{
		"customer_name": "PT Analitika Verteks",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Financial Services",
		"website": "https://analitikaverteks.example.com",
		"mobile_no": "+62 814 0009 0009",
		"email_id": "info@analitikaverteks.example.com",
	},
	{
		"customer_name": "PT Forge Digital",
		"customer_type": "Company",
		"customer_group": "Commercial",
		"territory": "Indonesia",
		"industry": "Advertising",
		"website": "https://forgedigital.example.com",
		"mobile_no": "+62 831 0010 0010",
		"email_id": "info@forgedigital.example.com",
	},
]

DEMO_CUSTOMER_NAMES = [c["customer_name"] for c in DEMO_CUSTOMERS]


def _ensure_masters():
	if not frappe.db.exists("Customer Group", "All Customer Groups"):
		frappe.get_doc({
			"doctype": "Customer Group",
			"customer_group_name": "All Customer Groups",
			"is_group": 1,
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Customer Group", "Commercial"):
		frappe.get_doc({
			"doctype": "Customer Group",
			"customer_group_name": "Commercial",
			"parent_customer_group": "All Customer Groups",
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Territory", "All Territories"):
		frappe.get_doc({
			"doctype": "Territory",
			"territory_name": "All Territories",
			"is_group": 1,
		}).insert(ignore_permissions=True)

	if not frappe.db.exists("Territory", "Indonesia"):
		frappe.get_doc({
			"doctype": "Territory",
			"territory_name": "Indonesia",
			"parent_territory": "All Territories",
		}).insert(ignore_permissions=True)

	industries = {"Technology", "Manufacturing", "Consulting", "Telecommunications", "Financial Services", "Advertising"}
	for name in industries:
		if not frappe.db.exists("Industry Type", name):
			frappe.get_doc({
				"doctype": "Industry Type",
				"industry": name,
			}).insert(ignore_permissions=True)


def create_demo_customers():
	_ensure_masters()
	created = []
	for data in DEMO_CUSTOMERS:
		if frappe.db.exists("Customer", data["customer_name"]):
			created.append(data["customer_name"])
			continue

		customer = frappe.get_doc({
			"doctype": "Customer",
			"customer_name": data["customer_name"],
			"customer_type": data["customer_type"],
			"customer_group": data["customer_group"],
			"territory": data["territory"],
			"industry": data.get("industry"),
			"website": data.get("website"),
			"mobile_no": data.get("mobile_no"),
			"email_id": data.get("email_id"),
		}).insert(ignore_permissions=True)
		created.append(customer.name)

	frappe.db.commit()
	return created


def delete_demo_customers(customer_names):
	# clefincode_chat links ClefinCode Chat Profile → Contact, blocking Customer deletion.
	if frappe.db.table_exists("ClefinCode Chat Profile"):
		frappe.db.sql("DELETE FROM `tabClefinCode Chat Profile`")
	for name in customer_names:
		if frappe.db.exists("Customer", name):
			frappe.delete_doc("Customer", name, ignore_permissions=True, force=True)
	frappe.db.commit()
