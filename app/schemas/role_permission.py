from pydantic import BaseModel


class RolePermissionBase(BaseModel):
    role_id: int
    permission_id: int

    class Config:
        orm_mode = True


class RolePermission(RolePermissionBase):
    ...
