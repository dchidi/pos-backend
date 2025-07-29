"""
API v1 routing module.

This file registers and exposes all versioned API routes under a single APIRouter
for FastAPI application inclusion. Routes should be organized and imported here
to maintain clean separation and versioning.
"""

from fastapi import APIRouter

# Import individual routers
from app.api.routes.v1.inventory.brand import router as brand_router
from app.api.routes.v1.user import router as user_router

from app.api.routes.v1.location import (
  area, country, region, state
)


from app.api.routes.v1.auth import router as auth_router
from app.api.routes.v1.permission import router as permission_router
from app.api.routes.v1.role import router as role_router

from app.api.routes.v1.organization.tenant import router as tenant_router

api_router = APIRouter()

# Authentication & Authentication
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(user_router, prefix="/user", tags=["Users"])

# Access Setup
api_router.include_router(role_router, prefix="/roles", tags=["Role Management"])

# Register routes under appropriate prefixes
api_router.include_router(brand_router, prefix="/brand", tags=["Brand"])
api_router.include_router(permission_router, prefix="/permissions", tags=["Permissions"])
api_router.include_router(user_router, prefix="/warehouse", tags=["Warehouse"])



# organization
api_router.include_router(tenant_router, prefix="/tenant", tags=["Organization/Tenant"])
api_router.include_router(country.router, prefix="/country", tags=["Organization/Country"])
api_router.include_router(region.router, prefix="/region", tags=["Organization/Region"])
api_router.include_router(area.router, prefix="/area", tags=["Organization/Area"])
api_router.include_router(state.router, prefix="/state", tags=["Organization/State"])