from fastapi import FastAPI
from typing import List

app = FastAPI()
from fastapi import HTTPException
from typing import Any
from services import metrics_analyzer

@app.get("/k8s/pod")
def get_k8s_pod() -> Any:
  pod_name="multi-container-resource-pod"
  namespace="kube-system"
  pod = metrics_analyzer.analyze_pod_resource_usage(pod_name=pod_name , namespace=namespace)
  #pod = metrics_analyzer.extract_pod_cpu_utilization(pod_name=pod_name , namespace=namespace)
  return pod

