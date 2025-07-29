# AppGroup Class

The `AppGroup` class manages multiple related services and provides cross-service configuration capabilities for complex applications.

## Overview

```python
from celestra import AppGroup, App, StatefulApp

# Basic usage
platform = AppGroup("ecommerce")
platform.add_services([
    StatefulApp("database").image("postgres:14"),
    App("api").image("api:latest"),
    App("web").image("web:latest")
])
```

## Functions

### Add Service
Add a single service to the group.

```python
# Add individual services
platform = AppGroup("myapp")
platform.add_service(App("api").image("api:latest"))
platform.add_service(StatefulApp("db").image("postgres:14"))
platform.add_service(App("web").image("web:latest"))
```

### Add Services
Add multiple services to the group at once.

```python
# Add multiple services
api = App("api").image("api:latest")
db = StatefulApp("db").image("postgres:14")
web = App("web").image("web:latest")

platform = AppGroup("myapp").add_services([api, db, web])
```

### Remove Service
Remove a service from the group by name.

```python
# Remove a service
platform = AppGroup("myapp")
platform.add_service(App("api").image("api:latest"))
platform.add_service(App("web").image("web:latest"))
platform.remove_service("api")  # Remove the API service
```

### Get Service
Get a service by name.

```python
# Get a specific service
platform = AppGroup("myapp")
platform.add_service(App("api").image("api:latest"))

api_service = platform.get_service("api")
if api_service:
    api_service.port(8080)
```

### Add Shared Secret
Add a secret that will be shared across all services in the group.

```python
# Add shared secret
shared_secret = Secret("shared-secret").add("api_key", "shared-key")
platform = AppGroup("myapp").add_shared_secret(shared_secret)

# All services in the group will have access to this secret
```

### Add Shared Config
Add a ConfigMap that will be shared across all services in the group.

```python
# Add shared configuration
shared_config = ConfigMap("shared-config").add("environment", "production")
platform = AppGroup("myapp").add_shared_config(shared_config)

# All services in the group will have access to this configuration
```

### Configure Networking
Configure networking policies for the group.

```python
# Basic internal communication
platform = AppGroup("myapp").configure_networking(allow_internal_communication=True)

# With external access restrictions
platform = AppGroup("myapp").configure_networking(
    allow_internal_communication=True,
    deny_external_access_except=["api", "web"]
)

# With service mesh
platform = AppGroup("myapp").configure_networking(
    service_mesh=True,
    mesh_config={"type": "istio", "version": "1.18"}
)
```

### Configure Monitoring
Configure monitoring for the group.

```python
# Basic monitoring
platform = AppGroup("myapp").configure_monitoring()

# Custom monitoring setup
platform = AppGroup("myapp").configure_monitoring(
    prometheus_enabled=True,
    grafana_enabled=True,
    jaeger_enabled=True,
    custom_metrics=["business_metrics", "user_activity"]
)
```

### Configure Security
Configure security policies for the group.

```python
# Basic security
platform = AppGroup("myapp").configure_security()

# Advanced security
platform = AppGroup("myapp").configure_security(
    rbac_enabled=True,
    pod_security_policy="restricted",
    network_policies=True,
    security_context={
        "runAsNonRoot": True,
        "runAsUser": 1000
    }
)
```

### Set Dependencies
Set service dependencies for deployment ordering.

```python
# Set multiple dependencies
dependencies = {
    "api": ["database"],
    "web": ["api"],
    "worker": ["database", "cache"]
}
platform = AppGroup("myapp").set_dependencies(dependencies)
```

### Add Dependency
Add a dependency for a specific service.

```python
# Single dependency
platform = AppGroup("myapp").add_dependency("api", "database")

# Multiple dependencies
platform = AppGroup("myapp").add_dependency("worker", ["database", "cache", "kafka"])
```

### For Environment
Create environment-specific configuration for the group.

```python
# Development environment
dev_platform = AppGroup("myapp").for_environment("development", {
    "replicas": 1,
    "resources": {"cpu": "100m", "memory": "256Mi"}
})

# Production environment
prod_platform = AppGroup("myapp").for_environment("production", {
    "replicas": 5,
    "resources": {"cpu": "500m", "memory": "1Gi"}
})
```

