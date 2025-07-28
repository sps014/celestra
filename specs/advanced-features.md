# Advanced Features

Production-ready features and enterprise integrations for the Celestra.

## Multi-Format Output

Generate multiple deployment formats from the same DSL code.

```python
from k8s_gen import App, StatefulApp

# Define your application once
app = (App("web-app")
    .image("webapp:latest")
    .port(8080)
    .scale(replicas=3)
    .expose(external_access=True))

database = StatefulApp("database").image("database-server:latest").storage("20Gi")

# Generate different output formats
app.generate().to_yaml("./k8s/")                    # Kubernetes YAML
app.generate().to_docker_compose("./compose.yml")   # Docker Compose
app.generate().to_helm_chart("./charts/")           # Helm Chart
app.generate().to_kustomize("./kustomize/")         # Kustomize
app.generate().to_terraform("./terraform/")         # Terraform

# Generate all formats at once
app.generate().to_all_formats("./output/", formats=["yaml", "helm", "compose"])
```

## Custom Resources & Operators

Extend Kubernetes with custom resources and operators.

```python
from k8s_gen import CustomResource

# Machine Learning Pipeline Custom Resource
ml_pipeline = (CustomResource("MLPipeline", "v1", "ml.company.com")
    .spec({
        "model": "bert-large",
        "training_data": "s3://bucket/data/",
        "resources": {"gpu": 2, "memory": "16Gi"},
        "hyperparameters": {
            "learning_rate": 0.001,
            "batch_size": 32,
            "epochs": 10
        }
    })
    .metadata(name="text-classification-pipeline"))

# Database Operator Custom Resource
database_cluster = (CustomResource("DatabaseCluster", "v1", "db.company.com")
    .spec({
        "replicas": 3,
        "storage": "100Gi",
        "backup_schedule": "0 2 * * *",
        "monitoring": True,
        "high_availability": True
    })
    .metadata(name="production-db-cluster"))

app.add_custom_resources([ml_pipeline, database_cluster])
```

## Observability and Monitoring

Comprehensive observability stack integration.

```python
from k8s_gen import Observability

app.observability(
    Observability()
        .metrics(
            endpoint="/metrics",
            port=9090,
            scrape_interval="30s",
            labels={"service": "web-app", "team": "backend"}
        )
        .logging(
            level="INFO",
            format="json",
            output="/var/log/app.log",
            rotation="daily",
            retention="30d"
        )
        .tracing(
            service_name="web-app",
            sampling_rate=0.1,
            endpoint="http://jaeger-collector:14268/api/traces"
        )
        .alerting(
            notification_webhook="https://hooks.chat.com/services/...",
            notification_email=["ops@company.com"],
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
                "cache": "PING",
                "external_api": "GET https://api.external.com/health"
            }
        )
)
```

### Generated Observability Resources

This configuration generates:
- **ServiceMonitor** for Prometheus scraping
- **PrometheusRule** for alerting rules and recording rules
- **Grafana Dashboard** ConfigMaps
- **Jaeger** tracing configuration
- **Fluentd/Fluent Bit** logging configuration
- **Alert Manager** notification configuration

## Advanced Deployment Strategies

Zero-downtime deployments with sophisticated rollout strategies.

```python
from k8s_gen import DeploymentStrategy

# Blue-Green Deployment
app.deployment_strategy(
    DeploymentStrategy()
        .blue_green(
            preview_service="web-app-preview",
            active_service="web-app-active", 
            auto_promotion_enabled=True,
            scaledown_delay="30s",
            rollback_window="10m"
        )
        .promotion_criteria(
            success_rate_threshold=99.5,
            latency_threshold="100ms",
            error_rate_threshold=0.1
        )
        .rollback_triggers(
            error_rate_threshold=1.0,
            latency_threshold="500ms"
        )
)

# Canary Deployment
app.deployment_strategy(
    DeploymentStrategy()
        .canary(
            steps=[
                {"weight": 10, "pause": "2m"},
                {"weight": 25, "pause": "5m"},
                {"weight": 50, "pause": "10m"},
                {"weight": 100}
            ],
            analysis_template="success-rate",
            analysis_args={"service-name": "web-app"}
        )
        .traffic_routing(
            smi_traffic_split=True,
            istio_virtual_service=True,
            header_routing={"version": "canary"}
        )
)

# Feature Flag Integration
app.deployment_strategy(
    DeploymentStrategy()
        .feature_flags(
            provider="flagsmith",  # or launchdarkly, split.io
            flags={
                "new_algorithm": {
                    "rollout_percentage": 25,
                    "user_segments": ["beta_users"],
                    "default_value": False
                },
                "enhanced_ui": {
                    "rollout_percentage": 50,
                    "geographic_restrictions": ["US", "CA"],
                    "default_value": True
                }
            }
        )
)
```

