# K8s-Gen DSL Specification

## Overview

K8s-Gen is a Python-based Domain-Specific Language (DSL) for generating Kubernetes manifests with minimal code complexity. The DSL abstracts away Kubernetes-specific terminology and provides an intuitive, builder-pattern API that allows developers to describe their applications and infrastructure needs without deep Kubernetes knowledge.

## Design Principles

### 1. Abstraction Over Configuration
- Users describe **what** they want, not **how** to configure it
- Business-focused terminology instead of Kubernetes jargon
- Sensible defaults for common patterns

### 2. Builder Pattern Architecture
- Fluent, chainable API
- Progressive disclosure of complexity
- Type-safe method chaining

### 3. Extensibility
- Plugin system for custom components
- Hooks for advanced configurations
- Composable patterns

## Core Concepts

### Application-Centric Model

Instead of thinking in terms of Pods, Services, and Deployments, users think in terms of:

- **Apps** - The main business logic containers (stateless)
- **StatefulApps** - Applications requiring persistent state (databases, message queues, etc.)
- **Companions** - Supporting containers (sidecars, init containers)
- **Storage** - Data persistence needs
- **Networking** - How services communicate
- **Scaling** - Performance and availability requirements
- **Lifecycle** - Container lifecycle management (hooks, signals)

## API Design

### 1. App Definition

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

### 2. Companions (Sidecars & Init Containers)

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

### 3. Storage Management

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

### 4. Networking & Service Discovery

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

### 5. Scaling & Availability

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

### 6. Health & Monitoring

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

### 7. Secrets Management

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

### 8. ConfigMap Management

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

### 9. Jobs and CronJobs

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

### 10. Lifecycle Events

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

### 11. Advanced Ingress Management

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

### 12. RBAC Security

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

### 13. Observability and Monitoring

```python
from k8s_gen import Observability

app.observability(
    Observability()
        .logging(
            level="INFO",
            format="json",
            output=["stdout", "fluentd"],
            structured_fields=["timestamp", "level", "message", "trace_id", "user_id"],
            retention_days=30,
            sampling_rate=1.0
        )
        .metrics(
            prometheus_scraping=True,
            scrape_interval="15s",
            metrics_path="/metrics",
            custom_metrics=[
                "http_requests_total",
                "http_request_duration_seconds",
                "db_connection_pool_size",
                "business_events_total"
            ],
            dashboards=[
                "grafana://app-dashboard",
                "grafana://business-metrics"
            ],
            recording_rules={
                "job:http_requests:rate5m": "rate(http_requests_total[5m])",
                "job:http_request_duration:p99": "histogram_quantile(0.99, http_request_duration_seconds_bucket)"
            }
        )
        .tracing(
            enabled=True,
            jaeger_endpoint="http://jaeger:14268/api/traces",
            sampling_rate=0.1,
            trace_headers=["x-trace-id", "x-request-id", "x-correlation-id"],
            service_name="myapp"
        )
        .alerting(
            slack_webhook="https://hooks.slack.com/services/...",
            pagerduty_integration_key="...",
            email_recipients=["ops@company.com"],
            rules={
                "high_error_rate": {
                    "condition": "rate(http_errors_total[5m]) > 0.05",
                    "for": "2m",
                    "severity": "critical",
                    "description": "Error rate is above 5% for 2 minutes"
                },
                "high_latency": {
                    "condition": "histogram_quantile(0.99, http_request_duration_seconds_bucket) > 2",
                    "for": "5m", 
                    "severity": "warning",
                    "description": "99th percentile latency is above 2 seconds"
                },
                "pod_crash_looping": {
                    "condition": "rate(kube_pod_container_status_restarts_total[15m]) > 0",
                    "for": "1m",
                    "severity": "critical"
                }
            }
        )
        .health_checks(
            startup_probe="/health/startup",
            readiness_probe="/health/ready", 
            liveness_probe="/health/live",
            custom_probes={
                "database": "SELECT 1",
                "redis": "PING",
                "external_api": "GET https://api.external.com/health"
            }
        )
)
```

### 14. Advanced Deployment Strategies

```python
from k8s_gen import DeploymentStrategy

app.deployment_strategy(
    DeploymentStrategy()
        .blue_green(
            enabled=True,
            switch_traffic_on_success=True,
            rollback_on_failure=True,
            test_suite="./tests/smoke_tests.py",
            success_criteria=[
                "error_rate < 1%",
                "latency_p99 < 500ms",
                "all_health_checks_pass"
            ],
            pre_switch_hook="./scripts/pre_switch.sh",
            post_switch_hook="./scripts/post_switch.sh"
        )
        .canary(
            enabled=True,
            initial_percentage=5,
            increment_percentage=10,
            success_criteria=[
                "error_rate < 0.5%",
                "latency_p95 < 200ms"
            ],
            analysis_duration="5m",
            automated_promotion=True,
            max_percentage=50,
            rollback_on_failure=True
        )
        .rolling_update(
            max_unavailable="25%",
            max_surge="25%",
            readiness_timeout="5m",
            progress_deadline="10m",
            revision_history_limit=5
        )
        .feature_flags(
            provider="launchdarkly",
            flags={
                "new_algorithm": {"default": False, "canary": True},
                "enhanced_ui": {"default": False, "percentage": 10}
            }
        )
)
```

### 15. External Service Integration

