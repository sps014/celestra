# Components Overview

Celestra provides a comprehensive set of components for building Kubernetes applications. Each component is designed to be intuitive, powerful, and production-ready.

## Component Categories

### 🏗️ Core Components

The foundational building blocks for your applications:

| Component | Purpose | Use Cases |
|-----------|---------|-----------|
| [**App**](core/app.md) | Stateless applications | Web services, APIs, microservices |
| [**StatefulApp**](core/stateful-app.md) | Stateful applications | Databases, message queues, storage |
| [**AppGroup**](core/app-group.md) | Application grouping | Microservices, related services |

### ⚙️ Workloads

Specialized workload types for different execution patterns:

| Component | Purpose | Use Cases |
|-----------|---------|-----------|
| [**Job**](workloads/job.md) | One-time tasks | Data migrations, batch processing |
| [**CronJob**](workloads/cron-job.md) | Scheduled tasks | Backups, periodic cleanup |
| [**Lifecycle**](workloads/lifecycle.md) | Container lifecycle | Startup/shutdown hooks |

### 🌐 Networking

Network communication and traffic management:

| Component | Purpose | Use Cases |
|-----------|---------|-----------|
| [**Service**](networking/service.md) | Service discovery | Load balancing, service mesh |
| [**Ingress**](networking/ingress.md) | External access | HTTPS termination, routing |
| [**Scaling**](networking/scaling.md) | Auto-scaling | HPA, VPA, scaling policies |
| [**Health**](networking/health.md) | Health monitoring | Probes, health checks |
| [**NetworkPolicy**](networking/network-policy.md) | Network security | Traffic filtering, isolation |

### 🔐 Security

Security, authentication, and access control:

| Component | Purpose | Use Cases |
|-----------|---------|-----------|
| [**RBAC**](security/rbac.md) | Access control | Users, roles, permissions |
| [**Secrets**](security/secrets.md) | Secret management | Passwords, certificates, keys |
| [**SecurityPolicy**](security/security-policy.md) | Security policies | Pod security, compliance |

### 💾 Storage

Data persistence and configuration management:

| Component | Purpose | Use Cases |
|-----------|---------|-----------|
| [**ConfigMap**](storage/config-map.md) | Configuration | App settings, environment config |
| [**Volumes**](storage/volumes.md) | Data persistence | File storage, shared data |

### 🚀 Advanced

Enterprise and advanced features:

| Component | Purpose | Use Cases |
|-----------|---------|-----------|
| [**Observability**](advanced/observability.md) | Monitoring | Metrics, logging, tracing |
| [**DeploymentStrategy**](advanced/deployment-strategy.md) | Deployment patterns | Blue-green, canary, rolling |
| [**DependencyManager**](advanced/dependency-manager.md) | Service dependencies | Startup ordering, health checks |
| [**CostOptimization**](advanced/cost-optimization.md) | Cost management | Resource optimization |
| [**CustomResources**](advanced/custom-resources.md) | Custom CRDs | Operators, custom resources |

## Quick Start Guide

### Basic Application

```python
from src.k8s_gen import App

# Simple web application
app = (App("my-app")
    .image("nginx:latest")
    .port(8080)
    .replicas(3)
    .expose())
```

### Web App with Database

```python
from src.k8s_gen import App, StatefulApp

# Web application
web = (App("web-app")
    .image("myapp:latest")
    .port(8080)
    .env("DB_HOST", "postgres")
    .replicas(2)
    .expose())

# Database
db = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432)
    .env("POSTGRES_DB", "myapp")
    .storage("/var/lib/postgresql/data", "10Gi"))
```

### Complete Microservices Platform

```python
from src.k8s_gen import App, StatefulApp, Service, Ingress, AppGroup

# Create microservices
user_service = App("user-service").image("user:latest").port(8080)
order_service = App("order-service").image("order:latest").port(8080)
payment_service = App("payment-service").image("payment:latest").port(8080)

# Database
database = StatefulApp("postgres").image("postgres:13").storage("10Gi")

# Group them together
platform = (AppGroup("ecommerce")
    .add_service(user_service)
    .add_service(order_service)
    .add_service(payment_service)
    .add_service(database))

# External access
ingress = (Ingress("platform-ingress")
    .host("myapp.com")
    .path("/users", "user-service", 8080)
    .path("/orders", "order-service", 8080)
    .path("/payments", "payment-service", 8080))
```

