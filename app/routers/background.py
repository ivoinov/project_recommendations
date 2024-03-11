from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordBearer
from celery_app.tasks import process_task

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")


@router.post("/execute-background-task/")
async def execute_background_task(
    job_name: str,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme),
):
    # Enqueue the background task
    background_tasks.add_task(process_task.delay, {"job_name": job_name})
    return {"message": "Background task enqueued"}
