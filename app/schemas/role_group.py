from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.role import RoleOutput


class RoleGroupBase(BaseModel):
    name: Optional[str] = None


class RoleGroupCreate(RoleGroupBase):
    name: str = Field(..., min_length=1)


class RoleGroupUpdate(RoleGroupBase):
    name: str = Field(..., min_length=1)


class RoleGroupInDBBase(RoleGroupBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class RoleGroup(RoleGroupInDBBase):
    ...


class RoleGroupOutput(RoleGroupInDBBase):
    name: Optional[str] = None
    roles: Optional[List[RoleOutput]] = None


class RoleGroupSchema(RoleGroupInDBBase):
    roles: Optional[List[RoleOutput]] = None
