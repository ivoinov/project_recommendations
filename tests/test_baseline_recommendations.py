from sqlalchemy import text

from app.models import Product, Order
from app.services.shop_db import ensure_shop_schema


def seed_shop_data(db, shop_id="test"):
    ensure_shop_schema(db, shop_id)

    products = [
        Product(
            sku="sku-1",
            name="Seed Product",
            short_description="Seed",
            description="Seed product",
            price=100,
            categories_names="tops",
            parent_category="cat-a",
            current_price=100,
            in_stock=True,
            tags="red summer",
        ),
        Product(
            sku="sku-2",
            name="Co Purchase",
            short_description="Co",
            description="Co purchase",
            price=110,
            categories_names="tops",
            parent_category="cat-a",
            current_price=110,
            in_stock=True,
            tags="red",
        ),
        Product(
            sku="sku-3",
            name="Alt Product",
            short_description="Alt",
            description="Alternate",
            price=90,
            categories_names="tops",
            parent_category="cat-a",
            current_price=90,
            in_stock=True,
            tags="blue",
        ),
        Product(
            sku="sku-6",
            name="Out of Stock",
            short_description="OOS",
            description="Out of stock",
            price=105,
            categories_names="tops",
            parent_category="cat-a",
            current_price=105,
            in_stock=False,
            tags="red",
        ),
        Product(
            sku="sku-7",
            name="In Stock",
            short_description="Stock",
            description="In stock",
            price=103,
            categories_names="tops",
            parent_category="cat-a",
            current_price=103,
            in_stock=True,
            tags="red",
        ),
    ]

    orders = [
        Order(
            increment_id="100",
            customer_id=1,
            sku="sku-1",
            quantity=1,
            product_name="Seed Product",
            total_price=100,
            item_price=100,
        ),
        Order(
            increment_id="100",
            customer_id=1,
            sku="sku-2",
            quantity=1,
            product_name="Co Purchase",
            total_price=110,
            item_price=110,
        ),
        Order(
            increment_id="101",
            customer_id=1,
            sku="sku-1",
            quantity=1,
            product_name="Seed Product",
            total_price=100,
            item_price=100,
        ),
        Order(
            increment_id="101",
            customer_id=1,
            sku="sku-3",
            quantity=1,
            product_name="Alt Product",
            total_price=90,
            item_price=90,
        ),
    ]

    db.add_all(products)
    db.add_all(orders)
    db.commit()
    db.execute(text("SET search_path TO public"))


def test_pdp_recommendations_include_co_purchase(authenticated_client, test_db):
    seed_shop_data(test_db)

    response = authenticated_client.get("/v1/shops/test/recommendations/pdp/sku-1")
    assert response.status_code == 200

    payload = response.json()
    assert payload["placement"] == "pdp"
    assert payload["seed_skus"] == ["sku-1"]
    assert "sku-2" in payload["co_purchase"]
    assert "sku-3" in payload["co_purchase"]
    assert "sku-1" not in payload["recommendations"]
    assert "sku-6" not in payload["recommendations"]


def test_cart_recommendations_apply_rules(authenticated_client, test_db):
    seed_shop_data(test_db)

    response = authenticated_client.post(
        "/v1/shops/test/recommendations/cart",
        json={"cart_skus": ["sku-1", "sku-2"], "exclude_skus": ["sku-3"], "limit": 5},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["placement"] == "cart"
    assert set(payload["seed_skus"]) == {"sku-1", "sku-2"}
    assert "sku-3" not in payload["recommendations"]
    assert "sku-6" not in payload["recommendations"]
    assert "sku-1" not in payload["recommendations"]
    assert "sku-2" not in payload["recommendations"]
    assert "sku-7" in payload["recommendations"]
