from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, ForeignKey
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy setup for table definitions
metadata = MetaData()

users = Table(
    "users", metadata,
    Column('id', Integer, primary_key=True),
    Column('username', String(50), unique=True, index=True),
    Column('hashed_password', String(100)),
    Column('email', String(100), unique=True, index=True),
    Column('full_name', String(100)),
    Column('disabled', Boolean, default=False)
)

products = Table(
    "products", metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String(100)),
    Column('description', String(1000)),
    Column('price', Integer),
    Column('category', String(100))
)

orders = Table(
    "orders", metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', ForeignKey('users.id')),
    Column('product_id', ForeignKey('products.id')),
    Column('quantity', Integer)
)

engine = create_engine(DATABASE_URL)
database = Database(DATABASE_URL)

def create_tables():
    metadata.create_all(bind=engine)
