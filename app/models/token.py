from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from app.config import ACCESS_TOKEN_EXPIRE_MINUTES
from .base import Base


class Token(Base):
    __tablename__ = "tokens"
    id = Column(Integer, primary_key=True)
    token = Column(String(254), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tokens")
    expires_at = Column(
        DateTime,
        default=datetime.utcnow() + timedelta(seconds=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
