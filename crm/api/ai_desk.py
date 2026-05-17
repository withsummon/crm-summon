import frappe
from frappe import _
import json


@frappe.whitelist()
def get_ai_desk_context():
	"""Get CRM context information for the AI Desk chatbot."""
	context = {
		"doctypes": [],
		"summary": {},
	}

	# Get CRM doctype summaries
	crm_doctypes = {
		"CRM Lead": {
			"description": "Leads - potential customers or prospects",
			"key_fields": ["lead_name", "email", "mobile_no", "status", "source", "lead_owner"],
		},
		"CRM Deal": {
			"description": "Deals - business opportunities being pursued",
			"key_fields": ["deal_owner", "organization", "status", "probability", "annual_revenue"],
		},
		"Contact": {
			"description": "Contacts - people associated with organizations",
			"key_fields": ["first_name", "last_name", "email_id", "mobile_no", "company_name"],
		},
		"CRM Organization": {
			"description": "Organizations - companies or businesses",
			"key_fields": ["organization_name", "website", "industry", "annual_revenue"],
		},
		"CRM Task": {
			"description": "Tasks - action items and to-dos",
			"key_fields": ["title", "status", "priority", "due_date", "assigned_to"],
		},
		"FCRM Note": {
			"description": "Notes - text notes and observations",
			"key_fields": ["title", "content"],
		},
	}

	for doctype, info in crm_doctypes.items():
		try:
			count = len(frappe.get_list(doctype, limit_page_length=0))
			context["doctypes"].append(
				{
					"doctype": doctype,
					"description": info["description"],
					"key_fields": info["key_fields"],
					"count": count,
				}
			)
		except Exception:
			pass

	# Get summary stats
	try:
		context["summary"]["total_leads"] = len(frappe.get_list("CRM Lead", limit_page_length=0))
		context["summary"]["total_deals"] = len(frappe.get_list("CRM Deal", limit_page_length=0))
		context["summary"]["total_contacts"] = len(frappe.get_list("Contact", limit_page_length=0))
		context["summary"]["total_organizations"] = len(frappe.get_list("CRM Organization", limit_page_length=0))
		context["summary"]["total_tasks"] = len(frappe.get_list("CRM Task", limit_page_length=0))

		# Get lead status distribution
		lead_statuses = {}
		for lead in frappe.get_list("CRM Lead", fields=["status"], limit_page_length=0):
			status = lead.status or "Unknown"
			lead_statuses[status] = lead_statuses.get(status, 0) + 1
		context["summary"]["lead_statuses"] = lead_statuses

		# Get deal status distribution
		deal_statuses = {}
		for deal in frappe.get_list("CRM Deal", fields=["status"], limit_page_length=0):
			status = deal.status or "Unknown"
			deal_statuses[status] = deal_statuses.get(status, 0) + 1
		context["summary"]["deal_statuses"] = deal_statuses

		# Include actual recent data for RAG so AI can answer "who are they?"
		context["recent_data"] = {}
		context["recent_data"]["leads"] = frappe.get_list(
			"CRM Lead",
			fields=["lead_name", "status", "organization", "mobile_no", "email"],
			limit_page_length=50,
			order_by="modified desc"
		)
		context["recent_data"]["contacts"] = frappe.get_list(
			"Contact",
			fields=["first_name", "last_name", "email_id", "mobile_no"],
			limit_page_length=50,
			order_by="modified desc"
		)
		context["recent_data"]["deals"] = frappe.get_list(
			"CRM Deal",
			fields=["name", "organization", "status", "deal_value"],
			limit_page_length=30,
			order_by="modified desc"
		)
		context["recent_data"]["organizations"] = frappe.get_list(
			"CRM Organization",
			fields=["name", "organization_name", "industry", "website"],
			limit_page_length=30,
			order_by="modified desc"
		)
		context["recent_data"]["tasks"] = frappe.get_list(
			"CRM Task",
			fields=["name", "title", "status", "priority", "due_date"],
			limit_page_length=30,
			order_by="modified desc"
		)
		context["recent_data"]["notes"] = frappe.get_list(
			"CRM Note",
			fields=["name", "title", "content"],
			limit_page_length=20,
			order_by="modified desc"
		)
		context["recent_data"]["call_logs"] = frappe.get_list(
			"CRM Call Log",
			fields=["name", "type", "status", "duration", "summary"],
			limit_page_length=20,
			order_by="modified desc"
		)
		if frappe.db.exists("DocType", "Event"):
			context["recent_data"]["events"] = frappe.get_list(
				"Event",
				fields=["name", "subject", "starts_on", "ends_on", "status"],
				limit_page_length=20,
				order_by="starts_on asc"
			)

	except Exception:
		pass

	return context


