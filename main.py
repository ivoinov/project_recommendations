import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import auth, recommendations, background, health
from contextlib import asynccontextmanager
from celery_app.background_tasks.train_similar_model import (
    load_description_matrices,
    load_price_vectors,
)
from celery_app.celery_worker import celery
from app.config import settings


# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        settings.description_tfidf_matrices = load_description_matrices()
        settings.price_vectors = load_price_vectors()
        yield
    finally:
        pass


app = FastAPI(lifespan=lifespan)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include routers from the routers directory
app.include_router(auth.router)
app.include_router(recommendations.router)
app.include_router(background.router)
app.include_router(health.router)

# CORS middleware configuration - environment-based
environment = os.getenv("ENVIRONMENT", "development")

if environment == "production":
    # Restrict origins in production - update with your actual domains
    allowed_origins = [
        os.getenv("ALLOWED_ORIGIN", "https://yourdomain.com"),
    ]
    # Filter out empty strings
    allowed_origins = [o for o in allowed_origins if o]
else:
    # Allow all in development
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Declare the Celery app
celery_app = celery
