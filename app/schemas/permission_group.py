from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PermissionGroupBase(BaseModel):
    name: Optional[str] = None
    permission_group_id: Optional[int] = None


class PermissionGroupCreate(PermissionGroupBase):
    name: str = Field(..., min_length=1)


class PermissionGroupUpdate(PermissionGroupBase):
    name: str = Field(..., min_length=1)
    permission_group_id: Dict[str, Any] = Field(None)


class PermissionGroupInDBBase(PermissionGroupBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class PermissionGroup(PermissionGroupInDBBase):
    ...


class PermissionGroupOutput(PermissionGroupInDBBase):
    name: Optional[str] = None


class PermissionGroupSchema(PermissionGroupInDBBase):
    pass
