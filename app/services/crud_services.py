# from typing import (
#     Type, TypeVar, Generic, List, Optional, Union, Dict, Any, Tuple
# )
# from pydantic import BaseModel
# from beanie import Document, PydanticObjectId
# from collections.abc import Mapping

# from app.services.exceptions import (
#     NotFoundError, AlreadyExistsError, ValidationError
# )


# from app.constants.sort_order import SortOrder


# ModelType = TypeVar("ModelType", bound=Document)


from typing import (
    Type, TypeVar, Generic, List, Optional, Union, Dict, Any, Tuple
)
from pydantic import BaseModel
from beanie import Document, PydanticObjectId
from collections.abc import Mapping

from app.services.exceptions import (
    NotFoundError, AlreadyExistsError, ValidationError
)

from app.constants.sort_order import SortOrder

ModelType = TypeVar("ModelType", bound=Document)


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
        company_id: Union[PydanticObjectId, str, None] = None,  # Make company_id optional
        unique_fields: Optional[List[str]] = None,
        session=None,
        use_company_id: bool = True  # Flag to conditionally apply company_id
    ) -> ModelType:
        obj = await self.get_by_id(doc_id, company_id, session=session, use_company_id=use_company_id)

        if isinstance(payload, BaseModel):
            data = payload.model_dump(exclude_unset=True)
        elif isinstance(payload, Mapping):
            data = dict(payload)  # in case it's not a native dict
        else:
            raise ValidationError("Payload must be a Pydantic model or a dictionary")

        checks = [f for f in (unique_fields or []) if f in data]

        # Duplicate check scoped to company, only if company_id exists in the model
        dup_filters = []
        for field in checks:
            val = data[field]
            if not isinstance(val, str) or not val.strip():
                raise ValidationError(f"'{field}' must not be empty")
            
            # Only add company_id to the check if it exists and is relevant (i.e., if use_company_id is True)
            if use_company_id and obj.company_id:
                dup_filters.append({
                    field: val.strip(),
                    "company_id": obj.company_id,
                    "_id": {"$ne": obj.id}
                })
            else:
                # If use_company_id is False or company_id doesn't exist on the model, just check uniqueness by field
                dup_filters.append({
                    field: val.strip(),
                    "_id": {"$ne": obj.id}
                })

        if dup_filters:
            existing = await self.model.find_one({"$or": dup_filters}, session=session)
            if existing:
                raise AlreadyExistsError(
                    f"{self.model.__name__} with these values already exists"
                )

        # Update the object with the new data
        for field, val in data.items():
            setattr(obj, field, val)
        await obj.replace(session=session)
        return obj


    async def update_flags(
        self,
        doc_id: Union[PydanticObjectId, str],
        company_id: Union[PydanticObjectId, str] = None,
        fields: List[Tuple[str, bool]] = None,
        session=None,
        use_company_id: bool = True  # Flag to conditionally apply company_id
    ) -> ModelType:
        obj = await self.get_by_id(doc_id, company_id, include_deleted=True, session=session, use_company_id=use_company_id)

        if not fields:
            raise ValidationError("No fields provided")

        for field, value in fields:
            if not hasattr(obj, field):
                raise ValidationError(f"Invalid field '{field}'")
            if not isinstance(value, bool):
                raise ValidationError("Flag values must be boolean")
            setattr(obj, field, value)

        await obj.save(session=session)
        return obj

    async def delete(
        self,
        doc_id: Union[PydanticObjectId, str],
        company_id: Union[PydanticObjectId, str] = None,
        hard_delete: bool = False,
        session=None,
        use_company_id: bool = True  # Flag to conditionally apply company_id
    ) -> None:
        obj = await self.get_by_id(doc_id, company_id, include_deleted=True, session=session, use_company_id=use_company_id)
        
        if hard_delete:
            await obj.delete(session=session)
        else:
            obj.is_deleted = True
            await obj.save(session=session)



# class CRUD(Generic[ModelType]):
#     def __init__(self, model: Type[ModelType]):
#         self.model = model

#     async def create(
#         self,
#         payload: Union[BaseModel, Dict[str, Any]],
#         unique_fields: Optional[List[str]] = None,
#         session= None
#     ) -> ModelType:
#         """
#         Create a new document, validating and enforcing uniqueness on specified fields.
#         :param payload: A Pydantic model with the data to insert.
#         :param unique_fields: List of document field names to check for uniqueness.
#         :returns: The inserted document instance.
#         """

#         # Process payload
#         if isinstance(payload, BaseModel):
#             data = payload.model_dump()
#         elif isinstance(payload, Mapping):
#             data = dict(payload)  # in case it's not a native dict
#         else:
#             raise ValidationError("Payload must be a Pydantic model or a dictionary")
        
#         checks = unique_fields or []

#         # 1) Validate non-empty for each unique field
#         filters = []
#         for field in checks:
#             val = data.get(field, "")
#             if not isinstance(val, str) or not val.strip():
#                 raise ValidationError(f"'{field}' must not be empty")
#             filters.append({field: val.strip()})

#         # 2) Check for duplicates
#         if filters:
#             existing = await self.model.find_one({"$or": filters}, session=session)
#             if existing:
#                 for field in checks:
#                     if getattr(existing, field) == data[field].strip():
#                         raise AlreadyExistsError(
#                             f"{self.model.__name__} '{field}' = {data[field]!r} already exists"
#                         )

#         # 3) Instantiate & insert
#         instance = self.model(**data)
#         await instance.insert(session=session)
#         return instance

