from celery import Celery

# Create a Celery app
celery = Celery("celery_worker", broker="redis://localhost:6379/0")
celery.conf.update(
    broker_connection_retry=True,
    broker_connection_retry_on_startup=True,
)
celery.autodiscover_tasks(["celery_app.tasks"], force=True)
