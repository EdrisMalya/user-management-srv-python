import logging
from typing import Any, Dict, List, Optional, Union

from app.crud.base import CRUDBase
from app.models.role import Role
from app.models.role_group_map import RoleGroupMap
from app.models.role_permission import RolePermission
from app.schemas.role import RoleCreate, RoleOutput, RoleUpdate, ShortRole
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload


class CRUDRole(CRUDBase[Role, RoleCreate, RoleUpdate]):

    # Return single role respected to it's name
    def get_by_role_name(self, db: Session, *, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    def get_short(self, db: Session) -> Optional[ShortRole]:
        return db.query(Role.id, Role.name).all()

    def get_multi(
        self, db: Session, *, skip: int = 1, limit: int = 100
    ) -> List[RoleOutput]:
        return db.query(Role).options(joinedload(Role.permissions)).all()

    # Create role based on the request
    def create(self, db: Session, *, obj_in: RoleCreate, user_id: int) -> Role:
        db_obj = Role(
            name=obj_in.name,
            description=obj_in.description,
            insertedBy=user_id,
        )
        db.add(db_obj)
        db.flush()
        role_id = db_obj.id
        role_group_map_in = RoleGroupMap(
            role_id=role_id, role_group_id=obj_in.role_group_id
        )
        db.add(role_group_map_in)
        try:
            db.commit()
            return db_obj
        except SQLAlchemyError as ex:
            exc_json = ex.__dict__
            logging.error(exc_json)
            # logging.error(exc_json["orig"])
            # TODO: Send the log message with the severity code to the log service
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "status": False,
                    "message": "Internal Server Error, please contact your administrator for this issue",
                },
            )

    # Update Role base on the request
    def update(
        self,
        db: Session,
        *,
        db_obj: RoleUpdate,
        obj_in: Union[RoleUpdate, Dict[str, Any]]
    ) -> Role:
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
        print(update_data)

        if update_data["permissions"]:
            permissions = update_data["permissions"]
            # First we will delete all the permissions in the role_permission table
            # respected to the role ID
            delete_permissions = delete(RolePermission).where(
                RolePermission.role_id == db_obj.id
            )
            db.execute(delete_permissions)
            db.commit()

            role_id: int = db_obj.id

            # Loop through the permissions IDs returned in the request and store
            # them in RolePermission table with the respected role ID
            for permission in permissions:
                role_permission_obj = RolePermission(
                    role_id=role_id, permission_id=permission
                )
                db.add(role_permission_obj)
                db.commit()
        return db_obj

    # Check if role has permissions assigned to it
    def check_if_role_has_permissions(self, db: Session, *, id: int) -> bool:
        permissions = (
            db.query(RolePermission).filter(RolePermission.role_id == id).all()
        )
        if len(permissions) > 0:
            return True
        else:
            return False

    def delete(self, db: Session, *, id: int) -> bool:
        # 1. Get the role by the id in request
        role = db.query(Role).get(id)
        # 2. Remove the role as per the user id in request
        db.delete(role)
        try:
            db.commit()
            # 3. Remove the role from role_group_map table
            delete_role_group_map = delete(RoleGroupMap).where(
                RoleGroupMap.role_id == role.id
            )
            db.execute(delete_role_group_map)
            db.commit()
            return True
        except SQLAlchemyError:
            return False


role = CRUDRole(Role)
