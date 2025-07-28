"""
CronJob class for Kubernetes CronJobs in Celestraa DSL.

This module contains the CronJob class for handling scheduled batch workloads
that run on a time-based schedule.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class CronJob(BaseBuilder):
    """
    Builder class for Kubernetes CronJobs.
    
    The CronJob class represents scheduled batch workloads that run at
    specified times or intervals using cron-like scheduling.
    
    Example:
        ```python
        backup_job = (CronJob("daily-backup")
            .schedule("0 2 * * *")  # Daily at 2 AM
            .image("backup-tool:latest")
            .command(["backup.sh"])
            .resources(cpu="500m", memory="1Gi")
            .timeout("30m")
            .suspend(False))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the CronJob builder.
        
        Args:
            name: Name of the cron job
        """
        super().__init__(name)
        self._schedule: str = "0 0 * * *"  # Default: daily at midnight
        self._image: Optional[str] = None
        self._command: List[str] = []
        self._args: List[str] = []
        self._environment: Dict[str, str] = {}
        self._resources: Dict[str, Any] = {}
        self._restart_policy: str = "OnFailure"
        self._concurrency_policy: str = "Allow"
        self._suspend: bool = False
        self._successful_jobs_history_limit: int = 3
        self._failed_jobs_history_limit: int = 1
        self._starting_deadline_seconds: Optional[int] = None
        self._backoff_limit: int = 6
        self._active_deadline_seconds: Optional[int] = None
        self._timezone: Optional[str] = None
        self._secrets: List[Any] = []
        self._config_maps: List[Any] = []
        self._volumes: List[Dict[str, Any]] = []
        self._ports: List[Dict[str, Any]] = []  # Added for multiple ports support
        self._volume_mounts: List[Dict[str, Any]] = []
        self._security_context: Optional[Dict[str, Any]] = None
        self._node_selector: Dict[str, str] = {}
        self._tolerations: List[Dict[str, Any]] = []
        self._affinity: Optional[Dict[str, Any]] = None
    
    def schedule(self, cron_schedule: str) -> "CronJob":
        """
        Set the cron schedule.
        
        Args:
            cron_schedule: Cron expression (e.g., "0 2 * * *" for daily at 2 AM)
            
        Returns:
            CronJob: Self for method chaining
        """
        self._schedule = cron_schedule
        return self
    
    def daily(self, hour: int = 0, minute: int = 0) -> "CronJob":
        """
        Set daily schedule.
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            CronJob: Self for method chaining
        """
        self._schedule = f"{minute} {hour} * * *"
        return self
    
    def weekly(self, day_of_week: int = 0, hour: int = 0, minute: int = 0) -> "CronJob":
        """
        Set weekly schedule.
        
        Args:
            day_of_week: Day of week (0=Sunday, 6=Saturday)
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            CronJob: Self for method chaining
        """
        self._schedule = f"{minute} {hour} * * {day_of_week}"
        return self
    
    def monthly(self, day: int = 1, hour: int = 0, minute: int = 0) -> "CronJob":
        """
        Set monthly schedule.
        
        Args:
            day: Day of month (1-31)
            hour: Hour (0-23)
            minute: Minute (0-59)
            
        Returns:
            CronJob: Self for method chaining
        """
        self._schedule = f"{minute} {hour} {day} * *"
        return self
    
    def every_minutes(self, minutes: int) -> "CronJob":
        """
        Set schedule to run every N minutes.
        
        Args:
            minutes: Number of minutes
            
        Returns:
            CronJob: Self for method chaining
        """
        self._schedule = f"*/{minutes} * * * *"
        return self
    
    def every_hours(self, hours: int) -> "CronJob":
        """
        Set schedule to run every N hours.
        
        Args:
            hours: Number of hours
            
        Returns:
            CronJob: Self for method chaining
        """
        self._schedule = f"0 */{hours} * * *"
        return self
    
    def image(self, image: str) -> "CronJob":
        """
        Set the container image.
        
        Args:
            image: Container image name and tag
            
        Returns:
            CronJob: Self for method chaining
        """
        self._image = image
        return self
    
    def command(self, command: List[str]) -> "CronJob":
        """
        Set the command to run in the container.
        
        Args:
            command: List of command arguments
            
        Returns:
            CronJob: Self for method chaining
        """
        self._command = command
        return self
    
    def args(self, args: List[str]) -> "CronJob":
        """
        Set the arguments for the command.
        
        Args:
            args: List of command arguments
            
        Returns:
            CronJob: Self for method chaining
        """
        self._args = args
        return self
    
    def environment(self, env_vars: Dict[str, str]) -> "CronJob":
        """
        Set environment variables.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            CronJob: Self for method chaining
        """
        self._environment.update(env_vars)
        return self
    
    def env(self, key: str, value: str) -> "CronJob":
        """
        Add a single environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            CronJob: Self for method chaining
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
    ) -> "CronJob":
        """
        Set resource requirements and limits.
        
        Args:
            cpu: CPU request (e.g., "500m")
            memory: Memory request (e.g., "512Mi")
            cpu_limit: CPU limit (e.g., "1000m")
            memory_limit: Memory limit (e.g., "1Gi")
            gpu: Number of GPUs required
            
        Returns:
            CronJob: Self for method chaining
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
    
    def concurrency_policy(self, policy: str) -> "CronJob":
        """
        Set the concurrency policy.
        
        Args:
            policy: Concurrency policy ("Allow", "Forbid", "Replace")
            
        Returns:
            CronJob: Self for method chaining
        """
        if policy not in ["Allow", "Forbid", "Replace"]:
            raise ValueError("Concurrency policy must be 'Allow', 'Forbid', or 'Replace'")
        self._concurrency_policy = policy
        return self
    
    def suspend(self, suspended: bool = True) -> "CronJob":
        """
        Suspend or resume the cron job.
        
        Args:
            suspended: Whether to suspend the cron job
            
        Returns:
            CronJob: Self for method chaining
        """
        self._suspend = suspended
        return self
    
    def port(self, port: int, name: str = "http", protocol: str = "TCP") -> "CronJob":
        """
        Add a port to the cron job container.
        
        Args:
            port: Port number
            name: Port name (default: "http")
            protocol: Port protocol (default: "TCP")
            
        Returns:
            CronJob: Self for method chaining
        """
        self._ports.append({
            "containerPort": port,
            "name": name,
            "protocol": protocol
        })
        return self
    
    def add_port(self, port: int, name: str = "http", protocol: str = "TCP") -> "CronJob":
        """
        Add a port to the cron job container (alias for port() method).
        
        Args:
            port: Port number
            name: Port name
            protocol: Port protocol (default: "TCP")
            
        Returns:
            CronJob: Self for method chaining
        """
        return self.port(port, name, protocol)
    
    def ports(self, ports: List[Dict[str, Any]]) -> "CronJob":
        """
        Set multiple ports for the cron job container.
        
        Args:
            ports: List of port configurations with 'port', 'name', and optional 'protocol'
            
        Example:
            ```python
            cron_job.ports([
                {"port": 8080, "name": "web"},
                {"port": 9090, "name": "metrics"},
                {"port": 8081, "name": "health"}
            ])
            ```
            
        Returns:
            CronJob: Self for method chaining
        """
        for port_config in ports:
            self._ports.append({
                "containerPort": port_config.get("port"),
                "name": port_config.get("name", "http"),
                "protocol": port_config.get("protocol", "TCP")
            })
        return self
    
    def metrics_port(self, port: int = 9090, name: str = "metrics") -> "CronJob":
        """
        Add metrics port (convenience method).
        
        Args:
            port: Metrics port number (default: 9090)
            name: Port name (default: "metrics")
            
        Returns:
            CronJob: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def web_port(self, port: int = 8080, name: str = "web") -> "CronJob":
        """
        Add web interface port (convenience method).
        
        Args:
            port: Web port number (default: 8080)
            name: Port name (default: "web")
            
        Returns:
            CronJob: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def status_port(self, port: int = 8081, name: str = "status") -> "CronJob":
        """
        Add status/health port (convenience method).
        
        Args:
            port: Status port number (default: 8081)
            name: Port name (default: "status")
            
        Returns:
            CronJob: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def history_limits(self, successful: int = 3, failed: int = 1) -> "CronJob":
        """
        Set job history limits.
        
        Args:
            successful: Number of successful jobs to keep
            failed: Number of failed jobs to keep
            
        Returns:
            CronJob: Self for method chaining
        """
        self._successful_jobs_history_limit = successful
        self._failed_jobs_history_limit = failed
        return self
    
    def starting_deadline(self, deadline_seconds: int) -> "CronJob":
        """
        Set starting deadline for jobs.
        
        Args:
            deadline_seconds: Deadline in seconds for starting the job
            
        Returns:
            CronJob: Self for method chaining
        """
        self._starting_deadline_seconds = deadline_seconds
        return self
    
    def timeout(self, timeout: Union[str, int]) -> "CronJob":
        """
        Set the job timeout.
        
        Args:
            timeout: Timeout in seconds or duration string (e.g., "1h", "30m")
            
        Returns:
            CronJob: Self for method chaining
        """
        if isinstance(timeout, str):
            # Parse duration string
            timeout_seconds = self._parse_duration(timeout)
            self._active_deadline_seconds = timeout_seconds
        else:
            self._active_deadline_seconds = timeout
        return self
    
    def retry_limit(self, limit: int) -> "CronJob":
        """
        Set the number of retries before considering the job as failed.
        
        Args:
            limit: Number of retry attempts
            
        Returns:
            CronJob: Self for method chaining
        """
        self._backoff_limit = limit
        return self
    
    def timezone(self, tz: str) -> "CronJob":
        """
        Set the timezone for the schedule.
        
        Args:
            tz: Timezone (e.g., "America/New_York", "UTC")
            
        Returns:
            CronJob: Self for method chaining
        """
        self._timezone = tz
        return self
    
    def restart_policy(self, policy: str) -> "CronJob":
        """
        Set the restart policy for the job pods.
        
        Args:
            policy: Restart policy ("OnFailure", "Never")
            
        Returns:
            CronJob: Self for method chaining
        """
        if policy not in ["OnFailure", "Never"]:
            raise ValueError("Restart policy must be 'OnFailure' or 'Never'")
        self._restart_policy = policy
        return self
    
    def add_secret(self, secret: "Secret") -> "CronJob":
        """
        Add a secret to the cron job.
        
        Args:
            secret: Secret configuration
            
        Returns:
            CronJob: Self for method chaining
        """
        self._secrets.append(secret)
        return self
    
    def add_config(self, config_map: "ConfigMap") -> "CronJob":
        """
        Add a ConfigMap to the cron job.
        
        Args:
            config_map: ConfigMap configuration
            
        Returns:
            CronJob: Self for method chaining
        """
        self._config_maps.append(config_map)
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
        Generate Kubernetes CronJob resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the CronJob resource
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
        
        # Build job template spec
        job_template_spec = {
            "spec": {
                "template": {
                    "metadata": {
                        "labels": self._labels
                    },
                    "spec": pod_spec
                }
            }
        }
        
        # Add job-specific configurations
        if self._backoff_limit != 6:
            job_template_spec["spec"]["backoffLimit"] = self._backoff_limit
        
        if self._active_deadline_seconds:
            job_template_spec["spec"]["activeDeadlineSeconds"] = self._active_deadline_seconds
        
        # Build cron job spec
        cron_job_spec = {
            "schedule": self._schedule,
            "jobTemplate": job_template_spec
        }
        
        # Add cron job specific configurations
        if self._concurrency_policy != "Allow":
            cron_job_spec["concurrencyPolicy"] = self._concurrency_policy
        
        if self._suspend:
            cron_job_spec["suspend"] = self._suspend
        
        if self._successful_jobs_history_limit != 3:
            cron_job_spec["successfulJobsHistoryLimit"] = self._successful_jobs_history_limit
        
        if self._failed_jobs_history_limit != 1:
            cron_job_spec["failedJobsHistoryLimit"] = self._failed_jobs_history_limit
        
        if self._starting_deadline_seconds:
            cron_job_spec["startingDeadlineSeconds"] = self._starting_deadline_seconds
        
        if self._timezone:
            cron_job_spec["timeZone"] = self._timezone
        
        # Build cron job resource
        cron_job = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": cron_job_spec
        }
        
        if self._namespace:
            cron_job["metadata"]["namespace"] = self._namespace
        
        return [cron_job] 