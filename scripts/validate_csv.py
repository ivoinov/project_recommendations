import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.services.csv_validation_service import validate_input_dir


def _format_rate(value: float) -> str:
    return f"{value * 100:.2f}%"


def _print_summary(results: dict) -> None:
    threshold = results["error_threshold"]
    print(f"CSV validation summary (threshold {_format_rate(threshold)})")

    if not results["shops"]:
        print("No shop files found. Expected *_products.csv and *_orders.csv.")
        return

    for shop_id in sorted(results["shops"].keys()):
        summary = results["shops"][shop_id]
        missing = summary.get("missing_files", [])
        status = (
            "PASS" if not missing and summary["error_rate"] <= threshold else "FAIL"
        )

        print(f"\nShop: {shop_id}")
        print(f"- Files: {', '.join(sorted(summary['files'])) or 'None'}")
        print(f"- Total rows: {summary['total_rows']}")
        print(f"- Error rows: {summary['error_rows']}")
        print(f"- Error rate: {_format_rate(summary['error_rate'])}")
        if missing:
            print(f"- Missing files: {', '.join(missing)}")
        print(f"- Status: {status}")

        for file_name in sorted(summary["files"]):
            file_result = results["files"].get(file_name)
            if not file_result:
                continue
            print(
                f"  - {file_name}: {file_result['error_rows']}/"
                f"{file_result['total_rows']} errors"
            )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate multi-shop CSVs with normalization rules."
    )
    parser.add_argument(
        "--input-dir",
        required=True,
        help="Directory containing *_products.csv and *_orders.csv files.",
    )
    parser.add_argument(
        "--error-threshold",
        type=float,
        default=0.05,
        help="Maximum error rate allowed per shop (default: 0.05).",
    )
    args = parser.parse_args()

    results = validate_input_dir(args.input_dir, args.error_threshold)
    _print_summary(results)
    return 0 if results["passes_threshold"] else 1


if __name__ == "__main__":
    sys.exit(main())
