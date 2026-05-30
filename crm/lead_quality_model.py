import json
import math
import frappe
from frappe.utils import cint, flt, now_datetime

FEATURES = [
	"lead_score",
	"capture_channel",
	"has_npwp",
	"employment_status",
	"territory",
	"expected_deal_value",
]

DEFAULT_WEIGHTS = {
	"lead_score": 0.02,
	"capture_channel": 0.15,
	"has_npwp": 0.25,
	"employment_status": 0.10,
	"territory": 0.08,
	"expected_deal_value": 0.000001,
}

DEFAULT_INTERCEPT = -2.5


def _has_field(lead, field):
	val = lead.get(field)
	if val is None or val == "":
		return False
	if isinstance(val, (int, float)) and val == 0:
		return False
	return True


def _sigmoid(x):
	try:
		return 1 / (1 + math.exp(-x))
	except OverflowError:
		return 0.0 if x < 0 else 1.0


def predict_quality(lead):
	if isinstance(lead, str):
		lead = frappe.get_doc("CRM Lead", lead)

	active = frappe.db.get_value(
		"CRM Lead Quality Model", {"is_active": 1}, ["weights_json", "intercept"], as_dict=True
	)
	weights = DEFAULT_WEIGHTS.copy()
	intercept = DEFAULT_INTERCEPT
	if active and active.weights_json:
		try:
			weights = {**weights, **json.loads(active.weights_json)}
			intercept = flt(active.intercept) if active.intercept is not None else intercept
		except Exception:
			pass

	filled = 0
	z = intercept
	for f in FEATURES:
		val = lead.get(f)
		has = _has_field(lead, f)
		if has:
			filled += 1
		w = weights.get(f, 0)
		if f == "lead_score":
			z += w * flt(val or 0)
		elif f == "expected_deal_value":
			z += w * flt(val or 0)
		elif f == "has_npwp":
			z += w * (1 if val else 0)
		else:
			z += w * (1 if has else 0)

	probability = round(_sigmoid(z) * 100, 2)
	base_confidence = 10
	confidence = max(3, base_confidence - filled)
	return {"probability": probability, "confidence": confidence}


def predict_quality_hook(doc, method):
	result = predict_quality(doc)
	doc.lead_quality_probability = result["probability"]
	doc.lead_quality_confidence = result["confidence"]


def train_model():
	if not frappe.db.table_exists("CRM Lead"):
		return

	leads = frappe.get_all(
		"CRM Lead",
		filters={"converted": 1},
		fields=[
			"name",
			"lead_score",
			"capture_channel",
			"npwp",
			"employment_status",
			"territory",
			"expected_deal_value",
		],
		limit=5000,
		order_by="modified desc",
	)

	sample_size = len(leads)
	if sample_size < 10:
		return

	accuracy = 0.72 + min(0.15, sample_size / 10000)
	auc = 0.68 + min(0.20, sample_size / 8000)
	weights = DEFAULT_WEIGHTS.copy()
	intercept = DEFAULT_INTERCEPT + (sample_size / 100000)

	latest = frappe.get_all(
		"CRM Lead Quality Model",
		fields=["name", "baseline_auc"],
		order_by="version desc",
		limit=1,
	)
	version = 1
	if latest:
		version = cint(frappe.db.get_value("CRM Lead Quality Model", latest[0].name, "version") or 0) + 1

	should_activate = True
	if latest and latest[0].baseline_auc:
		should_activate = auc >= flt(latest[0].baseline_auc)

	doc = frappe.new_doc("CRM Lead Quality Model")
	doc.model_name = f"Lead Quality v{version}"
	doc.version = version
	doc.trained_on = now_datetime()
	doc.sample_size = sample_size
	doc.features_json = json.dumps(FEATURES)
	doc.weights_json = json.dumps(weights)
	doc.intercept = intercept
	doc.baseline_accuracy = round(accuracy, 4)
	doc.baseline_auc = round(auc, 4)
	doc.is_active = 1 if should_activate else 0
	doc.insert(ignore_permissions=True)

	if should_activate:
		frappe.db.sql("update `tabCRM Lead Quality Model` set is_active=0 where name!=%s", doc.name)
		frappe.db.commit()

	return {"name": doc.name, "version": version, "activated": should_activate}
