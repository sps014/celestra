# Core Concepts

Understanding the fundamental concepts of K8s-Gen DSL will help you build cloud-native applications effectively. This guide covers the core principles and components that make up the DSL.

## DSL Philosophy

K8s-Gen DSL is built on three core principles:

### 🎯 **Simplicity First**
Write infrastructure as code using intuitive Python syntax that's easy to read and maintain.

### 🏗️ **Builder Pattern**
Use method chaining to configure components step-by-step, making the code self-documenting.

### 📦 **Multiple Outputs**
Generate various deployment formats (Kubernetes, Helm, Docker Compose, etc.) from the same codebase.

## Core Components

### Applications

#### App - Stateless Applications
The `App` class represents stateless applications that can be horizontally scaled without data persistence concerns.

```python
from k8s_gen import App

web_app = (App("web-server")
    .image("nginx:1.21")
    .port(8080, "http")
    .replicas(3)
    .resources(cpu="500m", memory="512Mi"))
```

**Key characteristics:**
- No persistent storage
- Can be scaled horizontally
- Suitable for web servers, APIs, microservices

#### StatefulApp - Stateful Applications
The `StatefulApp` class represents applications that require persistent storage and stable network identities.

```python
from k8s_gen import StatefulApp

database = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432, "database")
    .storage("/var/lib/postgresql/data", "10Gi")
    .env("POSTGRES_DB", "myapp"))
```

**Key characteristics:**
- Persistent storage with volumes
- Stable network identities
- Ordered deployment and scaling
- Suitable for databases, message queues

### Workloads

#### Job - One-time Tasks
Execute batch processing tasks that run to completion.

```python
from k8s_gen import Job

data_job = (Job("data-migration")
    .image("migrator:1.0")
    .command(["python", "migrate.py"])
    .resources(cpu="1", memory="2Gi"))
```

#### CronJob - Scheduled Tasks
Run jobs on a schedule using cron syntax.

```python
from k8s_gen import CronJob

backup_job = (CronJob("daily-backup")
    .schedule("0 2 * * *")  # Daily at 2 AM
    .image("backup-tool:1.0")
    .command(["backup.sh"]))
```

### Networking

#### Service - Service Discovery
Expose applications within the cluster or externally.

```python
from k8s_gen import Service

service = (Service("web-service")
    .selector({"app": "web-server"})
    .add_port("http", 80, 8080)
    .type("LoadBalancer"))
```

#### Ingress - External Access
Configure external HTTP/HTTPS access to services.

```python
from k8s_gen import Ingress

ingress = (Ingress("web-ingress")
    .host("myapp.example.com")
    .route("/", "web-service", 80)
    .tls("myapp-tls"))
```

### Security

#### RBAC - Role-Based Access Control
Configure fine-grained permissions for applications.

```python
from k8s_gen import ServiceAccount, Role, RoleBinding

service_account = ServiceAccount("app-sa")
role = (Role("app-role")
    .allow_get("configmaps", "secrets")
    .allow_list("services"))
binding = RoleBinding("app-binding", role, service_account)
```

#### Secrets - Sensitive Data
Manage sensitive information like passwords and API keys.

```python
from k8s_gen import Secret

secret = (Secret("app-secrets")
    .add_data("database_url", "postgres://...")
    .add_data("api_key", "secret-key"))
```

### Storage

#### ConfigMap - Configuration Data
Store non-sensitive configuration data.

```python
from k8s_gen import ConfigMap

config = (ConfigMap("app-config")
    .add_data("app.properties", "debug=false\nport=8080")
    .add_data("database.conf", "host=localhost"))
```

## Builder Pattern

K8s-Gen uses the builder pattern extensively, allowing you to chain methods to configure components:

```python
app = (App("my-app")                    # Start with component name
    .image("my-app:1.0")                # Set container image
    .port(8080, "http")                 # Add a port
    .port(9090, "metrics")              # Add another port
    .env("LOG_LEVEL", "info")           # Set environment variable
    .resources(cpu="500m", memory="1Gi") # Set resource requests
    .replicas(3)                        # Set replica count
    .health_check("/health", 8080)      # Add health check
    .expose())                          # Create service
```

