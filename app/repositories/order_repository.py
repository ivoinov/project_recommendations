from app.models import Order
from app.config import settings
from sqlalchemy import func


class OrderRepository:
    def __init__(self, db):
        self.db = db

    def create(self, order):
        try:
            db_order = Order(
                increment_id=order.increment_id,
                customer_id=order.customer_id,
                sku=order.sku,
                quantity=order.quantity,
                product_name=order.product_name,
                total_price=order.total_price,
                item_price=order.item_price,
            )
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
            db_order = Order()
            db_order.increment_id = order.increment_id
            db_order.customer_id = order.customer_id
            db_order.sku = order.sku
            db_order.quantity = order.quantity
            db_order.product_name = order.product_name
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
        finally:
            self.db.close()

    def get_all_increment_ids(self):
        try:
            increment_ids = self.db.query(Order.increment_id).all()
            return [increment_id for increment_id, in increment_ids]
        except Exception as e:
            self.db.rollback()
            settings.logger.error(f"Error getting existing increment ids: {e}")
            raise
        finally:
            self.db.close()

    def create_batch(self, orders):
        try:
            self.db.add_all(orders)
            self.db.commit()
            return orders
        except Exception as e:
            self.db.rollback()
            settings.logger.error(f"Error creating or updating orders: {e}")
            raise
        finally:
            self.db.close()
