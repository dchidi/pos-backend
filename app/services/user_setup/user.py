from typing import List, Optional, Set

from beanie import PydanticObjectId
from app.models.user_setup.user import User
from app.schemas.user_setup.user import UserCreate, UserUpdate
from app.services.exceptions import (
    AlreadyExistsError,
    NotFoundError,
    ValidationError,
)

from app.core.security import get_password_hash

async def get_user_by_email(email: str) -> Optional[User]:
    return await User.find_one({"email":email})


async def get_user_by_id(user_id: str, include_deleted: bool = False) -> User:
    try:
        obj_id = PydanticObjectId(user_id)
    except Exception:
        raise ValidationError(f"Invalid user ID '{user_id}'")

    user = await User.get(obj_id)

    if not user:
        raise NotFoundError("Invalid user ID")
    
    if not user or (user.is_deleted and not include_deleted):
        raise NotFoundError("User not found")
    
    return user


# async def get_users(
#     skip: int = 0,
#     limit: int = 10,
#     role: Optional[str] = None,
#     is_active: Optional[bool] = None,
#     email: Optional[str] = None
# ) -> Dict[str, object]:
#     query: Dict[str, Any] = {}
#     if role:
#         query["role"] = role
#     if is_active is not None:
#         query["is_active"] = is_active
#     if email:
#         query["email"] = {"$regex": email, "$options": "i"}

#     total = await User.find(query).count()
#     users = await User.find(query).skip(skip).limit(limit).to_list()
#     return {"items": users, "total": total}


async def create_user(user_data: UserCreate) -> User:
    if await get_user_by_email(user_data.email):
        raise AlreadyExistsError(f"Email '{user_data.email}' already registered")

    user_dict = user_data.model_dump(exclude={"password"})
    user_dict["hashed_password"] = get_password_hash(user_data.password)

    user = User(**user_dict)
    await user.insert()
    return user



async def list_users(
    *,
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    email: Optional[str] = None,
    role: Optional[str] = None,
    branch: Optional[str] = None,
    department: Optional[str] = None,
    warehouse: Optional[str] = None,
) -> List[User]:
    qb = User.find()

    if not include_deleted:
        qb = qb.find(User.is_deleted == False, User.is_active == True)
    if email:
        qb = qb.find(User.email == email)
    if role:
        qb = qb.find(User.role == role)
    if branch:
        qb = qb.find({"branch_ids": PydanticObjectId(branch)})
    if department:
        qb = qb.find(User.department_id == PydanticObjectId(department))
    if warehouse:
        qb = qb.find(User.warehouse_id == PydanticObjectId(warehouse))

    return await qb.skip(skip).limit(limit).to_list()


async def update_user(user_id: str, data: UserUpdate) -> User:
    user = await get_user_by_id(user_id)

    changes = data.model_dump(exclude_unset=True)

    # unique‑email validation
    if "email" in changes:
        if await User.find_one({"email": changes["email"], "_id": {"$ne": user.id}}):
            raise AlreadyExistsError("Email already in use")

    # dedupe sets before assigning
    if "permissions" in changes:
        changes["permissions"] = set(changes["permissions"])
    if "branch_ids" in changes:
        changes["branch_ids"] = set(changes["branch_ids"])

    for k, v in changes.items():
        setattr(user, k, v)

    await user.replace()
    return user


async def delete_user(user_id: str) -> None:
    user = await get_user_by_id(user_id)
    user.is_active = False
    user.is_deleted = True
    await user.replace()


async def restore_user(user_id: str) -> User:
    user = await get_user_by_id(user_id, include_deleted=True)
    if not user.is_deleted:
        raise ValidationError("User is not deleted")
    user.is_deleted = False
    user.is_active = True
    await user.replace()
    return user


async def toggle_active(user_id: str, *, active: bool) -> User:
    user = await get_user_by_id(user_id)
    user.is_active = active
    await user.replace()
    return user

# from typing import Optional, Dict, Any
# from bson import ObjectId
# from app.models.user import User
# from app.schemas.user import UserCreate, UserUpdate, UserPatch
# from app.core.security import get_password_hash
# from app.services.exceptions import NotFoundError, ValidationError, AlreadyExistsError


# async def get_user_by_email(email: str) -> Optional[User]:
#     return await User.find_one(User.email == email)


# async def get_user_by_id(user_id: str) -> User:
#     try:
#         obj_id = ObjectId(user_id)
#     except Exception:
#         raise ValidationError()

#     user = await User.get(obj_id)
#     if not user:
#         raise NotFoundError()
#     return user


# async def get_users(
#     skip: int = 0,
#     limit: int = 10,
#     role: Optional[str] = None,
#     is_active: Optional[bool] = None,
#     email: Optional[str] = None
# ) -> Dict[str, object]:
#     query: Dict[str, Any] = {}
#     if role:
#         query["role"] = role
#     if is_active is not None:
#         query["is_active"] = is_active
#     if email:
#         query["email"] = {"$regex": email, "$options": "i"}

#     total = await User.find(query).count()
#     users = await User.find(query).skip(skip).limit(limit).to_list()
#     return {"items": users, "total": total}


# async def create_user(user_data: UserCreate) -> User:
#     if await get_user_by_email(user_data.email):
#         raise AlreadyExistsError()

#     user_dict = user_data.model_dump(exclude={"password"})
#     user_dict["hashed_password"] = get_password_hash(user_data.password)

#     user = User(**user_dict)
#     await user.insert()
#     return user

# # async def create_brand(data: BrandCreate) -> Brand:
# #     """Create a new brand, enforcing business rules."""
# #     if not data.name.strip():
# #         raise ValidationError("Brand name must not be empty")
# #     # Unique name check
# #     existing_brand = await Brand.find_one({"name":data.name})
# #     if existing_brand:
# #         raise AlreadyExistsError(f"Brand '{data.name}' already exists")
# #     brand = Brand(**data.model_dump())
# #     await brand.insert()
# #     return brand


# async def update_user(user_id: str, user_data: UserUpdate) -> User:
#     user = await get_user_by_id(user_id)
#     update_data = user_data.model_dump(exclude_unset=True)
#     for field, value in update_data.items():
#         setattr(user, field, value)
#     await user.save()
#     return user


# async def partial_update_user(user_id: str, patch_data: UserPatch) -> User:
#     return await update_user(user_id, patch_data)


# async def delete_user(user_id: str) -> None:
#     try:
#         obj_id = ObjectId(user_id)
#     except Exception:
#         raise ValidationError()

#     result = await User.find(User.id == obj_id).delete()
#     if result.deleted_count == 0:
#         raise NotFoundError()
