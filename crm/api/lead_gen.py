import frappe
from frappe import _
import json


@frappe.whitelist()
def import_leads_from_excel(file_url: str):
	"""Import leads from an uploaded Excel file.

	Reads the Excel file, maps columns to CRM Lead fields,
	and creates CRM Lead records for each row.

	Expected columns: COMPANY, Industry, PHONE, NAME, POSITION, EMAIL, STATUS, LINKEDIN

	Args:
	    file_url: The URL of the uploaded file (e.g., /private/files/Lead Gen Data.xlsx)

	Returns:
	    dict with 'created' (int), 'skipped' (int), 'errors' (list), 'total' (int)
	"""
	try:
		import openpyxl
	except ImportError:
		frappe.throw(_("openpyxl is required. Install it with: pip install openpyxl"))

	# Resolve file path
	file_path = frappe.get_site_path(file_url.lstrip("/"))
	if not file_path:
		frappe.throw(_("File not found"))

	try:
		wb = openpyxl.load_workbook(file_path, read_only=True)
	except Exception as e:
		frappe.throw(_("Could not read Excel file: {0}").format(str(e)))

	ws = wb.active

	# Parse headers
	headers = [cell.value for cell in ws[1]]

	# Map Excel columns to CRM Lead fields
	column_map = {}
	for idx, header in enumerate(headers):
		if header is None:
			continue
		header_lower = header.strip().lower()
		if header_lower in ("company", "organization"):
			column_map["company"] = idx
		elif header_lower in ("industry",):
			column_map["industry"] = idx
		elif header_lower in ("phone", "mobile", "mobile_no"):
			column_map["phone"] = idx
		elif header_lower in ("name", "lead_name", "contact_name"):
			column_map["name"] = idx
		elif header_lower in ("position", "designation", "title", "job_title"):
			column_map["position"] = idx
		elif header_lower in ("email", "email_id", "email_address"):
			column_map["email"] = idx
		elif header_lower in ("status",):
			column_map["status"] = idx
		elif header_lower in ("linkedin", "linkedin_url"):
			column_map["linkedin"] = idx
		elif header_lower in ("feedback", "notes"):
			column_map["feedback"] = idx

	created = 0
	skipped = 0
	errors = []
	total = 0

	# Status mapping from Excel values to CRM Lead statuses
	status_map = {
		"open": "New",
		"new": "New",
		"contacted": "Contacted",
		"qualified": "Qualified",
		"converted": "Converted",
		"closed": "Closed",
		"lost": "Lost",
		"do not contact": "Do Not Contact",
	}

	for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
		# Skip completely empty rows
		if all(cell is None for cell in row):
			continue

		total += 1

		try:
			# Extract data
			company = _get_cell(row, column_map.get("company"))
			name = _get_cell(row, column_map.get("name"))
			email = _get_cell(row, column_map.get("email"))
			phone = _get_cell(row, column_map.get("phone"))
			position = _get_cell(row, column_map.get("position"))
			industry = _get_cell(row, column_map.get("industry"))
			status_raw = _get_cell(row, column_map.get("status"))
			linkedin = _get_cell(row, column_map.get("linkedin"))

			# Skip if no company and no name
			if not company and not name:
				skipped += 1
				continue

			# Check for duplicate by email
			if email and frappe.db.exists("CRM Lead", {"email": email}):
				skipped += 1
				continue

			# Map status
			status = "New"
			if status_raw:
				status = status_map.get(status_raw.lower().strip(), "New")

			# Clean phone (convert wa.me links to phone numbers)
			if phone and "wa.me/" in str(phone):
				phone = "+" + str(phone).split("wa.me/")[-1].strip()

			# Create the lead
			lead = frappe.get_doc(
				{
					"doctype": "CRM Lead",
					"lead_name": name or company,
					"first_name": name.split()[0] if name and " " in name else (name or ""),
					"last_name": " ".join(name.split()[1:]) if name and " " in name else "",
					"email": email,
					"mobile_no": phone,
					"organization": company,
					"job_title": position,
					"industry": industry,
					"status": status,
					"source": "Excel Import",
					"website": linkedin if linkedin else None,
				}
			)
			lead.insert(ignore_permissions=True)
			created += 1

		except Exception as e:
			errors.append({"row": row_idx, "error": str(e)})
			if len(errors) > 20:
				break

	frappe.db.commit()
	wb.close()

	return {
		"created": created,
		"skipped": skipped,
		"errors": errors[:10],  # Return max 10 errors
		"total": total,
	}


@frappe.whitelist()
def get_excel_preview(file_url: str):
	"""Preview the first few rows of an Excel file before importing.

	Args:
	    file_url: The URL of the uploaded file

	Returns:
	    dict with 'headers' (list), 'rows' (list of lists), 'total_rows' (int)
	"""
	try:
		import openpyxl
	except ImportError:
		frappe.throw(_("openpyxl is required"))

	file_path = frappe.get_site_path(file_url.lstrip("/"))

	try:
		wb = openpyxl.load_workbook(file_path, read_only=True)
	except Exception as e:
		frappe.throw(_("Could not read Excel file: {0}").format(str(e)))

	ws = wb.active
	headers = [str(cell.value or "") for cell in ws[1]]

	rows = []
	for row in ws.iter_rows(min_row=2, max_row=min(11, ws.max_row), values_only=True):
		rows.append([str(cell) if cell is not None else "" for cell in row])

	total_rows = ws.max_row - 1  # Exclude header

	wb.close()
	return {"headers": headers, "rows": rows, "total_rows": total_rows}


