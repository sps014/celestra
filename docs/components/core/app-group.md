# AppGroup Component

The `AppGroup` component allows you to manage multiple related applications as a single unit, providing coordinated deployment and management of microservices and application suites.

## Overview

Use `AppGroup` for:
- **Microservices** - Group related services together
- **Application Suites** - Manage multi-component applications
- **Environment Management** - Deploy complete environments
- **Dependency Management** - Handle service dependencies

## Basic Usage

```python
from celestra import AppGroup, App, StatefulApp

# Create individual services
user_service = App("user-service").image("user:latest").port(8080)
order_service = App("order-service").image("order:latest").port(8080)
database = StatefulApp("postgres").image("postgres:13").storage("10Gi")

# Group them together
ecommerce = (AppGroup("ecommerce-platform")
    .add_service(user_service)
    .add_service(order_service)
    .add_service(database))
```

## Configuration Methods

### Adding Services

```python
# Add individual services
app_group = (AppGroup("web-platform")
    .add_service(App("frontend").image("react:latest"))
    .add_service(App("backend").image("node:latest"))
    .add_service(StatefulApp("redis").image("redis:latest")))

# Add multiple services at once
services = [
    App("api").image("api:latest"),
    App("worker").image("worker:latest"),
    StatefulApp("database").image("postgres:latest")
]
app_group = AppGroup("platform").add_services(services)
```

### Dependencies and Ordering

```python
# Define service dependencies
app_group = (AppGroup("microservices")
    .add_service(database)
    .add_service(api.depends_on(database))
    .add_service(worker.depends_on(database))
    .add_service(frontend.depends_on(api)))
```

### Shared Configuration

```python
# Apply configuration to all services
app_group = (AppGroup("production-stack")
    .add_service(user_service)
    .add_service(order_service)
    .namespace("production")
    .label("environment", "prod")
    .label("team", "backend")
    .annotation("managed-by", "Celestra"))
```

## Complete Example