```python
from k8s_gen import ExternalServices

app.external_services(
    ExternalServices()
        # AWS Services
        .aws_s3_bucket("my-app-storage", 
            region="us-east-1",
            versioning=True,
            encryption="AES256",
            lifecycle_policy="./s3-lifecycle.json"
        )
        .aws_rds_instance("my-app-db",
            engine="postgres",
            version="13.7",
            instance_class="db.r5.large",
            storage="100GB",
            connection_secret="db-secret"
        )
        .aws_elasticache("my-app-cache",
            engine="redis",
            node_type="cache.r6g.large",
            num_nodes=3
        )
        .aws_sqs_queue("my-app-queue",
            visibility_timeout=300,
            message_retention=1209600
        )
        
        # Google Cloud Services
        .gcp_cloud_sql("my-app-db",
            database_version="POSTGRES_13",
            tier="db-custom-2-8192"
        )
        .gcp_pub_sub("my-app-events",
            topics=["user-events", "order-events"]
        )
        
        # Monitoring and Observability
        .datadog(
            api_key_secret="datadog-secret",
            tags=["env:production", "service:myapp"]
        )
        .new_relic(
            license_key_secret="newrelic-secret",
            app_name="MyApp Production"
        )
        
        # External APIs
        .external_api("payment-gateway",
            url="https://api.stripe.com",
            auth={"type": "bearer", "secret": "stripe-secret"},
            rate_limit=100
        )
        .external_api("notification-service",
            url="https://api.sendgrid.com",
            auth={"type": "api_key", "secret": "sendgrid-secret"}
        )
        
        # CDN and Load Balancing
        .cloudfront_distribution("my-app-cdn",
            origins=["api.mycompany.com"],
            cache_behaviors={
                "/api/*": {"ttl": 0},
                "/static/*": {"ttl": 86400}
            }
        )
)
```

### 16. StatefulApp (Databases, Message Queues, etc.)

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

### 17. Environment-Specific Configuration

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

### 18. Multi-Service Applications

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



## Advanced Features

### 1. Multi-Format Output

The DSL can generate multiple deployment formats from the same code:

- **Kubernetes YAML** - For production deployment to K8s clusters
- **Docker Compose** - For local development and testing
- **Helm Charts** - For templated K8s deployments
- **Kustomize** - For environment-specific overlays
- **Terraform** - For infrastructure as code

This allows developers to:
- Start development locally with Docker Compose
- Test the same application structure in different environments
- Gradually migrate from Docker Compose to Kubernetes
- Maintain consistency across development and production

### 2. Custom Resources & Operators

```python
# Custom resource integration
app.add_custom_resource(
    CustomResource("CertManager")
        .api_version("cert-manager.io/v1")
        .kind("Certificate")
        .spec({
            "secretName": "my-app-tls",
            "dnsNames": ["api.mycompany.com"],
            "issuerRef": {"name": "letsencrypt-prod", "kind": "ClusterIssuer"}
        })
)

# Operator pattern
app.add_operator(
    Operator("prometheus")
        .helm_chart("prometheus-community/prometheus")
        .values_file("./charts/prometheus-values.yaml")
        .namespace("monitoring")
)
```

### 3. Security Policies

```python
app.security(
    SecurityPolicy()
        .run_as_non_root()
        .read_only_filesystem()
        .drop_capabilities(["ALL"])
        .add_capabilities(["NET_ADMIN"])  # if needed
        .security_context_constraints("restricted")
        .pod_security_policy("baseline")
)

# Network security
app.network_security(
    NetworkSecurity()
        .deny_all_ingress()
        .allow_ingress_from_namespaces(["frontend", "api-gateway"])
        .allow_egress_to_services(["database", "cache"])
        .require_tls()
)
```

### 4. Cost Optimization

```python
app.cost_optimization(
    CostOptimization()
        .spot_instances(percentage=50)
        .scheduled_scaling({
            "business_hours": {"replicas": 5, "schedule": "0 8 * * 1-5"},
            "off_hours": {"replicas": 1, "schedule": "0 18 * * 1-5"}
        })
        .resource_quotas(
            cpu_limit="2000m",
            memory_limit="4Gi",
            storage_limit="100Gi"
        )
)
```

### 5. Plugin System

```python
# Custom plugin for specific needs
from k8s_gen.plugins import Plugin

class CustomLogPlugin(Plugin):
    def apply(self, app):
        app.add_companion(
            Companion("custom-logger")
                .image("mycompany/custom-logger:latest")
                .type("sidecar")
                .environment(self.config)
        )

app.use_plugin(
    CustomLogPlugin(config={"LOG_FORMAT": "json", "LOG_LEVEL": "info"})
)
```

## Code Generation

### 1. Output Formats

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

### 2. Validation & Linting

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

### 3. Environment Management

```python
# Multi-environment deployment
environments = {
    "development": {
        "replicas": 1,
        "resources": {"cpu": "100m", "memory": "256Mi"},
        "ingress": "dev-api.mycompany.com"
    },
    "staging": {
        "replicas": 2,
        "resources": {"cpu": "500m", "memory": "512Mi"},
        "ingress": "staging-api.mycompany.com"
    },
    "production": {
        "replicas": 5,
        "resources": {"cpu": "1000m", "memory": "1Gi"},
        "ingress": "api.mycompany.com",
        "auto_scaling": True
    }
}

for env_name, config in environments.items():
    env_app = app.for_environment(env_name)
    env_app.apply_config(config)
    env_app.generate().to_yaml(f"./k8s/{env_name}/")
```

## Implementation Architecture

### 1. Core Builder Classes

