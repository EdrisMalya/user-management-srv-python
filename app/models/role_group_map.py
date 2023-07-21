from sqlalchemy import Column, ForeignKey, Integer

from app.db.base_class import Base


class RoleGroupMap(Base):
    __tablename__ = "role_group_map"
    role_group_id = Column(
        Integer,
        ForeignKey("role_group.id", ondelete="NO ACTION", use_alter=True),
        primary_key=True,
        index=True,
    )
    role_id = Column(
        Integer,
        ForeignKey("role.id", ondelete="NO ACTION", use_alter=True),
        primary_key=True,
        index=True,
    )
