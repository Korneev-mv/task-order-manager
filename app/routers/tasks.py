from fastapi import Depends, HTTPException, APIRouter, Response

from app.services.task_service import *
from app.core.security import get_current_user
from app.models.schemas import TaskCreate, TaskUpdate, TaskResponse, UserTasksStats

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/")
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)) -> TaskResponse:
    user_id = current_user["id"]
    return await insert_task(user_id, task)



@router.get("/")
async def show_all_tasks(current_user: dict = Depends(get_current_user)) -> list[TaskResponse]:
    user_id = current_user["id"]
    return await get_tasks_by_user(user_id)

@router.get("/top")
async def top_5_by_tasks() -> list[UserTasksStats]:
    return await get_top_users_by_tasks(5)

@router.get("/{task_id}")
async def get_task(task_id: int, current_user: dict = Depends(get_current_user)) -> TaskResponse:
    user_id = current_user["id"]
    task = await get_task_by_id(task_id, user_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task

@router.put("/{task_id}")
async def update_task(task_id: int, task: TaskUpdate, current_user: dict = Depends(get_current_user)) -> TaskResponse:
    user_id = current_user["id"]
    return await update_task_by_id(task_id, user_id, task)

@router.delete("/{task_id}", status_code=204)
async def delete_task(task_id: int, current_user: dict = Depends(get_current_user)):
    user_id = current_user["id"]
    res = await delete_task_by_id(task_id, user_id)
    if not res:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)


