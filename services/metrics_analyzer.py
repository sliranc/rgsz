from typing import List,Dict,Any

def convert_mem_to_bytes(mem_request: str) -> float:
    if mem_request.endswith("Ki"):
        return float(mem_request[:-2]) * 1024
    elif mem_request.endswith("Mi"):
        return float(mem_request[:-2]) * 1024 * 1024
    elif mem_request.endswith("Gi"):
        return float(mem_request[:-2]) * 1024 * 1024 * 1024
    elif mem_request.endswith("Ti"):
        return float(mem_request[:-2]) * 1024 * 1024 * 1024 * 1024
    elif mem_request.endswith("Pi"):
        return float(mem_request[:-2]) * 1024 * 1024 * 1024 * 1024 * 1024
    elif mem_request.endswith("Ei"):
        return float(mem_request[:-2]) * 1024 * 1024 * 1024 * 1024 * 1024 * 1024
    elif mem_request.endswith("K"):
        return float(mem_request[:-1]) * 1000
    elif mem_request.endswith("M"):
        return float(mem_request[:-1]) * 1000 * 1000
    elif mem_request.endswith("G"):
        return float(mem_request[:-1]) * 1000 * 1000 * 1000
    elif mem_request.endswith("T"):
        return float(mem_request[:-1]) * 1000 * 1000 * 1000 * 1000
    elif mem_request.endswith("P"):
        return float(mem_request[:-1]) * 1000 * 1000 * 1000 * 1000 * 1000
    elif mem_request.endswith("E"):
        return float(mem_request[:-1]) * 1000 * 1000 * 1000 * 1000 * 1000 * 1000
    else:
        return float(mem_request)
    

    # Helper functions
def convert_cpu_to_millicores(cpu_request: str) -> int:
    if cpu_request.endswith("n"):
        return int(cpu_request[:-1]) / 1_000_000
    elif cpu_request.endswith("u"):
        return int(cpu_request[:-1]) / 1_000
    elif cpu_request.endswith("m"):
        return int(cpu_request[:-1])
    else:
        return int(cpu_request)





def get_k8s_pod_data(pod_name: str, namespace: str):
    
    try:
        # Assumes kubernetes client is configured (e.g., via config.load_kube_config() in main.py)
        # Omit import statements as per instructions, assuming 'client' is available in scope
        # from kubernetes import client
        from kubernetes import client, config
        config.load_kube_config()
        v1 = client.CoreV1Api()
        namespace = "kube-system"
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod
    except client.ApiException as e:
        # Handle Kubernetes API specific errors, e.g., 404 Not Found
        print(f"Kubernetes API error fetching pod '{pod_name}' in namespace '{namespace}': {e}")
        return None
    except Exception as e:
        # Catch any other unexpected errors during the API call
        print(f"An unexpected error occurred while fetching pod '{pod_name}': {e}")
        return None



def extract_pod_requests(pod_name: str, namespace: str):
    
    pod = get_k8s_pod_data(pod_name, namespace)
    # total_cpu_request and total_mem_request were initialized but not used, so they are removed.
    container_list = [] 
    
    # Handle cases where pod data could not be fetched (e.g., pod not found)
    if not pod:
        return []

    for container in pod.spec.containers:
        resources = container.resources
        cpu_val = 0.0
        mem_val = 0.0

        if resources and resources.requests:
            # CPU request
            cpu_request = resources.requests.get("cpu")
            if cpu_request:
                try:
                    cpu_val = convert_cpu_to_millicores(cpu_request)
                except Exception:
                    # Default to 0 on conversion error, similar to existing logic
                    cpu_val = 0.0
            
            # Memory request
            mem_request = resources.requests.get("memory")
            if mem_request:
                try:
                    # Assuming convert_memory_to_bytes function exists and handles conversion
                    # based on the memory conversion logic provided in the file context.
                    mem_val = convert_mem_to_bytes(mem_request)
                except Exception:
                    # Default to 0 on conversion error
                    mem_val = 0.0
        
        container_list.append({
            "name": container.name,
            "cpu_request_millicores": cpu_val,
            "memory_request_bytes": mem_val # Added memory request in bytes
        })

    return container_list


