from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def background_task(job_name: str):
    # TODO: Implement processing for different data: products, orders, etc from files to DB
    pass


@router.post("/execute-background-task/")
async def execute_background_task(
    job_name: str,
    background_tasks: BackgroundTasks,
    token: str = Depends(oauth2_scheme),
):
    background_tasks.add_task(background_task, job_name)
    return {"message": "Background task enqueued"}
