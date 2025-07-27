# backend/celery_app.py

from celery import Celery
from celery.schedules import crontab
from config import Config

celery = Celery(
    __name__,
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    include=['tasks.reminder', 'tasks.export']
)
celery.config_from_object(Config)  

celery.conf.update(
    include=["tasks.reminder", "tasks.export"],
)

celery.conf.beat_schedule = {
    "send-daily-quiz-reminders": {
        "task": "tasks.reminder.send_daily_quiz_reminders",
        "schedule": crontab(hour=7, minute=0),
    },
    "send-monthly-performance-reports": {
        "task": "tasks.reminder.send_monthly_reports",
        "schedule": crontab(day_of_month=1, hour=8, minute=0),
    },
}

def init_celery(app):
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

app = celery
