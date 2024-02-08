from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, ForeignKey
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from sqlalchemy.sql import select
from models import UserCreate, UserInDB

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user(user: UserCreate):
    hashed_password = get_password_hash(user.password)
    query = users.insert().values(email=user.email, hashed_password=hashed_password, full_name=user.full_name, username=user.username, disabled=False)
    last_record_id = await database.execute(query)
    return {**user.model_dump(), "id": last_record_id, "hashed_password": hashed_password}

async def get_user_by_email(email: str):
    query = select([users]).where(users.c.email == email)
    return await database.fetch_one(query)

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

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
