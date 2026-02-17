import csv
import logging
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pathlib import Path

LOGGER = logging.getLogger(__name__)

REQUIRED_PRODUCT_FIELDS = [
    "sku",
    "name",
    "category",
    "price",
    "in_stock",
    "short_description",
    "meta_title",
    "meta_description",
]

REQUIRED_ORDER_FIELDS = [
    "order_id",
    "shop_id",
    "customer_id",
    "order_date",
    "sku",
    "qty",
    "price",
]


def _trim_value(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value.strip()
    return value


def _parse_bool(value):
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip().lower()
        if cleaned in {"true", "1", "yes", "y", "t"}:
            return True
        if cleaned in {"false", "0", "no", "n", "f"}:
            return False
        return None
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def _parse_decimal(value):
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


def _parse_date(value):
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, str):
        cleaned = value.strip()
        if cleaned == "":
            return None
        try:
            return datetime.fromisoformat(cleaned).date().isoformat()
        except ValueError:
            pass
        try:
            return date.fromisoformat(cleaned).isoformat()
        except ValueError:
            pass
        for fmt in ("%Y/%m/%d", "%m/%d/%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(cleaned, fmt).date().isoformat()
            except ValueError:
                continue
    return None


def normalize_product_row(row: dict) -> dict:
    cleaned = {key: _trim_value(value) for key, value in row.items()}
    cleaned["in_stock"] = _parse_bool(cleaned.get("in_stock"))
    cleaned["price"] = _parse_decimal(cleaned.get("price"))
    return cleaned


def normalize_order_row(row: dict) -> dict:
    cleaned = {key: _trim_value(value) for key, value in row.items()}
    cleaned["qty"] = _parse_decimal(cleaned.get("qty"))
    cleaned["price"] = _parse_decimal(cleaned.get("price"))
    cleaned["order_date"] = _parse_date(cleaned.get("order_date"))
    return cleaned


def _validate_required_fields(normalized_row: dict, required_fields: list) -> list:
    errors = []
    for field in required_fields:
        value = normalized_row.get(field)
        if value is None or value == "":
            errors.append(f"missing {field}")
    return errors


def _validate_type_fields(
    normalized_row: dict, raw_row: dict, field_name: str, kind: str
) -> list:
    raw_value = _trim_value(raw_row.get(field_name))
    normalized_value = normalized_row.get(field_name)
    if raw_value not in (None, "") and normalized_value is None:
        return [f"invalid {kind} for {field_name}"]
    return []


def _validate_csv_file(file_path: Path, file_type: str, shop_id: str) -> dict:
    results = {
        "shop_id": shop_id,
        "file_type": file_type,
        "total_rows": 0,
        "error_rows": 0,
        "errors": [],
        "normalized_rows": [],
        "valid_rows": [],
    }

    with file_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=";", quotechar='"')
        for index, row in enumerate(reader, start=2):
            results["total_rows"] += 1
            normalized = (
                normalize_product_row(row)
                if file_type == "products"
                else normalize_order_row(row)
            )
            errors = (
                _validate_required_fields(normalized, REQUIRED_PRODUCT_FIELDS)
                if file_type == "products"
                else _validate_required_fields(normalized, REQUIRED_ORDER_FIELDS)
            )

            if file_type == "products":
                errors.extend(
                    _validate_type_fields(normalized, row, "price", "decimal")
                )
                errors.extend(
                    _validate_type_fields(normalized, row, "in_stock", "boolean")
                )
            else:
                errors.extend(_validate_type_fields(normalized, row, "qty", "decimal"))
                errors.extend(
                    _validate_type_fields(normalized, row, "price", "decimal")
                )
                errors.extend(
                    _validate_type_fields(normalized, row, "order_date", "date")
                )

            results["normalized_rows"].append(normalized)
            if errors:
                results["error_rows"] += 1
                results["errors"].append(
                    {
                        "row_number": index,
                        "errors": errors,
                        "normalized_row": normalized,
                    }
                )
            else:
                results["valid_rows"].append(normalized)

    return results


def _discover_csv_files(input_dir: Path) -> dict:
    files = {"products": [], "orders": []}
    for entry in input_dir.iterdir():
        if not entry.is_file():
            continue
        name = entry.name
        if name.endswith("_products.csv"):
            files["products"].append(entry)
        elif name.endswith("_orders.csv"):
            files["orders"].append(entry)
    return files


def validate_input_dir(input_dir: str, error_threshold: float = 0.05) -> dict:
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")

    discovered = _discover_csv_files(input_path)
    results = {
        "error_threshold": error_threshold,
        "files": {},
        "shops": {},
        "passes_threshold": True,
    }

    for file_type, files in discovered.items():
        for file_path in sorted(files):
            shop_id = file_path.name.replace(f"_{file_type}.csv", "")
            file_results = _validate_csv_file(file_path, file_type, shop_id)
            results["files"][file_path.name] = file_results
            shop_summary = results["shops"].setdefault(
                shop_id,
                {
                    "files": [],
                    "total_rows": 0,
                    "error_rows": 0,
                    "missing_files": [],
                    "error_rate": 0.0,
                },
            )
            shop_summary["files"].append(file_path.name)
            shop_summary["total_rows"] += file_results["total_rows"]
            shop_summary["error_rows"] += file_results["error_rows"]

    for shop_id, summary in results["shops"].items():
        has_products = any(name.endswith("_products.csv") for name in summary["files"])
        has_orders = any(name.endswith("_orders.csv") for name in summary["files"])
        if not has_products:
            summary["missing_files"].append("products")
        if not has_orders:
            summary["missing_files"].append("orders")

        if summary["missing_files"] or summary["total_rows"] == 0:
            summary["error_rate"] = 1.0
        else:
            summary["error_rate"] = summary["error_rows"] / summary["total_rows"]

        if summary["error_rate"] > error_threshold or summary["missing_files"]:
            results["passes_threshold"] = False

    if not results["shops"]:
        LOGGER.error(
            "No CSV files found for validation. Expected *_products.csv and *_orders.csv."
        )
        results["passes_threshold"] = False

    return results
