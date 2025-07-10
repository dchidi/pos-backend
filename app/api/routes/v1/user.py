from fastapi import APIRouter, HTTPException, status, Depends, Path
from app.schemas.user import (
    UserCreate, UserUpdate, UserPatch,
    UserResponse, PaginatedUserResponse,
    PaginationParams, UserFilterParams
)
from app.services.user_service import (
    get_users, get_user_by_id, get_user_by_email,
    create_user, update_user, partial_update_user, delete_user
)
from app.exceptions import(
  UserNotFound, InvalidUserId, 
  EmailAlreadyExists
)
from app.core.auth import require_roles, require_permissions

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# @limiter.limit("100/minute") --rate limit for individual routes
async def register_user(user: UserCreate) -> UserResponse:
    try:
        return await create_user(user)
    except EmailAlreadyExists:
        raise HTTPException(status_code=400, detail="Email already registered.")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to register user.")


@router.get("/", response_model=PaginatedUserResponse)
async def list_users(
    params: PaginationParams = Depends(),
    filters: UserFilterParams = Depends(),
    _ = Depends(require_permissions("admin"))
) -> PaginatedUserResponse:
    try:
        return await get_users(
            skip=params.skip,
            limit=params.limit,
            role=filters.role,
            is_active=filters.is_active,
            email=filters.email
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to fetch users.")


@router.get("/{user_id}", response_model=UserResponse)
async def retrieve_user(user_id: str = Path(..., title="User ID")) -> UserResponse:
    try:
        return await get_user_by_id(user_id)
    except InvalidUserId:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve user.")


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_details(
    user_id: str,
    updated_data: UserUpdate,
    _ = Depends(require_roles("admin"))
) -> UserResponse:
    try:
        return await update_user(user_id, updated_data)
    except InvalidUserId:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to update user.")


@router.patch("/{user_id}", response_model=UserResponse)
async def patch_user_details(
    user_id: str,
    partial_data: UserPatch,
    _ = Depends(require_roles("admin"))
) -> UserResponse:
    try:
        return await partial_update_user(user_id, partial_data)
    except InvalidUserId:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to patch user.")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_user(
    user_id: str,
    _ = Depends(require_roles("admin"))
):
    try:
        await delete_user(user_id)
    except InvalidUserId:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")
    except UserNotFound:
        raise HTTPException(status_code=404, detail="User not found.")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to delete user.")

