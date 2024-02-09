from .celery_worker import celery

# Define a task
@celery.task(bind=True, max_retries=5, default_retry_delay=300)
def process_task(self, data):
    try:
        #TODO: implement logic here
        print(f"Processing task with data: {data}")
        print(f"Task ID: {self.request.id}")
        pass
    except Exception as e:
        # Retry the task
        self.retry(exc=e)
