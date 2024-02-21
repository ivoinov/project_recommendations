import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from passlib.context import CryptContext
from app.models import User, Token, Base, Product, Order
from config import logger, DATABASE_URL

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup the database engine
engine = create_engine(DATABASE_URL)

# Create a scoped session factory
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)


# Function to create tables, useful during application initialization
def create_tables():
    Base.metadata.create_all(bind=engine)


# Utility function to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Functions related to password hashing and verification
def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# User related functions
async def create_user(db_session, user):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            full_name=user.full_name,
            username=user.username,
            disabled=False,
        )
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)
        return db_user
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()


async def get_user_by_email(db_session, email):
    return db_session.query(User).filter(User.email == email).first()


async def create_user_token(db_session, user_id, token, expires_at=None):
    try:
        db_token = Token(token=token, user_id=user_id)
        if expires_at:
            db_token.expires_at = expires_at
        db_session.add(db_token)
        db_session.commit()
        db_session.refresh(db_token)
        return db_token
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()


async def update_user_token(db_session, user_id, token, expires_at=None):
    try:
        db_token = db_session.query(Token).filter(Token.user_id == user_id).first()
        db_token.token = token
        if expires_at:
            db_token.expires_at = expires_at
        db_session.commit()
        db_session.refresh(db_token)
        return db_token
    except:
        db_session.rollback()
        raise
    finally:
        db_session.close()


async def get_token_by_user_id(db_session, user_id):
    return db_session.query(Token).filter(Token.user_id == user_id).first()


## Product related functions
def create_or_update_product(product):
    try:
        db_session = SessionLocal()
        db_product = (
            db_session.query(Product).filter(Product.sku == product.sku).first()
        )
        if db_product is None:
            # Product does not exist, create a new one
            db_product = Product(
                sku=product.sku,
                name=product.name,
                description=product.description,
                price=product.price,
                categories_names=product.categories_names,
                current_price=product.current_price,
            )
        else:
            # Product exists, update its values
            db_product.name = product.name
            db_product.description = product.description
            db_product.price = product.price
            db_product.categories_names = product.categories_names
            db_product.current_price = product.current_price

        db_session.add(db_product)
        db_session.commit()
        db_session.refresh(db_product)
        return db_product
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating or updating product: {e}")
        raise
    finally:
        db_session.close()


# Order related functions
def create_or_update_order(order):
    try:
        db_session = SessionLocal()
        db_order = (
            db_session.query(Order)
            .filter(
                Order.increment_id == str(order.increment_id),
                Order.sku == str(order.sku),
            )
            .first()
        )
        if db_order is None:
            # Order does not exist, create a new one
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
            # Order exists, update its values
            db_order.quantity = order.quantity
            db_order.total_price = order.total_price
            db_order.item_price = order.item_price

        db_session.add(db_order)
        db_session.commit()
        db_session.refresh(db_order)
        return db_order
    except Exception as e:
        db_session.rollback()
        logger.error(f"Error creating or updating order: {e}")
        raise
    finally:
        db_session.close()


def get_orders():
    db_session = SessionLocal()
    orders = db_session.query(Order).all()
    db_session.close()
    return orders


def get_unique_customer_ids():
    db_session = SessionLocal()
    customer_ids = db_session.query(Order.customer_id).distinct().all()
    db_session.close()
    return customer_ids


def get_unique_product_skus():
    db_session = SessionLocal()
    skus = db_session.query(Order.sku).distinct().all()
    db_session.close()
    return skus
