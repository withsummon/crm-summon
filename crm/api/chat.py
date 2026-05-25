import frappe
import json
from frappe import _

CLEFINCODE_API = "clefincode_chat.api.api_1_3_4.api"


def _clefin_api(method: str):
    return frappe.get_attr(f"{CLEFINCODE_API}.{method}")


def _resolve_contact(doctype: str, docname: str) -> str | None:
    if doctype == "Contact":
        return docname
    if doctype == "CRM Deal":
        return frappe.db.get_value("CRM Deal", docname, "contact")
    if doctype == "CRM Lead":
        lead = frappe.db.get_value("CRM Lead", docname,
            ["email", "mobile_no", "lead_name"], as_dict=True)
        if not lead:
            return None
        for field in ("email", "mobile_no"):
            val = lead.get(field)
            if val:
                row = frappe.db.sql("""
                    SELECT cp.contact FROM `tabClefinCode Chat Profile` cp
                    INNER JOIN `tabClefinCode Chat Profile Contact Details` cd
                        ON cd.parent = cp.name
                    WHERE cd.contact_info = %s AND cp.contact IS NOT NULL
                    LIMIT 1
                """, val, as_dict=True)
                if row and row[0].contact:
                    return row[0].contact
        return None
    if doctype == "CRM Organization":
        org = frappe.db.get_value("CRM Organization", docname,
            ["email", "phone"], as_dict=True)
        if org:
            for field in ("email", "phone"):
                val = org.get(field)
                if val:
                    row = frappe.db.sql("""
                        SELECT cp.contact FROM `tabClefinCode Chat Profile` cp
                        INNER JOIN `tabClefinCode Chat Profile Contact Details` cd
                            ON cd.parent = cp.name
                        WHERE cd.contact_info = %s AND cp.contact IS NOT NULL
                        LIMIT 1
                    """, val, as_dict=True)
                    if row and row[0].contact:
                        return row[0].contact
        return None
    return None


def _get_chat_profile_by_contact(contact: str) -> str | None:
    profiles = frappe.db.get_all("ClefinCode Chat Profile",
        filters={"contact": contact}, fields=["name"], limit=1)
    return profiles[0].name if profiles else None


def _create_chat_profile_for_contact(contact_name: str) -> str | None:
    contact = frappe.db.get_value("Contact", contact_name,
        ["first_name", "email_id", "mobile_no"], as_dict=True)
    if not contact:
        return None
    contact_details = []
    if contact.email_id:
        contact_details.append({
            "doctype": "ClefinCode Chat Profile Contact Details",
            "contact_info": contact.email_id,
            "type": "Chat",
            "verified": 1,
            "default": 1,
        })
        contact_details.append({
            "doctype": "ClefinCode Chat Profile Contact Details",
            "contact_info": contact.email_id,
            "type": "Email",
            "verified": 1,
            "default": 0,
        })
    if contact.mobile_no:
        contact_details.append({
            "doctype": "ClefinCode Chat Profile Contact Details",
            "contact_info": contact.mobile_no,
            "type": "WhatsApp",
            "verified": 1,
            "default": 0,
        })
    try:
        profile = frappe.get_doc({
            "doctype": "ClefinCode Chat Profile",
            "contact": contact_name,
            "full_name": contact.first_name or "Unknown",
            "contact_details": contact_details,
        })
        profile.insert(ignore_permissions=True)
        return profile.name
    except Exception:
        frappe.log_error(frappe.get_traceback(),
            f"CRM Chat - create profile for {contact_name}")
        return None


def _get_channels_for_profile(profile_id: str) -> list[dict]:
    channels = frappe.db.sql("""
        SELECT DISTINCT ch.name, ch.channel_name, ch.chat_status, ch.platform,
               ch.type, ch.creation_date, ch.last_message
        FROM `tabClefinCode Chat Channel` ch
        INNER JOIN `tabClefinCode Chat Channel User` mu ON mu.parent = ch.name
        WHERE mu.profile_id = %s
        ORDER BY ch.modified_date DESC
    """, profile_id, as_dict=True)
    for ch in channels:
        ch["member_count"] = frappe.db.count("ClefinCode Chat Channel User",
            filters={"parent": ch.name})
    return channels


