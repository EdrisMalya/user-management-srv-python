from typing import Optional

from sqlalchemy import delete, exc
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import PermissionGroup
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.schemas.permission import PermissionCreate, PermissionUpdate


class CRUDPermission(CRUDBase[Permission, PermissionCreate, PermissionUpdate]):

    # Return single permission respected to it's name
    def get_by_permission_name(self, db: Session, *, name: str) -> Optional[Permission]:
        return db.query(Permission).filter(Permission.name == name).first()

    # Create new permission base on the send request
    def create(self, db: Session, *, obj_in: PermissionCreate, user_id: int) -> bool:
        db_obj = Permission(
            name=obj_in.name,
            description=obj_in.description,
            group_id=obj_in.group_id,
            insertedBy=user_id,
        )
        db.add(db_obj)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            return False

    def assign_permissions_to_role(
        self, db: Session, *, role_id: int, permission: list[int]
    ) -> bool:
        for p in permission:
            db_obj = RolePermission(role_id=role_id, permission_id=p)
            db.add(db_obj)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False

    def get_assigned_permissions(self, db: Session, *, role_id: int):
        roles = db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
        all_permissions = []
        for r in roles:
            all_permissions.append(
                db.query(Permission).filter(Permission.id == r.permission_id).first()
            )
        assigned_permissions = []
        for p in all_permissions:
            assigned_permissions.append(p.id)
        return assigned_permissions

    def delete_permissions_base_on_role_id(self, db: Session, *, role_id: int) -> bool:
        result = (
            db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
        )
        if len(result) > 0:
            delete_role_permissions = delete(RolePermission).where(
                RolePermission.role_id == role_id
            )
            db.execute(delete_role_permissions)
            try:
                db.commit()
                return True
            except exc.SQLAlchemyError:
                db.rollback()
                return False
        else:
            return False

    def get_group_by_id(self, db: Session, *, group_id: int):
        return (
            db.query(PermissionGroup)
            .filter(PermissionGroup.id == group_id)
            .first()
        )


permission = CRUDPermission(Permission)
