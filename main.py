from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, recommendations
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, Token, Product, Order

app = FastAPI()

# CORS middleware configuration
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers from the routers directory
app.include_router(auth.router)
app.include_router(recommendations.router)