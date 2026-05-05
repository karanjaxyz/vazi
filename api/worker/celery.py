from celery import Celery

from config import settings

celery_app = Celery(
    "vazi",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    # Serialize everything as JSON — no pickle, safe for untrusted data
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # UTC everywhere
    timezone="UTC",
    enable_utc=True,

    # Don't hold results forever — we store everything in Postgres anyway
    result_expires=3600,

    # Retry connecting to Redis on startup instead of crashing
    broker_connection_retry_on_startup=True,

    # One task at a time per worker — monitoring runs are heavy
    worker_concurrency=2,
    worker_prefetch_multiplier=1,

    # Auto-discover tasks from our tasks module
    imports=["worker.tasks"],
)
