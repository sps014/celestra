"""
Job class for Kubernetes Jobs in Celestraa DSL.

This module contains the Job class for handling batch processing workloads
that run to completion.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class Job(BaseBuilder):
    """
    Builder class for Kubernetes Jobs.
    
    The Job class represents batch processing workloads that run to completion.
    Jobs ensure one or more pods successfully complete their task.
    
    Example:
        ```python
        job = (Job("data-migration")
            .image("migration-tool:latest")
            .command(["python", "migrate.py"])
            .resources(cpu="1000m", memory="2Gi")
            .timeout("1h")
            .retry_limit(3))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the Job builder.
        
        Args:
            name: Name of the job
        """
        super().__init__(name)
        self._image: Optional[str] = None
        self._command: List[str] = []
        self._args: List[str] = []
        self._environment: Dict[str, str] = {}
        self._resources: Dict[str, Any] = {}
        self._parallelism: int = 1
        self._completions: int = 1
        self._backoff_limit: int = 6
        self._active_deadline_seconds: Optional[int] = None
        self._restart_policy: str = "OnFailure"
        self._secrets: List[Any] = []
        self._config_maps: List[Any] = []
        self._volumes: List[Dict[str, Any]] = []
        self._ports: List[Dict[str, Any]] = []  # Added for multiple ports support
        self._volume_mounts: List[Dict[str, Any]] = []
        self._security_context: Optional[Dict[str, Any]] = None
        self._node_selector: Dict[str, str] = {}
        self._tolerations: List[Dict[str, Any]] = []
        self._affinity: Optional[Dict[str, Any]] = None
    
    def image(self, image: str) -> "Job":
        """
        Set the container image.
        
        Args:
            image: Container image name and tag
            
        Returns:
            Job: Self for method chaining
        """
        self._image = image
        return self
    
    def command(self, command: List[str]) -> "Job":
        """
        Set the command to run in the container.
        
        Args:
            command: List of command arguments
            
        Returns:
            Job: Self for method chaining
        """
        self._command = command
        return self
    
    def args(self, args: List[str]) -> "Job":
        """
        Set the arguments for the command.
        
        Args:
            args: List of command arguments
            
        Returns:
            Job: Self for method chaining
        """
        self._args = args
        return self
    
    def environment(self, env_vars: Dict[str, str]) -> "Job":
        """
        Set environment variables.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            Job: Self for method chaining
        """
        self._environment.update(env_vars)
        return self
    
    def env(self, key: str, value: str) -> "Job":
        """
        Add a single environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            Job: Self for method chaining
        """
        self._environment[key] = value
        return self
    
    def resources(
        self, 
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        cpu_limit: Optional[str] = None,
        memory_limit: Optional[str] = None,
        gpu: Optional[int] = None
    ) -> "Job":
        """
        Set resource requirements and limits.
        
        Args:
            cpu: CPU request (e.g., "500m")
            memory: Memory request (e.g., "512Mi")
            cpu_limit: CPU limit (e.g., "1000m")
            memory_limit: Memory limit (e.g., "1Gi")
            gpu: Number of GPUs required
            
        Returns:
            Job: Self for method chaining
        """
        if cpu or memory:
            self._resources.setdefault("requests", {})
            if cpu:
                self._resources["requests"]["cpu"] = cpu
            if memory:
                self._resources["requests"]["memory"] = memory
        
        if cpu_limit or memory_limit:
            self._resources.setdefault("limits", {})
            if cpu_limit:
                self._resources["limits"]["cpu"] = cpu_limit
            if memory_limit:
                self._resources["limits"]["memory"] = memory_limit
        
        if gpu:
            self._resources.setdefault("limits", {})
            self._resources["limits"]["nvidia.com/gpu"] = str(gpu)
        
        return self
    
    def parallelism(self, count: int) -> "Job":
        """
        Set the number of pods to run in parallel.
        
        Args:
            count: Number of parallel pods
            
        Returns:
            Job: Self for method chaining
        """
        self._parallelism = count
        return self
    
    def completions(self, count: int) -> "Job":
        """
        Set the number of successful completions required.
        
        Args:
            count: Number of completions required
            
        Returns:
            Job: Self for method chaining
        """
        self._completions = count
        return self
    
    def retry_limit(self, limit: int) -> "Job":
        """
        Set the number of retries before considering the job as failed.
        
        Args:
            limit: Number of retry attempts
            
        Returns:
            Job: Self for method chaining
        """
        self._backoff_limit = limit
        return self
    
    def timeout(self, timeout: Union[str, int]) -> "Job":
        """
        Set the job timeout.
        
        Args:
            timeout: Timeout in seconds or duration string (e.g., "1h", "30m")
            
        Returns:
            Job: Self for method chaining
        """
        if isinstance(timeout, str):
            # Parse duration string
            timeout_seconds = self._parse_duration(timeout)
            self._active_deadline_seconds = timeout_seconds
        else:
            self._active_deadline_seconds = timeout
        return self
    
    def restart_policy(self, policy: str) -> "Job":
        """
        Set restart policy for job pods.
        
        Args:
            policy: Restart policy ("OnFailure", "Never")
            
        Returns:
            Job: Self for method chaining
        """
        self._restart_policy = policy
        return self
    
    def port(self, port: int, name: str = "http", protocol: str = "TCP") -> "Job":
        """
        Add a port to the job container.
        
        Args:
            port: Port number
            name: Port name (default: "http")
            protocol: Port protocol (default: "TCP")
            
        Returns:
            Job: Self for method chaining
        """
        self._ports.append({
            "containerPort": port,
            "name": name,
            "protocol": protocol
        })
        return self
    
    def add_port(self, port: int, name: str = "http", protocol: str = "TCP") -> "Job":
        """
        Add a port to the job container (alias for port() method).
        
        Args:
            port: Port number
            name: Port name
            protocol: Port protocol (default: "TCP")
            
        Returns:
            Job: Self for method chaining
        """
        return self.port(port, name, protocol)
    
    def ports(self, ports: List[Dict[str, Any]]) -> "Job":
        """
        Set multiple ports for the job container.
        
        Args:
            ports: List of port configurations with 'port', 'name', and optional 'protocol'
            
        Example:
            ```python
            job.ports([
                {"port": 8080, "name": "web"},
                {"port": 9090, "name": "metrics"},
                {"port": 8081, "name": "health"}
            ])
            ```
            
        Returns:
            Job: Self for method chaining
        """
        for port_config in ports:
            self._ports.append({
                "containerPort": port_config.get("port"),
                "name": port_config.get("name", "http"),
                "protocol": port_config.get("protocol", "TCP")
            })
        return self
    
    def metrics_port(self, port: int = 9090, name: str = "metrics") -> "Job":
        """
        Add metrics port (convenience method).
        
        Args:
            port: Metrics port number (default: 9090)
            name: Port name (default: "metrics")
            
        Returns:
            Job: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def web_port(self, port: int = 8080, name: str = "web") -> "Job":
        """
        Add web interface port (convenience method).
        
        Args:
            port: Web port number (default: 8080)
            name: Port name (default: "web")
            
        Returns:
            Job: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def status_port(self, port: int = 8081, name: str = "status") -> "Job":
        """
        Add status/health port (convenience method).
        
        Args:
            port: Status port number (default: 8081)
            name: Port name (default: "status")
            
        Returns:
            Job: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def add_secret(self, secret: "Secret") -> "Job":
        """
        Add a secret to the job.
        
        Args:
            secret: Secret configuration
            
        Returns:
            Job: Self for method chaining
        """
        self._secrets.append(secret)
        return self
    
    def add_config(self, config_map: "ConfigMap") -> "Job":
        """
        Add a ConfigMap to the job.
        
        Args:
            config_map: ConfigMap configuration
            
        Returns:
            Job: Self for method chaining
        """
        self._config_maps.append(config_map)
        return self
    
    def add_volume(self, name: str, volume_spec: Dict[str, Any]) -> "Job":
        """
        Add a volume to the job.
        
        Args:
            name: Volume name
            volume_spec: Volume specification
            
        Returns:
            Job: Self for method chaining
        """
        volume = {"name": name}
        volume.update(volume_spec)
        self._volumes.append(volume)
        return self
    
    def mount_volume(self, volume_name: str, mount_path: str, read_only: bool = False) -> "Job":
        """
        Mount a volume in the container.
        
        Args:
            volume_name: Name of the volume to mount
            mount_path: Path where to mount the volume
            read_only: Whether to mount as read-only
            
        Returns:
            Job: Self for method chaining
        """
        self._volume_mounts.append({
            "name": volume_name,
            "mountPath": mount_path,
            "readOnly": read_only
        })
        return self
    
    def security_context(self, context: Dict[str, Any]) -> "Job":
        """
        Set security context for the job.
        
        Args:
            context: Security context configuration
            
        Returns:
            Job: Self for method chaining
        """
        self._security_context = context
        return self
    
    def node_selector(self, selector: Dict[str, str]) -> "Job":
        """
        Set node selector for the job.
        
        Args:
            selector: Node selector labels
            
        Returns:
            Job: Self for method chaining
        """
        self._node_selector.update(selector)
        return self
    
    def toleration(self, key: str, operator: str = "Equal", value: str = "", effect: str = "NoSchedule") -> "Job":
        """
        Add a toleration for the job.
        
        Args:
            key: Taint key
            operator: Toleration operator
            value: Taint value
            effect: Taint effect
            
        Returns:
            Job: Self for method chaining
        """
        toleration = {
            "key": key,
            "operator": operator,
            "effect": effect
        }
        if value:
            toleration["value"] = value
        
        self._tolerations.append(toleration)
        return self
    
    def affinity(self, affinity_spec: Dict[str, Any]) -> "Job":
        """
        Set affinity rules for the job.
        
        Args:
            affinity_spec: Affinity specification
            
        Returns:
            Job: Self for method chaining
        """
        self._affinity = affinity_spec
        return self
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to seconds."""
        duration = duration.strip().lower()
        
        if duration.endswith('s'):
            return int(duration[:-1])
        elif duration.endswith('m'):
            return int(duration[:-1]) * 60
        elif duration.endswith('h'):
            return int(duration[:-1]) * 3600
        elif duration.endswith('d'):
            return int(duration[:-1]) * 86400
        else:
            # Assume seconds if no unit
            return int(duration)
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes Job resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the Job resource
        """
        container = {
            "name": self._name,
            "image": self._image or "busybox:latest"
        }
        
        # Add command and args
        if self._command:
            container["command"] = self._command
        if self._args:
            container["args"] = self._args
        
        # Add environment variables
        env_vars = []
        for key, value in self._environment.items():
            env_vars.append({"name": key, "value": value})
        
        # Add environment from secrets and config maps
        for secret in self._secrets:
            if hasattr(secret, 'get_env_var_mappings'):
                env_vars.extend(secret.get_env_var_mappings())
        
        for config_map in self._config_maps:
            if hasattr(config_map, 'get_env_var_mappings'):
                env_vars.extend(config_map.get_env_var_mappings())
        
        if env_vars:
            container["env"] = env_vars
        
        # Add resources
        if self._resources:
            container["resources"] = self._resources
        
        # Add ports
        if self._ports:
            container["ports"] = self._ports
        
        # Add volume mounts
        volume_mounts = self._volume_mounts.copy()
        
        # Add volume mounts from secrets and config maps
        for secret in self._secrets:
            if hasattr(secret, 'get_volume_mount'):
                mount = secret.get_volume_mount()
                if mount:
                    volume_mounts.append(mount)
        
        for config_map in self._config_maps:
            if hasattr(config_map, 'get_volume_mount'):
                mount = config_map.get_volume_mount()
                if mount:
                    volume_mounts.append(mount)
        
        if volume_mounts:
            container["volumeMounts"] = volume_mounts
        
        # Add security context
        if self._security_context:
            container["securityContext"] = self._security_context
        
        # Build pod spec
        pod_spec = {
            "containers": [container],
            "restartPolicy": self._restart_policy
        }
        
        # Add volumes
        volumes = self._volumes.copy()
        
        # Add volumes from secrets and config maps
        for secret in self._secrets:
            if hasattr(secret, 'get_volume'):
                volume = secret.get_volume()
                if volume:
                    volumes.append(volume)
        
        for config_map in self._config_maps:
            if hasattr(config_map, 'get_volume'):
                volume = config_map.get_volume()
                if volume:
                    volumes.append(volume)
        
        if volumes:
            pod_spec["volumes"] = volumes
        
        # Add node selector
        if self._node_selector:
            pod_spec["nodeSelector"] = self._node_selector
        
        # Add tolerations
        if self._tolerations:
            pod_spec["tolerations"] = self._tolerations
        
        # Add affinity
        if self._affinity:
            pod_spec["affinity"] = self._affinity
        
        # Build job spec
        job_spec = {
            "template": {
                "metadata": {
                    "labels": self._labels
                },
                "spec": pod_spec
            }
        }
        
        # Add job-specific configurations
        if self._parallelism != 1:
            job_spec["parallelism"] = self._parallelism
        
        if self._completions != 1:
            job_spec["completions"] = self._completions
        
        if self._backoff_limit != 6:
            job_spec["backoffLimit"] = self._backoff_limit
        
        if self._active_deadline_seconds:
            job_spec["activeDeadlineSeconds"] = self._active_deadline_seconds
        
        # Build job resource
        job = {
            "apiVersion": "batch/v1",
            "kind": "Job",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": job_spec
        }
        
        if self._namespace:
            job["metadata"]["namespace"] = self._namespace
        
        return [job] 