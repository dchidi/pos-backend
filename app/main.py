from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes.v1 import api_router
from app.core.settings import settings
from app.db.mongodb import mongo

# from app.middlewares.role_middleware import RoleMiddleware
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
    lifespan=lifespan
)

app.add_middleware(LoggingMiddleware)
# app.add_middleware(RoleMiddleware, required_roles=["admin", "user"])

# Add rate limiter middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router, prefix="/api/v1")
