from fastapi import FastAPI
from database import database, create_tables

app = FastAPI()

@app.on_event("startup")
async def startup():
    create_tables()
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