## External Service Integration

Connect to cloud services, APIs, and external systems.

```python
from k8s_gen import ExternalServices

app.external_services(
    ExternalServices()
        # Cloud Storage Services
        .cloud_storage("app-storage", 
            type="s3",  # or gcs, azure_blob
            region="us-east-1",
            versioning=True,
            encryption="AES256",
            lifecycle_policy="./storage-lifecycle.json"
        )
        .cloud_database("app-db",
            type="relational",  # or document, cache, graph
            engine="postgresql",
            version="13.7",
            instance_class="standard-large",
            storage="100GB",
            connection_secret="db-secret"
        )
        .cloud_cache("app-cache",
            type="redis",
            node_type="standard-large",
            num_nodes=3,
            cluster_mode=True
        )
        .cloud_queue("app-queue",
            type="message_queue",
            visibility_timeout=300,
            message_retention=1209600
        )
        
        # Monitoring and Observability
        .monitoring_service(
            provider="datadog",  # or newrelic, honeycomb
            api_key_secret="monitoring-secret",
            tags=["env:production", "service:myapp"]
        )
        .logging_service(
            provider="elasticsearch",  # or splunk, datadog
            endpoint="https://logging.company.com",
            auth_secret="logging-secret"
        )
        
        # External APIs
        .external_api("payment-gateway",
            url="https://api.payment.com",
            auth={"type": "bearer", "secret": "payment-secret"},
            rate_limit=100,
            timeout="30s"
        )
        .external_api("notification-service",
            url="https://api.notifications.com",
            auth={"type": "api_key", "secret": "notification-secret"},
            retry_policy={"max_attempts": 3, "backoff": "exponential"}
        )
        
        # CDN and Load Balancing
        .cdn_distribution("app-cdn",
            origins=["api.mycompany.com"],
            cache_behaviors={
                "/api/*": {"ttl": 0},
                "/static/*": {"ttl": 86400}
            },
            ssl_certificate="wildcard-cert"
        )
)
```

### Generated External Service Resources

This generates:
- **ConfigMaps** with connection details
- **Secrets** for authentication
- **ExternalName Services** for service discovery
- **NetworkPolicies** for secure communication
- **ServiceEntries** for service mesh integration

## Security Policies

Enterprise-grade security and compliance features.

```python
from k8s_gen import SecurityPolicy

app.security(
    SecurityPolicy()
        .pod_security_standards(
            profile="restricted",  # baseline, restricted, privileged
            audit=True,
            warn=True,
            enforce=True
        )
        .network_policies(
            default_deny_all=True,
            allowed_ingress=[
                {"from": "same-namespace", "ports": [8080]},
                {"from": "monitoring-namespace", "ports": [9090]}
            ],
            allowed_egress=[
                {"to": "database-namespace", "ports": [5432]},
                {"to": "external", "ports": [443, 80]}
            ]
        )
        .rbac_policies(
            principle_of_least_privilege=True,
            service_account_per_workload=True,
            rotate_tokens=True,
            token_ttl="1h"
        )
        .image_policies(
            allowed_registries=["company-registry.com", "docker.io"],
            required_signatures=True,
            vulnerability_scanning=True,
            base_image_restrictions=["alpine", "distroless"]
        )
        .runtime_security(
            admission_controller="gatekeeper",  # or opa, falco
            policies_path="./security-policies/",
            violation_action="block"  # warn, block
        )
)
```

## Cost Optimization

Intelligent resource management and cost controls.

```python
from k8s_gen import CostOptimization

app.cost_optimization(
    CostOptimization()
        .resource_requests(
            cpu_percentile=95,  # Use 95th percentile of actual usage
            memory_percentile=90,
            right_sizing_window="7d"
        )
        .vertical_scaling(
            enabled=True,
            mode="Auto",  # Off, Initial, Auto
            resource_policies={
                "cpu": {"min": "100m", "max": "2000m"},
                "memory": {"min": "128Mi", "max": "4Gi"}
            }
        )
        .horizontal_scaling(
            predictive_scaling=True,
            schedule_based_scaling={
                "business_hours": {"replicas": 10, "schedule": "0 9 * * 1-5"},
                "night_hours": {"replicas": 2, "schedule": "0 18 * * 1-5"}
            }
        )
        .spot_instances(
            enabled=True,
            interruption_handling=True,
            mixed_instance_policy={
                "on_demand_percentage": 20,
                "spot_instance_types": ["m5.large", "m5.xlarge", "c5.large"]
            }
        )
        .idle_resource_detection(
            cpu_threshold=5,  # Percentage
            memory_threshold=10,
            duration="1h",
            action="scale_down"  # alert, scale_down, terminate
        )
)
```

