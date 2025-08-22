from typing import (
    Type, TypeVar, Generic, List, Optional, Union, Dict, Any, Tuple
)
from fastapi import Request
from pydantic import BaseModel
from beanie import Document, PydanticObjectId
from collections.abc import Mapping
from datetime import datetime, timezone

from app.services.exceptions import (
    NotFoundError, AlreadyExistsError, ValidationError
)

from app.constants import SortOrder, LogLevel
from app.models.logs import Log

ModelType = TypeVar("ModelType", bound=Document)

PROTECTED_FIELDS = {"_id", "id", "company_id", "created_by", "created_at"}


class CRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def _build_query_filter(
        self,
        company_id: Union[PydanticObjectId, str, None] = None,
        use_company_id: bool = True,  # Flag to conditionally include company_id
        include_deleted: bool = False,
        include_deactivated: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Helper function to build the query filter based on conditions.
        """
        query_filter: Dict[str, Any] = {}

        # Conditionally add company_id to the filter
        if use_company_id and company_id:
            query_filter["company_id"] = PydanticObjectId(company_id)

        if not include_deleted:
            query_filter["is_deleted"] = False

        if not include_deactivated:
            query_filter["is_active"] = True

        # Apply additional filters if provided
        if filters:
            for field, value in filters.items():
                if value is not None:
                    query_filter[field] = (
                        {"$regex": f"^{value}$", "$options": "i"}
                        if isinstance(value, str)
                        else value
                    )

        return query_filter

    async def create(
        self,
        payload: Union[BaseModel, Dict[str, Any]],
        unique_fields: Optional[List[str]] = None,
        session=None
    ) -> ModelType:
        # Process payload
        if isinstance(payload, BaseModel):
            data = payload.model_dump()
        elif isinstance(payload, Mapping):
            data = dict(payload)  # in case it's not a native dict
        else:
            raise ValidationError("Payload must be a Pydantic model or a dictionary")

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
            existing = await self.model.find_one({"$or": filters}, session=session)
            if existing:
                for field in checks:
                    if getattr(existing, field) == data[field].strip():
                        raise AlreadyExistsError(
                            f"{self.model.__name__} '{field}' = {data[field]!r} already exists"
                        )

        # 3) Instantiate & insert
        instance = self.model(**data)
        await instance.insert(session=session)
        return instance

    async def get_by_id(
        self,
        doc_id: Union[PydanticObjectId, str],
        company_id: Union[PydanticObjectId, str] = None,
        include_deleted: bool = False,
        include_deactivated: bool = False,
        session=None,
        use_company_id: bool = True  # Use the flag to decide if company_id is included
    ) -> ModelType:
        try:
            doc_oid = PydanticObjectId(doc_id)
            company_oid = PydanticObjectId(company_id)
        except Exception as e:
            raise ValidationError("Invalid document identifier") from e

        query = self._build_query_filter(
            company_id=company_oid,
            use_company_id=use_company_id,
            include_deleted=include_deleted,
            include_deactivated=include_deactivated
        )
        query["_id"] = doc_oid

        obj = await self.model.find_one(query, session=session)
        if not obj:
            raise NotFoundError("Document not found or inaccessible")

        return obj

    async def list(
        self,
        company_id: Union[PydanticObjectId, str] = None,
        skip: int = 0,
        limit: int = 50,
        include_deleted: bool = False,
        include_deactivated: bool = False,
        filters: Optional[Dict[str, Any]] = None,
        search: Optional[Dict[str, str]] = None,
        exact_match: bool = False,
        sort: Optional[List[Tuple[str, SortOrder]]] = None,
        use_company_id: bool = True  # Flag to conditionally apply company_id
    ) -> List[ModelType]:
        try:
            company_oid = PydanticObjectId(company_id) if company_id else None
        except Exception as e:
            raise ValidationError("Invalid company identifier") from e

        # Use the _build_query_filter helper to generate the filter
        query_filter = self._build_query_filter(
            company_id=company_oid,
            use_company_id=use_company_id,
            include_deleted=include_deleted,
            include_deactivated=include_deactivated,
            filters=filters
        )

        # Apply search criteria
        if search:
            for field, term in search.items():
                if term is not None:
                    query_filter[field] = (
                        {"$regex": f"^{term}$", "$options": "i"} 
                        if exact_match 
                        else {"$regex": term, "$options": "i"}
                    )

        # Sorting logic
        sort_params = [(field, order.value) for field, order in (sort or [("_id", SortOrder.ASC)])]

        return await self.model.find(query_filter).sort(sort_params).skip(skip).limit(limit).to_list()

    async def update(
        self,
        payload: BaseModel,
        doc_id: Union[PydanticObjectId, str],
        user_id: Union[PydanticObjectId, str], # Use to track who made the change
        company_id: Union[PydanticObjectId, str, None] = None,
        unique_fields: Optional[List[str]] = None,
        session=None,
        use_company_id: bool = True,  # Flag to conditionally apply company_id
    ) -> ModelType:
        obj = await self.get_by_id(
            doc_id=doc_id, company_id=company_id,
            session=session, use_company_id=use_company_id,
            include_deleted=True, include_deactivated=True
        )

        # Validate user_id
        try:
            user_oid = PydanticObjectId(str(user_id))
        except Exception:
            raise ValidationError("Invalid user_id")

        # Normalize payload
        if isinstance(payload, BaseModel):
            incoming = payload.model_dump(exclude_unset=True)
        elif isinstance(payload, Mapping):
            incoming = dict(payload)
        else:
            raise ValidationError("Payload must be a Pydantic model or a dictionary")

        # Remove protected fields
        for f in list(incoming.keys()):
            if f in PROTECTED_FIELDS:
                incoming.pop(f)

        # Uniqueness checks (accept non-strings too)
        checks = [f for f in (unique_fields or []) if f in incoming]
        dup_filters = []
        for field in checks:
            val = incoming[field]
            if isinstance(val, str) and not val.strip():
                raise ValidationError(f"'{field}' must not be empty")
            filt = {field: val}
            if use_company_id and getattr(obj, "company_id", None):
                filt["company_id"] = obj.company_id
            filt["_id"] = {"$ne": obj.id}
            dup_filters.append(filt)

        if dup_filters:
            existing = await self.model.find_one({"$or": dup_filters}, session=session)
            if existing:
                raise AlreadyExistsError(f"{self.model.__name__} with these values already exists")

        # Compute delta vs current object to avoid no-op writes
        to_set = {}
        for k, v in incoming.items():
            if getattr(obj, k, None) != v:
                to_set[k] = v

        if not to_set:
            # Nothing changed; return without mutating audit fields
            return obj

        # Audit fields
        to_set["updated_by"] = user_oid
        # to_set["updated_at"] = datetime.now(timezone.utc)

        # Optional optimistic concurrency (if you track updated_at or version)
        # match = {"_id": obj.id, "updated_at": obj.updated_at}  # if present
        match = {"_id": obj.id}

        # Atomic update
        updated = await self.model.find_one(match, session=session).update({"$set": to_set})
        if not updated:
            # If using optimistic locking with updated_at/version, this indicates a conflict
            # raise ConflictError("Document was updated by someone else. Please retry.")
            pass

        # Re-fetch fresh document
        return await self.get_by_id(
            doc_id=doc_id, company_id=company_id,
            session=session, use_company_id=use_company_id,
            include_deleted=True, include_deactivated=True
        )

    async def update_flags(
        self,
        doc_id: Union[PydanticObjectId, str],
        user_id: Union[PydanticObjectId, str],
        company_id: Union[PydanticObjectId, str] = None,
        fields: List[Tuple[str, bool]] = None,
        session=None,
        use_company_id: bool = True  # Flag to conditionally apply company_id
    ) -> ModelType:
        # To ensure update always works if the document exist irrepective of delete and active status
        # set include_deleted=True and include_deactivated=True
        obj = await self.get_by_id(
            doc_id=doc_id, company_id=company_id, 
            include_deleted=True, include_deactivated=True,            
            session=session, use_company_id=use_company_id
        )

        # Validate user_id
        try:
            user_oid = PydanticObjectId(str(user_id))
        except Exception:
            raise ValidationError("Invalid user_id")

        if not fields:
            raise ValidationError("No fields provided")

        for field, value in fields:
            if not hasattr(obj, field):
                raise ValidationError(f"Invalid field '{field}'")
            if not isinstance(value, bool):
                raise ValidationError("Flag values must be boolean")
            setattr(obj, field, value)

        setattr(obj, "updated_by", user_oid)

        await obj.save(session=session)
        return obj

    async def delete(
        self,
        doc_id: Union[PydanticObjectId, str],
        user_id: Union[PydanticObjectId, str],
        company_id: Union[PydanticObjectId, str] = None,
        hard_delete: bool = False,
        session=None,
        use_company_id: bool = True,  # Flag to conditionally apply company_id
        request: Request = None
    ) -> None:
        # To ensure update always works if the document exist irrepective of delete and active status
        # set include_deleted=True and include_deactivated=True
        obj = await self.get_by_id(
            doc_id=doc_id, company_id=company_id, 
            include_deleted=True, include_deactivated=True,            
            session=session, use_company_id=use_company_id
        )

        if hard_delete:

            endpoint = str(request.url) if request and hasattr(request, "url") else None
            method = str(request.method) if request and hasattr(request, "method") else None
            headers = {k: str(v)[:100] for k, v in request.headers.items()} if request and hasattr(request, "headers") else {}
            query_params = {k: str(v)[:200] for k, v in request.query_params.items()} if request and hasattr(request, "query_params") else {}
            client_host = request.client.host if request and hasattr(request, "client") and hasattr(request.client, "host") else None

            deleted_data = obj.model_dump()  # snapshot of the document

            await Log(
                user_id=str(user_id) if user_id else None,
                endpoint=endpoint,
                action=method,
                level=LogLevel.PERMANENT_DELETE,
                details={
                    "deleted_doc": deleted_data,
                    "error_msg": "",
                    "headers": headers,
                    "query_params": query_params,
                    "client_host": client_host
                }
            ).insert()

            await obj.delete(session=session)
        else:
            obj.is_deleted = True
            obj.updated_by = user_id
            obj.deleted_by = user_id
            obj.deleted_at = datetime.now(timezone.utc)
            await obj.save(session=session)
