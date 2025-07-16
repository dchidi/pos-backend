from functools import wraps
from fastapi import HTTPException, status
from typing import Any, Callable, Coroutine

from app.services.exceptions import (
    NotFoundError,
    AlreadyExistsError,
    ValidationError,
    ServiceError, 
    OTPAttemptsExceeded, OTPExpired, OTPInvalid
)

def handle_service_errors(func: Callable[..., Coroutine[Any, Any, Any]]):
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
        except AlreadyExistsError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e)
            )
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )
        except (ValueError, TypeError) as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input: {str(e)}"
            )
         # OTP-specific errors
        except OTPAttemptsExceeded as e:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e) or "Maximum OTP attempts exceeded"
            )
        except OTPExpired as e:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=str(e) or "OTP has expired"
            )
        except OTPInvalid as e:  # If you have this
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e) or "Invalid OTP"
            )
            
        # Service and fallback errors
        except ServiceError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e) or "Service operation failed"
            )
        except Exception as e:
            # Log unexpected errors here (recommended)
            # logger.exception("Unexpected error")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An unexpected error occurred"
            )
    return wrapper