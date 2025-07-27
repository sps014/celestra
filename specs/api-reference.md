# API Reference

Complete reference for the K8s-Gen DSL API with examples and usage patterns.

## Core Components

### App (Stateless Applications)

The `App` class represents stateless applications that don't require persistent storage.

```python
from k8s_gen import App

app = (App("my-web-app")
    .image("nginx:1.21")
    .port(80)
    .environment({
        "ENV": "production",
        "DB_HOST": "postgres.default.svc.cluster.local"
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
| `.image(name)` | Set container image | `.image("nginx:alpine")` |
| `.port(number)` | Expose port | `.port(8080)` |
| `.environment(dict)` | Set environment variables | `.environment({"DEBUG": "true"})` |
| `.resources(...)` | Set CPU/memory limits | `.resources(cpu="500m", memory="1Gi")` |
| `.replicas(count)` | Set replica count | `.replicas(3)` |
| `.expose(...)` | Expose service externally | `.expose(external_access=True)` |

### StatefulApp (Stateful Applications)

The `StatefulApp` class represents applications requiring persistent state like databases.

```python
from k8s_gen import StatefulApp

# PostgreSQL database
postgres = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432)
    .storage("20Gi")
    .replicas(1)
    .environment({
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "admin"
    })
    .backup_schedule("0 2 * * *")  # Daily at 2 AM
)

# Kafka event streaming
kafka = (StatefulApp("kafka")
    .image("bitnami/kafka:latest")
    .port(9092)
    .storage("50Gi")
    .replicas(3)
    .environment({
        "KAFKA_REPLICATION_FACTOR": "2",
        "KAFKA_NUM_PARTITIONS": "3"
    })
    .topics(["user-events", "order-events"])
    .retention_hours(168)  # 7 days
)

# Redis cache cluster
redis = (StatefulApp("redis")
    .image("redis:alpine")
    .port(6379)
    .storage("10Gi")
    .replicas(3)
    .cluster_mode()
    .persistence(save_interval="60 1000"))

# Connect app to stateful services
app.connect_to([postgres, kafka, redis])
```

### Secrets Management

Secure handling of sensitive data like passwords, API keys, and certificates.

```python
from k8s_gen import Secret

# Database credentials
db_secret = (Secret("database-credentials")
    .add("username", "admin")
    .add("password", "super-secret-password")
    .add("connection-string", "postgresql://admin:password@postgres:5432/myapp")
    .from_env_file(".env.secrets")
    .mount_path("/etc/secrets")
    .mount_as_env_vars(prefix="DB_"))

# API keys and certificates
api_secret = (Secret("api-keys")
    .add("stripe_key", "sk_live_...")
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

aws_secret = (Secret("aws-secrets")
    .from_aws_parameter_store("/myapp/production/")
    .from_aws_secrets_manager("myapp/api-keys"))

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
    .add("database_url", "postgresql://localhost:5432/myapp")
    .add("api_key", "your-api-key-here")
    .add("debug", "true")
    .mount_path("/etc/config"))

# Load from files
file_config = (ConfigMap("file-config")
    .from_file("app.yaml", "./config/app.yaml")
    .from_file("nginx.conf", "./config/nginx.conf")
    .mount_path("/etc/app"))

# Load entire directory
dir_config = (ConfigMap("dir-config")
    .from_directory("./config/")
    .mount_path("/etc/config")
    .file_mode(0o644))

# Environment-style configuration
env_config = (ConfigMap("env-config")
    .from_env_file(".env")
    .from_env_file(".env.production", prefix="PROD_")
    .mount_as_env_vars())

# JSON/YAML data structures
data_config = (ConfigMap("data-config")
    .add_json("database", {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    })
    .add_yaml("features", {
        "feature_a": True,
        "feature_b": False,
        "limits": {"max_users": 1000}
    })
    .mount_path("/etc/data"))

# Template-based configuration
template_config = (ConfigMap("template-config")
    .from_template("app.yaml.j2", {
        "environment": "production",
        "replicas": 3,
        "db_host": "postgres.prod.svc.cluster.local"
    })
    .mount_path("/etc/templates"))

# Hot-reload configuration
hot_reload_config = (ConfigMap("hot-config")
    .from_file("config.yaml", "./config/config.yaml")
    .enable_hot_reload(interval="30s")
    .mount_path("/etc/config")
    .on_change(restart_pods=True))

