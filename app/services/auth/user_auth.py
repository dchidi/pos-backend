from datetime import datetime, timezone
from jose import JWTError
from beanie import PydanticObjectId

from app.models.user_setup.user import User

from app.schemas.auth import LoginRequest, OTPResendRequest, Token

from app.services.auth import create_access_token, decode_token, verify_password
from app.services.exceptions import ValidationError, UnAuthorized, ResetPassword


async def authenticate_user(data: LoginRequest) -> User:
    user = await User.find_one(User.email == data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise ValidationError("Invalid user credentials")
    if not user.company_id:  # Ensure user has tenant context
        raise ValidationError("User not assigned to a company")
    if not user.is_verified:  # Ensure user has tenant context
        raise UnAuthorized("Your account is not verified. Contact your administrator.")
    if not user.is_active:  # Ensure user has tenant context
        raise UnAuthorized("Your account has been disabled. Contact your administrator.")
    if user.reset_password:  # Ensure user has tenant context
        raise ResetPassword("Please reset your password.")
    return user


async def verify_email(data: OTPResendRequest) -> User:
    user = await User.find_one(User.email == data.email)
    if not user:
        raise ValidationError("Invalid user credentials")
    if not user.company_id:  # Ensure user has tenant context
        raise ValidationError("User not assigned to a company")
    return user


async def verify_account(verification_token:str):
  """Returns user if verification succeeds"""
  try:
      payload = decode_token(verification_token)
      
      # Security checks
      if payload.get("purpose") != "account_verification":
          raise ValidationError("This link is for email verification only")
          
      if datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc):
          raise ValidationError("Verification link expired")
          
      user = await User.find_one(User.id == PydanticObjectId(payload["sub"]))
      if not user:
          raise ValidationError(404, "User not found")
          
      if user.is_verified:
          return user  # Idempotent return
          
      user.is_verified = True
      await user.save()
      return user
      
  except JWTError:
      raise ValidationError("Invalid verification link")
  
async def refresh_user_token(refresh_token:str):
    payload = decode_token(refresh_token)
    user_id = PydanticObjectId(payload["sub"])
    company_id = PydanticObjectId(payload["company_id"])

    user = await User.find_one({"_id":user_id, "company_id":company_id, "refresh_token":refresh_token})

    if not user or user.refresh_token_expires_at < datetime.now(timezone.utc):
        raise UnAuthorized("Refresh token expired or invalid")


    access_token = create_access_token(subject=user_id, company_id=company_id)

    
    return Token(access_token=access_token, refresh_token=refresh_token)