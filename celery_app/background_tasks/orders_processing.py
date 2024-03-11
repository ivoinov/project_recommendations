import os
import pandas as pd
from app.config import settings, db_settings
from app.services import OrderService
from app.repositories import OrderRepository


def process_orders_csv_file():
    db = next(db_settings.get_db())
    order_service = OrderService(OrderRepository(db))
    file_path = os.path.join(settings.project_root, "var", "orders_data.csv")
    orders = pd.read_csv(
        file_path,
        sep=",",
        dtype={
            "increment_id": pd.StringDtype(),
            "customer_id": pd.Int64Dtype(),
            "sku": pd.StringDtype(),
            "qty_ordered": pd.Int64Dtype(),
            "name": pd.StringDtype(),
            "base_grand_total": pd.Float64Dtype(),
            "row_total": pd.Float64Dtype(),
        },
    )
    batch_size = 1000
    for i in range(0, len(orders), batch_size):
        batch = orders[i : i + batch_size]
        data = []
        for order in batch.itertuples():
            try:
                if hasattr(order, "increment_id"):
                    increment_id = order.increment_id
                else:
                    increment_id = ""
                customer_id = (
                    int(order.customer_id) if pd.notna(order.customer_id) else 0
                )
                increment_id = (
                    int(order.increment_id) if pd.notna(order.increment_id) else 0
                )
                customer_id = (
                    int(order.customer_id) if pd.notna(order.customer_id) else 0
                )
                order_data = {}
                order_data["increment_id"] = str(increment_id)
                order_data["customer_id"] = int(customer_id)
                order_data["sku"] = str(order.sku)
                order_data["quantity"] = int(order.qty_ordered)
                order_data["product_name"] = str(order.name)
                order_data["total_price"] = (
                    0.0 if pd.isna(order.base_grand_total) else order.base_grand_total
                )
                order_data["item_price"] = (
                    0.0 if pd.isna(order.row_total) else order.row_total
                )
                data.append(order_data)
            except Exception as e:
                print(f"Error processing order: {order}")
                print(e)
        order_service.create_or_update_batch(data)
    db.close()
