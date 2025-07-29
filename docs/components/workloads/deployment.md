# Deployment Class

The `Deployment` class manages stateless application deployments in Kubernetes. It provides deployment strategies, rolling updates, rollback capabilities, and lifecycle management for applications.

## Overview

```python
from celestra import Deployment

# Basic deployment
deployment = Deployment("web-app").image("nginx:latest").replicas(3)

# Production deployment with strategy
deployment = (Deployment("api-app")
    .image("api:1.0.0")
    .replicas(5)
    .strategy("RollingUpdate")
    .max_surge(1)
    .max_unavailable(0))
```

## Core API Functions

### Container Configuration

#### Image Configuration
Set the container image.

```python
# Basic image
deployment = Deployment("web-app").image("nginx:latest")

# Specific version
deployment = Deployment("api-app").image("api:1.0.0")

# Private registry
deployment = Deployment("app").image("registry.example.com/app:latest")
```

#### Build Configuration
Build image from Dockerfile.

```python
# Build from local context
deployment = Deployment("app").build("./app")

# Build with custom Dockerfile
deployment = Deployment("app").build("./app", "Dockerfile.prod")
```

#### Dockerfile Configuration
Set Dockerfile path for building.

```python
deployment = Deployment("app").from_dockerfile("./Dockerfile")
```

#### Command Configuration
Set the container command.

```python
# Custom command
deployment = Deployment("app").command(["python", "app.py"])

# Shell command
deployment = Deployment("app").command(["sh", "-c", "echo 'Hello World'"])
```

#### Arguments Configuration
Set the container arguments.

```python
# Custom arguments
deployment = Deployment("app").args(["--port", "8080", "--host", "0.0.0.0"])

# Environment-specific arguments
deployment = Deployment("app").args(["--env", "production"])
```

### Scaling Configuration

#### Replicas Configuration
Set the number of replicas.

```python
# Single replica
deployment = Deployment("app").replicas(1)

# Multiple replicas
deployment = Deployment("app").replicas(5)

# High availability
deployment = Deployment("app").replicas(10)
```

#### Minimum Replicas
Set minimum number of replicas.

```python
deployment = Deployment("app").min_replicas(2)
```

#### Maximum Replicas
Set maximum number of replicas.

```python
deployment = Deployment("app").max_replicas(10)
```

#### Scale Configuration
Scale the deployment (alias for replicas).

```python
deployment = Deployment("app").scale(3)
```

### Deployment Strategy

#### Strategy Configuration
Set the deployment strategy.

```python
# Rolling update (default)
deployment = Deployment("app").strategy("RollingUpdate")

# Recreate strategy
deployment = Deployment("app").strategy("Recreate")

# Blue-green strategy
deployment = Deployment("app").strategy("BlueGreen")
```

#### Rolling Update Strategy
Configure rolling update strategy.

```python
deployment = Deployment("app").rolling_update()
```

#### Recreate Strategy
Configure recreate strategy.

```python
deployment = Deployment("app").recreate_strategy()
```

#### Blue-Green Strategy
Configure blue-green strategy.

```python
deployment = Deployment("app").blue_green_strategy()
```

#### Canary Strategy
Configure canary strategy.

```python
deployment = Deployment("app").canary_strategy()
```

### Update Configuration

#### Maximum Surge
Set maximum surge during updates.

```python
# Allow 1 extra pod during update
deployment = Deployment("app").max_surge(1)

# Allow 25% extra pods
deployment = Deployment("app").max_surge("25%")

# No surge
deployment = Deployment("app").max_surge(0)
```

#### Maximum Unavailable
Set maximum unavailable pods during updates.

```python
# Allow 0 unavailable pods
deployment = Deployment("app").max_unavailable(0)

# Allow 25% unavailable pods
deployment = Deployment("app").max_unavailable("25%")

# Allow 1 unavailable pod
deployment = Deployment("app").max_unavailable(1)
```

#### Update Period
Set update period in seconds.

```python
deployment = Deployment("app").update_period_seconds(30)
```

#### Progress Deadline
Set progress deadline in seconds.

```python
deployment = Deployment("app").progress_deadline_seconds(600)
```

