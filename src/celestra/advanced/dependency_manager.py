"""
DependencyManager class for advanced dependency management in Celestraa DSL.

This module provides sophisticated dependency management including dependency ordering,
health checks, readiness gates, and conditional dependencies.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from ..core.base_builder import BaseBuilder


class DependencyType(Enum):
    """Types of dependencies."""
    SERVICE = "service"
    DATABASE = "database"
    MESSAGE_QUEUE = "message_queue"
    API = "api"
    STORAGE = "storage"
    CUSTOM = "custom"


class DependencyManager(BaseBuilder):
    """
    Builder class for advanced dependency management.
    
    Manages complex dependencies between services, databases, and external systems
    with health checks, readiness gates, and conditional logic.
    
    Example:
        ```python
        deps = (DependencyManager("app-dependencies")
            .add_service_dependency("user-service", health_check="/health")
            .add_database_dependency("postgres", connection_string="postgres://...")
            .add_condition("production", lambda: env == "prod")
            .set_timeout("5m")
            .enable_retry(max_attempts=3))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the DependencyManager builder.
        
        Args:
            name: Name of the dependency manager
        """
        super().__init__(name)
        self._dependencies: List[Dict[str, Any]] = []
        self._conditions: Dict[str, Any] = {}
        self._timeout: str = "5m"
        self._retry_config: Dict[str, Any] = {}
        self._health_checks: Dict[str, Any] = {}
        self._readiness_gates: List[Dict[str, Any]] = []
        self._startup_order: List[str] = []
        self._circuit_breaker: Optional[Dict[str, Any]] = None
    
    def add_service_dependency(
        self,
        name: str,
        service_name: str,
        port: int = 80,
        health_check: Optional[str] = None,
        required: bool = True,
        timeout: str = "30s"
    ) -> "DependencyManager":
        """
        Add a service dependency.
        
        Args:
            name: Dependency name
            service_name: Kubernetes service name
            port: Service port
            health_check: Health check endpoint
            required: Whether dependency is required
            timeout: Health check timeout
            
        Returns:
            DependencyManager: Self for method chaining
        """
        dependency = {
            "name": name,
            "type": DependencyType.SERVICE.value,
            "service_name": service_name,
            "port": port,
            "health_check": health_check,
            "required": required,
            "timeout": timeout
        }
        self._dependencies.append(dependency)
        return self
    
    def add_database_dependency(
        self,
        name: str,
        host: str,
        port: int = 5432,
        database: Optional[str] = None,
        connection_string: Optional[str] = None,
        required: bool = True,
        timeout: str = "30s"
    ) -> "DependencyManager":
        """
        Add a database dependency.
        
        Args:
            name: Dependency name
            host: Database host
            port: Database port
            database: Database name
            connection_string: Full connection string
            required: Whether dependency is required
            timeout: Connection timeout
            
        Returns:
            DependencyManager: Self for method chaining
        """
        dependency = {
            "name": name,
            "type": DependencyType.DATABASE.value,
            "host": host,
            "port": port,
            "database": database,
            "connection_string": connection_string,
            "required": required,
            "timeout": timeout
        }
        self._dependencies.append(dependency)
        return self
    
    def add_api_dependency(
        self,
        name: str,
        base_url: str,
        health_endpoint: str = "/health",
        required: bool = True,
        timeout: str = "30s",
        headers: Optional[Dict[str, str]] = None
    ) -> "DependencyManager":
        """
        Add an API dependency.
        
        Args:
            name: Dependency name
            base_url: API base URL
            health_endpoint: Health check endpoint
            required: Whether dependency is required
            timeout: Request timeout
            headers: Request headers
            
        Returns:
            DependencyManager: Self for method chaining
        """
        dependency = {
            "name": name,
            "type": DependencyType.API.value,
            "base_url": base_url,
            "health_endpoint": health_endpoint,
            "required": required,
            "timeout": timeout,
            "headers": headers or {}
        }
        self._dependencies.append(dependency)
        return self
    
    def add_message_queue_dependency(
        self,
        name: str,
        endpoint: str,
        queue_type: str = "redis",
        queues: Optional[List[str]] = None,
        required: bool = True,
        timeout: str = "30s"
    ) -> "DependencyManager":
        """
        Add a message queue dependency.
        
        Args:
            name: Dependency name
            endpoint: Queue endpoint
            queue_type: Queue type (redis, kafka, rabbitmq)
            queues: List of required queues
            required: Whether dependency is required
            timeout: Connection timeout
            
        Returns:
            DependencyManager: Self for method chaining
        """
        dependency = {
            "name": name,
            "type": DependencyType.MESSAGE_QUEUE.value,
            "endpoint": endpoint,
            "queue_type": queue_type,
            "queues": queues or [],
            "required": required,
            "timeout": timeout
        }
        self._dependencies.append(dependency)
        return self
    
    def add_storage_dependency(
        self,
        name: str,
        bucket: str,
        storage_type: str = "s3",
        region: Optional[str] = None,
        required: bool = True,
        timeout: str = "30s"
    ) -> "DependencyManager":
        """
        Add a storage dependency.
        
        Args:
            name: Dependency name
            bucket: Storage bucket/container
            storage_type: Storage type (s3, gcs, azure-blob)
            region: Storage region
            required: Whether dependency is required
            timeout: Operation timeout
            
        Returns:
            DependencyManager: Self for method chaining
        """
        dependency = {
            "name": name,
            "type": DependencyType.STORAGE.value,
            "bucket": bucket,
            "storage_type": storage_type,
            "region": region,
            "required": required,
            "timeout": timeout
        }
        self._dependencies.append(dependency)
        return self
    
    def add_custom_dependency(
        self,
        name: str,
        check_command: List[str],
        required: bool = True,
        timeout: str = "30s",
        description: Optional[str] = None
    ) -> "DependencyManager":
        """
        Add a custom dependency check.
        
        Args:
            name: Dependency name
            check_command: Command to execute for check
            required: Whether dependency is required
            timeout: Check timeout
            description: Description of the dependency
            
        Returns:
            DependencyManager: Self for method chaining
        """
        dependency = {
            "name": name,
            "type": DependencyType.CUSTOM.value,
            "check_command": check_command,
            "required": required,
            "timeout": timeout,
            "description": description
        }
        self._dependencies.append(dependency)
        return self
    
    def add_condition(
        self,
        name: str,
        expression: str,
        description: Optional[str] = None
    ) -> "DependencyManager":
        """
        Add a conditional dependency.
        
        Args:
            name: Condition name
            expression: Condition expression
            description: Condition description
            
        Returns:
            DependencyManager: Self for method chaining
        """
        self._conditions[name] = {
            "expression": expression,
            "description": description
        }
        return self
    
    def set_startup_order(self, order: List[str]) -> "DependencyManager":
        """
        Set the startup order for dependencies.
        
        Args:
            order: List of dependency names in startup order
            
        Returns:
            DependencyManager: Self for method chaining
        """
        self._startup_order = order
        return self
    
    def set_timeout(self, timeout: str) -> "DependencyManager":
        """
        Set global timeout for dependency checks.
        
        Args:
            timeout: Timeout duration (e.g., "5m", "30s")
            
        Returns:
            DependencyManager: Self for method chaining
        """
        self._timeout = timeout
        return self
    
    def enable_retry(
        self,
        max_attempts: int = 3,
        backoff: str = "exponential",
        initial_delay: str = "1s",
        max_delay: str = "60s"
    ) -> "DependencyManager":
        """
        Enable retry logic for dependency checks.
        
        Args:
            max_attempts: Maximum retry attempts
            backoff: Backoff strategy (linear, exponential)
            initial_delay: Initial delay between retries
            max_delay: Maximum delay between retries
            
        Returns:
            DependencyManager: Self for method chaining
        """
        self._retry_config = {
            "max_attempts": max_attempts,
            "backoff": backoff,
            "initial_delay": initial_delay,
            "max_delay": max_delay
        }
        return self
    
    def enable_circuit_breaker(
        self,
        failure_threshold: int = 5,
        timeout: str = "60s",
        half_open_requests: int = 3
    ) -> "DependencyManager":
        """
        Enable circuit breaker for dependency checks.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Circuit open timeout
            half_open_requests: Number of requests in half-open state
            
        Returns:
            DependencyManager: Self for method chaining
        """
        self._circuit_breaker = {
            "failure_threshold": failure_threshold,
            "timeout": timeout,
            "half_open_requests": half_open_requests
        }
        return self
    
    def add_readiness_gate(
        self,
        condition_type: str,
        description: Optional[str] = None
    ) -> "DependencyManager":
        """
        Add a readiness gate condition.
        
        Args:
            condition_type: Type of the readiness condition
            description: Description of the condition
            
        Returns:
            DependencyManager: Self for method chaining
        """
        gate = {
            "conditionType": condition_type,
            "description": description
        }
        self._readiness_gates.append(gate)
        return self
    
    # Preset configurations
    
    @classmethod
    def web_app_dependencies(cls, name: str = "web-app-deps") -> "DependencyManager":
        """
        Create typical web application dependencies.
        
        Args:
            name: Manager name
            
        Returns:
            DependencyManager: Configured dependency manager
        """
        return (cls(name)
            .add_database_dependency("postgres", host="postgres", port=5432)
            .add_message_queue_dependency("redis", endpoint="redis:6379")
            .enable_retry(max_attempts=3)
            .set_timeout("2m"))
    
    @classmethod
    def microservices_dependencies(cls, name: str = "microservices-deps") -> "DependencyManager":
        """
        Create microservices dependencies.
        
        Args:
            name: Manager name
            
        Returns:
            DependencyManager: Configured dependency manager
        """
        return (cls(name)
            .add_service_dependency("user-service", service_name="user-service", health_check="/health")
            .add_service_dependency("auth-service", service_name="auth-service", health_check="/health")
            .add_database_dependency("postgres", host="postgres")
            .add_message_queue_dependency("kafka", endpoint="kafka:9092", queue_type="kafka")
            .enable_retry(max_attempts=5)
            .enable_circuit_breaker()
            .set_timeout("5m"))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for dependency management.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        # Generate ConfigMap for dependency configuration
        config_data = {
            "timeout": self._timeout,
            "dependencies": str(len(self._dependencies))
        }
        
        # Add dependency configurations
        for i, dep in enumerate(self._dependencies):
            prefix = f"dep_{i}"
            config_data[f"{prefix}_name"] = dep["name"]
            config_data[f"{prefix}_type"] = dep["type"]
            config_data[f"{prefix}_required"] = str(dep.get("required", True)).lower()
            config_data[f"{prefix}_timeout"] = dep.get("timeout", "30s")
            
            if dep["type"] == DependencyType.SERVICE.value:
                config_data[f"{prefix}_service_name"] = dep["service_name"]
                config_data[f"{prefix}_port"] = str(dep["port"])
                if dep.get("health_check"):
                    config_data[f"{prefix}_health_check"] = dep["health_check"]
            
            elif dep["type"] == DependencyType.DATABASE.value:
                config_data[f"{prefix}_host"] = dep["host"]
                config_data[f"{prefix}_port"] = str(dep["port"])
                if dep.get("database"):
                    config_data[f"{prefix}_database"] = dep["database"]
            
            elif dep["type"] == DependencyType.API.value:
                config_data[f"{prefix}_base_url"] = dep["base_url"]
                config_data[f"{prefix}_health_endpoint"] = dep["health_endpoint"]
        
        # Add retry configuration
        if self._retry_config:
            config_data["retry_enabled"] = "true"
            config_data["retry_max_attempts"] = str(self._retry_config["max_attempts"])
            config_data["retry_backoff"] = self._retry_config["backoff"]
            config_data["retry_initial_delay"] = self._retry_config["initial_delay"]
            config_data["retry_max_delay"] = self._retry_config["max_delay"]
        
        # Add circuit breaker configuration
        if self._circuit_breaker:
            config_data["circuit_breaker_enabled"] = "true"
            config_data["circuit_breaker_failure_threshold"] = str(self._circuit_breaker["failure_threshold"])
            config_data["circuit_breaker_timeout"] = self._circuit_breaker["timeout"]
            config_data["circuit_breaker_half_open_requests"] = str(self._circuit_breaker["half_open_requests"])
        
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
        
        # Generate Job for dependency checking
        dependency_check_job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": f"{self._name}-check",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "template": {
                    "spec": {
                        "restartPolicy": "OnFailure",
                        "containers": [{
                            "name": "dependency-checker",
                            "image": "busybox:1.35",
                            "command": ["/bin/sh"],
                            "args": ["-c", self._generate_check_script()],
                            "env": [
                                {
                                    "name": "TIMEOUT",
                                    "valueFrom": {
                                        "configMapKeyRef": {
                                            "name": f"{self._name}-config",
                                            "key": "timeout"
                                        }
                                    }
                                }
                            ]
                        }]
                    }
                }
            }
        }
        
        if self._namespace:
            dependency_check_job["metadata"]["namespace"] = self._namespace
        
        resources.append(dependency_check_job)
        
        return resources
    
    def _generate_check_script(self) -> str:
        """
        Generate shell script for dependency checking.
        
        Returns:
            str: Shell script content
        """
        script_lines = [
            "#!/bin/sh",
            "set -e",
            "",
            "echo 'Starting dependency checks...'",
            ""
        ]
        
        for dep in self._dependencies:
            if dep["type"] == DependencyType.SERVICE.value:
                script_lines.extend([
                    f"echo 'Checking service dependency: {dep['name']}'",
                    f"until nc -z {dep['service_name']} {dep['port']}; do",
                    f"  echo 'Waiting for {dep['service_name']}:{dep['port']}'",
                    f"  sleep 2",
                    f"done",
                    f"echo 'Service {dep['name']} is ready'",
                    ""
                ])
            
            elif dep["type"] == DependencyType.DATABASE.value:
                script_lines.extend([
                    f"echo 'Checking database dependency: {dep['name']}'",
                    f"until nc -z {dep['host']} {dep['port']}; do",
                    f"  echo 'Waiting for database {dep['host']}:{dep['port']}'",
                    f"  sleep 2",
                    f"done",
                    f"echo 'Database {dep['name']} is ready'",
                    ""
                ])
        
        script_lines.append("echo 'All dependencies are ready!'")
        
        return " && ".join([line for line in script_lines if line and not line.startswith("echo")])
    
    def _parse_duration(self, duration: str) -> int:
        """
        Parse duration string to seconds.
        
        Args:
            duration: Duration string (e.g., "30s", "5m")
            
        Returns:
            int: Duration in seconds
        """
        if duration.endswith("s"):
            return int(duration[:-1])
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 3600
        else:
            return int(duration) 