import csv, os
from itertools import islice
from app.config import settings, db_settings
from app.services import ProductService
from app.repositories import ProductRepository

def process_products_csv_file():
    db = next(db_settings.get_db())
    file_path = os.path.join(settings.project_root, "var", "products_data.csv")
    chunk_size = 1000
    product_repository = ProductRepository(db)
    product_service = ProductService(product_repository)

    with open(file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=",", quotechar='"')
        while True:
            products = []
            for row in islice(reader, chunk_size):
                try:
                    product = {}
                    # Process each row of the CSV file
                    product["sku"] = row.get("sku", "")
                    product["name"] = row.get("product_name", "")
                    product["short_description"] = row.get("short_description", "")
                    product["description"] = row.get("description", "")
                    product["categories_names"] = row.get("categories", "")
                    product["price"] = (
                        float(row.get("price", 0)) if is_float(row.get("price", 0)) else 0.0
                    )
                    product["current_price"] = (
                        float(row.get("price", 0)) if is_float(row.get("price", 0)) else 0.0
                    )
                    # Split the categories_names string by comma and get the last element
                    product["parent_category"] = (
                        product["categories_names"].split(",")[-1].strip()
                        if product["categories_names"]
                        else ""
                    )
                    products.append(product)
                except Exception as e:
                    print(f"Error processing row: {row}. Exception: {e}")
                    settings.logger.error(f"Error processing row: {row}. Exception: {e}")
                    continue

            if not products:
                break

            product_service.create_or_update_products_bulk(products)

    db.close()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False