from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

# if TYPE_CHECKING:
#     from app.models.permission import Permission


class PermissionGroup(Base):
    __tablename__ = "permission_group"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=True, index=True)
    permission_group_id = Column(Integer, ForeignKey("permission_group.id"))
    insertedBy = Column(Integer, nullable=True, index=True)
    insertedDate = Column(String(250), default=datetime.utcnow())
    groups = relationship("PermissionGroup", lazy="joined", join_depth=10)
    permissions = relationship("Permission", lazy="joined")
