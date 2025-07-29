# Companion Class

The `Companion` class manages companion services and sidecar containers in Kubernetes. It provides capabilities for sidecar patterns, init containers, ambassador patterns, and service mesh sidecars.

## Overview

```python
from celestra import Companion

# Basic sidecar container
companion = Companion("app-sidecar").image("sidecar:latest").port(8080)

# Production sidecar with multiple containers
companion = (Companion("production-sidecar")
    .sidecar_image("sidecar:1.0.0")
    .init_container("init-db", "init:latest")
    .ambassador_container("ambassador", "envoy:latest")
    .shared_volume("app-data"))
```

## Core API Functions

### Sidecar Configuration

#### Sidecar Image
Set the sidecar container image.

```python
# Basic sidecar
companion = Companion("app-sidecar").sidecar_image("sidecar:latest")

# Specific version
companion = Companion("app-sidecar").sidecar_image("sidecar:1.0.0")

# Custom registry
companion = Companion("app-sidecar").sidecar_image("registry.example.com/sidecar:latest")
```

#### Sidecar Port
Set the sidecar container port.

```python
# Sidecar port
companion = Companion("app-sidecar").sidecar_port(8080)

# Metrics port
companion = Companion("metrics-sidecar").sidecar_port(9090)
```

#### Sidecar Command
Set the sidecar container command.

```python
# Custom command
companion = Companion("app-sidecar").sidecar_command(["sidecar", "--config", "/config/sidecar.yaml"])

# Shell command
companion = Companion("app-sidecar").sidecar_command(["sh", "-c", "sidecar start"])
```

#### Sidecar Arguments
Set the sidecar container arguments.

```python
# Custom arguments
companion = Companion("app-sidecar").sidecar_args(["--port", "8080", "--host", "0.0.0.0"])

# Environment-specific arguments
companion = Companion("app-sidecar").sidecar_args(["--env", "production"])
```

### Init Container Configuration

#### Init Container
Add an init container.

```python
# Database init container
companion = Companion("app-sidecar").init_container("init-db", "postgres:13")

# Config init container
companion = Companion("app-sidecar").init_container("init-config", "config-init:latest")
```

#### Init Command
Set the init container command.

```python
# Database initialization
companion = Companion("app-sidecar").init_command(["sh", "-c", "pg_isready -h db"])

# Config initialization
companion = Companion("app-sidecar").init_command(["config-init", "--env", "production"])
```

#### Init Arguments
Set the init container arguments.

```python
# Init container arguments
companion = Companion("app-sidecar").init_args(["--timeout", "30", "--retries", "3"])
```

#### Init Timeout
Set init container timeout.

```python
# 60 second timeout
companion = Companion("app-sidecar").init_timeout(60)

# 300 second timeout for slow init
companion = Companion("app-sidecar").init_timeout(300)
```

### Ambassador Pattern

#### Ambassador Container
Add an ambassador container.

```python
# Envoy ambassador
companion = Companion("app-sidecar").ambassador_container("ambassador", "envoy:latest")

# Nginx ambassador
companion = Companion("app-sidecar").ambassador_container("ambassador", "nginx:alpine")
```

#### Ambassador Port
Set the ambassador container port.

```python
# Ambassador port
companion = Companion("app-sidecar").ambassador_port(8080)

# Admin port
companion = Companion("app-sidecar").ambassador_port(9901)
```

#### Ambassador Config
Set the ambassador configuration path.

```python
# Envoy config
companion = Companion("app-sidecar").ambassador_config("/etc/envoy/envoy.yaml")

# Nginx config
companion = Companion("app-sidecar").ambassador_config("/etc/nginx/nginx.conf")
```

### Adapter Pattern

#### Adapter Container
Add an adapter container.

```python
# Protocol adapter
companion = Companion("app-sidecar").adapter_container("adapter", "protocol-adapter:latest")

# Format adapter
companion = Companion("app-sidecar").adapter_container("adapter", "format-adapter:latest")
```

#### Adapter Protocol
Set the adapter protocol.

```python
# HTTP adapter
companion = Companion("app-sidecar").adapter_protocol("http")

# gRPC adapter
companion = Companion("app-sidecar").adapter_protocol("grpc")

# WebSocket adapter
companion = Companion("app-sidecar").adapter_protocol("websocket")
```

