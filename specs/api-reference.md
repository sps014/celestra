# API Reference

Complete reference for the K8s-Gen DSL API with examples and usage patterns.

## Core Components

### App (Stateless Applications)

The `App` class represents stateless applications that don't require persistent storage.

```python
from k8s_gen import App

app = (App("my-web-app")
    .image("web-server:latest")
    .port(8080)
    .environment({
        "ENV": "production",
        "DB_HOST": "database.default.svc.cluster.local"
    })
    .resources(
        cpu="500m",
        memory="512Mi",
        cpu_limit="1000m",
        memory_limit="1Gi"
    ))
```

#### App Methods

| Method | Description | Example |
|--------|-------------|---------|
| `.image(name)` | Set container image | `.image("web-server:latest")` |
| `.port(number)` | Expose port | `.port(8080)` |
| `.environment(dict)` | Set environment variables | `.environment({"DEBUG": "true"})` |
| `.resources(...)` | Set CPU/memory limits | `.resources(cpu="500m", memory="1Gi")` |
| `.replicas(count)` | Set replica count | `.replicas(3)` |
| `.expose(...)` | Expose service externally | `.expose(external_access=True)` |

### StatefulApp (Stateful Applications)

The `StatefulApp` class represents applications requiring persistent state like databases.

```python
from k8s_gen import StatefulApp

# Database server
database = (StatefulApp("database")
    .image("database-server:latest")
    .port(5432)
    .storage("20Gi")
    .replicas(1)
    .environment({
        "DB_NAME": "myapp",
        "DB_USER": "admin"
    })
    .backup_schedule("0 2 * * *")  # Daily at 2 AM
)

# Message queue
message_queue = (StatefulApp("message-queue")
    .image("message-broker:latest")
    .port(9092)
    .storage("50Gi")
    .replicas(3)
    .environment({
        "REPLICATION_FACTOR": "2",
        "NUM_PARTITIONS": "3"
    })
    .topics(["user-events", "order-events"])
    .retention_hours(168)  # 7 days
)

# Cache cluster
cache = (StatefulApp("cache")
    .image("cache-server:latest")
    .port(6379)
    .storage("10Gi")
    .replicas(3)
    .cluster_mode()
    .persistence(save_interval="60 1000"))

# Connect app to stateful services
app.connect_to([database, message_queue, cache])
```

### Secrets Management

Secure handling of sensitive data like passwords, API keys, and certificates.

```python
from k8s_gen import Secret

# Database credentials
db_secret = (Secret("database-credentials")
    .add("username", "admin")
    .add("password", "super-secret-password")
    .add("connection-string", "database://admin:password@database:5432/myapp")
    .from_env_file(".env.secrets")
    .mount_path("/etc/secrets")
    .mount_as_env_vars(prefix="DB_"))

# API keys and certificates
api_secret = (Secret("api-keys")
    .add("payment_key", "pk_live_...")
    .add("jwt_secret", "...")
    .add("github_token", "ghp_...")
    .from_file("tls.crt", "./certs/app.crt")
    .from_file("tls.key", "./certs/app.key")
    .type("tls"))  # for TLS secrets

# External secret sources
vault_secret = (Secret("vault-secrets")
    .from_vault("secret/myapp/db", mapping={
        "username": "db_user",
        "password": "db_pass"
    })
    .vault_auth("kubernetes", role="myapp-role"))

cloud_secret = (Secret("cloud-secrets")
    .from_cloud_parameter_store("/myapp/production/")
    .from_cloud_secrets_manager("myapp/api-keys"))

# Generated secrets
generated_secret = (Secret("generated-keys")
    .generate_password("admin_password", length=32)
    .generate_rsa_key_pair("jwt_private_key", "jwt_public_key")
    .generate_random("session_key", length=64))

app.add_secrets([db_secret, api_secret, vault_secret])
```

### ConfigMap Management