#     async def get_by_id(
#         self,
#         doc_id: Union[PydanticObjectId, str],
#         company_id: Union[PydanticObjectId, str],
#         include_deleted: bool = False,        
#         include_deactivated: bool = False,
#         session=None
#     ) -> ModelType:
#         try:
#             doc_oid = PydanticObjectId(doc_id)
#             company_oid = PydanticObjectId(company_id)
#         except Exception as e:
#             raise ValidationError("Invalid document identifier") from e

#         query = {
#             "_id": doc_oid,
#             "company_id": company_oid
#         }
        
#         if not include_deleted:
#             query["is_deleted"] = False
        
#         if not include_deactivated:
#             query["is_active"] = True

#         obj = await self.model.find_one(query, session=session)
             
#         if not obj:
#             # Generic error to avoid information leakage
#             raise NotFoundError("Document not found or inaccessible")
            
#         return obj

#     async def list(
#         self,
#         company_id: Union[PydanticObjectId, str],
#         skip: int = 0,
#         limit: int = 50,
#         include_deleted: bool = False,
#         include_deactivated: bool = False,
#         filters: Optional[Dict[str, Any]] = None,
#         search: Optional[Dict[str, str]] = None,
#         exact_match: bool = False,
#         sort: Optional[List[Tuple[str, SortOrder]]] = None
#     ) -> List[ModelType]:
#         """
#         Tenant-isolated document listing with strict permission checks.
#         """
#         try:
#             company_oid = PydanticObjectId(company_id)
#         except Exception as e:
#             raise ValidationError("Invalid company identifier") from e

#         # Base query - MUST include company_id
#         query_filter: Dict[str, Any] = {"company_id": company_oid}
        
#         if not include_deleted:
#             query_filter["is_deleted"] = False
        
#         if not include_deactivated:
#             query_filter["is_active"] = True

#         # Merge additional filters
#         if filters:
#             for field, value in filters.items():
#                 if value is None:
#                     continue
#                 query_filter[field] = (
#                     {"$regex": f"^{value}$", "$options": "i"} 
#                     if isinstance(value, str) 
#                     else value
#                 )

#         # Search criteria
#         if search:
#             for field, term in search.items():
#                 if term is None:
#                     continue
#                 query_filter[field] = (
#                     {"$regex": f"^{term}$", "$options": "i"} 
#                     if exact_match 
#                     else {"$regex": term, "$options": "i"}
#                 )
#         # Sorting
#         sort_params = [
#             (field, order.value) 
#             for field, order in (sort or [("_id", SortOrder.ASC)])
#         ]

#         return await self.model.find(
#             query_filter
#         ).sort(sort_params).skip(skip).limit(limit).to_list()

#     async def update(
#         self,
#         doc_id: Union[PydanticObjectId, str],
#         company_id: Union[PydanticObjectId, str],
#         payload: BaseModel,
#         unique_fields: Optional[List[str]] = None,
#         session=None
#     ) -> ModelType:
#         """
#         Tenant-isolated update with uniqueness checks.
#         """
#         obj = await self.get_by_id(doc_id, company_id, session=session)

#         if isinstance(payload, BaseModel):
#             data = payload.model_dump(exclude_unset=True)
#         elif isinstance(payload, Mapping):
#             data = dict(payload)  # in case it's not a native dict
#         else:
#             raise ValidationError("Payload must be a Pydantic model or a dictionary")

#         checks = [f for f in (unique_fields or []) if f in data]

#         # Duplicate check scoped to company
#         dup_filters = []
#         for field in checks:
#             val = data[field]
#             if not isinstance(val, str) or not val.strip():
#                 raise ValidationError(f"'{field}' must not be empty")
#             dup_filters.append({
#                 field: val.strip(),
#                 "company_id": obj.company_id,
#                 "_id": {"$ne": obj.id}
#             })

#         if dup_filters:
#             existing = await self.model.find_one({"$or": dup_filters}, session=session)
#             if existing:
#                 raise AlreadyExistsError(
#                     f"{self.model.__name__} with these values already exists"
#                 )

#         for field, val in data.items():
#             setattr(obj, field, val)
#         await obj.replace(session=session)
#         return obj

#     async def update_flags(
#         self,
#         doc_id: Union[PydanticObjectId, str],
#         company_id: Union[PydanticObjectId, str],
#         fields: List[Tuple[str, bool]] = None,
#         session=None
#     ) -> ModelType:
#         """
#         Tenant-isolated flag updates.
#         """
#         obj = await self.get_by_id(doc_id, company_id, include_deleted=True, session=session)

#         if not fields:
#             raise ValidationError("No fields provided")

#         for field, value in fields:
#             if not hasattr(obj, field):
#                 raise ValidationError(f"Invalid field '{field}'")
#             if not isinstance(value, bool):
#                 raise ValidationError("Flag values must be boolean")
#             setattr(obj, field, value)

#         await obj.save(session=session)
#         return obj

#     async def delete(
#         self,
#         doc_id: Union[PydanticObjectId, str],
#         company_id: Union[PydanticObjectId, str],
#         hard_delete: bool = False,
#         session=None
#     ) -> None:
#         """
#         Tenant-isolated deletion.
#         """
#         obj = await self.get_by_id(doc_id, company_id, include_deleted=True)
        
#         if hard_delete:
#             await obj.delete(session=session)
#         else:
#             obj.is_deleted = True
#             await obj.save(session=session)