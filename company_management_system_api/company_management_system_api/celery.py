import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_management_system_api.settings')

app = Celery('company_management_system_api')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'count-vehicle-every-hour': {
        'task': 'api.tasks.count_vehicle',
        'schedule': crontab(hour='*/1')
    },
    'send-report-of-vehicle-count': {
        'task': 'api.tasks.send_vehicle_report',
        'schedule': crontab(hour=8, day_of_week='friday')
    }
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks()
