# K8s-Gen DSL Overview

A Python-based Domain-Specific Language for generating Kubernetes manifests with minimal complexity.

## Design Principles

### 1. Simplicity Over Configuration
- **No YAML Required**: Write infrastructure as Python code
- **Business Language**: Use terms like `App`, `Database`, `Cache` instead of `Deployment`, `StatefulSet`, `Service`
- **Smart Defaults**: Sensible defaults with easy customization

### 2. Progressive Disclosure
- **Start Simple**: `App("api").image("myapp:latest").port(8080)`
- **Add Complexity When Needed**: Scale, security, monitoring, etc.
- **Environment Aware**: Same code, different configs for dev/staging/prod

### 3. Multi-Format Output
- **Kubernetes YAML**: Production deployments
- **Docker Compose**: Local development
- **Helm Charts**: Package management
- **Terraform**: Infrastructure as Code

## Core Concepts

### Applications vs. Stateful Services

```python
# Stateless application (scales horizontally)
api = App("api-service").image("myorg/api:v1.0").port(8080)

# Stateful service (requires persistent storage)
database = StatefulApp("database").image("database-server:latest").storage("20Gi")
cache = StatefulApp("cache").image("cache-server:latest").storage("5Gi")
```

### Service Discovery and Dependencies

```python
# Automatic service discovery
api.connect_to([database, cache])

# Dependency management
frontend.depends_on([api, auth_service])
```

## Quick Start Example

```python
from k8s_gen import App, StatefulApp, AppGroup

# Database service
database = StatefulApp("database").image("database-server:latest").storage("20Gi")

# Web application
app = (App("web-app")
    .image("web-server:latest")
    .port(8080)
    .connect_to([database])
    .scale(replicas=3, auto_scale_on_cpu=70)
    .expose(external_access=True))

# Generate all outputs
app.generate().to_yaml("./k8s/")
app.generate().to_docker_compose("./docker-compose.yml")
```

This generates complete Kubernetes manifests, Docker Compose files, and more with just a few lines of Python code.

## Key Benefits

### For Developers
- **Familiar Syntax**: If you know Python, you know K8s-Gen
- **No YAML Debugging**: Catch errors at "compile time"
- **Local Development**: Start with Docker Compose, deploy to Kubernetes
- **Type Safety**: IDE completion and error detection

### For DevOps Teams
- **Standardization**: Consistent patterns across teams
- **Security by Default**: RBAC, secrets, network policies
- **Multi-Environment**: Same code, different configurations
- **Observability Ready**: Built-in monitoring and logging

### For Organizations
- **Reduced Learning Curve**: Abstract Kubernetes complexity
- **Faster Onboarding**: Developers focus on business logic
- **Cost Optimization**: Built-in resource management
- **Compliance**: Security and governance built-in

## Simple Example

```python
# The simplest possible application
app = App("hello-world").image("web-server:latest").port(8080)

# Generate Kubernetes YAML
app.generate().to_yaml("./k8s/")
```

This creates a complete Kubernetes `Deployment`, `Service`, and optional `Ingress` with production-ready defaults. 