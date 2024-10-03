from typing import Any, Dict, List, Optional, Union

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models import Role
from app.models.role_permission import RolePermission
from app.models.user import User
from app.models.user_password_history import UserPasswordHistory
from app.models.user_role import UserRole
from app.schemas.user import UserCreate, UserOutput, UserOutputPaginated, UserUpdate
from fastapi.encoders import jsonable_encoder
from sqlalchemy import asc, delete, desc, exc, or_
from sqlalchemy.orm import Session, joinedload


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_single_user(self, db: Session, *, user_id: int) -> UserOutput:
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_user_roles(self, db: Session, *, user_id: int) -> Optional[List[UserRole]]:
        user_rule = db.query(UserRole).filter(UserRole.user_id == user_id).all()
        return user_rule

    def get_user_permissions_based_on_roles(self, db: Session, *, role_id: int) -> Any:
        permissions = (
            db.query(RolePermission).filter(RolePermission.role_id == role_id).all()
        )
        return permissions

    def get_previous_passwords_of_current_user(self, db: Session, user_id: int) -> Any:
        passwords = (
            db.query(UserPasswordHistory)
            .filter(UserPasswordHistory.user_id == user_id)
            .all()
        )
        return passwords

    def get_multi_paginated(
        self,
        db: Session,
        *,
        page: int,
        limit: int,
        search: str,
        field_name: str,
        order_by: str,
        role_id: int,
        user_id: int,
    ) -> UserOutputPaginated:

        # Retrieve all the data for the User model and store it in a data variable
        data = db.query(User).filter(User.id != user_id)

        if role_id != 0 and role_id > 0:
            data = data.join(UserRole).filter(UserRole.role_id == role_id)

        # Check if the search filed is not empty or None
        # Convert the filed to SQL search query field that can be used in LIKE clause
        if search:
            search = "%{}%".format(search)
            data = data.where(
                or_(
                    User.first_name.like(search),
                    User.last_name.like(search),
                    User.email.like(search),
                    User.employee_id.like(search),
                )
            )

        # Convert the string for order_by to lowercase
        if order_by and field_name:
            # Check for conditions if the order_by is 'DESC' or 'ASC', the default is ASC
            if order_by.lower() == "desc":
                data = data.order_by(desc(field_name))
            elif order_by.lower() == "asc":
                data = data.order_by(asc(field_name))
        else:
            data = data.order_by(User.id.asc())

        # Get all the regards filtered and store is in the data variable
        data = data
        users = super().get_multi_paginated(
            db,
            page=page,
            limit=limit,
            data=data,
            endpoint='users'
        )
        return users

    def get_multi(
        self, db: Session, *, skip: int = 1, limit: int = 100
    ) -> List[UserOutput]:
        return db.query(User).options(joinedload(User.roles)).all()

    def create(self, db: Session, *, obj_in: UserCreate) -> bool:
        # 1: Insert the User record to the Database
        db_obj = User(
            employee_id=obj_in.employee_id,
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            is_superuser=obj_in.is_superuser,
            contactPhone=obj_in.contactPhone,
            expiryDate=obj_in.expiryDate,
            needsToChangePassword=obj_in.needsToChangePassword,
        )
        db.add(db_obj)
        db.flush()

        # 4. If the roles filed is set then remove the roles from the user_role table
        if "role_id" in obj_in:
            if 0 in obj_in.role_id:
                print("Zero Exists")
            else:
                roles = obj_in.role_id
                # roles = db.query(UserRole).get(db_obj.id)
                # for role in roles:
                stmt = delete(UserRole).where(UserRole.user_id == db_obj.id)
                db.execute(stmt)

                # Store the User ID in a variable
                user_id: int = db_obj.id

                # Loop trough the roles IDs returned in the request and store them one by one respected to the user_id
                for role in roles:
                    user_role_obj = UserRole(user_id=user_id, role_id=role)
                    # 4. Store the result in the DB
                    db.add(user_role_obj)
        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False

    # User Update
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> bool:
        obj_data = jsonable_encoder(db_obj)
        # 1. Check the inserted is of type dictionary and assign it ot the update_date variable
        if isinstance(obj_in, dict):
            update_data = obj_in
        # 2. If the object is not dictionary, convert it to dictionary and store it in update_data variable
        else:
            update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.flush()

        # 4. If the roles filed is set then remove the roles from the user_role table
        if "role_id" in update_data:
            if 0 in update_data["role_id"]:
                print("Zero Exists")
            else:
                roles = []
                for r in update_data["role_id"]:
                    roles.append(r["id"])
                # roles = db.query(UserRole).get(db_obj.id)
                # for role in roles:
                stmt = delete(UserRole).where(UserRole.user_id == db_obj.id)
                db.execute(stmt)
                db.commit()

                # Store the User ID in a variable
                user_id: int = db_obj.id

                # Loop trough the roles IDs returned in the request and store them one by one respected to the user_id
                for role in roles:
                    user_role_obj = UserRole(user_id=user_id, role_id=role)
                    # 4. Store the result in the DB
                    db.add(user_role_obj)

        try:
            db.commit()
            return True
        except exc.SQLAlchemyError:
            db.rollback()
            return False

    def delete(self, db: Session, *, id: int) -> User:
        # 1. Get the user by the id in request
        user = db.query(User).get(id)
        # 2. Remove the user as per the user id in request
        db.delete(user)
        db.commit()
        # 3. Remove the user roles respected to the user id
        delete_user_roles = delete(UserRole).where(UserRole.user_id == user.id)
        db.execute(delete_user_roles)
        db.commit()
        return

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def needs_to_change_password(self, user: User) -> bool:
        return user.needsToChangePassword

    def is_superuser(self, user: User) -> bool:
        return user.is_superuser


user = CRUDUser(User)
