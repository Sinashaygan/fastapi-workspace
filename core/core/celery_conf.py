import datetime

from celery import Celery
from core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL,
)

celery_app.conf.update(
    broker_connection_retry_on_startup=True,
    timezone="UTC",
    beat_schedule={
        "print-hello-every-minute": {
            "task": "core.celery_conf.print_hello",
            "schedule": 60,  # every minute
        },
    },
)


@celery_app.task
def add_number(x, y):
    return x + y

@celery_app.task
def print_hello():
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Hello Current time:{now}")