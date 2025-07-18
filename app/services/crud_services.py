from token import OP
from typing import (
    Type, TypeVar, Generic, List, Optional, Union, Dict, Any, Tuple
)
from pydantic import BaseModel
from beanie import Document, PydanticObjectId
from app.services.exceptions import (
    NotFoundError, AlreadyExistsError, ValidationError
)
from app.constants.sort_order import SortOrder

ModelType = TypeVar("ModelType", bound=Document)


class CRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(
        self,
        payload: BaseModel,
        unique_fields: Optional[List[str]] = None
    ) -> ModelType:
        """
        Create a new document, validating and enforcing uniqueness on specified fields.
        :param payload: A Pydantic model with the data to insert.
        :param unique_fields: List of document field names to check for uniqueness.
        :returns: The inserted document instance.
        """
        data = payload.model_dump()
        checks = unique_fields or []

        # 1) Validate non-empty for each unique field
        filters = []
        for field in checks:
            val = data.get(field, "")
            if not isinstance(val, str) or not val.strip():
                raise ValidationError(f"'{field}' must not be empty")
            filters.append({field: val.strip()})

        # 2) Check for duplicates
        if filters:
            existing = await self.model.find_one({"$or": filters})
            if existing:
                for field in checks:
                    if getattr(existing, field) == data[field].strip():
                        raise AlreadyExistsError(
                            f"{self.model.__name__} '{field}' = {data[field]!r} already exists"
                        )

        # 3) Instantiate & insert
        instance = self.model(**data)
        await instance.insert()
        return instance

    async def get_by_id(
        self,
        doc_id: Union[PydanticObjectId, str],
        include_deleted: bool = False
    ) -> ModelType:
        try:
            oid = PydanticObjectId(doc_id)
        except Exception:
            raise NotFoundError(f"Invalid ID '{doc_id}'")

        obj = await self.model.get(oid)
        if obj is None or (getattr(obj, 'is_deleted', False) and not include_deleted):
            raise NotFoundError(f"{self.model.__name__} with ID '{doc_id}' not found")
        return obj

    # async def list(
    #     self,
    #     skip: int = 0,
    #     limit: int = 50,
    #     include_deleted: bool = False,
    #     filters: Optional[Dict[str, Any]] = None,
    #     sort: Optional[List[Tuple[str, SortOrder]]] = None
    # ) -> List[ModelType]:
    #     """
    #     List documents with optional filters, pagination, soft-delete flag, and sorting.
    #     :param skip: Number of documents to skip.
    #     :param limit: Maximum number of documents to return.
    #     :param include_deleted: Whether to include soft-deleted documents.
    #     :param filters: Field-based equality filters; keys with None values are ignored.
    #     :param sort: List of (field, SortOrder) tuples; defaults to _id ASC.
    #     :returns: List of document instances.
    #     """
    #     # Build base filter dict
    #     query_filter: Dict[str, Any] = {}
    #     if not include_deleted:
    #         query_filter['is_deleted'] = False
    #     # Merge non-None filters
    #     if filters:
    #         for field, value in filters.items():
    #             if value is not None:
    #                 query_filter[field] = value

    #     # Determine sort parameters: use SortOrder enum values
    #     sort_orders = sort or [("_id", SortOrder.ASC)]
    #     sort_params = [(field, order.value) for field, order in sort_orders]

    #     # Execute query once with combined filters and sort
    #     qb = self.model.find(query_filter).sort(sort_params)
    #     return await qb.skip(skip).limit(limit).to_list()

    async def list(
        self,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[Dict[str, str]] = None,
        exact_match: bool = False,
        sort: Optional[List[tuple[str, SortOrder]]] = None
    ) -> List[ModelType]:
        """
        List documents with optional filters, search, pagination, soft-delete flag, and sorting.
        :param skip: Number of documents to skip.
        :param limit: Maximum number of documents to return.
        :param include_deleted: Whether to include soft-deleted documents.
        :param filters: Field-based equality filters; keys with None values are ignored.
        :param search: Field-based string searches; values are patterns or exact.
        :param exact_match: Determines if 'search' uses exact or pattern matching.
        :param sort: List of (field, SortOrder) pairs; defaults to _id ASC.
        :returns: List of document instances.
        """
        # Build base filter dict
        query_filter: Dict[str, Any] = {}
        if not include_deleted:
            query_filter['is_deleted'] = False
        # Merge equality filters
        if filters:
            for field, value in filters.items():
                if value is None:
                    continue
                if not isinstance(value, str):
                    query_filter[field] = value
                else:
                    # exact match, case-insensitive
                    query_filter[field] = {"$regex": f"^{value}$", "$options": "i"}
        # Add search criteria
        if search:
            for field, term in search.items():
                if term is None:
                    continue
                if exact_match:
                    # exact match, case-insensitive
                    query_filter[field] = {"$regex": f"^{term}$", "$options": "i"}
                else:
                    # substring or regex search, case-insensitive
                    query_filter[field] = {"$regex": term, "$options": "i"}

        # Determine sort parameters: use SortOrder enum values
        sort_orders = sort or [("_id", SortOrder.ASC)]
        sort_params = [(field, order.value) for field, order in sort_orders]

        # Execute query once with combined filters and sort
        qb = self.model.find(query_filter).sort(sort_params)
        return await qb.skip(skip).limit(limit).to_list()

    async def update(
        self,
        doc_id: Union[PydanticObjectId, str],
        payload: BaseModel,
        unique_fields: Optional[List[str]] = None
    ) -> ModelType:
        obj = await self.get_by_id(doc_id)
        data = payload.model_dump(exclude_unset=True)
        checks = [f for f in (unique_fields or []) if f in data]

        # Validate non-empty and build duplicate filters
        dup_filters = []
        for field in checks:
            val = data[field]
            if not isinstance(val, str) or not val.strip():
                raise ValidationError(f"'{field}' must not be empty")
            dup_filters.append({field: val.strip(), '_id': {'$ne': obj.id}})

        # Check for duplicates
        if dup_filters:
            existing = await self.model.find_one({'$or': dup_filters})
            if existing:
                for field in checks:
                    if getattr(existing, field) == data[field].strip():
                        raise AlreadyExistsError(
                            f"{self.model.__name__} '{field}' = {data[field]!r} already exists"
                        )

        # Apply updates
        for field, val in data.items():
            setattr(obj, field, val)
        await obj.replace()
        return obj

    async def soft_delete(
        self,
        doc_id: Union[PydanticObjectId, str]
    ) -> ModelType:
        obj = await self.get_by_id(doc_id, include_deleted=True)
        setattr(obj, 'is_deleted', True)
        await obj.save()
        return obj

    async def delete(
        self,
        doc_id: Union[PydanticObjectId, str]
    ) -> None:
        obj = await self.get_by_id(doc_id, include_deleted=True)
        await obj.delete()
