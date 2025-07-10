from datetime import datetime, timezone
from beanie import PydanticObjectId
from app.models.role import Role
from app.schemas.role import RoleCreate, RoleUpdate, RolePatch
from app.exceptions import RoleNotFound, InvalidPermissionSet

class RoleService:
    @staticmethod
    async def create_role(role_data: RoleCreate, created_by: str) -> Role:
        if await Role.find_one(Role.name == role_data.name):
            raise ValueError("Role with this name already exists")
        
        role = Role(
            **role_data.model_dump(),
            created_by=created_by,
            last_modified_by=created_by
        )
        await role.insert()
        return role

    @staticmethod
    async def list_roles(status: str = None) -> list[Role]:
        query = {}
        if status:
            query["status"] = status
        return await Role.find(query).to_list()

    @staticmethod
    async def get_role(role_id: PydanticObjectId) -> Role:
        role = await Role.get(role_id)
        if not role:
            raise RoleNotFound()
        return role

    @staticmethod
    async def full_update(
        role_id: PydanticObjectId, 
        role_data: RoleUpdate,
        modified_by: str
    ) -> Role:
        role = await Role.get(role_id)
        if not role:
            raise RoleNotFound()
            
        update_data = role_data.model_dump()
        update_data["updated_at"] = datetime.now(timezone.utc)
        update_data["last_modified_by"] = modified_by
        
        await role.update(update_data)
        return role

    @staticmethod
    async def partial_update(
        role_id: PydanticObjectId,
        role_data: RolePatch,
        modified_by: str
    ) -> Role:
        role = await Role.get(role_id)
        if not role:
            raise RoleNotFound()
            
        update_data = role_data.model_dump(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            update_data["last_modified_by"] = modified_by
            await role.update(update_data)
            
        return role

    @staticmethod
    async def archive_role(role_id: PydanticObjectId, modified_by: str) -> None:
        role = await Role.get(role_id)
        if not role:
            raise RoleNotFound()
            
        role.status = "archived"
        role.last_modified_by = modified_by
        role.updated_at = datetime.now(timezone.utc)
        await role.save()