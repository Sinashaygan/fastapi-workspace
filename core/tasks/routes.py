from fastapi import APIRouter , Path

router = APIRouter(tags=["tasks"], prefix="/todo")


@router.get("/tasks")
async def retrieve_tasks_list():
    return []


@router.get("/tasks/{task_id}")
async def retrieve_task_by_id(task_id: int):
    return {"task_id": task_id}


@router.post("/tasks")
async def create_task():
    return []


@router.put("/tasks/{task_id}")
async def update_task(task_id: int = Path(... , gt=0)):
    return {}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int = Path(... , gt=0)):
    return {}