### Method Chaining Benefits

1. **Readable**: Code reads like natural language
2. **Flexible**: Add or remove configuration as needed
3. **Type-safe**: Methods are strongly typed
4. **Self-documenting**: Method names explain their purpose

## Configuration Patterns

### Environment Variables
Set environment variables for application configuration:

```python
app = (App("config-demo")
    .image("app:1.0")
    .env("DATABASE_URL", "postgres://db:5432/app")
    .env("REDIS_URL", "redis://cache:6379")
    .env("LOG_LEVEL", "info"))
```

### Resource Management
Define CPU and memory requirements:

```python
app = (App("resource-demo")
    .image("app:1.0")
    .resources(
        cpu="500m",           # 0.5 CPU cores
        memory="1Gi",         # 1 GB memory
        cpu_limit="1",        # Max 1 CPU core
        memory_limit="2Gi"    # Max 2 GB memory
    ))
```

### Port Configuration
Configure multiple ports for different purposes:

```python
app = (App("multi-port-app")
    .image("app:1.0")
    .http_port(8080, "api")           # HTTP API
    .https_port(8443, "secure-api")   # HTTPS API
    .metrics_port(9090, "prometheus") # Metrics endpoint
    .health_port(8081, "health"))     # Health check endpoint
```

## Output Generation

### Kubernetes YAML
Generate standard Kubernetes manifests:

```python
from k8s_gen import KubernetesOutput

# Generate resources
resources = app.generate_kubernetes_resources()

# Save to files
output = KubernetesOutput()
output.generate(app, "manifests/")
```

### Multiple Formats
Generate different deployment formats:

```python
from k8s_gen import HelmOutput, DockerComposeOutput

# Helm chart
helm = HelmOutput("my-app-chart")
helm.add_resource(app).generate("helm/")

# Docker Compose
compose = DockerComposeOutput()
compose.generate(app, "docker-compose.yml")
```

## Advanced Features

### Observability
Add monitoring and tracing capabilities:

```python
from k8s_gen import Observability

observability = (Observability("monitoring")
    .enable_metrics()
    .enable_tracing()
    .enable_logging())

app.add_observability(observability)
```

### Dependency Management
Define dependencies between components:

```python
from k8s_gen import DependencyManager

deps = (DependencyManager()
    .add_dependency(web_app, database)
    .add_dependency(web_app, cache))
```

### Cost Optimization
Optimize resource usage and costs:

```python
from k8s_gen import CostOptimization

optimizer = (CostOptimization("cost-optimizer")
    .resource_optimization()
    .enable_vertical_scaling()
    .enable_spot_instances())
```

## Best Practices

### 🏷️ **Naming Conventions**
- Use lowercase with hyphens: `web-server`, `user-service`
- Be descriptive: `postgres-database` instead of `db`
- Include environment if needed: `web-server-prod`

### 📊 **Resource Planning**
- Set resource requests for scheduling
- Set resource limits to prevent resource hogging
- Monitor actual usage and adjust accordingly

### 🔒 **Security**
- Use RBAC with least privilege principle
- Store sensitive data in Secrets, not ConfigMaps
- Enable security policies and scanning

### 📈 **Scalability**
- Design stateless applications when possible
- Use horizontal scaling for stateless apps
- Plan storage requirements for stateful apps

### 🧪 **Testing**
- Test configurations with validation tools
- Use examples and demos to verify functionality
- Validate generated manifests before deployment

## Next Steps

Now that you understand the core concepts:

1. **[First App](first-app.md)** - Build your first complete application
2. **[Quick Start](quick-start.md)** - Get hands-on experience
3. **[Examples](../examples/index.md)** - Explore real-world patterns
4. **[Tutorials](../tutorials/index.md)** - Follow detailed guides

---

**Ready to build?** Move on to creating your [first application](first-app.md) or jump into the [quick start guide](quick-start.md)!