### Set Resource Quotas
Set resource quotas for the namespace.

```python
# Set resource quotas
platform = AppGroup("myapp").set_resource_quotas(
    cpu_limit="10",
    memory_limit="20Gi",
    storage_limit="100Gi",
    pod_limit=50
)
```

### Configure Namespace
Configure the namespace for the group.

```python
# Basic namespace
platform = AppGroup("myapp").configure_namespace()

# Custom namespace configuration
platform = AppGroup("myapp").configure_namespace(
    create_namespace=True,
    namespace_labels={
        "environment": "production",
        "team": "platform"
    },
    namespace_annotations={
        "description": "E-commerce platform"
    }
)
```

### Get Service Names
Get the names of all services in the group.

```python
platform = AppGroup("myapp")
platform.add_services([
    App("api").image("api:latest"),
    StatefulApp("db").image("postgres:14"),
    App("web").image("web:latest")
])

service_names = platform.get_service_names()
# Returns: ["api", "db", "web"]
```

### Get Service Count
Get the number of services in the group.

```python
platform = AppGroup("myapp")
platform.add_services([
    App("api").image("api:latest"),
    StatefulApp("db").image("postgres:14")
])

count = platform.get_service_count()  # Returns: 2
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete AppGroup Example - E-commerce Platform
"""

import os
from celestra import AppGroup, App, StatefulApp, Secret, ConfigMap, KubernetesOutput

def load_config(config_path: str) -> str:
    """Load configuration from external file."""
    with open(f"configs/{config_path}", "r") as f:
        return f.read()

def create_ecommerce_platform():
    """Create a complete e-commerce platform."""
    
    # Load external configurations
    nginx_config = load_config("application/nginx.conf")
    postgres_config = load_config("database/postgres.conf")
    
    # Create shared secrets
    shared_secret = (Secret("shared-secret")
        .add("jwt_secret", "jwt-signing-key")
        .add("stripe_key", "sk_live_...")
        .mount_as_env_vars(prefix="SHARED_"))
    
    # Create shared configurations
    shared_config = (ConfigMap("shared-config")
        .add("environment", "production")
        .add("log_level", "info")
        .add_json("features", {
            "new_ui": True,
            "beta_features": False
        }))
    
    # Create services
    database = (StatefulApp("postgres")
        .image("postgres:14")
        .port(5432)
        .storage("50Gi", "fast-ssd")
        .resources(cpu="2", memory="4Gi")
        .replicas(3)
        .add_secret(Secret("db-secret").add("password", "secure-password")))
    
    cache = (StatefulApp("redis")
        .image("redis:7-alpine")
        .port(6379)
        .storage("10Gi", "fast-ssd")
        .resources(cpu="1", memory="2Gi")
        .replicas(3))
    
    api = (App("api")
        .image("api:v2.1.0")
        .port(8080)
        .replicas(5)
        .resources(cpu="500m", memory="1Gi")
        .add_secret(Secret("api-secret").add("api_key", "api-key-123")))
    
    web = (App("web")
        .image("web:v2.1.0")
        .port(8080)
        .replicas(3)
        .resources(cpu="300m", memory="512Mi")
        .add_config(ConfigMap("nginx-config").add_data("nginx.conf", nginx_config)))
    
    worker = (App("worker")
        .image("worker:v2.1.0")
        .port(8080)
        .replicas(2)
        .resources(cpu="200m", memory="512Mi"))
    
    # Create the platform
    platform = (AppGroup("ecommerce")
        .add_services([database, cache, api, web, worker])
        .add_shared_secret(shared_secret)
        .add_shared_config(shared_config)
        .configure_networking(
            allow_internal_communication=True,
            deny_external_access_except=["api", "web"]
        )
        .configure_monitoring(
            prometheus_enabled=True,
            grafana_enabled=True,
            jaeger_enabled=True
        )
        .configure_security(
            rbac_enabled=True,
            pod_security_policy="restricted",
            network_policies=True
        )
        .set_dependencies({
            "api": ["postgres", "redis"],
            "web": ["api"],
            "worker": ["postgres", "redis"]
        })
        .set_resource_quotas(
            cpu_limit="20",
            memory_limit="40Gi",
            storage_limit="200Gi",
            pod_limit=100
        )
        .configure_namespace(
            create_namespace=True,
            namespace_labels={
                "environment": "production",
                "team": "ecommerce"
            }
        ))
    
    return platform

if __name__ == "__main__":
    platform = create_ecommerce_platform()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    resources = platform.generate_kubernetes_resources()
    
    # Write to files
    for i, resource in enumerate(resources):
        output.write_resource(resource, f"ecommerce-platform/resource-{i}.yaml")
    
    print("✅ E-commerce platform generated!")
    print("🚀 Deploy: kubectl apply -f ecommerce-platform/")
```

