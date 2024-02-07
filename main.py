from fastapi import FastAPI
from routers import auth, recommendations

app = FastAPI()

app.include_router(auth.router)
app.include_router(recommendations.router)
