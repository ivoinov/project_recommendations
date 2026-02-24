import os

from fastapi import FastAPI
from redis import Redis
from redis.exceptions import RedisError

SERVICE_NAME = "recommendation-worker"
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")

app = FastAPI()


def _check_broker_ready() -> bool:
    try:
        client = Redis.from_url(BROKER_URL)
        client.ping()
        return True
    except RedisError:
        return False
    except Exception:
        return False


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": SERVICE_NAME}


@app.get("/readiness")
def readiness() -> dict:
    if _check_broker_ready():
        return {"status": "ready", "service": SERVICE_NAME}
    return {"status": "not_ready", "service": SERVICE_NAME}
