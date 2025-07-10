from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, Token, OTPVerifyRequest
from app.services.auth_service import (
    authenticate_user, create_access_token, generate_otp
)
from app.models.otp import OTP
from app.models.user import User
from datetime import datetime, timezone
from app.utils.mail import send_otp_email  # Assume you define this

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(data: LoginRequest):
    user = await authenticate_user(data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid credentials"
        )
    otp = await generate_otp(user.email)
    await send_otp_email(user.email, otp)
    return Token(access_token="otp_sent", token_type="awaiting_verification")


@router.post("/verify", response_model=Token)
async def verify_otp(data: OTPVerifyRequest):
    record = await OTP.find_one(OTP.email == data.email)
    print(record)
    if not record:
        raise HTTPException(status_code=400, detail="OTP not found or expired")
    if record.attempts_left < 1:
        raise HTTPException(status_code=403, detail="Too many incorrect attempts")

    if record.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=403, detail="OTP expired")

    if record.otp_code != data.otp:
        record.attempts_left -= 1
        await record.save()
        raise HTTPException(status_code=403, detail="Invalid OTP")

    await OTP.find(OTP.email == data.email).delete()
    user = await User.find_one(User.email == data.email)
    if user:
        user.is_verified = True
        await user.save()
        token = create_access_token(subject=user.email)
        return Token(access_token=token)
    raise HTTPException(status_code=404, detail="User not found")
