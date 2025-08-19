from fastapi import APIRouter, Query, Path, status, BackgroundTasks, Depends
from typing import List, Optional, Dict, Any
from beanie import PydanticObjectId

from app.utils.parse_sort_clause import parse_sort
from app.core.settings import settings

from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse
)

from app.models.user_setup.user import User

from app.services.auth import require_permissions, get_current_company

from app.services.user import (
    create_user,
    get_user,
    list_users,
    update_user,
    soft_delete_user,
    delete_user,
    restore_user,
    disable_user,
    activate_user
)
from app.services.email_services import send_welcome_email 
from app.services.auth import (
    create_verification_token
)


router = APIRouter()


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
async def create_user_route(
    payload: UserCreate,
    background_tasks: BackgroundTasks # use Redis + Celery later for email operations
    # _: User = Depends(require_permissions("user:create"))
):
    user = await create_user(payload)
    activation_token = create_verification_token(user.id)
    activation_link = f"{settings.ACTIVATION_LINK}{activation_token}"
    background_tasks.add_task(
        send_welcome_email,
        to_email=user.email,
        verification_url=activation_link
    )
    return user


# GET /users/?skip=0&limit=20&include_deleted=false&name=East%20User
# &search_name=Reg&exact_match=false&sort=name,-code

@router.get(
    "/",
    response_model=List[UserResponse],
    summary="List users with optional filters and sorting",
)
async def get_users_route(
    company_id: str = Query(None, description="Company ObjectId"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(
        False, description="Include soft-deleted users"
    ),
    name: Optional[str] = Query(None, description="Exact match on name"),
    code: Optional[str] = Query(None, description="Exact match on code"),
    created_by: Optional[str] = Query(None),
    updated_by: Optional[str] = Query(None),
    sort: Optional[str] = Query(
        None,
        description="Comma-separated fields to sort by; prefix '-' for DESC. E.g. `sort=name,-code`"
    ),

    # Search filters (pattern or exact based on flag)
    search_name: Optional[str] = Query(None, description="Search term for name"),
    search_code: Optional[str] = Query(None, description="Search term for code"),
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
    if code is not None:
        filters["code"] = code
    if updated_by is not None:
        filters["updated_by"] = updated_by

    # Build search dict
    search: Dict[str, str] = {}
    if search_name:
        search["name"] = search_name
    if search_code:
        search["code"] = search_code

    return await list_users(
        company_id = company_id,
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
        filters=filters or None,
        search=search or None,
        exact_match=exact_match,
        sort_order=sort_params or None,
    )


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a single user by ID",
)
async def get_user_route(
    user_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Query(None, description="Company ObjectId"),
    include_deleted: bool = Query(
        False, description="Include if the user is soft-deleted"
    ),
):
    return await get_user(user_id, company_id, include_deleted)


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update an existing user",
)
async def update_user_route(
    user_id: str = Path(..., description="User ObjectId"),    
    payload: UserUpdate = ...,         
    company_id:PydanticObjectId = Depends(get_current_company)
):
    return await update_user(user_id = user_id, data = payload, company_id = company_id)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete a user",
)
async def soft_delete_user_route(
    user_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Query(None, description="Company ObjectId"),
):
    await soft_delete_user(user_id, company_id)

@router.delete(
    "/{user_id}/permanently",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Hard-delete a user and it cannot be restored",
)
async def delete_user_route(
    user_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Query(None, description="Company ObjectId"),
):
    await delete_user(user_id, company_id)

@router.patch(
    "/{user_id}/restore",
    response_model=UserResponse,
    summary="Restore a soft-deleted user",
)
async def restore_user_route(
    user_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Query(None, description="Company ObjectId"),
):
    return await restore_user(user_id, company_id)


@router.patch(
    "/{user_id}/disable",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate a user",
)
async def disable_user_route(
    user_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Query(None, description="Company ObjectId"),
):
    await disable_user(user_id, company_id)


@router.patch(
    "/{user_id}/activate",
    response_model=UserResponse,
    summary="Activate a disabled user",
)
async def restore_user_route(
    user_id: str = Path(..., description="Brand ObjectId"),
    company_id: str = Query(None, description="Company ObjectId"),
):
    return await activate_user(user_id, company_id)


# from fastapi import APIRouter, Query, Path, status, Depends
# from typing import List, Optional

# from app.schemas.user_setup.user import UserCreate, UserUpdate, UserResponse

# from app.services.user_setup.user import (
#     create_user, get_user_by_id, list_users,
#     update_user, delete_user, restore_user,
#     toggle_active,
# )

# from app.core.auth import require_roles, require_permissions

# router = APIRouter()


# @router.post(
#         "/",
#         response_model=UserResponse,
#         status_code=status.HTTP_201_CREATED,
#         summary="Create a new user account",
# )
# async def register_user(payload: UserCreate) -> UserResponse:
#     return await create_user(payload)

# # --- List ---------------------------------------------------------
# @router.get("/", response_model=List[UserResponse])
# async def list_users_route(
#     skip: int = Query(0, ge=0),
#     limit: int = Query(50, ge=1, le=100),
#     include_deleted: bool = Query(False),
#     email: Optional[str] = None,
#     role: Optional[str] = None,
#     branch: Optional[str] = None,
#     department: Optional[str] = None,
#     warehouse: Optional[str] = None,
# ):
#     return await list_users(
#         skip=skip,
#         limit=limit,
#         include_deleted=include_deleted,
#         email=email,
#         role=role,
#         branch=branch,
#         department=department,
#         warehouse=warehouse,
#     )

# # --- Retrieve -----------------------------------------------------
# @router.get("/{user_id}", response_model=UserResponse)
# async def get_user_by_id_route(
#     user_id: str = Path(..., description="User ObjectId"),
#     include_deleted: bool = Query(False),
# ):
#     return await get_user_by_id(user_id, include_deleted)

# # --- Update -------------------------------------------------------
# @router.put(
#         "/{user_id}", 
#         response_model=UserResponse,
#         # dependencies=[Depends(require_roles("admin"))],
# )
# async def update_user_route(user_id: str, payload: UserUpdate):
#     return await update_user(user_id, payload)

# # --- Soft‑delete --------------------------------------------------
# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user_route(user_id: str):
#     await delete_user(user_id)

# # --- Restore ------------------------------------------------------
# @router.patch("/{user_id}/restore", response_model=UserResponse)
# async def restore_user_route(user_id: str):
#     return await restore_user(user_id)

# # --- Activate / Deactivate ---------------------------------------
# @router.patch("/{user_id}/activate", response_model=UserResponse)
# async def activate_user_route(user_id: str):
#     return await toggle_active(user_id, active=True)

# @router.patch("/{user_id}/deactivate", response_model=UserResponse)
# async def deactivate_user_route(user_id: str):
#     return await toggle_active(user_id, active=False)
