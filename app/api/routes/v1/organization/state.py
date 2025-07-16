from fastapi import APIRouter, Query, Path, status
from typing import List, Optional

from app.schemas.organization.location import StateCreate, LocationUpdate, StateResponse
from app.services.organization.state import (
    create_state,
    get_state,
    list_states,
    update_state,
    delete_state,
    restore_state,
    disable_state,
    activate_state
)
# from app.api.routes.v1.handle_errors import handle_service_errors


router = APIRouter()


@router.post(
    "/",
    response_model=StateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new state",
)
async def create_state_route(payload: StateCreate):
    return await create_state(payload)


@router.get(
    "/",
    response_model=List[StateResponse],
    summary="List states with optional filters",
)
async def get_states_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted states"
    ),
    name: Optional[str] = Query(
        None, description="Exact match on state name"
    ),
    company_id: Optional[str] = Query(
        None, description="Filter by owning company ID"
    ),
    category_id: Optional[str] = Query(
        None, description="Filter by associated category ID"
    ),
):
    return await list_states(
        skip,
        limit,
        include_deleted,
        name,
        company_id,
        category_id,
    )


@router.get(
    "/{state_id}",
    response_model=StateResponse,
    summary="Get a single state by ID",
)
async def get_state_route(
    state_id: str = Path(..., description="Brand ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the state is soft-deleted"
    ),
):
    return await get_state(state_id, include_deleted)


@router.put(
    "/{state_id}",
    response_model=StateResponse,
    summary="Update an existing state",
)
async def update_state_route(
    state_id: str = Path(..., description="Brand ObjectId"),
    payload: LocationUpdate = ...,
):
    return await update_state(state_id, payload)


@router.delete(
    "/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a state",
)
async def delete_state_route(
    state_id: str = Path(..., description="Brand ObjectId"),
):
    await delete_state(state_id)


@router.patch(
    "/{state_id}/restore",
    response_model=StateResponse,
    summary="Restore a soft-deleted state",
)
async def restore_state_route(
    state_id: str = Path(..., description="Brand ObjectId"),
):
    return await restore_state(state_id)


@router.patch(
    "/{state_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a state",
)
async def disable_state_route(
    state_id: str = Path(..., description="Brand ObjectId"),
):
    await disable_state(state_id)


@router.patch(
    "/{state_id}/activate",
    response_model=StateResponse,
    summary="Activate a disabled state",
)
async def restore_state_route(
    state_id: str = Path(..., description="Brand ObjectId"),
):
    return await activate_state(state_id)