### Service Mesh Sidecar

#### Service Mesh Sidecar
Enable or disable service mesh sidecar.

```python
# Enable service mesh sidecar
companion = Companion("app-sidecar").service_mesh_sidecar(True)

# Disable service mesh sidecar
companion = Companion("app-sidecar").service_mesh_sidecar(False)
```

#### Service Mesh Type
Set the service mesh type.

```python
# Istio sidecar
companion = Companion("app-sidecar").service_mesh_type("istio")

# Linkerd sidecar
companion = Companion("app-sidecar").service_mesh_type("linkerd")

# Consul sidecar
companion = Companion("app-sidecar").service_mesh_type("consul")
```

#### Service Mesh Port
Set the service mesh sidecar port.

```python
# Istio proxy port
companion = Companion("app-sidecar").service_mesh_port(15001)

# Linkerd proxy port
companion = Companion("app-sidecar").service_mesh_port(4140)
```

### Volume Sharing

#### Shared Volume
Add a shared volume between containers.

```python
# Shared app data
companion = Companion("app-sidecar").shared_volume("app-data")

# Shared config
companion = Companion("app-sidecar").shared_volume("app-config")
```

#### Volume Mount Path
Set the volume mount path.

```python
# App data mount
companion = Companion("app-sidecar").volume_mount_path("/app/data")

# Config mount
companion = Companion("app-sidecar").volume_mount_path("/app/config")
```

#### Read Only Volume
Set volume as read-only.

```python
# Read-only volume
companion = Companion("app-sidecar").read_only_volume(True)

# Read-write volume
companion = Companion("app-sidecar").read_only_volume(False)
```

### Resource Configuration

#### Sidecar Resources
Set sidecar container resources.

```python
# Set CPU and memory
companion = Companion("app-sidecar").sidecar_resources(cpu="100m", memory="128Mi")

# Set only CPU
companion = Companion("app-sidecar").sidecar_resources(cpu="100m")

# Set only memory
companion = Companion("app-sidecar").sidecar_resources(memory="256Mi")
```

#### Init Resources
Set init container resources.

```python
# Set CPU and memory
companion = Companion("app-sidecar").init_resources(cpu="50m", memory="64Mi")
```

#### Ambassador Resources
Set ambassador container resources.

```python
# Set CPU and memory
companion = Companion("app-sidecar").ambassador_resources(cpu="200m", memory="256Mi")
```

### Health Checks

#### Sidecar Health Check
Add health check for sidecar.

```python
# Sidecar health check
companion = Companion("app-sidecar").sidecar_health_check("/health")

# Sidecar health check with port
companion = Companion("app-sidecar").sidecar_health_check("/health", 8080)
```

#### Init Health Check
Add health check for init container.

```python
# Init container health check
companion = Companion("app-sidecar").init_health_check(["pg_isready", "-h", "db"])
```

#### Ambassador Health Check
Add health check for ambassador.

```python
# Ambassador health check
companion = Companion("app-sidecar").ambassador_health_check("/health")

# Ambassador admin health check
companion = Companion("app-sidecar").ambassador_health_check("/stats", 9901)
```

### Environment Configuration

#### Sidecar Environment
Set environment variables for sidecar.

```python
# Set environment variables
env = {
    "SIDECAR_PORT": "8080",
    "SIDECAR_HOST": "0.0.0.0",
    "LOG_LEVEL": "info"
}
companion = Companion("app-sidecar").sidecar_environment(env)
```

#### Init Environment
Set environment variables for init container.

```python
# Set init environment variables
env = {
    "DB_HOST": "db",
    "DB_PORT": "5432",
    "TIMEOUT": "30"
}
companion = Companion("app-sidecar").init_environment(env)
```

#### Ambassador Environment
Set environment variables for ambassador.

```python
# Set ambassador environment variables
env = {
    "ENVOY_PORT": "8080",
    "ENVOY_ADMIN_PORT": "9901",
    "LOG_LEVEL": "info"
}
companion = Companion("app-sidecar").ambassador_environment(env)
```

### Security Configuration

#### Sidecar Security Context
Set security context for sidecar.

