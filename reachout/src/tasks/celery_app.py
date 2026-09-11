from celery import Celery
from celery.schedules import crontab

from reachout.src.core.config import settings


celery_app = Celery(
    "reachout",
    broker=settings.RABBITMQ_URL,
    backend=f"{settings.REDIS_URL}/1"
)


celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Europe/Moscow", 
    enable_utc=True,
    task_acks_late=True, 
)


celery_app.autodiscover_tasks(["reachout.src.tasks"])


celery_app.conf.beat_schedule = {
    "daily-birthday-check": {
        "task": "src.tasks.scheduled.check_birthdays_task", 
        "schedule": crontab(hour=9, minute=0),
    }
}
