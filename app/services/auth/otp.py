import secrets
from datetime import datetime, timedelta, timezone

from app.models.user_setup.user import User
from app.models.user_setup.otp import OTP

from app.core.settings import settings

from app.services.exceptions import (
    OTPExpired, NotFoundError, OTPAttemptsExceeded, InvalidOTP
)
from app.services.auth.token import create_access_token, create_refresh_token

async def generate_otp(email: str) -> str:
    otp = str(secrets.randbelow(9000) + 1000)
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRY_TIME_MINUTES)

    await OTP.find({"email": email}).delete()

    await OTP(
        email=email,
        otp_code=otp,
        expires_at=expires,
        attempts_left=3,
        created_at=datetime.now(timezone.utc)
    ).insert()

    return otp


async def verify_otp(email: str, input_otp: str) -> str:
    record = await OTP.find_one(OTP.email == email)
    if not record:
        raise NotFoundError("OTP not found or expired")

    if record.attempts_left < 1:
        raise OTPAttemptsExceeded("Too many incorrect attempts")

    if record.expires_at < datetime.now(timezone.utc):
        raise OTPExpired("OTP expired")

    if record.otp_code != input_otp:
        record.attempts_left -= 1
        await record.save()
        raise InvalidOTP("Invalid OTP")

    await OTP.find(OTP.email == email).delete()

    user = await User.find_one(User.email == email)
    if not user:
        raise NotFoundError("User not found")
    
    
    access_token = create_access_token(subject=user.id, company_id=user.company_id)    
    refresh_token = create_refresh_token(subject=user.id, company_id=user.company_id)

    user.refresh_token = refresh_token
    user.refresh_token_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    await user.save()

    return access_token, refresh_token
