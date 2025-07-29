# Quick Start Guide

Get up and running with Celestra in 5 minutes! This guide will walk you through creating your first application and deploying it to Kubernetes.

## Prerequisites

Before you begin, make sure you have:

- **Python 3.8+** installed
- **Docker** installed (for local development)
- **kubectl** configured (for Kubernetes deployment)
- **A Kubernetes cluster** (local or remote)

## Installation

### Option 1: Install from PyPI (Recommended)

```bash
pip install celestra
```

### Option 2: Install from Source

```bash
git clone https://github.com/sps014/celestra.git
cd celestra
pip install -e src/
```

## Your First Application

Let's create a simple web application that demonstrates Celestra's core features.

### 1. Create the Application

Create a file called `my_first_app.py`:

```python
from celestra import App, StatefulApp, Secret, ConfigMap

# Database credentials
db_secret = (Secret("db-secret")
    .add("username", "admin")
    .add("password", "secure-password"))

# Database configuration
db_config = (ConfigMap("db-config")
    .add("database", "myapp")
    .add("max_connections", "100"))

# Database
database = (StatefulApp("postgres")
    .image("postgres:15")
    .port(5432)
    .storage("10Gi")
    .add_secret(db_secret)
    .add_config(db_config))

# Web application
web_app = (App("web-app")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .resources(cpu="500m", memory="512Mi")
    .add_secret(db_secret)
    .add_config(db_config)
    .expose())

# Generate Kubernetes manifests
web_app.generate().to_yaml("./k8s/")
database.generate().to_yaml("./k8s/")
db_secret.generate().to_yaml("./k8s/")
db_config.generate().to_yaml("./k8s/")

print("✅ Kubernetes manifests generated in ./k8s/")
```

### 2. Run the Application

```bash
python my_first_app.py
```

This will create a `k8s/` directory with all the necessary Kubernetes manifests.

### 3. Deploy to Kubernetes

```bash
kubectl apply -f ./k8s/
```

### 4. Check the Deployment

```bash
kubectl get pods
kubectl get services
kubectl get configmaps
kubectl get secrets
```

## What Just Happened?

Let's break down what Celestra created for you:

### 1. **Database (StatefulApp)**
- **PostgreSQL StatefulSet** with persistent storage
- **Service** for database connectivity
- **Secret** for database credentials
- **ConfigMap** for database configuration

### 2. **Web Application (App)**
- **Deployment** with 3 replicas
- **Service** for load balancing
- **Resource limits** for CPU and memory
- **Secret and ConfigMap** mounted as environment variables

### 3. **Security**
- **Secrets** for sensitive data
- **ConfigMaps** for configuration
- **RBAC** (if enabled)

## Next Steps

### Explore the Generated Files

Check out what was created in the `k8s/` directory:

```bash
ls -la k8s/
```

You'll see files like:
- `web-app-deployment.yaml`
- `web-app-service.yaml`
- `postgres-statefulset.yaml`
- `postgres-service.yaml`
- `db-secret.yaml`
- `db-config-configmap.yaml`

### Customize Your Application

Try modifying the application:

```python
# Add environment variables
web_app = (App("web-app")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .env("DEBUG", "false")
    .env("ENVIRONMENT", "production")
    .expose())

# Add health checks
web_app = (App("web-app")
    .image("nginx:latest")
    .port(80)
    .health_check("/health")
    .liveness_probe("/health")
    .readiness_probe("/ready")
    .expose())

# Add resource limits
web_app = (App("web-app")
    .image("nginx:latest")
    .port(80)
    .resources(
        cpu="500m", 
        memory="512Mi",
        cpu_limit="1000m",
        memory_limit="1Gi"
    )
    .expose())
```

### Generate Different Outputs

Celestra supports multiple output formats:

```python
# Kubernetes YAML
web_app.generate().to_yaml("./k8s/")

# Docker Compose (for local development)
web_app.generate().to_docker_compose("./docker-compose.yml")

# Helm Chart
web_app.generate().to_helm_chart("./charts/")

# Kustomize
web_app.generate().to_kustomize("./kustomize/")
```

## Common Patterns

### Multi-Service Application

```python
from celestra import App, StatefulApp, AppGroup

# Create an application group
platform = AppGroup("my-platform")

# Database
database = StatefulApp("postgres").image("postgres:15").port(5432).storage("20Gi")

# API Service
api = App("api").image("myapp/api:latest").port(8080).replicas(3)

# Frontend
frontend = App("frontend").image("myapp/frontend:latest").port(80).replicas(2)

# Add all services to the group
platform.add([database, api, frontend])

# Generate everything
platform.generate().to_yaml("./k8s/")
```

### Environment-Specific Configuration

```python
# Development
dev_app = (App("myapp-dev")
    .image("myapp:latest")
    .port(8080)
    .replicas(1)
    .resources(cpu="100m", memory="256Mi")
    .env("ENVIRONMENT", "development"))

# Production
prod_app = (App("myapp")
    .image("myapp:latest")
    .port(8080)
    .replicas(5)
    .resources(cpu="500m", memory="1Gi")
    .env("ENVIRONMENT", "production"))

dev_app.generate().to_yaml("./dev/")
prod_app.generate().to_yaml("./prod/")
```

## Troubleshooting

### Common Issues

**1. Import Error**
```bash
ModuleNotFoundError: No module named 'celestra'
```
**Solution**: Install Celestra: `pip install celestra`

**2. Kubernetes Connection Error**
```bash
The connection to the server localhost:8080 was refused
```
**Solution**: Start your Kubernetes cluster (e.g., `minikube start`)

**3. Permission Denied**
```bash
Error from server (Forbidden)
```
**Solution**: Check your kubectl configuration and permissions

### Getting Help

- **Documentation**: Browse the [complete documentation](../index.md)
- **Examples**: Check out [example applications](../examples/index.md)
- **Issues**: Report problems on [GitHub Issues](https://github.com/sps014/Celestra/issues)

## What's Next?

Now that you've created your first application, explore:

- **[Core Concepts](core-concepts.md)** - Understand Celestra's fundamental concepts
- **[Components Guide](../components/index.md)** - Learn about all available components
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides for complex scenarios
- **[Examples](../examples/index.md)** - Real-world examples and patterns

Ready to build something more complex? Check out the [Kafka Deployment Tutorial](../tutorials/kafka-deployment.md) or [Microservices Guide](../tutorials/microservices.md)! 