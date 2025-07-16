from typing import TypeVar, Generic, Optional, Type, Any, List, Dict, Union
from beanie import Document, PydanticObjectId
from pydantic import BaseModel
from enum import Enum, auto
from app.services.exceptions import NotFoundError, ValidationError

T = TypeVar('T', bound=Document)
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)

class ObjectState(Enum):
    ACTIVE = auto()
    INACTIVE = auto()
    DELETED = auto()

class FilterOperator(Enum):
    EQ = "=="
    NE = "!="
    GT = ">"
    LT = "<"
    IN = "in"

class BaseCRUDService(Generic[T, CreateSchema, UpdateSchema]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.soft_delete_enabled = hasattr(model, 'is_deleted')
        self.activation_enabled = hasattr(model, 'is_active')
    
    # CREATE
    async def create(self, data: CreateSchema, **kwargs) -> T:
        await self._validate_create(data)
        obj = self.model(**data.model_dump(), **kwargs)
        await obj.insert()
        return obj

    # READ
    async def get(self, id: str, include_deleted: bool = False, **kwargs) -> T:
        try:
            oid = PydanticObjectId(id)
        except Exception:
            raise NotFoundError(f"Invalid ID format: {id}")
        
        query = {"_id": oid}
        if not include_deleted and self.soft_delete_enabled:
            query["is_deleted"] = False
            
        obj = await self.model.find_one(query, **kwargs)
        if not obj:
            raise NotFoundError(f"{self.model.__name__} not found: {id}")
        return obj

    # UPDATE
    async def update(self, id: str, data: UpdateSchema, **kwargs) -> T:
        obj = await self.get(id)
        update_data = data.model_dump(exclude_unset=True)
        await self._validate_update(obj, update_data)
        
        for field, value in update_data.items():
            setattr(obj, field, value)
        await obj.save()
        return obj

    # DELETE
    async def delete(self, id: str, permanent: bool = False, **kwargs) -> bool:
        obj = await self.get(id)
        
        # Check for dependencies if the model has the method
        if hasattr(self, '_check_dependencies'):
            await self._check_dependencies(obj)
            
        if permanent or not self.soft_delete_enabled:
            await obj.delete()
            return True
        
        await self.change_state(obj, ObjectState.DELETED)
        return True

    # LIST
    async def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
        **kwargs
    ) -> List[T]:
        query = self._build_base_query(include_deleted)
        
        if filters:
            for field, value in filters.items():
                if isinstance(value, dict) and 'operator' in value:
                    op = FilterOperator(value['operator'])
                    query = query.find({field: {op.value: value['value']}})
                else:
                    query = query.find({field: value})
        
        if search and hasattr(self.model, 'search_fields'):
            search_conditions = [
                {field: {"$regex": search, "$options": "i"}} 
                for field in self.model.search_fields
            ]
            query = query.find({"$or": search_conditions})
            
        return await query.skip(skip).limit(limit).to_list()

    # STATE MANAGEMENT
    async def change_state(
        self,
        id_or_obj: Union[str, T],
        target_state: ObjectState,
        **kwargs
    ) -> T:
        """Handle state changes with proper validation"""
        obj = await self._get_obj_for_state_change(id_or_obj, target_state)
        
        current_state = self._get_current_state(obj)
        
        # Validate state transition
        if not self._is_valid_transition(current_state, target_state):
            raise ValidationError(
                f"Cannot transition {self.model.__name__} from {current_state.name.lower()} "
                f"to {target_state.name.lower()}"
            )
            
        self._apply_state_change(obj, target_state)
        await obj.save()
        return obj

    async def activate(self, id: str, **kwargs) -> T:
        return await self.change_state(id, ObjectState.ACTIVE, **kwargs)

    async def deactivate(self, id: str, **kwargs) -> T:
        return await self.change_state(id, ObjectState.INACTIVE, **kwargs)

    async def restore(self, id: str, **kwargs) -> T:
        return await self.change_state(id, ObjectState.ACTIVE, **kwargs)

    # PROTECTED METHODS
    async def _get_obj_for_state_change(self, id_or_obj: Union[str, T], target_state: ObjectState) -> T:
        """Helper to get object for state changes with proper include_deleted flag"""
        if isinstance(id_or_obj, str):
            include_deleted = target_state in (ObjectState.ACTIVE, ObjectState.RESTORE)
            return await self.get(id_or_obj, include_deleted=include_deleted)
        return id_or_obj

    def _is_valid_transition(self, current: ObjectState, target: ObjectState) -> bool:
        """Validate state transition rules"""
        transitions = {
            ObjectState.ACTIVE: [ObjectState.INACTIVE, ObjectState.DELETED],
            ObjectState.INACTIVE: [ObjectState.ACTIVE, ObjectState.DELETED],
            ObjectState.DELETED: [ObjectState.ACTIVE]
        }
        return target in transitions.get(current, [])

    def _build_base_query(self, include_deleted: bool = False):
        query = self.model.find()
        if not include_deleted and self.soft_delete_enabled:
            query = query.find(self.model.is_deleted == False)
        if self.activation_enabled:
            query = query.find(self.model.is_active == True)
        return query

    def _get_current_state(self, obj: T) -> ObjectState:
        if getattr(obj, 'is_deleted', False):
            return ObjectState.DELETED
        if not getattr(obj, 'is_active', True):
            return ObjectState.INACTIVE
        return ObjectState.ACTIVE

    def _apply_state_change(self, obj: T, target_state: ObjectState):
        if target_state == ObjectState.ACTIVE:
            obj.is_active = True
            obj.is_deleted = False
        elif target_state == ObjectState.INACTIVE:
            obj.is_active = False
        elif target_state == ObjectState.DELETED:
            obj.is_active = False
            obj.is_deleted = True

    # VALIDATION HOOKS (to be overridden)
    async def _validate_create(self, data: CreateSchema):
        """Pre-create validation"""
        pass

    async def _validate_update(self, obj: T, update_data: dict):
        """Pre-update validation"""
        pass