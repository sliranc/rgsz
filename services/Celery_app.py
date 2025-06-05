from services.Celery_tasks import celery_app

# Required for Celery CLI to discover the tasks
celery = celery_app