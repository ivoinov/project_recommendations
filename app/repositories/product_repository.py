from app.models import Product
from app.config import settings
from sqlalchemy import func


class ProductRepository:
    def __init__(self, db):
        self.db = db

    def create(self, product):
        try:
            db_product = Product(
                sku=product.sku,
                name=product.name,
                description=product.description,
                price=product.price,
                short_description=product.short_description,
                categories_names=product.categories_names,
                parent_category=product.parent_category,
                current_price=product.current_price,
                in_stock=product.in_stock,
                tags=product.tags,
            )
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error creating product")
            raise

    def update(self, product):
        try:
            db_product = (
                self.db.query(Product).filter(Product.sku == product.sku).first()
            )
            db_product.name = product.name
            db_product.price = product.price
            db_product.description = product.description
            db_product.short_description = product.short_description
            db_product.categories_names = product.categories_names
            db_product.parent_category = product.parent_category
            db_product.current_price = product.current_price
            db_product.in_stock = product.in_stock
            db_product.tags = product.tags
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error updating product")
            raise

    def search_by_attribute(self, attribute, value):
        if isinstance(value, list) or isinstance(value, tuple):
            return (
                self.db.query(Product)
                .filter(getattr(Product, attribute).in_(value))
                .all()
            )
        else:
            return (
                self.db.query(Product)
                .filter(getattr(Product, attribute) == value)
                .all()
            )

    def get_by_sku(self, sku):
        return self.db.query(Product).filter(Product.sku == sku).first()

    def get_by_skus(self, skus):
        if not skus:
            return []
        return self.db.query(Product).filter(Product.sku.in_(list(skus))).all()

    def get_by_parent_category(self, parent_category):
        return (
            self.db.query(Product)
            .filter(Product.parent_category == parent_category)
            .all()
        )

    def get_all(self):
        return self.db.query(Product).all()

    def create_bulk(self, products):
        try:
            self.db.add_all(products)
            self.db.commit()
            return products
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error creating products in bulk")
            raise

    def update_bulk(self, products):
        try:
            product_mappings = [
                {
                    "id": product.id,
                    "sku": product.sku,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "short_description": product.short_description,
                    "categories_names": product.categories_names,
                    "parent_category": product.parent_category,
                    "current_price": product.current_price,
                    "in_stock": product.in_stock,
                    "tags": product.tags,
                }
                for product in products
            ]
            self.db.bulk_update_mappings(Product, product_mappings)
            self.db.commit()
            return products
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error updating products in bulk")
            raise

    def count_products(self):
        try:
            count = self.db.query(func.count(Product.id)).scalar()
            return int(count or 0)
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error counting products")
            raise

    def list_all_skus(self):
        try:
            rows = self.db.query(Product.sku).all()
            return [sku for (sku,) in rows if sku]
        except Exception:
            self.db.rollback()
            settings.logger.exception("Error listing product skus")
            raise