@frappe.whitelist()
def query_ai_desk(message: str, conversation_history: str | None = None):
	"""Process an AI Desk chat message and return a response.

	This endpoint processes user queries about the CRM data and features,
	generating relevant SQL queries and returning human-readable responses.

	Args:
	    message: The user's chat message/question
	    conversation_history: Optional JSON string of previous conversation messages

	Returns:
	    dict with 'response' (str), 'data' (list/dict or None), 'query' (str or None)
	"""
	if not message or not message.strip():
		return {"response": _("Please enter a valid question."), "data": None, "query": None}

	message = message.strip()
	history = json.loads(conversation_history) if conversation_history else []

	# Get CRM context
	context = get_ai_desk_context()

	ai_provider = "Gemini"
	gemini_api_key = None
	kimi_api_key = None
	
	try:
		doc = frappe.get_doc("FCRM Settings")
		ai_provider = doc.ai_provider or "Gemini"
		gemini_api_key = doc.get_password("gemini_api_key")
		kimi_api_key = doc.get_password("kimi_api_key")
	except Exception:
		pass
			
	if ai_provider == "Kimi" and kimi_api_key and "******" not in kimi_api_key:
		return call_kimi_api(message, kimi_api_key, context, history)
	elif ai_provider == "Gemini" and gemini_api_key and "******" not in gemini_api_key:
		return call_gemini_api(message, gemini_api_key, context, history)

	# Try to answer the query using CRM data
	response = process_crm_query(message, context, history)

	return response


def call_gemini_api(message: str, api_key: str, context: dict, history: list) -> dict:
	import requests
	api_key = api_key.strip()
	
	try:
		models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
		r_models = requests.get(models_url, timeout=10)
		r_models.raise_for_status()
		
		available = r_models.json().get("models", [])
		valid_models = [m["name"] for m in available if "generateContent" in m.get("supportedGenerationMethods", [])]
		
		if not valid_models:
			return {"response": "No supported Gemini models found for this API Key.", "data": None, "query": None}
			
		# Prefer flash, else take first
		model_name = next((m for m in valid_models if "1.5-flash" in m), valid_models[0])
	except Exception as e:
		return {"response": f"Failed to fetch available Gemini models: {str(e)}", "data": None, "query": None}
		
	url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
	
	system_instruction = (
		"You are Summon CRM AI Assistant. Be helpful, concise, and professional. "
		"You format your responses in Markdown. "
		"Here is the current CRM context with counts of various records:\n"
		f"{json.dumps(context)}"
	)
	
	payload = {
		"contents": []
	}
	
	contents = []
	last_role = None
	
	for msg in history:
		role = "model" if msg.get("sender") == "ai" else "user"
		text = msg.get("text", "")
		if not text: continue
		
		if role == last_role:
			contents[-1]["parts"][0]["text"] += "\n" + text
		else:
			contents.append({
				"role": role,
				"parts": [{"text": text}]
			})
		last_role = role
		
	if last_role == "user":
		contents[-1]["parts"][0]["text"] += "\n" + message
	else:
		contents.append({
			"role": "user",
			"parts": [{"text": message}]
		})
		
	if contents and contents[0]["role"] == "model":
		contents.insert(0, {"role": "user", "parts": [{"text": "Hello"}]})
		
	if contents:
		contents[0]["parts"][0]["text"] = f"[SYSTEM INSTRUCTION]\n{system_instruction}\n[END SYSTEM INSTRUCTION]\n\n" + contents[0]["parts"][0]["text"]
		
	payload["contents"] = contents
	
	try:
		response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
		response.raise_for_status()
		data = response.json()
		
		reply_text = data["candidates"][0]["content"]["parts"][0]["text"]
		return {"response": reply_text, "data": None, "query": None}
	except requests.exceptions.RequestException as e:
		error_details = response.text if 'response' in locals() and hasattr(response, 'text') else str(e)
		frappe.log_error(error_details, "Gemini API Error")
		return {"response": f"Sorry, Gemini API rejected the request: {error_details}", "data": None, "query": None}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Gemini API Error")
		return {"response": f"Sorry, an internal error occurred: {str(e)}", "data": None, "query": None}


