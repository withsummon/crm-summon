import frappe

from crm.api.ai_agent_center import get_agents, query_agent


@frappe.whitelist()
def get_ai_desk_context():
	"""Compatibility wrapper for the former AI Desk context endpoint."""
	return {"agents": get_agents(), "name": "AI Agent Center"}


@frappe.whitelist()
def query_ai_desk(message: str, conversation_history: str | None = None):
	"""Compatibility wrapper for the former AI Desk chat endpoint."""
	return query_agent(agent_key="general", message=message)
