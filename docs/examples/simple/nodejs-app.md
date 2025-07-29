# Node.js Application

This example demonstrates how to deploy a Node.js application with a database using Celestra DSL.

## Overview

This example shows how to:
- Deploy a Node.js application
- Set up a PostgreSQL database
- Configure service discovery
- Manage secrets and configuration
- Set up health checks

## Prerequisites

- Kubernetes cluster
- Celestra DSL installed
- kubectl configured

## Implementation

### 1. Basic Node.js Application

```python
from celestra import App, StatefulApp, Secret, ConfigMap

# Create PostgreSQL database
db = (StatefulApp("postgres")
    .image("postgres:14")
    .port(5432)
    .storage("10Gi")
    .environment({
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "myapp",
        "POSTGRES_PASSWORD": "password"
    })
    .expose())

# Create database secret
db_secret = (Secret("db-secret")
    .add("username", "myapp")
    .add("password", "password")
    .add("database", "myapp")
    .mount_as_env_vars(prefix="DB_"))

# Create Node.js application
app = (App("nodejs-app")
    .image("node:18-alpine")
    .port(3000)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3000"
    })
    .expose())

# Add database secret to app
app.add_secret(db_secret)

# Generate manifests
db.generate().to_yaml("./k8s/")
app.generate().to_yaml("./k8s/")
```

### 2. Production Node.js with Full Configuration

```python
from celestra import App, StatefulApp, Secret, ConfigMap, Health, Ingress

# Create PostgreSQL database
db = (StatefulApp("postgres-prod")
    .image("postgres:14")
    .port(5432)
    .storage("20Gi")
    .replicas(3)
    .resources(cpu="500m", memory="1Gi")
    .environment({
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "myapp"
    })
    .expose())

# Database secret
db_secret = (Secret("db-secret")
    .add("password", "secure-password-123")
    .add("host", "postgres-prod")
    .add("port", "5432")
    .mount_as_env_vars(prefix="DB_"))

# Application configuration
app_config = (ConfigMap("app-config")
    .add("config.json", """
{
    "server": {
        "port": 3000,
        "host": "0.0.0.0"
    },
    "database": {
        "pool": {
            "min": 2,
            "max": 10
        }
    },
    "logging": {
        "level": "info",
        "format": "json"
    }
}""")
    .mount_as_file("/app/config/config.json"))

# Health checks
health = (Health("app-health")
    .liveness_probe("/health", 3000, 30, 10, 5, 3)
    .readiness_probe("/ready", 3000, 5, 5, 3, 1)
    .startup_probe("/health", 3000, 30, 10, 5, 3))

# Create Node.js application
app = (App("nodejs-prod")
    .image("nodejs-app:1.0.0")
    .port(3000)
    .replicas(5)
    .resources(cpu="500m", memory="512Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3000"
    })
    .expose()
    .namespace("production"))

# Add configurations
app.add_secret(db_secret)
app.add_config(app_config)
app.add_health(health)

# Create ingress
ingress = (Ingress("app-ingress")
    .add_rule("api.example.com", "/", "nodejs-prod", 3000)
    .add_rule("api.example.com", "/api", "nodejs-prod", 3000)
    .tls_enabled(True)
    .add_tls_secret("app-tls"))

# Generate manifests
db.generate().to_yaml("./k8s/")
app.generate().to_yaml("./k8s/")
ingress.generate().to_yaml("./k8s/")
```

### 3. Node.js with Redis Cache

```python
from celestra import App, StatefulApp, Secret, ConfigMap

# Create Redis cache
redis = (StatefulApp("redis")
    .image("redis:7-alpine")
    .port(6379)
    .storage("5Gi")
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .expose())

# Redis secret
redis_secret = (Secret("redis-secret")
    .add("password", "redis-password")
    .mount_as_env_vars(prefix="REDIS_"))

# Create Node.js application with Redis
app = (App("nodejs-with-redis")
    .image("nodejs-app:1.0.0")
    .port(3000)
    .replicas(3)
    .resources(cpu="300m", memory="512Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3000",
        "REDIS_HOST": "redis",
        "REDIS_PORT": "6379"
    })
    .expose())

# Add secrets
app.add_secret(redis_secret)

# Generate manifests
redis.generate().to_yaml("./k8s/")
app.generate().to_yaml("./k8s/")
```

### 4. Node.js with Environment-Specific Configuration

```python
from celestra import App, ConfigMap, Secret

# Development configuration
dev_config = (ConfigMap("dev-config")
    .add("config.json", """
{
    "server": {
        "port": 3000,
        "host": "0.0.0.0"
    },
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "logging": {
        "level": "debug"
    }
}"""))

# Production configuration
prod_config = (ConfigMap("prod-config")
    .add("config.json", """
{
    "server": {
        "port": 3000,
        "host": "0.0.0.0"
    },
    "database": {
        "host": "postgres-prod",
        "port": 5432
    },
    "logging": {
        "level": "info"
    }
}"""))

# Development app
dev_app = (App("nodejs-dev")
    .image("nodejs-app:dev")
    .port(3000)
    .replicas(1)
    .resources(cpu="100m", memory="128Mi")
    .environment({"NODE_ENV": "development"})
    .add_config(dev_config)
    .expose())

# Production app
prod_app = (App("nodejs-prod")
    .image("nodejs-app:1.0.0")
    .port(3000)
    .replicas(5)
    .resources(cpu="500m", memory="512Mi")
    .environment({"NODE_ENV": "production"})
    .add_config(prod_config)
    .expose()
    .namespace("production"))

# Generate manifests
dev_app.generate().to_yaml("./k8s/dev/")
prod_app.generate().to_yaml("./k8s/prod/")
```

