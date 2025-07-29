from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError

from app.core.settings import settings

from app.services.exceptions import UnAuthorized

from app.schemas import PyObjectId


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise UnAuthorized("Invalid or expired token")

def create_access_token(
        subject: str,
        company_id: str,
        expires_delta: timedelta = None
) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"exp": expire, "sub": str(subject), "company_id": str(company_id), "type": "access_token" }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(
        subject: str,
        company_id: str,
        expires_delta: timedelta = None
) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    to_encode = {"exp": expire, "sub": str(subject), "company_id": str(company_id), "type": "refresh_token" }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_verification_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=settings.ACCOUNT_VERIFICATION_EXPIRY_TIME_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "purpose": "account_verification",
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)