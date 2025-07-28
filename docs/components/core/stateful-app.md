# StatefulApp Component

The `StatefulApp` component is designed for stateful applications that require persistent storage, stable network identities, and ordered deployment. It generates Kubernetes StatefulSets and associated resources.

## Overview

Use `StatefulApp` for:
- **Databases** - PostgreSQL, MySQL, MongoDB
- **Message Queues** - Kafka, RabbitMQ, NATS
- **Data Stores** - Elasticsearch, Redis clusters
- **Stateful Services** - Any app requiring persistent identity

## Basic Usage

```python
from src.k8s_gen import StatefulApp

# Simple database
database = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432, "postgres")
    .env("POSTGRES_DB", "myapp")
    .storage("/var/lib/postgresql/data", "20Gi"))
```

## Key Differences from App

| Feature | App (Deployment) | StatefulApp (StatefulSet) |
|---------|------------------|---------------------------|
| **Pod Identity** | Random names | Stable, predictable names |
| **Storage** | Ephemeral by default | Persistent by design |
| **Network** | Service-based | Stable hostname per pod |
| **Scaling** | Parallel | Ordered (one at a time) |
| **Updates** | Rolling update | Ordered update |

## Configuration Methods

### Basic Setup

```python
db = (StatefulApp("mongodb")
    .image("mongo:5.0")
    .port(27017, "mongodb")
    .replicas(3)                    # Creates 3 pods: mongodb-0, mongodb-1, mongodb-2
    .service_name("mongodb"))       # Headless service name
```

### Persistent Storage

```python
# Single volume
db = (StatefulApp("mysql")
    .storage("/var/lib/mysql", "50Gi")
    .storage_class("fast-ssd"))

# Multiple volumes
app = (StatefulApp("elasticsearch")
    .storage("/usr/share/elasticsearch/data", "100Gi", "es-data")
    .storage("/usr/share/elasticsearch/logs", "10Gi", "es-logs")
    .storage_class("fast-ssd"))
```

### Database-Specific Helpers

```python
# PostgreSQL
postgres = (StatefulApp("postgres")
    .postgres_port(5432, "database")
    .postgres_config(
        database="myapp",
        user="app_user", 
        password_secret="postgres-secret"
    ))

# MySQL
mysql = (StatefulApp("mysql")
    .mysql_port(3306, "database")
    .mysql_config(
        database="wordpress",
        user="wp_user",
        password_secret="mysql-secret"
    ))

# MongoDB
mongo = (StatefulApp("mongodb")
    .mongo_port(27017, "mongodb")
    .mongo_config(
        database="app_db",
        auth_secret="mongo-secret"
    ))
```

### Clustering and Replication

```python
# Redis cluster
redis = (StatefulApp("redis")
    .image("redis:7-alpine")
    .port(6379, "redis")
    .port(16379, "cluster")
    .replicas(6)                    # 3 masters + 3 replicas
    .cluster_mode(True)
    .storage("/data", "5Gi"))

# Kafka cluster
kafka = (StatefulApp("kafka")
    .image("confluentinc/cp-kafka:7.4.0")
    .port(9092, "kafka")
    .port(9093, "external")
    .replicas(3)
    .env("KAFKA_ZOOKEEPER_CONNECT", "zookeeper:2181")
    .env("KAFKA_ADVERTISED_LISTENERS", "PLAINTEXT://kafka:9092")
    .storage("/var/lib/kafka/data", "100Gi"))
```

## Advanced Configuration

### Network Identity

```python
# Each pod gets: cassandra-0.cassandra.default.svc.cluster.local
cassandra = (StatefulApp("cassandra")
    .image("cassandra:3.11")
    .port(9042, "cql")
    .port(7000, "internode")
    .replicas(3)
    .service_name("cassandra")     # Controls DNS names
    .pod_management_policy("Parallel"))  # Allow parallel startup
```

### Initialization and Lifecycle