Flexible configuration management with multiple data sources and formats.

```python
from k8s_gen import ConfigMap

# Simple key-value configuration
app_config = (ConfigMap("app-config")
    .add("environment", "production")
    .add("log_level", "info")
    .add("max_connections", "100")
    .add("feature_flags", '{"new_ui": true, "beta_features": false}'))

# Configuration from files
file_config = (ConfigMap("file-config")
    .from_file("app.properties", "./config/app.properties")
    .from_file("database.conf", "./config/database.conf")
    .from_directory("./config/", pattern="*.conf"))

# Environment-specific configuration
env_config = (ConfigMap("env-config")
    .from_env_file(".env.production")
    .from_env_file(".env.shared"))

# Structured configuration formats
structured_config = (ConfigMap("structured-config")
    .add_json("app_settings", {
        "server": {"host": "0.0.0.0", "port": 8080},
        "database": {"pool_size": 10, "timeout": 30},
        "cache": {"ttl": 3600, "max_size": "128MB"}
    })
    .add_yaml("logging_config", """
        version: 1
        handlers:
          console:
            class: logging.StreamHandler
            level: INFO
        root:
          level: INFO
          handlers: [console]
    """)
    .add_properties("app_properties", {
        "database_url": "database://localhost:5432/myapp",
        "cache_ttl": "3600",
        "debug_mode": "false"
    }))

# Advanced ConfigMap features
advanced_config = (ConfigMap("advanced-config")
    .from_template("config.j2", variables={
        "environment": "production",
        "replica_count": 3
    })
    .hot_reload(enabled=True, restart_policy="rolling")
    .mount_path("/etc/config")
    .mount_as_env_vars(prefix="APP_")
    .file_permissions(0o644))

app.add_config([app_config, file_config, env_config])
```

## Workload Management

### Jobs and CronJobs

Batch processing and scheduled tasks.

```python
from k8s_gen import Job, CronJob

# Database migration job
migration = (Job("db-migration")
    .image("myapp/migrator:latest")
    .command(["python", "migrate.py"])
    .environment({"DB_URL": "database://user:pass@database:5432/myapp"})
    .depends_on([database])
    .timeout("10m")
    .retention_limit(3))

# Batch processing job
batch_job = (Job("data-processing")
    .image("myapp/processor:latest")
    .command(["python", "process_data.py", "--batch-size=1000"])
    .resources(cpu="2000m", memory="4Gi")
    .parallelism(5)
    .completions(10)
    .timeout("2h"))

# Scheduled backup
backup_job = (CronJob("backup")
    .image("database-tools:latest")
    .schedule("0 2 * * *")  # Daily at 2 AM
    .command(["sh", "-c", "backup_tool --source database --dest /backup/backup-$(date +%Y%m%d).sql"])
    .volumes([{"name": "backup-storage", "mount_path": "/backup"}])
    .retention_limit(7))  # Keep 7 successful jobs

# Cleanup job
cleanup_job = (CronJob("cleanup-temp-files")
    .image("alpine:latest")
    .schedule("0 0 * * 0")  # Weekly on Sunday
    .command(["find", "/tmp", "-type", "f", "-mtime", "+7", "-delete"])
    .volumes([{"name": "tmp-storage", "mount_path": "/tmp"}])
    .concurrent_policy("Forbid"))  # Don't run multiple instances

app.add_jobs([migration, batch_job, backup_job, cleanup_job])
```

### Lifecycle Events

Container lifecycle management with hooks and signals.

```python
app.lifecycle(
    Lifecycle()
        .post_start(command=["sh", "-c", "echo 'Container started' > /tmp/started"])
        .pre_stop(command=["sh", "-c", "/app/graceful-shutdown.sh"])
        .pre_stop_http(path="/shutdown", port=8080)
        .termination_grace_period(30)
)

# Advanced lifecycle with hooks
app.lifecycle(
    Lifecycle()
        .post_start_exec(["./init-script.sh"])
        .pre_stop_http(path="/api/shutdown", port=8080, timeout=10)
        .on_failure(restart_policy="Always", backoff_limit=3)
        .cleanup_on_exit(["rm", "-rf", "/tmp/cache"])
)
```

