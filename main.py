from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recommendations, background
from app.database import SessionLocal, create_tables
from contextlib import asynccontextmanager
from celery_app.background_tasks.train_similar_model import (
    load_description_matrices,
    load_price_vector,
)
from celery_app.celery_worker import celery
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        settings.description_tfidf_matrices = load_description_matrices()
        settings.price_vector = load_price_vector()
        yield
    finally:
        pass


app = FastAPI(lifespan=lifespan)
# Include routers from the routers directory
app.include_router(auth.router)
app.include_router(recommendations.router)
app.include_router(background.router)

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
create_tables()
