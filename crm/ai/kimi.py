import json
from decimal import Decimal

import frappe
from frappe import _
import requests


KIMI_BASE_URL = "https://api.moonshot.ai/v1"
KIMI_CHAT_URL = f"{KIMI_BASE_URL}/chat/completions"
DEFAULT_KIMI_MODEL = "kimi-k2.6"
KIMI_MODEL_ALIASES = {
	"kimi-k2": DEFAULT_KIMI_MODEL,
	"kimi-k2-latest": DEFAULT_KIMI_MODEL,
	"kimi k2.6": DEFAULT_KIMI_MODEL,
}


def normalize_kimi_model(model=None):
	model = (model or DEFAULT_KIMI_MODEL).strip()
	return KIMI_MODEL_ALIASES.get(model.lower(), model)


def get_ai_settings():
	settings = frappe._dict(
		{
			"provider": "Kimi",
			"kimi_model": DEFAULT_KIMI_MODEL,
			"kimi_base_url": KIMI_BASE_URL,
			"kimi_api_key": None,
			"rag_storage_path": "",
			"local_embedding_model": "BAAI/bge-m3",
			"guardrail_confidence_threshold": 0.45,
			"daily_cost_limit_usd": 25,
			"thinking_mode": "disabled",
		}
	)
	try:
		doc = frappe.get_doc("FCRM Settings")
		settings.provider = doc.get("ai_provider") or "Kimi"
		settings.kimi_model = normalize_kimi_model(doc.get("kimi_model"))
		settings.kimi_base_url = (doc.get("kimi_base_url") or KIMI_BASE_URL).rstrip("/")
		settings.kimi_api_key = doc.get_password("kimi_api_key") or doc.get_password("moonshot_api_key")
		settings.rag_storage_path = doc.get("rag_storage_path") or ""
		settings.local_embedding_model = doc.get("local_embedding_model") or "BAAI/bge-m3"
		val = doc.get("guardrail_confidence_threshold")
		settings.guardrail_confidence_threshold = float(val) if (val is not None and val != "") else 0.45
		cost_limit = doc.get("daily_cost_limit_usd")
		settings.daily_cost_limit_usd = float(cost_limit) if (cost_limit is not None and cost_limit != "") else 25.0
		settings.thinking_mode = doc.get("kimi_thinking_mode") or "disabled"
	except Exception:
		pass
	return settings


def estimate_kimi_cost(tokens: int) -> Decimal:
	# Conservative estimate for spend visibility when exact pricing is not configured.
	return Decimal(tokens or 0) * Decimal("0.000012")


def call_kimi_chat(messages, model=None, tools=None, thinking_mode="disabled", timeout=60):
	settings = get_ai_settings()
	api_key = (settings.kimi_api_key or "").strip()
	if not api_key or "******" in api_key:
		frappe.throw(_("Kimi/Moonshot API key is not configured in FCRM Settings."))

	base_url = (settings.kimi_base_url or KIMI_BASE_URL).rstrip("/")
	payload = {
		"model": normalize_kimi_model(model or settings.kimi_model),
		"messages": messages,
	}
	if tools:
		payload["tools"] = tools
		payload["tool_choice"] = "auto"
	if thinking_mode:
		payload["thinking"] = {"type": thinking_mode}

	response = requests.post(
		f"{base_url}/chat/completions",
		headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
		data=json.dumps(payload),
		timeout=timeout,
	)
	if response.status_code >= 400:
		frappe.log_error(response.text, "Kimi API Error")
		frappe.throw(_("Kimi API rejected the request: {0}").format(response.text[:500]))

	data = response.json()
	usage = data.get("usage") or {}
	content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
	return frappe._dict(
		{
			"content": content,
			"raw": data,
			"model": data.get("model") or payload["model"],
			"prompt_tokens": usage.get("prompt_tokens") or 0,
			"completion_tokens": usage.get("completion_tokens") or 0,
			"total_tokens": usage.get("total_tokens") or 0,
			"cost": estimate_kimi_cost(usage.get("total_tokens") or 0),
		}
	)


def stream_kimi_chat_events(messages, model=None, tools=None, thinking_mode="disabled", timeout=120):
	settings = get_ai_settings()
	api_key = (settings.kimi_api_key or "").strip()
	if not api_key or "******" in api_key:
		frappe.throw(_("Kimi/Moonshot API key is not configured in FCRM Settings."))

	base_url = (settings.kimi_base_url or KIMI_BASE_URL).rstrip("/")
	payload = {
		"model": normalize_kimi_model(model or settings.kimi_model),
		"messages": messages,
		"stream": True,
		"stream_options": {"include_usage": True},
	}
	if tools:
		payload["tools"] = tools
		payload["tool_choice"] = "auto"
	if thinking_mode:
		payload["thinking"] = {"type": thinking_mode}

	response = requests.post(
		f"{base_url}/chat/completions",
		headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
		data=json.dumps(payload),
		timeout=timeout,
		stream=True,
	)
	if response.status_code >= 400:
		frappe.log_error(response.text, "Kimi API Error")
		frappe.throw(_("Kimi API rejected the request: {0}").format(response.text[:500]))

	usage = {}
	response_model = payload["model"]
	for raw_line in response.iter_lines(decode_unicode=True):
		if not raw_line:
			continue
		line = raw_line.strip()
		if line.startswith("data:"):
			line = line[5:].strip()
		if not line or line == "[DONE]":
			continue
		try:
			data = json.loads(line)
		except Exception:
			continue
		response_model = data.get("model") or response_model
		if data.get("usage"):
			usage = data.get("usage") or usage
		delta = (((data.get("choices") or [{}])[0].get("delta") or {}).get("content")) or ""
		if delta:
			yield frappe._dict({"event": "delta", "delta": delta, "model": response_model, "usage": usage})

	total_tokens = usage.get("total_tokens") or 0
	yield frappe._dict(
		{
			"event": "done",
			"model": response_model,
			"prompt_tokens": usage.get("prompt_tokens") or 0,
			"completion_tokens": usage.get("completion_tokens") or 0,
			"total_tokens": total_tokens,
			"cost": estimate_kimi_cost(total_tokens),
		}
	)
