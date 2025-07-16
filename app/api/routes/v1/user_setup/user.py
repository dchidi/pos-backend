# from fastapi import APIRouter, HTTPException, status, Depends, Path
# from app.schemas.user import (
#     UserCreate, UserUpdate, UserPatch,
#     UserResponse, PaginatedUserResponse,
#     PaginationParams, UserFilterParams
# )
# from app.services.user_service import (
#     get_user_by_ids, get_user_by_id_by_id, get_user_by_id_by_email,
#     create_user, update_user, partial_update_user, delete_user
# )
# from app.services.exceptions import(
#   UserNotFound, InvalidUserId, 
#   EmailAlreadyExists
# )
# from app.core.auth import require_roles, require_permissions

# router = APIRouter()


# @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# # @limiter.limit("100/minute") --rate limit for individual routes
# async def register_user(user: UserCreate) -> UserResponse:
#     try:
#         return await create_user(user)
#     except EmailAlreadyExists:
#         raise HTTPException(status_code=400, detail="Email already registered.")
#     except Exception as e:
#         print(e)
#         raise HTTPException(status_code=500, detail="Failed to register user.")


# @router.get("/", response_model=PaginatedUserResponse)
# async def list_users(
#     params: PaginationParams = Depends(),
#     filters: UserFilterParams = Depends(),
#     _ = Depends(require_permissions("admin"))
# ) -> PaginatedUserResponse:
#     try:
#         return await get_user_by_ids(
#             skip=params.skip,
#             limit=params.limit,
#             role=filters.role,
#             is_active=filters.is_active,
#             email=filters.email
#         )
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to fetch users.")


# @router.get("/{user_id}", response_model=UserResponse)
# async def retrieve_user(user_id: str = Path(..., title="User ID")) -> UserResponse:
#     try:
#         return await get_user_by_id_by_id(user_id)
#     except InvalidUserId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format.")
#     except UserNotFound:
#         raise HTTPException(status_code=404, detail="User not found.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to retrieve user.")


# @router.put("/{user_id}", response_model=UserResponse)
# async def update_user_details(
#     user_id: str,
#     updated_data: UserUpdate,
#     _ = Depends(require_roles("admin"))
# ) -> UserResponse:
#     try:
#         return await update_user(user_id, updated_data)
#     except InvalidUserId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format.")
#     except UserNotFound:
#         raise HTTPException(status_code=404, detail="User not found.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to update user.")


# @router.patch("/{user_id}", response_model=UserResponse)
# async def patch_user_details(
#     user_id: str,
#     partial_data: UserPatch,
#     _ = Depends(require_roles("admin"))
# ) -> UserResponse:
#     try:
#         return await partial_update_user(user_id, partial_data)
#     except InvalidUserId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format.")
#     except UserNotFound:
#         raise HTTPException(status_code=404, detail="User not found.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to patch user.")


# @router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_user(
#     user_id: str,
#     _ = Depends(require_roles("admin"))
# ):
#     try:
#         await delete_user(user_id)
#     except InvalidUserId:
#         raise HTTPException(status_code=400, detail="Invalid user ID format.")
#     except UserNotFound:
#         raise HTTPException(status_code=404, detail="User not found.")
#     except Exception:
#         raise HTTPException(status_code=500, detail="Failed to delete user.")

from fastapi import APIRouter, Query, Path, status, Depends
from typing import List, Optional

from app.schemas.user_setup.user import UserCreate, UserUpdate, UserResponse

from app.services.user_setup.user import (
    create_user, get_user_by_id, list_users,
    update_user, delete_user, restore_user,
    toggle_active,
)

from app.core.auth import require_roles, require_permissions

router = APIRouter()


@router.post(
        "/",
        response_model=UserResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Create a new user account",
)
async def register_user(payload: UserCreate) -> UserResponse:
    return await create_user(payload)

# --- List ---------------------------------------------------------
@router.get("/", response_model=List[UserResponse])
async def list_users_route(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    include_deleted: bool = Query(False),
    email: Optional[str] = None,
    role: Optional[str] = None,
    branch: Optional[str] = None,
    department: Optional[str] = None,
    warehouse: Optional[str] = None,
):
    return await list_users(
        skip=skip,
        limit=limit,
        include_deleted=include_deleted,
        email=email,
        role=role,
        branch=branch,
        department=department,
        warehouse=warehouse,
    )

# --- Retrieve -----------------------------------------------------
@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id_route(
    user_id: str = Path(..., description="User ObjectId"),
    include_deleted: bool = Query(False),
):
    return await get_user_by_id(user_id, include_deleted)

# --- Update -------------------------------------------------------
@router.put(
        "/{user_id}", 
        response_model=UserResponse,
        # dependencies=[Depends(require_roles("admin"))],
)
async def update_user_route(user_id: str, payload: UserUpdate):
    return await update_user(user_id, payload)

# --- Soft‑delete --------------------------------------------------
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_route(user_id: str):
    await delete_user(user_id)

# --- Restore ------------------------------------------------------
@router.patch("/{user_id}/restore", response_model=UserResponse)
async def restore_user_route(user_id: str):
    return await restore_user(user_id)

# --- Activate / Deactivate ---------------------------------------
@router.patch("/{user_id}/activate", response_model=UserResponse)
async def activate_user_route(user_id: str):
    return await toggle_active(user_id, active=True)

@router.patch("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user_route(user_id: str):
    return await toggle_active(user_id, active=False)