def _get_or_create_contact_for_lead(lead_docname: str) -> str | None:
    lead = frappe.db.get_value("CRM Lead", lead_docname,
        ["lead_name", "email", "mobile_no", "phone"], as_dict=True)
    if not lead or not (lead.lead_name or lead.email or lead.mobile_no):
        return None

    contact_name = None
    if lead.email:
        contact_name = frappe.db.get_value("Contact",
            {"email_id": lead.email}, "name")
        if contact_name:
            return contact_name
    if not contact_name and lead.mobile_no:
        contact_name = frappe.db.get_value("Contact",
            {"mobile_no": lead.mobile_no}, "name")
        if contact_name:
            return contact_name
    try:
        contact = frappe.get_doc({
            "doctype": "Contact",
            "name": f"Lead-Contact-{lead_docname}",
            "first_name": lead.lead_name or "Unknown",
            "email_id": lead.email or "",
            "mobile_no": lead.mobile_no or "",
            "phone": lead.phone or "",
        })
        contact.insert(ignore_permissions=True)
        _create_chat_profile_for_contact(contact.name)
        return contact.name
    except frappe.DuplicateEntryError:
        existing = frappe.db.get_value("Contact",
            f"Lead-Contact-{lead_docname}", "name")
        if existing:
            _create_chat_profile_for_contact(existing)
        return existing if existing else None


@frappe.whitelist()
def resolve_record_channels(doctype: str, docname: str) -> dict:
    contact = _resolve_contact(doctype, docname)
    if not contact:
        if doctype == "CRM Lead":
            contact = _get_or_create_contact_for_lead(docname)
        if not contact:
            return {"channels": [], "contact": None, "profile": None}
    profile = _get_chat_profile_by_contact(contact)
    if not profile:
        profile = _create_chat_profile_for_contact(contact)
    if not profile:
        return {"channels": [], "contact": contact, "profile": None}
    channels = _get_channels_for_profile(profile)
    return {"channels": channels, "contact": contact, "profile": profile}


@frappe.whitelist()
def ensure_channel(doctype: str, docname: str) -> dict:
    result = resolve_record_channels(doctype, docname)
    if result.get("channels"):
        return {"channel": result["channels"][0], **result}
    contact = result.get("contact") or _resolve_contact(doctype, docname)
    if not contact and doctype == "CRM Lead":
        contact = _get_or_create_contact_for_lead(docname)
    if not contact:
        frappe.throw(_("No Contact found for this record"))
    profile = result.get("profile") or _get_chat_profile_by_contact(contact)
    current_user = frappe.session.user
    if profile:
        channel_name = f"CRM: {contact}"
        users = json.dumps([
            {"email": current_user, "platform": "Chat"},
            {"profile_id": profile, "email": "", "platform": "Chat"},
        ])
        try:
            channel_resp = _clefin_api("create_channel")(
                channel_name=channel_name, users=users, type="Direct",
                last_message="", creator_email=current_user, creator=current_user)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "CRM Chat - create_channel")
            return {"channel": None, "channels": [], "contact": contact, "profile": profile}
        if channel_resp and channel_resp.get("results"):
            channels = _get_channels_for_profile(profile)
            return {"channel": channels[0] if channels else None,
                    "channels": channels, "contact": contact, "profile": profile}
    return {"channel": None, "channels": [], "contact": contact, "profile": profile}


@frappe.whitelist()
def get_messages(doctype: str, docname: str, limit: int = 20, offset: int = 0) -> dict:
    result = resolve_record_channels(doctype, docname)
    if not result.get("channels"):
        return {"messages": [], "channels": result.get("channels", [])}
    channel = result["channels"][0]
    try:
        msg_data = _clefin_api("get_messages")(
            room=channel.name, user_email=frappe.session.user,
            room_type=channel.type, limit=limit, offset=offset)
        return {"messages": msg_data.get("results", []) if msg_data else [],
                "channel": channel}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "CRM Chat - get_messages")
        return {"messages": [], "error": str(e)}


@frappe.whitelist()
def send_message(doctype: str, docname: str, content: str) -> dict:
    if not content or not content.strip():
        frappe.throw(_("Message content is required"))
    result = ensure_channel(doctype, docname)
    channel = result.get("channel")
    if not channel:
        frappe.throw(_("Could not create a chat channel for this record"))
    current_user = frappe.session.user
    try:
        msg = _clefin_api("send")(
            content=content, user=frappe.session.user,
            room=channel.name, email=current_user, message_type="")
        frappe.publish_realtime("crm_chat_message_sent", {
            "doctype": doctype, "docname": docname,
            "channel": channel.name, "message": msg})
        return {"success": True, "message": msg}
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "CRM Chat - send_message")
        frappe.throw(_("Failed to send message"))
