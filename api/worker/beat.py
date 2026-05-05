from celery.schedules import crontab

from .celery import celery_app

celery_app.conf.beat_schedule = {
    # Every hour, check which projects are due for a monitoring run
    "check-due-projects": {
        "task": "worker.tasks.check_due_projects",
        "schedule": crontab(minute=0),  # top of every hour
    },

    # Daily at 9am UTC — send weekly digest emails for completed runs
    "send-weekly-digests": {
        "task": "worker.tasks.send_weekly_digests",
        "schedule": crontab(hour=9, minute=0, day_of_week="monday"),
    },
}
