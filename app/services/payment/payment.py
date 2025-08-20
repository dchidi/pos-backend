from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4


from fastapi import HTTPException


from app.constants import Currency, to_minor_units
from app.models.payment.payment import Payment
from app.gateways.paystack_cleint import PaystackClient


class PaymentService:
  def __init__(self, gateway: Optional[PaystackClient] = None):
    self.gateway = gateway or PaystackClient()

  async def initialize(
      self, *, tenant_id, customer_email: str, customer_name: Optional[str], 
      currency: Currency, items: list[Dict[str, Any]], callback_url: Optional[str], 
      reference: Optional[str], metadata: Dict[str, Any]
  ) -> Dict[str, Any]:
    if not items:
      raise HTTPException(400, "Cart items cannot be empty")
    amount_major = sum(float(i["quantity"]) * float(i["unit_price"]) for i in items)
    amount_minor = to_minor_units(amount_major, currency)
    ref = reference or f"{tenant_id}-{uuid4()}"
    full_meta = {
      "tenant_id": str(tenant_id), "customer_email": customer_email, 
      "customer_name": customer_name, "items": items, "type": "pos_payment", **(metadata or {})
    }


    data = await self.gateway.initialize_transaction(
      email=customer_email, amount_minor=amount_minor, reference=ref, 
      callback_url=callback_url, currency=currency, metadata=full_meta
    )


    await Payment(
      reference=ref, tenant_id=tenant_id, customer_email=customer_email, 
      amount_minor=amount_minor, currency=currency, status="initialized", 
      authorization_url=data.get("authorization_url"), metadata=full_meta
    ).insert()

    return {
      "reference": ref, "authorization_url": data["authorization_url"], 
      "access_code": data.get("access_code")
    }


  async def verify(self, reference: str) -> Dict[str, Any]:
    data = await self.gateway.verify_transaction(reference)
    status = data.get("status")
    amount = data.get("amount")
    currency = data.get("currency", "NGN")
    paid_at_str = data.get("paid_at")
    gateway_response = data.get("gateway_response")


    paid_at = None
    if paid_at_str:
      try:
        paid_at = datetime.fromisoformat(paid_at_str.replace("Z", "+00:00"))
      except Exception:
        paid_at = None


    if status == "success":
      await Payment.find(Payment.reference == reference).update(
        {"$set": {"status": "paid", "paid_at": paid_at or datetime.now(timezone.utc)}}
      )
    elif status == "failed":
      await Payment.find(Payment.reference == reference).update({"$set": {"status": "failed"}})

    return {
      "reference": reference, "status": status, "amount_minor": amount, 
      "currency": currency, "paid_at": paid_at, "gateway_response": gateway_response
    }


  async def get_by_reference(self, reference: str) -> Optional[Payment]:
    return await Payment.find_one(Payment.reference == reference)