```python
db = (StatefulApp("postgres")
    .image("postgres:13")
    .init_container("init-db", "postgres:13")
    .init_command(["sh", "-c", "createdb myapp"])
    .post_start_exec(["pg_isready"])
    .pre_stop_exec(["pg_ctl", "stop", "-m", "fast"]))
```

### Backup and Recovery

```python
database = (StatefulApp("postgres")
    .image("postgres:13")
    .storage("/var/lib/postgresql/data", "100Gi")
    .backup_schedule("0 2 * * *")        # Daily at 2 AM
    .backup_retention(30)                # Keep 30 days
    .backup_storage("backup-bucket"))
```

## Complete Example - PostgreSQL Cluster

```python
#!/usr/bin/env python3
"""
Production PostgreSQL Cluster with High Availability
"""

from src.k8s_gen import StatefulApp, Secret, ConfigMap, Service, KubernetesOutput

def create_postgres_cluster():
    # Configuration
    postgres_config = ConfigMap("postgres-config")
    postgres_config.add_data("postgresql.conf", """
# PostgreSQL Configuration
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
""")
    
    postgres_config.add_data("pg_hba.conf", """
# PostgreSQL HBA Configuration
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    replication     postgres        0.0.0.0/0               md5
host    all             all             0.0.0.0/0               md5
""")
    
    # Secrets
    postgres_secret = Secret("postgres-secret")
    postgres_secret.add_data("username", "postgres")
    postgres_secret.add_data("password", "supersecret123")
    postgres_secret.add_data("replication-password", "replicationsecret")
    
    # PostgreSQL StatefulSet
    postgres = (StatefulApp("postgres")
        .image("postgres:15.2")
        .replicas(3)
        
        # Networking
        .postgres_port(5432, "database")
        .port(5433, "replication")
        
        # Environment
        .env("POSTGRES_DB", "myapp")
        .env("POSTGRES_USER", "postgres")
        .env_from_secret("postgres-secret", "POSTGRES_PASSWORD", "password")
        .env_from_secret("postgres-secret", "POSTGRES_REPLICATION_PASSWORD", "replication-password")
        .env("PGDATA", "/var/lib/postgresql/data/pgdata")
        
        # Storage
        .storage("/var/lib/postgresql/data", "100Gi")
        .storage_class("fast-ssd")
        
        # Configuration volumes
        .config_volume("/etc/postgresql", "postgres-config")
        
        # Resources
        .resources(
            cpu="2000m",
            memory="4Gi",
            cpu_limit="4000m", 
            memory_limit="8Gi"
        )
        
        # Health checks
        .liveness_probe("/", port=5432, initial_delay=60)
        .readiness_probe("/", port=5432, initial_delay=30)
        
        # Lifecycle
        .post_start_exec([
            "sh", "-c", 
            "until pg_isready -h localhost -p 5432; do sleep 1; done"
        ])
        .pre_stop_exec([
            "sh", "-c",
            "pg_ctl stop -D /var/lib/postgresql/data/pgdata -m fast"
        ])
        
        # Metadata
        .label("app", "postgres")
        .label("component", "database")
        .annotation("backup.io/enabled", "true")
        .annotation("monitoring.io/scrape", "true")
        
        # Security
        .service_account("postgres-sa"))
    
    # Headless service for StatefulSet
    postgres_headless = (Service("postgres-headless")
        .cluster_ip("None")  # Headless service
        .selector({"app": "postgres"})
        .add_port("database", 5432, 5432))
    
    # Load balancer service for read replicas
    postgres_read = (Service("postgres-read")
        .type("ClusterIP")
        .selector({"app": "postgres"})
        .add_port("database", 5432, 5432))
    
    return postgres_config, postgres_secret, postgres, postgres_headless, postgres_read

if __name__ == "__main__":
    components = create_postgres_cluster()
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "postgres-cluster/")
    
    print("✅ PostgreSQL cluster generated!")
    print("🚀 Deploy: kubectl apply -f postgres-cluster/")
    print("🔗 Connect: postgres-0.postgres-headless:5432")
```

## Kafka Cluster Example