```python
# Base builder class
class BaseBuilder:
    def __init__(self, name):
        self.name = name
        self._config = {}
    
    def _set(self, key, value):
        self._config[key] = value
        return self
    
    def build(self):
        return self._config

# App builder
class App(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def port(self, port_number):
        return self._set('port', port_number)
    
    def environment(self, env_vars):
        return self._set('environment', env_vars)
    
    # ... more methods

# StatefulApp builder
class StatefulApp(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def storage(self, size):
        return self._set('storage_size', size)
    
    def replicas(self, count):
        return self._set('replicas', count)
    
    # ... more methods

# Secret builder
class Secret(BaseBuilder):
    def add(self, key, value):
        if 'data' not in self._config:
            self._config['data'] = {}
        self._config['data'][key] = value
        return self
    
    def from_env_file(self, file_path):
        return self._set('env_file', file_path)
    
    def from_vault(self, path, mapping):
        return self._set('vault_path', path).set('vault_mapping', mapping)
    
    def mount_as_env_vars(self, prefix=""):
        return self._set('mount_type', 'env').set('env_prefix', prefix)
    
    def type(self, secret_type):
        return self._set('type', secret_type)
    
    # ... more methods

# ConfigMap builder
class ConfigMap(BaseBuilder):
    def add(self, key, value):
        if 'data' not in self._config:
            self._config['data'] = {}
        self._config['data'][key] = value
        return self
    
    def from_file(self, key, file_path):
        return self._set(f'file_{key}', file_path)
    
    def from_directory(self, directory_path):
        return self._set('directory', directory_path)
    
    def mount_path(self, path):
        return self._set('mount_path', path)
    
    def mount_as_env_vars(self):
        return self._set('mount_type', 'env')
    
    # ... more methods

# Job builder
class Job(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def command(self, command_list):
        return self._set('command', command_list)
    
    def parallelism(self, count):
        return self._set('parallelism', count)
    
    def completions(self, count):
        return self._set('completions', count)
    
    def timeout(self, duration):
        return self._set('timeout', duration)
    
    # ... more methods

# CronJob builder
class CronJob(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def schedule(self, cron_expression):
        return self._set('schedule', cron_expression)
    
    def retention_limit(self, successful=3, failed=1):
        return self._set('successful_jobs_history_limit', successful).set('failed_jobs_history_limit', failed)
    
    def concurrent_policy(self, policy):
        return self._set('concurrency_policy', policy)
    
    # ... more methods

# Ingress builder
class Ingress(BaseBuilder):
    def host(self, hostname):
        return self._set('host', hostname)
    
    def path(self, path, service, port, rewrite=None):
        if 'paths' not in self._config:
            self._config['paths'] = []
        self._config['paths'].append({
            'path': path, 'service': service, 'port': port, 'rewrite': rewrite
        })
        return self
    
    def ssl_certificate(self, cert_manager=None):
        return self._set('ssl', True).set('cert_manager', cert_manager)
    
    def rate_limiting(self, requests_per_minute, burst=None):
        return self._set('rate_limit', requests_per_minute).set('rate_burst', burst)
    
    # ... more methods
```

### 2. Template System

```python
# Jinja2 templates for Kubernetes manifests
class TemplateRenderer:
    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.PackageLoader('k8s_gen', 'templates')
        )
    
    def render_deployment(self, app_config):
        template = self.env.get_template('deployment.yaml.j2')
        return template.render(app_config)
    
    def render_service(self, service_config):
        template = self.env.get_template('service.yaml.j2')
        return template.render(service_config)
    
    def render_configmap(self, config_map_config):
        template = self.env.get_template('configmap.yaml.j2')
        return template.render(config_map_config)
    
    def render_docker_compose(self, compose_config):
        template = self.env.get_template('docker-compose.yml.j2')
        return template.render(compose_config)
    
    def render_docker_compose_override(self, override_config):
        template = self.env.get_template('docker-compose.override.yml.j2')
        return template.render(override_config)
    
    def render_secret(self, secret_config):
        template = self.env.get_template('secret.yaml.j2')
        return template.render(secret_config)
    
    def render_job(self, job_config):
        template = self.env.get_template('job.yaml.j2')
        return template.render(job_config)
    
    def render_cronjob(self, cronjob_config):
        template = self.env.get_template('cronjob.yaml.j2')
        return template.render(cronjob_config)
    
    def render_ingress(self, ingress_config):
        template = self.env.get_template('ingress.yaml.j2')
        return template.render(ingress_config)
    
    def render_rbac(self, rbac_config):
        templates = ['serviceaccount.yaml.j2', 'role.yaml.j2', 'rolebinding.yaml.j2']
        return [self.env.get_template(t).render(rbac_config) for t in templates]
```

### 3. Validation Engine

```python
class Validator:
    def validate_app(self, app_config):
        errors = []
        
        # Required fields validation
        if 'image' not in app_config:
            errors.append("App must specify a container image")
        
        # Resource validation
        if 'resources' in app_config:
            errors.extend(self._validate_resources(app_config['resources']))
        
        return ValidationResult(errors)
    
    def validate_stateful_app(self, stateful_config):
        errors = []
        
        # Stateful-specific validation
        if 'storage_size' not in stateful_config:
            errors.append("StatefulApp must specify storage size")
        
        if 'replicas' in stateful_config and stateful_config['replicas'] < 1:
            errors.append("StatefulApp must have at least 1 replica")
        
        return ValidationResult(errors)
    
    def validate_secret(self, secret_config):
        errors = []
        
        if 'data' not in secret_config or len(secret_config['data']) == 0:
            errors.append("Secret must contain at least one key-value pair")
        
        # Validate secret type
        valid_types = ['Opaque', 'kubernetes.io/tls', 'kubernetes.io/basic-auth']
        if 'type' in secret_config and secret_config['type'] not in valid_types:
            errors.append(f"Invalid secret type. Must be one of: {valid_types}")
        
        return ValidationResult(errors)
    
    def validate_job(self, job_config):
        errors = []
        
        if 'image' not in job_config:
            errors.append("Job must specify a container image")
        
        if 'parallelism' in job_config and job_config['parallelism'] < 1:
            errors.append("Job parallelism must be at least 1")
        
        if 'completions' in job_config and job_config['completions'] < 1:
            errors.append("Job completions must be at least 1")
        
        return ValidationResult(errors)
    
    def validate_cronjob(self, cronjob_config):
        errors = []
        
        if 'schedule' not in cronjob_config:
            errors.append("CronJob must specify a schedule")
        
        # Basic cron expression validation
        if 'schedule' in cronjob_config:
            schedule = cronjob_config['schedule']
            parts = schedule.split()
            if len(parts) != 5:
                errors.append("CronJob schedule must be a valid cron expression (5 fields)")
        
        return ValidationResult(errors)
    
    def validate_ingress(self, ingress_config):
        errors = []
        
        if 'host' not in ingress_config:
            errors.append("Ingress must specify a host")
        
        if 'paths' not in ingress_config or len(ingress_config['paths']) == 0:
            errors.append("Ingress must specify at least one path")
        
        # Validate paths
        for path_config in ingress_config.get('paths', []):
            if 'path' not in path_config or 'service' not in path_config:
                errors.append("Each ingress path must specify path and service")
        
        return ValidationResult(errors)
```

