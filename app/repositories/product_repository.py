from app.models import Product
from app.config import settings


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
            )
            self.db.add(db_product)
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except:
            self.db.rollback()
            settings.logger.exception("Error creating product")
            raise
        finally:
            self.db.close()

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
            self.db.commit()
            self.db.refresh(db_product)
            return db_product
        except:
            self.db.rollback()
            settings.logger.exception("Error updating product")
            raise
        finally:
            self.db.close()

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

    def get_all(self):
        return self.db.query(Product).all()
