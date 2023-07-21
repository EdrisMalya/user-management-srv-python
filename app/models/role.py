from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    pass


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=True, index=True)
    description = Column(String(250), nullable=True, index=True)
    insertedBy = Column(Integer, nullable=True, index=True)
    insertedDate = Column(String(250), default=datetime.utcnow())
    permissions = relationship(
        "Permission", secondary="role_permission", backref="roles"
    )