### Port Configuration

#### Single Port
Set the container port.

```python
deployment = Deployment("app").port(8080)
```

#### Multiple Ports
Set multiple container ports.

```python
deployment = Deployment("app").ports([80, 443, 8080])
```

#### Add Port
Add a port to the container.

```python
deployment = Deployment("app").add_port(8080)
```

#### HTTP Port
Set HTTP port.

```python
deployment = Deployment("app").http_port(80)
```

#### HTTPS Port
Set HTTPS port.

```python
deployment = Deployment("app").https_port(443)
```

#### Metrics Port
Set metrics port.

```python
deployment = Deployment("app").metrics_port(9090)
```

### Environment Configuration

#### Environment Variables
Set environment variables.

```python
# Set environment variables
env = {
    "NODE_ENV": "production",
    "PORT": "8080",
    "DATABASE_URL": "postgresql://user:pass@db:5432/app"
}
deployment = Deployment("app").environment(env)
```

#### Single Environment Variable
Add a single environment variable.

```python
deployment = Deployment("app").env("NODE_ENV", "production")
```

#### Environment from Secret
Add environment variables from secret.

```python
deployment = Deployment("app").env_from_secret("app-secret")
```

#### Environment from ConfigMap
Add environment variables from ConfigMap.

```python
deployment = Deployment("app").env_from_config_map("app-config")
```

### Resource Configuration

#### Resource Limits
Set resource limits and requests.

```python
# Set CPU and memory
deployment = Deployment("app").resources(cpu="500m", memory="512Mi")

# Set only CPU
deployment = Deployment("app").resources(cpu="500m")

# Set only memory
deployment = Deployment("app").resources(memory="1Gi")
```

#### CPU Request
Set CPU request.

```python
deployment = Deployment("app").cpu_request("250m")
```

#### CPU Limit
Set CPU limit.

```python
deployment = Deployment("app").cpu_limit("500m")
```

#### Memory Request
Set memory request.

```python
deployment = Deployment("app").memory_request("256Mi")
```

#### Memory Limit
Set memory limit.

```python
deployment = Deployment("app").memory_limit("512Mi")
```

### Health Checks

#### Health Check Endpoint
Add health check endpoint.

```python
deployment = Deployment("app").health_check("/health")
```

#### Liveness Probe
Configure liveness probe.

```python
deployment = Deployment("app").liveness_probe("/health", 8080, 30, 10)
```

#### Readiness Probe
Configure readiness probe.

```python
deployment = Deployment("app").readiness_probe("/ready", 8080, 5, 5)
```

#### Startup Probe
Configure startup probe.

```python
deployment = Deployment("app").startup_probe("/startup", 8080, 30, 10)
```

### Volume Mounts

#### Add Volume
Add a volume to the deployment.

```python
from celestra import Volume

volume = Volume("app-data").size("10Gi")
deployment = Deployment("app").add_volume(volume)
```

#### Add Multiple Volumes
Add multiple volumes to the deployment.

```python
from celestra import Volume

volumes = [
    Volume("app-data").size("10Gi"),
    Volume("config-data").size("1Gi")
]
deployment = Deployment("app").add_volumes(volumes)
```

#### Mount Path
Set the mount path for volumes.

```python
deployment = Deployment("app").mount_path("/app/data")
```

### Security Configuration

#### Service Account
Set the service account.

```python
deployment = Deployment("app").service_account("app-sa")
```

#### Security Context
Set security context.

```python
security_context = {
    "runAsNonRoot": True,
    "runAsUser": 1000,
    "fsGroup": 2000
}
deployment = Deployment("app").security_context(security_context)
```

#### Run as User
Set the user ID to run as.

```python
deployment = Deployment("app").run_as_user(1000)
```

#### Run as Group
Set the group ID to run as.

```python
deployment = Deployment("app").run_as_group(2000)
```

#### Read-Only Root Filesystem
Set read-only root filesystem.

```python
deployment = Deployment("app").read_only_root_filesystem(True)
```

### Advanced Configuration

#### Namespace
Set the namespace for the deployment.

```python
deployment = Deployment("app").namespace("production")
```

#### Add Label
Add a label to the deployment.

