from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base_class import Base

if TYPE_CHECKING:
    pass


class LoggedInUsers(Base):
    __tablename__ = "logged_in_users"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="CASCADE ", use_alter=True), index=True, unique=True
    )
    refresh_token = Column(String(250), nullable=True, index=True)
