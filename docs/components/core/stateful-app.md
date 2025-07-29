# StatefulApp Class

The `StatefulApp` class represents stateful applications that require persistent storage and stable network identities. It's designed for databases, message queues, and other stateful workloads that need ordered deployment and stable storage.

## Overview

```python
from celestra import StatefulApp

# Basic usage
db = StatefulApp("postgres").image("postgres:15").port(5432).storage("20Gi")

# Production-ready database
db = (StatefulApp("production-db")
    .image("postgres:15")
    .port(5432)
    .storage("100Gi")
    .replicas(3)
    .resources(cpu="1000m", memory="4Gi")
    .backup_schedule("0 2 * * *"))
```

## Core API Functions

### Container Configuration

#### Image
Set the container image for the application.

```python
db = StatefulApp("postgres").image("postgres:15")
cache = StatefulApp("redis").image("redis:7-alpine")
kafka = StatefulApp("kafka").image("confluentinc/cp-kafka:7.4.0")
```

#### Build
Build container from local Dockerfile instead of using pre-built image.

```python
# Build from current directory
db = StatefulApp("custom-db").build(".", "Dockerfile", VERSION="1.0")

# Build from subdirectory with custom Dockerfile
db = StatefulApp("custom-cache").build("./cache", "Dockerfile.prod", ENV="production")
```

#### From Dockerfile
Use a custom Dockerfile for building the container.

```python
# Use custom Dockerfile
db = StatefulApp("custom-db").from_dockerfile("Dockerfile.prod", ".", ENV="production")

# Multi-stage build
db = StatefulApp("optimized-db").from_dockerfile("Dockerfile.multi", ".", TARGET="production")
```

#### Command
Set the command to run in the container.

```python
db = StatefulApp("postgres").image("postgres:15").command(["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"])
```

#### Arguments
Set the arguments for the container command.

```python
db = StatefulApp("postgres").image("postgres:15").args(["--config-file=/etc/postgresql/postgresql.conf"])
```

### Port Configuration

#### Port
Add a port to the application.

```python
# Basic database port
db = StatefulApp("postgres").port(5432, "postgres")

# Multiple ports
kafka = (StatefulApp("kafka")
    .port(9092, "kafka")
    .port(9093, "kafka-internal")
    .port(9094, "kafka-external"))
```

#### Add Port
Add a port to the application (alias for port()).

```python
# Add multiple ports
kafka = (StatefulApp("kafka")
    .add_port(9092, "kafka")
    .add_port(9093, "kafka-internal")
    .add_port(9094, "kafka-external"))
```

#### Ports
Add multiple ports at once.

```python
# Bulk port configuration
ports_config = [
    {"port": 9092, "name": "kafka"},
    {"port": 9093, "name": "kafka-internal"},
    {"port": 9094, "name": "kafka-external"}
]
kafka = StatefulApp("kafka").ports(ports_config)
```

### Database-Specific Port Methods

#### Postgres Port
```python
db = StatefulApp("postgres").postgres_port(5432)
```

#### MySQL Port
```python
db = StatefulApp("mysql").mysql_port(3306)
```

#### MongoDB Port
```python
db = StatefulApp("mongodb").mongodb_port(27017)
```

#### Redis Port
```python
cache = StatefulApp("redis").redis_port(6379)
```

#### Kafka Port
```python
kafka = StatefulApp("kafka").kafka_port(9092)
```

#### Elasticsearch Port
```python
es = StatefulApp("elasticsearch").elasticsearch_port(9200)
```

### Storage Configuration

#### Storage
Configure persistent storage for the application.

```python
# Basic storage
db = StatefulApp("postgres").storage("20Gi")

# With mount path
db = StatefulApp("postgres").storage("20Gi", "/var/lib/postgresql/data")

# With storage class
db = StatefulApp("postgres").storage("20Gi", "/var/lib/postgresql/data", "fast-ssd")
```