# Multi-format configuration
multi_config = (ConfigMap("multi-config")
    .add_properties("app.properties", {
        "server.port": "8080",
        "logging.level": "INFO"
    })
    .add_ini("database.ini", {
        "database": {
            "host": "localhost",
            "port": "5432"
        }
    })
    .add_toml("features.toml", {
        "features": {
            "feature_a": True,
            "feature_b": False
        }
    })
    .mount_path("/etc/config"))

# Add config to app
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
    .run_once()
    .depends_on([postgres])
    .environment({"MIGRATE_UP": "true"})
    .command(["python", "migrate.py", "--up"])
    .on_success(cleanup=True)
    .on_failure(restart_policy="Never")
    .timeout("10m")
    .parallelism(1)
    .completions(1))

# Data processing job
batch_job = (Job("data-processing")
    .image("myapp/processor:latest")
    .parallelism(5)
    .completions(100)
    .environment({"BATCH_SIZE": "1000"})
    .resources(cpu="2000m", memory="4Gi")
    .timeout("2h")
    .backoff_limit(3))

# Scheduled backup
backup_job = (CronJob("daily-backup")
    .image("postgres:13")
    .schedule("0 2 * * *")  # 2 AM daily
    .command(["sh", "-c", "pg_dump -h postgres mydb > /backup/backup-$(date +%Y%m%d).sql"])
    .environment({"PGPASSWORD": {"secret": "db-secret", "key": "password"}})
    .retention_limit(successful=7, failed=3)
    .timezone("America/New_York")
    .suspend(False))

# Scheduled cleanup
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

## Networking and Exposure

### Companions (Sidecars & Init Containers)

Supporting containers that run alongside your main application.

```python
# Sidecar for logging
app.add_companion(
    Companion("log-collector")
        .image("fluentd:latest")
        .type("sidecar")
        .mount_shared_volume("/var/log")
        .environment({"LOG_LEVEL": "info"})
)

# Init container for database migration
app.add_companion(
    Companion("db-migrate")
        .image("migrate:latest")
        .type("init")
        .environment({"DB_URL": "postgresql://..."})
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
    Storage("shared-logs")
        .type("shared")
        .mount_path("/var/log")
        .share_with_companions()
)

# Configuration storage
app.add_storage(
    Storage("app-config")
        .type("config")
        .from_files({
            "app.yaml": "./config/app.yaml",
            "database.yaml": "./config/database.yaml"
        })
        .mount_path("/etc/config")
)

# Secret storage
app.add_storage(
    Storage("api-keys")
        .type("secret")
        .from_env_file(".env")
        .mount_path("/etc/secrets")
)
```

### Networking & Service Discovery

How services communicate with each other.

```python
# Expose application to cluster
app.expose(
    Networking()
        .internal_port(80)
        .cluster_access()  # Creates ClusterIP service
        .service_name("web-api")
)

# External access
app.expose(
    Networking()
        .internal_port(80)
        .external_access()  # Creates LoadBalancer service
        .domain("api.mycompany.com")
        .ssl_redirect()
)

# Service mesh integration
app.expose(
    Networking()
        .internal_port(80)
        .service_mesh()  # Istio/Linkerd annotations
        .traffic_policy("round_robin")
        .circuit_breaker(max_failures=3)
)
```

### Advanced Ingress Management

Sophisticated HTTP routing and traffic management.

```python
from k8s_gen import Ingress

# Basic HTTP routing
basic_ingress = (Ingress("app-ingress")
    .host("api.mycompany.com")
    .path("/", app, port=8080)
    .ssl_certificate(cert_manager="letsencrypt-prod")
    .annotations({"kubernetes.io/ingress.class": "nginx"}))

# Multi-service routing
api_ingress = (Ingress("api-gateway")
    .host("api.mycompany.com")
    .path("/api/v1/users", user_service, port=8080)
    .path("/api/v1/products", product_service, port=8081)
    .path("/api/v1/orders", order_service, port=8082)
    .path("/", frontend_service, port=3000)
    .ssl_certificate(cert_manager="letsencrypt-prod")
    .rate_limiting(requests_per_minute=1000, burst=100)
    .cors(
        origins=["https://myapp.com", "https://admin.myapp.com"],
        methods=["GET", "POST", "PUT", "DELETE"],
        headers=["Authorization", "Content-Type"]
    )
    .middleware(["auth", "logging", "compression"])
    .load_balancer_class("nginx")
    .ip_whitelist(["192.168.1.0/24", "10.0.0.0/8"]))

# Advanced routing with rewrites
advanced_ingress = (Ingress("advanced-routing")
    .host("myapp.com")
    .path("/api/(.*)", api_service, port=8080, rewrite="/v1/$1")
    .path("/legacy/(.*)", legacy_service, port=9090, rewrite="/$1")
    .redirect_http_to_https()
    .custom_headers({
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff"
    })
    .timeout(connect=5, read=30, send=30))

app.add_ingress([basic_ingress, api_ingress])
```