### Dependency Management

Comprehensive dependency management without relying on init containers or sidecars.

```python
from k8s_gen import DependencyManager, WaitCondition

# Service-Level Dependencies
app.dependencies(
    DependencyManager()
        .wait_for_service("database", health_check="/health")
        .wait_for_service("cache", health_check="PING")
        .wait_for_service("message-queue", health_check="/ready")
        .wait_for_external_service("payment-gateway", url="https://api.payment.com/health")
        .wait_for_config_map("app-config")
        .wait_for_secret("db-credentials")
        .wait_for_persistent_volume("data-storage")
)

# Advanced Wait Conditions
app.dependencies(
    DependencyManager()
        .wait_for(
            WaitCondition("database-ready")
                .service("database")
                .health_check("/health")
                .timeout("5m")
                .retry_interval("10s")
                .max_retries(30)
                .success_criteria("status == 'ready'")
        )
        .wait_for(
            WaitCondition("cache-warm")
                .service("cache")
                .custom_check("cache-cli ping")
                .timeout("2m")
                .poll_interval("5s")
        )
        .wait_for(
            WaitCondition("message-queue-ready")
                .service("message-queue")
                .custom_check("queue-admin status")
                .timeout("3m")
                .expected_topics(["user-events", "order-events"])
        )
)

# Multi-Service Orchestration
orchestrator = DependencyManager()
orchestrator.wait_for_all([
    "database", "cache", "message-queue"
]).then_start("api-service")

orchestrator.wait_for_any([
    "primary-db", "replica-db"
]).then_start("read-service")

orchestrator.wait_for_sequence([
    "init-db", "migrate-schema", "seed-data"
]).then_start("web-app")

# Health Check Based Dependencies
app.dependencies(
    DependencyManager()
        .wait_for_healthy_pods("database", min_ready=1)
        .wait_for_healthy_pods("cache", min_ready=2)
        .wait_for_service_endpoints("api-gateway", min_endpoints=3)
        .wait_for_load_balancer_ready("external-service")
)

# Custom Dependency Checks
app.dependencies(
    DependencyManager()
        .wait_for_custom_check(
            name="database-migration-complete",
            command=["kubectl", "get", "job", "db-migration", "-o", "jsonpath='{.status.succeeded}'"],
            expected_result="1",
            timeout="10m"
        )
        .wait_for_custom_check(
            name="config-sync-complete",
            command=["kubectl", "get", "configmap", "app-config", "-o", "jsonpath='{.data.version}'"],
            expected_result="v2.0.0",
            timeout="2m"
        )
)

# Conditional Dependencies
app.dependencies(
    DependencyManager()
        .wait_for_if(
            condition="environment == 'production'",
            service="monitoring-stack"
        )
        .wait_for_if(
            condition="feature_flags.advanced_logging == true",
            service="log-aggregator"
        )
)

# Dependency Groups
app.dependencies(
    DependencyManager()
        .wait_for_group("infrastructure", [
            "database", "cache", "storage"
        ])
        .wait_for_group("monitoring", [
            "prometheus", "grafana", "alertmanager"
        ])
        .wait_for_group("security", [
            "vault", "cert-manager"
        ])
)
```

## Networking and Exposure

### Companions (Sidecars & Init Containers)

Supporting containers that run alongside your main application.

```python
# Sidecar for logging
app.add_companion(
    Companion("log-collector")
        .image("log-agent:latest")
        .type("sidecar")
        .mount_shared_volume("/var/log")
        .environment({"LOG_LEVEL": "info"})
)

# Init container for database migration
app.add_companion(
    Companion("db-migrate")
        .image("migrate:latest")
        .type("init")
        .environment({"DB_URL": "database://..."})
        .wait_for_completion()
)
```