#### Add Volume
Add a custom volume to the application.

```python
from celestra import Volume

# Add additional volume
config_volume = Volume("config-volume").config_map("db-config")
db = StatefulApp("postgres").add_volume(config_volume)
```

#### Add Volumes
Add multiple volumes to the application.

```python
from celestra import Volume

# Multiple volumes
volumes = [
    Volume("data-volume").persistent_volume_claim("20Gi"),
    Volume("config-volume").config_map("db-config"),
    Volume("backup-volume").persistent_volume_claim("50Gi")
]
db = StatefulApp("postgres").add_volumes(volumes)
```

#### Mount Path
Set the mount path for the primary storage volume.

```python
db = StatefulApp("postgres").storage("20Gi").mount_path("/var/lib/postgresql/data")
```

#### Storage Class
Set the storage class for persistent volumes.

```python
db = StatefulApp("postgres").storage("20Gi").storage_class("fast-ssd")
```

### Environment Configuration

#### Environment
Set multiple environment variables at once.

```python
# Database environment variables
db_env = {
    "POSTGRES_DB": "myapp",
    "POSTGRES_USER": "admin",
    "POSTGRES_PASSWORD": "password",
    "POSTGRES_INITDB_ARGS": "--encoding=UTF-8"
}
db = StatefulApp("postgres").environment(db_env)
```

#### Environment Variable
Add a single environment variable.

```python
# Single environment variable
db = StatefulApp("postgres").env("POSTGRES_DB", "myapp")

# Multiple individual variables
db = (StatefulApp("postgres")
    .env("POSTGRES_DB", "myapp")
    .env("POSTGRES_USER", "admin")
    .env("POSTGRES_PASSWORD", "password"))
```

#### Environment from Secret
Load environment variables from a Secret.

```python
db = StatefulApp("postgres").env_from_secret("db-secret")
```

#### Environment from ConfigMap
Load environment variables from a ConfigMap.

```python
db = StatefulApp("postgres").env_from_config_map("db-config")
```

### Resource Management

#### Resources
Set resource requests and limits for the application.

```python
# Basic resources
db = StatefulApp("postgres").resources(cpu="500m", memory="1Gi")

# With limits
db = (StatefulApp("postgres")
    .resources(
        cpu="1000m", 
        memory="4Gi",
        cpu_limit="2000m",
        memory_limit="8Gi"
    ))

# High-performance database
db = StatefulApp("postgres").resources(cpu="4000m", memory="16Gi", cpu_limit="8000m", memory_limit="32Gi")
```

#### Replicas
Set the number of replicas for the application.

```python
# Single instance
db = StatefulApp("postgres").replicas(1)

# High availability
db = StatefulApp("postgres").replicas(3)

# Read replicas
db = StatefulApp("postgres").replicas(5)
```

### Database-Specific Configuration

#### Postgres Config
Configure PostgreSQL-specific settings.

```python
postgres_config = {
    "max_connections": "200",
    "shared_buffers": "256MB",
    "effective_cache_size": "1GB",
    "maintenance_work_mem": "64MB"
}
db = StatefulApp("postgres").postgres_config(postgres_config)
```

#### MySQL Config
Configure MySQL-specific settings.

```python
mysql_config = {
    "innodb_buffer_pool_size": "1G",
    "max_connections": "200",
    "query_cache_size": "64M"
}
db = StatefulApp("mysql").mysql_config(mysql_config)
```

#### Redis Config
Configure Redis-specific settings.

```python
redis_config = {
    "maxmemory": "2gb",
    "maxmemory-policy": "allkeys-lru",
    "save": "900 1 300 10 60 10000"
}
cache = StatefulApp("redis").redis_config(redis_config)
```

#### Kafka Config
Configure Kafka-specific settings.

