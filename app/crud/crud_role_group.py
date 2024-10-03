from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, exc
from sqlalchemy.orm import Session, joinedload, with_loader_criteria

from app.crud.base import CRUDBase
from app.models import Role, UserRole, User
from app.models.role_group import RoleGroup
from app.models.role_group_map import RoleGroupMap
from app.schemas.role_group import RoleGroupCreate, RoleGroupUpdate


class CRUDRoleGroup(CRUDBase[RoleGroup, RoleGroupCreate, RoleGroupUpdate]):

    # GET single role_group respected to it's ID
    def get(self, db: Session, *, id: int) -> RoleGroup:
        return (
            db.query(RoleGroup)
            .filter(RoleGroup.id == id)
            .options(joinedload(RoleGroup.roles))
            .first()
        )

    def get_multi(self, db: Session, current_user: User) -> List[Any]:
        role_ids = [item.role_id for item in db.query(UserRole).filter(UserRole.user_id == current_user.id)]
        return db.query(RoleGroup).options(
            joinedload(RoleGroup.roles),
            with_loader_criteria(Role, Role.id.notin_(role_ids)),
        ).all()

    def get_multi_paginated(
        self, db: Session, *, page: int = 0, limit: int = 100
    ) -> List[RoleGroup]:
        data = db.query(RoleGroup).options(joinedload(RoleGroup.roles)).all()
        return super().get_multi_paginated(db, page=page, limit=limit, data=data)

    # Return single roleGroup respected to it's name
    def get_by_role_group_name(self, db: Session, *, name: str) -> Optional[RoleGroup]:
        return db.query(RoleGroup).filter(RoleGroup.name == name).first()

    # Check if RoleGroup has any roles assigned to it
    def check_role_group_has_any_roles(
        self, db: Session, *, role_group_id: int
    ) -> bool:
        role_group = (
            db.query(RoleGroupMap)
            .filter(RoleGroupMap.role_group_id == role_group_id)
            .all()
        )
        if len(role_group) > 0:
            return True
        else:
            return False

    # Create role_group based on the request
    def create(
        self, db: Session, *, obj_in: RoleGroupCreate, user_id: int
    ) -> Optional[RoleGroup]:
        # Check if the role_group already exists
        role_group_name = (
            db.query(RoleGroup).filter(RoleGroup.name == obj_in.name).first()
        )
        if role_group_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "field_name": "name",
                    "message": "Role Group name already exist",
                },
            )
        else:
            db_obj = RoleGroup(name=obj_in.name, insertedBy=user_id)
            db.add(db_obj)
            db.commit()
            return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: RoleGroupUpdate,
        obj_in: Union[RoleGroupUpdate, Dict[str, Any]]
    ) -> RoleGroup:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data and field != "roles":
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

        # if update_data["roles"] and len(update_data["roles"]) > 0 and 0 in update_data["roles"]:
        #     roles = update_data["roles"]
        #     has_role_group = (
        #         db.query(RoleGroupMap)
        #         .filter(RoleGroupMap.role_group_id == db_obj.id)
        #         .all()
        #     )
        #     # Retrive all the roles
        #     roles = []
        #     for role in db.query(Role).all():
        #         roles.append(role.id)

        #     if len(has_role_group) > 0:
        #         delete_roles_assigned_role_group = delete(RoleGroupMap).where(
        #             RoleGroupMap.role_group_id == db_obj.id
        #         )
        #         db.execute(delete_roles_assigned_role_group)
        #         db.commit()

        #         role_group_id: int = db_obj.id
        #         for role in roles:
        #             if roles.count(role) > 0:
        #                 role_group_obj = RoleGroupMap(
        #                     role_group_id=role_group_id, role_id=role
        #                 )
        #                 db.add(role_group_obj)
        #         db.commit()
        #     else:
        #         role_group_id: int = db_obj.id
        #         for role in roles:
        #             if roles.count(role) > 0:
        #                 role_group_obj = RoleGroupMap(
        #                     role_group_id=role_group_id, role_id=role
        #                 )
        #                 db.add(role_group_obj)
        #         db.commit()
        return db_obj

    def delete(self, db: Session, *, id: int) -> Optional[bool]:
        # 1. Get the role by the id in request
        role_group = db.query(RoleGroup).get(id)
        # 2. Remove the user as per the user id in request
        db.delete(role_group)
        # db.commit()
        # 3. Remove the role_group roles respected to the role_group id
        delete_role_group = delete(RoleGroupMap).where(
            RoleGroupMap.role_group_id == role_group.id
        )
        db.execute(delete_role_group)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="There is some error in your query",
            )


role_group = CRUDRoleGroup(RoleGroup)
