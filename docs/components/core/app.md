# App Component

The `App` component is the primary building block for stateless applications in Celestra. It generates Kubernetes Deployments and Services for your applications.

## Overview

Use the `App` component for:
- **Web applications** - APIs, frontend services
- **Microservices** - Individual service components
- **Stateless workloads** - Applications that don't need persistent storage

## Basic Usage

```python
from src.k8s_gen import App

# Simple web application
app = (App("my-web-app")
    .image("nginx:1.21")
    .port(8080)
    .replicas(3)
    .expose())
```

## Configuration Methods

### Image and Basic Setup

```python
app = (App("api-service")
    .image("myapp:v1.2.0")           # Container image
    .tag("latest")                   # Image tag
    .pull_policy("Always"))          # Image pull policy
```

### Ports and Networking

```python
app = (App("web-app")
    .port(8080, "http")             # Add a port with name
    .http_port(8080, "main")        # HTTP port helper
    .https_port(8443, "secure")     # HTTPS port helper
    .metrics_port(9090, "metrics")  # Metrics port helper
    .admin_port(9000, "admin")      # Admin port helper
    .grpc_port(9091, "grpc")        # gRPC port helper
    .expose())                      # Create Service automatically
```

### Environment Variables

```python
app = (App("backend")
    .env("DATABASE_URL", "postgres://...")
    .env("LOG_LEVEL", "info")
    .env("DEBUG", "false")
    .env_from_secret("db-secret", "DATABASE_PASSWORD")
    .env_from_configmap("app-config", "API_KEY"))
```

### Resource Management

```python
app = (App("cpu-intensive")
    .resources(
        cpu="500m",           # CPU request
        memory="1Gi",         # Memory request
        cpu_limit="1000m",    # CPU limit
        memory_limit="2Gi"    # Memory limit
    ))
```

### Scaling and Replicas

```python
app = (App("scalable-app")
    .replicas(5)              # Static replica count
    .auto_scale(              # Horizontal Pod Autoscaler
        min_replicas=2,
        max_replicas=10,
        cpu_percent=80
    ))
```

### Health Checks

```python
app = (App("monitored-app")
    .liveness_probe("/health", port=8080, initial_delay=30)
    .readiness_probe("/ready", port=8080, initial_delay=10)
    .startup_probe("/startup", port=8080, initial_delay=5))
```

### Storage and Volumes

```python
app = (App("file-processor")
    .storage("/data", "10Gi")              # Persistent volume
    .temp_storage("/tmp", "1Gi")           # Temporary storage
    .config_volume("/config", "app-config") # ConfigMap volume
    .secret_volume("/secrets", "app-secret")) # Secret volume
```

## Advanced Configuration

### Labels and Annotations

```python
app = (App("labeled-app")
    .label("environment", "production")
    .label("team", "backend")
    .annotation("prometheus.io/scrape", "true")
    .annotation("prometheus.io/port", "9090"))
```

### Namespace and Service Account

```python
app = (App("secure-app")
    .namespace("production")
    .service_account("app-service-account"))
```

### Lifecycle Hooks

