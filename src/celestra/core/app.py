"""
App class for stateless applications in Celestraa DSL.

This module contains the App class which represents stateless applications
that don't require persistent storage.
"""

from typing import Dict, List, Any, Optional, Union
from .base_builder import BaseBuilder
from ..utils.decorators import docker_compose_only, kubernetes_only, output_formats


class App(BaseBuilder):
    """
    Builder class for stateless applications.
    
    The App class represents applications that are stateless and can be
    horizontally scaled without concerns about data persistence.
    
    Example:
        ```python
        app = (App("web-app")
            .image("web-server:latest")
            .port(8080)
            .resources(cpu="500m", memory="512Mi")
            .scale(replicas=3)
            .expose(external_access=True))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the App builder.
        
        Args:
            name: Name of the application
        """
        super().__init__(name)
        self._image: Optional[str] = None
        self._ports: List[Dict[str, Any]] = []
        self._environment: Dict[str, str] = {}
        self._resources: Dict[str, Any] = {}
        self._replicas: int = 1
        self._companions: List[Any] = []
        self._secrets: List[Any] = []
        self._config_maps: List[Any] = []
        self._storage: List[Any] = []
        self._dependencies: List[str] = []
        self._connections: List[str] = []
        self._lifecycle: Optional[Any] = None
        self._health: Optional[Any] = None
        self._scaling: Optional[Any] = None
        self._ingress: List[Any] = []
        self._service: Optional[Any] = None
        self._security_context: Optional[Dict[str, Any]] = None
        self._service_account_name: Optional[str] = None
        self._jobs: List[Any] = []
        self._build_context: Optional[str] = None
        self._dockerfile: Optional[str] = None
        self._build_args: Dict[str, str] = {}
    
    def image(self, image: str) -> "App":
        """
        Set the container image.
        
        Args:
            image: Container image name and tag
            
        Returns:
            App: Self for method chaining
        """
        self._image = image
        # Clear build context when using pre-built image
        self._build_context = None
        self._dockerfile = None
        self._build_args = {}
        return self

    def build(self, context: str, dockerfile: str = "Dockerfile", **build_args) -> "App":
        """
        Build container from local Dockerfile.
        
        This method configures the app to build from a local Dockerfile instead
        of using a pre-built image. Use this for local development or custom builds.
        
        Args:
            context: Build context path (relative to project root)
            dockerfile: Dockerfile path relative to context (default: "Dockerfile")
            **build_args: Build arguments to pass to Docker build
            
        Example:
            ```python
            # Build from current directory with custom Dockerfile
            app.build(".", "custom.Dockerfile", VERSION="1.0")
            
            # Build from subdirectory
            app.build("./backend", "Dockerfile.dev", ENV="development")
            ```
            
        Returns:
            App: Self for method chaining
        """
        self._build_context = context
        self._dockerfile = dockerfile
        self._build_args = dict(build_args)
        # Clear image when using build context
        self._image = None
        return self

    def from_dockerfile(self, dockerfile: str, context: str = ".", **build_args) -> "App":
        """
        Build from Dockerfile (alternative syntax).
        
        Alternative method for building from Dockerfile with dockerfile-first syntax.
        
        Args:
            dockerfile: Dockerfile path
            context: Build context path (default: current directory)
            **build_args: Build arguments
            
        Example:
            ```python
            app.from_dockerfile("Dockerfile.prod", context="./app", VERSION="2.0")
            ```
            
        Returns:
            App: Self for method chaining
        """
        return self.build(context, dockerfile, **build_args)

    @kubernetes_only  
    def node_selector(self, selectors: Dict[str, str]) -> "App":
        """
        Set node selector for pod scheduling (Kubernetes only).
        
        Args:
            selectors: Dictionary of node selector labels
            
        Example:
            ```python
            app.node_selector({"disktype": "ssd", "region": "us-west"})
            ```
            
        Returns:
            App: Self for method chaining
        """
        if not hasattr(self, '_node_selector'):
            self._node_selector = {}
        self._node_selector.update(selectors)
        return self

    @kubernetes_only
    def tolerations(self, tolerations: List[Dict[str, Any]]) -> "App":
        """
        Set pod tolerations for tainted nodes (Kubernetes only).
        
        Args:
            tolerations: List of toleration configurations
            
        Example:
            ```python
            app.tolerations([
                {"key": "special", "operator": "Equal", "value": "gpu", "effect": "NoSchedule"}
            ])
            ```
            
        Returns:
            App: Self for method chaining
        """
        if not hasattr(self, '_tolerations'):
            self._tolerations = []
        self._tolerations.extend(tolerations)
        return self
    
    def port(self, port: int, name: str = "http", protocol: str = "TCP") -> "App":
        """
        Add a port to the application.
        
        Args:
            port: Port number
            name: Port name (default: "http")
            protocol: Port protocol (default: "TCP")
            
        Returns:
            App: Self for method chaining
        """
        self._ports.append({
            "containerPort": port,
            "name": name,
            "protocol": protocol
        })
        return self

    @docker_compose_only
    def port_mapping(self, host_port: int, container_port: int, name: str = "http", protocol: str = "TCP") -> "App":
        """
        Add a port mapping (host:container) to the application.
        
        This is useful for Docker Compose where you want to map a different host port
        to the container port (e.g., host:8080 → container:80).
        
        Args:
            host_port: Host/external port number
            container_port: Container port number
            name: Port name (default: "http")
            protocol: Port protocol (default: "TCP")
            
        Example:
            ```python
            # Map host port 8080 to container port 80
            app.port_mapping(8080, 80, "http")
            ```
            
        Returns:
            App: Self for method chaining
        """
        self._ports.append({
            "containerPort": container_port,
            "hostPort": host_port,
            "name": name,
            "protocol": protocol
        })
        return self

    @docker_compose_only
    def expose_port(self, port: int, name: str = "http", protocol: str = "TCP", external_port: Optional[int] = None) -> "App":
        """
        Add a port and optionally expose it externally.
        
        Args:
            port: Container port number
            name: Port name (default: "http")
            protocol: Port protocol (default: "TCP")
            external_port: External/host port (if different from container port)
            
        Example:
            ```python
            # Container port 8080, exposed on host port 80
            app.expose_port(8080, "http", external_port=80)
            ```
            
        Returns:
            App: Self for method chaining
        """
        port_config = {
            "containerPort": port,
            "name": name,
            "protocol": protocol
        }
        
        if external_port is not None:
            port_config["hostPort"] = external_port
            
        self._ports.append(port_config)
        return self
    
    def add_port(self, port: int, name: str = "http", protocol: str = "TCP") -> "App":
        """
        Add a port to the application (alias for port() method).
        
        Args:
            port: Port number
            name: Port name
            protocol: Port protocol (default: "TCP")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, protocol)
    
    def ports(self, ports: List[Dict[str, Any]]) -> "App":
        """
        Set multiple ports for the application.
        
        Args:
            ports: List of port configurations with 'port', 'name', and optional 'protocol'
            
        Example:
            ```python
            app.ports([
                {"port": 8080, "name": "http"},
                {"port": 9090, "name": "metrics"},
                {"port": 8081, "name": "health"}
            ])
            ```
            
        Returns:
            App: Self for method chaining
        """
        for port_config in ports:
            self._ports.append({
                "containerPort": port_config.get("port"),
                "name": port_config.get("name", "http"),
                "protocol": port_config.get("protocol", "TCP")
            })
        return self
    
    def http_port(self, port: int = 8080, name: str = "http") -> "App":
        """
        Add HTTP port (convenience method).
        
        Args:
            port: HTTP port number (default: 8080)
            name: Port name (default: "http")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def https_port(self, port: int = 8443, name: str = "https") -> "App":
        """
        Add HTTPS port (convenience method).
        
        Args:
            port: HTTPS port number (default: 8443)
            name: Port name (default: "https")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def metrics_port(self, port: int = 9090, name: str = "metrics") -> "App":
        """
        Add metrics port (convenience method).
        
        Args:
            port: Metrics port number (default: 9090)
            name: Port name (default: "metrics")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def health_port(self, port: int = 8081, name: str = "health") -> "App":
        """
        Add health check port (convenience method).
        
        Args:
            port: Health check port number (default: 8081)
            name: Port name (default: "health")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def admin_port(self, port: int = 9000, name: str = "admin") -> "App":
        """
        Add admin/management port (convenience method).
        
        Args:
            port: Admin port number (default: 9000)
            name: Port name (default: "admin")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def grpc_port(self, port: int = 9090, name: str = "grpc") -> "App":
        """
        Add gRPC port (convenience method).
        
        Args:
            port: gRPC port number (default: 9090)
            name: Port name (default: "grpc")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def debug_port(self, port: int = 5005, name: str = "debug") -> "App":
        """
        Add debug port (convenience method).
        
        Args:
            port: Debug port number (default: 5005)
            name: Port name (default: "debug")
            
        Returns:
            App: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def common_ports(self, http: int = 8080, metrics: int = 9090, health: int = 8081) -> "App":
        """
        Add common application ports (convenience method).
        
        Args:
            http: HTTP port number (default: 8080)
            metrics: Metrics port number (default: 9090)
            health: Health check port number (default: 8081)
            
        Returns:
            App: Self for method chaining
        """
        return (self
            .http_port(http)
            .metrics_port(metrics)
            .health_port(health))
    
    def environment(self, env_vars: Dict[str, str]) -> "App":
        """
        Set environment variables.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            App: Self for method chaining
        """
        self._environment.update(env_vars)
        return self
    
    def env(self, key: str, value: str) -> "App":
        """
        Add a single environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            App: Self for method chaining
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
    ) -> "App":
        """
        Set resource requirements and limits.
        
        Args:
            cpu: CPU request (e.g., "500m")
            memory: Memory request (e.g., "512Mi")
            cpu_limit: CPU limit (e.g., "1000m")
            memory_limit: Memory limit (e.g., "1Gi")
            gpu: Number of GPUs required
            
        Returns:
            App: Self for method chaining
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
    
    def replicas(self, count: int) -> "App":
        """
        Set the number of replicas.
        
        Args:
            count: Number of replicas
            
        Returns:
            App: Self for method chaining
        """
        self._replicas = count
        return self
    
    def service_account(self, service_account_name: str) -> "App":
        """
        Set the service account name for the application.
        
        Args:
            service_account_name: Name of the service account to use
            
        Returns:
            App: Self for method chaining
        """
        self._service_account_name = service_account_name
        return self
    
    def scale(self, scaling_config: "Scaling") -> "App":
        """
        Set scaling configuration.
        
        Args:
            scaling_config: Scaling configuration object
            
        Returns:
            App: Self for method chaining
        """
        self._scaling = scaling_config
        if hasattr(scaling_config, 'replicas') and scaling_config.replicas:
            self._replicas = scaling_config.replicas
        return self
    
    def add_companion(self, companion: "Companion") -> "App":
        """
        Add a companion container (sidecar or init container).
        
        Args:
            companion: Companion container configuration
            
        Returns:
            App: Self for method chaining
        """
        self._companions.append(companion)
        return self
    
    def add_companions(self, companions: List["Companion"]) -> "App":
        """
        Add multiple companion containers.
        
        Args:
            companions: List of companion configurations
            
        Returns:
            App: Self for method chaining
        """
        self._companions.extend(companions)
        return self
    
    def add_secret(self, secret: "Secret") -> "App":
        """
        Add a secret to the application.
        
        Args:
            secret: Secret configuration
            
        Returns:
            App: Self for method chaining
        """
        self._secrets.append(secret)
        return self
    
    def add_secrets(self, secrets: List["Secret"]) -> "App":
        """
        Add multiple secrets to the application.
        
        Args:
            secrets: List of secret configurations
            
        Returns:
            App: Self for method chaining
        """
        self._secrets.extend(secrets)
        return self
    
    def add_config(self, config_map: "ConfigMap") -> "App":
        """
        Add a ConfigMap to the application.
        
        Args:
            config_map: ConfigMap configuration
            
        Returns:
            App: Self for method chaining
        """
        self._config_maps.append(config_map)
        return self
    
    def add_configs(self, config_maps: List["ConfigMap"]) -> "App":
        """
        Add multiple ConfigMaps to the application.
        
        Args:
            config_maps: List of ConfigMap configurations
            
        Returns:
            App: Self for method chaining
        """
        self._config_maps.extend(config_maps)
        return self
    
    def add_storage(self, storage: "Storage") -> "App":
        """
        Add storage to the application.
        
        Args:
            storage: Storage configuration
            
        Returns:
            App: Self for method chaining
        """
        self._storage.append(storage)
        return self
    
    def connect_to(self, services: List[str]) -> "App":
        """
        Connect to other services.
        
        Args:
            services: List of service names to connect to
            
        Returns:
            App: Self for method chaining
        """
        self._connections.extend(services)
        return self
    
    def depends_on(self, dependencies: List[str]) -> "App":
        """
        Set service dependencies.
        
        Args:
            dependencies: List of service names this app depends on
            
        Returns:
            App: Self for method chaining
        """
        self._dependencies.extend(dependencies)
        return self
    
    def lifecycle(self, lifecycle_config: "Lifecycle") -> "App":
        """
        Set lifecycle configuration.
        
        Args:
            lifecycle_config: Lifecycle configuration
            
        Returns:
            App: Self for method chaining
        """
        self._lifecycle = lifecycle_config
        return self
    
    def health(self, health_config: "Health") -> "App":
        """
        Set health check configuration.
        
        Args:
            health_config: Health check configuration
            
        Returns:
            App: Self for method chaining
        """
        self._health = health_config
        return self
    
    def expose(
        self, 
        external_access: bool = False,
        domain: Optional[str] = None,
        service_type: str = "ClusterIP"
    ) -> "App":
        """
        Expose the application as a service.
        
        Args:
            external_access: Whether to allow external access
            domain: Domain name for ingress
            service_type: Kubernetes service type
            
        Returns:
            App: Self for method chaining
        """
        from ..networking.service import Service
        from ..networking.ingress import Ingress
        
        # Create service
        service = Service(f"{self._name}-service")
        for port in self._ports:
            service.add_port(
                name=port["name"],
                port=port["containerPort"], 
                target_port=port["containerPort"]
            )
        
        if external_access:
            service.type("LoadBalancer")
        else:
            service.type(service_type)
        
        self._service = service
        
        # Create ingress if domain specified
        if domain:
            ingress = Ingress(f"{self._name}-ingress")
            ingress.host(domain)
            for port in self._ports:
                ingress.path("/", self._name, port["containerPort"])
            self._ingress.append(ingress)
        
        return self
    
    def add_ingress(self, ingress: "Ingress") -> "App":
        """
        Add an ingress configuration.
        
        Args:
            ingress: Ingress configuration
            
        Returns:
            App: Self for method chaining
        """
        self._ingress.append(ingress)
        return self
    
    def security_context(self, context: Dict[str, Any]) -> "App":
        """
        Set security context.
        
        Args:
            context: Security context configuration
            
        Returns:
            App: Self for method chaining
        """
        self._security_context = context
        return self
    
    def add_job(self, job: "Job") -> "App":
        """
        Add a related job.
        
        Args:
            job: Job configuration
            
        Returns:
            App: Self for method chaining
        """
        self._jobs.append(job)
        return self
    
    def add_jobs(self, jobs: List["Job"]) -> "App":
        """
        Add multiple related jobs.
        
        Args:
            jobs: List of job configurations
            
        Returns:
            App: Self for method chaining
        """
        self._jobs.extend(jobs)
        return self
    
    def for_environment(self, environment: str) -> "App":
        """
        Create environment-specific configuration.
        
        Args:
            environment: Environment name (dev, staging, prod)
            
        Returns:
            App: Cloned app with environment-specific config
        """
        cloned = self.clone()
        cloned.add_label("environment", environment)
        return cloned
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for the application.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resource dictionaries
        """
        resources = []
        
        # Generate Deployment
        deployment = self._generate_deployment()
        resources.append(deployment)
        
        # Generate Service
        if self._service or self._ports:
            service = self._generate_service()
            resources.append(service)
        
        # Generate Ingress
        for ingress in self._ingress:
            if hasattr(ingress, 'generate_kubernetes_resources'):
                resources.extend(ingress.generate_kubernetes_resources())
        
        # Generate ConfigMaps
        for config_map in self._config_maps:
            if hasattr(config_map, 'generate_kubernetes_resources'):
                resources.extend(config_map.generate_kubernetes_resources())
        
        # Generate Secrets
        for secret in self._secrets:
            if hasattr(secret, 'generate_kubernetes_resources'):
                resources.extend(secret.generate_kubernetes_resources())
        
        # Generate Jobs
        for job in self._jobs:
            if hasattr(job, 'generate_kubernetes_resources'):
                resources.extend(job.generate_kubernetes_resources())
        
        # Generate HPA if scaling is configured
        if self._scaling and hasattr(self._scaling, 'auto_scale_enabled'):
            if self._scaling.auto_scale_enabled:
                hpa = self._generate_hpa()
                resources.append(hpa)
        
        return resources
    
    def _generate_deployment(self) -> Dict[str, Any]:
        """Generate Kubernetes Deployment resource."""
        container = {
            "name": self._name,
            "image": self._image or "nginx:latest",
            "ports": self._ports if self._ports else [{"containerPort": 80, "name": "http"}]
        }
        
        # Add environment variables
        if self._environment:
            container["env"] = [
                {"name": k, "value": v} for k, v in self._environment.items()
            ]
        
        # Add resources
        if self._resources:
            container["resources"] = self._resources
        
        # Add health checks
        if self._health:
            if hasattr(self._health, 'liveness_probe'):
                container["livenessProbe"] = self._health.liveness_probe
            if hasattr(self._health, 'readiness_probe'):
                container["readiness_probe"] = self._health.readiness_probe
            if hasattr(self._health, 'startup_probe'):
                container["startupProbe"] = self._health.startup_probe
        
        # Add lifecycle
        if self._lifecycle:
            if hasattr(self._lifecycle, 'to_dict'):
                container["lifecycle"] = self._lifecycle.to_dict()
        
        # Add security context
        if self._security_context:
            container["securityContext"] = self._security_context
        
        deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "replicas": self._replicas,
                "selector": {
                    "matchLabels": {"app": self._name}
                },
                "template": {
                    "metadata": {
                        "labels": self._labels
                    },
                    "spec": {
                        "containers": [container]
                    }
                }
            }
        }
        
        if self._namespace:
            deployment["metadata"]["namespace"] = self._namespace
        
        # Add init containers
        init_containers = [c for c in self._companions if hasattr(c, 'type') and c.type == 'init']
        if init_containers:
            deployment["spec"]["template"]["spec"]["initContainers"] = [
                c.to_dict() for c in init_containers
            ]
        
        # Add sidecar containers
        sidecar_containers = [c for c in self._companions if hasattr(c, 'type') and c.type == 'sidecar']
        if sidecar_containers:
            deployment["spec"]["template"]["spec"]["containers"].extend([
                c.to_dict() for c in sidecar_containers
            ])
        
        # Add service account
        if self._service_account_name:
            deployment["spec"]["template"]["spec"]["serviceAccountName"] = self._service_account_name
        
        return deployment
    
    def _generate_service(self) -> Dict[str, Any]:
        """Generate Kubernetes Service resource."""
        if self._service:
            return self._service.generate_kubernetes_resources()[0]
        
        # Generate default service
        ports = []
        for port in self._ports:
            ports.append({
                "name": port["name"],
                "port": port["containerPort"],
                "targetPort": port["containerPort"],
                "protocol": port.get("protocol", "TCP")
            })
        
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "selector": {"app": self._name},
                "ports": ports,
                "type": "ClusterIP"
            }
        }
        
        if self._namespace:
            service["metadata"]["namespace"] = self._namespace
        
        return service
    
    def _generate_hpa(self) -> Dict[str, Any]:
        """Generate Kubernetes HorizontalPodAutoscaler resource."""
        hpa = {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {
                "name": f"{self._name}-hpa",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "scaleTargetRef": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "name": self._name
                },
                "minReplicas": getattr(self._scaling, 'min_replicas', 1),
                "maxReplicas": getattr(self._scaling, 'max_replicas', 10),
                "metrics": []
            }
        }
        
        if hasattr(self._scaling, 'cpu_target'):
            hpa["spec"]["metrics"].append({
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": self._scaling.cpu_target
                    }
                }
            })
        
        if self._namespace:
            hpa["metadata"]["namespace"] = self._namespace
        
        return hpa 