### Storage Management

Different types of storage for various use cases.

```python
# Persistent storage
app.add_storage(
    Storage("user-data")
        .type("persistent")
        .size("10Gi")
        .mount_path("/data")
        .access_mode("read_write_once")
)

# Shared storage between containers
app.add_storage(
    Storage("shared-cache")
        .type("shared")
        .size("5Gi")
        .mount_path("/cache")
        .access_mode("read_write_many")
)

# Temporary storage
app.add_storage(
    Storage("temp-data")
        .type("ephemeral")
        .size("1Gi")
        .mount_path("/tmp")
)
```

### Service Discovery

Automatic service discovery and networking.

```python
# Basic service exposure
app.expose(
    Service()
        .type("cluster_ip")
        .port(8080)
        .target_port(8080)
)

# Load balancer service
app.expose(
    Service()
        .type("load_balancer")
        .port(80)
        .target_port(8080)
        .external_traffic_policy("Local")
)

# Multiple ports
app.expose(
    Service()
        .add_port("http", 8080, 8080)
        .add_port("metrics", 9090, 9090)
        .add_port("admin", 8081, 8081)
)
```

### Advanced Ingress Management

Sophisticated HTTP routing, SSL, rate limiting, and more.

```python
from k8s_gen import Ingress

advanced_ingress = (Ingress("api-ingress")
    .host("api.mycompany.com")
    .path("/api/v1", "api-service", 8080)
    .path("/api/v2", "api-v2-service", 8080)
    .ssl_certificate("api-tls-secret")
    .rate_limiting(requests_per_minute=1000, burst=100)
    .cors(
        allowed_origins=["https://myapp.com", "https://admin.myapp.com"],
        allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allowed_headers=["Authorization", "Content-Type", "X-Requested-With"]
    )
    .middleware([
        {"name": "auth", "config": {"auth_url": "http://auth-service.default.svc.cluster.local/auth"}},
        {"name": "compression", "config": {"level": 6}},
        {"name": "timeout", "config": {"read_timeout": "30s", "write_timeout": "30s"}}
    ])
    .load_balancer_class("external-lb")
    .ip_whitelist(["10.0.0.0/8", "192.168.0.0/16"])
    .redirect_http_to_https(True)
    .custom_headers({
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    })
    .timeout(connect=10, read=60, write=60))

app.add_ingress([advanced_ingress])
```

### Scaling Configuration

Horizontal and vertical scaling with advanced policies.

```python
from k8s_gen import Scaling

app.scale(
    Scaling()
        .replicas(3)
        .auto_scale_on_cpu(target_percentage=70, min_replicas=2, max_replicas=10)
        .auto_scale_on_memory(target_percentage=80, min_replicas=2, max_replicas=10)
        .auto_scale_on_custom_metric("http_requests_per_second", target_value=100)
        .scale_down_policy(period="5m", pods=2, percentage=10)
        .scale_up_policy(period="1m", pods=4, percentage=50)
        .spread_across_zones()
        .anti_affinity("hard")
)
```

### Health & Monitoring

Comprehensive health checks and observability.

```python
from k8s_gen import Health

app.health(
    Health()
        .startup_probe("/health/startup", initial_delay=10, period=10, timeout=5, failure_threshold=30)
        .readiness_probe("/health/ready", initial_delay=5, period=5, timeout=3, failure_threshold=3)
        .liveness_probe("/health/live", initial_delay=30, period=10, timeout=5, failure_threshold=3)
        .custom_probes({
            "database": "SELECT 1",
            "cache": "PING",
            "external_api": "GET https://api.external.com/health"
        })
        .metrics_endpoint("/metrics", port=9090)
        .log_config(level="INFO", format="json", output="/var/log/app.log")
)
```