```python
#!/usr/bin/env python3
"""
E-commerce Platform with AppGroup
"""

from celestra import AppGroup, App, StatefulApp, Service, Secret, ConfigMap, KubernetesOutput

def create_ecommerce_platform():
    # Shared configuration
    shared_config = ConfigMap("ecommerce-config")
    shared_config.add_data("database.host", "postgres.ecommerce.svc.cluster.local")
    shared_config.add_data("redis.host", "redis.ecommerce.svc.cluster.local")
    shared_config.add_data("log.level", "info")
    
    # Shared secrets
    shared_secrets = Secret("ecommerce-secrets")
    shared_secrets.add_data("database.password", "dbsecret123")
    shared_secrets.add_data("jwt.secret", "jwtsecret456")
    shared_secrets.add_data("api.key", "apisecret789")
    
    # Database layer
    postgres = (StatefulApp("postgres")
        .image("postgres:13")
        .port(5432, "postgres")
        .env("POSTGRES_DB", "ecommerce")
        .env_from_secret("ecommerce-secrets", "POSTGRES_PASSWORD", "database.password")
        .storage("/var/lib/postgresql/data", "50Gi")
        .resources(cpu="1000m", memory="2Gi")
        .replicas(1))
    
    redis = (StatefulApp("redis")
        .image("redis:6-alpine")
        .port(6379, "redis")
        .storage("/data", "5Gi")
        .resources(cpu="200m", memory="512Mi"))
    
    # Microservices layer
    user_service = (App("user-service")
        .image("ecommerce/user-service:v1.2.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .env_from_configmap("ecommerce-config", "DATABASE_URL", "database.host")
        .env_from_configmap("ecommerce-config", "REDIS_URL", "redis.host")
        .env_from_secret("ecommerce-secrets", "JWT_SECRET", "jwt.secret")
        .resources(cpu="500m", memory="1Gi")
        .replicas(3)
        .expose())
    
    order_service = (App("order-service")
        .image("ecommerce/order-service:v1.2.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .env_from_configmap("ecommerce-config", "DATABASE_URL", "database.host")
        .env_from_configmap("ecommerce-config", "REDIS_URL", "redis.host")
        .env_from_secret("ecommerce-secrets", "JWT_SECRET", "jwt.secret")
        .env("USER_SERVICE_URL", "http://user-service:8080")
        .resources(cpu="500m", memory="1Gi")
        .replicas(3)
        .expose())
    
    payment_service = (App("payment-service")
        .image("ecommerce/payment-service:v1.2.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .env_from_configmap("ecommerce-config", "DATABASE_URL", "database.host")
        .env_from_secret("ecommerce-secrets", "API_KEY", "api.key")
        .env("ORDER_SERVICE_URL", "http://order-service:8080")
        .resources(cpu="300m", memory="512Mi")
        .replicas(2)
        .expose())
    
    # Frontend layer
    frontend = (App("frontend")
        .image("ecommerce/frontend:v1.2.0")
        .port(80, "http")
        .env("API_BASE_URL", "http://api-gateway")
        .resources(cpu="200m", memory="256Mi")
        .replicas(2)
        .expose())
    
    # API Gateway
    api_gateway = (App("api-gateway")
        .image("nginx:1.21")
        .port(80, "http")
        .port(443, "https")
        .env("USER_SERVICE", "user-service:8080")
        .env("ORDER_SERVICE", "order-service:8080")
        .env("PAYMENT_SERVICE", "payment-service:8080")
        .resources(cpu="200m", memory="256Mi")
        .replicas(2)
        .expose())
    
    # Group everything together
    ecommerce_platform = (AppGroup("ecommerce-platform")
        # Infrastructure layer
        .add_service(postgres)
        .add_service(redis)
        # Application layer
        .add_service(user_service)
        .add_service(order_service)
        .add_service(payment_service)
        # Presentation layer
        .add_service(frontend)
        .add_service(api_gateway)
        # Shared configuration
        .namespace("ecommerce")
        .label("platform", "ecommerce")
        .label("managed-by", "Celestra")
        .annotation("version", "v1.2.0")
        .annotation("contact", "platform-team@company.com"))
    
    return shared_config, shared_secrets, ecommerce_platform

if __name__ == "__main__":
    config, secrets, platform = create_ecommerce_platform()
    
    # Generate all components
    components = [config, secrets]
    components.extend(platform.get_all_services())
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "ecommerce-platform/")
    
    print("✅ E-commerce platform generated!")
    print("🚀 Deploy: kubectl apply -f ecommerce-platform/")
    print("🌐 Services:", [s.name for s in platform.get_all_services()])
```

## Advanced Features

### Service Dependencies

```python
# Define deployment order with dependencies
platform = (AppGroup("data-platform")
    .add_service(database)
    .add_service(api.depends_on("postgres"))
    .add_service(worker.depends_on("postgres", "api"))
    .add_service(frontend.depends_on("api")))
```

### Health Checks and Readiness

```python
# Group-wide health monitoring
platform = (AppGroup("web-platform")
    .add_service(database)
    .add_service(api)
    .add_service(frontend)
    .enable_health_checks()
    .readiness_timeout(300))  # Wait 5 minutes for all services
```

### Scaling Policies

```python
# Coordinated scaling
platform = (AppGroup("microservices")
    .add_service(user_service)
    .add_service(order_service)
    .scale_together(True)  # Scale all services proportionally
    .min_replicas(2)
    .max_replicas(10))
```

### Environment Management

```python
# Different configurations per environment
def create_environment_platform(env: str):
    if env == "development":
        config = {
            "replicas": 1,
            "resources": {"cpu": "100m", "memory": "256Mi"},
            "image_tag": "dev"
        }
    elif env == "staging":
        config = {
            "replicas": 2,
            "resources": {"cpu": "500m", "memory": "1Gi"},
            "image_tag": "staging"
        }
    else:  # production
        config = {
            "replicas": 3,
            "resources": {"cpu": "1000m", "memory": "2Gi"},
            "image_tag": "v1.0.0"
        }
    
    platform = (AppGroup(f"platform-{env}")
        .add_service(
            App("api")
            .image(f"api:{config['image_tag']}")
            .replicas(config["replicas"])
            .resources(**config["resources"])
        )
        .namespace(env)
        .label("environment", env))
    
    return platform
```

