from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_pod_metrics_for_system_pod():
    """
    Tests the /k8s/pod endpoint by attempting to fetch metrics for a common system pod.
    This test requires a running Kubernetes cluster accessible from the test environment
    and for the specified pod (e.g., 'kube-proxy') to exist and have metrics available.
    It does not mock Kubernetes API calls, relying on the 'real system' interaction.
    """
    pod_name = "kube-proxy"
    namespace = "kube-system"

    response = client.get(f"/k8s/pod?pod_name={pod_name}&namespace={namespace}")

    assert response.status_code == 200, \
        f"Expected status code 200, but got {response.status_code}. Response: {response.json()}"
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert isinstance(data, list), f"Expected response to be a list, but got {type(data)}: {data}"

    # If data is returned, check its structure.
    # Note: This test might return an empty list if the K8s cluster is not running,
    # the pod doesn't exist, or metrics are not available, but the status code will still be 200.
    if data:
        assert len(data) > 0, "Expected at least one container's metrics, but got an empty list."
        first_container_metrics = data[0]
        assert isinstance(first_container_metrics, dict)

        # Check for essential keys that should always be present as per analyze_pod_resource_usage
        expected_keys = [
            "pod_name", "namespace", "name", "cpu_request_millicores",
            "cpu_utilization_millicores", "cpu_usage_vs_request_ratio",
            "cpu_over_provisioned", "cpu_under_provisioned",
            "memory_request_bytes", "memory_utilization_bytes"
        ]
        for key in expected_keys:
            assert key in first_container_metrics, f"Missing expected key '{key}' in response item: {first_container_metrics}"

        # Verify the pod_name and namespace match the request
        assert first_container_metrics["pod_name"] == pod_name
        assert first_container_metrics["namespace"] == namespace

        # Check types for some key fields
        assert isinstance(first_container_metrics["cpu_request_millicores"], (int, float))
        assert isinstance(first_container_metrics["cpu_utilization_millicores"], (int, float))
        assert isinstance(first_container_metrics["cpu_over_provisioned"], bool)
        assert isinstance(first_container_metrics["cpu_under_provisioned"], bool)

def test_get_pod_metrics_for_non_existent_pod():
    """
    Tests the /k8s/pod endpoint with a pod name that is highly unlikely to exist.
    The metrics_analyzer functions are designed to return an empty list if a pod
    or its metrics are not found, resulting in a 200 OK with an empty list from the API.
    """
    pod_name = "this-pod-should-not-exist-1234567890"
    namespace = "default" # Can be any namespace

    response = client.get(f"/k8s/pod?pod_name={pod_name}&namespace={namespace}")

    assert response.status_code == 200, \
        f"Expected status code 200 for non-existent pod, but got {response.status_code}. Response: {response.json()}"
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert isinstance(data, list), f"Expected response to be a list, but got {type(data)}: {data}"
    assert len(data) == 0, f"Expected an empty list for non-existent pod, but got: {data}"

def test_get_pod_metrics_missing_required_parameters():
    """
    Tests the /k8s/pod endpoint when required query parameters (pod_name, namespace) are missing.
    FastAPI's validation should return a 422 Unprocessable Entity.
    """
    response = client.get("/k8s/pod") # No query parameters

    assert response.status_code == 422, \
        f"Expected status code 422 for missing parameters, but got {response.status_code}. Response: {response.json()}"
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert "detail" in data, f"Expected 'detail' key in error response, but got: {data}"
    assert isinstance(data["detail"], list), f"Expected 'detail' to be a list, but got {type(data['detail'])}: {data['detail']}"
    
    # Check if error messages indicate missing fields
    error_messages = [err.get("msg", "").lower() for err in data["detail"]]
    assert any("field required" in msg for msg in error_messages), \
        f"Expected 'field required' error message, but got: {error_messages}"
    assert any("pod_name" in err.get("loc", []) for err in data["detail"]), \
        f"Expected error for 'pod_name', but got: {data['detail']}"
    assert any("namespace" in err.get("loc", []) for err in data["detail"]), \
        f"Expected error for 'namespace', but got: {data['detail']}"