"""
AppGroup class for multi-service applications in Celestraa DSL.

This module contains the AppGroup class which manages multiple related services
and provides cross-service configuration capabilities.
"""

from typing import Dict, List, Any, Optional, Union
from .base_builder import BaseBuilder


class AppGroup(BaseBuilder):
    """
    Builder class for managing multiple related services.
    
    The AppGroup class allows you to define and manage multiple applications
    and stateful services together, providing cross-service configuration
    and coordinated deployment.
    
    Example:
        ```python
        platform = AppGroup("ecommerce")
        
        database = StatefulApp("database").image("database-server:latest")
        cache = StatefulApp("cache").image("cache-server:latest")
        api = App("api").image("api-server:latest")
        
        platform.add_services([database, cache, api])
        platform.configure_networking(allow_internal_communication=True)
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the AppGroup builder.
        
        Args:
            name: Name of the application group
        """
        super().__init__(name)
        self._services: List[BaseBuilder] = []
        self._shared_secrets: List[Any] = []
        self._shared_configs: List[Any] = []
        self._network_policies: List[Any] = []
        self._service_mesh_config: Optional[Dict[str, Any]] = None
        self._monitoring_config: Optional[Dict[str, Any]] = None
        self._security_policies: List[Any] = []
        self._dependencies: Dict[str, List[str]] = {}
        self._environment_configs: Dict[str, Dict[str, Any]] = {}
        self._resource_quotas: Optional[Dict[str, Any]] = None
        self._namespace_config: Optional[Dict[str, Any]] = None
    
    def add_service(self, service: BaseBuilder) -> "AppGroup":
        """
        Add a service to the group.
        
        Args:
            service: Service to add (App or StatefulApp)
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._services.append(service)
        return self
    
    def add_services(self, services: List[BaseBuilder]) -> "AppGroup":
        """
        Add multiple services to the group.
        
        Args:
            services: List of services to add
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._services.extend(services)
        return self
    
    def remove_service(self, service_name: str) -> "AppGroup":
        """
        Remove a service from the group by name.
        
        Args:
            service_name: Name of the service to remove
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._services = [s for s in self._services if s.name != service_name]
        return self
    
    def get_service(self, service_name: str) -> Optional[BaseBuilder]:
        """
        Get a service by name.
        
        Args:
            service_name: Name of the service to get
            
        Returns:
            Optional[BaseBuilder]: Service if found, None otherwise
        """
        for service in self._services:
            if service.name == service_name:
                return service
        return None
    
    def add_shared_secret(self, secret: "Secret") -> "AppGroup":
        """
        Add a shared secret accessible by all services.
        
        Args:
            secret: Secret configuration
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._shared_secrets.append(secret)
        return self
    
    def add_shared_config(self, config_map: "ConfigMap") -> "AppGroup":
        """
        Add a shared ConfigMap accessible by all services.
        
        Args:
            config_map: ConfigMap configuration
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._shared_configs.append(config_map)
        return self
    
    def configure_networking(
        self,
        allow_internal_communication: bool = True,
        deny_external_access_except: Optional[List[str]] = None,
        service_mesh: bool = False,
        mesh_config: Optional[Dict[str, Any]] = None
    ) -> "AppGroup":
        """
        Configure networking policies for the group.
        
        Args:
            allow_internal_communication: Allow communication between services
            deny_external_access_except: List of services that can accept external traffic
            service_mesh: Enable service mesh integration
            mesh_config: Service mesh configuration
            
        Returns:
            AppGroup: Self for method chaining
        """
        from ..networking.network_policy import NetworkPolicy
        
        if allow_internal_communication:
            # Create network policy allowing internal communication
            internal_policy = (NetworkPolicy(f"{self._name}-internal")
                .allow_internal_communication()
                .apply_to_services([s.name for s in self._services]))
            self._network_policies.append(internal_policy)
        
        if deny_external_access_except:
            # Create network policy denying external access except for specified services
            external_policy = (NetworkPolicy(f"{self._name}-external")
                .deny_external_access_except(deny_external_access_except))
            self._network_policies.append(external_policy)
        
        if service_mesh:
            self._service_mesh_config = mesh_config or {}
        
        return self
    
    def configure_monitoring(
        self,
        prometheus_enabled: bool = True,
        grafana_enabled: bool = True,
        jaeger_enabled: bool = False,
        custom_metrics: Optional[List[str]] = None
    ) -> "AppGroup":
        """
        Configure monitoring for all services in the group.
        
        Args:
            prometheus_enabled: Enable Prometheus monitoring
            grafana_enabled: Enable Grafana dashboards
            jaeger_enabled: Enable Jaeger tracing
            custom_metrics: List of custom metrics to collect
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._monitoring_config = {
            "prometheus": prometheus_enabled,
            "grafana": grafana_enabled,
            "jaeger": jaeger_enabled,
            "custom_metrics": custom_metrics or []
        }
        return self
    
    def configure_security(
        self,
        rbac_enabled: bool = True,
        pod_security_policy: Optional[str] = None,
        network_policies: bool = True,
        security_context: Optional[Dict[str, Any]] = None
    ) -> "AppGroup":
        """
        Configure security policies for the group.
        
        Args:
            rbac_enabled: Enable RBAC policies
            pod_security_policy: Pod security policy name
            network_policies: Enable network policies
            security_context: Default security context for all services
            
        Returns:
            AppGroup: Self for method chaining
        """
        from ..security.security_policy import SecurityPolicy
        
        security_policy = SecurityPolicy(f"{self._name}-security")
        
        if rbac_enabled:
            security_policy.enable_rbac()
        
        if pod_security_policy:
            security_policy.pod_security_policy(pod_security_policy)
        
        if network_policies:
            security_policy.enable_network_policies()
        
        if security_context:
            security_policy.default_security_context(security_context)
        
        self._security_policies.append(security_policy)
        return self
    
    def set_dependencies(self, dependencies: Dict[str, List[str]]) -> "AppGroup":
        """
        Set dependencies between services in the group.
        
        Args:
            dependencies: Dictionary mapping service names to their dependencies
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._dependencies.update(dependencies)
        return self
    
    def add_dependency(self, service: str, depends_on: Union[str, List[str]]) -> "AppGroup":
        """
        Add a dependency for a service.
        
        Args:
            service: Service name
            depends_on: Service or list of services it depends on
            
        Returns:
            AppGroup: Self for method chaining
        """
        if isinstance(depends_on, str):
            depends_on = [depends_on]
        
        if service not in self._dependencies:
            self._dependencies[service] = []
        
        self._dependencies[service].extend(depends_on)
        return self
    
    def for_environment(
        self, 
        environment: str,
        config_overrides: Optional[Dict[str, Any]] = None
    ) -> "AppGroup":
        """
        Create environment-specific configuration.
        
        Args:
            environment: Environment name (dev, staging, prod)
            config_overrides: Environment-specific configuration overrides
            
        Returns:
            AppGroup: Cloned group with environment-specific config
        """
        cloned = self.clone()
        cloned.add_label("environment", environment)
        
        if config_overrides:
            cloned._environment_configs[environment] = config_overrides
        
        # Apply environment config to all services
        for service in cloned._services:
            service.add_label("environment", environment)
            if hasattr(service, 'for_environment'):
                service = service.for_environment(environment)
        
        return cloned
    
    def set_resource_quotas(
        self,
        cpu_limit: Optional[str] = None,
        memory_limit: Optional[str] = None,
        storage_limit: Optional[str] = None,
        pod_limit: Optional[int] = None
    ) -> "AppGroup":
        """
        Set resource quotas for the entire group.
        
        Args:
            cpu_limit: Total CPU limit for the group
            memory_limit: Total memory limit for the group
            storage_limit: Total storage limit for the group
            pod_limit: Maximum number of pods
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._resource_quotas = {}
        
        if cpu_limit:
            self._resource_quotas["requests.cpu"] = cpu_limit
            self._resource_quotas["limits.cpu"] = cpu_limit
        
        if memory_limit:
            self._resource_quotas["requests.memory"] = memory_limit
            self._resource_quotas["limits.memory"] = memory_limit
        
        if storage_limit:
            self._resource_quotas["requests.storage"] = storage_limit
        
        if pod_limit:
            self._resource_quotas["count/pods"] = str(pod_limit)
        
        return self
    
    def configure_namespace(
        self,
        create_namespace: bool = True,
        namespace_labels: Optional[Dict[str, str]] = None,
        namespace_annotations: Optional[Dict[str, str]] = None
    ) -> "AppGroup":
        """
        Configure namespace settings for the group.
        
        Args:
            create_namespace: Whether to create a dedicated namespace
            namespace_labels: Labels for the namespace
            namespace_annotations: Annotations for the namespace
            
        Returns:
            AppGroup: Self for method chaining
        """
        self._namespace_config = {
            "create": create_namespace,
            "labels": namespace_labels or {},
            "annotations": namespace_annotations or {}
        }
        
        if create_namespace:
            # Set namespace for all services
            for service in self._services:
                service.set_namespace(self._name)
        
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for all services in the group.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resource dictionaries
        """
        resources = []
        
        # Generate namespace if configured
        if self._namespace_config and self._namespace_config.get("create"):
            namespace = self._generate_namespace()
            resources.append(namespace)
        
        # Generate resource quota if configured
        if self._resource_quotas:
            resource_quota = self._generate_resource_quota()
            resources.append(resource_quota)
        
        # Generate shared secrets
        for secret in self._shared_secrets:
            if hasattr(secret, 'generate_kubernetes_resources'):
                secret_resources = secret.generate_kubernetes_resources()
                for resource in secret_resources:
                    if self._namespace:
                        resource.setdefault("metadata", {})["namespace"] = self._namespace
                resources.extend(secret_resources)
        
        # Generate shared config maps
        for config_map in self._shared_configs:
            if hasattr(config_map, 'generate_kubernetes_resources'):
                config_resources = config_map.generate_kubernetes_resources()
                for resource in config_resources:
                    if self._namespace:
                        resource.setdefault("metadata", {})["namespace"] = self._namespace
                resources.extend(config_resources)
        
        # Apply dependencies to services
        self._apply_service_dependencies()
        
        # Generate resources for each service
        for service in self._services:
            if hasattr(service, 'generate_kubernetes_resources'):
                service_resources = service.generate_kubernetes_resources()
                for resource in service_resources:
                    if self._namespace:
                        resource.setdefault("metadata", {})["namespace"] = self._namespace
                resources.extend(service_resources)
        
        # Generate network policies
        for policy in self._network_policies:
            if hasattr(policy, 'generate_kubernetes_resources'):
                policy_resources = policy.generate_kubernetes_resources()
                for resource in policy_resources:
                    if self._namespace:
                        resource.setdefault("metadata", {})["namespace"] = self._namespace
                resources.extend(policy_resources)
        
        # Generate security policies
        for policy in self._security_policies:
            if hasattr(policy, 'generate_kubernetes_resources'):
                policy_resources = policy.generate_kubernetes_resources()
                for resource in policy_resources:
                    if self._namespace:
                        resource.setdefault("metadata", {})["namespace"] = self._namespace
                resources.extend(policy_resources)
        
        # Generate monitoring resources
        if self._monitoring_config:
            monitoring_resources = self._generate_monitoring_resources()
            resources.extend(monitoring_resources)
        
        return resources
    
    def _apply_service_dependencies(self) -> None:
        """Apply dependency configuration to services."""
        for service_name, deps in self._dependencies.items():
            service = self.get_service(service_name)
            if service and hasattr(service, 'depends_on'):
                service.depends_on(deps)
    
    def _generate_namespace(self) -> Dict[str, Any]:
        """Generate Kubernetes Namespace resource."""
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": self._name,
                "labels": {**self._labels, **self._namespace_config.get("labels", {})},
                "annotations": {**self._annotations, **self._namespace_config.get("annotations", {})}
            }
        }
        return namespace
    
    def _generate_resource_quota(self) -> Dict[str, Any]:
        """Generate Kubernetes ResourceQuota resource."""
        resource_quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {
                "name": f"{self._name}-quota",
                "namespace": self._namespace or self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "hard": self._resource_quotas
            }
        }
        return resource_quota
    
    def _generate_monitoring_resources(self) -> List[Dict[str, Any]]:
        """Generate monitoring resources for the group."""
        resources = []
        
        if not self._monitoring_config:
            return resources
        
        # Generate ServiceMonitor for Prometheus
        if self._monitoring_config.get("prometheus"):
            service_monitor = {
                "apiVersion": "monitoring.coreos.com/v1",
                "kind": "ServiceMonitor",
                "metadata": {
                    "name": f"{self._name}-monitoring",
                    "namespace": self._namespace or self._name,
                    "labels": self._labels
                },
                "spec": {
                    "selector": {
                        "matchLabels": {"app.kubernetes.io/part-of": self._name}
                    },
                    "endpoints": [{
                        "port": "metrics",
                        "path": "/metrics",
                        "interval": "30s"
                    }]
                }
            }
            resources.append(service_monitor)
        
        # Generate Grafana dashboard ConfigMap
        if self._monitoring_config.get("grafana"):
            dashboard_config = {
                "apiVersion": "v1",
                "kind": "ConfigMap",
                "metadata": {
                    "name": f"{self._name}-grafana-dashboard",
                    "namespace": self._namespace or self._name,
                    "labels": {**self._labels, "grafana_dashboard": "1"}
                },
                "data": {
                    "dashboard.json": self._generate_grafana_dashboard()
                }
            }
            resources.append(dashboard_config)
        
        return resources
    
    def _generate_grafana_dashboard(self) -> str:
        """Generate Grafana dashboard JSON."""
        # This would generate a complete Grafana dashboard
        # For brevity, returning a simple placeholder
        return '{"dashboard": {"title": "' + self._name + ' Monitoring"}}'
    
    def get_service_names(self) -> List[str]:
        """Get list of service names in the group."""
        return [service.name for service in self._services]
    
    def get_service_count(self) -> int:
        """Get the number of services in the group."""
        return len(self._services)
    
    def validate(self) -> List[str]:
        """
        Validate the application group configuration.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = super().validate()
        
        # Validate services
        if not self._services:
            errors.append("AppGroup must contain at least one service")
        
        # Validate service names are unique
        service_names = [s.name for s in self._services]
        if len(service_names) != len(set(service_names)):
            errors.append("Service names within AppGroup must be unique")
        
        # Validate dependencies
        for service_name, deps in self._dependencies.items():
            if service_name not in service_names:
                errors.append(f"Dependency reference to unknown service: {service_name}")
            
            for dep in deps:
                if dep not in service_names:
                    errors.append(f"Service {service_name} depends on unknown service: {dep}")
        
        # Validate each service
        for service in self._services:
            if hasattr(service, 'validate'):
                service_errors = service.validate()
                errors.extend([f"{service.name}: {error}" for error in service_errors])
        
        return errors 