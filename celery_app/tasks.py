from .celery_worker import celery
from .background_tasks.products_processing import process_csv_file


# Define a task
@celery.task(bind=True, max_retries=5, default_retry_delay=300)
def process_task(self, data):
    try:
        if not "job_name" in data:
            print("Job name is required")
            return
        # Process the task
        print(f"Processing task: {data['job_name']}")
        job_name = data["job_name"]
        if job_name == "process_products_file":
            process_csv_file()
    except Exception as e:
        # Retry the task
        self.retry(exc=e)