## Component Features Matrix

| Feature | App | StatefulApp | Job | CronJob | Service | Ingress |
|---------|-----|-------------|-----|---------|---------|---------|
| **Replicas** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Ports** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Environment Variables** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Resource Limits** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Persistent Storage** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ |
| **Health Checks** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Scaling** | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Load Balancing** | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| **SSL/TLS** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Scheduling** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |

## Common Patterns

### Pattern 1: Three-Tier Web Application

```python
# Frontend
frontend = (App("frontend")
    .image("nginx:latest")
    .port(80)
    .replicas(2)
    .expose())

# Backend API
backend = (App("backend")
    .image("api:latest")
    .port(8080)
    .env("DB_HOST", "database")
    .replicas(3))

# Database
database = (StatefulApp("database")
    .image("postgres:13")
    .port(5432)
    .storage("/data", "50Gi"))

# Connect them
Service("backend-service").target(backend)
Service("database-service").target(database)
```

### Pattern 2: Event-Driven Architecture

```python
# Message queue
kafka = (StatefulApp("kafka")
    .image("confluentinc/cp-kafka:latest")
    .port(9092)
    .storage("/data", "20Gi")
    .replicas(3))

# Event producer
producer = (App("producer")
    .image("producer:latest")
    .env("KAFKA_BROKERS", "kafka:9092")
    .replicas(2))

# Event consumer
consumer = (App("consumer")
    .image("consumer:latest")
    .env("KAFKA_BROKERS", "kafka:9092")
    .replicas(5))
```

### Pattern 3: Batch Processing

```python
# Scheduled data processing
data_processor = (CronJob("data-processor")
    .schedule("0 2 * * *")  # Daily at 2 AM
    .image("processor:latest")
    .env("S3_BUCKET", "data-lake")
    .resources(cpu="2", memory="4Gi"))

# One-time migration
migration = (Job("migration")
    .image("migrator:latest")
    .command(["python", "migrate.py"])
    .resources(cpu="1", memory="2Gi"))
```

## Output Formats

All components support multiple output formats:

=== "Kubernetes YAML"

    ```python
    from src.celestra.output import KubernetesOutput
    
    output = KubernetesOutput()
    output.generate(app, "k8s/")
    ```

=== "Helm Charts"

    ```python
    from src.celestra.output import HelmOutput
    
    helm = HelmOutput("my-chart")
    helm.add_resource(app)
    helm.generate("charts/")
    ```

=== "Docker Compose"

    ```python
    from src.celestra.output import DockerComposeOutput
    
    compose = DockerComposeOutput()
    compose.generate(app, "docker-compose.yml")
    ```

=== "Kustomize"

    ```python
    from src.celestra.output import KustomizeOutput
    
    kustomize = KustomizeOutput("base")
    kustomize.add_resource(app)
    kustomize.generate("kustomize/")
    ```

=== "Terraform"

    ```python
    from src.celestra.output import TerraformOutput
    
    terraform = TerraformOutput("infrastructure")
    terraform.add_resource(app)
    terraform.generate("terraform/")
    ```

## Best Practices

!!! tip "Component Design Principles"

    **Single Responsibility**: Each component has a clear, focused purpose
    
    **Composability**: Components work together seamlessly
    
    **Production Ready**: Built-in best practices and security
    
    **Extensibility**: Easy to extend and customize

!!! warning "Common Pitfalls"

    **Over-Engineering**: Start simple, add complexity as needed
    
    **Resource Limits**: Always set appropriate resource limits
    
    **Security**: Enable security features in production
    
    **Monitoring**: Include observability from the start

## Next Steps

<div class="grid cards" markdown>

-   **[Quick Start Tutorial](../getting-started/quick-start.md)**
    
    Build your first application in minutes

-   **[Kafka Deployment](../tutorials/kafka-deployment.md)**
    
    Deploy a production Kafka cluster

-   **[Multi-Environment Setup](../tutorials/multi-environment.md)**
    
    Configure dev/staging/production

-   **[API Reference](../api-reference/index.md)**
    
    Complete API documentation

</div>

---

**Ready to dive deeper?** Explore specific components or check out our [tutorials](../tutorials/index.md) for hands-on examples! 