def call_kimi_api(message: str, api_key: str, context: dict, history: list) -> dict:
	import requests
	api_key = api_key.strip()
	url = "https://api.moonshot.ai/v1/chat/completions"
	
	system_instruction = (
		"You are Summon CRM AI Assistant powered by Kimi. Be helpful, concise, and professional. "
		"You format your responses in Markdown. "
		"Here is the current CRM context with counts of various records:\n"
		f"{json.dumps(context)}"
	)
	
	messages = [{"role": "system", "content": system_instruction}]
	
	for msg in history:
		role = "assistant" if msg.get("sender") == "ai" else "user"
		text = msg.get("text", "")
		if not text: continue
		messages.append({"role": role, "content": text})
		
	messages.append({"role": "user", "content": message})
	
	payload = {
		"model": "kimi-k2.6",
		"messages": messages
	}
	
	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {api_key}"
	}
	
	try:
		response = requests.post(url, json=payload, headers=headers, timeout=45)
		response.raise_for_status()
		data = response.json()
		
		reply_text = data["choices"][0]["message"]["content"]
		return {"response": reply_text, "data": None, "query": None}
	except requests.exceptions.RequestException as e:
		error_details = response.text if 'response' in locals() and hasattr(response, 'text') else str(e)
		frappe.log_error(error_details, "Kimi API Error")
		return {"response": f"Sorry, Kimi API rejected the request: {error_details}", "data": None, "query": None}
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Kimi API Error")
		return {"response": f"Sorry, an internal error occurred: {str(e)}", "data": None, "query": None}


def process_crm_query(message: str, context: dict, history: list) -> dict:
	"""Process a CRM query and return an intelligent response.

	Uses pattern matching and direct database queries to answer
	common CRM questions without requiring an external AI API.
	"""
	message_lower = message.lower()

	# Feature guide responses
	feature_responses = get_feature_response(message_lower)
	if feature_responses:
		return {"response": feature_responses, "data": None, "query": None}

	# Data queries
	data_response = get_data_response(message_lower, context)
	if data_response:
		return data_response

	# Default: provide a helpful overview
	return get_default_response(message_lower, context)


