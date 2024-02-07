from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, recommendations
from database import create_tables, database

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
# Event handlers to manage database connection lifecycle
@app.on_event("startup")
async def startup():
    create_tables()
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Include routers from the routers directory
app.include_router(auth.router)
app.include_router(recommendations.router)
