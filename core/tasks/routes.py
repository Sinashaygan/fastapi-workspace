from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from auth.jwt_auth import get_authenticated_user
from users.models import UserModel
from tasks.shemas import *
from tasks.models import TaskModel
from sqlalchemy.orm import Session
from core.database import get_db

router = APIRouter(tags=["tasks"], prefix="/todo")


@router.get("/tasks", response_model=List[TaskResponseSchema])
async def retrieve_tasks_list(
    completed: bool = Query(
        None, description="filter tasks based on being completed or not"
    ),
    limit: int = Query(
        10, gt=0, le=50, description="limiting the number of items to retrieve"
    ),
    offset: int = Query(0, ge=0, description="use for pagination base on passed items"),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    query = db.query(TaskModel).filter_by(user_id=user.id)
    if completed is not None:
        query = query.filter_by(is_completed=completed)
    return query.limit(limit).offset(offset).all()


@router.get("/tasks/{task_id}", response_model=TaskResponseSchema)
async def retrieve_task_by_id(
    task_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    task_obj = db.query(TaskModel).filter_by(user_id=user.id, id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_obj


@router.post("/tasks", response_model=TaskResponseSchema)
async def create_task(
    request: TaskCreateSchema,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    data = request.model_dump()
    data.update({"user_id": user.id})
    task_obj = TaskModel(**data)
    db.add(task_obj)
    db.commit()
    db.refresh(task_obj)
    return task_obj


@router.put("/tasks/{task_id}", response_model=TaskResponseSchema)
async def update_task(
    request: TaskUpdateSchema,
    task_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    task_obj = db.query(TaskModel).filter_by(user_id=user.id, id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in request.model_dump(exclude_unset=True).items():
        setattr(task_obj, field, value)

    db.commit()
    db.refresh(task_obj)

    return task_obj


@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(
    task_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_authenticated_user),
):
    task_obj = db.query(TaskModel).filter_by(user_id=user.id, id=task_id).first()
    if not task_obj:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task_obj)
    db.commit()
