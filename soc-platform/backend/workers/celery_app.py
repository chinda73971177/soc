from celery import Celery
from celery.schedules import crontab
from core.config import settings

celery_app = Celery(
    "soc_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["workers.scan_tasks", "workers.alert_tasks"]
)

celery_app.conf.beat_schedule = {
    "quick-network-scan": {
        "task": "workers.scan_tasks.quick_scan",
        "schedule": crontab(minute="*/15"),
    },
    "process-ids-alerts": {
        "task": "workers.alert_tasks.process_ids_alerts",
        "schedule": crontab(minute="*/5"),
    },
}

celery_app.conf.timezone = "UTC"
celery_app.conf.task_serializer = "json"
celery_app.conf.result_serializer = "json"
celery_app.conf.accept_content = ["json"]
