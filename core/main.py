from contextlib import asynccontextmanager
import logging
import random
import time
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
import httpx
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from auth.jwt_auth import get_authenticated_user
from core.celery_config import add_number
from core.config import settings
from core.email_util import send_email
from users.models import UserModel
from tasks.routes import router as tasks_routes
from users.routes import router as users_routes
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.triggers.interval import IntervalTrigger
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

redis = aioredis.from_url(settings.REDIS_URL)
cache_backend = RedisBackend(redis)
FastAPICache.init(cache_backend, prefix="fastapi-cache")


# Initialize Redis Job store for APScheduler:
jobstores = {
    "default": RedisJobStore(
        jobs_key="apscheduler.jobs",
        run_times_key="apscheduler.run_times",
        host="redis",
        port=6379,
        db=1,
    )
}

scheduler = AsyncIOScheduler(jobstores=jobstores)


def my_task():
    logger.info(
        "Task executed at %s",
        time.strftime("%Y-%m-%d %H:%M:%S"),
    )


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
    logger.info("Application startup")

    scheduler.add_job(
        my_task,
        IntervalTrigger(seconds=10),
        id="my_task",
        replace_existing=True,
    )
    scheduler.start()

    yield

    scheduler.shutdown()
    logger.info("Application shutdown")


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
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, content=error_response
    )


task_counter = 1


def start_task(task_id):
    logger.info("Doing the process: %s", task_id)
    time.sleep(random.randint(3, 10))
    logger.info("Finished task %s", task_id)


async def request_current_weather(latitude: float, longitude: float):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.json().get("current_weather")
        except Exception:
            pass
    return None


@app.get("/initiate-task", status_code=200)
async def initiate_task(background_tasks: BackgroundTasks):
    global task_counter
    background_tasks.add_task(start_task, task_id=task_counter)
    task_counter += 1
    return JSONResponse(content={"detail": "task is done"})


@app.get("/fetch-tehran-weather", status_code=200)
@cache(expire=30)  # کش کردن پاسخ به مدت ۳۰ ثانیه در ردیس
async def fetch_tehran_weather():
    # مختصات تهران: عرض ۳۵.۶۸۹۲ و طول ۵۱.۳۸۹۰
    latitude = 35.6892
    longitude = 51.3890

    current_weather = await request_current_weather(latitude, longitude)

    if current_weather:
        return JSONResponse(
            content={"city": "Tehran", "current_weather": current_weather}
        )
    else:
        return JSONResponse(
            content={"detail": "Failed to fetch weather"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@app.get("/send-mail", status_code=200)
async def test_send_mail():
    await send_email(
        subject="Test Email from FastAPI",
        recipients=["recipient@example.com"],
        body="This is a test email sent using the email_util function.",
    )
    return JSONResponse(content={"detail": "Email has been sent"})


@app.get("initiate-celery-tasks", status_code=200)
async def initiate_celery_tasks():
    add_number.delay(1, 2)
    return JSONResponse(content={"detail": "task is done"})
