#!/usr/bin/env python3
"""
Brevo API - All Use Cases in Python

This script demonstrates every major use case of the Brevo API.
See: https://developers.brevo.com/docs/getting-started

Usage:
    1. Set BREVO_API_KEY in .env or environment
    2. Run: python brevo_all_use_cases.py

Note: Some use cases require setup in Brevo dashboard (senders, templates,
      WhatsApp activation, etc.). Replace placeholders with your actual values.
"""

import os
import json
from pathlib import Path
from typing import Any, Optional

# Load .env - try dotenv first, then manual fallback
_env_dir = Path(__file__).resolve().parent
try:
    from dotenv import load_dotenv
    load_dotenv(_env_dir / ".env")
except ImportError:
    pass

# Fallback: read .env manually (ensures vars load even if dotenv path is wrong)
_env_file = _env_dir / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                key, val = key.strip(), val.strip().strip('"').strip("'")
                if val:
                    os.environ[key] = val

import httpx

# Configuration
BASE_URL = "https://api.brevo.com"
API_KEY = os.getenv("BREVO_API_KEY") or os.getenv("BREVO_WEBHOOK_SECRET")
HTTPX_TIMEOUT = 15.0  # seconds - prevents hanging on slow endpoints

# Default values - set in .env: BREVO_SENDER_EMAIL, BREVO_TEST_EMAIL, BREVO_TEST_PHONE
DEFAULT_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL", "hello@example.com")
DEFAULT_SENDER_NAME = os.getenv("BREVO_SENDER_NAME", "Your Company")
DEFAULT_RECIPIENT_EMAIL = os.getenv("BREVO_TEST_EMAIL", "test@example.com")
DEFAULT_RECIPIENT_NAME = os.getenv("BREVO_TEST_USER", "Test User")
DEFAULT_RECIPIENT_PHONE = os.getenv("BREVO_TEST_PHONE")  # e.g. 919876543210 (country code, no spaces)


def get_headers() -> dict:
    """API request headers with authentication."""
    if not API_KEY:
        raise ValueError(
            "Set BREVO_API_KEY or BREVO_WEBHOOK_SECRET in .env "
            "(get key from https://app.brevo.com/settings/keys/api)"
        )
    return {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": API_KEY,
    }


def print_result(name: str, response: httpx.Response, data: Any = None):
    """Pretty-print API result."""
    status = "✅" if response.is_success else "❌"
    print(f"\n{status} {name}")
    print(f"   Status: {response.status_code}")
    if data is not None:
        print(f"   Response: {json.dumps(data, indent=2)[:500]}{'...' if len(json.dumps(data)) > 500 else ''}")


def _http_client():
    """Shared HTTP client with timeout."""
    return httpx.Client(timeout=HTTPX_TIMEOUT)


# =============================================================================
# 1. ACCOUNT MANAGEMENT
# =============================================================================

def get_account() -> dict | None:
    """Get account information - validates API key and returns plan details."""
    with _http_client() as client:
        response = client.get(f"{BASE_URL}/v3/account", headers=get_headers())
        data = response.json() if response.content else {}
        print_result("Get Account", response, data)
        return data if response.is_success else None


# =============================================================================
# 2. TRANSACTIONAL EMAILS (Messaging API)
# =============================================================================

