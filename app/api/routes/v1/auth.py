from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import LoginRequest, Token, OTPVerifyRequest
from app.services.auth_service import (
    authenticate_user, create_access_token, generate_otp, verify_otp
)
from app.utils.mail import send_otp_email
from app.exceptions import *

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(data: LoginRequest):
    try:
        user = await authenticate_user(data)
        otp = await generate_otp(user.email)
        await send_otp_email(user.email, otp)
        return Token(access_token="otp_sent", token_type="awaiting_verification")
    except InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Login failed due to internal error"
        )


@router.post("/verify", response_model=Token)
async def verify_otp_route(data: OTPVerifyRequest):
    try:
        token = await verify_otp(data.email, data.otp)
        return Token(access_token=token)
    except OTPNotFound:
        raise HTTPException(status_code=400, detail="OTP not found or expired")
    except OTPAttemptsExceeded:
        raise HTTPException(status_code=403, detail="Too many incorrect attempts")
    except OTPExpired:
        raise HTTPException(status_code=403, detail="OTP expired")
    except InvalidOTP:
        raise HTTPException(status_code=403, detail="Invalid OTP")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found")
    except Exception:
        raise HTTPException(status_code=500, detail="OTP verification failed")
