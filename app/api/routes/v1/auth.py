from fastapi import APIRouter, Request, Query, BackgroundTasks, Depends
from fastapi.responses import RedirectResponse
from app.core.rate_limit import limiter

from app.schemas.auth import (
  LoginRequest, Token, OTPVerifyRequest, OTPResendRequest,
  ResetPassword, RefreshTokenRequest
)

from app.services.auth import (
    authenticate_user, generate_otp, verify_otp,
    verify_email, logout, verify_account, get_current_token,
    reset_password, create_verification_token, refresh_user_token
)
from app.services.email_services import send_otp_email, send_reset_password_email

from app.services.exceptions import ValidationError

from app.core.settings import settings


router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_route(
    request:Request, # request:Request is needed for routes with specific rate limter.
    data: LoginRequest, 
    background_tasks:BackgroundTasks # use Redis + Cellery later for sending email
): 
    user = await authenticate_user(data)
    otp = await generate_otp(user.email)
    # await send_otp_email(user.email, otp)
    background_tasks.add_task(
        send_otp_email,
        to_email=user.email,
        otp=otp
    )
    return Token(access_token="otp_sent", refresh_toke="", token_type="awaiting_verification")

@router.post("/verify_otp", response_model=Token)
@limiter.limit("5/minute")
async def verify_otp_route(request:Request, data: OTPVerifyRequest):
    access_token, refresh_token = await verify_otp(data.email, data.otp)
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/resend_otp", response_model=Token)
@limiter.limit("3/minute")
async def resend_otp_route(
    request:Request, 
    data: OTPResendRequest,
    background_tasks: BackgroundTasks # use Redis + Celery later for email operations
):
    user = await verify_email(data)
    otp = await generate_otp(user.email)
    # await send_otp_email(user.email, otp)
    background_tasks.add_task(
        send_otp_email,
        to_email=user.email,
        otp=otp
    )
    return Token(access_token="otp_sent", refresh_toke="",  token_type="awaiting_verification")

@router.post("/reset_password", response_model=Token)
@limiter.limit("5/minute")
async def reset_password_route(request:Request, data: ResetPassword):
    access_token, refresh_token = await reset_password(**data.model_dump())
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.get("/verify_account")
@limiter.limit("5/minute")
async def verify_account_route(
    request:Request, 
    verification_token: str = Query(..., description="JWT verification token")
):
    try:
        user = await verify_account(verification_token)
        return RedirectResponse(
            f"{settings.REDIRECT_TO_UPDATE_PASSWORD}?uid={user.id}&cid={user.company_id}"
        )
    except ValidationError as e:
        return e.detail

@router.post("/forgot_password", response_model=Token)
@limiter.limit("5/minute")
async def forgot_password_route(
    request:Request, 
    data: OTPResendRequest, 
    background_tasks: BackgroundTasks):
    user = await verify_email(data)
    user.reset_password = True
    user.is_verified = False
    await user.save()
    
    # send reset password email with link not otp
    activation_token = create_verification_token(user.id)
    activation_link = f"{settings.ACTIVATION_LINK}{activation_token}"

    # await send_reset_password_email(to_email=user.email, verification_url=activation_link)
    background_tasks.add_task(
        send_reset_password_email,
        to_email=user.email,
        verification_url=activation_link
    )
    
    return Token(access_token="verification_link_sent", refresh_token="", token_type="awaiting_verification")

@router.post("/refresh_token", response_model=Token)
@limiter.limit("5/minute")
async def refresh_token_route(request:Request, refresh_token:str = Depends(get_current_token)):
    return await refresh_user_token(refresh_token)

@router.post("/logout", response_model=dict[str, str])
@limiter.limit("5/minute")
async def logout_route(request:Request, data:RefreshTokenRequest):
    if not data.refresh_token:
        raise ValidationError("Missing refresh token")
    res = await logout(data.refresh_token)
    return res