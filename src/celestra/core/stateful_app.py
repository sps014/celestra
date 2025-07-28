"""
StatefulApp class for stateful applications in Celestraa DSL.

This module contains the StatefulApp class which represents stateful applications
that require persistent storage and stable network identities.
"""

from typing import Dict, List, Any, Optional, Union
from .base_builder import BaseBuilder


class StatefulApp(BaseBuilder):
    """
    Builder class for stateful applications.
    
    The StatefulApp class represents applications that are stateful and require
    persistent storage, stable network identities, and ordered deployment/scaling.
    
    Example:
        ```python
        database = (StatefulApp("database")
            .image("database-server:latest")
            .port(5432)
            .storage("20Gi")
            .replicas(3)
            .backup_schedule("0 2 * * *"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the StatefulApp builder.
        
        Args:
            name: Name of the stateful application
        """
        super().__init__(name)
        self._image: Optional[str] = None
        self._ports: List[Dict[str, Any]] = []
        self._environment: Dict[str, str] = {}
        self._resources: Dict[str, Any] = {}
        self._replicas: int = 1
        self._storage_size: Optional[str] = None
        self._storage_class: Optional[str] = None
        self._access_modes: List[str] = ["ReadWriteOnce"]
        self._mount_path: str = "/data"
        self._backup_schedule: Optional[str] = None
        self._backup_retention: int = 7
        self._cluster_mode: bool = False
        self._persistence: Dict[str, Any] = {}
        self._topics: List[str] = []  # For message queues
        self._retention_hours: Optional[int] = None
        self._companions: List[Any] = []
        self._secrets: List[Any] = []
        self._config_maps: List[Any] = []
        self._lifecycle: Optional[Any] = None
        self._health: Optional[Any] = None
        self._security_context: Optional[Dict[str, Any]] = None
        self._service_type: str = "ClusterIP"
        self._headless_service: bool = True
        self._update_strategy: str = "RollingUpdate"
        self._partition: Optional[int] = None
    
    def image(self, image: str) -> "StatefulApp":
        """
        Set the container image.
        
        Args:
            image: Container image name and tag
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._image = image
        return self
    
    def port(self, port: int, name: str = "app", protocol: str = "TCP") -> "StatefulApp":
        """
        Add a port to the application.
        
        Args:
            port: Port number
            name: Port name (default: "app")
            protocol: Port protocol (default: "TCP")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._ports.append({
            "containerPort": port,
            "name": name,
            "protocol": protocol
        })
        return self
    
    def add_port(self, port: int, name: str = "app", protocol: str = "TCP") -> "StatefulApp":
        """
        Add a port to the application (alias for port() method).
        
        Args:
            port: Port number
            name: Port name
            protocol: Port protocol (default: "TCP")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, protocol)
    
    def ports(self, ports: List[Dict[str, Any]]) -> "StatefulApp":
        """
        Set multiple ports for the application.
        
        Args:
            ports: List of port configurations with 'port', 'name', and optional 'protocol'
            
        Example:
            ```python
            stateful_app.ports([
                {"port": 5432, "name": "postgres"},
                {"port": 9187, "name": "metrics"},
                {"port": 8080, "name": "admin"}
            ])
            ```
            
        Returns:
            StatefulApp: Self for method chaining
        """
        for port_config in ports:
            self._ports.append({
                "containerPort": port_config.get("port"),
                "name": port_config.get("name", "app"),
                "protocol": port_config.get("protocol", "TCP")
            })
        return self
    
    def database_port(self, port: int, name: str = "database") -> "StatefulApp":
        """
        Add database port (convenience method).
        
        Args:
            port: Database port number
            name: Port name (default: "database")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def postgres_port(self, port: int = 5432, name: str = "postgres") -> "StatefulApp":
        """
        Add PostgreSQL port (convenience method).
        
        Args:
            port: PostgreSQL port number (default: 5432)
            name: Port name (default: "postgres")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def mysql_port(self, port: int = 3306, name: str = "mysql") -> "StatefulApp":
        """
        Add MySQL port (convenience method).
        
        Args:
            port: MySQL port number (default: 3306)
            name: Port name (default: "mysql")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def redis_port(self, port: int = 6379, name: str = "redis") -> "StatefulApp":
        """
        Add Redis port (convenience method).
        
        Args:
            port: Redis port number (default: 6379)
            name: Port name (default: "redis")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def mongodb_port(self, port: int = 27017, name: str = "mongodb") -> "StatefulApp":
        """
        Add MongoDB port (convenience method).
        
        Args:
            port: MongoDB port number (default: 27017)
            name: Port name (default: "mongodb")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def elasticsearch_port(self, port: int = 9200, name: str = "elasticsearch") -> "StatefulApp":
        """
        Add Elasticsearch port (convenience method).
        
        Args:
            port: Elasticsearch port number (default: 9200)
            name: Port name (default: "elasticsearch")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def kafka_port(self, port: int = 9092, name: str = "kafka") -> "StatefulApp":
        """
        Add Kafka port (convenience method).
        
        Args:
            port: Kafka port number (default: 9092)
            name: Port name (default: "kafka")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def metrics_port(self, port: int = 9090, name: str = "metrics") -> "StatefulApp":
        """
        Add metrics port (convenience method).
        
        Args:
            port: Metrics port number (default: 9090)
            name: Port name (default: "metrics")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def admin_port(self, port: int = 8080, name: str = "admin") -> "StatefulApp":
        """
        Add admin/management port (convenience method).
        
        Args:
            port: Admin port number (default: 8080)
            name: Port name (default: "admin")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def cluster_port(self, port: int, name: str = "cluster") -> "StatefulApp":
        """
        Add cluster communication port (convenience method).
        
        Args:
            port: Cluster port number
            name: Port name (default: "cluster")
            
        Returns:
            StatefulApp: Self for method chaining
        """
        return self.port(port, name, "TCP")
    
    def environment(self, env_vars: Dict[str, str]) -> "StatefulApp":
        """
        Set environment variables.
        
        Args:
            env_vars: Dictionary of environment variables
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._environment.update(env_vars)
        return self
    
    def env(self, key: str, value: str) -> "StatefulApp":
        """
        Add a single environment variable.
        
        Args:
            key: Environment variable name
            value: Environment variable value
            
        Returns:
            StatefulApp: Self for method chaining
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
    ) -> "StatefulApp":
        """
        Set resource requirements and limits.
        
        Args:
            cpu: CPU request (e.g., "500m")
            memory: Memory request (e.g., "512Mi")
            cpu_limit: CPU limit (e.g., "1000m")
            memory_limit: Memory limit (e.g., "1Gi")
            gpu: Number of GPUs required
            
        Returns:
            StatefulApp: Self for method chaining
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
    
    def replicas(self, count: int) -> "StatefulApp":
        """
        Set the number of replicas.
        
        Args:
            count: Number of replicas
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._replicas = count
        return self
    
    def storage(
        self, 
        size: str,
        storage_class: Optional[str] = None,
        access_modes: Optional[List[str]] = None,
        mount_path: str = "/data"
    ) -> "StatefulApp":
        """
        Configure persistent storage.
        
        Args:
            size: Storage size (e.g., "20Gi")
            storage_class: Storage class name
            access_modes: List of access modes
            mount_path: Mount path for the volume
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._storage_size = size
        self._storage_class = storage_class
        self._mount_path = mount_path
        
        if access_modes:
            self._access_modes = access_modes
        
        return self
    
    def backup_schedule(self, schedule: str, retention: int = 7) -> "StatefulApp":
        """
        Configure backup schedule.
        
        Args:
            schedule: Cron schedule for backups
            retention: Number of backups to retain
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._backup_schedule = schedule
        self._backup_retention = retention
        return self
    
    def cluster_mode(self, enabled: bool = True) -> "StatefulApp":
        """
        Enable cluster mode for the application.
        
        Args:
            enabled: Whether to enable cluster mode
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._cluster_mode = enabled
        return self
    
    def persistence(self, **config) -> "StatefulApp":
        """
        Configure persistence settings.
        
        Args:
            **config: Persistence configuration options
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._persistence.update(config)
        return self
    
    def topics(self, topic_list: List[str]) -> "StatefulApp":
        """
        Configure topics for message queue applications.
        
        Args:
            topic_list: List of topic names
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._topics = topic_list
        return self
    
    def retention_hours(self, hours: int) -> "StatefulApp":
        """
        Set data retention period in hours.
        
        Args:
            hours: Retention period in hours
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._retention_hours = hours
        return self
    
    def add_companion(self, companion: "Companion") -> "StatefulApp":
        """
        Add a companion container (sidecar or init container).
        
        Args:
            companion: Companion container configuration
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._companions.append(companion)
        return self
    
    def add_secret(self, secret: "Secret") -> "StatefulApp":
        """
        Add a secret to the application.
        
        Args:
            secret: Secret configuration
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._secrets.append(secret)
        return self
    
    def add_secrets(self, secrets: List["Secret"]) -> "StatefulApp":
        """
        Add multiple secrets to the application.
        
        Args:
            secrets: List of secret configurations
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._secrets.extend(secrets)
        return self
    
    def add_config(self, config_map: "ConfigMap") -> "StatefulApp":
        """
        Add a ConfigMap to the application.
        
        Args:
            config_map: ConfigMap configuration
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._config_maps.append(config_map)
        return self
    
    def add_configs(self, config_maps: List["ConfigMap"]) -> "StatefulApp":
        """
        Add multiple ConfigMaps to the application.
        
        Args:
            config_maps: List of ConfigMap configurations
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._config_maps.extend(config_maps)
        return self
    
    def lifecycle(self, lifecycle_config: "Lifecycle") -> "StatefulApp":
        """
        Set lifecycle configuration.
        
        Args:
            lifecycle_config: Lifecycle configuration
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._lifecycle = lifecycle_config
        return self
    
    def health(self, health_config: "Health") -> "StatefulApp":
        """
        Set health check configuration.
        
        Args:
            health_config: Health check configuration
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._health = health_config
        return self
    
    def security_context(self, context: Dict[str, Any]) -> "StatefulApp":
        """
        Set security context.
        
        Args:
            context: Security context configuration
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._security_context = context
        return self
    
    def service_type(self, service_type: str) -> "StatefulApp":
        """
        Set the service type.
        
        Args:
            service_type: Kubernetes service type (ClusterIP, LoadBalancer, etc.)
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._service_type = service_type
        return self
    
    def headless_service(self, enabled: bool = True) -> "StatefulApp":
        """
        Configure headless service.
        
        Args:
            enabled: Whether to create a headless service
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._headless_service = enabled
        return self
    
    def update_strategy(self, strategy: str, partition: Optional[int] = None) -> "StatefulApp":
        """
        Set update strategy.
        
        Args:
            strategy: Update strategy (RollingUpdate, OnDelete)
            partition: Partition for rolling updates
            
        Returns:
            StatefulApp: Self for method chaining
        """
        self._update_strategy = strategy
        self._partition = partition
        return self
    
    def for_environment(self, environment: str) -> "StatefulApp":
        """
        Create environment-specific configuration.
        
        Args:
            environment: Environment name (dev, staging, prod)
            
        Returns:
            StatefulApp: Cloned app with environment-specific config
        """
        cloned = self.clone()
        cloned.add_label("environment", environment)
        return cloned
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for the stateful application.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resource dictionaries
        """
        resources = []
        
        # Generate StatefulSet
        statefulset = self._generate_statefulset()
        resources.append(statefulset)
        
        # Generate Service
        service = self._generate_service()
        resources.append(service)
        
        # Generate backup CronJob if configured
        if self._backup_schedule:
            backup_job = self._generate_backup_cronjob()
            resources.append(backup_job)
        
        # Generate ConfigMaps
        for config_map in self._config_maps:
            if hasattr(config_map, 'generate_kubernetes_resources'):
                resources.extend(config_map.generate_kubernetes_resources())
        
        # Generate Secrets
        for secret in self._secrets:
            if hasattr(secret, 'generate_kubernetes_resources'):
                resources.extend(secret.generate_kubernetes_resources())
        
        return resources
    
    def _generate_statefulset(self) -> Dict[str, Any]:
        """Generate Kubernetes StatefulSet resource."""
        container = {
            "name": self._name,
            "image": self._image or "nginx:latest",
            "ports": self._ports if self._ports else [{"containerPort": 5432, "name": "app"}]
        }
        
        # Add environment variables
        if self._environment:
            container["env"] = [
                {"name": k, "value": v} for k, v in self._environment.items()
            ]
        
        # Add resources
        if self._resources:
            container["resources"] = self._resources
        
        # Add volume mounts
        volume_mounts = []
        if self._storage_size:
            volume_mounts.append({
                "name": "data",
                "mountPath": self._mount_path
            })
        
        # Add ConfigMap mounts
        for config_map in self._config_maps:
            if hasattr(config_map, 'mount_path') and config_map.mount_path:
                volume_mounts.append({
                    "name": f"{config_map.name}-volume",
                    "mountPath": config_map.mount_path,
                    "readOnly": True
                })
        
        # Add Secret mounts
        for secret in self._secrets:
            if hasattr(secret, 'mount_path') and secret.mount_path:
                volume_mounts.append({
                    "name": f"{secret.name}-volume",
                    "mountPath": secret.mount_path,
                    "readOnly": True
                })
        
        if volume_mounts:
            container["volumeMounts"] = volume_mounts
        
        # Add health checks
        if self._health:
            if hasattr(self._health, 'liveness_probe'):
                container["livenessProbe"] = self._health.liveness_probe
            if hasattr(self._health, 'readiness_probe'):
                container["readinessProbe"] = self._health.readiness_probe
            if hasattr(self._health, 'startup_probe'):
                container["startupProbe"] = self._health.startup_probe
        
        # Add lifecycle
        if self._lifecycle:
            if hasattr(self._lifecycle, 'to_dict'):
                container["lifecycle"] = self._lifecycle.to_dict()
        
        # Add security context
        if self._security_context:
            container["securityContext"] = self._security_context
        
        statefulset = {
            "apiVersion": "apps/v1",
            "kind": "StatefulSet",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "serviceName": self._name,
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
            statefulset["metadata"]["namespace"] = self._namespace
        
        # Add update strategy
        update_strategy = {"type": self._update_strategy}
        if self._update_strategy == "RollingUpdate" and self._partition is not None:
            update_strategy["rollingUpdate"] = {"partition": self._partition}
        statefulset["spec"]["updateStrategy"] = update_strategy
        
        # Add volume claim templates
        if self._storage_size:
            volume_claim_template = {
                "metadata": {
                    "name": "data"
                },
                "spec": {
                    "accessModes": self._access_modes,
                    "resources": {
                        "requests": {
                            "storage": self._storage_size
                        }
                    }
                }
            }
            
            if self._storage_class:
                volume_claim_template["spec"]["storageClassName"] = self._storage_class
            
            statefulset["spec"]["volumeClaimTemplates"] = [volume_claim_template]
        
        # Add volumes for ConfigMaps and Secrets
        volumes = []
        for config_map in self._config_maps:
            if hasattr(config_map, 'mount_path') and config_map.mount_path:
                volumes.append({
                    "name": f"{config_map.name}-volume",
                    "configMap": {
                        "name": config_map.name
                    }
                })
        
        for secret in self._secrets:
            if hasattr(secret, 'mount_path') and secret.mount_path:
                volumes.append({
                    "name": f"{secret.name}-volume",
                    "secret": {
                        "secretName": secret.name
                    }
                })
        
        if volumes:
            statefulset["spec"]["template"]["spec"]["volumes"] = volumes
        
        # Add init containers
        init_containers = [c for c in self._companions if hasattr(c, 'type') and c.type == 'init']
        if init_containers:
            statefulset["spec"]["template"]["spec"]["initContainers"] = [
                c.to_dict() for c in init_containers
            ]
        
        # Add sidecar containers
        sidecar_containers = [c for c in self._companions if hasattr(c, 'type') and c.type == 'sidecar']
        if sidecar_containers:
            statefulset["spec"]["template"]["spec"]["containers"].extend([
                c.to_dict() for c in sidecar_containers
            ])
        
        return statefulset
    
    def _generate_service(self) -> Dict[str, Any]:
        """Generate Kubernetes Service resource."""
        ports = []
        for port in self._ports:
            ports.append({
                "name": port["name"],
                "port": port["containerPort"],
                "targetPort": port["name"],
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
                "type": self._service_type
            }
        }
        
        if self._headless_service:
            service["spec"]["clusterIP"] = "None"
        
        if self._namespace:
            service["metadata"]["namespace"] = self._namespace
        
        return service
    
    def _generate_backup_cronjob(self) -> Dict[str, Any]:
        """Generate backup CronJob resource."""
        cronjob = {
            "apiVersion": "batch/v1",
            "kind": "CronJob",
            "metadata": {
                "name": f"{self._name}-backup",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "schedule": self._backup_schedule,
                "successfulJobsHistoryLimit": self._backup_retention,
                "failedJobsHistoryLimit": 3,
                "jobTemplate": {
                    "spec": {
                        "template": {
                            "spec": {
                                "containers": [{
                                    "name": "backup",
                                    "image": self._image or "backup-tools:latest",
                                    "command": [
                                        "sh", "-c",
                                        f"backup_tool --source {self._name} --dest /backup/backup-$(date +%Y%m%d).sql"
                                    ],
                                    "volumeMounts": [{
                                        "name": "backup-storage",
                                        "mountPath": "/backup"
                                    }]
                                }],
                                "volumes": [{
                                    "name": "backup-storage",
                                    "persistentVolumeClaim": {
                                        "claimName": f"{self._name}-backup"
                                    }
                                }],
                                "restartPolicy": "OnFailure"
                            }
                        }
                    }
                }
            }
        }
        
        if self._namespace:
            cronjob["metadata"]["namespace"] = self._namespace
        
        return cronjob 