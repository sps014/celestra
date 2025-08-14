# Components

Celestra provides a comprehensive set of components for building Kubernetes applications. Each component is designed with a fluent API for easy configuration and deployment.

## Core Components

### [App](core/app.md)
Stateless applications that can be horizontally scaled without persistent storage concerns.

```python
from celestra import App

app = (App("web-app")
    .image("nginx:latest")
    .port(8080)
    .replicas(3)
    .resources(cpu="500m", memory="1Gi")
    .expose())
```

**Key Features:**
- Horizontal scaling
- Rolling updates
- Load balancing
- Multiple port support
- Environment configuration
- Resource management

### [StatefulApp](core/stateful-app.md)
Stateful applications that require persistent storage and stable network identities.

```python
from celestra import StatefulApp

db = (StatefulApp("postgres")
    .image("postgres:14")
    .port(5432)
    .storage("10Gi")
    .replicas(3)
    .backup_schedule("0 2 * * *"))
```

**Key Features:**
- Persistent storage
- Stable network identities
- Ordered deployment
- Database-specific port helpers
- Backup scheduling
- Cluster mode support

## Security Components

### [Secret](security/secrets.md)
Manage sensitive data like passwords, API keys, and certificates.

```python
from celestra import Secret

secret = (Secret("db-secret")
    .add("username", "admin")
    .add("password", "secure-password")
    .mount_as_env_vars(prefix="DB_"))
```

**Key Features:**
- Multiple data sources (files, environment, Vault, cloud)
- Automatic secret generation
- Binary data support
- Environment variable mounting
- Cloud integration (AWS, GCP, Azure)

## Storage Components

### [ConfigMap](storage/config-map.md)
Manage configuration data and application settings.

```python
from celestra import ConfigMap

config = (ConfigMap("app-config")
    .add("debug", "false")
    .add_json("features", {"new_ui": True})
    .from_file("nginx.conf", "configs/nginx.conf")
    .mount_as_env_vars(prefix="APP_"))
```

**Key Features:**
- Multiple format support (JSON, YAML, Properties, INI, TOML)
- File and directory loading
- Template rendering
- Hot reload support
- Environment variable mounting

## Workload Components

### [Job](workloads/job.md)
Batch processing workloads that run to completion.

```python
from celestra import Job

job = (Job("data-migration")
    .image("migrator:latest")
    .command(["python", "migrate.py"])
    .resources(cpu="1000m", memory="2Gi")
    .timeout("2h")
    .retry_limit(3))
```

**Key Features:**
- Parallel execution
- Completion tracking
- Retry policies
- Timeout management
- Resource allocation
- Volume mounting

## Usage Patterns

### Web Application Stack

```python
from celestra import App, StatefulApp, Secret, ConfigMap

# Database
db = (StatefulApp("postgres")
    .image("postgres:14")
    .port(5432)
    .storage("10Gi")
    .add_secret(Secret("db-secret").add("password", "secret123")))

# Web Application
web = (App("web-app")
    .image("webapp:latest")
    .port(8080)
    .replicas(3)
    .add_secret(Secret("api-secret").add("api_key", "sk_live_..."))
    .add_config(ConfigMap("app-config").add("debug", "false"))
    .expose())
```

### Microservices Architecture

```python
from celestra import App, StatefulApp, Secret, ConfigMap

# Message Queue
kafka = (StatefulApp("kafka")
    .image("confluentinc/cp-kafka:7.4.0")
    .kafka_port(9092)
    .storage("100Gi")
    .replicas(3))

# API Service
api = (App("api-service")
    .image("api:v1.0")
    .port(8080)
    .replicas(5)
    .add_secret(Secret("api-secret").add("jwt_secret", "jwt-key"))
    .add_config(ConfigMap("api-config").add_json("endpoints", {"users": "/api/users"})))

# Worker Service
worker = (App("worker-service")
    .image("worker:v1.0")
    .port(8080)
    .replicas(3)
    .add_secret(Secret("worker-secret").add("queue_password", "queue-pass")))
```

### Data Processing Pipeline

```python
from celestra import Job, StatefulApp, ConfigMap

# Data Storage
storage = (StatefulApp("elasticsearch")
    .image("elasticsearch:8.8.0")
    .elasticsearch_port(9200)
    .storage("200Gi")
    .replicas(3))

# Data Processing Job
processor = (Job("data-processor")
    .image("processor:v1.0")
    .command(["python", "process.py"])
    .resources(cpu="2000m", memory="4Gi")
    .parallelism(5)
    .timeout("6h")
    .add_config(ConfigMap("processor-config").add("batch_size", "1000")))
```

## Best Practices

### 1. Use External Configuration

```python
# ✅ Good: Load from external files
config = ConfigMap("app-config").from_file("config.json", "configs/app.json")
secret = Secret("db-secret").from_file("password", "secrets/password.txt")

# ❌ Bad: Hardcode in code
config = ConfigMap("app-config").add("config", '{"debug": true}')
secret = Secret("db-secret").add("password", "hardcoded-password")
```

### 2. Environment-Specific Configuration

```python
# Development
dev_app = App("myapp-dev").for_environment("development")
dev_app.resources(cpu="100m", memory="256Mi").replicas(1)

# Production
prod_app = App("myapp").for_environment("production")
prod_app.resources(cpu="500m", memory="1Gi").replicas(5)
```

### 3. Security First

```python
# ✅ Good: Use secrets for sensitive data
app = App("secure-app").add_secret(Secret("api-secret").add("key", "secret-value"))

# ❌ Bad: Use ConfigMaps for secrets
app = App("insecure-app").add_config(ConfigMap("api-config").add("key", "secret-value"))
```

### 4. Resource Management

```python
# ✅ Good: Set appropriate resources
app = App("myapp").resources(cpu="500m", memory="1Gi", cpu_limit="1000m", memory_limit="2Gi")

# ❌ Bad: No resource limits
app = App("myapp")  # No resource limits
```

### 5. Use Appropriate Components

```python
# ✅ Good: Use StatefulApp for databases
db = StatefulApp("postgres").storage("10Gi")

# ❌ Bad: Use App for databases
db = App("postgres")  # No persistent storage
```

## Output & Execution

### [Output Execution](output-execution.md)
Execute generated configurations directly with Docker Compose and Kubernetes commands.

```python
from celestra import App, DockerComposeOutput, KubernetesOutput

# Docker Compose execution
docker_output = DockerComposeOutput()
docker_output.generate(app, "compose.yml").up(detached=True).logs()

# Kubernetes execution
k8s_output = KubernetesOutput()
k8s_output.generate(app, "./manifests/").apply(wait=True).health()
```

**Key Features:**
- Direct execution of generated configurations
- Method chaining for fluent workflows
- Automatic file tracking
- Comprehensive error handling
- CI/CD pipeline integration

## Next Steps

- **Explore [App](core/app.md)** - Learn about stateless applications
- **Check [StatefulApp](core/stateful-app.md)** - Understand stateful applications
- **Review [Secret](security/secrets.md)** - Manage sensitive data
- **Study [ConfigMap](storage/config-map.md)** - Handle configuration
- **Examine [Job](workloads/job.md)** - Create batch processing workloads
- **Try [Output Execution](output-execution.md)** - Execute configurations directly

## Getting Help

- **Documentation**: Browse the [complete documentation](../index.md)
- **Examples**: Check out [example applications](../examples/index.md)
- **Issues**: Report problems on [GitHub Issues](https://github.com/sps014/Celestra/issues) 