## Example Usage Scenarios

### 1. Simple Web Application

```python
from k8s_gen import App, StatefulApp

# Create configuration
wp_config = (ConfigMap("wordpress-config")
    .add("WORDPRESS_DB_HOST", "mysql")
    .add("WORDPRESS_DB_NAME", "blog")
    .add_json("features", {
        "enable_cache": True,
        "max_upload_size": "50M"
    })
    .from_file("wp-config-extra.php", "./config/wp-config-extra.php")
    .mount_path("/etc/wordpress"))

# Create database
mysql = (StatefulApp("mysql")
    .image("mysql:8.0")
    .port(3306)
    .storage("20Gi")
    .environment({"MYSQL_DATABASE": "blog"}))

# Create a simple web app with database
web_app = (App("blog-app")
    .image("wordpress:latest")
    .port(80)
    .connect_to([mysql])
    .add_config([wp_config])
    .add_storage(
        Storage("wp-content")
            .type("persistent")
            .size("10Gi")
            .mount_path("/var/www/html")
    )
    .expose(external_access=True, domain="blog.example.com")
    .scale(replicas=2, auto_scale_on_cpu=70)
    .lifecycle(
        Lifecycle()
            .pre_stop_http(path="/wp-admin/shutdown.php")
            .termination_grace_period(30)
    ))

# Generate Kubernetes manifests
web_app.generate().to_yaml("./k8s/blog-app/")

# Generate Docker Compose for local development
web_app.generate().to_docker_compose("./docker-compose.yml")

# Generate both formats
web_app.generate().to_all_formats("./output/", formats=["yaml", "docker-compose"])
```

### 2. Microservices with Service Mesh

```python
from k8s_gen import AppGroup, App, StatefulApp

ecommerce = AppGroup("ecommerce")

# Stateful services
postgres = StatefulApp("postgres").image("postgres:13").storage("20Gi")
mongodb = StatefulApp("mongodb").image("mongo:5.0").storage("15Gi")
elasticsearch = StatefulApp("elasticsearch").image("elasticsearch:7.17").storage("30Gi")

# API Gateway
gateway = (App("api-gateway")
    .image("nginx:alpine")
    .port(80)
    .expose(external_access=True)
    .service_mesh(traffic_management=True)
    .lifecycle(
        Lifecycle()
            .pre_stop(command=["nginx", "-s", "quit"])
            .termination_grace_period(15)
    ))

# User service
users = (App("user-service")
    .image("mycompany/users:v1.0.0")
    .port(8080)
    .connect_to([postgres])
    .service_mesh())

# Product service
products = (App("product-service")
    .image("mycompany/products:v1.0.0")
    .port(8080)
    .connect_to([mongodb, elasticsearch])
    .service_mesh())

ecommerce.add_services([postgres, mongodb, elasticsearch, gateway, users, products])
ecommerce.configure_service_mesh(
    observability=True,
    security=True,
    traffic_management=True
)

ecommerce.generate().to_yaml("./k8s/ecommerce/")
```

### 3. Data Pipeline

```python
# Stateful services for data pipeline
postgres = (StatefulApp("postgres")
    .image("postgres:13")
    .storage("50Gi")
    .environment({"POSTGRES_DB": "airflow"}))

redis = (StatefulApp("redis")
    .image("redis:alpine")
    .storage("10Gi")
    .persistence(save_interval="60 1000"))

# ETL pipeline with batch processing
pipeline = (App("data-pipeline")
    .image("apache/airflow:latest")
    .schedule("0 2 * * *")  # Daily at 2 AM
    .environment({
        "AIRFLOW__CORE__EXECUTOR": "KubernetesExecutor",
        "AIRFLOW__CORE__SQL_ALCHEMY_CONN": "postgresql://..."
    })
    .add_storage(
        Storage("airflow-dags")
            .type("persistent")
            .size("50Gi")
            .mount_path("/opt/airflow/dags")
    )
    .resources(cpu="2000m", memory="4Gi")
    .connect_to([postgres, redis])
    .lifecycle(
        Lifecycle()
            .post_start_exec(["airflow", "db", "upgrade"])
            .pre_stop_http(path="/health", timeout=60)
    ))

# Worker pods for processing
worker = (App("pipeline-worker")
    .image("mycompany/etl-worker:latest")
    .scale(replicas=5, auto_scale_on_cpu=80)
    .resources(cpu="1000m", memory="2Gi")
    .add_storage(
        Storage("shared-data")
            .type("shared")
            .mount_path("/data")
    )
    .connect_to([postgres, redis]))

pipeline_group = AppGroup("data-platform")
pipeline_group.add_services([postgres, redis, pipeline, worker])
pipeline_group.generate().to_yaml("./k8s/data-platform/")
```

## Generated Output Examples

This section shows the actual Kubernetes manifests generated from the DSL code examples.

### 1. Simple Web Application Output

**DSL Code:**
```python
web_app = (App("blog-app")
    .image("wordpress:latest")
    .port(80)
    .environment({"WORDPRESS_DB_HOST": "mysql"})
    .resources(cpu="500m", memory="512Mi", cpu_limit="1000m", memory_limit="1Gi")
    .scale(replicas=2, auto_scale_on_cpu=70)
    .expose(external_access=True, domain="blog.example.com")
    .lifecycle(
        Lifecycle()
            .pre_stop_http(path="/shutdown")
            .termination_grace_period(30)
    ))
```