### Generated Cost Optimization Resources

This creates:
- **VerticalPodAutoscaler** resources
- **PodDisruptionBudgets** for safe scaling
- **Custom metrics** for cost tracking
- **Scheduled scaling** CronJobs
- **Resource quotas** and limits

## Plugin System

Extend Celestra with custom functionality and integrations.

```python
from k8s_gen import PluginManager

# Register custom plugins
plugins = PluginManager()
plugins.register("custom_database", "./plugins/database_plugin.py")
plugins.register("monitoring_stack", "./plugins/monitoring_plugin.py")
plugins.register("ml_workflow", "./plugins/ml_plugin.py")

# Use plugin-provided builders
from k8s_gen.plugins import CustomDatabase, MonitoringStack

# Custom database with automatic clustering
database = (CustomDatabase("postgres-cluster")
    .version("13.7")
    .cluster_size(3)
    .automatic_failover(True)
    .backup_retention("30d")
    .connection_pooling(max_connections=100))

# Complete monitoring stack
monitoring = (MonitoringStack("observability")
    .prometheus(retention="30d", storage="100Gi")
    .grafana(plugins=["postgres", "redis"])
    .alertmanager(slack_webhook="...", email_smtp="...")
    .jaeger(sampling_rate=0.1)
    .fluentd(log_retention="7d"))

app.add_plugins([database, monitoring])
```

### Plugin Development

```python
# plugins/database_plugin.py
from k8s_gen import Plugin, StatefulApp, Secret, ConfigMap

class CustomDatabase(Plugin):
    def __init__(self, name):
        super().__init__(name)
        self.cluster_size = 1
        self.version = "latest"
        
    def cluster_size(self, size):
        self.cluster_size = size
        return self
        
    def version(self, version):
        self.version = version
        return self
    
    def generate(self):
        # Generate database cluster resources
        primary = StatefulApp(f"{self.name}-primary")
        replicas = [StatefulApp(f"{self.name}-replica-{i}") 
                   for i in range(self.cluster_size - 1)]
        
        # Generate cluster configuration
        cluster_config = ConfigMap(f"{self.name}-config")
        cluster_secret = Secret(f"{self.name}-credentials")
        
        return [primary] + replicas + [cluster_config, cluster_secret]
```

## Integration Examples

### CI/CD Pipeline Integration

```python
# .github/workflows/deploy.yml integration
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Generate K8s manifests
      run: |
        pip install Celestra
        Celestra generate app.py --output ./k8s/
        
    - name: Validate manifests
      run: |
        Celestra validate ./k8s/
        Celestra security-scan ./k8s/
        
    - name: Deploy to staging
      run: |
        Celestra deploy ./k8s/ --environment staging
        Celestra test ./k8s/ --wait-for-ready
        
    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: |
        Celestra deploy ./k8s/ --environment production --strategy blue-green
```

### Multi-Environment Configuration

```python
# environments/base.py
from k8s_gen import App, StatefulApp

def create_app(env_config):
    database = (StatefulApp("database")
        .image("database-server:latest")
        .storage(env_config.database_storage)
        .replicas(env_config.database_replicas))
    
    app = (App("web-app")
        .image(f"webapp:{env_config.app_version}")
        .replicas(env_config.app_replicas)
        .resources(
            cpu=env_config.cpu_request,
            memory=env_config.memory_request
        ))
    
    return app, database

# environments/development.py
from dataclasses import dataclass

@dataclass
class DevConfig:
    app_version = "latest"
    app_replicas = 1
    database_storage = "10Gi"
    database_replicas = 1
    cpu_request = "100m"
    memory_request = "256Mi"

# environments/production.py
@dataclass
class ProdConfig:
    app_version = "v1.2.3"
    app_replicas = 5
    database_storage = "100Gi"
    database_replicas = 3
    cpu_request = "500m"
    memory_request = "1Gi"
```

This advanced features specification demonstrates the enterprise-ready capabilities of Celestra while maintaining the simplicity and abstraction that makes it powerful for both development and production use cases. 