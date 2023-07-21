from typing import Optional

from pydantic import BaseModel, Field


class PermissionBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    group_id: Optional[int] = None


# Properties to receive via API on Creation
class PermissionCreate(PermissionBase):
    name: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


# Properties to receive via API on Update
class PermissionUpdate(PermissionBase):
    description: Optional[str] = None


class PermissionOutput(PermissionBase):
    pass


class PermissionInDBBase(PermissionBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class Permission(PermissionInDBBase):
    ...
