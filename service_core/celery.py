import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service_core.settings')  # prod veya base olabilir

app = Celery('service_core')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Django app’lerindeki tasks.py dosyalarını otomatik bulsun
app.autodiscover_tasks()
