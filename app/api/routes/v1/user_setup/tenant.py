from fastapi import APIRouter, Query, Path, status, Depends
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId
from app.utils.parse_sort_clause import parse_sort

from app.schemas.organization.tenant import (
    TenantCreate, TenantUpdate, TenantResponse
)
from app.services.user_setup.tenant import (
    create_tenant,
    get_tenant,
    list_tenants,
    update_tenant,
    soft_delete_tenant,
    delete_tenant,
    restore_tenant,
    disable_tenant,
    activate_tenant
)

from app.services.auth import get_current_company


router = APIRouter()


@router.post(
    "/",
    response_model=TenantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tenant",
)
async def create_tenant_route(
    payload: TenantCreate
):
    return await create_tenant(payload)


# GET /tenants/?skip=0&limit=20&include_deleted=false&name=East%20Tenant
# &search_name=Reg&exact_match=false&sort=name

@router.get(
    "/",
    response_model=List[TenantResponse],
    summary="List tenants with optional filters and sorting",
)
async def get_tenants_route(
    company_id: PydanticObjectId = Depends(get_current_company),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted tenants"
    ),
    include_deactivated: bool = Query(
        False, description="Include deactivated tenants"
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

    return await list_tenants(
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
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Get a single tenant by ID",
)
async def get_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
    include_deleted: bool = Query(
        False, description="Include if the tenant is soft-deleted"
    ),    
    include_deactivated: bool = Query(
        False, description="Include deactivated tenants"
    ),
):
    return await get_tenant(tenant_id, company_id, include_deleted, include_deactivated)


@router.put(
    "/{tenant_id}",
    response_model=TenantResponse,
    summary="Update an existing tenant",
)
async def update_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),    
    company_id: str = Depends(get_current_company),
    payload: TenantUpdate = ...,
):
    return await update_tenant(tenant_id=tenant_id, company_id=company_id, data=payload)


@router.patch(
    "/{tenant_id}/soft_delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a tenant",
)
async def soft_delete_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    await soft_delete_tenant(tenant_id=tenant_id, company_id=company_id)

@router.delete(
    "/{tenant_id}/permanently",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard-delete a tenant and it cannot be restored",
)
async def delete_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    await delete_tenant(tenant_id, company_id)

@router.patch(
    "/{tenant_id}/restore",
    response_model=TenantResponse,
    summary="Restore a soft-deleted tenant",
)
async def restore_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    return await restore_tenant(tenant_id=tenant_id, company_id=company_id)


@router.patch(
    "/{tenant_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a tenant",
)
async def disable_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    await disable_tenant(tenant_id, company_id)


@router.patch(
    "/{tenant_id}/activate",
    response_model=TenantResponse,
    summary="Activate a disabled tenant",
)
async def restore_tenant_route(
    tenant_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Depends(get_current_company),
):
    return await activate_tenant(tenant_id, company_id)