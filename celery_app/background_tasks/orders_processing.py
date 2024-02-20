import csv, os
import pandas as pd
from config import project_root
from app.models import Order
from app.database import create_or_update_order


def process_orders_csv_file():
    file_path = os.path.join(project_root, "var", "order_data.csv")
    orders = pd.read_csv(file_path, sep=";")
    orders = orders.rename(
        columns={"639553": "user_id", "649385": "sku", "1": "quantity"}
    )

    for order in orders.itertuples():
        if hasattr(order, "increment_id"):
            increment_id = order.increment_id
        else:
            increment_id = ""
        order = Order(
            customer_id=order.user_id,
            increment_id=increment_id,
            sku=order.sku,
            quantity=order.quantity,
            product_name=order.sku,
            total_price=200,
            item_price=100,
        )
        create_or_update_order(order)
