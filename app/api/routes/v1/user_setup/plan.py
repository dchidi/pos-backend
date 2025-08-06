from fastapi import APIRouter, Query, Path, status, Depends
from typing import List, Optional, Dict, Any
from app.utils.parse_sort_clause import parse_sort

from app.schemas.user_setup.plan import (
    PlanCreate, PlanUpdate, PlanResponse
)
from app.services.user_setup.plan import (
    create_plan,
    get_plan,
    list_plans,
    update_plan,
    soft_delete_plan,
    delete_plan,
    restore_plan,
    disable_plan,
    activate_plan
)

from app.services.auth import get_current_user_id


router = APIRouter()


@router.post(
    "/",
    response_model=PlanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new plan",
)
async def create_plan_route(
    payload: PlanCreate,
    current_user_id:str = Depends(get_current_user_id)
):
    return await create_plan(payload, current_user_id)


# GET /plans/?skip=0&limit=20&include_deleted=false&name=East%20Plan
# &search_name=Reg&exact_match=false&sort=name

@router.get(
    "/",
    response_model=List[PlanResponse],
    summary="List plans with optional filters and sorting",
)
async def get_plans_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted plans"
    ),
    include_deactivated: bool = Query(
        False, description="Include deactivated plans"
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

    return await list_plans(
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
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Get a single plan by ID",
)
async def get_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the plan is soft-deleted"
    ),    
    include_deactivated: bool = Query(
        False, description="Include deactivated plans"
    ),
):
    return await get_plan(plan_id, include_deleted, include_deactivated)


@router.put(
    "/{plan_id}",
    response_model=PlanResponse,
    summary="Update an existing plan",
)
async def update_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId"),
    payload: PlanUpdate = ...,
):
    return await update_plan(plan_id=plan_id, data=payload)


@router.patch(
    "/{plan_id}/soft_delete",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a plan",
)
async def soft_delete_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId")
):
    await soft_delete_plan(plan_id=plan_id)

@router.delete(
    "/{plan_id}/permanently",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard-delete a plan and it cannot be restored",
)
async def delete_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId")
):
    await delete_plan(plan_id)

@router.patch(
    "/{plan_id}/restore",
    response_model=PlanResponse,
    summary="Restore a soft-deleted plan",
)
async def restore_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId")
):
    return await restore_plan(plan_id=plan_id)


@router.patch(
    "/{plan_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a plan",
)
async def disable_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId")
):
    await disable_plan(plan_id)


@router.patch(
    "/{plan_id}/activate",
    response_model=PlanResponse,
    summary="Activate a disabled plan",
)
async def restore_plan_route(
    plan_id: str = Path(..., description="Brand ObjectId")
):
    return await activate_plan(plan_id)