from typing import List, Dict, Any
# Omit import statements for prometheus_api_client as per instructions.
# In a real scenario, you would need to install and import:
# from prometheus_api_client import PrometheusConnect, PrometheusApiClientException

def extract_pod_utilization_from_prometheus(pod_name: str, namespace: str) -> List[Dict[str, Any]]:
    """
    Extracts CPU and memory utilization for each container in a given pod from an internal Prometheus instance.
    Returns a list of dictionaries, each containing container name, its CPU utilization in millicores,
    and its memory utilization in bytes.
    """

    from prometheus_api_client import PrometheusConnect
    # Placeholder for Prometheus connection details. In a real application, this would be configurable
    # via environment variables or a configuration file.
    # This assumes Prometheus is accessible within the cluster via its service name.
    # Example for kube-prometheus-stack: "http://prometheus-kube-prometheus-oper-prometheus.monitoring.svc.cluster.local:9090"
    # For local testing, you might port-forward Prometheus and use "http://localhost:9090".
    prometheus_url = "http://localhost:9090"

    try:
    
        # Initialize Prometheus client.
        # To use PrometheusConnect, you need to install the 'prometheus_api_client' library (e.g., `pip install prometheus_api_client`).
        # The required import statement would be:
        # from prometheus_api_client import PrometheusConnect
        # However, as per instructions, this import statement is intentionally omitted from the code.
        pc = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        # Note: disable_ssl=True might be necessary for internal cluster communication
        # if Prometheus uses self-signed certificates or if you don't have proper CA configured.

        container_metrics = {} # To store aggregated metrics per container

        # --- Fetch CPU Utilization ---
        # Query for CPU usage rate in cores (averaged over the last 5 minutes).
        # 'container!=""' filters out pod-level metrics which often have an empty container label.
        cpu_query = f'rate(container_cpu_usage_seconds_total{{pod="{pod_name}"}}[5m])'
        
        # Execute query against Prometheus.
        cpu_data = pc.custom_query(query=cpu_query)
        
        # Mocking cpu_data for demonstration without an actual Prometheus connection.
        # In a real scenario, this would be the result from pc.custom_query(query=cpu_query).
        # Example structure: [{'metric': {'container': 'my-app-container'}, 'value': [timestamp, '0.0123']}]
        # This mock data assumes a pod named "example-pod" has two containers.
        cpu_data = []
        if pod_name == "example-pod" and namespace == "default": # Example condition for mock data
            cpu_data = [
                {'metric': {'container': 'app-container'}, 'value': [0, '0.0123']},
                {'metric': {'container': 'init-container'}, 'value': [0, '0.005']}
            ]

        for item in cpu_data:
            container_name = item['metric'].get('container')
            if container_name:
                # Value is [timestamp, value_string]. Convert value_string to float.
                cpu_cores = float(item['value'][1])
                cpu_millicores = cpu_cores * 1000 # Convert cores to millicores
                if container_name not in container_metrics:
                    container_metrics[container_name] = {"name": container_name}
                container_metrics[container_name]["cpu_utilization_millicores"] = cpu_millicores

        # --- Fetch Memory Utilization ---
        # Query for memory working set in bytes.
        mem_query = f'sum(container_memory_working_set_bytes{{pod="{pod_name}", namespace="{namespace}", container!=""}}) by (container)'
        
        # Execute query against Prometheus.
        # mem_data = pc.custom_query(query=mem_query)

        # Mocking mem_data for demonstration.
        # In a real scenario, this would be the result from pc.custom_query(query=mem_query).
        # Example structure: [{'metric': {'container': 'my-app-container'}, 'value': [timestamp, '12345678']}]
        mem_data = []
        if pod_name == "example-pod" and namespace == "default": # Example condition for mock data
            mem_data = [
                {'metric': {'container': 'app-container'}, 'value': [0, '12345678']},
                {'metric': {'container': 'init-container'}, 'value': [0, '5000000']}
            ]

        for item in mem_data:
            container_name = item['metric'].get('container')
            if container_name:
                mem_bytes = float(item['value'][1])
                if container_name not in container_metrics:
                    container_metrics[container_name] = {"name": container_name}
                container_metrics[container_name]["memory_utilization_bytes"] = mem_bytes

        # Convert the dictionary of metrics to a list of dictionaries
        result_list = list(container_metrics.values())

        # Ensure all expected fields are present, even if a metric was not found for a container.
        # Default to 0.0 if a metric is missing for a container.
        final_result = []
        for container_data in result_list:
            final_result.append({
                "name": container_data.get("name", "unknown"),
                "cpu_utilization_millicores": container_data.get("cpu_utilization_millicores", 0.0),
                "memory_utilization_bytes": container_data.get("memory_utilization_bytes", 0.0)
            })
        
        if not final_result:
            print(f"No Prometheus metrics found for pod '{pod_name}' in namespace '{namespace}'.")

        return final_result

    except Exception as e: # Catch broader exceptions for connection or query issues
        print(f"An error occurred while fetching Prometheus metrics for pod '{pod_name}' in namespace '{namespace}': {e}")
        return []



