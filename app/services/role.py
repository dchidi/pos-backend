from typing import List, Optional, Tuple, Any, Dict
from beanie import PydanticObjectId
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse
from app.services.crud_services import CRUD
from app.constants.sort_order import SortOrder
from app.services.exceptions import ValidationError

crud = CRUD(Role)


async def create_role(data: RoleCreate, company_id:PydanticObjectId) -> Role:    
    data_dict = data.model_dump()
    data_dict["company_id"] = company_id
    res = await crud.create(data_dict, unique_fields=["name"])
    return res


async def get_role(
    role_id: str,
    company_id:PydanticObjectId ,
    include_deleted: bool = False,
    include_deactivated: bool = False
) -> RoleResponse:
    res = await crud.get_by_id(role_id, company_id, include_deleted, include_deactivated)
    return res


async def list_roles(
    company_id:PydanticObjectId,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    include_deactivated: bool = False,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[Dict[str, Any]] = None,
    sort_order: Optional[List[Tuple[str, SortOrder]]] = None,
    exact_match: Optional[bool] = False
) -> List[RoleResponse]:
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


async def update_role(
    role_id: str,
    data: RoleUpdate,     
    company_id:PydanticObjectId
) -> Role:
    res = await crud.update(role_id, company_id, data, unique_fields=["name"])
    return res

async def soft_delete_role(
    role_id: str,
    company_id:PydanticObjectId
) -> None:
    """Soft-delete a role."""
    res = await crud.update_flags(role_id, company_id,  fields=[("is_deleted", True), ("is_active", False)])
    return res

async def delete_role(
    role_id: str,
    company_id:PydanticObjectId
) -> None:
    """hard-delete a role."""
    res = await crud.delete(role_id, company_id, hard_delete= True)
    return res

async def restore_role(
    role_id: str,
    company_id:PydanticObjectId
) -> Role:
    """Restore a previously soft-deleted role."""
    res = await crud.update_flags(role_id, company_id, fields=[("is_deleted", False), ("is_active", True)])
    return res


async def disable_role(
    role_id: str,
    company_id:PydanticObjectId
) -> None:
    """Deactivate a role."""
    res = await crud.update_flags(role_id, company_id, [("is_active", False)])
    return res


async def activate_role(
    role_id: str,
    company_id:PydanticObjectId
) -> Role:
    """Restore a previously deactivated role."""
    res = await crud.update_flags(role_id, company_id, [("is_active", True)])
    return res
