"""
Companion class for sidecar and init containers in Celestraa DSL.

This module contains the Companion class for managing sidecar containers
and init containers that support the main application.
"""

from typing import Dict, List, Any, Optional, Union


class Companion:
    """
    Builder class for companion containers (sidecars and init containers).
    
    The Companion class manages containers that run alongside or before
    the main application container to provide supporting functionality.
    
    Example:
        ```python
        # Sidecar container
        logging_sidecar = (Companion("log-shipper", "sidecar")
            .image("log-agent:latest")
            .resources(cpu="100m", memory="128Mi")
            .mount_volume("app-logs", "/var/log/app"))
        
        # Init container
        db_migration = (Companion("db-migrate", "init")
            .image("migration-tool:latest")
            .command(["migrate", "--up"])
            .wait_for_completion())
        ```
    """
    
    def __init__(self, name: str, container_type: str = "sidecar"):
        """
        Initialize the Companion builder.
        
        Args:
            name: Name of the companion container
            container_type: Type of container ("sidecar" or "init")
        """
        if container_type not in ["sidecar", "init"]:
            raise ValueError("Container type must be 'sidecar' or 'init'")
        
        self.name = name
        self.type = container_type
        self._image: Optional[str] = None
        self._command: List[str] = []
        self._args: List[str] = []
        self._environment: Dict[str, str] = {}
        self._resources: Dict[str, Any] = {}
        self._volume_mounts: List[Dict[str, Any]] = []
        self._ports: List[Dict[str, Any]] = []
        self._security_context: Optional[Dict[str, Any]] = None
        self._working_dir: Optional[str] = None
        self._restart_policy: Optional[str] = None
        self._image_pull_policy: str = "IfNotPresent"
        self._stdin: bool = False
        self._tty: bool = False
    
    def image(self, image: str) -> "Companion":
        """
        Set the container image.
        
        Args:
            image: Container image name and tag
            
        Returns:
            Companion: Self for method chaining
        """
        self._image = image
        return self
    
    def command(self, command: List[str]) -> "Companion":
        """
        Set the command to run in the container.
        
        Args:
            command: List of command arguments
            
        Returns:
            Companion: Self for method chaining
        """
        self._command = command
        return self
    
    def args(self, args: List[str]) -> "Companion":
        """
        Set the arguments for the command.
        
        Args:
            args: List of command arguments
            
        Returns:
            Companion: Self for method chaining
        """
        self._args = args
        return self
    
    def environment(self, env_vars: Dict[str, str]) -> "Companion":
        """
        Set environment variables.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            Companion: Self for method chaining
        """
        self._environment.update(env_vars)
        return self
    
    def env(self, key: str, value: str) -> "Companion":
        """
        Add a single environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            Companion: Self for method chaining
        """
        self._environment[key] = value
        return self
    
    def resources(
        self, 
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        cpu_limit: Optional[str] = None,
        memory_limit: Optional[str] = None
    ) -> "Companion":
        """
        Set resource requirements and limits.
        
        Args:
            cpu: CPU request (e.g., "100m")
            memory: Memory request (e.g., "128Mi")
            cpu_limit: CPU limit (e.g., "500m")
            memory_limit: Memory limit (e.g., "256Mi")
            
        Returns:
            Companion: Self for method chaining
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
        
        return self
    
    def mount_volume(self, volume_name: str, mount_path: str, read_only: bool = False) -> "Companion":
        """
        Mount a volume in the container.
        
        Args:
            volume_name: Name of the volume to mount
            mount_path: Path where to mount the volume
            read_only: Whether to mount as read-only
            
        Returns:
            Companion: Self for method chaining
        """
        self._volume_mounts.append({
            "name": volume_name,
            "mountPath": mount_path,
            "readOnly": read_only
        })
        return self
    
    def port(self, port: int, name: str = "http", protocol: str = "TCP") -> "Companion":
        """
        Add a port to the companion container.
        
        Args:
            port: Port number
            name: Port name
            protocol: Port protocol
            
        Returns:
            Companion: Self for method chaining
        """
        self._ports.append({
            "containerPort": port,
            "name": name,
            "protocol": protocol
        })
        return self
    
    def security_context(self, context: Dict[str, Any]) -> "Companion":
        """
        Set security context for the container.
        
        Args:
            context: Security context configuration
            
        Returns:
            Companion: Self for method chaining
        """
        self._security_context = context
        return self
    
    def working_directory(self, workdir: str) -> "Companion":
        """
        Set the working directory for the container.
        
        Args:
            workdir: Working directory path
            
        Returns:
            Companion: Self for method chaining
        """
        self._working_dir = workdir
        return self
    
    def image_pull_policy(self, policy: str) -> "Companion":
        """
        Set the image pull policy.
        
        Args:
            policy: Pull policy ("Always", "IfNotPresent", "Never")
            
        Returns:
            Companion: Self for method chaining
        """
        if policy not in ["Always", "IfNotPresent", "Never"]:
            raise ValueError("Image pull policy must be 'Always', 'IfNotPresent', or 'Never'")
        self._image_pull_policy = policy
        return self
    
    def stdin(self, enabled: bool = True) -> "Companion":
        """
        Enable stdin for the container.
        
        Args:
            enabled: Whether to enable stdin
            
        Returns:
            Companion: Self for method chaining
        """
        self._stdin = enabled
        return self
    
    def tty(self, enabled: bool = True) -> "Companion":
        """
        Enable TTY for the container.
        
        Args:
            enabled: Whether to enable TTY
            
        Returns:
            Companion: Self for method chaining
        """
        self._tty = enabled
        return self
    
    # Pre-built companion configurations
    
    @classmethod
    def logging_sidecar(
        cls, 
        name: str = "log-shipper",
        image: str = "log-agent:latest",
        log_path: str = "/var/log/app"
    ) -> "Companion":
        """
        Create a logging sidecar container.
        
        Args:
            name: Container name
            image: Log agent image
            log_path: Path to application logs
            
        Returns:
            Companion: Configured logging sidecar
        """
        return (cls(name, "sidecar")
            .image(image)
            .resources(cpu="50m", memory="64Mi")
            .mount_volume("app-logs", log_path, read_only=True)
            .environment({
                "LOG_LEVEL": "info",
                "OUTPUT": "stdout"
            }))
    
    @classmethod
    def monitoring_sidecar(
        cls, 
        name: str = "metrics-exporter",
        image: str = "metrics-exporter:latest",
        metrics_port: int = 9090
    ) -> "Companion":
        """
        Create a monitoring/metrics sidecar container.
        
        Args:
            name: Container name
            image: Metrics exporter image
            metrics_port: Port for metrics endpoint
            
        Returns:
            Companion: Configured monitoring sidecar
        """
        return (cls(name, "sidecar")
            .image(image)
            .port(metrics_port, "metrics")
            .resources(cpu="50m", memory="64Mi")
            .environment({
                "METRICS_PORT": str(metrics_port),
                "SCRAPE_INTERVAL": "30s"
            }))
    
    @classmethod
    def proxy_sidecar(
        cls, 
        name: str = "proxy",
        image: str = "envoy:latest",
        proxy_port: int = 8080,
        admin_port: int = 9901
    ) -> "Companion":
        """
        Create a proxy sidecar container (e.g., Envoy, nginx).
        
        Args:
            name: Container name
            image: Proxy image
            proxy_port: Port for proxy traffic
            admin_port: Port for admin interface
            
        Returns:
            Companion: Configured proxy sidecar
        """
        return (cls(name, "sidecar")
            .image(image)
            .port(proxy_port, "proxy")
            .port(admin_port, "admin")
            .resources(cpu="100m", memory="128Mi")
            .mount_volume("proxy-config", "/etc/proxy")
            .environment({
                "PROXY_PORT": str(proxy_port),
                "ADMIN_PORT": str(admin_port)
            }))
    
    @classmethod
    def database_migration_init(
        cls, 
        name: str = "db-migrate",
        image: str = "migration-tool:latest",
        migration_command: List[str] = ["migrate", "--up"]
    ) -> "Companion":
        """
        Create a database migration init container.
        
        Args:
            name: Container name
            image: Migration tool image
            migration_command: Migration command to run
            
        Returns:
            Companion: Configured migration init container
        """
        return (cls(name, "init")
            .image(image)
            .command(migration_command)
            .resources(cpu="200m", memory="256Mi")
            .environment({
                "MIGRATION_MODE": "up",
                "WAIT_FOR_DB": "true"
            }))
    
    @classmethod
    def secret_init(
        cls, 
        name: str = "secret-fetcher",
        image: str = "secret-manager:latest",
        secret_path: str = "/secrets"
    ) -> "Companion":
        """
        Create a secret fetching init container.
        
        Args:
            name: Container name
            image: Secret management image
            secret_path: Path to store secrets
            
        Returns:
            Companion: Configured secret init container
        """
        return (cls(name, "init")
            .image(image)
            .mount_volume("secrets", secret_path)
            .resources(cpu="100m", memory="128Mi")
            .environment({
                "SECRET_PATH": secret_path,
                "SECRET_FORMAT": "env"
            }))
    
    @classmethod
    def dependency_wait_init(
        cls, 
        name: str = "wait-for-deps",
        image: str = "busybox:latest",
        dependencies: List[str] = None
    ) -> "Companion":
        """
        Create a dependency waiting init container.
        
        Args:
            name: Container name
            image: Wait utility image
            dependencies: List of services to wait for
            
        Returns:
            Companion: Configured dependency wait init container
        """
        deps = dependencies or []
        wait_commands = []
        
        for dep in deps:
            wait_commands.append(f"until nslookup {dep}; do sleep 1; done")
        
        command = ["sh", "-c", " && ".join(wait_commands)] if wait_commands else ["true"]
        
        return (cls(name, "init")
            .image(image)
            .command(command)
            .resources(cpu="50m", memory="32Mi"))
    
    def wait_for_completion(self) -> "Companion":
        """
        Configure init container to wait for completion (init containers only).
        
        Returns:
            Companion: Self for method chaining
        """
        if self.type != "init":
            raise ValueError("wait_for_completion() can only be used with init containers")
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert companion configuration to dictionary for Kubernetes spec.
        
        Returns:
            Dict[str, Any]: Container specification
        """
        container_spec = {
            "name": self.name,
            "image": self._image or "busybox:latest"
        }
        
        # Add command and args
        if self._command:
            container_spec["command"] = self._command
        if self._args:
            container_spec["args"] = self._args
        
        # Add environment variables
        if self._environment:
            container_spec["env"] = [
                {"name": k, "value": v} for k, v in self._environment.items()
            ]
        
        # Add resources
        if self._resources:
            container_spec["resources"] = self._resources
        
        # Add volume mounts
        if self._volume_mounts:
            container_spec["volumeMounts"] = self._volume_mounts
        
        # Add ports (for sidecars)
        if self._ports and self.type == "sidecar":
            container_spec["ports"] = self._ports
        
        # Add security context
        if self._security_context:
            container_spec["securityContext"] = self._security_context
        
        # Add working directory
        if self._working_dir:
            container_spec["workingDir"] = self._working_dir
        
        # Add image pull policy
        if self._image_pull_policy != "IfNotPresent":
            container_spec["imagePullPolicy"] = self._image_pull_policy
        
        # Add stdin/tty
        if self._stdin:
            container_spec["stdin"] = self._stdin
        if self._tty:
            container_spec["tty"] = self._tty
        
        return container_spec 