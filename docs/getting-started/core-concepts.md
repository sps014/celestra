# Core Concepts

This guide explains the fundamental concepts behind Celestra and how they work together to simplify Kubernetes application deployment.

## 🎯 Design Philosophy

Celestra is built around three core principles:

### 1. **Simplicity Over Configuration**
Instead of writing complex YAML, you write simple Python code:

```python
# Instead of 50+ lines of YAML...
app = App("my-app").image("nginx:latest").port(80).expose()
```

### 2. **Progressive Disclosure**
Start simple, add complexity when needed:

```python
# Start simple
app = App("my-app").image("nginx:latest").port(80)

# Add features as needed
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .resources(cpu="500m", memory="512Mi")
    .health_check("/health")
    .expose())
```

### 3. **Multi-Format Output**
Write once, deploy anywhere:

```python
# Same code, multiple outputs
app.generate().to_yaml("./k8s/")                    # Kubernetes
app.generate().to_docker_compose("./docker-compose.yml")  # Local dev
app.generate().to_helm_chart("./charts/")           # Helm packaging
```

## 🏗️ Architecture Overview

Celestra provides a layered architecture that abstracts Kubernetes complexity:

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │     App     │  │ StatefulApp │  │     Job     │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Celestra Core                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Validation  │  │ Templates   │  │   Plugins   │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Output Layer                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │
│  │ Kubernetes  │  │Docker Compose│  │   Helm      │      │
│  └─────────────┘  └─────────────┘  └─────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Components

### Applications vs. Stateful Services

Celestra distinguishes between two main types of applications:

#### **App** - Stateless Applications
For applications that can be horizontally scaled without persistent storage concerns:

```python
from celestra import App

# Web applications, APIs, microservices
web_app = (App("web-app")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .expose())

# API services
api = (App("api-service")
    .image("myapp/api:v1.0")
    .port(8080)
    .replicas(5)
    .resources(cpu="500m", memory="1Gi"))
```

**Characteristics:**
- Horizontal scaling
- Rolling updates
- Load balancing
- No persistent storage
- Multiple replicas

#### **StatefulApp** - Stateful Applications
For applications that require persistent storage and stable network identities:

```python
from celestra import StatefulApp

# Databases
database = (StatefulApp("postgres")
    .image("postgres:15")
    .port(5432)
    .storage("20Gi")
    .replicas(3))

# Message queues
kafka = (StatefulApp("kafka")
    .image("confluentinc/cp-kafka:7.4.0")
    .kafka_port(9092)
    .storage("100Gi")
    .replicas(3))
```

**Characteristics:**
- Persistent storage
- Stable network identities
- Ordered deployment
- Database-specific helpers
- Backup scheduling

## 🔗 Service Discovery and Dependencies

### Automatic Service Discovery

Celestra automatically handles service discovery between components:

```python
from celestra import App, StatefulApp

# Database
database = StatefulApp("postgres").image("postgres:15").port(5432)

# API that connects to database
api = (App("api")
    .image("myapp/api:latest")
    .port(8080)
    .connect_to([database]))  # Automatic service discovery

# Frontend that connects to API
frontend = (App("frontend")
    .image("myapp/frontend:latest")
    .port(80)
    .connect_to([api]))  # Chained dependencies
```

### Dependency Management

```python
from celestra import AppGroup

# Create an application group
platform = AppGroup("my-platform")

# Add components with dependencies
platform.add([
    database,  # Database first
    api,       # API depends on database
    frontend   # Frontend depends on API
])

# Generate with proper dependency order
platform.generate().to_yaml("./k8s/")
```

## 🔒 Security by Default

### Built-in Security Features

Celestra includes security features by default:

```python
from celestra import App, Secret, ServiceAccount, Role

# Secure application with RBAC
secure_app = (App("secure-app")
    .image("myapp:latest")
    .port(8080)
    .add_service_account(ServiceAccount("app-sa"))
    .add_role(Role("app-role").add_policy("read", "pods"))
    .add_secret(Secret("app-secret").add("api_key", "secret-value"))
    .add_network_policy(NetworkPolicy("app-policy").deny_all()))
```

### Security Components

- **Secrets** - Manage sensitive data
- **ServiceAccounts** - Identity for applications
- **Roles/RoleBindings** - Access control
- **NetworkPolicies** - Network security
- **SecurityPolicies** - Pod security standards

## 📊 Resource Management

### Resource Allocation

Celestra provides intelligent resource management:

```python
# Automatic resource allocation
app = App("my-app").image("nginx:latest").port(80)

# Manual resource specification
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .resources(
        cpu="500m",           # CPU request
        memory="512Mi",        # Memory request
        cpu_limit="1000m",     # CPU limit
        memory_limit="1Gi"     # Memory limit
    ))
```

### Cost Optimization