```python
kafka_config = {
    "num.partitions": "3",
    "default.replication.factor": "3",
    "min.insync.replicas": "2",
    "offsets.topic.replication.factor": "3"
}
kafka = StatefulApp("kafka").kafka_config(kafka_config)
```

### Backup and Recovery

#### Backup Schedule
Configure automated backup scheduling.

```python
# Daily backup at 2 AM
db = StatefulApp("postgres").backup_schedule("0 2 * * *")

# Weekly backup on Sunday at 3 AM
db = StatefulApp("postgres").backup_schedule("0 3 * * 0")

# Multiple backups per day
db = StatefulApp("postgres").backup_schedule("0 */6 * * *")  # Every 6 hours
```

#### Backup Retention
Set backup retention period.

```python
db = StatefulApp("postgres").backup_retention(30)  # Keep backups for 30 days
```

#### Backup Location
Set backup storage location.

```python
db = StatefulApp("postgres").backup_location("s3://my-backups/postgres")
db = StatefulApp("postgres").backup_location("gcs://my-backups/postgres")
```

#### Enable Point-in-Time Recovery
Enable point-in-time recovery for databases.

```python
db = StatefulApp("postgres").enable_point_in_time_recovery()
```

### Clustering and Replication

#### Cluster Mode
Enable cluster mode for distributed databases.

```python
# Enable clustering
db = StatefulApp("postgres").cluster_mode(True)

# Disable clustering (single instance)
db = StatefulApp("postgres").cluster_mode(False)
```

#### Replication Factor
Set replication factor for distributed systems.

```python
kafka = StatefulApp("kafka").replication_factor(3)
es = StatefulApp("elasticsearch").replication_factor(2)
```

#### Quorum Size
Set quorum size for distributed consensus.

```python
db = StatefulApp("postgres").quorum_size(3)
```

### Health Checks and Monitoring

#### Health Check
Add a health check endpoint.

```python
db = StatefulApp("postgres").health_check("/health")
kafka = StatefulApp("kafka").health_check("/health", port=9092)
```

#### Liveness Probe
Configure liveness probe.

```python
db = StatefulApp("postgres").liveness_probe("/health")
```

#### Readiness Probe
Configure readiness probe.

```python
db = StatefulApp("postgres").readiness_probe("/ready")
```

#### Startup Probe
Configure startup probe.

```python
db = StatefulApp("postgres").startup_probe("/startup")
```

### Security and RBAC

#### Add Service Account
Add a service account to the application.

```python
from celestra import ServiceAccount
sa = ServiceAccount("db-sa")
db = StatefulApp("postgres").add_service_account(sa)
```

#### Add Role
Add a role to the application.

```python
from celestra import Role
role = Role("db-role").add_policy("get", "pods")
db = StatefulApp("postgres").add_role(role)
```

#### Add Network Policy
Add a network policy to the application.

```python
from celestra import NetworkPolicy
policy = NetworkPolicy("db-policy").allow_pods_with_label("app", "api")
db = StatefulApp("postgres").add_network_policy(policy)
```

#### Add Security Policy
Add a security policy to the application.

```python
from celestra import SecurityPolicy
policy = SecurityPolicy("restricted").pod_security_standards("restricted")
db = StatefulApp("postgres").add_security_policy(policy)
```

### Configuration Management

#### Add Secret
Add a secret to the application.

```python
from celestra import Secret
db_secret = Secret("db-secret").add("password", "secure-password")
db = StatefulApp("postgres").add_secret(db_secret)
```

#### Add Secrets
Add multiple secrets to the application.

```python
from celestra import Secret
secrets = [
    Secret("db-secret").add("password", "secure-password"),
    Secret("tls-cert").from_file("cert.pem"),
    Secret("ca-cert").from_file("ca.pem")
]
db = StatefulApp("postgres").add_secrets(secrets)
```

#### Add Config
Add a ConfigMap to the application.

```python
from celestra import ConfigMap
db_config = ConfigMap("db-config").add("max_connections", "200")
db = StatefulApp("postgres").add_config(db_config)
```

