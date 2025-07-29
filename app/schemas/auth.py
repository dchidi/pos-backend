from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from beanie import PydanticObjectId


class OTPResendRequest(BaseModel):
    email: EmailStr

class LoginRequest(OTPResendRequest):
    password: str

class OTPVerifyRequest(OTPResendRequest):
    otp: str

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None

class ResetPassword(BaseModel):
    password: str = Field(..., min_length=8)   
    user_id: PydanticObjectId
    company_id: PydanticObjectId

class RefreshTokenRequest(BaseModel):
    refresh_token: str