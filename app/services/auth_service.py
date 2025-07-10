import secrets
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.models.user import User
from app.models.otp import OTP
from app.schemas.auth import LoginRequest
from app.core.settings import settings
from app.core.security import verify_password
from app.exceptions import (
    InvalidCredentials,
    OTPExpired,
    OTPNotFound,
    OTPAttemptsExceeded,
    InvalidOTP,
    UserNotFound
)


def create_access_token(subject: str, expires_delta: timedelta = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": subject}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def authenticate_user(data: LoginRequest) -> User:
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise InvalidCredentials()
    return user


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
        raise OTPNotFound()

    if record.attempts_left < 1:
        raise OTPAttemptsExceeded()

    if record.expires_at < datetime.now(timezone.utc):
        raise OTPExpired()

    if record.otp_code != input_otp:
        record.attempts_left -= 1
        await record.save()
        raise InvalidOTP()

    await OTP.find(OTP.email == email).delete()

    user = await User.find_one(User.email == email)
    if not user:
        raise UserNotFound()

    user.is_verified = True
    await user.save()

    return create_access_token(subject=user.email)
