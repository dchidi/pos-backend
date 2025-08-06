from datetime import datetime, timezone

from app.models.blacklisted_token import BlacklistedToken

from app.services.auth.token import decode_token


async def logout(refresh_token: str) -> dict[str, str]:
    # Decode token to get expiry time
    decoded = decode_token(refresh_token)
    expires_at = datetime.fromtimestamp(decoded["exp"])

    # Store in MongoDB
    await BlacklistedToken(token=refresh_token, expires_at=expires_at).insert()
    
    return {"message": "Logged out successfully"}

# Run in cron
async def cleanup_expired_tokens():
    await BlacklistedToken.find({"expires_at": {"$lt": datetime.now(timezone.utc)}}).delete()
