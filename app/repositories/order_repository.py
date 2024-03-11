from app.models import Order
from app.config import settings
from sqlalchemy import func


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def create(self, order):
        try:
            db_order = (
                self.db.query(Order)
                .filter(Order.increment_id == order.increment_id)
                .first()
            )
            if db_order is None:
                db_order = Order(
                    increment_id=order.increment_id,
                    customer_id=order.customer_id,
                    sku=order.sku,
                    quantity=order.quantity,
                    product_name=order.product_name,
                    total_price=order.total_price,
                    item_price=order.item_price,
                )
            else:
                db_order.quantity = order.quantity
                db_order.total_price = order.total_price
                db_order.item_price = order.item_price
            self.db.add(db_order)
            self.db.commit()
            self.db.refresh(db_order)
            return db_order
        except Exception as e:
            self.db.rollback()
            settings.logger.error(f"Error creating or updating order: {e}")
            raise
        finally:
            self.db.close()

    def update(self, order):
        try:
            db_order = (
                self.db.query(Order)
                .filter(Order.increment_id == order.increment_id)
                .first()
            )
            db_order.quantity = order.quantity
            db_order.total_price = order.total_price
            db_order.item_price = order.item_price
            self.db.commit()
            self.db.refresh(db_order)
            return db_order
        except Exception as e:
            self.db.rollback()
            settings.logger.error(f"Error updating order: {e}")
            raise
        finally:
            self.db.close()

    def get_order_aggregated_data_query(self):
        try:
            query = self.db.query(
                Order.customer_id.label("user_id"),
                Order.sku.label("item_id"),
                (
                    func.sum(Order.quantity * Order.item_price)
                    / func.sum(Order.quantity)
                ).label("rating"),
            ).group_by(Order.customer_id, Order.sku)
            return query
        except Exception as e:
            self.db.rollback()
            settings.logger.error(f"Error getting orders aggregated data: {e}")
            raise
