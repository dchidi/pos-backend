from time import time
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.core.logger import logger  # Unified import

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time()
        response = await call_next(request)
        process_time = round(time() - start_time, 4)

        logger.info(f"{request.method} {request.url} - {response.status_code} - {process_time}s")
        return response