### RBAC Security

Role-Based Access Control with service accounts and permissions.

```python
from k8s_gen import ServiceAccount, Role, ClusterRole, RoleBinding

# Service account
service_account = ServiceAccount("app-service-account")

# Application-specific role
app_role = (Role("app-role")
    .allow("get", "list", "watch").on("configmaps", "secrets")
    .allow("create", "update", "patch").on("events")
    .allow("get").on("pods"))

# Monitoring role
monitoring_role = (ClusterRole("monitoring-role")
    .allow("get", "list", "watch").on("nodes", "pods", "services", "endpoints"))

# Role bindings
role_binding = RoleBinding("app-binding", app_role, service_account)
admin_binding = RoleBinding("admin-binding", "admin", service_account)

app.rbac(
    service_account=service_account,
    roles=[app_role, monitoring_role],
    bindings=[role_binding, admin_binding]
)
```

## Multi-Service Applications

### AppGroup (Multi-Service Applications)

Managing multiple related services together.

```python
from k8s_gen import AppGroup

microservices = AppGroup("ecommerce-platform")

# Stateful services
database = StatefulApp("database").image("database-server:latest").storage("20Gi")
cache = StatefulApp("cache").image("cache-server:latest").storage("5Gi")
message_queue = StatefulApp("message-queue").image("message-broker:latest").storage("10Gi")

# User service
user_service = (App("user-service")
    .image("mycompany/user-service:v1.2.0")
    .port(8080)
    .connect_to([database, cache]))

# Product service
product_service = (App("product-service")
    .image("mycompany/product-service:v1.1.0")
    .port(8080)
    .connect_to([database, message_queue]))

# Order service
order_service = (App("order-service")
    .image("mycompany/order-service:v1.0.0")
    .port(8080)
    .depends_on([user_service, product_service])
    .connect_to([database, message_queue]))

microservices.add_services([
    database, cache, message_queue,
    user_service, product_service, order_service
])

# Cross-service configuration
microservices.configure_networking(
    NetworkPolicy()
        .allow_internal_communication()
        .deny_external_access_except(["user-service"])
)
```

### Environment-Specific Configuration

Configure applications for different environments.

```python
# Development environment
dev_app = app.for_environment("development")
dev_app.scale(Scaling().replicas(1))
dev_app.resources(cpu="100m", memory="256Mi")

# Production environment
prod_app = app.for_environment("production")
prod_app.scale(
    Scaling()
        .replicas(5)
        .auto_scale_on_cpu(70)
        .spread_across_zones()
)
```

## Output Generation

### Code Generation

Generate different output formats from the same DSL code.

```python
# Generate standard Kubernetes YAML
app.generate().to_yaml("./k8s/")

# Generate Docker Compose (great for local development)
app.generate().to_docker_compose("./docker-compose.yml")

# Generate Docker Compose with override files
app.generate().to_docker_compose(
    base_file="./docker-compose.yml",
    override_files={
        "development": "./docker-compose.override.yml",
        "production": "./docker-compose.prod.yml"
    }
)

# Generate Helm chart
app.generate().to_helm_chart("./charts/my-app/")

# Generate Kustomize overlays
app.generate().to_kustomize("./k8s/base/", overlays=["dev", "staging", "prod"])

# Generate Terraform modules
app.generate().to_terraform("./terraform/modules/")

# Generate multiple formats at once
app.generate().to_all_formats("./output/", formats=["yaml", "docker-compose", "helm"])
```

### Validation & Linting

Built-in validation and best practices checking.

```python
# Built-in validation
validation_result = app.validate()
if not validation_result.is_valid:
    print(validation_result.errors)

# Security scanning
security_scan = app.security_scan()
if security_scan.has_vulnerabilities:
    print(security_scan.vulnerabilities)

# Best practices check
best_practices = app.check_best_practices()
print(best_practices.recommendations)
``` 