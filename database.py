from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base  # Importing Base from models.py to use the declarative base
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from models import User, Token

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Password context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Setup the database engine
engine = create_engine(DATABASE_URL)

# Create a scoped session factory
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

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
        db_user = User(email=user.email, hashed_password=hashed_password, full_name=user.full_name, username=user.username, disabled=False)
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

async def create_user_token(db_session, user_id, token, expires_at = None):
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

async def update_user_token(db_session, user_id, token, expires_at = None):
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