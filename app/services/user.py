from fastapi import Depends
from typing import List, Optional, Tuple, Any, Dict
from beanie import PydanticObjectId

from app.models.user_setup.user import User
from app.models.inventory.warehouse.user_warehouse_access import UserWarehouseAccess

from app.schemas.user import UserCreate, UserUpdate

from app.services.crud_services import CRUD
from app.services.auth import (
  get_current_company, get_password_hash
)




from app.constants import SortOrder


from app.utils.db_transaction import with_transaction

user_crud = CRUD(User)
user_wh_crud = CRUD(UserWarehouseAccess)



@with_transaction()
async def create_user(
    user_data: UserCreate, session=None
) -> User:
    # Extract and exclude fields as needed
    warehouse_id = user_data.warehouse_id
    plain_password = user_data.password
    user_dict = user_data.model_dump(exclude={"password", "warehouse_id"})
    
    # Get hashed password
    user_dict["hashed_password"] = get_password_hash(plain_password)

    # Validate unique fields and create user record
    created_user = await user_crud.create(
        user_dict,
        unique_fields=["email"],
        session=session
    )
    
    # Link user with warehouse
    if warehouse_id:
        access_data = UserWarehouseAccess(
            user_id=created_user.id,
            company_id=created_user.company_id,
            warehouse_id=warehouse_id
        )
        await user_wh_crud.create(access_data, session=session)
 
    return created_user

async def get_user(
    user_id: str,
    company_id:PydanticObjectId = Depends(get_current_company),
    include_flag: bool = False
) -> User:
    res = await user_crud.get_by_id(user_id, company_id, include_flag)
    return res


async def list_users(
    company_id:PydanticObjectId = Depends(get_current_company),
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    filters: Optional[Dict[str, Any]] = None,
    search: Optional[Dict[str, Any]] = None,
    sort_order: Optional[List[Tuple[str, SortOrder]]] = None,
    exact_match: Optional[bool] = False
) -> List[User]:

    res = await user_crud.list(
        company_id,
        skip,
        limit,
        include_deleted,
        filters=filters,
        sort=sort_order,
        search=search,
        exact_match=exact_match if exact_match is not None else False
    )
    return res


async def update_user(
    user_id: str,
    data: UserUpdate,     
    company_id:PydanticObjectId = Depends(get_current_company)
) -> User:
    res = await user_crud.update(user_id, company_id, data, unique_fields=["name", "code"])
    return res

async def soft_delete_user(
    user_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> None:
    """Soft-delete a user."""
    res = await user_crud.update_flags(user_id, company_id,  fields=[("is_deleted", True), ("is_active", False)])
    return res

async def delete_user(
    user_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> None:
    """hard-delete a user."""
    res = await user_crud.delete(user_id, company_id, hard_delete= True)
    return res

async def restore_user(
    user_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> User:
    """Restore a previously soft-deleted user."""
    res = await user_crud.update_flags(user_id, company_id, fields=[("is_deleted", False), ("is_active", True)])
    return res


async def disable_user(
    user_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> None:
    """Deactivate a user."""
    res = await user_crud.update_flags(user_id, company_id, [("is_active", False)])
    return res


async def activate_user(
    user_id: str,
    company_id:PydanticObjectId = Depends(get_current_company)
) -> User:
    """Restore a previously deactivated user."""
    res = await user_crud.update_flags(user_id, company_id, [("is_active", True)])
    return res
