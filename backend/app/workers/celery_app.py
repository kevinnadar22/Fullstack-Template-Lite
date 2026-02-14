from typing import Any, Callable

from app.core.config import settings

try:
    from celery import Celery

    HAS_CELERY = True
except ImportError:
    HAS_CELERY = False

celery_app = None

if HAS_CELERY and settings.RABBITMQ_URL:
    celery_app = Celery(
        "tasks",
        broker=settings.RABBITMQ_URL,
        include=[],
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        task_track_started=True,
        task_acks_late=True,
        worker_prefetch_multiplier=1,
    )

    # Updated autodiscover to look in app.workers
    celery_app.autodiscover_tasks(["app.workers"])


def task(*args: Any, **kwargs: Any) -> Callable[[Callable[..., Any]], Any]:
    """
    Unified task decorator. If Celery is enabled, it uses celery_app.task.
    Otherwise, it returns a shim that executes the function synchronously when .delay() is called.
    """

    def decorator(func: Callable[..., Any]) -> Any:
        if celery_app:
            return celery_app.task(*args, **kwargs)(func)

        # Shim for .delay()
        def delay(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        func.delay = delay  # type: ignore
        return func

    return decorator
