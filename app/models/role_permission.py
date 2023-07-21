from sqlalchemy import Column, ForeignKey, Integer

from app.db.base_class import Base


class RolePermission(Base):
    __tablename__ = "role_permission"
    role_id = Column(
        Integer,
        ForeignKey("role.id", ondelete="NO ACTION", use_alter=True),
        primary_key=True,
        index=True,
    )
    permission_id = Column(
        Integer,
        ForeignKey("permission.id", ondelete="NO ACTION", use_alter=True),
        primary_key=True,
        index=True,
    )
