import pytest
from app.models import Product
from sqlalchemy import Column, Integer, String, Text

def test_product_table():
    assert Product.__tablename__ == "products", "Product table name should be 'products'"

def test_product_columns():
    assert isinstance(Product.__table__.c.id, Column), "id should be a Column"
    assert isinstance(Product.__table__.c.id.type, Integer), "id should be an Integer"
    assert Product.__table__.c.id.primary_key == True, "id should be a primary key"
    assert Product.__table__.c.id.index == True, "id should be indexed"

    assert isinstance(Product.__table__.c.sku, Column), "sku should be a Column"
    assert isinstance(Product.__table__.c.sku.type, String), "sku should be a String"
    assert Product.__table__.c.sku.index == True, "sku should be indexed"

    assert isinstance(Product.__table__.c.name, Column), "name should be a Column"
    assert isinstance(Product.__table__.c.name.type, String), "name should be a String"
    assert Product.__table__.c.name.index == True, "name should be indexed"

    assert isinstance(Product.__table__.c.short_description, Column), "short_description should be a Column"
    assert isinstance(Product.__table__.c.short_description.type, Text), "short_description should be a Text"

    assert isinstance(Product.__table__.c.description, Column), "description should be a Column"
    assert isinstance(Product.__table__.c.description.type, Text), "description should be a Text"

    assert isinstance(Product.__table__.c.price, Column), "price should be a Column"
    assert isinstance(Product.__table__.c.price.type, Integer), "price should be an Integer"

    assert isinstance(Product.__table__.c.categories_names, Column), "categories_names should be a Column"
    assert isinstance(Product.__table__.c.categories_names.type, String), "categories_names should be a String"

    assert isinstance(Product.__table__.c.parent_category, Column), "parent_category should be a Column"
    assert isinstance(Product.__table__.c.parent_category.type, String), "parent_category should be a String"

    assert isinstance(Product.__table__.c.current_price, Column), "current_price should be a Column"
    assert isinstance(Product.__table__.c.current_price.type, Integer), "current_price should be an Integer"

def test_product_as_dict():
    product = Product(
        sku="test_sku",
        name="test_name",
        short_description="test_short_description",
        description="test_description",
        price=100,
        categories_names="test_categories_names",
        parent_category="test_parent_category",
        current_price=90,
    )

    expected_dict = {
        "sku": "test_sku",
        "name": "test_name",
        "short_description": "test_short_description",
        "description": "test_description",
        "price": 100,
        "categories_names": "test_categories_names",
        "parent_category": "test_parent_category",
        "current_price": 90,
    }

    assert product.as_dict() == expected_dict, "as_dict method should return the correct dictionary"