```python
def create_kafka_cluster():
    # ZooKeeper (required for Kafka)
    zookeeper = (StatefulApp("zookeeper")
        .image("confluentinc/cp-zookeeper:7.4.0")
        .port(2181, "client")
        .port(2888, "follower")
        .port(3888, "election")
        .replicas(3)
        .env("ZOOKEEPER_CLIENT_PORT", "2181")
        .env("ZOOKEEPER_SERVERS", 
             "zookeeper-0.zookeeper:2888:3888;zookeeper-1.zookeeper:2888:3888;zookeeper-2.zookeeper:2888:3888")
        .storage("/var/lib/zookeeper/data", "10Gi")
        .storage("/var/lib/zookeeper/log", "5Gi", mount_path="/var/lib/zookeeper/log"))
    
    # Kafka brokers
    kafka = (StatefulApp("kafka")
        .image("confluentinc/cp-kafka:7.4.0")
        .port(9092, "kafka")
        .port(9101, "jmx")
        .replicas(3)
        .env("KAFKA_ZOOKEEPER_CONNECT", "zookeeper:2181")
        .env("KAFKA_ADVERTISED_LISTENERS", "PLAINTEXT://kafka:9092")
        .env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "3")
        .env("KAFKA_DEFAULT_REPLICATION_FACTOR", "3")
        .env("KAFKA_MIN_INSYNC_REPLICAS", "2")
        .storage("/var/lib/kafka/data", "100Gi")
        .resources(cpu="1000m", memory="2Gi"))
    
    return zookeeper, kafka
```

## Generated Resources

### StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-headless
  replicas: 3
  selector:
    matchLabels:
      app: postgres
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:15.2
        ports:
        - containerPort: 5432
          name: database
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
```

### Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-headless
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
    name: database
```

## Best Practices

!!! tip "StatefulSet Guidelines"
    
    **Storage:**
    - Use high-performance storage classes (SSD)
    - Plan storage capacity carefully (hard to resize)
    - Consider backup and disaster recovery
    
    **Networking:**
    - Use headless services for pod-to-pod communication
    - Create regular services for client access
    - Plan for both internal and external connectivity
    
    **Scaling:**
    - Scale StatefulSets carefully (ordered operation)
    - Test scaling procedures in staging
    - Monitor resource usage during scaling
    
    **Updates:**
    - Use rolling updates with appropriate strategy
    - Test update procedures thoroughly
    - Plan for rollback scenarios

## Common Use Cases

### Database Patterns

```python
# Primary-replica setup
primary = StatefulApp("postgres-primary").replicas(1).env("ROLE", "primary")
replica = StatefulApp("postgres-replica").replicas(2).env("ROLE", "replica")

# Sharded database
for shard in range(3):
    shard_db = StatefulApp(f"postgres-shard-{shard}").env("SHARD_ID", str(shard))
```

### Message Queue Patterns

```python
# Kafka with external access
kafka = (StatefulApp("kafka")
    .port(9092, "internal")
    .port(9093, "external")
    .env("KAFKA_LISTENERS", "INTERNAL://0.0.0.0:9092,EXTERNAL://0.0.0.0:9093"))
```

## Troubleshooting

### Common Issues

!!! warning "StatefulSet Problems"
    
    **Pods Stuck in Pending:**
    - Check PVC creation and storage availability
    - Verify storage class exists and is default
    - Check node capacity and resource requests
    
    **Pods Not Starting in Order:**
    - Verify readiness probes are configured
    - Check for resource constraints
    - Review StatefulSet events
    
    **Storage Issues:**
    - PVCs not binding to PVs
    - Storage class misconfiguration
    - Insufficient storage capacity

## API Reference

::: src.celestra.core.stateful_app.StatefulApp
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[App](app.md)** - For stateless applications
- **[Service](../networking/service.md)** - Network services
- **[ConfigMap](../storage/config-map.md)** - Configuration
- **[Secret](../security/secrets.md)** - Secrets management

---

**Next:** Learn about [AppGroup](app-group.md) for managing multiple services together. 