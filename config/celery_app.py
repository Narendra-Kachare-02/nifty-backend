import os 
from celery import Celery
from celery.schedules import crontab
import logging

logger = logging.getLogger(__name__)

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery('property_backend')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Periodic task schedule for RERA data sync
app.conf.beat_schedule = {
    "nifty.fetch.market_hours.0915_0959": {
        "task": "nifty.fetchNifty",
        "schedule": crontab(minute="15-59/1", hour="9", day_of_week="mon-fri"),
    },
    "nifty.fetch.market_hours.10_14": {
        "task": "nifty.fetchNifty",
        "schedule": crontab(minute="*/1", hour="10-14", day_of_week="mon-fri"),
    },
    "nifty.fetch.market_hours.1500_1515": {
        "task": "nifty.fetchNifty",
        "schedule": crontab(minute="0-15/1", hour="15", day_of_week="mon-fri"),
    },
    "optionchain.fetch.market_hours.0915_0959": {
        "task": "nifty.fetchOptionChain",
        "schedule": crontab(minute="15-59/1", hour="9", day_of_week="mon-fri"),
    },
    "optionchain.fetch.market_hours.10_14": {
        "task": "nifty.fetchOptionChain",
        "schedule": crontab(minute="*/1", hour="10-14", day_of_week="mon-fri"),
    },
    "optionchain.fetch.market_hours.1500_1515": {
        "task": "nifty.fetchOptionChain",
        "schedule": crontab(minute="0-15/1", hour="15", day_of_week="mon-fri"),
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    # logger.info(f'Request: {self.request!r}')
    print(f'Request: {self.request!r}')