#### Add Configs
Add multiple ConfigMaps to the application.

```python
from celestra import ConfigMap
configs = [
    ConfigMap("db-config").add("max_connections", "200"),
    ConfigMap("postgres-config").from_file("postgresql.conf"),
    ConfigMap("pg_hba-config").from_file("pg_hba.conf")
]
db = StatefulApp("postgres").add_configs(configs)
```

### Deployment Strategy

#### Deployment Strategy
Configure deployment strategy.

```python
# Rolling update (default for StatefulSets)
db = StatefulApp("postgres").deployment_strategy("rolling")

# OnDelete strategy
db = StatefulApp("postgres").deployment_strategy("on-delete")
```

#### Rolling Update
Configure rolling update strategy for StatefulSets.

```python
db = StatefulApp("postgres").rolling_update(partition=0)
```

#### On Delete Strategy
Configure on-delete update strategy.

```python
db = StatefulApp("postgres").on_delete_strategy()
```

### Networking and Exposure

#### Expose
Expose the application via Service.

```python
# Internal service only
db = StatefulApp("postgres").expose()

# External service (for development)
db = StatefulApp("postgres").expose(external=True)
```

#### Add Service
Add a custom service configuration.

```python
from celestra import Service
service = Service("postgres-service").type("ClusterIP")
db = StatefulApp("postgres").add_service(service)
```

### Observability

#### Add Observability
Add observability configuration.

```python
from celestra import Observability
obs = Observability("db-monitoring").enable_metrics().enable_logging()
db = StatefulApp("postgres").add_observability(obs)
```

#### Enable Metrics
Enable metrics collection.

```python
db = StatefulApp("postgres").enable_metrics(port=9090)
```

#### Enable Logging
Enable structured logging.

```python
db = StatefulApp("postgres").enable_logging(log_format="json")
```

### Advanced Configuration

#### Namespace
Set the namespace for the application.

```python
db = StatefulApp("postgres").namespace("databases")
```

#### Add Label
Add a label to the application.

```python
db = StatefulApp("postgres").add_label("environment", "production")
db = StatefulApp("postgres").add_label("tier", "database")
```

#### Add Labels
Add multiple labels to the application.

```python
labels = {
    "environment": "production",
    "tier": "database",
    "team": "data-platform"
}
db = StatefulApp("postgres").add_labels(labels)
```

#### Add Annotation
Add an annotation to the application.

```python
db = StatefulApp("postgres").add_annotation("description", "Primary database")
```

#### Add Annotations
Add multiple annotations to the application.

```python
annotations = {
    "description": "Primary database",
    "owner": "data-team",
    "backup-schedule": "daily"
}
db = StatefulApp("postgres").add_annotations(annotations)
```

#### Node Selector
Set node selector for pod placement.

```python
db = StatefulApp("postgres").node_selector({"node-type": "database"})
```

#### Tolerations
Set tolerations for pod scheduling.

```python
tolerations = [{"key": "dedicated", "operator": "Equal", "value": "database", "effect": "NoSchedule"}]
db = StatefulApp("postgres").tolerations(tolerations)
```

#### Affinity
Set pod affinity rules.

```python
affinity = {
    "podAntiAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [{
            "weight": 100,
            "podAffinityTerm": {
                "labelSelector": {"matchExpressions": [{"key": "app", "operator": "In", "values": ["postgres"]}]},
                "topologyKey": "kubernetes.io/hostname"
            }
        }]
    }
}
db = StatefulApp("postgres").affinity(affinity)
```

### Output Generation

#### Generate Configuration
Generate the application configuration.

```python
# Generate Kubernetes YAML
db.generate().to_yaml("./k8s/")

# Generate Docker Compose
db.generate().to_docker_compose("./docker-compose.yml")

# Generate Helm Chart
db.generate().to_helm_chart("./charts/")

# Generate Kustomize
db.generate().to_kustomize("./kustomize/")
```

