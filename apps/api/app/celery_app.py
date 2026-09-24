from celery import Celery
from .config import get_settings

celery_app = Celery(
    "youtube_auto_editor",
    broker=get_settings().redis_url,
    backend=get_settings().redis_url,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
)
