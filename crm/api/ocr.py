import json
import re

import frappe
from frappe import _

from crm.ai.kimi import call_kimi_chat, get_ai_settings


def _get_ocr_prompt(document_type):
    prompts = {
        "KTP": (
            "Extract all information from this Indonesian KTP (Identity Card) image. "
            "Return ONLY valid JSON with these fields: nik, nama, tempat_lahir, tanggal_lahir, "
            "jenis_kelamin, golongan_darah, alamat, rt_rw, kel_desa, kecamatan, "
            "agama, status_perkawinan, pekerjaan, kewarganegaraan, berlaku_hingga. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
        "NPWP": (
            "Extract all information from this Indonesian NPWP (Tax ID) card image. "
            "Return ONLY valid JSON with these fields: npwp_number, name, address. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
        "KK": (
            "Extract all information from this Indonesian KK (Family Card) image. "
            "Return ONLY valid JSON with these fields: nomor_kk, kepala_keluarga, alamat, "
            "rt_rw, kel_desa, kecamatan, kabupaten_kota, provinsi, kode_pos. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
        "Akta": (
            "Extract all information from this Indonesian Akta (Certificate/Legal Document) image. "
            "Return ONLY valid JSON with the relevant fields found. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
        "SHM": (
            "Extract all information from this Indonesian SHM (Certificate of Ownership) image. "
            "Return ONLY valid JSON with these fields: nomor_sertifikat, atas_nama, "
            "luas_tanah, luas_bangunan, alamat, kel_desa, kecamatan. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
        "Sertifikat": (
            "Extract all information from this Indonesian Sertifikat (Certificate) image. "
            "Return ONLY valid JSON with the relevant fields found. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
        "business_card": (
            "Extract business card information from this image. "
            "Return ONLY valid JSON with these fields: name, phone, email, company, position, website, address. "
            "Use null for any field not visible. Do not include any text outside the JSON."
        ),
    }
    return prompts.get(document_type, (
        "Extract all visible text and information from this document image. "
        "Return ONLY valid JSON with the relevant fields found. "
        "Use null for any field not visible. Do not include any text outside the JSON."
    ))


def _clean_base64(data_url):
    if not data_url:
        return None
    if "," in data_url:
        return data_url.split(",", 1)[1]
    return data_url


def _extract_json(text):
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        text = match.group(1)
    text = text.strip()
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    brace_depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if start == -1:
                start = i
            brace_depth += 1
        elif ch == "}":
            brace_depth -= 1
            if brace_depth == 0 and start != -1:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    pass
    try:
        return {"extracted_text": text}
    except Exception:
        return {"extracted_text": text}


@frappe.whitelist()
def scan_document(image_data=None, image_url=None, document_type="KTP"):
    if not image_data and not image_url:
        frappe.throw(_("image_data or image_url is required"))

    if image_data:
        base64_data = _clean_base64(image_data)
    elif image_url:
        file_path = frappe.get_site_path(image_url.lstrip("/"))
        try:
            with open(file_path, "rb") as f:
                import base64
                base64_data = base64.b64encode(f.read()).decode("utf-8")
        except Exception:
            frappe.throw(_("Could not read file at {0}").format(image_url))

    settings = get_ai_settings()
    prompt = _get_ocr_prompt(document_type)

    messages = [
        {"role": "system", "content": "You are a precise OCR assistant for Indonesian documents. Extract text and return JSON only."},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_data}"}},
            {"type": "text", "text": prompt},
        ]},
    ]

    result = call_kimi_chat(messages, thinking_mode=settings.kimi_thinking_mode or "disabled")
    parsed = _extract_json(result.content)

    return {
        "extracted": parsed,
        "raw_text": result.content,
        "document_type": document_type,
        "model": result.model,
        "tokens": result.total_tokens,
    }


@frappe.whitelist()
def scan_business_card(image_data=None, image_url=None):
    result = scan_document(
        image_data=image_data,
        image_url=image_url,
        document_type="business_card",
    )
    extracted = result.get("extracted", {})
    return {
        "name": extracted.get("name") or extracted.get("nama") or "",
        "phone": extracted.get("phone") or extracted.get("telepon") or extracted.get("no_telepon") or "",
        "email": extracted.get("email") or "",
        "company": extracted.get("company") or extracted.get("perusahaan") or "",
        "position": extracted.get("position") or extracted.get("jabatan") or "",
        "website": extracted.get("website") or "",
        "address": extracted.get("address") or extracted.get("alamat") or "",
        "raw_text": result.get("raw_text", ""),
    }
