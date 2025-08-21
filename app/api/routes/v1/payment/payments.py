from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse


from app.schemas.payment import InitPaymentRequest, InitPaymentResponse, VerifyResponse
from app.constants import Currency
from app.services.payment.payment import PaymentService
from app.utils.qr_code import generate_qr_png_bytes


router = APIRouter()


def get_payment_service() -> PaymentService:
    return PaymentService()


@router.post("/initialize", response_model=InitPaymentResponse)
async def initialize_payment(req: InitPaymentRequest, svc: PaymentService = Depends(get_payment_service)):
    out = await svc.initialize(
        tenant_id=req.tenant_id, customer_email=req.customer_email, 
        customer_name=req.customer_name, currency=req.currency, 
        items=[i.model_dump() for i in req.items], 
        callback_url=str(req.callback_url) if req.callback_url else None, 
        reference=req.reference, metadata=req.metadata or {}
    )
    return InitPaymentResponse(**out)


@router.get("/verify/{reference}", response_model=VerifyResponse)
async def verify_payment(reference: str, svc: PaymentService = Depends(get_payment_service)):
    out = await svc.verify(reference)
    return VerifyResponse(reference=out["reference"], status=out["status"], amount_minor=out["amount_minor"], currency=Currency(out["currency"]), paid_at=out["paid_at"], gateway_response=out["gateway_response"])


@router.get("/{reference}/qr", response_class=StreamingResponse)
async def payment_qr(reference: str, svc: PaymentService = Depends(get_payment_service)):
    rec = await svc.get_by_reference(reference)
    if not rec or not rec.authorization_url:
        raise HTTPException(status_code=404, detail="Payment or authorization URL not found")
    png = generate_qr_png_bytes(rec.authorization_url)
    return StreamingResponse(iter([png]), media_type="image/png")