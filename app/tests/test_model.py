import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base, User, Token, Product, Order, ProductRecommendation

engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def db():
    return next(get_db())


def test_create_and_query_user(db: Session):
    user = User(username="test", hashed_password="test", email="test@test.com")
    db.add(user)
    db.commit()
    user_from_db = db.query(User).filter(User.username == "test").first()
    assert user_from_db.username == "test"


def test_create_and_query_token(db: Session):
    token = Token(token="test_token", user_id=1)
    db.add(token)
    db.commit()
    token_from_db = db.query(Token).filter(Token.token == "test_token").first()
    assert token_from_db.token == "test_token"


def test_create_and_query_product(db: Session):
    product = Product(
        id=1,
        sku="test_sku",
        name="test_product",
        description="test_description",
        price=100,
        categories_names="test_category",
        current_price=100,
    )
    db.add(product)
    db.commit()
    product_from_db = db.query(Product).filter(Product.name == "test_product").first()
    assert product_from_db.name == "test_product"


def test_create_and_query_order(db: Session):
    order = Order(
        id=1,
        sku="test_sku",
        quantity=10,
        product_name="test_product",
        total_price=1000,
        item_price=100,
    )
    db.add(order)
    db.commit()
    order_from_db = db.query(Order).filter(Order.sku == "test_sku").first()
    assert order_from_db.sku == "test_sku"


def test_product_recommendation():
    product_recommendation = ProductRecommendation(product_id=1, recommendations=[2, 3])
    assert product_recommendation.product_id == 1
    assert product_recommendation.recommendations == [2, 3]
