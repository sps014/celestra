"""
WaitCondition class for sophisticated wait conditions in Celestraa DSL.

This module provides advanced wait conditions for deployment orchestration,
including resource readiness, custom conditions, and complex dependencies.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from ..core.base_builder import BaseBuilder


class WaitType(Enum):
    """Types of wait conditions."""
    RESOURCE_READY = "resource_ready"
    CONDITION_MET = "condition_met"
    HTTP_SUCCESS = "http_success"
    TCP_CONNECT = "tcp_connect"
    CUSTOM_COMMAND = "custom_command"
    LOG_PATTERN = "log_pattern"
    METRIC_THRESHOLD = "metric_threshold"


class WaitCondition(BaseBuilder):
    """
    Builder class for sophisticated wait conditions.
    
    Provides advanced wait conditions for orchestrating complex deployments
    with dependencies, custom checks, and conditional logic.
    
    Example:
        ```python
        wait = (WaitCondition("app-wait")
            .wait_for_pod_ready("user-service", namespace="default")
            .wait_for_http_success("http://auth-service/health")
            .wait_for_metric("cpu_usage < 80")
            .set_timeout("10m")
            .enable_parallel_checks())
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the WaitCondition builder.
        
        Args:
            name: Name of the wait condition
        """
        super().__init__(name)
        self._wait_conditions: List[Dict[str, Any]] = []
        self._timeout: str = "5m"
        self._parallel_execution: bool = False
        self._failure_policy: str = "fail_fast"
        self._retry_config: Dict[str, Any] = {}
        self._success_threshold: int = 1
        self._failure_threshold: int = 3
    
    def wait_for_pod_ready(
        self,
        name: str,
        namespace: Optional[str] = None,
        selector: Optional[Dict[str, str]] = None,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for pod(s) to be ready.
        
        Args:
            name: Pod name or label selector
            namespace: Pod namespace
            selector: Label selector for pods
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.RESOURCE_READY.value,
            "resource": "pod",
            "name": name,
            "namespace": namespace or self._namespace,
            "selector": selector,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_service_ready(
        self,
        name: str,
        namespace: Optional[str] = None,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for service to be ready.
        
        Args:
            name: Service name
            namespace: Service namespace
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.RESOURCE_READY.value,
            "resource": "service",
            "name": name,
            "namespace": namespace or self._namespace,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_deployment_ready(
        self,
        name: str,
        namespace: Optional[str] = None,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for deployment to be ready.
        
        Args:
            name: Deployment name
            namespace: Deployment namespace
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.RESOURCE_READY.value,
            "resource": "deployment",
            "name": name,
            "namespace": namespace or self._namespace,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_http_success(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        expected_status: int = 200,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for HTTP endpoint to return success.
        
        Args:
            url: URL to check
            method: HTTP method
            headers: Request headers
            expected_status: Expected HTTP status code
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.HTTP_SUCCESS.value,
            "url": url,
            "method": method,
            "headers": headers or {},
            "expected_status": expected_status,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_tcp_connect(
        self,
        host: str,
        port: int,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for TCP connection to be successful.
        
        Args:
            host: Host to connect to
            port: Port to connect to
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.TCP_CONNECT.value,
            "host": host,
            "port": port,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_custom_command(
        self,
        command: List[str],
        expected_exit_code: int = 0,
        timeout: Optional[str] = None,
        description: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for custom command to succeed.
        
        Args:
            command: Command to execute
            expected_exit_code: Expected exit code
            timeout: Wait timeout
            description: Description of the check
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.CUSTOM_COMMAND.value,
            "command": command,
            "expected_exit_code": expected_exit_code,
            "timeout": timeout or self._timeout,
            "description": description
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_log_pattern(
        self,
        resource_name: str,
        pattern: str,
        namespace: Optional[str] = None,
        container: Optional[str] = None,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for log pattern to appear.
        
        Args:
            resource_name: Name of the resource (pod/deployment)
            pattern: Log pattern to match
            namespace: Resource namespace
            container: Container name (for pods with multiple containers)
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.LOG_PATTERN.value,
            "resource_name": resource_name,
            "pattern": pattern,
            "namespace": namespace or self._namespace,
            "container": container,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_metric_threshold(
        self,
        metric_query: str,
        threshold: float,
        comparison: str = ">=",
        prometheus_url: str = "http://prometheus:9090",
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for metric to meet threshold.
        
        Args:
            metric_query: Prometheus metric query
            threshold: Threshold value
            comparison: Comparison operator (>=, <=, ==, !=, >, <)
            prometheus_url: Prometheus server URL
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.METRIC_THRESHOLD.value,
            "metric_query": metric_query,
            "threshold": threshold,
            "comparison": comparison,
            "prometheus_url": prometheus_url,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def wait_for_condition(
        self,
        resource_type: str,
        resource_name: str,
        condition_type: str,
        status: str = "True",
        namespace: Optional[str] = None,
        timeout: Optional[str] = None
    ) -> "WaitCondition":
        """
        Wait for Kubernetes resource condition.
        
        Args:
            resource_type: Type of resource (deployment, pod, etc.)
            resource_name: Name of the resource
            condition_type: Type of condition to wait for
            status: Expected condition status
            namespace: Resource namespace
            timeout: Wait timeout
            
        Returns:
            WaitCondition: Self for method chaining
        """
        condition = {
            "type": WaitType.CONDITION_MET.value,
            "resource_type": resource_type,
            "resource_name": resource_name,
            "condition_type": condition_type,
            "status": status,
            "namespace": namespace or self._namespace,
            "timeout": timeout or self._timeout
        }
        self._wait_conditions.append(condition)
        return self
    
    def set_timeout(self, timeout: str) -> "WaitCondition":
        """
        Set global timeout for wait conditions.
        
        Args:
            timeout: Timeout duration (e.g., "10m", "30s")
            
        Returns:
            WaitCondition: Self for method chaining
        """
        self._timeout = timeout
        return self
    
    def enable_parallel_checks(self, enabled: bool = True) -> "WaitCondition":
        """
        Enable parallel execution of wait conditions.
        
        Args:
            enabled: Whether to enable parallel execution
            
        Returns:
            WaitCondition: Self for method chaining
        """
        self._parallel_execution = enabled
        return self
    
    def set_failure_policy(self, policy: str) -> "WaitCondition":
        """
        Set failure policy for wait conditions.
        
        Args:
            policy: Failure policy (fail_fast, continue_on_failure)
            
        Returns:
            WaitCondition: Self for method chaining
        """
        self._failure_policy = policy
        return self
    
    def enable_retry(
        self,
        max_attempts: int = 3,
        delay: str = "10s",
        backoff_multiplier: float = 2.0
    ) -> "WaitCondition":
        """
        Enable retry logic for wait conditions.
        
        Args:
            max_attempts: Maximum retry attempts
            delay: Initial delay between retries
            backoff_multiplier: Backoff multiplier for exponential backoff
            
        Returns:
            WaitCondition: Self for method chaining
        """
        self._retry_config = {
            "max_attempts": max_attempts,
            "delay": delay,
            "backoff_multiplier": backoff_multiplier
        }
        return self
    
    def set_thresholds(
        self,
        success_threshold: int = 1,
        failure_threshold: int = 3
    ) -> "WaitCondition":
        """
        Set success and failure thresholds.
        
        Args:
            success_threshold: Number of consecutive successes required
            failure_threshold: Number of consecutive failures before giving up
            
        Returns:
            WaitCondition: Self for method chaining
        """
        self._success_threshold = success_threshold
        self._failure_threshold = failure_threshold
        return self
    
    # Preset configurations
    
    @classmethod
    def database_ready(
        cls,
        name: str = "database-wait",
        host: str = "postgres",
        port: int = 5432
    ) -> "WaitCondition":
        """
        Create wait condition for database readiness.
        
        Args:
            name: Wait condition name
            host: Database host
            port: Database port
            
        Returns:
            WaitCondition: Configured wait condition
        """
        return (cls(name)
            .wait_for_tcp_connect(host, port)
            .set_timeout("5m")
            .enable_retry(max_attempts=10, delay="5s"))
    
    @classmethod
    def service_stack_ready(
        cls,
        name: str = "service-stack-wait",
        services: Optional[List[str]] = None
    ) -> "WaitCondition":
        """
        Create wait condition for service stack readiness.
        
        Args:
            name: Wait condition name
            services: List of service names to wait for
            
        Returns:
            WaitCondition: Configured wait condition
        """
        wait_condition = cls(name).set_timeout("10m").enable_parallel_checks()
        
        for service in (services or ["user-service", "auth-service", "api-gateway"]):
            wait_condition.wait_for_deployment_ready(service)
            wait_condition.wait_for_http_success(f"http://{service}/health")
        
        return wait_condition
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for wait conditions.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        # Generate ConfigMap for wait configuration
        config_data = {
            "timeout": self._timeout,
            "parallel_execution": str(self._parallel_execution).lower(),
            "failure_policy": self._failure_policy,
            "success_threshold": str(self._success_threshold),
            "failure_threshold": str(self._failure_threshold),
            "conditions_count": str(len(self._wait_conditions))
        }
        
        # Add retry configuration
        if self._retry_config:
            config_data["retry_enabled"] = "true"
            config_data["retry_max_attempts"] = str(self._retry_config["max_attempts"])
            config_data["retry_delay"] = self._retry_config["delay"]
            config_data["retry_backoff_multiplier"] = str(self._retry_config["backoff_multiplier"])
        
        # Add individual wait conditions
        for i, condition in enumerate(self._wait_conditions):
            prefix = f"condition_{i}"
            config_data[f"{prefix}_type"] = condition["type"]
            config_data[f"{prefix}_timeout"] = condition.get("timeout", self._timeout)
            
            if condition["type"] == WaitType.RESOURCE_READY.value:
                config_data[f"{prefix}_resource"] = condition["resource"]
                config_data[f"{prefix}_name"] = condition["name"]
                if condition.get("namespace"):
                    config_data[f"{prefix}_namespace"] = condition["namespace"]
            
            elif condition["type"] == WaitType.HTTP_SUCCESS.value:
                config_data[f"{prefix}_url"] = condition["url"]
                config_data[f"{prefix}_method"] = condition["method"]
                config_data[f"{prefix}_expected_status"] = str(condition["expected_status"])
            
            elif condition["type"] == WaitType.TCP_CONNECT.value:
                config_data[f"{prefix}_host"] = condition["host"]
                config_data[f"{prefix}_port"] = str(condition["port"])
            
            elif condition["type"] == WaitType.CUSTOM_COMMAND.value:
                config_data[f"{prefix}_command"] = " ".join(condition["command"])
                config_data[f"{prefix}_expected_exit_code"] = str(condition["expected_exit_code"])
        
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self._name}-config",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "data": config_data
        }
        
        if self._namespace:
            config_map["metadata"]["namespace"] = self._namespace
        
        resources.append(config_map)
        
        # Generate Job for wait execution
        wait_job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{self._name}-job",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "template": {
                    "spec": {
                        "restartPolicy": "OnFailure",
                        "containers": [{
                            "name": "wait-executor",
                            "image": "curlimages/curl:8.4.0",
                            "command": ["/bin/sh"],
                            "args": ["-c", self._generate_wait_script()],
                            "envFrom": [{
                                "configMapRef": {
                                    "name": f"{self._name}-config"
                                }
                            }]
                        }]
                    }
                }
            }
        }
        
        if self._namespace:
            wait_job["metadata"]["namespace"] = self._namespace
        
        resources.append(wait_job)
        
        return resources
    
    def _generate_wait_script(self) -> str:
        """
        Generate shell script for wait execution.
        
        Returns:
            str: Shell script content
        """
        script_lines = [
            "#!/bin/sh",
            "set -e",
            "",
            "echo 'Starting wait conditions...'",
            ""
        ]
        
        for i, condition in enumerate(self._wait_conditions):
            if condition["type"] == WaitType.TCP_CONNECT.value:
                script_lines.extend([
                    f"echo 'Waiting for TCP connection to {condition['host']}:{condition['port']}'",
                    f"until nc -z {condition['host']} {condition['port']}; do",
                    f"  echo 'Waiting for {condition['host']}:{condition['port']} to be ready'",
                    f"  sleep 5",
                    f"done",
                    f"echo 'TCP connection to {condition['host']}:{condition['port']} is ready'",
                    ""
                ])
            
            elif condition["type"] == WaitType.HTTP_SUCCESS.value:
                script_lines.extend([
                    f"echo 'Waiting for HTTP success from {condition['url']}'",
                    f"until curl -s -f {condition['url']} > /dev/null; do",
                    f"  echo 'Waiting for {condition['url']} to return success'",
                    f"  sleep 10",
                    f"done",
                    f"echo 'HTTP endpoint {condition['url']} is ready'",
                    ""
                ])
        
        script_lines.append("echo 'All wait conditions completed successfully!'")
        
        return " && ".join([line for line in script_lines if line and not line.startswith("echo")]) 