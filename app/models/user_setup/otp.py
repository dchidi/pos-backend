from beanie import Document
from pydantic import EmailStr, Field
from datetime import datetime, timedelta, timezone
from typing import Optional


class OTP(Document):
    email: EmailStr
    otp_code: str
    expires_at: datetime
    attempts_left: int = 3
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "otps"
