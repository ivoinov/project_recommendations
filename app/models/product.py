from sqlalchemy import Boolean, Column, Integer, String, Text
from .base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(255), index=True)
    name = Column(String(255), index=True)
    short_description = Column(Text)
    description = Column(Text)
    price = Column(Integer)
    categories_names = Column(Text)
    parent_category = Column(String(255))
    current_price = Column(Integer)
    in_stock = Column(Boolean, nullable=True)
    tags = Column(Text, nullable=True)
    as_dict = lambda self: {
        "sku": self.sku,
        "name": self.name,
        "short_description": self.short_description,
        "description": self.description,
        "price": self.price,
        "categories_names": self.categories_names,
        "parent_category": self.parent_category,
        "current_price": self.current_price,
        "in_stock": self.in_stock,
        "tags": self.tags,
    }
