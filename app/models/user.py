from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    pass


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, nullable=True, index=True)
    first_name = Column(String(250), nullable=True, index=True)
    last_name = Column(String(250), nullable=True, index=True)
    email = Column(String(250), unique=True, index=True, nullable=False)
    password = Column(String(250), nullable=False, index=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    lastUpdatedDate = Column(String(250), nullable=True, index=True)
    lastUpdatedBy = Column(Integer, nullable=True, index=True)
    needsToChangePassword = Column(Boolean(), default=True, index=True)
    expiryDate = Column(String(250), nullable=True, index=True)
    contactPhone = Column(String(250), nullable=True, index=True)
    lastChangedPasswordDate = Column(String(250), nullable=True, index=True)
    numberOfFailedAttempts = Column(Integer, nullable=True, index=True)
    roles = relationship("Role", secondary="user_role", backref="users")
