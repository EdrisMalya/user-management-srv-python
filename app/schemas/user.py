from typing import Any, Dict, List, Optional

from app.schemas.role import Role
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    employee_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    subscriberId: Optional[int] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    needsToChangePassword: Optional[bool] = True
    expiryDate: Optional[str] = None
    contactPhone: Optional[str] = None
    lastChangedPasswordDate: Optional[str] = None
    numberOfFailedAttempts: Optional[int] = None
    positionId: Optional[int] = None
    roles: Optional[List[Role]]


# Properties to receive via API on creation
class UserCreate(UserBase):
    employee_id: int = None
    role_id: Optional[List[int]] = None
    password: Optional[str] = None
    lastChangedPasswordDate: Optional[str] = None


# Properties to receive via API on update
class UserUpdate(UserBase):
    role_id: Optional[List[Dict]] = None
    password: Optional[str] = None
    lastChangedPasswordDate: Optional[str] = None


class UserInDBBase(UserBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class User(UserInDBBase):
    ...


class UserOutput(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: Optional[bool] = None
    is_active: Optional[bool] = None
    expiryDate: Optional[str] = None
    roles: Optional[List[Role]] = None

    class Config:
        smart_union: True


class UserOutputPaginated(BaseModel):
    data: Optional[List[User]] = None
    total: Optional[int] = None
    count: Optional[int] = None
    pagination: Dict[str, Any] = None


class UserOutputPaginatedSchema(BaseModel):
    data: Optional[UserOutputPaginated]
    status: Optional[str]
    message: Optional[str]


# this class contain all information for the token
class UserLoginSchema(BaseModel):
    id: Optional[int] = None
    employee_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False
    is_superuser: Optional[bool] = False
    needsToChangePassword: Optional[bool] = False
    expiryDate: Optional[str] = None
    contactPhone: Optional[str] = None
    numberOfFailedAttempts: Optional[int] = None
    roles: Optional[List[int]] = None
    permissions: Optional[List[str]] = None


class UserSchema(UserInDBBase):
    roles: Optional[List[Role]] = None


class UserPasswordReset(BaseModel):
    is_active: Optional[bool] = None
    needsToChangePassword: Optional[bool] = None
    expiryDate: Optional[str] = None
