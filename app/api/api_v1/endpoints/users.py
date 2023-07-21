from typing import Any, Dict, List

from app import crud, models, schemas
from app.api import deps
from app.core.producer import publisher
from app.core.security import get_password_hash
from app.schemas.msg import Msg
from app.schemas.user import UserOutputPaginated
from app.utils import generate_random_password
from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import ORJSONResponse
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

router = APIRouter()


@router.get(
    "/",
    response_model=UserOutputPaginated | Msg,
)
def read_users(
        db: Session = Depends(deps.get_db),
        page: int = 1,
        limit: int = 10,
        search: str = None,
        sort: str = None,
        direction: str = None,
        role_id: int = 0,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Retrieve users.
    """
    loggedInUser = current_user.__dict__
    if "user.view" in permissions or loggedInUser["is_superuser"] == True:
        users = crud.user.get_multi_paginated(
            db=db,
            page=page,
            limit=limit,
            search=search,
            field_name=sort,
            order_by=direction,
            role_id=role_id,
        )
        if len(users["data"]) <= 0:
            raise HTTPException(
                status_code=404, detail={"status": False, "message": "User not found"}
            )
        else:
            return users
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.post("/", response_model=schemas.User | Msg, response_class=ORJSONResponse)
async def create_user(
        *,
        db: Session = Depends(deps.get_db),
        first_name: str = Body(...),
        last_name: str = Body(None),
        email: EmailStr = Body(...),
        is_active: bool = Body(False),
        employee_id: int = Body(...),
        password: str = Body(False),
        expiryDate: str = Body(None),
        contactPhone: str = Body(None),
        useAdminLog: bool = Body(None),
        role_id: List[Dict] = Body(...),
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Create new user.
    """
    loggedInUser = current_user.__dict__
    if "user.add" in permissions or loggedInUser["is_superuser"] == True:
        # 1. Get the user and check if the email is already exists in the system.
        user = crud.user.get_by_email(db, email=email)
        if user and user != None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "field_name": "email",
                    "message": "The user with this email already exists in the system.",
                },
            )
        # 2. Generate a random password
        random_password = generate_random_password()
        roles = []
        for r in role_id:
            roles.append(r["value"])

        # 3. Create the UserCreate Schema
        user_in = schemas.UserCreate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            is_active=is_active,
            password=password,
            expiryDate=expiryDate,
            contactPhone=contactPhone,
            useAdminLog=useAdminLog,
            role_id=roles,
            employee_id=employee_id
        )

        # 4. Insert the user detail
        user = crud.user.create(db, obj_in=user_in)
        publisher.publish(
            queue_name="emails",
            exchange_name="emails",
            method="user_created",
            message={"email": email, "random_password": random_password},
            routing_key="emails",
        )
        raise HTTPException(
            status_code=status.HTTP_201_CREATED,
            detail={"status": True, "message": "User created successfully"},
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.put("/me", response_model=schemas.User)
def update_user_me(
        *,
        db: Session = Depends(deps.get_db),
        password: str = Body(None),
        first_name: str = Body(None),
        last_name: str = Body(None),
        email: EmailStr = Body(None),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if first_name is not None:
        user_in.first_name = first_name
    if last_name is not None:
        user_in.last_name = last_name
    if email is not None:
        user_in.email = email
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    raise HTTPException(
        status_code=status.HTTP_202_ACCEPTED,
        detail={"status": True, "message": "Content updated successfully"},
    )


@router.get("/me", response_model=schemas.User)
def read_user_me(
        db: Session = Depends(deps.get_db),
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User | Msg)
def read_user_by_id(
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
        db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    loggedInUser = current_user.__dict__
    if "user.view" in permissions or loggedInUser["is_superuser"] == True:
        user = crud.user.get_single_user(db, user_id=user_id)
        if user == current_user:
            return user
        if not crud.user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "status": False,
                    "message": "The user doesn't have enough privileges",
                },
            )
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.put("/{user_id}", response_model=schemas.User | Msg)
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int,
        user_in: schemas.UserUpdate,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Update a user.
    """
    loggedInUser = current_user.__dict__
    if "user.edit" in permissions or loggedInUser["is_superuser"] == True:
        db_user = crud.user.get(db, id=user_id)
        if user_in.password == '':
            user_in.password = db_user.password
        else:
            user_in.password = get_password_hash(user_in.password)
            user_in.needsToChangePassword = True
        user = crud.user.update(db, db_obj=db_user, obj_in=user_in)
        if user:
            raise HTTPException(
                status_code=status.HTTP_200_OK,
                detail={"status": True, "message": "User updated successfully"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )


@router.delete("/{user_id}", response_model=schemas.Role | Msg)
def delete_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: int,
        current_user: models.User = Depends(deps.get_current_active_user),
        permissions: list = Depends(deps.get_current_active_user_permissions),
) -> Any:
    """
    Delete a role
    """
    if "user.delete" in permissions:
        user = crud.user.get(db=db, id=user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        if not crud.user.is_superuser(current_user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Note enough permission"
            )
        user = crud.user.delete(db=db, id=user_id)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "You do not have enough privileges"},
        )
