import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'news_portal.settings')

app = Celery('news_portal')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send_weekly_email': {
        'task': 'my_news_portal.tasks.send_weekly_email',
        'schedule': crontab(hour=8, minute=0, day_of_week='monday'),
        #'args': (5,),
    },
}