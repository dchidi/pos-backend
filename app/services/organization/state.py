from typing import List, Optional
from beanie import PydanticObjectId
from app.models.organization.state import State
from app.schemas.organization.location import StateCreate, LocationUpdate
from app.services.exceptions import NotFoundError, AlreadyExistsError, ValidationError


async def create_state(data: StateCreate) -> State:
    """Create a new state, enforcing business rules."""
    if not (data.name.strip() or data.name.strip()):
        raise ValidationError("State name or code must not be empty")
    # Unique name check
    existing_state = await State.find_one({"code":data.code})
    if existing_state:
        raise AlreadyExistsError(f"State '{data.name}' or '{data.code}' already exists")
    state = State(**data.model_dump())
    await state.insert()
    return state

async def get_state(state_id: str, include_flag: bool = False) -> State:
    """Retrieve a state by ID, optionally including deleted ones."""
    try:
        oid = PydanticObjectId(state_id)
    except Exception:
        raise NotFoundError(f"Invalid state ID '{state_id}'")
    state = await State.get(oid)
    if not state or (state.is_deleted and not include_flag):
        raise NotFoundError(f"State '{state_id}' not found or deleted")
    return state

async def list_states(
    skip: int = 0,
    limit: int = 50,
    include_deleted: bool = False,
    name: Optional[str] = None,
    code: Optional[str] = None,
    created_by: Optional[str] = None,    
    updated_by: Optional[str] = None,
) -> List[State]:
    """List states with optional filters and deletion flag."""
    qb = State.find()
    # Soft-delete filter
    if not include_deleted:
        qb = qb.find(State.is_active == True, State.is_deleted == False)
    # Name filter
    if name:
        qb = qb.find(State.name == name)
    # Cpde filter
    if code:
        qb = qb.find(State.code == code)
    # created by filter
    if created_by:
        qb = qb.find({'created_by': created_by})

    if updated_by:
        qb = qb.find({'updated_by': updated_by})
    return await qb.skip(skip).limit(limit).to_list()

async def update_state(state_id: str, data: LocationUpdate) -> State:
    """Update fields on an existing state."""
    state = await get_state(state_id)
    update_data = data.model_dump(exclude_unset=True)
    # Name validations
    if 'name' in update_data or 'code' in update_data:
        if not update_data['name'].strip():
            raise ValidationError("State name must not be empty")
        
        if 'name' in update_data or 'code' in update_data:
            # Check for conflicts in name OR code
            existing = await State.find_one({
                "$or": [
                    {"name": update_data.get('name'), "_id": {"$ne": state.id}},
                    {"code": update_data.get('code'), "_id": {"$ne": state.id}},
                ]
            })
            if existing:
                conflict_field = "name" if existing.name == update_data.get('name') else "code"
                raise AlreadyExistsError(
                    f"State {conflict_field} '{update_data[conflict_field]}' already exists"
                )
        
    for field, val in update_data.items():
        setattr(state, field, val)
    await state.replace()
    return state

async def delete_state(state_id: str) -> None:
    """Soft-delete a state."""
    state = await get_state(state_id)
    state.is_active = False
    state.is_deleted = True
    await state.replace()

async def restore_state(state_id: str) -> State:
    """Restore a previously soft-deleted state."""
    state = await get_state(state_id, include_flag=True)
    if not state.is_deleted:
        raise ValidationError(f"State '{state_id}' is not deleted")
    state.is_deleted = False
    state.is_active = True
    await state.replace()
    return state


async def disable_state(state_id: str) -> None:
    """Deactivate a state."""
    state = await get_state(state_id)
    state.is_active = False
    await state.replace()


async def activate_state(state_id: str) -> State:
    """Restore a previously soft-deleted state."""
    state = await get_state(state_id, include_flag=True)
    if state.is_active:
        raise ValidationError(f"State '{state_id}' is not disabled")
    state.is_active = True
    await state.replace()
    return state