def get_feature_response(message: str) -> str | None:
	"""Return help text about CRM features."""
	features = {
		"lead": _(
			"## 📋 Leads Management\n\n"
			"Leads represent potential customers or prospects in your pipeline.\n\n"
			"**Key Features:**\n"
			"- Create and track leads from various sources\n"
			"- Assign leads to team members\n"
			"- Track lead status and progress\n"
			"- Convert qualified leads to deals\n"
			"- Import leads from CSV/Excel files\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Leads** from the sidebar\n"
			"- Click **+ Create** to add a new lead\n"
			"- Use filters and views to organize your leads"
		),
		"deal": _(
			"## 💰 Deals Management\n\n"
			"Deals represent business opportunities that you are actively pursuing.\n\n"
			"**Key Features:**\n"
			"- Track deal value, probability, and status\n"
			"- Associate deals with organizations and contacts\n"
			"- Monitor deal pipeline with Kanban view\n"
			"- Track activities, emails, and notes per deal\n"
			"- Set up custom deal stages\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Deals** from the sidebar\n"
			"- Convert a lead to a deal from the lead detail page\n"
			"- Use the Kanban view for visual pipeline management"
		),
		"contact": _(
			"## 👤 Contacts Management\n\n"
			"Contacts are individuals associated with organizations in your CRM.\n\n"
			"**Key Features:**\n"
			"- Store contact details (email, phone, address)\n"
			"- Link contacts to organizations\n"
			"- Track communication history\n"
			"- Send emails directly from the contact page\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Contacts** from the sidebar\n"
			"- Click **+ Create** to add a new contact"
		),
		"organization": _(
			"## 🏢 Organizations\n\n"
			"Organizations represent companies or businesses you work with.\n\n"
			"**Key Features:**\n"
			"- Track company details and annual revenue\n"
			"- Link related leads, deals, and contacts\n"
			"- Store website and industry information\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Organizations** from the sidebar\n"
			"- Click **+ Create** to add a new organization"
		),
		"task": _(
			"## ✅ Tasks\n\n"
			"Tasks help you manage action items and to-dos.\n\n"
			"**Key Features:**\n"
			"- Create tasks with due dates and priorities\n"
			"- Assign tasks to team members\n"
			"- Link tasks to leads or deals\n"
			"- Track task status and completion\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Tasks** from the sidebar\n"
			"- Create tasks directly from a lead or deal page"
		),
		"note": _(
			"## 📝 Notes\n\n"
			"Notes let you capture important information and observations.\n\n"
			"**Key Features:**\n"
			"- Create rich-text notes\n"
			"- Link notes to leads or deals\n"
			"- Organize notes with titles\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Notes** from the sidebar\n"
			"- Add notes directly from a lead or deal page"
		),
		"calendar": _(
			"## 📅 Calendar\n\n"
			"The calendar helps you manage events and appointments.\n\n"
			"**Key Features:**\n"
			"- View events in day, week, or month format\n"
			"- Create and manage meetings\n"
			"- Set reminders and notifications\n"
			"- Link events to leads or deals\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Calendar** from the sidebar"
		),
		"email": _(
			"## 📧 Email\n\n"
			"Send and receive emails directly within Summon CRM.\n\n"
			"**Key Features:**\n"
			"- Send emails from lead/deal/contact pages\n"
			"- Track email communication history\n"
			"- Use email templates for quick responses\n"
			"- Configure email accounts in Settings\n\n"
			"**Quick Actions:**\n"
			"- Open Settings → Email → Accounts to configure\n"
			"- Use Templates for quick email composition"
		),
		"dashboard": _(
			"## 📊 Dashboard\n\n"
			"The dashboard provides an overview of your CRM performance.\n\n"
			"**Key Features:**\n"
			"- View key metrics and KPIs\n"
			"- Track lead and deal pipeline\n"
			"- Monitor team performance\n"
			"- Customizable widgets and charts\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Dashboard** from the sidebar"
		),
		"setting": _(
			"## ⚙️ Settings\n\n"
			"Configure your Summon CRM experience.\n\n"
			"**Available Settings:**\n"
			"- **Profile** — Manage your account information\n"
			"- **Preferences** — Customize your experience\n"
			"- **General** — System-wide configuration\n"
			"- **Brand** — Custom branding and logo\n"
			"- **Calendar** — Calendar preferences\n"
			"- **Email** — Email account configuration\n"
			"- **Telephony** — Phone integration setup\n"
			"- **Assignment Rules** — Auto-assign leads/deals\n"
			"- **SLA Policies** — Service level agreements\n\n"
			"**Quick Actions:**\n"
			"- Click the user dropdown → Settings"
		),
		"import": _(
			"## 📥 Data Import\n\n"
			"Import data from external sources into Summon CRM.\n\n"
			"**Key Features:**\n"
			"- Import leads, contacts, organizations from CSV/Excel\n"
			"- Map columns to CRM fields\n"
			"- Preview data before importing\n"
			"- Track import history\n\n"
			"**Quick Actions:**\n"
			"- Navigate to **Data Import** from the sidebar or URL"
		),
	}

	for keyword, response in features.items():
		if keyword in message:
			return response

	# Help/getting started
	if any(kw in message for kw in ["help", "start", "how to", "guide", "tutorial", "mulai", "bantuan"]):
		return _(
			"## 🚀 Getting Started with Summon CRM\n\n"
			"Here's how to get started:\n\n"
			"1. **Create your first lead** — Go to Leads → + Create\n"
			"2. **Add contact details** — Fill in email, phone, and organization\n"
			"3. **Track progress** — Update lead status as you engage\n"
			"4. **Convert to deal** — When a lead qualifies, convert it to a deal\n"
			"5. **Manage your pipeline** — Use the Kanban view for visual tracking\n\n"
			"**Ask me about any feature!** For example:\n"
			"- \"How do leads work?\"\n"
			"- \"Tell me about deals\"\n"
			"- \"How many leads do I have?\"\n"
			"- \"Show me the dashboard overview\""
		)

	return None