```python
app = (App("lifecycle-app")
    .post_start_exec(["sh", "-c", "echo 'Starting' > /tmp/started"])
    .pre_stop_exec(["sh", "-c", "echo 'Stopping' > /tmp/stopped"]))
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete App Example - E-commerce API Service
"""

from src.k8s_gen import App, Secret, ConfigMap, KubernetesOutput

def create_ecommerce_api():
    # Configuration
    config = ConfigMap("api-config")
    config.add_data("database.host", "postgres.default.svc.cluster.local")
    config.add_data("redis.host", "redis.default.svc.cluster.local")
    config.add_data("log.level", "info")
    
    # Secrets
    secret = Secret("api-secrets")
    secret.add_data("database.password", "supersecret")
    secret.add_data("jwt.secret", "jwt-signing-key")
    secret.add_data("stripe.key", "sk_live_...")
    
    # Application
    api = (App("ecommerce-api")
        .image("ecommerce/api:v2.1.0")
        .pull_policy("Always")
        
        # Networking
        .http_port(8080, "api")
        .metrics_port(9090, "metrics")
        .admin_port(9000, "admin")
        .expose()
        
        # Environment
        .env("NODE_ENV", "production")
        .env("PORT", "8080")
        .env_from_configmap("api-config", "DATABASE_HOST", "database.host")
        .env_from_configmap("api-config", "REDIS_HOST", "redis.host")
        .env_from_configmap("api-config", "LOG_LEVEL", "log.level")
        .env_from_secret("api-secrets", "DATABASE_PASSWORD", "database.password")
        .env_from_secret("api-secrets", "JWT_SECRET", "jwt.secret")
        .env_from_secret("api-secrets", "STRIPE_KEY", "stripe.key")
        
        # Resources
        .resources(
            cpu="1000m",
            memory="2Gi", 
            cpu_limit="2000m",
            memory_limit="4Gi"
        )
        
        # Scaling
        .replicas(3)
        .auto_scale(min_replicas=3, max_replicas=20, cpu_percent=70)
        
        # Health checks
        .liveness_probe("/health", port=8080, initial_delay=60)
        .readiness_probe("/ready", port=8080, initial_delay=30)
        .startup_probe("/startup", port=8080, initial_delay=10)
        
        # Storage for logs and cache
        .temp_storage("/tmp", "1Gi")
        .storage("/app/logs", "5Gi")
        
        # Metadata
        .label("app", "ecommerce")
        .label("component", "api")
        .label("environment", "production")
        .annotation("prometheus.io/scrape", "true")
        .annotation("prometheus.io/port", "9090")
        .annotation("prometheus.io/path", "/metrics")
        
        # Security
        .namespace("ecommerce")
        .service_account("ecommerce-api"))
    
    return config, secret, api

if __name__ == "__main__":
    config, secret, api = create_ecommerce_api()
    
    # Generate Kubernetes resources
    components = [config, secret, api]
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "ecommerce-api/")
    
    print("✅ E-commerce API generated!")
    print("🚀 Deploy: kubectl apply -f ecommerce-api/")
```

## Generated Resources

The App component generates these Kubernetes resources:

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ecommerce-api
  namespace: ecommerce
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ecommerce-api
  template:
    spec:
      containers:
      - name: ecommerce-api
        image: ecommerce/api:v2.1.0
        ports:
        - containerPort: 8080
          name: api
        - containerPort: 9090
          name: metrics
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 2000m
            memory: 4Gi
```

### Service (when using .expose())

```yaml
apiVersion: v1
kind: Service
metadata:
  name: ecommerce-api
  namespace: ecommerce
spec:
  selector:
    app: ecommerce-api
  ports:
  - port: 8080
    targetPort: 8080
    name: api
  - port: 9090
    targetPort: 9090
    name: metrics
```

## Best Practices

!!! tip "Production Guidelines"
    
    **Resource Limits:**
    - Always set resource requests and limits
    - Monitor actual usage to tune settings
    - Use vertical scaling recommendations
    
    **Health Checks:**
    - Implement proper health endpoints
    - Set appropriate timeouts and delays
    - Test health checks in staging
    
    **Security:**
    - Use specific image tags, not `latest`
    - Set `imagePullPolicy: Always` for production
    - Use service accounts with minimal permissions
    
    **Scaling:**
    - Start with manual scaling, add HPA later
    - Monitor scaling events and tune thresholds
    - Set appropriate min/max replica counts

## Common Patterns

### Development vs Production

```python
# Development
dev_app = (App("myapp-dev")
    .image("myapp:dev")
    .replicas(1)
    .resources(cpu="100m", memory="256Mi")
    .env("DEBUG", "true"))

# Production  
prod_app = (App("myapp")
    .image("myapp:v1.0.0")
    .replicas(3)
    .resources(cpu="500m", memory="1Gi", cpu_limit="1000m", memory_limit="2Gi")
    .env("DEBUG", "false")
    .auto_scale(min_replicas=3, max_replicas=10))
```

### Multi-Container Pods

```python
# Main application with sidecar
app = (App("app-with-sidecar")
    .image("myapp:latest")
    .port(8080)
    .sidecar("log-shipper", "fluent/fluent-bit:latest")
    .sidecar_port("log-shipper", 24224))
```

## API Reference

::: src.celestra.core.app.App
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[StatefulApp](stateful-app.md)** - For stateful applications
- **[Service](../networking/service.md)** - Network service configuration
- **[Ingress](../networking/ingress.md)** - External access
- **[ConfigMap](../storage/config-map.md)** - Configuration management
- **[Secret](../security/secrets.md)** - Secret management

---

**Next:** Learn about [StatefulApp](stateful-app.md) for stateful workloads. 