## Generated Kubernetes Resources

The AppGroup class generates the following Kubernetes resources:

- **Namespace** - Dedicated namespace for the group
- **ResourceQuota** - Resource limits for the namespace
- **Services** - All services in the group
- **Deployments/StatefulSets** - All workloads
- **ConfigMaps** - Shared and service-specific configurations
- **Secrets** - Shared and service-specific secrets
- **NetworkPolicies** - Network security policies
- **RBAC** - Role-based access control
- **Monitoring** - Prometheus, Grafana, Jaeger (if enabled)

## Usage Patterns

### Microservices Platform

```python
# Microservices platform
platform = AppGroup("microservices")
platform.add_services([
    StatefulApp("postgres").image("postgres:14").port(5432),
    StatefulApp("redis").image("redis:7").port(6379),
    App("user-service").image("user-service:latest").port(8080),
    App("order-service").image("order-service:latest").port(8080),
    App("payment-service").image("payment-service:latest").port(8080),
    App("notification-service").image("notification-service:latest").port(8080)
])
platform.configure_networking(allow_internal_communication=True)
```

### Data Processing Platform

```python
# Data processing platform
platform = AppGroup("data-platform")
platform.add_services([
    StatefulApp("kafka").image("confluentinc/cp-kafka:7.4.0").port(9092),
    StatefulApp("elasticsearch").image("elasticsearch:8.8.0").port(9200),
    App("data-ingestion").image("ingestion:latest").port(8080),
    App("data-processing").image("processing:latest").port(8080),
    App("data-visualization").image("visualization:latest").port(8080)
])
platform.configure_monitoring(prometheus_enabled=True, grafana_enabled=True)
```

### Development vs Production

```python
# Development environment
dev_platform = AppGroup("myapp-dev").for_environment("development", {
    "replicas": 1,
    "resources": {"cpu": "100m", "memory": "256Mi"}
})

# Production environment
prod_platform = AppGroup("myapp").for_environment("production", {
    "replicas": 5,
    "resources": {"cpu": "500m", "memory": "1Gi"}
})
```

## Best Practices

### 1. Use Shared Resources

```python
# ✅ Good: Use shared secrets and configs
platform = AppGroup("myapp")
platform.add_shared_secret(Secret("shared-secret").add("key", "value"))
platform.add_shared_config(ConfigMap("shared-config").add("env", "prod"))

# ❌ Bad: Duplicate secrets/configs for each service
```

### 2. Set Dependencies

```python
# ✅ Good: Set proper dependencies
platform = AppGroup("myapp").set_dependencies({
    "api": ["database"],
    "web": ["api"]
})

# ❌ Bad: No dependency management
```

### 3. Configure Security

```python
# ✅ Good: Enable security features
platform = AppGroup("myapp").configure_security(
    rbac_enabled=True,
    network_policies=True
)

# ❌ Bad: No security configuration
```

### 4. Set Resource Quotas

```python
# ✅ Good: Set resource quotas
platform = AppGroup("myapp").set_resource_quotas(
    cpu_limit="10",
    memory_limit="20Gi"
)

# ❌ Bad: No resource limits
```

### 5. Use Environment-Specific Configs

```python
# ✅ Good: Environment-specific configuration
dev_platform = AppGroup("myapp").for_environment("development")
prod_platform = AppGroup("myapp").for_environment("production")

# ❌ Bad: Same config for all environments
``` 