import secrets
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from .models import DeveloperAPIKey, WebhookEndpoint

API_KEY_SCOPES = [
    "products:read",
    "orders:read",
    "orders:write",
    "payments:read",
    "courses:read",
    "webhooks:manage",
    "profile:read",
]

WEBHOOK_EVENTS = [
    "order.created",
    "order.paid",
    "order.cancelled",
    "payment.succeeded",
    "payment.failed",
    "delivery.assigned",
    "delivery.failed",
    "return.requested",
    "refund.approved",
    "product.approved",
    "product.rejected",
    "course.enrolled",
]

def generate_api_key(environment):
    raw_secret = secrets.token_urlsafe(32)
    prefix = f"ck_{environment}_{raw_secret[:12]}"
    full_key = f"{prefix}_{raw_secret}"
    return prefix, full_key

def create_api_key(*, owner, name, environment, scopes, expires_at=None):
    valid_scopes = [s for s in scopes if s in API_KEY_SCOPES]
    
    prefix, full_key = generate_api_key(environment)

    api_key = DeveloperAPIKey.objects.create(
        owner=owner,
        name=name,
        key_prefix=prefix,
        hashed_key=make_password(full_key),
        environment=environment,
        scopes=valid_scopes,
        expires_at=expires_at,
    )

    return api_key, full_key

def verify_api_key(raw_key):
    try:
        key_prefix = "_".join(raw_key.split("_")[:3])
        api_key = DeveloperAPIKey.objects.get(key_prefix=key_prefix, is_active=True)
    except DeveloperAPIKey.DoesNotExist:
        return None

    if api_key.expires_at and api_key.expires_at < timezone.now():
        return None

    if check_password(raw_key, api_key.hashed_key):
        api_key.last_used_at = timezone.now()
        api_key.request_count += 1
        api_key.save(update_fields=["last_used_at", "request_count"])
        return api_key

    return None

def revoke_api_key(api_key):
    api_key.is_active = False
    api_key.revoked_at = timezone.now()
    api_key.save(update_fields=["is_active", "revoked_at"])
    return api_key

def create_webhook_endpoint(*, owner, url, description, events):
    valid_events = [e for e in events if e in WEBHOOK_EVENTS] or ["*"] if "*" in events else []
    secret = "whsec_" + secrets.token_hex(24)
    
    endpoint = WebhookEndpoint.objects.create(
        owner=owner,
        url=url,
        description=description,
        events=valid_events,
        secret=secret,
    )
    return endpoint

import hmac
import hashlib
import json

def sign_webhook_payload(payload_dict, secret):
    """
    Generate an HMAC SHA256 signature for a webhook payload.
    """
    payload_str = json.dumps(payload_dict, separators=(',', ':'))
    signature = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload_str.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    
    return payload_str, f"sha256={signature}"
