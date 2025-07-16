from fastapi import APIRouter, HTTPException, status, Depends
from app.utils.permission_filter import filter_super_admin
from app.services.exceptions import *
from app.constants.permissions import PERMISSION_GROUPS
from app.core.auth import require_permissions

router = APIRouter()



# TODO :: Add can_create_user permission to route
@router.get("/permissions", response_model=list, status_code=status.HTTP_200_OK)
async def list_permissions(_ = Depends(require_permissions("admin", "super_admin"))):
    """
    Returns all permissions grouped by functional areas.
    """
    try:
        return filter_super_admin(PERMISSION_GROUPS)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Login failed due to internal error"
        )

