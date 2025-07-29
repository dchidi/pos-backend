from fastapi import status, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["300/minute"]
)

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    # Default Retry-After header to 60 seconds
    retry_after = 60

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Rate limit exceeded. Please try again later."},
        headers={"Retry-After": str(retry_after)}
    )
