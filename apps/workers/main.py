import os
from celery import Celery
import structlog

from .config import settings
from .tasks import vault_processing


logger = structlog.get_logger()

# Create Celery app
celery_app = Celery(
    "secondbrain-workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "apps.workers.tasks.vault_processing",
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    result_expires=3600,
)

# Task routing
celery_app.conf.task_routes = {
    "apps.workers.tasks.vault_processing.process_vault": {"queue": "vault_processing"},
    "apps.workers.tasks.vault_processing.extract_vault_files": {"queue": "vault_processing"},
    "apps.workers.tasks.vault_processing.analyze_vault_content": {"queue": "vault_processing"},
}

# Configure logging
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks."""
    # Add periodic tasks here if needed
    pass


@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing."""
    logger.info("Debug task called", task_id=self.request.id)
    return f"Request: {self.request!r}"


if __name__ == "__main__":
    celery_app.start()