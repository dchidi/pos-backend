# app/api/errors.py
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.services.exceptions import (
    NotFoundError,
    AlreadyExistsError,
    ValidationError,
    ServiceError,
    OTPAttemptsExceeded,
    OTPExpired,
    OTPInvalid,
)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_404_NOT_FOUND)

    @app.exception_handler(AlreadyExistsError)
    async def conflict_handler(request: Request, exc: AlreadyExistsError):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_409_CONFLICT)

    @app.exception_handler(ValidationError)
    async def unprocessable_handler(request: Request, exc: ValidationError):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    @app.exception_handler(OTPAttemptsExceeded)
    async def otp_too_many_handler(request: Request, exc: OTPAttemptsExceeded):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    @app.exception_handler(OTPExpired)
    async def otp_expired_handler(request: Request, exc: OTPExpired):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_410_GONE)

    @app.exception_handler(OTPInvalid)
    async def otp_invalid_handler(request: Request, exc: OTPInvalid):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_403_FORBIDDEN)

    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        # fallback for any other ServiceError
        return JSONResponse({"detail": str(exc) or "Service operation failed"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        # log.exc_info() here if you want
        return JSONResponse({"detail": "An unexpected error occurred"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
