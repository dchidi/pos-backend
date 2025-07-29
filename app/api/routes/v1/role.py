from fastapi import APIRouter, Query, Path, status, Depends
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from app.utils.parse_sort_clause import parse_sort

from app.schemas.role import (
    RoleCreate, RoleUpdate, RoleResponse
)
from app.services.role import (
    create_role,
    get_role,
    list_roles,
    update_role,
    soft_delete_role,
    delete_role,
    restore_role,
    disable_role,
    activate_role
)

from app.services.auth import get_current_company


router = APIRouter()


@router.post(
    "/",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new role",
)
async def create_role_route(
    payload: RoleCreate,
    company_id: PydanticObjectId = Depends(get_current_company)
):
    return await create_role(payload, company_id)


# GET /roles/?skip=0&limit=20&include_deleted=false&name=East%20Role
# &search_name=Reg&exact_match=false&sort=name

@router.get(
    "/",
    response_model=List[RoleResponse],
    summary="List roles with optional filters and sorting",
)
async def get_roles_route(
    company_id: PydanticObjectId = Depends(get_current_company),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted roles"
    ),
    include_deactivated: bool = Query(
        False, description="Include deactivated roles"
    ),
    name: Optional[str] = Query(None, description="Exact match on name"),
    created_by: Optional[str] = Query(None, description="user id"),
    updated_by: Optional[str] = Query(None), description="user id",
    sort: Optional[str] = Query(
        None,
        description="Comma-separated fields to sort by; prefix '-' for DESC. E.g. `sort=name,-code`"
    ),

    # Search filters (pattern or exact based on flag)
    search_name: Optional[str] = Query(None, description="Search term for name"),
    exact_match: bool = Query(
        True, description="Flag to require exact match (true) vs pattern search (false)"
    ),
):
    sort_params = parse_sort(sort)

    # Build filters dict
    filters: Dict[str, Any] = {}
    if name is not None:
        filters["name"] = name
    if created_by is not None:
        filters["created_by"] = created_by
    if updated_by is not None:
        filters["updated_by"] = updated_by

    # Build search dict
    search: Dict[str, str] = {}
    if search_name:
        search["name"] = search_name

    return await list_roles(
        company_id = company_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,        
        include_deactivated=include_deactivated,
        filters=filters or None,
        search=search or None,
        exact_match=exact_match,
        sort_order=sort_params or None,
    )


@router.get(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Get a single role by ID",
)
async def get_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
    include_deleted: bool = Query(
        False, description="Include if the role is soft-deleted"
    ),    
    include_deactivated: bool = Query(
        False, description="Include deactivated roles"
    ),
):
    return await get_role(role_id, company_id, include_deleted, include_deactivated)


@router.put(
    "/{role_id}",
    response_model=RoleResponse,
    summary="Update an existing role",
)
async def update_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),    
    company_id: str = Depends(get_current_company),
    payload: RoleUpdate = ...,
):
    return await update_role(role_id=role_id, company_id=company_id, data=payload)


@router.patch(
    "/{role_id}/soft_delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a role",
)
async def soft_delete_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    await soft_delete_role(role_id=role_id, company_id=company_id)

@router.delete(
    "/{role_id}/permanently",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard-delete a role and it cannot be restored",
)
async def delete_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    await delete_role(role_id, company_id)

@router.patch(
    "/{role_id}/restore",
    response_model=RoleResponse,
    summary="Restore a soft-deleted role",
)
async def restore_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    return await restore_role(role_id=role_id, company_id=company_id)


@router.patch(
    "/{role_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a role",
)
async def disable_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    await disable_role(role_id, company_id)


@router.patch(
    "/{role_id}/activate",
    response_model=RoleResponse,
    summary="Activate a disabled role",
)
async def restore_role_route(
    role_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    return await activate_role(role_id, company_id)