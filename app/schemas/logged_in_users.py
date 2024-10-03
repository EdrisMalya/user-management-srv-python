from pydantic import BaseModel, Field
from typing import List, Optional


class LoggedInUsersSchema(BaseModel):
    use_id: Optional[int] = None


class LoggedInUserCreate(BaseModel):
    use_id: int = Field(...)
    refresh_token: str = Field(...)


class LoggedInUserUpdate(BaseModel):
    use_id: int = Field(...)
    refresh_token: str = Field(...)