**Generated Kubernetes YAML:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blog-app
  labels:
    app: blog-app
    generated-by: k8s-gen
spec:
  replicas: 2
  selector:
    matchLabels:
      app: blog-app
  template:
    metadata:
      labels:
        app: blog-app
    spec:
      containers:
      - name: blog-app
        image: wordpress:latest
        ports:
        - containerPort: 80
          name: http
        env:
        - name: WORDPRESS_DB_HOST
          value: mysql
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        lifecycle:
          preStop:
            httpGet:
              path: /shutdown
              port: http
      terminationGracePeriodSeconds: 30
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: blog-app
  labels:
    app: blog-app
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: blog-app
---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: blog-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: blog-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: blog-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - blog.example.com
    secretName: blog-app-tls
  rules:
  - host: blog.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: blog-app
            port:
              number: 80
```

### 2. Application with Sidecars Output

**DSL Code:**
```python
app = (App("web-server")
    .image("nginx:alpine")
    .port(80)
    .add_companion(
        Companion("log-collector")
            .image("fluentd:latest")
            .type("sidecar")
            .mount_shared_volume("/var/log")
    )
    .add_storage(
        Storage("shared-logs")
            .type("shared")
            .mount_path("/var/log")
    ))
```

**Generated Kubernetes YAML:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
  labels:
    app: web-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-server
  template:
    metadata:
      labels:
        app: web-server
    spec:
      containers:
      - name: web-server
        image: nginx:alpine
        ports:
        - containerPort: 80
          name: http
        volumeMounts:
        - name: shared-logs
          mountPath: /var/log
      - name: log-collector
        image: fluentd:latest
        volumeMounts:
        - name: shared-logs
          mountPath: /var/log
      volumes:
      - name: shared-logs
        emptyDir: {}
```

### 3. StatefulApp Output

**DSL Code:**
```python
postgres = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432)
    .storage("20Gi")
    .replicas(1)
    .environment({
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "admin"
    })
    .backup_schedule("0 2 * * *"))
```

**Generated Kubernetes YAML:**

```yaml
# statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  labels:
    app: postgres
    type: stateful
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: myapp
        - name: POSTGRES_USER
          value: admin
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretRef:
              name: postgres-credentials
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 20Gi
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: postgres
  selector:
    app: postgres
---
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command: ["/bin/bash"]
            args:
            - -c
            - "pg_dump -h postgres -U admin myapp > /backup/backup-$(date +%Y%m%d).sql"
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backup
          restartPolicy: OnFailure
```

### 4. Secrets Output

**DSL Code:**
```python
# Database credentials and API keys
db_secret = (Secret("database-credentials")
    .add("username", "admin")
    .add("password", "super-secret-password")
    .add("connection-string", "postgresql://admin:password@postgres:5432/myapp")
    .mount_as_env_vars(prefix="DB_"))

api_secret = (Secret("api-keys")
    .add("stripe_key", "sk_live_...")
    .add("jwt_secret", "...")
    .from_file("tls.crt", "./certs/app.crt")
    .from_file("tls.key", "./certs/app.key")
    .type("tls"))

app.add_secrets([db_secret, api_secret])
```

**Generated Kubernetes YAML:**

```yaml
# secret-database-credentials.yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  labels:
    app: myapp
    generated-by: k8s-gen
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: c3VwZXItc2VjcmV0LXBhc3N3b3Jk  # base64 encoded
  connection-string: cG9zdGdyZXNxbDovL2FkbWluOnBhc3N3b3JkQHBvc3RncmVzOjU0MzIvbXlhcHA=
---
# secret-api-keys.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  labels:
    app: myapp
type: kubernetes.io/tls
data:
  stripe_key: c2tfbGl2ZV8uLi4=
  jwt_secret: Li4u
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t...
---
# Updated deployment.yaml (with secrets)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: password
        - name: DB_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: connection-string
        volumeMounts:
        - name: api-keys
          mountPath: /etc/ssl/certs
          readOnly: true
      volumes:
      - name: api-keys
        secret:
          secretName: api-keys
```

### 5. Jobs and CronJobs Output

**DSL Code:**
```python
# Database migration job
migration = (Job("db-migration")
    .image("myapp/migrator:latest")
    .command(["python", "migrate.py", "--up"])
    .timeout("10m")
    .on_success(cleanup=True))

# Scheduled backup
backup_job = (CronJob("daily-backup")
    .image("postgres:13")
    .schedule("0 2 * * *")
    .command(["sh", "-c", "pg_dump -h postgres mydb > /backup/backup-$(date +%Y%m%d).sql"])
    .retention_limit(successful=7, failed=3))

app.add_jobs([migration, backup_job])
```

**Generated Kubernetes YAML:**

```yaml
# job-db-migration.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  labels:
    app: myapp
    component: migration
spec:
  template:
    metadata:
      labels:
        app: myapp
        component: migration
    spec:
      restartPolicy: Never
      containers:
      - name: db-migration
        image: myapp/migrator:latest
        command: ["python", "migrate.py", "--up"]
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
      activeDeadlineSeconds: 600
  backoffLimit: 3
  ttlSecondsAfterFinished: 100
---
# cronjob-daily-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
  labels:
    app: myapp
    component: backup
spec:
  schedule: "0 2 * * *"
  successfulJobsHistoryLimit: 7
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: myapp
            component: backup
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: postgres:13
            command:
            - sh
            - -c
            - "pg_dump -h postgres mydb > /backup/backup-$(date +%Y%m%d).sql"
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

### 6. Advanced Ingress Output

**DSL Code:**
```python
# Multi-service routing with advanced features
api_ingress = (Ingress("api-gateway")
    .host("api.mycompany.com")
    .path("/api/v1/users", user_service, port=8080)
    .path("/api/v1/products", product_service, port=8081)
    .ssl_certificate(cert_manager="letsencrypt-prod")
    .rate_limiting(requests_per_minute=1000)
    .cors(origins=["https://myapp.com"])
    .middleware(["auth", "logging"]))

