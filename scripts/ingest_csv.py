import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.csv_ingestion_service import ingest_directory


def _print_summary(results: dict) -> None:
    shops = results.get("shops", {})
    validation = results.get("validation", {})

    if not shops:
        print("No shop data ingested.")
        return

    print("Ingestion summary:")
    for shop_id, summary in sorted(shops.items()):
        products = summary.get("products", {})
        orders = summary.get("orders", {})
        print(
            f"- {shop_id}: products {products.get('accepted', 0)} accepted, "
            f"{products.get('rejected', 0)} rejected | orders "
            f"{orders.get('accepted', 0)} accepted, {orders.get('rejected', 0)} rejected"
        )

    if not validation.get("passes_threshold", True):
        print("Warning: validation threshold not met for one or more shops.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest multi-shop CSV data")
    parser.add_argument(
        "--input-dir", default="var", help="Directory containing CSV files"
    )
    parser.add_argument(
        "--error-threshold",
        type=float,
        default=0.05,
        help="Max error rate per shop before validation fails",
    )
    parser.add_argument("--json", action="store_true", help="Output JSON summary")
    args = parser.parse_args()

    results = ingest_directory(args.input_dir, error_threshold=args.error_threshold)

    if args.json:
        print(json.dumps(results.get("shops", {}), indent=2))
    else:
        _print_summary(results)


if __name__ == "__main__":
    main()
