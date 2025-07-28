"""
ExternalServices class for cloud service integrations in Celestraa DSL.

This module provides integration with external cloud services like databases,
message queues, storage services, and other managed services.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class ExternalServices(BaseBuilder):
    """
    Builder class for external service integrations.
    
    Provides integration with cloud services, databases, message queues,
    and other external dependencies.
    
    Example:
        ```python
        ext = (ExternalServices("app-externals")
            .add_database("postgres", host="db.example.com", port=5432)
            .add_message_queue("redis", endpoint="redis.example.com:6379")
            .add_storage("s3", bucket="my-app-bucket")
            .add_secret_store("vault", endpoint="vault.example.com"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the ExternalServices builder.
        
        Args:
            name: Name of the external services configuration
        """
        super().__init__(name)
        self._databases: List[Dict[str, Any]] = []
        self._message_queues: List[Dict[str, Any]] = []
        self._storage_services: List[Dict[str, Any]] = []
        self._secret_stores: List[Dict[str, Any]] = []
        self._monitoring_services: List[Dict[str, Any]] = []
        self._api_services: List[Dict[str, Any]] = []
        self._service_mesh_config: Optional[Dict[str, Any]] = None
    
    def add_database(
        self,
        name: str,
        type: str = "postgres",
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        ssl_enabled: bool = True,
        connection_pool_size: int = 20
    ) -> "ExternalServices":
        """
        Add a database service.
        
        Args:
            name: Database service name
            type: Database type (postgres, mysql, mongodb, etc.)
            host: Database host
            port: Database port
            database: Database name
            ssl_enabled: Enable SSL connection
            connection_pool_size: Connection pool size
            
        Returns:
            ExternalServices: Self for method chaining
        """
        db_config = {
            "name": name,
            "type": type,
            "host": host,
            "port": port,
            "database": database,
            "ssl_enabled": ssl_enabled,
            "connection_pool_size": connection_pool_size
        }
        self._databases.append(db_config)
        return self
    
    def add_message_queue(
        self,
        name: str,
        type: str = "redis",
        endpoint: Optional[str] = None,
        queues: Optional[List[str]] = None,
        ssl_enabled: bool = True
    ) -> "ExternalServices":
        """
        Add a message queue service.
        
        Args:
            name: Message queue service name
            type: Queue type (redis, rabbitmq, kafka, sqs, etc.)
            endpoint: Queue endpoint
            queues: List of queue names
            ssl_enabled: Enable SSL connection
            
        Returns:
            ExternalServices: Self for method chaining
        """
        queue_config = {
            "name": name,
            "type": type,
            "endpoint": endpoint,
            "queues": queues or [],
            "ssl_enabled": ssl_enabled
        }
        self._message_queues.append(queue_config)
        return self
    
    def add_storage(
        self,
        name: str,
        type: str = "s3",
        bucket: Optional[str] = None,
        region: Optional[str] = None,
        endpoint: Optional[str] = None,
        access_key_secret: Optional[str] = None
    ) -> "ExternalServices":
        """
        Add a storage service.
        
        Args:
            name: Storage service name
            type: Storage type (s3, gcs, azure-blob, etc.)
            bucket: Bucket/container name
            region: Storage region
            endpoint: Custom endpoint (for S3-compatible services)
            access_key_secret: Secret containing access keys
            
        Returns:
            ExternalServices: Self for method chaining
        """
        storage_config = {
            "name": name,
            "type": type,
            "bucket": bucket,
            "region": region,
            "endpoint": endpoint,
            "access_key_secret": access_key_secret
        }
        self._storage_services.append(storage_config)
        return self
    
    def add_secret_store(
        self,
        name: str,
        type: str = "vault",
        endpoint: Optional[str] = None,
        auth_method: str = "kubernetes",
        mount_path: str = "secret"
    ) -> "ExternalServices":
        """
        Add a secret store service.
        
        Args:
            name: Secret store service name
            type: Secret store type (vault, aws-secrets-manager, etc.)
            endpoint: Secret store endpoint
            auth_method: Authentication method
            mount_path: Mount path for secrets
            
        Returns:
            ExternalServices: Self for method chaining
        """
        secret_store_config = {
            "name": name,
            "type": type,
            "endpoint": endpoint,
            "auth_method": auth_method,
            "mount_path": mount_path
        }
        self._secret_stores.append(secret_store_config)
        return self
    
    def add_monitoring_service(
        self,
        name: str,
        type: str = "datadog",
        api_key_secret: Optional[str] = None,
        endpoint: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None
    ) -> "ExternalServices":
        """
        Add a monitoring service.
        
        Args:
            name: Monitoring service name
            type: Monitoring type (datadog, newrelic, etc.)
            api_key_secret: Secret containing API key
            endpoint: Custom endpoint
            tags: Default tags
            
        Returns:
            ExternalServices: Self for method chaining
        """
        monitoring_config = {
            "name": name,
            "type": type,
            "api_key_secret": api_key_secret,
            "endpoint": endpoint,
            "tags": tags or {}
        }
        self._monitoring_services.append(monitoring_config)
        return self
    
    def add_api_service(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        retry_count: int = 3,
        auth_secret: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> "ExternalServices":
        """
        Add an external API service.
        
        Args:
            name: API service name
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            auth_secret: Secret containing authentication credentials
            headers: Default headers
            
        Returns:
            ExternalServices: Self for method chaining
        """
        api_config = {
            "name": name,
            "base_url": base_url,
            "timeout": timeout,
            "retry_count": retry_count,
            "auth_secret": auth_secret,
            "headers": headers or {}
        }
        self._api_services.append(api_config)
        return self
    
    def enable_service_mesh(
        self,
        type: str = "istio",
        mutual_tls: bool = True,
        circuit_breaker: bool = True,
        rate_limiting: bool = False
    ) -> "ExternalServices":
        """
        Enable service mesh for external services.
        
        Args:
            type: Service mesh type (istio, linkerd, consul-connect)
            mutual_tls: Enable mutual TLS
            circuit_breaker: Enable circuit breaker
            rate_limiting: Enable rate limiting
            
        Returns:
            ExternalServices: Self for method chaining
        """
        self._service_mesh_config = {
            "type": type,
            "mutual_tls": mutual_tls,
            "circuit_breaker": circuit_breaker,
            "rate_limiting": rate_limiting
        }
        return self
    
    # Preset configurations
    
    @classmethod
    def web_app_stack(cls, name: str = "web-app-externals") -> "ExternalServices":
        """
        Create typical web application external services.
        
        Args:
            name: Configuration name
            
        Returns:
            ExternalServices: Configured external services
        """
        return (cls(name)
            .add_database("postgres", type="postgres", port=5432)
            .add_message_queue("redis", type="redis")
            .add_storage("file-storage", type="s3")
            .add_secret_store("vault", type="vault"))
    
    @classmethod
    def microservices_stack(cls, name: str = "microservices-externals") -> "ExternalServices":
        """
        Create microservices external services stack.
        
        Args:
            name: Configuration name
            
        Returns:
            ExternalServices: Configured external services
        """
        return (cls(name)
            .add_database("postgres", type="postgres")
            .add_message_queue("kafka", type="kafka")
            .add_storage("object-storage", type="s3")
            .add_secret_store("vault", type="vault")
            .add_monitoring_service("datadog", type="datadog")
            .enable_service_mesh())
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for external services.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        # Generate ConfigMap for external services configuration
        config_data = {}
        
        # Database configurations
        for db in self._databases:
            prefix = f"DB_{db['name'].upper().replace('-', '_')}"
            if db.get("host"):
                config_data[f"{prefix}_HOST"] = db["host"]
            if db.get("port"):
                config_data[f"{prefix}_PORT"] = str(db["port"])
            if db.get("database"):
                config_data[f"{prefix}_NAME"] = db["database"]
            config_data[f"{prefix}_SSL_MODE"] = "require" if db.get("ssl_enabled", True) else "disable"
            config_data[f"{prefix}_POOL_SIZE"] = str(db.get("connection_pool_size", 20))
        
        # Message queue configurations
        for queue in self._message_queues:
            prefix = f"QUEUE_{queue['name'].upper().replace('-', '_')}"
            if queue.get("endpoint"):
                config_data[f"{prefix}_ENDPOINT"] = queue["endpoint"]
            config_data[f"{prefix}_TYPE"] = queue["type"]
            config_data[f"{prefix}_SSL_ENABLED"] = str(queue.get("ssl_enabled", True)).lower()
        
        # Storage configurations
        for storage in self._storage_services:
            prefix = f"STORAGE_{storage['name'].upper().replace('-', '_')}"
            if storage.get("bucket"):
                config_data[f"{prefix}_BUCKET"] = storage["bucket"]
            if storage.get("region"):
                config_data[f"{prefix}_REGION"] = storage["region"]
            if storage.get("endpoint"):
                config_data[f"{prefix}_ENDPOINT"] = storage["endpoint"]
            config_data[f"{prefix}_TYPE"] = storage["type"]
        
        # API service configurations
        for api in self._api_services:
            prefix = f"API_{api['name'].upper().replace('-', '_')}"
            config_data[f"{prefix}_BASE_URL"] = api["base_url"]
            config_data[f"{prefix}_TIMEOUT"] = str(api["timeout"])
            config_data[f"{prefix}_RETRY_COUNT"] = str(api["retry_count"])
        
        if config_data:
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
        
        # Generate ExternalSecrets for secret stores
        for secret_store in self._secret_stores:
            if secret_store["type"] == "vault":
                external_secret = {
                    "apiVersion": "external-secrets.io/v1beta1",
                    "kind": "ExternalSecret",
                    "metadata": {
                        "name": f"{self._name}-{secret_store['name']}-secrets",
                        "labels": self._labels,
                        "annotations": self._annotations
                    },
                    "spec": {
                        "secretStoreRef": {
                            "name": f"{secret_store['name']}-store",
                            "kind": "SecretStore"
                        },
                        "target": {
                            "name": f"{self._name}-{secret_store['name']}-secret",
                            "creationPolicy": "Owner"
                        },
                        "data": []
                    }
                }
                
                if self._namespace:
                    external_secret["metadata"]["namespace"] = self._namespace
                
                resources.append(external_secret)
                
                # Generate SecretStore
                secret_store_resource = {
                    "apiVersion": "external-secrets.io/v1beta1",
                    "kind": "SecretStore",
                    "metadata": {
                        "name": f"{secret_store['name']}-store",
                        "labels": self._labels,
                        "annotations": self._annotations
                    },
                    "spec": {
                        "provider": {
                            "vault": {
                                "server": secret_store.get("endpoint", ""),
                                "path": secret_store.get("mount_path", "secret"),
                                "version": "v2",
                                "auth": {
                                    "kubernetes": {
                                        "mountPath": "kubernetes",
                                        "role": f"{self._name}-vault-role"
                                    }
                                }
                            }
                        }
                    }
                }
                
                if self._namespace:
                    secret_store_resource["metadata"]["namespace"] = self._namespace
                
                resources.append(secret_store_resource)
        
        # Generate Service entries for service mesh
        if self._service_mesh_config and self._service_mesh_config.get("type") == "istio":
            # Generate ServiceEntry for databases
            for db in self._databases:
                if db.get("host"):
                    service_entry = {
                        "apiVersion": "networking.istio.io/v1beta1",
                        "kind": "ServiceEntry",
                        "metadata": {
                            "name": f"{self._name}-{db['name']}-service-entry",
                            "labels": self._labels,
                            "annotations": self._annotations
                        },
                        "spec": {
                            "hosts": [db["host"]],
                            "ports": [{
                                "number": db.get("port", 5432),
                                "name": db["type"],
                                "protocol": "TCP"
                            }],
                            "location": "MESH_EXTERNAL",
                            "resolution": "DNS"
                        }
                    }
                    
                    if self._namespace:
                        service_entry["metadata"]["namespace"] = self._namespace
                    
                    resources.append(service_entry)
        
        return resources 