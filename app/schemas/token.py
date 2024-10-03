from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[int] = None
    iat: Optional[int] = None
    iss: Optional[str] = None
    aud: Optional[str] = None


class RefreshTokenPayload(BaseModel):
    sub: Optional[int] = None
    exp: Optional[int] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