app.add_ingress([api_ingress])
```

**Generated Kubernetes YAML:**

```yaml
# ingress-api-gateway.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://myapp.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Authorization, Content-Type"
    nginx.ingress.kubernetes.io/auth-url: "http://auth-service.default.svc.cluster.local/auth"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Request-ID: $req_id";
      access_log /var/log/nginx/api-access.log main;
spec:
  tls:
  - hosts:
    - api.mycompany.com
    secretName: api-gateway-tls
  rules:
  - host: api.mycompany.com
    http:
      paths:
      - path: /api/v1/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 8080
      - path: /api/v1/products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 8081
```

### 7. RBAC Output

**DSL Code:**
```python
# Service account and RBAC
service_account = ServiceAccount("app-service-account")
app_role = (Role("app-role")
    .allow("get", "list", "watch").on("pods", "services")
    .allow("create", "update").on("configmaps"))

app.rbac(service_account=service_account, roles=[app_role])
```

**Generated Kubernetes YAML:**

```yaml
# serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: default
  labels:
    app: myapp
    generated-by: k8s-gen
automountServiceAccountToken: false
---
# role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["create", "update"]
---
# rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-role-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: default
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
---
# Updated deployment.yaml (with service account)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      serviceAccountName: app-service-account
      automountServiceAccountToken: false
      containers:
      - name: myapp
        image: myapp:latest
```

### 8. ConfigMap Output

**DSL Code:**
```python
# Multi-format configuration
config = (ConfigMap("app-config")
    .add("database_url", "postgresql://localhost:5432/myapp")
    .add("api_key", "your-api-key-here")
    .add_json("features", {
        "feature_a": True,
        "feature_b": False,
        "limits": {"max_users": 1000}
    })
    .from_file("nginx.conf", "./config/nginx.conf")
    .mount_path("/etc/config"))

app.add_config([config])
```

**Generated Kubernetes YAML:**

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  labels:
    app: myapp
    generated-by: k8s-gen
data:
  database_url: "postgresql://localhost:5432/myapp"
  api_key: "your-api-key-here"
  features.json: |
    {
      "feature_a": true,
      "feature_b": false,
      "limits": {
        "max_users": 1000
      }
    }
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
---
# Updated deployment.yaml (with config mount)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        volumeMounts:
        - name: app-config
          mountPath: /etc/config
          readOnly: true
      volumes:
      - name: app-config
        configMap:
          name: app-config
          defaultMode: 0644
```

### 9. Application with Persistent Storage Output

**DSL Code:**
```python
app = (App("database-app")
    .image("postgres:13")
    .port(5432)
    .add_storage(
        Storage("postgres-data")
            .type("persistent")
            .size("20Gi")
            .mount_path("/var/lib/postgresql/data")
            .access_mode("read_write_once")
    )
    .add_storage(
        Storage("db-config")
            .type("config")
            .from_files({"postgresql.conf": "./config/postgresql.conf"})
            .mount_path("/etc/postgresql")
    ))
```

**Generated Kubernetes YAML:**

```yaml
# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-data
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 20Gi
---
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: db-config
data:
  postgresql.conf: |
    # PostgreSQL configuration content here
    max_connections = 100
    shared_buffers = 128MB
---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database-app
  template:
    metadata:
      labels:
        app: database-app
    spec:
      containers:
      - name: database-app
        image: postgres:13
        ports:
        - containerPort: 5432
          name: postgres
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
        - name: db-config
          mountPath: /etc/postgresql
      volumes:
      - name: postgres-data
        persistentVolumeClaim:
          claimName: postgres-data
      - name: db-config
        configMap:
          name: db-config
```

### 10. Multi-Service Application Output

**DSL Code:**
```python
microservices = AppGroup("ecommerce")

postgres = StatefulApp("postgres").image("postgres:13").storage("20Gi")

user_service = (App("user-service")
    .image("mycompany/users:v1.0.0")
    .port(8080)
    .connect_to([postgres])
    .environment({"DB_HOST": "postgres"}))

product_service = (App("product-service")
    .image("mycompany/products:v1.0.0")
    .port(8080)
    .depends_on([user_service])
    .connect_to([postgres]))

microservices.add_services([postgres, user_service, product_service])
```

**Generated Kubernetes YAML:**

```yaml
# user-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
  namespace: ecommerce
  labels:
    app: user-service
    group: ecommerce
spec:
  replicas: 1
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: mycompany/users:v1.0.0
        ports:
        - containerPort: 8080
          name: http
        env:
        - name: DB_HOST
          value: postgres-users
---
# user-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
  namespace: ecommerce
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: http
  selector:
    app: user-service
---
# product-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: product-service
  namespace: ecommerce
  labels:
    app: product-service
    group: ecommerce
spec:
  replicas: 1
  selector:
    matchLabels:
      app: product-service
  template:
    metadata:
      labels:
        app: product-service
    spec:
      initContainers:
      - name: wait-for-user-service
        image: busybox:1.28
        command: ['sh', '-c', 'until nslookup user-service; do echo waiting for user-service; sleep 2; done;']
      containers:
      - name: product-service
        image: mycompany/products:v1.0.0
        ports:
        - containerPort: 8080
          name: http
---
# product-service-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: product-service
  namespace: ecommerce
spec:
  type: ClusterIP
  ports:
  - port: 8080
    targetPort: http
  selector:
    app: product-service
---
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ecommerce
  labels:
    generated-by: k8s-gen
```

### 11. Helm Chart Output

**DSL Code:**
```python
app = (App("api-server")
    .image("mycompany/api:latest")
    .port(8080)
    .scale(replicas=3))

app.generate().to_helm_chart("./charts/api-server/")
```