```python
# Set security context
security_context = {
    "runAsNonRoot": True,
    "runAsUser": 1000,
    "fsGroup": 2000
}
companion = Companion("app-sidecar").sidecar_security_context(security_context)
```

#### Init Security Context
Set security context for init container.

```python
# Set init security context
security_context = {
    "runAsNonRoot": True,
    "runAsUser": 1000
}
companion = Companion("app-sidecar").init_security_context(security_context)
```

#### Ambassador Security Context
Set security context for ambassador.

```python
# Set ambassador security context
security_context = {
    "runAsNonRoot": True,
    "runAsUser": 1000
}
companion = Companion("app-sidecar").ambassador_security_context(security_context)
```

### Advanced Configuration

#### Namespace
Set the namespace for the companion configuration.

```python
companion = Companion("app-sidecar").namespace("production")
```

#### Add Label
Add a label to the companion configuration.

```python
companion = Companion("app-sidecar").add_label("environment", "production")
```

#### Add Labels
Add multiple labels to the companion configuration.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "sidecar"
}
companion = Companion("app-sidecar").add_labels(labels)
```

#### Add Annotation
Add an annotation to the companion configuration.

```python
companion = Companion("app-sidecar").add_annotation("description", "Application sidecar")
```

#### Add Annotations
Add multiple annotations to the companion configuration.

```python
annotations = {
    "description": "Application sidecar for production",
    "owner": "platform-team",
    "sidecar-type": "service-mesh"
}
companion = Companion("app-sidecar").add_annotations(annotations)
```

#### Lifecycle Hooks
Enable or disable lifecycle hooks.

```python
# Enable lifecycle hooks
companion = Companion("app-sidecar").lifecycle_hooks(True)

# Disable lifecycle hooks
companion = Companion("app-sidecar").lifecycle_hooks(False)
```

#### Termination Grace Period
Set termination grace period.

```python
# 30 second grace period
companion = Companion("app-sidecar").termination_grace_period(30)

# 60 second grace period
companion = Companion("app-sidecar").termination_grace_period(60)
```

### Output Generation

#### Generate Configuration
Generate the companion configuration.

```python
# Generate Kubernetes YAML
companion.generate().to_yaml("./k8s/")

# Generate Helm values
companion.generate().to_helm_values("./helm/")

# Generate Terraform
companion.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready companion configuration:

```python
from celestra import Companion

# Create comprehensive companion configuration
production_companion = (Companion("production-sidecar")
    .sidecar_image("sidecar:1.0.0")
    .sidecar_port(8080)
    .sidecar_command(["sidecar", "--config", "/config/sidecar.yaml"])
    .sidecar_args(["--port", "8080", "--host", "0.0.0.0"])
    .sidecar_resources(cpu="100m", memory="128Mi")
    .sidecar_health_check("/health", 8080)
    .sidecar_environment({
        "SIDECAR_PORT": "8080",
        "SIDECAR_HOST": "0.0.0.0",
        "LOG_LEVEL": "info"
    })
    .sidecar_security_context({
        "runAsNonRoot": True,
        "runAsUser": 1000,
        "fsGroup": 2000
    })
    .init_container("init-db", "postgres:13")
    .init_command(["sh", "-c", "pg_isready -h db"])
    .init_args(["--timeout", "30", "--retries", "3"])
    .init_timeout(60)
    .init_resources(cpu="50m", memory="64Mi")
    .init_environment({
        "DB_HOST": "db",
        "DB_PORT": "5432",
        "TIMEOUT": "30"
    })
    .init_security_context({
        "runAsNonRoot": True,
        "runAsUser": 1000
    })
    .init_health_check(["pg_isready", "-h", "db"])
    .ambassador_container("ambassador", "envoy:latest")
    .ambassador_port(8080)
    .ambassador_config("/etc/envoy/envoy.yaml")
    .ambassador_resources(cpu="200m", memory="256Mi")
    .ambassador_health_check("/health", 8080)
    .ambassador_environment({
        "ENVOY_PORT": "8080",
        "ENVOY_ADMIN_PORT": "9901",
        "LOG_LEVEL": "info"
    })
    .ambassador_security_context({
        "runAsNonRoot": True,
        "runAsUser": 1000
    })
    .service_mesh_sidecar(True)
    .service_mesh_type("istio")
    .service_mesh_port(15001)
    .shared_volume("app-data")
    .volume_mount_path("/app/data")
    .read_only_volume(False)
    .lifecycle_hooks(True)
    .termination_grace_period(30)
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "sidecar"
    })
    .add_annotations({
        "description": "Production sidecar configuration",
        "owner": "platform-team@company.com",
        "sidecar-type": "service-mesh"
    }))

# Generate manifests
production_companion.generate().to_yaml("./k8s/")
```

