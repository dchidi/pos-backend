from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException


from app.schemas.payment import (
  StartSubscriptionRequest, StartSubscriptionResponse, SubscriptionStatusResponse
)
from app.services.payment.subscription import SubscriptionService


router = APIRouter()




def get_subscription_service() -> SubscriptionService:
  return SubscriptionService()




@router.post("/start", response_model=StartSubscriptionResponse)
async def start_subscription(
  req: StartSubscriptionRequest, 
  svc: SubscriptionService = Depends(get_subscription_service)
):
  out = await svc.start(
    tenant_id=req.tenant_id, customer_email=req.customer_email, 
    plan_id=req.plan_id, plan_name=req.plan_name, 
    amount_major=float(req.amount_major) if req.amount_major else None, 
    interval=req.interval.value if req.interval else None, 
    callback_url=str(req.callback_url) if req.callback_url else None
  )
  return StartSubscriptionResponse(**out)




@router.get("/status", response_model=SubscriptionStatusResponse)
async def get_subscription_status(
  tenant_id: str, customer_email: str, 
  svc: SubscriptionService = Depends(get_subscription_service)
):
  rec = await svc.get_status(tenant_id=tenant_id, customer_email=customer_email)
  if not rec:
    raise HTTPException(status_code=404, detail="Subscription not found")
  return SubscriptionStatusResponse(
    tenant_id=rec.tenant_id, customer_email=rec.customer_email, 
    status=rec.status, plan_id=rec.plan_id, 
    subscription_code=rec.subscription_code
  )

