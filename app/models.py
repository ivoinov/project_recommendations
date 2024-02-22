from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
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
    sku = Column(String(255), index=True)
    name = Column(String(255), index=True)
    short_description = Column(Text)
    description = Column(Text)
    price = Column(Integer)
    categories_names = Column(String(255))
    parent_category = Column(Integer)
    current_price = Column(Integer)


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    increment_id = Column(String(255), index=True)
    customer_id = Column(Integer)
    sku = Column(String(255), index=True)
    quantity = Column(Integer)
    product_name = Column(String(254), index=False, nullable=False)
    total_price = Column(Integer)
    item_price = Column(Integer)


class ProductRecommendation:
    def __init__(self, product_id, recommendations):
        self.product_id = product_id
        self.recommendations = recommendations
