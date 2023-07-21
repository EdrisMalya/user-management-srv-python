from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from app.db.base_class import Base
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi_paginated(
        self, db: Session, *, page: int, limit: int, data: Any, endpoint: str,
    ) -> Any:
        if page == 1:
            offset = 0
        else:
            offset = (page - 1) * limit
        end = offset + limit

        # Count the result in store it in a data_length variable
        data_length = data.count()  # > 1
        data = data.offset(offset).limit(limit).all()
        """
                {
            "data": [...],
            "pagination": {
                "next": "link to the next page",
                "previous": "link to the previous page",
            },
            "count": "total number of items",
            "total": "total number of items"
        }
        """

        response = {
            "data": data,
            "total": data_length,
            "count": limit,
            "pagination": {},
        }

        if end >= data_length:
            response["pagination"]["next"] = None

            if page > 1:
                response["pagination"][
                    "previous"
                ] = f"/api/v1/{endpoint}/?page={page-1}&limit={limit}"
            else:
                response["pagination"]["previous"] = None
        else:
            if page > 1:
                response["pagination"][
                    "previous"
                ] = f"/api/v1/{endpoint}/?page={page-1}&limit={limit}"
            else:
                response["pagination"]["previous"] = None

            response["pagination"][
                "next"
            ] = f"/api/v1/{endpoint}/?page={page+1}&limit={limit}"

        return response

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        require_join: bool = False,
    ) -> List[ModelType]:
        return (
            db.query(self.model)
            .order_by(self.model.id)
            .offset(skip)
            .limit(limit)
            .from_self()
            .all()
        )

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return