**Generated Helm Chart Structure:**
```
charts/api-server/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── ingress.yaml
│   └── NOTES.txt
└── .helmignore
```

**Chart.yaml:**
```yaml
apiVersion: v2
name: api-server
description: A Helm chart for api-server generated by k8s-gen
type: application
version: 0.1.0
appVersion: "latest"
```

**values.yaml:**
```yaml
replicaCount: 3

image:
  repository: mycompany/api
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix
  tls: []

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

resources: {}
nodeSelector: {}
tolerations: []
affinity: {}
```

**templates/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api-server.fullname" . }}
  labels:
    {{- include "api-server.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "api-server.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "api-server.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

### 12. Kustomize Output

**DSL Code:**
```python
app = (App("web-app")
    .image("nginx:alpine")
    .port(80))

app.generate().to_kustomize("./k8s/base/", overlays=["dev", "staging", "prod"])
```

**Generated Kustomize Structure:**
```
k8s/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── dev/
    │   ├── kustomization.yaml
    │   └── dev-patch.yaml
    ├── staging/
    │   ├── kustomization.yaml
    │   └── staging-patch.yaml
    └── prod/
        ├── kustomization.yaml
        └── prod-patch.yaml
```

**base/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml

commonLabels:
  app: web-app
  generated-by: k8s-gen
```

**overlays/prod/kustomization.yaml:**
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesStrategicMerge:
- prod-patch.yaml

replicas:
- name: web-app
  count: 5
```

**overlays/prod/prod-patch.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  template:
    spec:
      containers:
      - name: web-app
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
```

### 13. Security Policy Output

**DSL Code:**
```python
app = (App("secure-app")
    .image("mycompany/app:latest")
    .port(8080)
    .security(
        SecurityPolicy()
            .run_as_non_root()
            .read_only_filesystem()
            .drop_capabilities(["ALL"])
    ))
```

**Generated Security Resources:**

```yaml
# pod-security-policy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: secure-app-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
  readOnlyRootFilesystem: true
---
# deployment.yaml (with security context)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-app
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: secure-app
        image: mycompany/app:latest
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-cache
          mountPath: /var/cache
      volumes:
      - name: tmp
        emptyDir: {}
      - name: var-cache
        emptyDir: {}
```

### 14. Docker Compose Output

**DSL Code:**
```python
# Create configuration
wp_config = ConfigMap("wordpress-config").add("WORDPRESS_DB_HOST", "mysql")

# Create database
mysql = (StatefulApp("mysql")
    .image("mysql:8.0")
    .port(3306)
    .storage("20Gi")
    .environment({"MYSQL_DATABASE": "blog", "MYSQL_ROOT_PASSWORD": "secret"}))

# Create web app
web_app = (App("blog-app")
    .image("wordpress:latest")
    .port(80)
    .connect_to([mysql])
    .add_config([wp_config])
    .scale(replicas=2)
    .expose(external_access=True))

# Generate Docker Compose
web_app.generate().to_docker_compose("./docker-compose.yml")
```

**Generated Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    restart: unless-stopped
    ports:
      - "3306:3306"
    environment:
      MYSQL_DATABASE: blog
      MYSQL_ROOT_PASSWORD: secret
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  blog-app:
    image: wordpress:latest
    container_name: blog-app
    restart: unless-stopped
    ports:
      - "80:80"
    environment:
      WORDPRESS_DB_HOST: mysql
    volumes:
      - ./config/wordpress-config:/etc/wordpress:ro
    networks:
      - app-network
    depends_on:
      mysql:
        condition: service_healthy
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

volumes:
  mysql_data:
    driver: local

networks:
  app-network:
    driver: bridge
```

**Docker Compose Override for Development:**
```yaml
# docker-compose.override.yml (for development)
version: '3.8'

services:
  mysql:
    ports:
      - "3306:3306"  # Expose MySQL port for debugging
    volumes:
      - ./mysql-dev-data:/var/lib/mysql  # Use local directory

  blog-app:
    ports:
      - "8080:80"  # Different port for development
    volumes:
      - ./wp-content:/var/www/html/wp-content  # Mount source code
    environment:
      WORDPRESS_DEBUG: 1
    deploy:
      replicas: 1  # Single instance for development
```

**Docker Compose for Production:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mysql:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  blog-app:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 5
         environment:
       WORDPRESS_DEBUG: 0
```

### 15. Microservices Docker Compose Output

**DSL Code:**
```python
microservices = AppGroup("ecommerce")

# Stateful services
postgres = StatefulApp("postgres").image("postgres:13").storage("20Gi")
redis = StatefulApp("redis").image("redis:alpine").storage("5Gi")

# Microservices
user_service = (App("user-service")
    .image("mycompany/users:v1.0.0")
    .port(8080)
    .connect_to([postgres, redis]))

product_service = (App("product-service")
    .image("mycompany/products:v1.0.0")
    .port(8081)
    .connect_to([postgres]))

api_gateway = (App("api-gateway")
    .image("nginx:alpine")
    .port(80)
    .depends_on([user_service, product_service])
    .expose(external_access=True))

microservices.add_services([postgres, redis, user_service, product_service, api_gateway])
microservices.generate().to_docker_compose("./docker-compose.yml")
```

**Generated Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    container_name: ecommerce-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secret}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ecommerce-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d ecommerce"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:alpine
    container_name: ecommerce-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ecommerce-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  user-service:
    image: mycompany/users:v1.0.0
    container_name: ecommerce-user-service
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      DB_HOST: postgres
      REDIS_HOST: redis
      SPRING_PROFILES_ACTIVE: docker
    networks:
      - ecommerce-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  product-service:
    image: mycompany/products:v1.0.0
    container_name: ecommerce-product-service
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      DB_HOST: postgres
      SPRING_PROFILES_ACTIVE: docker
    networks:
      - ecommerce-network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  api-gateway:
    image: nginx:alpine
    container_name: ecommerce-api-gateway
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - ecommerce-network
    depends_on:
      user-service:
        condition: service_healthy
      product-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  ecommerce-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Output Format Mapping

| DSL Concept | Kubernetes Resources | Docker Compose Resources |
|-------------|---------------------|--------------------------|
| `App()` | Deployment + Service | Service definition |
| `StatefulApp()` | StatefulSet + Service + PVC + CronJob | Service with volumes + healthcheck |
| `Secret()` | Secret + Volume mounts + Env vars | Environment variables (secrets) |
| `ConfigMap()` | ConfigMap + Volume mounts | Environment variables + file mounts |
| `Job()` | Job | Run-once service with restart policy |
| `CronJob()` | CronJob | Scheduled service with cron-like timing |
| `Ingress()` | Ingress + Certificate + NetworkPolicy | Published ports + labels |
| `ServiceAccount()` | ServiceAccount + Role + RoleBinding | User and group settings |
| `.scale()` | HorizontalPodAutoscaler | Deploy replicas + restart_policy |
| `.expose(external_access=True)` | LoadBalancer Service + Ingress | Published ports |
| `.add_storage(type="persistent")` | PersistentVolumeClaim | Named volumes |
| `.add_storage(type="config")` | ConfigMap | File mounts + environment |
| `.add_storage(type="secret")` | Secret | Environment variables (secrets) |
| `.add_companion(type="sidecar")` | Additional container in Pod | Additional service in compose |
| `.add_companion(type="init")` | InitContainer in Pod | depends_on with init service |
| `.health()` | Liveness/Readiness Probes | healthcheck configuration |
| `.lifecycle()` | Lifecycle hooks (preStop, postStart) | restart_policy + stop_signal |
| `.security()` | SecurityContext + PodSecurityPolicy | user, security_opt settings |
| `.observability()` | ServiceMonitor + PrometheusRule + ConfigMap | logging and monitoring configs |
| `.deployment_strategy()` | Deployment strategy + Argo Rollouts | Deploy configuration |
| `.external_services()` | ExternalName Service + ConfigMap | external_links and networks |
| `AppGroup()` | Namespace + multiple Deployments/StatefulSets | Multiple services + networks |
| `.connect_to()` | Service references + environment variables | depends_on + networks + env vars |
| `.service_mesh()` | Service + VirtualService + DestinationRule | networks + external networks |

## CLI Interface

```bash
# Initialize new project
k8s-gen init my-app

# Generate Kubernetes manifests
k8s-gen generate app.py --output ./k8s/

# Generate Docker Compose
k8s-gen generate app.py --format docker-compose --output ./docker-compose.yml

# Generate Docker Compose with override files
k8s-gen generate app.py --format docker-compose --output ./docker-compose.yml \
  --override development:./docker-compose.override.yml \
  --override production:./docker-compose.prod.yml

# Generate multiple formats
k8s-gen generate app.py --format all --output ./output/
k8s-gen generate app.py --format kubernetes,docker-compose,helm --output ./output/

# Validate configuration
k8s-gen validate app.py

# Deploy to Kubernetes cluster
k8s-gen deploy app.py --environment production

# Deploy using Docker Compose
k8s-gen deploy app.py --format docker-compose --environment development

# Dry run
k8s-gen deploy app.py --dry-run --diff

# Generate different formats
k8s-gen generate app.py --format helm --output ./charts/
k8s-gen generate app.py --format kustomize --output ./kustomize/
k8s-gen generate app.py --format terraform --output ./terraform/

# Start local development with Docker Compose
k8s-gen dev app.py  # Generates and runs docker-compose up -d

# Stop local development
k8s-gen dev app.py --down

# Watch for changes and auto-regenerate
k8s-gen dev app.py --watch

# Secrets management
k8s-gen secrets generate app.py --output ./secrets/
k8s-gen secrets encrypt ./secrets/ --key-file ./encryption.key
k8s-gen secrets sync --vault-addr https://vault.company.com

# Jobs and batch processing
k8s-gen jobs run migration.py --wait
k8s-gen jobs list --status completed
k8s-gen jobs logs db-migration --follow

# RBAC and security
k8s-gen rbac validate app.py
k8s-gen rbac generate app.py --output ./rbac/
k8s-gen security scan app.py --report ./security-report.html

# Observability
k8s-gen monitor setup app.py  # Sets up Prometheus, Grafana, Jaeger
k8s-gen monitor dashboards app.py --import ./dashboards/
k8s-gen alerts test app.py --dry-run
```

## Extension Points

### 1. Custom Builders

Users can extend the DSL with custom builders for specific use cases:

```python
class MLWorkloadBuilder(BaseBuilder):
    def gpu_resources(self, gpu_count, gpu_type="nvidia.com/gpu"):
        return self._set('gpu', {'count': gpu_count, 'type': gpu_type})
    
    def model_storage(self, model_path, size="100Gi"):
        return self._set('model_storage', {'path': model_path, 'size': size})
    
    def training_dataset(self, dataset_config):
        return self._set('dataset', dataset_config)

# Usage
ml_app = (App("model-training")
    .image("tensorflow/tensorflow:latest-gpu")
    .extend_with(MLWorkloadBuilder())
    .gpu_resources(2)
    .model_storage("/models")
    .training_dataset({"source": "s3://my-bucket/data"}))
```

### 2. Template Customization

```python
# Custom template directory
app.generate().with_templates("./custom-templates/").to_yaml()

# Template hooks
app.add_template_hook('pre_render', custom_preprocessing_function)
app.add_template_hook('post_render', custom_postprocessing_function)
```

This specification provides a comprehensive foundation for building a user-friendly, extensible Kubernetes DSL that abstracts complexity while maintaining the power and flexibility needed for real-world applications. 