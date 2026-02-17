from collections import defaultdict
from decimal import Decimal, InvalidOperation

from app.config import settings
from app.repositories import OrderRepository, ProductRepository
from app.services.csv_validation_service import validate_input_dir
from app.services.db_routing import get_shop_session
from app.services.order_service import OrderService
from app.services.product_service import ProductService


def _build_shop_summary() -> dict:
    return {
        "products": {"accepted": 0, "rejected": 0, "total": 0},
        "orders": {"accepted": 0, "rejected": 0, "total": 0},
    }


def _to_int(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, Decimal):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "":
            return None
        try:
            return int(Decimal(cleaned))
        except (InvalidOperation, ValueError):
            return None
    return None


def _to_decimal(value):
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "":
            return None
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return None
    return None


def _build_product_payload(normalized_row: dict) -> dict:
    price_value = _to_int(normalized_row.get("price"))
    description = normalized_row.get("description") or normalized_row.get(
        "meta_description"
    )
    category = normalized_row.get("category")
    return {
        "sku": normalized_row.get("sku"),
        "name": normalized_row.get("name"),
        "short_description": normalized_row.get("short_description"),
        "description": description,
        "price": price_value,
        "categories_names": category,
        "parent_category": category,
        "current_price": price_value,
    }


def _build_order_payload(normalized_row: dict) -> dict:
    qty_value = _to_int(normalized_row.get("qty"))
    item_price = _to_decimal(normalized_row.get("price"))
    total_price = (
        item_price * qty_value
        if item_price is not None and qty_value is not None
        else None
    )
    product_name = (
        normalized_row.get("product_name")
        or normalized_row.get("name")
        or normalized_row.get("sku")
        or "unknown"
    )
    return {
        "increment_id": normalized_row.get("order_id"),
        "customer_id": _to_int(normalized_row.get("customer_id")),
        "sku": normalized_row.get("sku"),
        "quantity": qty_value,
        "product_name": product_name,
        "total_price": total_price,
        "item_price": item_price,
    }


def ingest_directory(input_dir: str, error_threshold: float = 0.05) -> dict:
    validation_results = validate_input_dir(input_dir, error_threshold=error_threshold)

    shops_summary = defaultdict(_build_shop_summary)
    products_by_shop = defaultdict(list)
    orders_by_shop = defaultdict(list)

    for file_results in validation_results.get("files", {}).values():
        shop_id = file_results.get("shop_id")
        file_type = file_results.get("file_type")
        if not shop_id or file_type not in {"products", "orders"}:
            continue

        shop_summary = shops_summary[shop_id]
        accepted = len(file_results.get("valid_rows", []))
        shop_summary[file_type]["accepted"] += accepted
        shop_summary[file_type]["rejected"] += file_results.get("error_rows", 0)
        shop_summary[file_type]["total"] += file_results.get("total_rows", 0)

        if accepted:
            if file_type == "products":
                products_by_shop[shop_id].extend(file_results["valid_rows"])
            else:
                orders_by_shop[shop_id].extend(file_results["valid_rows"])

    for shop_id in shops_summary:
        session = get_shop_session(shop_id)
        try:
            if products_by_shop.get(shop_id):
                product_repo = ProductRepository(session)
                product_service = ProductService(product_repo)
                product_payloads = [
                    _build_product_payload(row) for row in products_by_shop[shop_id]
                ]
                product_service.create_or_update_products_bulk(product_payloads)

            if orders_by_shop.get(shop_id):
                order_repo = OrderRepository(session)
                order_service = OrderService(order_repo)
                order_payloads = [
                    _build_order_payload(row) for row in orders_by_shop[shop_id]
                ]
                order_service.create_or_update_batch(order_payloads)
        except Exception:
            settings.logger.exception("Error ingesting CSV data for shop")
            raise
        finally:
            session.close()

    return {
        "shops": dict(shops_summary),
        "validation": validation_results,
    }