def send_transactional_email_html(
    to_email: str = DEFAULT_RECIPIENT_EMAIL,
    to_name: str = DEFAULT_RECIPIENT_NAME,
    subject: str = "Hello from Brevo!",
    html_content: str = "<html><body><p>Hello,</p><p>This is a transactional email.</p></body></html>",
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> dict | None:
    """Send transactional email with HTML content."""
    se, sn = sender_email or DEFAULT_SENDER_EMAIL, sender_name or DEFAULT_SENDER_NAME
    payload = {
        "sender": {"name": sn, "email": se},
        "to": [{"email": to_email, "name": to_name}],
        "subject": subject,
        "htmlContent": html_content,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/smtp/email",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send Transactional Email (HTML)", response, data)
        return data if response.is_success else None


def send_transactional_email_text(
    to_email: str = DEFAULT_RECIPIENT_EMAIL,
    subject: str = "Plain text email from Brevo",
    text_content: str = "Hello. This is a plain text transactional email.",
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> dict | None:
    """Send transactional email with plain text content."""
    se, sn = sender_email or DEFAULT_SENDER_EMAIL, sender_name or DEFAULT_SENDER_NAME
    payload = {
        "sender": {"name": sn, "email": se},
        "to": [{"email": to_email}],
        "subject": subject,
        "textContent": text_content,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/smtp/email",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send Transactional Email (Text)", response, data)
        return data if response.is_success else None


def send_transactional_email_template(
    template_id: int,
    to_email: str = DEFAULT_RECIPIENT_EMAIL,
    params: Optional[dict] = None,
) -> dict | None:
    """Send transactional email using a template ID."""
    payload = {
        "sender": {"name": DEFAULT_SENDER_NAME, "email": DEFAULT_SENDER_EMAIL},
        "to": [{"email": to_email}],
        "templateId": template_id,
        "params": params or {},
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/smtp/email",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send Transactional Email (Template)", response, data)
        return data if response.is_success else None


def send_transactional_email_dynamic(
    to_email: str = DEFAULT_RECIPIENT_EMAIL,
    params: dict = None,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> dict | None:
    """Send transactional email with dynamic variables (params)."""
    params = params or {"trackingCode": "JD01460000300002350000", "estimatedArrival": "Tomorrow"}
    html = f"<html><body><p>Your delivery is expected {params.get('estimatedArrival')}. "
    html += f"Tracking code: {params.get('trackingCode')}</p></body></html>"
    se, sn = sender_email or DEFAULT_SENDER_EMAIL, sender_name or DEFAULT_SENDER_NAME
    payload = {
        "sender": {"name": sn, "email": se},
        "to": [{"email": to_email}],
        "subject": "Order Update - Dynamic Content",
        "params": params,
        "htmlContent": html,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/smtp/email",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send Transactional Email (Dynamic)", response, data)
        return data if response.is_success else None


def send_transactional_email_with_tags(
    to_email: str = DEFAULT_RECIPIENT_EMAIL,
    tags: list[str] = None,
    sender_email: Optional[str] = None,
    sender_name: Optional[str] = None,
) -> dict | None:
    """Send transactional email with tags for webhook tracking."""
    tags = tags or ["order_confirmation", "transactional_v1"]
    se, sn = sender_email or DEFAULT_SENDER_EMAIL, sender_name or DEFAULT_SENDER_NAME
    payload = {
        "sender": {"name": sn, "email": se},
        "to": [{"email": to_email}],
        "subject": "Order Confirmation (Tagged)",
        "textContent": "Thank you for your order. You can track delivery via webhooks.",
        "tags": tags,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/smtp/email",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send Transactional Email (with Tags)", response, data)
        return data if response.is_success else None


# =============================================================================
# 3. SMS (Messaging API)
# =============================================================================

def send_transactional_sms(
    recipient: str,
    content: str = "Hello! This is a transactional SMS from Brevo.",
    sender: str = "Brevo",
    tag: Optional[str] = None,
) -> dict | None:
    """
    Send transactional SMS.
    recipient: Phone number with country code, no spaces (e.g. 4915778559164)
    sender: Max 11 alphanumeric or 15 numeric chars
    """
    payload = {
        "sender": sender,
        "recipient": recipient,
        "content": content,
        "type": "transactional",
    }
    if tag:
        payload["tag"] = tag
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/transactionalSMS/send",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send Transactional SMS", response, data)
        return data if response.is_success else None


# =============================================================================
# 4. WHATSAPP (Messaging API) - Requires WhatsApp activation in Brevo
# =============================================================================

def send_whatsapp_message_template(
    contact_numbers: list[str],
    template_id: int,
    sender_number: str,
) -> dict | None:
    """Send WhatsApp message using a template. First message must use template."""
    payload = {
        "contactNumbers": contact_numbers,
        "templateId": template_id,
        "senderNumber": sender_number,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/whatsapp/sendMessage",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send WhatsApp (Template)", response, data)
        return data if response.is_success else None


def send_whatsapp_message_text(
    contact_numbers: list[str],
    text: str,
    sender_number: str,
) -> dict | None:
    """Send WhatsApp message as plain text (when conversation exists)."""
    payload = {
        "contactNumbers": contact_numbers,
        "text": text,
        "senderNumber": sender_number,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/whatsapp/sendMessage",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Send WhatsApp (Text)", response, data)
        return data if response.is_success else None


def get_whatsapp_statistics(
    limit: int = 50,
    offset: int = 0,
    days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict | None:
    """Get WhatsApp event statistics (last 30 days by default)."""
    params = {"limit": limit, "offset": offset}
    if days:
        params["days"] = days
    elif start_date and end_date:
        params["startDate"] = start_date
        params["endDate"] = end_date
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/whatsapp/statistics/events",
            headers=get_headers(),
            params=params,
        )
        data = response.json() if response.content else {}
        print_result("Get WhatsApp Statistics", response, data)
        return data if response.is_success else None


# =============================================================================
# 5. CONTACTS
# =============================================================================

def create_contact(
    email: str = DEFAULT_RECIPIENT_EMAIL,
    attributes: Optional[dict] = None,
    list_ids: Optional[list[int]] = None,
    update_enabled: bool = False,
) -> dict | None:
    """Create a new contact. Pass email, or SMS in attributes, or ext_id."""
    payload = {
        "email": email,
        "attributes": attributes or {"FIRSTNAME": "John", "LASTNAME": "Doe"},
        "updateEnabled": update_enabled,
    }
    if list_ids:
        payload["listIds"] = list_ids
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/contacts",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Create Contact", response, data)
        return data if response.is_success else None


def get_contact(identifier: str) -> dict | None:
    """Get contact by email or ID."""
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/contacts/{identifier}",
            headers=get_headers(),
        )
        data = response.json() if response.content else {}
        print_result("Get Contact", response, data)
        return data if response.is_success else None


