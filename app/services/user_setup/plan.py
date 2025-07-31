from typing import List, Optional, Tuple, Any, Dict
from app.models.user_setup.plan import Plan
from app.schemas.user_setup.plan import PlanCreate, PlanUpdate, PlanResponse
from app.services.crud_services import CRUD
from app.constants.sort_order_enum import SortOrder

crud = CRUD(Plan)


async def create_plan(data: PlanCreate, current_user_id: str) -> Plan:  
    data_dict = data.model_dump();
    data_dict["created_by"] = current_user_id  
    res = await crud.create(data_dict, unique_fields=["name"])
    return res


async def get_plan(
    plan_id: str,
    include_deleted: bool = False,
    include_deactivated: bool = False
) -> PlanResponse:
    res = await crud.get_by_id(
        doc_id=plan_id,
        include_deleted=include_deleted,
        include_deactivated=include_deactivated,
        use_company_id= False
    )
    return res


async def list_plans(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    include_deactivated: bool = False,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[Dict[str, Any]] = None,
    sort_order: Optional[List[Tuple[str, SortOrder]]] = None,
    exact_match: Optional[bool] = False
) -> List[PlanResponse]:
    res = await crud.list(
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
        include_deactivated=include_deactivated,
        filters=filters,
        sort=sort_order,
        search=search,
        exact_match=exact_match if exact_match is not None else False,
        use_company_id=False
    )
    return res


async def update_plan(
    plan_id: str,
    data: PlanUpdate
) -> Plan:
    res = await crud.update(
        doc_id=plan_id,
        payload=data, 
        unique_fields=["name"],
        use_company_id=False
    )
    return res

async def soft_delete_plan(
    plan_id: str,
) -> None:
    """Soft-delete a plan."""
    res = await crud.update_flags(
        doc_id=plan_id, 
        fields=[("is_deleted", True), ("is_active", False)],
        use_company_id= False
    )
    return res

async def delete_plan(
    plan_id: str,
) -> None:
    """hard-delete a plan."""
    res = await crud.delete(
        doc_id=plan_id, 
        hard_delete= True,
        use_company_id=False
    )
    return res

async def restore_plan(
    plan_id: str,
) -> Plan:
    """Restore a previously soft-deleted plan."""
    res = await crud.update_flags(
        doc_id=plan_id, 
        fields=[("is_deleted", False), ("is_active", True)],
        use_company_id=False
    )
    return res


async def disable_plan(
    plan_id: str,
) -> None:
    """Deactivate a plan."""
    res = await crud.update_flags(
        doc_id=plan_id, 
        fields=[("is_active", False)],
        use_company_id=False
    )
    return res


async def activate_plan(
    plan_id: str,
) -> Plan:
    """Restore a previously deactivated plan."""
    res = await crud.update_flags(
        doc_id=plan_id, 
        fields=[("is_active", True)],
        use_company_id=False
    )
    return res