## Multi-Environment Example

```python
#!/usr/bin/env python3
"""
Multi-Environment Platform Deployment
"""

def create_multi_env_platform():
    environments = ["development", "staging", "production"]
    platforms = {}
    
    for env in environments:
        # Environment-specific configuration
        if env == "development":
            replicas = 1
            resources = {"cpu": "100m", "memory": "256Mi"}
            db_storage = "5Gi"
        elif env == "staging":
            replicas = 2
            resources = {"cpu": "500m", "memory": "1Gi"}
            db_storage = "20Gi"
        else:  # production
            replicas = 5
            resources = {"cpu": "1000m", "memory": "2Gi"}
            db_storage = "100Gi"
        
        # Create services for this environment
        database = (StatefulApp(f"postgres-{env}")
            .image("postgres:13")
            .storage("/data", db_storage)
            .replicas(1 if env != "production" else 3))
        
        api = (App(f"api-{env}")
            .image(f"api:{env}")
            .replicas(replicas)
            .resources(**resources)
            .expose())
        
        frontend = (App(f"frontend-{env}")
            .image(f"frontend:{env}")
            .replicas(replicas)
            .resources(**resources)
            .expose())
        
        # Create platform for this environment
        platform = (AppGroup(f"platform-{env}")
            .add_service(database)
            .add_service(api)
            .add_service(frontend)
            .namespace(env)
            .label("environment", env)
            .label("platform", "myapp"))
        
        platforms[env] = platform
    
    return platforms

# Deploy all environments
platforms = create_multi_env_platform()
for env, platform in platforms.items():
    print(f"Deploying {env} environment...")
    # Generate and deploy each environment
```

## Generated Resources

AppGroup generates all resources from its constituent services plus coordination resources:

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce
  labels:
    platform: ecommerce
    managed-by: Celestra
```

### Services and Deployments

All individual service resources plus:

```yaml
# Service discovery helpers
apiVersion: v1
kind: ConfigMap
metadata:
  name: service-discovery
  namespace: ecommerce
data:
  user-service: "user-service.ecommerce.svc.cluster.local:8080"
  order-service: "order-service.ecommerce.svc.cluster.local:8080"
  payment-service: "payment-service.ecommerce.svc.cluster.local:8080"
```

## Best Practices

!!! tip "AppGroup Design Guidelines"
    
    **Service Organization:**
    - Group related services that deploy together
    - Keep groups small and focused (5-10 services max)
    - Use clear, descriptive group names
    
    **Dependencies:**
    - Define clear dependency relationships
    - Avoid circular dependencies
    - Use health checks to ensure readiness
    
    **Configuration:**
    - Share common configuration via ConfigMaps
    - Use consistent labeling strategy
    - Apply security policies group-wide
    
    **Deployment:**
    - Test deployment order in staging
    - Plan for rollback scenarios
    - Monitor group health collectively

## Common Patterns

### Three-Tier Architecture

```python
# Separate tiers as different groups
frontend_tier = AppGroup("frontend").add_service(web_app).add_service(cdn)
backend_tier = AppGroup("backend").add_service(api).add_service(auth)
data_tier = AppGroup("data").add_service(database).add_service(cache)

# Or combined
three_tier = (AppGroup("web-application")
    .add_service(web_app)     # Presentation
    .add_service(api)         # Logic
    .add_service(database))   # Data
```

### Microservices Platform

```python
# Domain-based microservices
user_domain = AppGroup("user-domain").add_service(user_service).add_service(auth_service)
order_domain = AppGroup("order-domain").add_service(order_service).add_service(inventory_service)
platform = AppGroup("ecommerce").add_group(user_domain).add_group(order_domain)
```

## API Reference

::: src.celestra.core.app_group.AppGroup
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[App](app.md)** - Individual applications
- **[StatefulApp](stateful-app.md)** - Stateful services
- **[Service](../networking/service.md)** - Service networking
- **[ConfigMap](../storage/config-map.md)** - Shared configuration

---

**Next:** Learn about [Job](../workloads/job.md) for batch processing workloads. 