```python
deployment = Deployment("app").add_label("environment", "production")
```

#### Add Multiple Labels
Add multiple labels to the deployment.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "frontend"
}
deployment = Deployment("app").add_labels(labels)
```

#### Add Annotation
Add an annotation to the deployment.

```python
deployment = Deployment("app").add_annotation("description", "Web application")
```

#### Add Multiple Annotations
Add multiple annotations to the deployment.

```python
annotations = {
    "description": "Web application for production",
    "owner": "platform-team",
    "version": "1.0.0"
}
deployment = Deployment("app").add_annotations(annotations)
```

#### Node Selector
Set node selector.

```python
deployment = Deployment("app").node_selector({"node-type": "app"})
```

#### Tolerations
Set tolerations.

```python
tolerations = [{
    "key": "dedicated",
    "operator": "Equal",
    "value": "app",
    "effect": "NoSchedule"
}]
deployment = Deployment("app").tolerations(tolerations)
```

#### Pod Affinity
Set pod affinity.

```python
affinity = {
    "podAntiAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [{
            "weight": 100,
            "podAffinityTerm": {
                "labelSelector": {
                    "matchExpressions": [{
                        "key": "app",
                        "operator": "In",
                        "values": ["web"]
                    }]
                },
                "topologyKey": "kubernetes.io/hostname"
            }
        }]
    }
```

### Lifecycle Management

#### Pre-Stop Command
Set pre-stop command.

```python
deployment = Deployment("app").pre_stop_command(["sh", "-c", "sleep 10"])
```

#### Post-Start Command
Set post-start command.

```python
deployment = Deployment("app").post_start_command(["sh", "-c", "echo 'Started'"])
```

#### Termination Grace Period
Set termination grace period.

```python
deployment = Deployment("app").termination_grace_period(30)
```

### Rollback Configuration

#### Revision History Limit
Set revision history limit.

```python
deployment = Deployment("app").revision_history_limit(10)
```

#### Rollback to Revision
Rollback to specific revision.

```python
deployment = Deployment("app").rollback_to_revision(5)
```

#### Pause Deployment
Pause the deployment.

```python
deployment = Deployment("app").pause_deployment(True)
```

#### Resume Deployment
Resume the deployment.

```python
deployment = Deployment("app").resume_deployment()
```

### Output Generation

#### Generate Configuration
Generate the deployment configuration.

```python
# Generate Kubernetes YAML
deployment.generate().to_yaml("./k8s/")

# Generate Helm values
deployment.generate().to_helm_values("./helm/")

# Generate Terraform
deployment.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready deployment:

```python
from celestra import Deployment, Volume

# Create comprehensive deployment
production_deployment = (Deployment("api-app")
    .image("api:1.0.0")
    .replicas(5)
    .strategy("RollingUpdate")
    .max_surge(1)
    .max_unavailable(0)
    .port(8080)
    .ports([80, 443, 8080, 9090])
    .environment({
        "NODE_ENV": "production",
        "PORT": "8080",
        "DATABASE_URL": "postgresql://user:pass@db:5432/app"
    })
    .env_from_secret("api-secret")
    .env_from_config_map("api-config")
    .resources(cpu="500m", memory="512Mi")
    .liveness_probe("/health", 8080, 30, 10)
    .readiness_probe("/ready", 8080, 5, 5)
    .startup_probe("/startup", 8080, 30, 10)
    .add_volume(Volume("app-data").size("10Gi").mount_path("/app/data"))
    .service_account("api-sa")
    .security_context({
        "runAsNonRoot": True,
        "runAsUser": 1000,
        "fsGroup": 2000
    })
    .read_only_root_filesystem(True)
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "backend"
    })
    .add_annotations({
        "description": "API application for production",
        "owner": "platform-team@company.com",
        "version": "1.0.0"
    })
    .node_selector({"node-type": "app"})
    .tolerations([{
        "key": "dedicated",
        "operator": "Equal",
        "value": "app",
        "effect": "NoSchedule"
    }])
    .affinity({
        "podAntiAffinity": {
            "preferredDuringSchedulingIgnoredDuringExecution": [{
                "weight": 100,
                "podAffinityTerm": {
                    "labelSelector": {
                        "matchExpressions": [{
                            "key": "app",
                            "operator": "In",
                            "values": ["api"]
                        }]
                    },
                    "topologyKey": "kubernetes.io/hostname"
                }
            }]
        }
    })
    .pre_stop_command(["sh", "-c", "sleep 10"])
    .post_start_command(["sh", "-c", "echo 'Started'"])
    .termination_grace_period(30)
    .revision_history_limit(10))

# Generate manifests
production_deployment.generate().to_yaml("./k8s/")
```

