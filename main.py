from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, recommendations, background
from app.database import SessionLocal, create_tables

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
create_tables()


# Include routers from the routers directory
app.include_router(auth.router)
app.include_router(recommendations.router)
app.include_router(background.router)
