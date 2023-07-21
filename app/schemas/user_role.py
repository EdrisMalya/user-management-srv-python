from typing import Optional

from pydantic import BaseModel


class UserRoleBase(BaseModel):
    user_id: Optional[int] = None
    role_id: Optional[int] = None


class UserRoleInDBBase(UserRoleBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class UserRole(UserRoleInDBBase):
    ...