```python
from celestra import CostOptimization

# Enable cost optimization
optimizer = CostOptimization("optimizer")
optimizer.resource_optimization()
optimizer.spot_instance_recommendation()
optimizer.storage_optimization()
```

## 🔄 Deployment Strategies

### Rolling Updates

```python
# Default rolling update
app = App("my-app").image("nginx:latest").port(80)

# Custom rolling update
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .rolling_update(
        max_surge=1,
        max_unavailable=0,
        min_ready_seconds=30
    ))
```

### Blue-Green Deployment

```python
# Blue-green deployment
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .deployment_strategy("blue-green")
    .health_check("/health")
    .rollback_on_failure())
```

### Canary Deployment

```python
# Canary deployment
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .deployment_strategy("canary")
    .canary_percentage(10)
    .promotion_criteria("success_rate > 95%"))
```

## 🔍 Observability

### Built-in Monitoring

```python
from celestra import Observability

# Enable observability
observability = Observability("monitoring")
observability.enable_metrics()
observability.enable_tracing()
observability.enable_logging()

# Add to application
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .add_observability(observability))
```

### Health Checks

```python
# Health checks
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .health_check("/health")
    .liveness_probe("/health")
    .readiness_probe("/ready")
    .startup_probe("/startup"))
```

## 🎨 Configuration Management

### Environment Variables

```python
# Environment variables
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .env("DEBUG", "false")
    .env("ENVIRONMENT", "production")
    .env("DATABASE_URL", "postgresql://localhost:5432/myapp"))
```

### ConfigMaps and Secrets

```python
from celestra import ConfigMap, Secret

# Configuration
config = (ConfigMap("app-config")
    .add("debug", "false")
    .add_json("features", {"new_ui": True})
    .from_file("nginx.conf", "configs/nginx.conf"))

# Secrets
secret = (Secret("app-secret")
    .add("api_key", "sk_live_...")
    .add("database_password", "secure-password"))

# Mount in application
app = (App("my-app")
    .image("nginx:latest")
    .port(80)
    .add_config(config)
    .add_secret(secret))
```

## 🔧 Extensibility

### Plugin System

Celestra supports custom plugins:

```python
from celestra import Plugin

# Custom plugin
class CustomPlugin(Plugin):
    def apply(self, app):
        # Custom logic
        app.add_annotation("custom/plugin", "enabled")
        return app

# Use plugin
app = App("my-app").image("nginx:latest").port(80)
app.add_plugin(CustomPlugin())
```

### Custom Resources

```python
from celestra import CustomResource

# Custom resource
custom_crd = CustomResource("MyCustomResource")
custom_crd.add_field("spec", {"replicas": 3})
custom_crd.add_field("status", {"ready": True})

# Generate
custom_crd.generate().to_yaml("./k8s/")
```

## 🎯 Best Practices

### 1. **Use Appropriate Components**

```python
# ✅ Good: Use StatefulApp for databases
db = StatefulApp("postgres").storage("20Gi")

# ❌ Bad: Use App for databases
db = App("postgres")  # No persistent storage
```

### 2. **Environment-Specific Configuration**

```python
# Development
dev_app = App("myapp-dev").for_environment("development")
dev_app.resources(cpu="100m", memory="256Mi").replicas(1)

# Production
prod_app = App("myapp").for_environment("production")
prod_app.resources(cpu="500m", memory="1Gi").replicas(5)
```

### 3. **Security First**

```python
# ✅ Good: Use secrets for sensitive data
app = App("secure-app").add_secret(Secret("api-secret").add("key", "secret-value"))

# ❌ Bad: Use ConfigMaps for secrets
app = App("insecure-app").add_config(ConfigMap("api-config").add("key", "secret-value"))
```

### 4. **Resource Management**

```python
# ✅ Good: Set appropriate resources
app = App("myapp").resources(cpu="500m", memory="1Gi", cpu_limit="1000m", memory_limit="2Gi")

# ❌ Bad: No resource limits
app = App("myapp")  # No resource limits
```

### 5. **Use External Configuration**

```python
# ✅ Good: Load from external files
config = ConfigMap("app-config").from_file("config.json", "configs/app.json")
secret = Secret("db-secret").from_file("password", "secrets/password.txt")

# ❌ Bad: Hardcode in code
config = ConfigMap("app-config").add("config", '{"debug": true}')
secret = Secret("db-secret").add("password", "hardcoded-password")
```

## 🚀 Next Steps

Now that you understand the core concepts, explore:

- **[Components Guide](../components/index.md)** - Learn about all available components
- **[Examples](../examples/index.md)** - Real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides
- **[Examples](../examples/index.md)** - Real-world examples

Ready to build something? Check out the [Quick Start Guide](quick-start.md) or jump into the [Components Guide](../components/index.md)! 