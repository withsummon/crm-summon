import os
from decimal import Decimal

import frappe
from frappe import _
from openrouter import OpenRouter


DEFAULT_LLM_MODEL = "openai/gpt-6-luna"


def get_ai_settings():
	settings = frappe._dict(
		{
			"provider": "OpenRouter",
			"model": os.getenv("OPENROUTER_MODEL") or DEFAULT_LLM_MODEL,
			"api_key": os.getenv("OPENROUTER_API_KEY"),
			"rag_storage_path": "",
			"local_embedding_model": "BAAI/bge-m3",
			"guardrail_confidence_threshold": 0.45,
			"daily_cost_limit_usd": 25,
			"thinking_mode": "disabled",
		}
	)
	try:
		doc = frappe.get_doc("FCRM Settings")
		settings.model = doc.get("llm_model") or os.getenv("OPENROUTER_MODEL") or DEFAULT_LLM_MODEL
		settings.api_key = os.getenv("OPENROUTER_API_KEY") or doc.get_password("openrouter_api_key")
		settings.rag_storage_path = doc.get("rag_storage_path") or ""
		settings.local_embedding_model = doc.get("local_embedding_model") or "BAAI/bge-m3"
		val = doc.get("guardrail_confidence_threshold")
		settings.guardrail_confidence_threshold = float(val) if val not in (None, "") else 0.45
		cost_limit = doc.get("daily_cost_limit_usd")
		settings.daily_cost_limit_usd = float(cost_limit) if cost_limit not in (None, "") else 25.0
	except Exception:
		pass
	return settings


def _client(settings, timeout):
	if not settings.api_key or "******" in settings.api_key:
		frappe.throw(_("OpenRouter API key is not configured. Set OPENROUTER_API_KEY or add it in AI Settings."))
	return OpenRouter(api_key=settings.api_key, x_open_router_title="IGLO CRM", timeout_ms=timeout * 1000)


def _cost(usage):
	return Decimal(str(usage.cost)) if usage and isinstance(usage.cost, (int, float)) else Decimal("0")


def call_llm_chat(messages, model=None, tools=None, thinking_mode="disabled", timeout=180):
	settings = get_ai_settings()
	request = {"model": model or settings.model, "messages": messages}
	if tools:
		request.update({"tools": tools, "tool_choice": "auto"})
	if thinking_mode == "enabled":
		request["reasoning"] = {"enabled": True}
	with _client(settings, timeout) as client:
		response = client.chat.send(**request)
	usage = response.usage
	return frappe._dict(
		{
			"content": response.choices[0].message.content or "",
			"raw": response.model_dump(),
			"model": response.model or request["model"],
			"prompt_tokens": usage.prompt_tokens if usage else 0,
			"completion_tokens": usage.completion_tokens if usage else 0,
			"total_tokens": usage.total_tokens if usage else 0,
			"cost": _cost(usage),
		}
	)


def stream_llm_chat_events(messages, model=None, tools=None, thinking_mode="disabled", timeout=120):
	settings = get_ai_settings()
	request = {
		"model": model or settings.model,
		"messages": messages,
		"stream": True,
		"stream_options": {"include_usage": True},
	}
	if tools:
		request.update({"tools": tools, "tool_choice": "auto"})
	if thinking_mode == "enabled":
		request["reasoning"] = {"enabled": True}
	usage = None
	response_model = request["model"]
	with _client(settings, timeout) as client:
		for event in client.chat.send(**request):
			response_model = event.model or response_model
			usage = event.usage or usage
			if not event.choices:
				continue
			delta = event.choices[0].delta
			content = delta.content or ""
			if content:
				yield frappe._dict({"event": "delta", "delta": content, "reasoning_delta": "", "model": response_model})
	yield frappe._dict(
		{
			"event": "done",
			"model": response_model,
			"prompt_tokens": usage.prompt_tokens if usage else 0,
			"completion_tokens": usage.completion_tokens if usage else 0,
			"total_tokens": usage.total_tokens if usage else 0,
			"cost": _cost(usage),
		}
	)
