from .celery_worker import celery
from .background_tasks.products_processing import process_products_csv_file
from .background_tasks.orders_processing import process_orders_csv_file
from .background_tasks.train_upsell_model import train_upsell_model

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
            process_products_csv_file()
        if job_name == "process_orders_file":
            process_orders_csv_file()
        if job_name == "train_upsell_model":
            train_upsell_model()
    except Exception as e:
        # Retry the task
        self.retry(exc=e)
