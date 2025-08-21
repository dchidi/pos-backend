from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.routes.v1 import api_router
from app.api.errors import register_exception_handlers
from app.core.settings import settings
from app.db.mongodb import mongo
from app.middlewares.logging_middleware import LoggingMiddleware
from app.core.logging_config import setup_logging
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

@asynccontextmanager
async def lifespan(app: FastAPI):
    await mongo.connect()
    yield
    await mongo.disconnect()

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
app.add_middleware(LoggingMiddleware)
# app.add_middleware(RoleMiddleware, required_roles=["admin", "user"])

# Rate limiting
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Global exception handlers for services
register_exception_handlers(app)

# Handle FastAPI / Pydantic request validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

# Health check endpoint - Used for uptime probe
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

# Mount API
app.include_router(api_router, prefix="/api/v1")