def get_contacts_list(
    limit: int = 50,
    offset: int = 0,
) -> dict | None:
    """Get paginated list of contacts."""
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/contacts",
            headers=get_headers(),
            params={"limit": limit, "offset": offset},
        )
        data = response.json() if response.content else {}
        print_result("Get Contacts List", response, {"count": data.get("count"), "contacts": len(data.get("contacts", []))})
        return data if response.is_success else None


def add_contact_to_list(
    list_id: int,
    emails: Optional[list[str]] = None,
    ids: Optional[list[int]] = None,
) -> dict | None:
    """Add contacts to a list. Pass emails, ids, or extIds (max 150 per request)."""
    payload = {}
    if emails:
        payload["emails"] = emails
    if ids:
        payload["ids"] = ids
    if not payload:
        raise ValueError("Provide emails or ids")
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/contacts/lists/{list_id}/contacts/add",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Add Contact to List", response, data)
        return data if response.is_success else None


# =============================================================================
# 6. CONTACT LISTS
# =============================================================================

def get_contact_lists(
    limit: int = 50,
    offset: int = 0,
) -> dict | None:
    """Get all contact lists."""
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/contacts/lists",
            headers=get_headers(),
            params={"limit": limit, "offset": offset},
        )
        data = response.json() if response.content else {}
        print_result("Get Contact Lists", response, data)
        return data if response.is_success else None


# =============================================================================
# 7. SENDERS (Account management)
# =============================================================================

def get_senders(ip: Optional[str] = None, domain: Optional[str] = None) -> dict | None:
    """Get list of senders."""
    params = {}
    if ip:
        params["ip"] = ip
    if domain:
        params["domain"] = domain
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/senders",
            headers=get_headers(),
            params=params or None,
        )
        data = response.json() if response.content else {}
        print_result("Get Senders", response, data)
        return data if response.is_success else None