## Complete Example

Here's a complete example of a production-ready PostgreSQL database:

```python
from celestra import StatefulApp, Secret, ConfigMap, ServiceAccount, Role, NetworkPolicy

# Create secrets
db_secret = Secret("postgres-secret").add("password", "secure-password")

# Create configuration
db_config = ConfigMap("postgres-config").add("max_connections", "200")

# Create service account and role
sa = ServiceAccount("postgres-sa")
role = Role("postgres-role").add_policy("get", "pods")

# Create network policy
network_policy = NetworkPolicy("postgres-policy").allow_pods_with_label("app", "api")

# Create the database
db = (StatefulApp("postgres")
    .image("postgres:15")
    .postgres_port(5432)
    .storage("100Gi", "/var/lib/postgresql/data", "fast-ssd")
    .replicas(3)
    .resources(cpu="2000m", memory="8Gi", cpu_limit="4000m", memory_limit="16Gi")
    .env("POSTGRES_DB", "myapp")
    .env("POSTGRES_USER", "admin")
    .add_secret(db_secret)
    .add_config(db_config)
    .add_service_account(sa)
    .add_role(role)
    .add_network_policy(network_policy)
    .backup_schedule("0 2 * * *")
    .backup_retention(30)
    .backup_location("s3://my-backups/postgres")
    .health_check("/health")
    .liveness_probe("/health")
    .readiness_probe("/ready")
    .expose())

# Generate manifests
db.generate().to_yaml("./k8s/")
```

## Best Practices

### 1. **Storage Configuration**
```python
# ✅ Good: Use appropriate storage class and size
db = StatefulApp("postgres").storage("100Gi", "/var/lib/postgresql/data", "fast-ssd")

# ❌ Bad: No storage configuration
db = StatefulApp("postgres")  # No persistent storage
```

### 2. **Backup Strategy**
```python
# ✅ Good: Configure automated backups
db = (StatefulApp("postgres")
    .backup_schedule("0 2 * * *")
    .backup_retention(30)
    .backup_location("s3://backups/postgres"))

# ❌ Bad: No backup configuration
db = StatefulApp("postgres")  # No backups
```

### 3. **Resource Allocation**
```python
# ✅ Good: Set appropriate resources for databases
db = StatefulApp("postgres").resources(cpu="2000m", memory="8Gi", cpu_limit="4000m", memory_limit="16Gi")

# ❌ Bad: Insufficient resources
db = StatefulApp("postgres").resources(cpu="100m", memory="256Mi")  # Too small for production
```

### 4. **Security**
```python
# ✅ Good: Use secrets and RBAC
secret = Secret("db-secret").add("password", "secure-password")
sa = ServiceAccount("db-sa")
role = Role("db-role").add_policy("get", "pods")
db = StatefulApp("postgres").add_secret(secret).add_service_account(sa).add_role(role)

# ❌ Bad: No security configuration
db = StatefulApp("postgres")  # No security
```

### 5. **High Availability**
```python
# ✅ Good: Multiple replicas with proper configuration
db = (StatefulApp("postgres")
    .replicas(3)
    .cluster_mode(True)
    .quorum_size(3))

# ❌ Bad: Single instance
db = StatefulApp("postgres").replicas(1)  # No high availability
```

## Related Components

- **[App](app.md)** - For stateless applications
- **[Job](../workloads/job.md)** - For batch processing workloads
- **[CronJob](../workloads/cron-job.md)** - For scheduled batch jobs
- **[Secret](../security/secrets.md)** - For managing sensitive data
- **[ConfigMap](../storage/config-map.md)** - For managing configuration data
- **[ServiceAccount](../security/service-account.md)** - For RBAC identity
- **[Role](../security/role.md)** - For access control policies

## Next Steps

- **[App](app.md)** - Learn about stateless applications
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 