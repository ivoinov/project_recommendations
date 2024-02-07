from databases import Database

# Update with your actual database credentials
DATABASE_URL = "postgresql://user:password@localhost/fastapi_demo"

database = Database(DATABASE_URL)

async def connect_db():
    await database.connect()

async def disconnect_db():
    await database.disconnect()
