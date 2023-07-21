from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    login,
    permission,
    permission_group,
    role_group,
    roles,
    users,
    utils,
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(utils.router, prefix="/utils", tags=["Utils"])
api_router.include_router(roles.router, prefix="/roles", tags=["Roles"])
api_router.include_router(role_group.router, prefix="/role_group", tags=["Role Group"])
api_router.include_router(
    permission.router, prefix="/permissions", tags=["Permissions"]
)
api_router.include_router(
    permission_group.router, prefix="/permission_group", tags=["Permission Group"]
)
