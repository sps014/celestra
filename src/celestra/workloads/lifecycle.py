"""
Lifecycle class for container lifecycle management in Celestraa DSL.

This module contains the Lifecycle class for handling container lifecycle
hooks and termination settings.
"""

from typing import Dict, List, Any, Optional, Union


class Lifecycle:
    """
    Builder class for container lifecycle configuration.
    
    The Lifecycle class manages container lifecycle hooks including
    postStart and preStop events, and termination settings.
    
    Example:
        ```python
        lifecycle = (Lifecycle()
            .post_start_exec(["sh", "-c", "echo 'Container started'"])
            .pre_stop_http("http://localhost:8080/shutdown")
            .termination_grace_period("30s"))
        ```
    """
    
    def __init__(self):
        """Initialize the Lifecycle builder."""
        self._post_start: Optional[Dict[str, Any]] = None
        self._pre_stop: Optional[Dict[str, Any]] = None
        self._termination_grace_period_seconds: Optional[int] = None
    
    def post_start_exec(self, command: List[str]) -> "Lifecycle":
        """
        Set postStart hook with exec action.
        
        Args:
            command: Command to execute after container starts
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self._post_start = {
            "exec": {
                "command": command
            }
        }
        return self
    
    def post_start_http(
        self, 
        path: str,
        port: Union[int, str] = 8080,
        host: Optional[str] = None,
        scheme: str = "HTTP",
        headers: Optional[Dict[str, str]] = None
    ) -> "Lifecycle":
        """
        Set postStart hook with HTTP GET action.
        
        Args:
            path: HTTP path to request
            port: Port number or name
            host: Host name (defaults to pod IP)
            scheme: HTTP or HTTPS
            headers: HTTP headers
            
        Returns:
            Lifecycle: Self for method chaining
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
        
        self._post_start = {"httpGet": http_get}
        return self
    
    def pre_stop_exec(self, command: List[str]) -> "Lifecycle":
        """
        Set preStop hook with exec action.
        
        Args:
            command: Command to execute before container stops
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self._pre_stop = {
            "exec": {
                "command": command
            }
        }
        return self
    
    def pre_stop_http(
        self, 
        path: str,
        port: Union[int, str] = 8080,
        host: Optional[str] = None,
        scheme: str = "HTTP",
        headers: Optional[Dict[str, str]] = None
    ) -> "Lifecycle":
        """
        Set preStop hook with HTTP GET action.
        
        Args:
            path: HTTP path to request
            port: Port number or name
            host: Host name (defaults to pod IP)
            scheme: HTTP or HTTPS
            headers: HTTP headers
            
        Returns:
            Lifecycle: Self for method chaining
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
        
        self._pre_stop = {"httpGet": http_get}
        return self
    
    def termination_grace_period(self, period: Union[str, int]) -> "Lifecycle":
        """
        Set termination grace period.
        
        Args:
            period: Grace period in seconds or duration string (e.g., "30s")
            
        Returns:
            Lifecycle: Self for method chaining
        """
        if isinstance(period, str):
            # Parse duration string
            self._termination_grace_period_seconds = self._parse_duration(period)
        else:
            self._termination_grace_period_seconds = period
        return self
    
    def graceful_shutdown(self, signal_path: str, grace_period: Union[str, int] = "30s") -> "Lifecycle":
        """
        Configure graceful shutdown with HTTP endpoint.
        
        Args:
            signal_path: HTTP path to signal shutdown
            grace_period: Grace period for shutdown
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self.pre_stop_http(signal_path)
        self.termination_grace_period(grace_period)
        return self
    
    def health_check_wait(self, path: str = "/health", timeout: Union[str, int] = "30s") -> "Lifecycle":
        """
        Wait for health check to pass after start.
        
        Args:
            path: Health check path
            timeout: Timeout for health check
            
        Returns:
            Lifecycle: Self for method chaining
        """
        # Wait for health check
        self.post_start_exec([
            "sh", "-c", 
            f"timeout {timeout if isinstance(timeout, str) else f'{timeout}s'} "
            f"sh -c 'until curl -f http://localhost:8080{path}; do sleep 1; done'"
        ])
        return self
    
    def database_migration(
        self, 
        migration_command: List[str],
        health_check_path: str = "/health"
    ) -> "Lifecycle":
        """
        Run database migration after container starts.
        
        Args:
            migration_command: Command to run migrations
            health_check_path: Health check path to verify readiness
            
        Returns:
            Lifecycle: Self for method chaining
        """
        # Run migration then wait for health check
        full_command = migration_command + [
            "&&", "sh", "-c",
            f"until curl -f http://localhost:8080{health_check_path}; do sleep 1; done"
        ]
        self.post_start_exec(["sh", "-c", " ".join(full_command)])
        return self
    
    def cache_warmup(self, warmup_endpoint: str) -> "Lifecycle":
        """
        Warm up cache after container starts.
        
        Args:
            warmup_endpoint: HTTP endpoint to trigger cache warmup
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self.post_start_http(warmup_endpoint)
        return self
    
    def register_service(self, registry_endpoint: str) -> "Lifecycle":
        """
        Register service with service discovery.
        
        Args:
            registry_endpoint: Service registry endpoint
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self.post_start_http(registry_endpoint)
        return self
    
    def deregister_service(self, registry_endpoint: str) -> "Lifecycle":
        """
        Deregister service from service discovery.
        
        Args:
            registry_endpoint: Service registry endpoint
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self.pre_stop_http(registry_endpoint)
        return self
    
    def drain_connections(self, drain_endpoint: str, grace_period: Union[str, int] = "30s") -> "Lifecycle":
        """
        Drain connections before stopping.
        
        Args:
            drain_endpoint: Endpoint to signal connection draining
            grace_period: Grace period for draining
            
        Returns:
            Lifecycle: Self for method chaining
        """
        self.pre_stop_http(drain_endpoint)
        self.termination_grace_period(grace_period)
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
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert lifecycle configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Lifecycle configuration
        """
        lifecycle_config = {}
        
        if self._post_start:
            lifecycle_config["postStart"] = self._post_start
        
        if self._pre_stop:
            lifecycle_config["preStop"] = self._pre_stop
        
        return lifecycle_config
    
    def get_termination_grace_period(self) -> Optional[int]:
        """
        Get termination grace period.
        
        Returns:
            Optional[int]: Termination grace period in seconds
        """
        return self._termination_grace_period_seconds
    
    @property
    def liveness_probe(self) -> Optional[Dict[str, Any]]:
        """Get liveness probe configuration if available."""
        return None
    
    @property
    def readiness_probe(self) -> Optional[Dict[str, Any]]:
        """Get readiness probe configuration if available."""
        return None
    
    @property
    def startup_probe(self) -> Optional[Dict[str, Any]]:
        """Get startup probe configuration if available."""
        return None 