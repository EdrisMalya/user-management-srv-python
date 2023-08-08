import os
import pathlib
import secrets
from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, validator
from dotenv import load_dotenv

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent
load_dotenv()

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    SECRET_KEY: str = os.getenv('SECRET_KEY')
    ALGORITHM: str = "HS256"

    # 60 minutes * 24 hours * 1 day = 1 day
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * int(os.getenv('ACCESS_TOKEN_EXPIRE_DAYS'))
    # The audience of a token is the intended recipient of the token
    TOKEN_AUDIENCE: str = os.getenv('TOKEN_AUDIENCE')
    # Identifies the issuer, or "authorization server" that constructs and
    # returns the token
    TOKEN_ISSUER: str = os.getenv('TOKEN_ISSUER')
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [os.getenv('PROTOCOL')+"://"+ip for ip in os.getenv('ALLOWED_IPS').split(',')]    # Origins that match this regex OR are in the above list are allowed
    BACKEND_CORS_ORIGIN_REGEX: Optional[
        str
    ] = f"{os.getenv('PROTOCOL')}.*\.({os.getenv('ALLOWED_IPS').replace(',', '|')})"

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
    MSSQL_SERVER = os.getenv('DB_HOST')
    MSSQL_DATABASE = os.getenv('DB_DATABASE')
    MSSQL_USER = os.getenv('DB_USER')
    MSSQL_PASS = os.getenv('DB_PASSWORD')

    FIRST_SUPERUSER: EmailStr = "mnaim.faizy@gmail.com"
    FIRST_SUPERUSER_PW: str = "password"
    USER_CHANGED_PASSWORD_DATE: str = "2022/07/20 04:00:00"
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True


settings = Settings()
