# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.role import Role  # noqa
from app.models.permission import Permission
from app.models.permission_group import PermissionGroup
from app.models.user_password_history import UserPasswordHistory
from app.models.role_group import RoleGroup  # noqa
from app.models.user import User  # noqa
from app.models.user_role import UserRole  # noqa
