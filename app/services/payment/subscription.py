from __future__ import annotations
from typing import Optional
from uuid import uuid4


from app.constants import Currency, to_minor_units
from app.models.payment.subscription import Subscription
from app.gateways.paystack_cleint import PaystackClient




class SubscriptionService:
  def __init__(self, gateway: Optional[PaystackClient] = None):
    self.gateway = gateway or PaystackClient()


  async def start(
      self, *, tenant_id, customer_email: str, plan_id: Optional[str], 
      plan_name: Optional[str], amount_major: Optional[float], interval: Optional[str], 
      callback_url: Optional[str]
  ) -> dict:
    code = plan_id
    if not code:
      assert plan_name and amount_major and interval
      plan = await self.gateway.create_plan(
        name=plan_name, amount_minor=to_minor_units(amount_major, Currency.NGN), 
        interval=interval
      )
      code = plan["plan_id"]


    reference = f"sub-{tenant_id}-{uuid4()}"
    metadata = {
      "tenant_id": str(tenant_id), "customer_email": customer_email, 
      "type": "subscription_first_charge", "plan_id": code
    }
    init = await self.gateway.initialize_transaction(
      email=customer_email, 
      amount_minor=to_minor_units(amount_major or 0, Currency.NGN) if amount_major else 0, 
      reference=reference, callback_url=callback_url, 
      currency=Currency.NGN, metadata=metadata
    )


    await Subscription(
      tenant_id=tenant_id, customer_email=customer_email, 
      plan_id=code, status="incomplete"
    ).insert()
    return {"reference": reference, "authorization_url": init["authorization_url"], "plan_id": code}


  async def activate_from_webhook(self, *, tenant_id, email: str, plan_id: str, authorization_code: str) -> None:
    sub = await self.gateway.create_subscription(
      customer=email, plan_id=plan_id, authorization_code=authorization_code
    )
    
    await Subscription.find((Subscription.tenant_id == tenant_id) & (Subscription.customer_email == email)).update({
      "$set": {
      "authorization_code": authorization_code,
      "subscription_code": sub.get("subscription_code"),
      "email_token": sub.get("email_token"),
      "status": "active",
      }
    })


  async def get_status(self, *, tenant_id, customer_email: str) -> Optional[Subscription]:
    return await Subscription.find_one((Subscription.tenant_id == tenant_id) & (Subscription.customer_email == customer_email))