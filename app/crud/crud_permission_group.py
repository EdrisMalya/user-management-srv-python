from typing import Any, Dict, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import exc, literal, null, and_
from sqlalchemy.orm import Session, defer, raiseload

from app.crud.base import CRUDBase
from app.models.permission import Permission
from app.models.permission_group import PermissionGroup
from app.schemas.permission_group import PermissionGroupCreate, PermissionGroupUpdate


class CRUDPermissionGroup(
    CRUDBase[
        PermissionGroup,
        PermissionGroupCreate,
        PermissionGroupUpdate,
    ]
):
    def get(self, db: Session, *, id: int) -> Any:
        group = db.query(PermissionGroup, literal(0).label("parent_group"))
        group = group.options(
            defer(PermissionGroup.insertedBy),
            defer(PermissionGroup.insertedDate),
            raiseload(PermissionGroup.permissions),
            raiseload(PermissionGroup.groups),
        )
        group = group.filter(PermissionGroup.id == id).first()
        group = group[0].__dict__
        group["parent_group"] = (
            db.query(PermissionGroup)
            .options(
                raiseload(PermissionGroup.permissions),
                raiseload(PermissionGroup.groups),
            )
            .get(group["permission_group_id"])
        )
        data = {
            "group": group,
            "groups": db.query(PermissionGroup)
            .options(
                raiseload(PermissionGroup.permissions),
                raiseload(PermissionGroup.groups),
            )
            .filter(PermissionGroup.permission_group_id == null())
            .all(),
        }
        return data

    def get_single_record(self, db: Session, *, id: int) -> Any:
        return db.query(PermissionGroup).filter(PermissionGroup.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 1, limit: int = 100) -> Any:
        return (
            db.query(PermissionGroup)
            .filter(PermissionGroup.permission_group_id == null())
            .order_by(PermissionGroup.order)
            .all()
        )

    def get_group_by_id(self, db: Session, *, group_id: int):
        return (
            db.query(PermissionGroup)
            .filter(PermissionGroup.id == group_id)
            .first()
        )

    # Return single permissionGroup respected to it's name
    def get_by_permission_group_name(
            self, db: Session, *, name: str, permission_group_id: int
    ) -> Optional[PermissionGroup]:
        permission_group = (
            db.query(PermissionGroup)
            .filter(PermissionGroup.name == name, and_(PermissionGroup.permission_group_id == permission_group_id))
            .first()
        )
        return permission_group

    # Create permission_group based on the request
    def create(
            self, db: Session, *, obj_in: PermissionGroupCreate, user_id: int
    ) -> PermissionGroup:
        if obj_in.permission_group_id == 0:
            permission_groupId = None
            result = db.query(PermissionGroup).filter(PermissionGroup.permission_group_id == None).order_by(
                PermissionGroup.id.desc()).first()
            result = result.order + 1
        else:
            permission_groupId = obj_in.permission_group_id
            result = db.query(PermissionGroup).filter(
                PermissionGroup.permission_group_id == permission_groupId).order_by(
                PermissionGroup.id.desc()).first()
            if (result == None):
                result = 0
            else:
                result = result.order + 1
        db_obj = PermissionGroup(
            name=obj_in.name, permission_group_id=permission_groupId, insertedBy=user_id, order=result
        )
        db.add(db_obj)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False

    def update(
            self,
            db: Session,
            *,
            db_obj: PermissionGroupUpdate,
            obj_in: Union[PermissionGroupUpdate, Dict[str, Any]]
    ) -> PermissionGroup:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        update_data.pop('permission_group_id')
        update_data["name"] = update_data["name"]

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError as ex:
            print(ex)
            db.rollback()
            return False

    def check_permission_group_has_groups(self, db: Session, *, id: int) -> bool:
        result = db.query(PermissionGroup).filter(PermissionGroup.id == id).first()
        if len(result.__dict__["groups"]) > 0:
            return True
        else:
            return False

    def check_if_group_has_permissions(self, db: Session, *, id: int) -> bool:
        result = db.query(Permission).filter(Permission.group_id == id).all()
        if len(result) > 0:
            return True
        else:
            return False

    def delete(self, db: Session, *, id: int) -> PermissionGroup:
        # 1. Get the role by the id in request
        permissionGroup = db.query(PermissionGroup).get(id)
        # 2. Remove the user as per the user id in request
        db.delete(permissionGroup)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False


permission_group = CRUDPermissionGroup(PermissionGroup)
