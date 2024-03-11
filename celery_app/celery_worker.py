from celery import Celery
import os
from app.config import settings

# Get broker URL from environment variables
broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
# Create a Celery app
celery = Celery("celery_worker", broker=broker_url)
celery.conf.update(
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
)
celery.autodiscover_tasks(["celery_app.tasks"], force=True)
