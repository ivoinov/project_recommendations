from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordBearer
from celery_app.tasks import process_task

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.post("/execute-background-task/")
async def execute_background_task(
    job_name: str,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme),
):
    background_tasks.add_task(process_task.delay, 123)
    return {"message": "Background task enqueued"}
