from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    pass


class RoleGroup(Base):
    __tablename__ = "role_group"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=True, index=True)
    insertedBy = Column(Integer, nullable=True, index=True)
    insertedDate = Column(String(250), default=datetime.utcnow())
    roles = relationship("Role", secondary="role_group_map", backref="role_group")
