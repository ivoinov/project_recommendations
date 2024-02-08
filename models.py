from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, index=True)
    hashed_password = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    full_name = Column(String(100))
    disabled = Column(Boolean, default=False)
    tokens = relationship("Token", back_populates="user")


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


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    description = Column(String(1000))
    price = Column(Integer)
    category = Column(String(100))


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), index=True)
    quantity = Column(Integer)


class ProductRecommendation:
    def __init__(self, product_id, recommendations):
        self.product_id = product_id
        self.recommendations = recommendations
