from typing import Optional

from pydantic import BaseModel


class UserPasswordHistoryBase(BaseModel):
    user_id: Optional[int] = None
    password: Optional[str] = None


class UserPasswordHistoryCreate(UserPasswordHistoryBase):
    user_id: int
    password: str


class UserPasswordHistoryUpdate(UserPasswordHistoryBase):
    pass


class UserPasswordHistoryInDBBase(UserPasswordHistoryBase):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class UserPasswordHistory(UserPasswordHistoryInDBBase):
    ...