## Deployment

### 1. Apply the manifests

```bash
# Apply database first
kubectl apply -f k8s/postgres-*.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres --timeout=300s

# Apply application
kubectl apply -f k8s/nodejs-*.yaml

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods
```

### 2. Verify the deployment

```bash
# Check if pods are running
kubectl get pods -l app=nodejs-app

# Check database connection
kubectl exec -it <postgres-pod> -- psql -U myapp -d myapp

# Test the application
kubectl port-forward service/nodejs-app 3000:3000
curl http://localhost:3000/health
```

### 3. Monitor the application

```bash
# Check logs
kubectl logs -l app=nodejs-app

# Check resource usage
kubectl top pods -l app=nodejs-app

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Configuration Options

### Environment Variables

```python
# Add environment variables
app = (App("nodejs-app")
    .image("nodejs-app:1.0.0")
    .port(3000)
    .environment({
        "NODE_ENV": "production",
        "PORT": "3000",
        "LOG_LEVEL": "info",
        "API_VERSION": "v1"
    }))
```

### Resource Management

```python
# Set resource limits
app = (App("nodejs-app")
    .image("nodejs-app:1.0.0")
    .port(3000)
    .resources(
        cpu="500m",
        memory="512Mi",
        cpu_limit="1000m",
        memory_limit="1Gi"
    ))
```

### Health Checks

```python
# Configure health checks
health = (Health("app-health")
    .liveness_probe("/health", 3000, 30, 10, 5, 3)
    .readiness_probe("/ready", 3000, 5, 5, 3, 1))

app = App("nodejs-app").add_health(health)
```

### Secrets Management

```python
# Add secrets
app_secret = (Secret("app-secret")
    .add("jwt_secret", "your-jwt-secret")
    .add("api_key", "your-api-key")
    .mount_as_env_vars(prefix="APP_"))

app = App("nodejs-app").add_secret(app_secret)
```

## Troubleshooting

### Common Issues

1. **Database connection issues**
   ```bash
   kubectl logs -l app=nodejs-app
   kubectl exec -it <pod> -- env | grep DB_
   ```

2. **Application not starting**
   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name> --previous
   ```

3. **Health checks failing**
   ```bash
   kubectl describe pod <pod-name>
   kubectl exec -it <pod> -- curl http://localhost:3000/health
   ```

### Debug Commands

```bash
# Check pod status
kubectl get pods -o wide

# Check service endpoints
kubectl get endpoints

# Check configuration
kubectl describe configmap app-config

# Check secrets
kubectl describe secret app-secret

# Check logs with timestamps
kubectl logs -l app=nodejs-app --timestamps
```

## Best Practices

### 1. **Use Specific Image Tags**
```python
# ✅ Good: Use specific version
app = App("nodejs-app").image("nodejs-app:1.0.0")

# ❌ Bad: Use latest tag
app = App("nodejs-app").image("nodejs-app:latest")
```

### 2. **Set Resource Limits**
```python
# ✅ Good: Set resource limits
app = App("nodejs-app").resources(cpu="500m", memory="512Mi")

# ❌ Bad: No resource limits
app = App("nodejs-app")  # No resource limits
```

### 3. **Use Secrets for Sensitive Data**
```python
# ✅ Good: Use secrets for sensitive data
secret = Secret("app-secret").add("password", "secure-password")
app.add_secret(secret)

# ❌ Bad: Use ConfigMaps for secrets
config = ConfigMap("app-config").add("password", "secure-password")
app.add_config(config)
```

### 4. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
health = Health("health").liveness_probe("/health")
app.add_health(health)

# ❌ Bad: No health checks
app = App("nodejs-app")  # No health checks
```

### 5. **Use Environment-Specific Configurations**
```python
# ✅ Good: Use environment-specific configs
if environment == "production":
    app = App("nodejs-prod").resources(cpu="500m", memory="512Mi")
else:
    app = App("nodejs-dev").resources(cpu="100m", memory="128Mi")

# ❌ Bad: Same config for all environments
app = App("nodejs-app")  # Same config everywhere
```

## Next Steps

1. **[Production Deployments](../production/index.md)** - Learn about production configurations
2. **[Microservices Tutorial](../../tutorials/microservices.md)** - Build microservices architecture
3. **[App Component](../../components/core/app.md)** - Complete App documentation

Ready to build something more complex? Check out the [Production Deployments](../production/index.md) or jump to [Microservices Tutorial](../../tutorials/microservices.md)! 