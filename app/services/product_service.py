from typing import List

from app.config import settings
from app.models import Product
from app.repositories import ProductRepository


class ProductService:
    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository
        self.map_sku_to_id: dict = self.get_skus_to_ids()
        self.map_id_to_sku: dict = {v: k for k, v in self.map_sku_to_id.items()}

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

    def get_skus_to_ids(self) -> dict:
        try:
            map_sku_to_id = {}
            products = self.product_repository.get_all()
            map_sku_to_id = {product.sku: product.id for product in products}
            return map_sku_to_id
        except Exception as e:
            settings.logger.error(f"Error getting skus to ids: {e}")
            return None

    def get_product_id_by_sku(self, sku: str) -> int:
        try:
            return round(self.map_sku_to_id.get(sku, 0), 0)
        except Exception as e:
            settings.logger.error(f"Error getting product id by sku: {e}")
            return None

    def get_sku_by_product_id(self, product_id: int) -> str:
        try:
            return self.map_id_to_sku.get(product_id, None)
        except Exception as e:
            settings.logger.error(f"Error getting sku by product id: {e}")
            return None

    def create_or_update_products_bulk(self, products_data: List[dict]):
        try:
            to_update = []
            to_create = []
            products = []
            for data in products_data:
                product = Product(**data)
                sku = data.get("sku", "")
                product_id = self.map_sku_to_id.get(sku, None)
                if product_id is not None:
                    product.id = product_id
                    to_update.append(product)
                else:
                    to_create.append(product)
                products.append(product)
            self.product_repository.create_bulk(to_create)
            self.product_repository.update_bulk(to_update)
            return products
        except Exception as e:
            settings.logger.error(f"Error creating or updating products in bulk: {e}")
            return None
