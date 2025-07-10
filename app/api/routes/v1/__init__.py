"""
API v1 routing module.

This file registers and exposes all versioned API routes under a single APIRouter
for FastAPI application inclusion. Routes should be organized and imported here
to maintain clean separation and versioning.
"""

from fastapi import APIRouter

# Import individual routers
from app.api.routes.v1.user import router as user_router
from app.api.routes.v1.auth import router as auth_router
from app.api.routes.v1.permission import router as permission_router
from app.api.routes.v1.role import router as role_router

api_router = APIRouter()

# Register routes under appropriate prefixes
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(permission_router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(role_router, prefix="/roles", tags=["Role Management"])