"""Celery application factory."""
from __future__ import annotations

from celery import Celery

from app.config import get_settings

settings = get_settings()

app = Celery(
    "streamlit_fullstack",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email",
        "app.tasks.report",
        "app.tasks.cleanup",
        "app.tasks.ai",
    ],
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_retries_on_failure=True,
    broker_connection_retry_on_startup=True,
)

app.autodiscover_tasks()