from fastapi import HTTPException
from typing import Optional, Dict, Any
from bson import ObjectId
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPatch
from app.core.security import get_password_hash
from app.core.logger import logger


async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one(User.email == email)


async def get_user_by_id(user_id: str) -> Optional[User]:
    try:
        return await User.get(ObjectId(user_id))
    except Exception as e:
        logger.warning(f"Failed to get user by id {user_id}: {e}")
        return None

async def get_users(
    skip: int = 0,
    limit: int = 10,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    email: Optional[str] = None
) -> Dict[str, object]:
    try:
        query: Dict[str, Any] = {}

        if role:
            query["role"] = role
        if is_active is not None:
            query["is_active"] = is_active
        if email:
            query["email"] = {"$regex": email, "$options": "i"}  # case-insensitive partial match

        print(f"Fetching users with skip={skip}, limit={limit}, filters={query}")

        total = await User.find(query).count()
        users = await User.find(query).skip(skip).limit(limit).to_list()

        return {
            "items": users,
            "total": total
        }

    except Exception as e:
        print(f"Error in get_users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_user(user_data: UserCreate) -> User:
    user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role
    )
    await user.insert()
    return user


async def update_user(user_id: str, user_data: UserUpdate) -> Optional[User]:
    user = await get_user_by_id(user_id)
    if not user:
        return None

    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await user.save()
    return user


async def partial_update_user(user_id: str, patch_data: UserPatch) -> Optional[User]:
    return await update_user(user_id, patch_data)


async def delete_user(user_id: str) -> bool:
    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    result = await User.find(User.id == obj_id).delete()
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found.")