def get_data_response(message: str, context: dict) -> dict | None:
	"""Answer data-related queries about CRM records."""
	summary = context.get("summary", {})

	# Count queries
	if any(kw in message for kw in ["how many", "berapa", "count", "total", "jumlah"]):
		if any(kw in message for kw in ["lead", "prospek"]):
			count = summary.get("total_leads", 0)
			statuses = summary.get("lead_statuses", {})
			status_text = "\n".join([f"  - **{k}**: {v}" for k, v in statuses.items()]) if statuses else "  No status data available"
			return {
				"response": _(
					"## 📋 Lead Statistics\n\n"
					"**Total Leads:** {count}\n\n"
					"**By Status:**\n{statuses}"
				).format(count=count, statuses=status_text),
				"data": {"total": count, "by_status": statuses},
				"query": "SELECT status, COUNT(*) FROM `tabCRM Lead` GROUP BY status",
			}

		if any(kw in message for kw in ["deal", "transaksi", "kesepakatan"]):
			count = summary.get("total_deals", 0)
			statuses = summary.get("deal_statuses", {})
			status_text = "\n".join([f"  - **{k}**: {v}" for k, v in statuses.items()]) if statuses else "  No status data available"
			return {
				"response": _(
					"## 💰 Deal Statistics\n\n"
					"**Total Deals:** {count}\n\n"
					"**By Status:**\n{statuses}"
				).format(count=count, statuses=status_text),
				"data": {"total": count, "by_status": statuses},
				"query": "SELECT status, COUNT(*) FROM `tabCRM Deal` GROUP BY status",
			}

		if any(kw in message for kw in ["contact", "kontak"]):
			count = summary.get("total_contacts", 0)
			return {
				"response": _("## 👤 Contact Statistics\n\n**Total Contacts:** {count}").format(count=count),
				"data": {"total": count},
				"query": "SELECT COUNT(*) FROM `tabContact`",
			}

		if any(kw in message for kw in ["organization", "organisasi", "company", "perusahaan"]):
			count = summary.get("total_organizations", 0)
			return {
				"response": _("## 🏢 Organization Statistics\n\n**Total Organizations:** {count}").format(count=count),
				"data": {"total": count},
				"query": "SELECT COUNT(*) FROM `tabCRM Organization`",
			}

		if any(kw in message for kw in ["task", "tugas"]):
			count = summary.get("total_tasks", 0)
			return {
				"response": _("## ✅ Task Statistics\n\n**Total Tasks:** {count}").format(count=count),
				"data": {"total": count},
				"query": "SELECT COUNT(*) FROM `tabCRM Task`",
			}

		# General overview
		return {
			"response": _(
				"## 📊 CRM Overview\n\n"
				"| Module | Count |\n"
				"|--------|-------|\n"
				"| 📋 Leads | {leads} |\n"
				"| 💰 Deals | {deals} |\n"
				"| 👤 Contacts | {contacts} |\n"
				"| 🏢 Organizations | {orgs} |\n"
				"| ✅ Tasks | {tasks} |"
			).format(
				leads=summary.get("total_leads", 0),
				deals=summary.get("total_deals", 0),
				contacts=summary.get("total_contacts", 0),
				orgs=summary.get("total_organizations", 0),
				tasks=summary.get("total_tasks", 0),
			),
			"data": summary,
			"query": None,
		}

	# Recent records queries
	if any(kw in message for kw in ["recent", "latest", "terbaru", "last", "terakhir"]):
		return get_recent_records(message)

	# List queries
	if any(kw in message for kw in ["list", "show", "tampilkan", "daftar", "lihat"]):
		return get_recent_records(message, limit=10)

	return None