def _get_first_sender() -> tuple[str, str] | None:
    """Fetch first verified sender from account. Returns (email, name) or None."""
    try:
        with _http_client() as client:
            r = client.get(f"{BASE_URL}/v3/senders", headers=get_headers())
            if r.is_success and r.content:
                data = r.json()
                senders = data.get("senders") if isinstance(data, dict) else data
                if senders and len(senders) > 0:
                    s = senders[0]
                    email = s.get("email") or ""
                    name = s.get("name") or "Sender"
                    if email and "@" in email:
                        return (email, name)
    except Exception:
        pass
    return None


def create_sender(
    name: str,
    email: str,
    ips: Optional[list[dict]] = None,
) -> dict | None:
    """Create a new sender. Verification email sent to address."""
    payload = {"name": name, "email": email}
    if ips:
        payload["ips"] = ips
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/senders",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Create Sender", response, data)
        return data if response.is_success else None


# =============================================================================
# 8. WEBHOOKS
# =============================================================================

def get_webhooks() -> dict | None:
    """Get all webhooks (transactional + marketing). Max 40 total."""
    with _http_client() as client:
        # Transactional webhooks
        response = client.get(
            f"{BASE_URL}/v3/webhooks",
            headers=get_headers(),
            params={"type": "transactional"},
        )
        data = response.json() if response.content else {}
        print_result("Get Webhooks (Transactional)", response, data)
        if not response.is_success:
            return None
        return data


def create_webhook(
    url: str,
    description: str = "Python API webhook",
    events: Optional[list[str]] = None,
) -> dict | None:
    """Create a transactional webhook. events: sent, delivered, opened, etc."""
    events = events or ["delivered", "opened", "clicked"]
    payload = {
        "url": url,
        "description": description,
        "events": events,
    }
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/webhooks",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Create Webhook", response, data)
        return data if response.is_success else None


# =============================================================================
# 9. SMTP TEMPLATES
# =============================================================================

def get_smtp_templates(template_status: str = "true") -> dict | None:
    """Get SMTP (transactional) templates."""
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/smtp/templates",
            headers=get_headers(),
            params={"templateStatus": template_status},
        )
        data = response.json() if response.content else {}
        print_result("Get SMTP Templates", response, {"count": len(data.get("templates", []))})
        return data if response.is_success else None


# =============================================================================
# 10. ECOMMERCE
# =============================================================================

def activate_ecommerce() -> dict | None:
    """Activate eCommerce app in Brevo. Enables product/order sync."""
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/ecommerce/activate",
            headers=get_headers(),
        )
        data = response.json() if response.content else {}
        print_result("Activate eCommerce", response, data)
        return data if response.is_success else None


# =============================================================================
# 11. CUSTOM EVENTS (Tracking)
# =============================================================================

