from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.permission import Permission


class RoleBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    role_group_id: Optional[int] = None


# Properties to receive via API on Creation
class RoleCreate(RoleBase):
    name: str = Field(..., min_length=1)
    description: Optional[str] = Field(None)
    role_group_id: int = Field(...)


# Properties to receive via API on Update
class RoleUpdate(RoleBase):
    description: Optional[str] = None


# Output paginated data
class RoleOutput(BaseModel):
    pass


class RoleInDBBase(RoleBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class Role(RoleInDBBase):
    ...


class ShortRole(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None


class RoleOutput(RoleInDBBase):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[Permission]] = None


class RoleSchema(RoleInDBBase):
    pass
    # permissions: Optional[List[Permission]] = None
