from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.base_class import Base


class Permission(Base):
    __tablename__ = "permission"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=True, index=True)
    description = Column(String(250), nullable=True, index=True)
    group_id = Column(Integer, ForeignKey("permission_group.id"))
    insertedBy = Column(Integer, nullable=False, index=True)
    insertedDate = Column(String(250), default=datetime.utcnow())
