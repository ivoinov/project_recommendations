from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
)
from .base import Base


class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    increment_id = Column(String(255), nullable=True, index=False)
    customer_id = Column(Integer, nullable=True, index=False)
    sku = Column(String(255))
    quantity = Column(Integer)
    product_name = Column(String(254), index=False, nullable=False)
    total_price = Column(DECIMAL(12, 4))
    item_price = Column(DECIMAL(12, 4))
