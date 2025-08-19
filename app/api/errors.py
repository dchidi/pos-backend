from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.services.exceptions import (
    NotFoundError, AlreadyExistsError, ValidationError,
    ServiceError, OTPAttemptsExceeded, OTPExpired,
    InvalidOTP, UnAuthorized, ResetPassword
)

from app.constants import LogLevel
from app.core.audit_log import audit_log_bg

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
        audit_log_bg(request, LogLevel.INFO, str(exc))
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    @app.exception_handler(OTPExpired)
    async def otp_expired_handler(request: Request, exc: OTPExpired):        
        audit_log_bg(request, LogLevel.INFO, str(exc))
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_410_GONE)

    @app.exception_handler(InvalidOTP)
    async def invalid_otp_handler(request: Request, exc: InvalidOTP):        
        audit_log_bg(request, LogLevel.SECURITY, str(exc))
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_403_FORBIDDEN)

    @app.exception_handler(UnAuthorized)
    async def unauthorized_error_handler(request: Request, exc: UnAuthorized):
        audit_log_bg(request, LogLevel.SECURITY, str(exc))
        return JSONResponse({"detail": str(exc) or "Invalid or expired token"}, status_code=status.HTTP_401_UNAUTHORIZED)
    
    @app.exception_handler(ResetPassword)
    async def reset_password_handler(request: Request, exc: ResetPassword):
        return JSONResponse({"detail": str(exc)}, status_code=status.HTTP_202_ACCEPTED)
    
    @app.exception_handler(ServiceError)
    async def service_error_handler(request: Request, exc: ServiceError):
        audit_log_bg(request, LogLevel.ERROR, str(exc))
        return JSONResponse({"detail": str(exc) or "Service operation failed"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        audit_log_bg(request, LogLevel.ERROR, str(exc))
        return JSONResponse({"detail": f"An unexpected error occurred {str(exc)}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
