from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from .base import Base
from .token import Token


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    disabled = Column(Boolean, default=False)
    tokens = relationship("Token", back_populates="user", lazy="dynamic")