## Deployment Patterns

### Rolling Update Pattern
```python
# Rolling update with zero downtime
rolling_update = (Deployment("app")
    .image("app:1.0.0")
    .replicas(5)
    .strategy("RollingUpdate")
    .max_surge(1)
    .max_unavailable(0)
    .liveness_probe("/health")
    .readiness_probe("/ready"))
```

### Blue-Green Pattern
```python
# Blue-green deployment
blue_green = (Deployment("app")
    .image("app:1.0.0")
    .replicas(5)
    .strategy("BlueGreen")
    .liveness_probe("/health")
    .readiness_probe("/ready"))
```

### Canary Pattern
```python
# Canary deployment
canary = (Deployment("app")
    .image("app:1.0.0")
    .replicas(1)
    .strategy("Canary")
    .liveness_probe("/health")
    .readiness_probe("/ready"))
```

### High Availability Pattern
```python
# High availability deployment
ha_deployment = (Deployment("app")
    .image("app:1.0.0")
    .replicas(10)
    .strategy("RollingUpdate")
    .max_surge(2)
    .max_unavailable(1)
    .affinity({
        "podAntiAffinity": {
            "requiredDuringSchedulingIgnoredDuringExecution": [{
                "labelSelector": {
                    "matchExpressions": [{
                        "key": "app",
                        "operator": "In",
                        "values": ["app"]
                    }]
                },
                "topologyKey": "kubernetes.io/hostname"
            }]
        }
    }))
```

## Best Practices

### 1. **Use Rolling Updates for Zero Downtime**
```python
# ✅ Good: Use rolling update for zero downtime
deployment = Deployment("app").strategy("RollingUpdate").max_surge(1).max_unavailable(0)

# ❌ Bad: Use recreate strategy
deployment = Deployment("app").strategy("Recreate")
```

### 2. **Set Resource Limits**
```python
# ✅ Good: Set resource limits
deployment = Deployment("app").resources(cpu="500m", memory="512Mi")

# ❌ Bad: No resource limits
deployment = Deployment("app")  # No resource limits
```

### 3. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
deployment = Deployment("app").liveness_probe("/health").readiness_probe("/ready")

# ❌ Bad: No health checks
deployment = Deployment("app")  # No health checks
```

### 4. **Use Multiple Replicas**
```python
# ✅ Good: Use multiple replicas for high availability
deployment = Deployment("app").replicas(3)

# ❌ Bad: Single replica
deployment = Deployment("app").replicas(1)  # Single point of failure
```

### 5. **Set Security Context**
```python
# ✅ Good: Set security context
deployment = Deployment("app").security_context({
    "runAsNonRoot": True,
    "runAsUser": 1000
})

# ❌ Bad: Run as root
deployment = Deployment("app")  # Default security context
```

### 6. **Use Pod Anti-Affinity**
```python
# ✅ Good: Use pod anti-affinity for high availability
deployment = Deployment("app").affinity({
    "podAntiAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [{
            "weight": 100,
            "podAffinityTerm": {
                "labelSelector": {"matchExpressions": [{"key": "app", "operator": "In", "values": ["app"]}]},
                "topologyKey": "kubernetes.io/hostname"
            }
        }]
    }
})

# ❌ Bad: No anti-affinity
deployment = Deployment("app")  # Pods can be scheduled on same node
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Service](../networking/service.md)** - For service discovery
- **[Ingress](../networking/ingress.md)** - For external access
- **[Volume](../storage/volume.md)** - For persistent storage

## Next Steps

- **[Service](../networking/service.md)** - Learn about service discovery
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 