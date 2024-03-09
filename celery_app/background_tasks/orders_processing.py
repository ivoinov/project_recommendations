import os
import pandas as pd
from app.config import settings
from app.models import Order
from app.database import create_or_update_order


def process_orders_csv_file():
    file_path = os.path.join(settings.project_root, "var", "orders_data.csv")
    orders = pd.read_csv(
        file_path,
        sep=",",
        dtype={
            "increment_id": str,
            "customer_id": int,
            "sku": str,
            "qty_ordered": int,
            "name": str,
            "base_grand_total": float,
            "row_total": float,
        },
    )
    for order in orders.itertuples():
        try:
            if hasattr(order, "increment_id"):
                increment_id = order.increment_id
            else:
                increment_id = ""
            customer_id = int(order.customer_id) if pd.notna(order.customer_id) else 0
            order = Order(
                increment_id=str(increment_id),
                customer_id=customer_id,
                sku=str(order.sku),
                quantity=int(order.qty_ordered),
                product_name=str(order.name),
                total_price=float(order.base_grand_total),
                item_price=float(order.row_total),
            )
            create_or_update_order(order)
        except Exception as e:
            print(f"Error processing order: {order}")
            print(e)
            continue
