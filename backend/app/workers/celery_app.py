from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "major_compass",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    timezone="Asia/Shanghai",
)
