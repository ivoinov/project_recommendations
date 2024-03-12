import pytest
from sqlalchemy import Integer, String, DECIMAL
from app.models import Order

def test_order_id():
    assert isinstance(Order.id.type, Integer), "Order.id should be of type Integer"

def test_order_increment_id():
    assert isinstance(Order.increment_id.type, String), "Order.increment_id should be of type String"

def test_order_customer_id():
    assert isinstance(Order.customer_id.type, Integer), "Order.customer_id should be of type Integer"

def test_order_sku():
    assert isinstance(Order.sku.type, String), "Order.sku should be of type String"

def test_order_quantity():
    assert isinstance(Order.quantity.type, Integer), "Order.quantity should be of type Integer"

def test_order_product_name():
    assert isinstance(Order.product_name.type, String), "Order.product_name should be of type String"

def test_order_total_price():
    assert isinstance(Order.total_price.type, DECIMAL), "Order.total_price should be of type DECIMAL"

def test_order_item_price():
    assert isinstance(Order.item_price.type, DECIMAL), "Order.item_price should be of type DECIMAL"