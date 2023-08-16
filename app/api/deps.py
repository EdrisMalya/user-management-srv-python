from typing import Any, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            audience=settings.TOKEN_AUDIENCE,
            issuer=settings.TOKEN_ISSUER,
            options={"verify_aud": True, "require_aud": False},
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"status": False, "message": "Could not validate credentials"},
        )
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=404, detail={"status": False, "message": "User not found"}
        )
    return user


def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You do not  have enough privileges",
        )
    return current_user


def get_current_active_user_permissions(
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> list:
    # Get the Roles based on User ID
    roles = crud.user.get_user_roles(db=db, user_id=current_user.id)
    if roles:
        role_arr = []
        for r in roles:
            role_arr.append(r.role_id)

        # Second retrive all the permissions for the user in the assigned roles
        get_permissions_by_role_id = []
        get_permissions_by_permission_id = []
        for r in roles:
            get_permissions_by_role_id.append(
                crud.user.get_user_permissions_based_on_roles(db=db, role_id=r.role_id)
            )
        # Loop through the permissions retrived respected to role_id from role_permission table
        # Store the result in a variable
        for permission in get_permissions_by_role_id:
            for p in permission:
                get_permissions_by_permission_id.append(
                    crud.permission.get(db=db, id=p.permission_id)
                )
        # This iteration is for getting the permissions name from permission table respected to the permission ID
        permissions = []
        for x in get_permissions_by_permission_id:
            permissions.append(x.name)

    return permissions
