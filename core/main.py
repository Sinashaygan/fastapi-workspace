from contextlib import asynccontextmanager
import random
import time
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from auth.jwt_auth import get_authenticated_user
from users.models import UserModel
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

scheduler = AsyncIOScheduler()

def my_task():
   print(f"Task executed at {time.strftime("%Y-%n-%d %H:%H:%S")}")

tags_metadata = [
    {
        "name": "tasks",
        "description": "Operations related to task management",
        "externalDocs": {
            "description": "More about tasks",
            "url": "https://example.com/docs/tasks",
        },
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup")
    scheduler.add_job(my_task , IntervalTrigger(seconds=10))
    scheduler.start()
    yield
    scheduler.shutdown()
    print("Application shutdown")


app = FastAPI(lifespan=lifespan, openapi_tags=tags_metadata)


app.include_router(tasks_routes)
app.include_router(users_routes)


@app.get("/public")
def public_route():
    return {"message": "This is a public route."}


@app.get("/private")
def private_route(current_user: UserModel = Depends(get_authenticated_user)):
    return {"message": "This is a private route."}


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # یا استفاده از متغیر origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": exc.status_code,
        "detail": str(exc.detail),
    }
    return JSONResponse(status_code=exc.status_code, content=error_response)


@app.exception_handler(RequestValidationError)
async def http_validation_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "detail": "There was problem with your form request.",
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=error_response)


task_counter = 1


def start_task(task_id):
  print(f"doing the process: {task_id}")
  time.sleep(random.randint(3, 10))
  print(f"finished task {task_id}")


@app.get("/initiate-task", status_code=200)
async def initiate_task(background_tasks: BackgroundTasks):
  global task_counter
  background_tasks.add_task(start_task, task_id=task_counter)
  task_counter += 1
  return JSONResponse(content={"detail": "task is done"})