def _get_cell(row: tuple, idx: int | None) -> str | None:
	"""Safely get a cell value from a row tuple."""
	if idx is None or idx >= len(row):
		return None
	val = row[idx]
	if val is None or str(val).strip().lower() == "none":
		return None
	return str(val).strip()

@frappe.whitelist()
def mock_lead_scraping():
	"""Mock a scraping process by reading from the predefined /tmp/Lead Gen Data.xlsx"""
	try:
		import openpyxl
	except ImportError:
		frappe.throw(_("openpyxl is required."))

	file_path = "/tmp/Lead Gen Data.xlsx"

	try:
		wb = openpyxl.load_workbook(file_path, read_only=True)
	except Exception as e:
		frappe.throw(_("Could not read mock scraping data: {0}").format(str(e)))

	ws = wb.active
	headers = [str(cell.value).strip() if cell.value else "" for cell in ws[1]]
	
	# Improved Column Mapping
	column_map = {}
	for idx, header in enumerate(headers):
		if not header: continue
		h = header.lower()
		if any(x in h for x in ["company", "organization", "perusahaan", "nama entitas"]):
			column_map["company"] = idx
		elif any(x in h for x in ["industry", "industri", "sektor"]):
			column_map["industry"] = idx
		elif any(x in h for x in ["phone", "mobile", "telp", "no hp", "whatsapp"]):
			column_map["phone"] = idx
		elif any(x in h for x in ["name", "lead", "contact", "nama"]):
			column_map["name"] = idx
		elif any(x in h for x in ["position", "job", "title", "jabatan"]):
			column_map["position"] = idx
		elif any(x in h for x in ["email", "surel"]):
			column_map["email"] = idx
		elif any(x in h for x in ["linkedin", "website", "url"]):
			column_map["linkedin"] = idx
	
	# Debug mapping
	frappe.log_error(json.dumps(column_map), _("Lead Gen Detected Columns"))
	frappe.msgprint(_("Detected Columns: {0}").format(json.dumps(column_map)))

	created = 0
	skipped = 0
	total = 0

	status_map = {
		"open": "New",
		"new": "New",
		"contacted": "Contacted",
		"qualified": "Qualified",
		"converted": "Converted",
		"closed": "Closed",
		"lost": "Lost",
		"do not contact": "Do Not Contact",
	}

	for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
		if all(cell is None for cell in row):
			continue
		
		# Limit to 15 rows for the mock to prevent timeout
		if total >= 15:
			break
			
		total += 1

		try:
			company = _get_cell(row, column_map.get("company"))
			name = _get_cell(row, column_map.get("name"))
			email = _get_cell(row, column_map.get("email"))
			phone = _get_cell(row, column_map.get("phone"))
			position = _get_cell(row, column_map.get("position"))
			industry = _get_cell(row, column_map.get("industry"))
			status_raw = _get_cell(row, column_map.get("status"))
			linkedin = _get_cell(row, column_map.get("linkedin"))

			if not company and not name:
				skipped += 1
				continue

			# Clean Phone
			if phone:
				if "wa.me/" in str(phone):
					phone = str(phone).split("wa.me/")[-1].replace("-", "").strip()
				# Keep only digits and +
				phone = "".join(c for c in str(phone) if c.isdigit() or c == "+")

			# Clean Email
			if email and (email.strip() == "-" or "@" not in str(email)):
				email = None

			# Safely check Industry
			valid_industry = None
			if industry:
				try:
					if frappe.db.exists("Industry", industry):
						valid_industry = industry
				except Exception:
					pass

			lead = frappe.get_doc(
				{
					"doctype": "CRM Lead",
					"lead_name": name or company,
					"first_name": name.split()[0] if name and " " in name else (name or ""),
					"last_name": " ".join(name.split()[1:]) if name and " " in name else "",
					"email": email,
					"mobile_no": phone,
					"organization": company,
					"job_title": position,
					"industry": valid_industry,
					"status": "New",
					"source": "Campaign",
					"lead_owner": frappe.session.user,
					"owner": frappe.session.user,
					"website": linkedin if linkedin else None,
				}
			)

			lead.insert(ignore_permissions=True, ignore_links=True)
			created += 1
			frappe.db.commit()

			# Emit real-time event for live update
			frappe.publish_realtime("lead_scraped", {
				"lead_name": lead.lead_name,
				"company": lead.organization,
				"count": created
			}, user=frappe.session.user)

			# Small sleep so the user can see the live update effect
			import time
			time.sleep(0.8)
			
		except Exception as e:


			frappe.log_error(frappe.get_traceback(), _("Lead Scraping Error"))

	frappe.db.commit()
	frappe.clear_cache(doctype="CRM Lead")
	frappe.cache().delete_value("doctype_cache")
	# Force refresh the list view cache specifically
	frappe.cache().delete_keys("crm_lead_list")
	
	frappe.msgprint(_("Scraping finished. Total: {0}, Created: {1}, Skipped: {2}").format(total, created, skipped))




	return {
		"message": f"Successfully scraped and imported {created} new leads. Skipped {skipped} duplicates.",
		"created": created
	}