def track_event(
    email: str,
    event_name: str,
    properties: Optional[dict] = None,
    event_data: Optional[dict] = None,
) -> dict | None:
    """
    Track custom event via Brevo.
    Uses the Track API - may require different endpoint/format.
    """
    # Brevo tracking API
    track_url = "https://in-automate.brevo.com/api/v2/trackEvent"
    payload = {
        "email": email,
        "event": event_name,
        "properties": properties or {},
        "eventdata": event_data or {},
    }
    with _http_client() as client:
        response = client.post(
            track_url,
            headers={"Content-Type": "application/json", "api-key": API_KEY},
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result("Track Custom Event", response, data)
        return data if response.is_success else None


# =============================================================================
# 12. CUSTOM OBJECTS (Enterprise/Pro plans only)
# =============================================================================

def upsert_custom_object_records(
    object_type: str,
    records: list[dict],
) -> dict | None:
    """
    Create or update custom object records in bulk.
    object_type must exist in your schema. Max 1000 records per request.
    """
    payload = {"records": records}
    with _http_client() as client:
        response = client.post(
            f"{BASE_URL}/v3/objects/{object_type}/batch/upsert",
            headers=get_headers(),
            json=payload,
        )
        data = response.json() if response.content else {}
        print_result(f"Upsert Custom Objects ({object_type})", response, data)
        return data if response.is_success else None


def get_custom_object_records(
    object_type: str,
    limit: int = 50,
    sort: str = "desc",
) -> dict | None:
    """Get paginated records for a custom object type."""
    with _http_client() as client:
        response = client.get(
            f"{BASE_URL}/v3/objects/{object_type}/records",
            headers=get_headers(),
            params={"limit": limit, "sort": sort},
        )
        data = response.json() if response.content else {}
        print_result(f"Get Custom Object Records ({object_type})", response, data)
        return data if response.is_success else None


# =============================================================================
# MAIN - Run reliable use cases only (with error handling)
# =============================================================================

def _safe_run(name: str, fn, *args, **kwargs):
    """Run a use case; print and continue on any error."""
    try:
        fn(*args, **kwargs)
    except Exception as e:
        print(f"\n⏭️  {name}: skipped ({type(e).__name__}: {e})")


def run_all(skip_destructive: bool = True):
    """
    Execute reliable Brevo use cases. Each call is wrapped in try/except.
    Skips: eCommerce (often times out), Custom Objects (Enterprise only).
    Set skip_destructive=False to run email/SMS/WhatsApp sends.
    """
    print("=" * 60)
    print("Brevo API - Reliable Use Cases")
    print("=" * 60)

    # 1. Account
    _safe_run("Get Account", get_account)

    # 2. Transactional emails (only if not skip_destructive and we have a sender)
    if not skip_destructive:
        sender = _get_first_sender()
        env_sender = DEFAULT_SENDER_EMAIL if "@" in DEFAULT_SENDER_EMAIL and "example" not in DEFAULT_SENDER_EMAIL and "yourdomain" not in DEFAULT_SENDER_EMAIL else None
        sender_tuple = sender or (env_sender and (env_sender, DEFAULT_SENDER_NAME))
        if sender_tuple:
            se, sn = sender_tuple
            _safe_run("Send Email (HTML)", send_transactional_email_html, sender_email=se, sender_name=sn)
            _safe_run("Send Email (Text)", send_transactional_email_text, sender_email=se, sender_name=sn)
            _safe_run("Send Email (Dynamic)", send_transactional_email_dynamic, sender_email=se, sender_name=sn)
            _safe_run("Send Email (Tags)", send_transactional_email_with_tags, sender_email=se, sender_name=sn)
        else:
            print("\n⏭️  No sender: Create one at https://app.brevo.com/senders (or add BREVO_SENDER_EMAIL to .env)")
    else:
        print("\n⏭️  Skipping email sends (skip_destructive=True)")

    # 3. SMS - runs if BREVO_TEST_PHONE is set in .env
    if not skip_destructive and DEFAULT_RECIPIENT_PHONE:
        _safe_run("Send SMS", send_transactional_sms, DEFAULT_RECIPIENT_PHONE)
    elif not skip_destructive:
        print("\n⏭️  SMS: Add BREVO_TEST_PHONE to .env (e.g. 919876543210) to try")
    elif skip_destructive:
        print("\n⏭️  Skipping SMS (skip_destructive=True)")

    # 4. WhatsApp - requires template ID + sender; call send_whatsapp_message_template() manually

    # 5–6. Contacts & Lists (reliable)
    _safe_run("Get Contacts", get_contacts_list, 5)
    _safe_run("Get Contact Lists", get_contact_lists, 5)

    # 7. Senders
    _safe_run("Get Senders", get_senders)

    # 8. Webhooks
    _safe_run("Get Webhooks", get_webhooks)

    # 9. SMTP Templates
    _safe_run("Get SMTP Templates", get_smtp_templates)

    # eCommerce, Custom Objects, Track - skipped (unreliable/slow or need setup)
    print("\n⏭️  Skipped: eCommerce (often times out), Custom Objects (Enterprise), Track")

    print("\n" + "=" * 60)
    print("Done. Set skip_destructive=False to run email sends.")
    print("=" * 60)


if __name__ == "__main__":
    run_all(skip_destructive=False)  # Set True to skip sends (emails, SMS)
