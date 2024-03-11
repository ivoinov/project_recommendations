from app.repositories import ProductRepository
from app.models import Product
from app.config import settings


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def create_or_update_product(self, data: dict):
        try:
            product = Product(**data)
            sku = data.get("sku", "")
            existing_product = self.product_repository.search_by_attribute("sku", sku)
            if existing_product:
                self.product_repository.update(product)
            else:
                self.product_repository.create(product)
            return product
        except Exception as e:
            settings.logger.error(f"Error creating or updating product: {e}")
            return None
