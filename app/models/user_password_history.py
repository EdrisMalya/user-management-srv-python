from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String

from app.db.base_class import Base


class UserPasswordHistory(Base):
    __tablename__ = "user_password_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="SET NULL", use_alter=True), index=True
    )
    password = Column(String(250), nullable=True, index=True)
    inserted = Column(String(250), default=datetime.utcnow(), index=True)