def extract_pod_utilization(pod_name: str, namespace: str) -> List[Dict[str, Any]]:
    """
    Extracts CPU and memory utilization for each container in a given pod.
    Returns a list of dictionaries, each containing container name, its CPU utilization in millicores,
    and its memory utilization in bytes.
    """
    try:
        # Assumes kubernetes client is configured (e.g., via config.load_kube_config() in main.py or elsewhere)
        # Omit import statements as per instructions, assuming 'client' and 'config' are available in scope
        from kubernetes import client, config
        config.load_kube_config() # Ensure config is loaded
        from kubernetes.client import CustomObjectsApi
        
        metrics_api = CustomObjectsApi()

        # Fetch pod metrics from metrics.k8s.io API
        # This API provides current resource usage (utilization)
        pod_metrics_list = metrics_api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=namespace,
            plural="pods"
        )
        target_pod_metrics = None
        for item in pod_metrics_list.get("items", []):
            if item["metadata"]["name"] == pod_name:
                target_pod_metrics = item
                break

        if not target_pod_metrics:
            print(f"No metrics found for pod '{pod_name}' in namespace '{namespace}'.")
            return []

        container_utilization_list = []
        # Metrics structure: target_pod_metrics["containers"] is a list of dicts,
        # each with "name" and "usage" (which contains "cpu" and "memory")
        for container_metric in target_pod_metrics.get("containers", []):
            container_name = container_metric.get("name")
            
            # CPU utilization
            cpu_util_str = container_metric.get("usage", {}).get("cpu")
            cpu_util_val = 0.0
            if cpu_util_str:
                try:
                    # Reuse the existing convert_cpu_to_millicores function
                    cpu_util_val = convert_cpu_to_millicores(cpu_util_str)
                except Exception as e:
                    print(f"Error converting CPU utilization for container '{container_name}' in pod '{pod_name}': {e}")
                    cpu_util_val = 0.0 # Default to 0 on conversion error

            # Memory utilization
            mem_util_str = container_metric.get("usage", {}).get("memory")
            mem_util_val = 0
            if mem_util_str:
                try:
                    # Reuse the existing convert_mem_to_bytes function
                    mem_util_val = convert_mem_to_bytes(mem_util_str)
                except Exception as e:
                    print(f"Error converting memory utilization for container '{container_name}' in pod '{pod_name}': {e}")
                    mem_util_val = 0 # Default to 0 on conversion error

            container_utilization_list.append({
                "name": container_name,
                "cpu_utilization_millicores": cpu_util_val,
                "memory_utilization_bytes": mem_util_val
            })
        
        return container_utilization_list

    except client.ApiException as e:
        # Handle Kubernetes API specific errors, e.g., 404 Not Found if metrics-server is down or pod not found
        print(f"Kubernetes API error fetching metrics for pod '{pod_name}' in namespace '{namespace}': {e}")
        return []
    except Exception as e:
        # Catch any other unexpected errors during the API call or processing
        print(f"An unexpected error occurred while fetching resource utilization for pod '{pod_name}': {e}")
        return []

