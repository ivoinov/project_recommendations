from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.config import db_settings, settings
import redis
import os

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    """Basic health check - no authentication required"""
    return {"status": "healthy", "service": "recommendation-api"}


@router.get("/readiness")
async def readiness_check(db: Session = Depends(db_settings.get_db)):
    """Readiness check - verifies dependencies"""
    checks = {"database": "unknown", "redis": "unknown"}

    # Check database
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"

    # Check Redis
    try:
        redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        # Parse redis URL to get host and port
        redis_host = redis_url.split("://")[1].split(":")[0]
        redis_port = int(redis_url.split(":")[-1].split("/")[0])
        r = redis.Redis(host=redis_host, port=redis_port, db=0, socket_timeout=2)
        r.ping()
        checks["redis"] = "healthy"
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"

    all_healthy = all(v == "healthy" for v in checks.values())

    return {"status": "ready" if all_healthy else "not_ready", "checks": checks}
