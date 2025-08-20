"""
API v1 routing module.

This file registers and exposes all versioned API routes under a single APIRouter
for FastAPI application inclusion. Routes should be organized and imported here
to maintain clean separation and versioning.
"""

from fastapi import APIRouter

# User setup
from app.api.routes.v1.user_setup.plan import router as plan_router

# Import individual routers
from app.api.routes.v1.inventory.brand import router as brand_router
from app.api.routes.v1.user import router as user_router

from app.api.routes.v1.location import (
  area, country, region, state
)

from app.api.routes.v1.auth import router as auth_router
from app.api.routes.v1.permission import router as permission_router
from app.api.routes.v1.role import router as role_router

from app.api.routes.v1.user_setup.tenant import router as tenant_router

from app.api.routes.v1.payment.payments import router as payment_router
from app.api.routes.v1.payment.subscriptions import router as subscription_router
from app.api.routes.v1.webhooks.paystack_webhook import router as paystack_webhook_router

api_router = APIRouter()

# User setup
api_router.include_router(plan_router, prefix="/plans", tags=["User Setup/Plan"])

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

# Payment
api_router.include_router(payment_router, prefix="/payment", tags=["Payments"])
api_router.include_router(subscription_router, prefix="/subscription", tags=["Payments/Subscription"])
api_router.include_router(paystack_webhook_router, prefix="/paystack_webhook", tags=["Payments/PaystackWebhook"])