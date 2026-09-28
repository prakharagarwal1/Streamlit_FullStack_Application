"""Background task definitions (Celery-style)."""
from app.tasks.worker import app as celery_app
from app.tasks.email import send_email_task
from app.tasks.report import generate_report_task
from app.tasks.cleanup import cleanup_expired_files_task
from app.tasks.ai import summarize_text_task

__all__ = [
    "celery_app",
    "send_email_task",
    "generate_report_task",
    "cleanup_expired_files_task",
    "summarize_text_task",
]