from typing import List, Optional, Tuple, Any, Dict
from beanie import PydanticObjectId

from app.models.user_setup.tenant import Tenant

from app.schemas.user_setup.tenant import TenantCreate, TenantUpdate, TenantResponse

from app.services.crud_services import CRUD

from app.constants import SortOrder

crud = CRUD(Tenant)


async def create_tenant(data: TenantCreate) -> Tenant:    
    res = await crud.create(data, unique_fields=["name"])
    return res


async def get_tenant(
    tenant_id: str,
    company_id:PydanticObjectId ,
    include_deleted: bool = False,
    include_deactivated: bool = False
) -> TenantResponse:
    res = await crud.get_by_id(tenant_id, company_id, include_deleted, include_deactivated)
    return res


async def list_tenants(
    company_id:PydanticObjectId,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    include_deactivated: bool = False,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[Dict[str, Any]] = None,
    sort_order: Optional[List[Tuple[str, SortOrder]]] = None,
    exact_match: Optional[bool] = False
) -> List[TenantResponse]:
    res = await crud.list(
        company_id,
        skip,
        limit,
        include_deleted,
        include_deactivated,
        filters=filters,
        sort=sort_order,
        search=search,
        exact_match=exact_match if exact_match is not None else False
    )
    return res


async def update_tenant(
    tenant_id: str,
    data: TenantUpdate,     
    company_id:PydanticObjectId
) -> Tenant:
    res = await crud.update(tenant_id, company_id, data, unique_fields=["name"])
    return res

async def soft_delete_tenant(
    tenant_id: str,
    company_id:PydanticObjectId
) -> None:
    """Soft-delete a tenant."""
    res = await crud.update_flags(tenant_id, company_id,  fields=[("is_deleted", True), ("is_active", False)])
    return res

async def delete_tenant(
    tenant_id: str,
    company_id:PydanticObjectId
) -> None:
    """hard-delete a tenant."""
    res = await crud.delete(tenant_id, company_id, hard_delete= True)
    return res

async def restore_tenant(
    tenant_id: str,
    company_id:PydanticObjectId
) -> Tenant:
    """Restore a previously soft-deleted tenant."""
    res = await crud.update_flags(tenant_id, company_id, fields=[("is_deleted", False), ("is_active", True)])
    return res


async def disable_tenant(
    tenant_id: str,
    company_id:PydanticObjectId
) -> None:
    """Deactivate a tenant."""
    res = await crud.update_flags(tenant_id, company_id, [("is_active", False)])
    return res


async def activate_tenant(
    tenant_id: str,
    company_id:PydanticObjectId
) -> Tenant:
    """Restore a previously deactivated tenant."""
    res = await crud.update_flags(tenant_id, company_id, [("is_active", True)])
    return res
