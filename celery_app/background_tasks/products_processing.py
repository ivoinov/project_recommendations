import csv, os
from app.config import settings
from app.models import Product
from app.database import create_or_update_product


def process_products_csv_file():
    file_path = os.path.join(settings.project_root, "var", "products_data.csv")
    with open(file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            try:
                # Process each row of the CSV file
                sku = row.get("sku", "")
                name = row.get("product_name", "")
                short_description = row.get("short_description", "")
                description = row.get("description", "")
                categories_names = row.get("categories", "")
                price = (
                    float(row.get("price", 0)) if is_float(row.get("price", 0)) else 0.0
                )
                current_price = (
                    float(row.get("price", 0)) if is_float(row.get("price", 0)) else 0.0
                )
                # Split the categories_names string by comma and get the last element
                parent_category = (
                    categories_names.split(",")[-1].strip() if categories_names else ""
                )
                # Create a new Product instance
                product = Product(
                    sku=sku,
                    name=name,
                    price=price,
                    description=description,
                    short_description=short_description,
                    categories_names=categories_names,
                    parent_category=parent_category,
                    current_price=current_price,
                )
                create_or_update_product(product)
            except Exception as e:
                print(f"Error processing row: {row}")
                print(e)
                continue


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
