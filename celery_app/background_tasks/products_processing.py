import csv, os
from config import project_root
from app.models import Product
from app.database import create_or_update_product


def process_products_csv_file():
    file_path = os.path.join(project_root, "var", "df_total.csv")
    tasks = []
    with open(file_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            # Process each row of the CSV file
            sku = row.get("sku", "")
            name = row.get("name", "")
            short_description = row.get("product_description", "")
            description = row.get("full_description_text_translated", "")
            price = float(row.get("price", 0))
            categories_names = row.get("categories_names", "")
            current_price = float(row.get("current_price", 0))
            parent_category = int(row.get("parent_category", ""))
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
