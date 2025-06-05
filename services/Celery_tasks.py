from celery import Celery
from services import metrics_analyzer
celery_app = Celery("worker", broker="redis://localhost:6379/0")
@celery_app.task
def collect_pod_utilization():
  pod_name="multi-container-resource-pod"
  namespace="kube-system"
  pod = metrics_analyzer.extract_pod_requests(pod_name=pod_name , namespace=namespace)
  print (pod)


from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "collect-every-minute": {
        "task": "services.Celery_tasks.collect_pod_utilization",
        "schedule": crontab(minute="*"),
    },


    
}
celery_app.conf.timezone = "UTC"