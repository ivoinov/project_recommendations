from app.models import Order
from app.repositories import OrderRepository
from app.config import settings


class OrderService:
    existing_increment_ids: list = []

    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
        self.existing_increment_ids = self.order_repository.get_all_increment_ids()

    def create_or_update(self, order_data: dict) -> Order:
        try:
            order = Order(**order_data)
            if order.increment_id in self.existing_increment_ids:
                return self.order_repository.update(order)
            else:
                return self.order_repository.create(order)
        except Exception as e:
            settings.logger.error(f"Error creating or updating order: {e}")
            raise

    def create_or_update_batch(self, orders_data: list) -> list:
        try:
            orders = []
            for order_data in orders_data:
                order = Order(**order_data)
                if order.increment_id not in self.existing_increment_ids:
                    orders.append(order)
            return self.order_repository.create_batch(orders)
        except Exception as e:
            settings.logger.error(f"Error creating or updating orders: {e}")
            raise