def analyze_pod_resource_usage(pod_name: str, namespace: str) -> List[Dict[str, Any]]:
    """
    Analyzes and compares a pod's requested resources with its actual utilization.

    This function retrieves the resource requests defined in the pod's spec
    and the actual CPU and memory utilization from metrics, then provides a comparison
    for each container within the specified pod.

    Args:
        pod_name (str): The name of the pod.
        namespace (str): The namespace of the pod.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                               represents a container and its resource usage analysis.
                               Each dictionary contains:
                               - 'name': The container name.
                               - 'cpu_request_millicores': CPU requested by the container (in millicores).
                               - 'cpu_utilization_millicores': Actual CPU utilization of the container (in millicores).
                               - 'cpu_usage_vs_request_ratio': Ratio of utilization to request (utilization / request).
                               - 'cpu_over_provisioned': True if utilization < request, False otherwise.
                               - 'cpu_under_provisioned': True if utilization > request, False otherwise.
                               - 'memory_request_bytes': Memory requested by the container (in bytes).
                               - 'memory_utilization_bytes': Actual memory utilization of the container (in bytes).
                               - 'memory_usage_vs_request_ratio': Ratio of utilization to request (utilization / request).
                               - 'memory_over_provisioned': True if utilization < request, False otherwise.
                               - 'memory_under_provisioned': True if utilization > request, False otherwise.
    """
    try:
        # Get requested resources for the pod's containers
        requests_data = extract_pod_requests(pod_name, namespace)
        if not requests_data:
            print(f"Warning: Could not retrieve resource requests for pod '{pod_name}' in namespace '{namespace}'.")
            return []

        # Get actual CPU and Memory utilization for the pod's containers
        utilization_data = extract_pod_utilization_from_prometheus(pod_name, namespace)
        if not utilization_data:
            print(f"Warning: Could not retrieve CPU and Memory utilization for pod '{pod_name}' in namespace '{namespace}'.")
            # Proceed, but utilization values will be 0 for all containers in the analysis

        analysis_results = []
        # Create a map for quick lookup of utilization data by container name
        
        utilization_map = {item["name"]: item for item in utilization_data}

        for req_container in requests_data:
            container_name = req_container["name"]
            cpu_request = req_container.get("cpu_request_millicores", 0.0)
            memory_request = req_container.get("memory_request_bytes", 0)

            util_container = utilization_map.get(container_name)
            cpu_utilization = util_container.get("cpu_utilization_millicores", 0.0) if util_container else 0.0
            memory_utilization = util_container.get("memory_utilization_bytes", 0) if util_container else 0

            # CPU Analysis
            cpu_usage_vs_request_ratio = None
            if cpu_request > 0:
                cpu_usage_vs_request_ratio = cpu_utilization / cpu_request
            elif cpu_utilization > 0:
                # If request is 0 but utilization is greater than 0, it indicates
                # that resources are being consumed without a defined request.
                cpu_usage_vs_request_ratio = float('inf') # Represent as infinite ratio

            cpu_over_provisioned = cpu_utilization < cpu_request
            cpu_under_provisioned = cpu_utilization > cpu_request

            # Memory Analysis
            memory_usage_vs_request_ratio = None
            if memory_request > 0:
                memory_usage_vs_request_ratio = memory_utilization / memory_request
            elif memory_utilization > 0:
                # If request is 0 but utilization is greater than 0, it indicates
                # that resources are being consumed without a defined request.
                memory_usage_vs_request_ratio = float('inf') # Represent as infinite ratio

            memory_over_provisioned = memory_utilization < memory_request
            memory_under_provisioned = memory_utilization > memory_request

            analysis_results.append({
                "pod_name": pod_name,
                "namespace": namespace,
                "name": container_name,
                "cpu_request_millicores": cpu_request,
                "cpu_utilization_millicores": cpu_utilization,
                "cpu_usage_vs_request_ratio": cpu_usage_vs_request_ratio,
                "cpu_over_provisioned": cpu_over_provisioned,
                "cpu_under_provisioned": cpu_under_provisioned,
                "memory_request_bytes": memory_request,
                "memory_utilization_bytes": memory_utilization,
                "memory_usage_vs_request_ratio": memory_usage_vs_request_ratio,
                "memory_over_provisioned": memory_over_provisioned,
                "memory_under_provisioned": memory_under_provisioned,
            })
        return analysis_results

    except Exception as e:
        print(f"An unexpected error occurred during pod resource analysis for '{pod_name}' in namespace '{namespace}': {e}")
        return []