## Scaling & Availability

### Scaling Configuration

Performance and availability requirements.

```python
app.scale(
    Scaling()
        .replicas(3)
        .max_replicas(10)
        .auto_scale_on_cpu(70)  # CPU percentage
        .auto_scale_on_memory(80)  # Memory percentage
        .auto_scale_on_requests_per_second(100)
)

# Advanced scaling
app.scale(
    Scaling()
        .replicas(2)
        .spread_across_zones()
        .avoid_single_points_of_failure()
        .rolling_update(max_unavailable=1, max_surge=1)
)
```

### Health & Monitoring

Health checks and monitoring integration.

```python
app.health(
    HealthCheck()
        .startup_probe("/health/startup", timeout=30)
        .readiness_probe("/health/ready", interval=10)
        .liveness_probe("/health/live", interval=30)
        .graceful_shutdown_timeout(30)
)

# Monitoring integration
app.monitor(
    Monitoring()
        .metrics_endpoint("/metrics")
        .prometheus_scraping()
        .custom_metrics(["http_requests_total", "response_time"])
        .alerts({
            "high_error_rate": "rate(http_errors_total[5m]) > 0.1",
            "high_latency": "histogram_quantile(0.95, response_time) > 1"
        })
)
```

## Security

### RBAC Security

Role-based access control configuration.

```python
from k8s_gen import ServiceAccount, Role, ClusterRole, RoleBinding

# Service account for the application
service_account = (ServiceAccount("app-service-account")
    .namespace("production")
    .annotations({
        "eks.amazonaws.com/role-arn": "arn:aws:iam::123456789:role/MyAppRole",
        "iam.gke.io/gcp-service-account": "myapp@project.iam.gserviceaccount.com"
    })
    .automount_service_account_token(False)
    .image_pull_secrets(["regcred"]))

# Application-specific role
app_role = (Role("app-role")
    .allow("get", "list", "watch").on("pods", "services", "endpoints")
    .allow("create", "update", "patch").on("configmaps")
    .allow("get").on("secrets").names(["app-secrets", "db-credentials"])
    .deny("delete").on("*"))

# Monitoring role
monitoring_role = (ClusterRole("monitoring-role")
    .allow("get", "list", "watch").on("pods", "services", "nodes")
    .allow("get").on("metrics.k8s.io", "custom.metrics.k8s.io")
    .cluster_wide())

# Bind roles to service account
role_binding = (RoleBinding("app-role-binding")
    .bind(app_role).to(service_account)
    .namespace("production"))

# Admin access for ops team
admin_binding = (ClusterRoleBinding("ops-admin")
    .bind("cluster-admin").to_group("ops-team@company.com")
    .cluster_wide())

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
postgres = StatefulApp("postgres").image("postgres:13").storage("20Gi")
redis = StatefulApp("redis").image("redis:alpine").storage("5Gi")
kafka = StatefulApp("kafka").image("bitnami/kafka:latest").storage("10Gi")

# User service
user_service = (App("user-service")
    .image("mycompany/user-service:v1.2.0")
    .port(8080)
    .connect_to([postgres, redis]))

# Product service
product_service = (App("product-service")
    .image("mycompany/product-service:v1.1.0")
    .port(8080)
    .connect_to([postgres, kafka]))

# Order service
order_service = (App("order-service")
    .image("mycompany/order-service:v1.0.0")
    .port(8080)
    .depends_on([user_service, product_service])
    .connect_to([postgres, kafka]))

microservices.add_services([
    postgres, redis, kafka,
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