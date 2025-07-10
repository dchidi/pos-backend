from fastapi import APIRouter, Depends, HTTPException, status
from beanie import PydanticObjectId
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RolePatch, RoleResponse
from app.core.auth import require_permissions
from app.exceptions import RoleNotFound, InvalidPermissionSet
from typing import List

router = APIRouter()

@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: str = Depends(require_permissions("can_create_role", "super_admin"))
) -> RoleResponse:
    try:
        return await RoleService.create_role(role_data, current_user)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except InvalidPermissionSet as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to create role"
        )

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    status: str = None,
    _ = Depends(require_permissions("admin", "super_admin"))
) -> List[RoleResponse]:
    try:
        return await RoleService.list_roles(status)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch roles"
        )

@router.get("/roles/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: PydanticObjectId,
    _ = Depends(require_permissions("admin", "super_admin"))
) -> RoleResponse:
    try:
        return await RoleService.get_role(role_id)
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch role"
        )

@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: PydanticObjectId,
    role_data: RoleUpdate,
    current_user: str = Depends(require_permissions("super_admin"))
) -> RoleResponse:
    try:
        return await RoleService.full_update(role_id, role_data, current_user)
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    except InvalidPermissionSet as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update role"
        )

@router.patch("/roles/{role_id}", response_model=RoleResponse)
async def patch_role(
    role_id: PydanticObjectId,
    role_data: RolePatch,
    current_user: str = Depends(require_permissions("super_admin"))
) -> RoleResponse:
    try:
        return await RoleService.partial_update(role_id, role_data, current_user)
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    except InvalidPermissionSet as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update role"
        )

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: PydanticObjectId,
    current_user: str = Depends(require_permissions("super_admin"))
) -> None:
    try:
        await RoleService.archive_role(role_id, current_user)
    except RoleNotFound:
        raise HTTPException(status_code=404, detail="Role not found")
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to delete role"
        )