## Companion Patterns

### Sidecar Pattern
```python
# Sidecar pattern for logging
logging_sidecar = (Companion("logging-sidecar")
    .sidecar_image("fluentd:latest")
    .sidecar_port(24224)
    .sidecar_command(["fluentd", "-c", "/fluentd/etc/fluent.conf"])
    .shared_volume("app-logs")
    .volume_mount_path("/var/log/app"))
```

### Ambassador Pattern
```python
# Ambassador pattern for API gateway
api_ambassador = (Companion("api-ambassador")
    .ambassador_container("ambassador", "envoy:latest")
    .ambassador_port(8080)
    .ambassador_config("/etc/envoy/envoy.yaml")
    .ambassador_resources(cpu="200m", memory="256Mi")
    .ambassador_health_check("/health", 8080))
```

### Adapter Pattern
```python
# Adapter pattern for protocol conversion
protocol_adapter = (Companion("protocol-adapter")
    .adapter_container("adapter", "protocol-adapter:latest")
    .adapter_protocol("http")
    .adapter_port(8080)
    .adapter_resources(cpu="100m", memory="128Mi"))
```

### Init Container Pattern
```python
# Init container pattern for database setup
db_init = (Companion("db-init")
    .init_container("init-db", "postgres:13")
    .init_command(["sh", "-c", "pg_isready -h db"])
    .init_timeout(60)
    .init_resources(cpu="50m", memory="64Mi")
    .init_environment({
        "DB_HOST": "db",
        "DB_PORT": "5432"
    }))
```

### Service Mesh Sidecar Pattern
```python
# Service mesh sidecar pattern
service_mesh_sidecar = (Companion("service-mesh-sidecar")
    .service_mesh_sidecar(True)
    .service_mesh_type("istio")
    .service_mesh_port(15001)
    .sidecar_resources(cpu="100m", memory="128Mi")
    .sidecar_health_check("/health", 15001))
```

## Best Practices

### 1. **Use Appropriate Resource Limits**
```python
# ✅ Good: Set appropriate resource limits
companion = Companion("app-sidecar").sidecar_resources(cpu="100m", memory="128Mi")

# ❌ Bad: No resource limits
companion = Companion("app-sidecar")  # No resource limits
```

### 2. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
companion = Companion("app-sidecar").sidecar_health_check("/health", 8080)

# ❌ Bad: No health checks
companion = Companion("app-sidecar")  # No health checks
```

### 3. **Use Security Contexts**
```python
# ✅ Good: Use security contexts
companion = Companion("app-sidecar").sidecar_security_context({
    "runAsNonRoot": True,
    "runAsUser": 1000
})

# ❌ Bad: No security context
companion = Companion("app-sidecar")  # Default security context
```

### 4. **Set Appropriate Timeouts**
```python
# ✅ Good: Set appropriate timeouts
companion = Companion("app-sidecar").init_timeout(60)

# ❌ Bad: No timeout
companion = Companion("app-sidecar")  # No timeout
```

### 5. **Use Shared Volumes Appropriately**
```python
# ✅ Good: Use shared volumes appropriately
companion = Companion("app-sidecar").shared_volume("app-data").volume_mount_path("/app/data")

# ❌ Bad: No volume sharing
companion = Companion("app-sidecar")  # No volume sharing
```

### 6. **Enable Lifecycle Hooks**
```python
# ✅ Good: Enable lifecycle hooks
companion = Companion("app-sidecar").lifecycle_hooks(True)

# ❌ Bad: No lifecycle hooks
companion = Companion("app-sidecar")  # No lifecycle hooks
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Service](service.md)** - For service discovery
- **[NetworkPolicy](network-policy.md)** - For network security
- **[Health](health.md)** - For health checks

## Next Steps

- **[SecurityPolicy](../security/security-policy.md)** - Learn about security policies
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 