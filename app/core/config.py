import os
import pathlib
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = 'JvLQCqXNVU7r_mlIWDVuV91gmDyYwQ2QEEDGHH9d3r4'
    ALGORITHM: str = "HS256"

    # 60 minutes * 24 hours * 1 day = 1 day
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    # The audience of a token is the intended recipient of the token
    TOKEN_AUDIENCE: str = "http://localhost:3000"
    # Identifies the issuer, or "authorization server" that constructs and
    # returns the token
    TOKEN_ISSUER: str = "http://localhost:8001"
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8001",
        "http://localhost:8002",
        "http://10.0.0.30:8003",
        "http://10.0.5.38:3000",
        "http://10.0.5.38:8007",
        "http://10.0.0.68:8004",
        "http://10.0.5.54:8003",
        "http://10.0.5.54:3000",
        "http://10.0.5.48:3000",
        "http://10.0.0.30:3000",
        "http://10.0.0.68:8007",
        "http://10.0.0.68:8005",
    ]
    # Origins that match this regex OR are in the above list are allowed
    BACKEND_CORS_ORIGIN_REGEX: Optional[
        str
    ] = "http.*\.(10.0.0.68:8007|10.0.5.38:8007|10.0.0.68:8005|10.0.0.30:3000|10.0.5.48:3000|10.0.5.54:3000|localhost:3000|10.0.0.68:8004|localhost:8001|localhost:8002|10.0.5.38:3000|10.0.0.30:8003|10.0.5.54:8003)"  # noqa: W605

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str = "DAB User Management"

    MSSQL_DRIVER = "ODBC Driver 17 for SQL Server"
    MSSQL_DRIVER_PRODUCTION = "sql-server-data-source"

    MSSQL_TEST_SERVER = "10.0.0.30"
    MSSQL_TEST_DATABASE = "CWEBUSERM"
    MSSQL_TEST_USER = "sa"
    MSSQL_TEST_PASS = "Pass@786"
    
    MSSQL_LIVE_SERVER = ""
    MSSQL_LIVE_DATABASE = ""
    MSSQL_LIVE_USER = ""
    MSSQL_LIVE_PASS = ""


    FIRST_SUPERUSER: EmailStr = "abas.rafiq@dab.gov.af"
    FIRST_SUPERUSER_PW: str = "thisistest"
    USER_CHANGED_PASSWORD_DATE: str = "2022/07/20 04:00:00"
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True


settings = Settings()
