from celery import Celery
import os

# Configuration Celery
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://redis:6379/0')

celery_app = Celery(
    'notification_service',
    broker=broker_url,
    backend=result_backend,
    include=['app.workers.tasks']
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Paris',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240,  # 4 minutes soft limit
)

# Options de retry
celery_app.conf.task_routes = {
    'app.workers.tasks.send_order_confirmation_task': {'queue': 'emails'},
    'app.workers.tasks.send_welcome_email_task': {'queue': 'emails'},
    'app.workers.tasks.send_sms_task': {'queue': 'sms'},
}

print("✅ Celery app initialized")



