from __future__ import annotations
import json, hashlib, hmac
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response, status

from app.models.payment.webhook_event import WebhookEvent
from app.services.payment.payment import PaymentService
from app.services.payment.subscription import SubscriptionService
from app.core.settings import settings

import logging
logger = logging.getLogger(__name__)


router = APIRouter()

def get_payment_service() -> PaymentService: return PaymentService()
def get_subscription_service() -> SubscriptionService: return SubscriptionService()

def _parse_iso8601(dt: Optional[str]) -> Optional[datetime]:
    if not dt:
        return None
    try:
        return datetime.fromisoformat(dt.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None

@router.post("/paystack")
async def paystack_webhook(
    request: Request,
    psvc: PaymentService = Depends(get_payment_service),
    ssvc: SubscriptionService = Depends(get_subscription_service),
):
    # Manually extract the signature header (case-insensitive)
    headers = dict(request.headers)
    x_paystack_signature = headers.get('x-paystack-signature') or headers.get('X-Paystack-Signature')
    
    logger.info(f"All headers keys: {list(headers.keys())}")
    logger.info(f"Extracted signature: {x_paystack_signature}")

    if not x_paystack_signature:
        logger.warning("Missing X-Paystack-Signature header")
        raise HTTPException(status_code=401, detail="Missing signature")
    
    # 1) Read raw body exactly as received
    raw = await request.body()
    body_str = raw.decode('utf-8')
    logger.info(f"Raw body length: {len(body_str)} characters")

    # 2) Compute HMAC-SHA512 with your Paystack SECRET (sk_test_* or sk_live_*)
    # secret = settings.PAYSTACK_SECRET_KEY
    # if not secret:
    #     raise HTTPException(status_code=500, detail="PAYSTACK_SECRET_KEY not configured")
    # computed = hmac.new(secret.encode("utf-8"), raw, hashlib.sha512).hexdigest()
    secret = settings.PAYSTACK_SECRET_KEY
    if not secret:
        logger.error("PAYSTACK_SECRET_KEY not configured")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    computed = hmac.new(secret.encode("utf-8"), raw, hashlib.sha512).hexdigest()
    logger.info(f"Computed signature: {computed}")
    logger.info(f"Received signature: {x_paystack_signature}")

    # 3) Compare with header
    # if not x_paystack_signature or not hmac.compare_digest(computed, x_paystack_signature):
    #     # Return 401 so Paystack will retry
    #     raise HTTPException(status_code=401, detail="Invalid webhook signature")
    if not hmac.compare_digest(computed, x_paystack_signature):
        logger.warning("Signature validation failed")
        logger.warning(f"Expected: {computed}")
        logger.warning(f"Received: {x_paystack_signature}")
        raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    logger.info("Signature validation successful")

    # 4) Safe to parse JSON now
    payload = json.loads(raw.decode("utf-8"))
    event: str = payload.get("event") or ""
    data: dict = payload.get("data") or {}

    # 5) Idempotency guard (unique index on event_key)
    unique_id = str(data.get("id") or data.get("reference") or f"{event}:{data.get('reference')}")
    try:
        await WebhookEvent(event_key=unique_id, payload=payload).insert()
    except Exception:
        # Already processed; still ACK with 200 so Paystack stops retrying
        return Response(status_code=200)

    # 6) Your business logic
    gateway_paid_at = _parse_iso8601(data.get("paid_at"))
    webhook_received_at = datetime.now(timezone.utc)

    if event == "charge.success":
        reference = data.get("reference")
        metadata = data.get("metadata") or {}
        mtype = metadata.get("type")

        if reference:
            await psvc.mark_webhook_observed(
                reference=reference,
                gateway_paid_at=gateway_paid_at,
                webhook_received_at=webhook_received_at,
                raw=data,
            )

        if mtype == "pos_payment" and reference:
            await psvc.verify(reference, gateway_paid_at=gateway_paid_at)

        elif mtype == "subscription_first_charge":
            auth = data.get("authorization") or {}
            authorization_code = auth.get("authorization_code")
            customer = data.get("customer") or {}
            email = customer.get("email") or metadata.get("customer_email")
            plan_code = metadata.get("plan_code")
            tenant_id_str = metadata.get("tenant_id")
            if authorization_code and email and plan_code and tenant_id_str:
                await ssvc.activate_from_webhook(
                    tenant_id=tenant_id_str,
                    email=email,
                    plan_code=plan_code,
                    authorization_code=authorization_code,
                    activated_at=gateway_paid_at or webhook_received_at,
                )

    return Response(status_code=200)