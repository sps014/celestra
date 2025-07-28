"""
Health class for advanced health check configurations in Celestraa DSL.

This module contains the Health class for managing liveness, readiness,
and startup probes for containers.
"""

from typing import Dict, List, Any, Optional, Union


class Health:
    """
    Builder class for container health check configuration.
    
    The Health class manages liveness, readiness, and startup probes
    to ensure containers are healthy and ready to serve traffic.
    
    Example:
        ```python
        health = (Health()
            .liveness_http("/health", port=8080)
            .readiness_http("/ready", port=8080)
            .startup_http("/startup", port=8080, initial_delay="30s")
            .failure_threshold(3)
            .success_threshold(1))
        ```
    """
    
    def __init__(self):
        """Initialize the Health builder."""
        self.liveness_probe: Optional[Dict[str, Any]] = None
        self.readiness_probe: Optional[Dict[str, Any]] = None
        self.startup_probe: Optional[Dict[str, Any]] = None
        self._default_config = {
            "initialDelaySeconds": 0,
            "periodSeconds": 10,
            "timeoutSeconds": 1,
            "successThreshold": 1,
            "failureThreshold": 3
        }
    
    def liveness_http(
        self,
        path: str,
        port: Union[int, str] = 8080,
        host: Optional[str] = None,
        scheme: str = "HTTP",
        headers: Optional[Dict[str, str]] = None,
        **probe_config
    ) -> "Health":
        """
        Configure HTTP liveness probe.
        
        Args:
            path: HTTP path to check
            port: Port number or name
            host: Host header (defaults to pod IP)
            scheme: HTTP or HTTPS
            headers: HTTP headers
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        http_get = {
            "path": path,
            "port": port,
            "scheme": scheme
        }
        
        if host:
            http_get["host"] = host
        
        if headers:
            http_get["httpHeaders"] = [
                {"name": k, "value": v} for k, v in headers.items()
            ]
        
        self.liveness_probe = {
            **self._default_config,
            **probe_config,
            "httpGet": http_get
        }
        return self
    
    def readiness_http(
        self,
        path: str,
        port: Union[int, str] = 8080,
        host: Optional[str] = None,
        scheme: str = "HTTP",
        headers: Optional[Dict[str, str]] = None,
        **probe_config
    ) -> "Health":
        """
        Configure HTTP readiness probe.
        
        Args:
            path: HTTP path to check
            port: Port number or name
            host: Host header (defaults to pod IP)
            scheme: HTTP or HTTPS
            headers: HTTP headers
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        http_get = {
            "path": path,
            "port": port,
            "scheme": scheme
        }
        
        if host:
            http_get["host"] = host
        
        if headers:
            http_get["httpHeaders"] = [
                {"name": k, "value": v} for k, v in headers.items()
            ]
        
        self.readiness_probe = {
            **self._default_config,
            **probe_config,
            "httpGet": http_get
        }
        return self
    
    def startup_http(
        self,
        path: str,
        port: Union[int, str] = 8080,
        initial_delay: Union[str, int] = "30s",
        **probe_config
    ) -> "Health":
        """
        Configure HTTP startup probe.
        
        Args:
            path: HTTP path to check
            port: Port number or name
            initial_delay: Initial delay before first check
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        config = {
            **self._default_config,
            "initialDelaySeconds": self._parse_duration(initial_delay) if isinstance(initial_delay, str) else initial_delay,
            "periodSeconds": 5,  # More frequent checks for startup
            "failureThreshold": 30,  # Allow more failures during startup
            **probe_config
        }
        
        self.startup_probe = {
            **config,
            "httpGet": {
                "path": path,
                "port": port,
                "scheme": "HTTP"
            }
        }
        return self
    
    def liveness_tcp(self, port: Union[int, str], **probe_config) -> "Health":
        """
        Configure TCP liveness probe.
        
        Args:
            port: Port number or name
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        self.liveness_probe = {
            **self._default_config,
            **probe_config,
            "tcpSocket": {"port": port}
        }
        return self
    
    def readiness_tcp(self, port: Union[int, str], **probe_config) -> "Health":
        """
        Configure TCP readiness probe.
        
        Args:
            port: Port number or name
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        self.readiness_probe = {
            **self._default_config,
            **probe_config,
            "tcpSocket": {"port": port}
        }
        return self
    
    def liveness_exec(self, command: List[str], **probe_config) -> "Health":
        """
        Configure exec liveness probe.
        
        Args:
            command: Command to execute
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        self.liveness_probe = {
            **self._default_config,
            **probe_config,
            "exec": {"command": command}
        }
        return self
    
    def readiness_exec(self, command: List[str], **probe_config) -> "Health":
        """
        Configure exec readiness probe.
        
        Args:
            command: Command to execute
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        self.readiness_probe = {
            **self._default_config,
            **probe_config,
            "exec": {"command": command}
        }
        return self
    
    def startup_exec(self, command: List[str], initial_delay: Union[str, int] = "30s", **probe_config) -> "Health":
        """
        Configure exec startup probe.
        
        Args:
            command: Command to execute
            initial_delay: Initial delay before first check
            **probe_config: Additional probe configuration
            
        Returns:
            Health: Self for method chaining
        """
        config = {
            **self._default_config,
            "initialDelaySeconds": self._parse_duration(initial_delay) if isinstance(initial_delay, str) else initial_delay,
            "periodSeconds": 5,
            "failureThreshold": 30,
            **probe_config
        }
        
        self.startup_probe = {
            **config,
            "exec": {"command": command}
        }
        return self
    
    def initial_delay(self, delay: Union[str, int]) -> "Health":
        """
        Set initial delay for all probes.
        
        Args:
            delay: Initial delay in seconds or duration string
            
        Returns:
            Health: Self for method chaining
        """
        delay_seconds = self._parse_duration(delay) if isinstance(delay, str) else delay
        
        if self.liveness_probe:
            self.liveness_probe["initialDelaySeconds"] = delay_seconds
        if self.readiness_probe:
            self.readiness_probe["initialDelaySeconds"] = delay_seconds
        if self.startup_probe:
            self.startup_probe["initialDelaySeconds"] = delay_seconds
        
        return self
    
    def period(self, period: Union[str, int]) -> "Health":
        """
        Set period for all probes.
        
        Args:
            period: Period in seconds or duration string
            
        Returns:
            Health: Self for method chaining
        """
        period_seconds = self._parse_duration(period) if isinstance(period, str) else period
        
        if self.liveness_probe:
            self.liveness_probe["periodSeconds"] = period_seconds
        if self.readiness_probe:
            self.readiness_probe["periodSeconds"] = period_seconds
        if self.startup_probe:
            self.startup_probe["periodSeconds"] = period_seconds
        
        return self
    
    def timeout(self, timeout: Union[str, int]) -> "Health":
        """
        Set timeout for all probes.
        
        Args:
            timeout: Timeout in seconds or duration string
            
        Returns:
            Health: Self for method chaining
        """
        timeout_seconds = self._parse_duration(timeout) if isinstance(timeout, str) else timeout
        
        if self.liveness_probe:
            self.liveness_probe["timeoutSeconds"] = timeout_seconds
        if self.readiness_probe:
            self.readiness_probe["timeoutSeconds"] = timeout_seconds
        if self.startup_probe:
            self.startup_probe["timeoutSeconds"] = timeout_seconds
        
        return self
    
    def failure_threshold(self, threshold: int) -> "Health":
        """
        Set failure threshold for all probes.
        
        Args:
            threshold: Number of failures before marking as failed
            
        Returns:
            Health: Self for method chaining
        """
        if self.liveness_probe:
            self.liveness_probe["failureThreshold"] = threshold
        if self.readiness_probe:
            self.readiness_probe["failureThreshold"] = threshold
        if self.startup_probe:
            self.startup_probe["failureThreshold"] = threshold
        
        return self
    
    def success_threshold(self, threshold: int) -> "Health":
        """
        Set success threshold for readiness and startup probes.
        
        Args:
            threshold: Number of successes before marking as successful
            
        Returns:
            Health: Self for method chaining
        """
        if self.readiness_probe:
            self.readiness_probe["successThreshold"] = threshold
        if self.startup_probe:
            self.startup_probe["successThreshold"] = threshold
        
        return self
    
    # Pre-configured health check patterns
    
    @classmethod
    def web_application(
        cls,
        health_path: str = "/health",
        ready_path: str = "/ready",
        port: int = 8080
    ) -> "Health":
        """
        Create health checks for a typical web application.
        
        Args:
            health_path: Health check endpoint
            ready_path: Readiness check endpoint
            port: Application port
            
        Returns:
            Health: Configured health checks
        """
        return (cls()
            .liveness_http(health_path, port, periodSeconds=30, failureThreshold=3)
            .readiness_http(ready_path, port, periodSeconds=10, failureThreshold=2)
            .startup_http(health_path, port, initial_delay="30s", failureThreshold=30))
    
    @classmethod
    def database(
        cls,
        port: int = 5432,
        check_command: Optional[List[str]] = None
    ) -> "Health":
        """
        Create health checks for a database.
        
        Args:
            port: Database port
            check_command: Custom health check command
            
        Returns:
            Health: Configured health checks
        """
        health = cls()
        
        if check_command:
            health.liveness_exec(check_command, periodSeconds=30, failureThreshold=3)
            health.readiness_exec(check_command, periodSeconds=10, failureThreshold=2)
        else:
            health.liveness_tcp(port, periodSeconds=30, failureThreshold=3)
            health.readiness_tcp(port, periodSeconds=10, failureThreshold=2)
        
        return health
    
    @classmethod
    def microservice(
        cls,
        port: int = 8080,
        startup_delay: str = "15s"
    ) -> "Health":
        """
        Create health checks for a microservice.
        
        Args:
            port: Service port
            startup_delay: Initial startup delay
            
        Returns:
            Health: Configured health checks
        """
        return (cls()
            .liveness_http("/health", port, periodSeconds=20, failureThreshold=3)
            .readiness_http("/ready", port, periodSeconds=5, failureThreshold=2)
            .startup_http("/health", port, initial_delay=startup_delay, failureThreshold=20))
    
    @classmethod
    def batch_job(cls, check_file: str = "/tmp/healthy") -> "Health":
        """
        Create health checks for a batch job.
        
        Args:
            check_file: File to check for health status
            
        Returns:
            Health: Configured health checks
        """
        return (cls()
            .liveness_exec(["test", "-f", check_file], periodSeconds=60, failureThreshold=2)
            .readiness_exec(["test", "-f", check_file], periodSeconds=30, failureThreshold=1))
    
    def disable_liveness(self) -> "Health":
        """
        Disable liveness probe.
        
        Returns:
            Health: Self for method chaining
        """
        self.liveness_probe = None
        return self
    
    def disable_readiness(self) -> "Health":
        """
        Disable readiness probe.
        
        Returns:
            Health: Self for method chaining
        """
        self.readiness_probe = None
        return self
    
    def disable_startup(self) -> "Health":
        """
        Disable startup probe.
        
        Returns:
            Health: Self for method chaining
        """
        self.startup_probe = None
        return self
    
    def graceful_shutdown(
        self, 
        termination_grace_period: Union[str, int] = "30s"
    ) -> "Health":
        """
        Configure for graceful shutdown.
        
        Args:
            termination_grace_period: Grace period for termination
            
        Returns:
            Health: Self for method chaining
        """
        # Increase failure thresholds to allow graceful shutdown
        self.failure_threshold(5)
        
        # Store termination grace period for use in pod spec
        self._termination_grace_period = (
            self._parse_duration(termination_grace_period) 
            if isinstance(termination_grace_period, str) 
            else termination_grace_period
        )
        
        return self
    
    def fast_startup(self) -> "Health":
        """
        Configure for fast startup (aggressive probe settings).
        
        Returns:
            Health: Self for method chaining
        """
        if self.startup_probe:
            self.startup_probe.update({
                "initialDelaySeconds": 5,
                "periodSeconds": 2,
                "failureThreshold": 15
            })
        
        return self
    
    def slow_startup(self) -> "Health":
        """
        Configure for slow startup (patient probe settings).
        
        Returns:
            Health: Self for method chaining
        """
        if self.startup_probe:
            self.startup_probe.update({
                "initialDelaySeconds": 60,
                "periodSeconds": 10,
                "failureThreshold": 60
            })
        
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
        else:
            # Assume seconds if no unit
            return int(duration)
    
    def get_termination_grace_period(self) -> Optional[int]:
        """Get termination grace period if configured."""
        return getattr(self, '_termination_grace_period', None) 