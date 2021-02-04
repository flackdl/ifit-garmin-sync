from django.conf import settings
from sync.processor import SyncProcessor
from sync.celery import app

app.conf.beat_schedule = {
    'sync': {
        'task': 'tasks.sync',
        'schedule': 60 * 60 * settings.SYNC_HOURS,
    },
}
app.conf.timezone = 'UTC'


@app.task
def sync():
    processor = SyncProcessor()
    return processor.process()
