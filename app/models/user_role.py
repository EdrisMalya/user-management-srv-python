from sqlalchemy import Column, ForeignKey, Integer

from app.db.base_class import Base


class UserRole(Base):
    __tablename__ = "user_role"
    user_id = Column(
        Integer,
        ForeignKey("user.id", ondelete="NO ACTION", use_alter=True),
        primary_key=True,
        index=True,
    )
    role_id = Column(
        Integer,
        ForeignKey("role.id", ondelete="NO ACTION", use_alter=True),
        primary_key=True,
        index=True,
    )
