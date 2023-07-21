from pydantic import BaseModel


class RoleGroupMap(BaseModel):
    role_group_id: int
    role_id: int

    class Config:
        orm_mode = True