def get_recent_records(message: str, limit: int = 5) -> dict:
	"""Get recent records from the CRM."""
	if any(kw in message for kw in ["lead", "prospek"]):
		records = frappe.get_all(
			"CRM Lead",
			fields=["name", "lead_name", "status", "email", "creation"],
			order_by="creation desc",
			limit=limit,
		)
		if records:
			table = "| # | Name | Status | Email | Created |\n|---|------|--------|-------|--------|\n"
			for i, r in enumerate(records, 1):
				table += f"| {i} | {r.lead_name or 'N/A'} | {r.status or 'N/A'} | {r.email or 'N/A'} | {str(r.creation)[:10]} |\n"
			return {
				"response": f"## 📋 Recent Leads (Last {limit})\n\n{table}",
				"data": records,
				"query": f"SELECT name, lead_name, status, email, creation FROM `tabCRM Lead` ORDER BY creation DESC LIMIT {limit}",
			}

	if any(kw in message for kw in ["deal", "transaksi"]):
		records = frappe.get_all(
			"CRM Deal",
			fields=["name", "organization", "status", "annual_revenue", "creation"],
			order_by="creation desc",
			limit=limit,
		)
		if records:
			table = "| # | Organization | Status | Revenue | Created |\n|---|-------------|--------|---------|--------|\n"
			for i, r in enumerate(records, 1):
				table += f"| {i} | {r.organization or 'N/A'} | {r.status or 'N/A'} | {r.annual_revenue or 'N/A'} | {str(r.creation)[:10]} |\n"
			return {
				"response": f"## 💰 Recent Deals (Last {limit})\n\n{table}",
				"data": records,
				"query": f"SELECT name, organization, status, annual_revenue, creation FROM `tabCRM Deal` ORDER BY creation DESC LIMIT {limit}",
			}

	if any(kw in message for kw in ["contact", "kontak"]):
		records = frappe.get_all(
			"Contact",
			fields=["name", "first_name", "last_name", "email_id", "creation"],
			order_by="creation desc",
			limit=limit,
		)
		if records:
			table = "| # | Name | Email | Created |\n|---|------|-------|--------|\n"
			for i, r in enumerate(records, 1):
				name = f"{r.first_name or ''} {r.last_name or ''}".strip() or "N/A"
				table += f"| {i} | {name} | {r.email_id or 'N/A'} | {str(r.creation)[:10]} |\n"
			return {
				"response": f"## 👤 Recent Contacts (Last {limit})\n\n{table}",
				"data": records,
				"query": f"SELECT name, first_name, last_name, email_id, creation FROM `tabContact` ORDER BY creation DESC LIMIT {limit}",
			}

	# Default: show overview
	return get_data_response("how many", {"summary": {
		"total_leads": frappe.db.count("CRM Lead"),
		"total_deals": frappe.db.count("CRM Deal"),
		"total_contacts": frappe.db.count("Contact"),
		"total_organizations": frappe.db.count("CRM Organization"),
		"total_tasks": frappe.db.count("CRM Task"),
	}})


def get_default_response(message: str, context: dict) -> dict:
	"""Provide a default helpful response."""
	summary = context.get("summary", {})
	return {
		"response": _(
			"## 👋 Welcome to Summon AI Desk\n\n"
			"I can help you with:\n\n"
			"**📊 Data Queries:**\n"
			"- \"How many leads do I have?\"\n"
			"- \"Show me recent deals\"\n"
			"- \"List latest contacts\"\n"
			"- \"How many tasks?\"\n\n"
			"**📖 Feature Help:**\n"
			"- \"How do leads work?\"\n"
			"- \"Tell me about deals\"\n"
			"- \"How to use the calendar?\"\n"
			"- \"Help with email settings\"\n\n"
			"**📈 Quick Overview:**\n"
			"You currently have **{leads}** leads, **{deals}** deals, "
			"**{contacts}** contacts, and **{tasks}** tasks.\n\n"
			"_Ask me anything about your CRM!_"
		).format(
			leads=summary.get("total_leads", 0),
			deals=summary.get("total_deals", 0),
			contacts=summary.get("total_contacts", 0),
			tasks=summary.get("total_tasks", 0),
		),
		"data": None,
		"query": None,
	}
