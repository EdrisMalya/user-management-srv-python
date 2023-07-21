from pydantic import BaseModel


class Msg(BaseModel):
    status: bool
    message: str
