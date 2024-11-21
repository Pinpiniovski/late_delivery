from celery import Celery
from celery.schedules import crontab

celery_app = Celery("tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/0")

celery_app.conf.beat_schedule = {
    "fetch-all-unfulfilled-orders": {
        "task": "tasks.fetch_all_unfulfilled_orders",
        "schedule": crontab(hour="0,12"),  # Deux fois par jour
    },
    "fetch-recent-unfulfilled-orders": {
        "task": "tasks.fetch_recent_unfulfilled_orders",
        "schedule": crontab(minute="*/10"),  # Toutes les 10 minutes
    },
}
