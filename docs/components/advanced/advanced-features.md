# Advanced Features

This section covers advanced features and capabilities of the Celestra DSL for production-ready deployments.

## Overview

Advanced features provide enterprise-grade capabilities including:
- Production deployment strategies
- Advanced security configurations
- Comprehensive monitoring and observability
- Cost optimization techniques
- Custom resource management
- Plugin system for extensibility

## Production Deployment Strategies

### Blue-Green Deployment

```python
from celestra import App, DeploymentStrategy

# Blue environment
blue_app = (App("app-blue")
    .image("app:v1.0.0")
    .port(8080)
    .replicas(5)
    .expose())

# Green environment
green_app = (App("app-green")
    .image("app:v2.0.0")
    .port(8080)
    .replicas(5)
    .expose())

# Blue-green strategy
strategy = (DeploymentStrategy("blue-green")
    .blue_green()
    .traffic_shift(50)  # 50% traffic to green
    .health_check("/health")
    .rollback_threshold(5))  # 5% error rate triggers rollback
```

### Canary Deployment

```python
from celestra import App, DeploymentStrategy

# Canary deployment
canary_app = (App("app-canary")
    .image("app:v2.0.0")
    .port(8080)
    .replicas(1)  # Start with 1 replica
    .expose())

# Canary strategy
strategy = (DeploymentStrategy("canary")
    .canary()
    .traffic_percentage(10)  # 10% traffic to canary
    .duration("30m")  # Run for 30 minutes
    .metrics_threshold(0.95)  # 95% success rate required
    .auto_promote(True))
```

### Rolling Update with Advanced Configuration

```python
from celestra import App, DeploymentStrategy

# Application with rolling update
app = (App("app-rolling")
    .image("app:v2.0.0")
    .port(8080)
    .replicas(10)
    .expose())

# Advanced rolling update strategy
strategy = (DeploymentStrategy("rolling-advanced")
    .rolling_update()
    .max_surge(2)  # Maximum 2 extra pods
    .max_unavailable(1)  # Maximum 1 unavailable pod
    .progress_deadline("10m")  # 10 minute deadline
    .min_ready_seconds(30)  # Wait 30 seconds between updates
    .health_check("/health")
    .rollback_on_failure(True))
```

## Security Policies

### Pod Security Standards

```python
from celestra import App, SecurityPolicy

# Application with security policy
app = (App("secure-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Security policy
security = (SecurityPolicy("app-security")
    .pod_security_standard("restricted")  # Most restrictive
    .run_as_non_root(True)
    .read_only_root_filesystem(True)
    .drop_capabilities(["ALL"])
    .add_capabilities(["NET_BIND_SERVICE"])
    .seccomp_profile("runtime/default")
    .apparmor_profile("runtime/default"))
```

### Network Security

```python
from celestra import App, NetworkPolicy

# Application with network policy
app = (App("networked-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Network policy
network_policy = (NetworkPolicy("app-network")
    .policy_type("Ingress")
    .add_ingress_rule(
        from_pods={"app": "frontend"},
        ports=[{"port": 8080, "protocol": "TCP"}]
    )
    .add_ingress_rule(
        from_namespaces={"name": "monitoring"},
        ports=[{"port": 9090, "protocol": "TCP"}]
    )
    .add_egress_rule(
        to_pods={"app": "database"},
        ports=[{"port": 5432, "protocol": "TCP"}]
    ))
```

### RBAC Configuration

```python
from celestra import App, ServiceAccount, Role, RoleBinding

# Application with RBAC
app = (App("rbac-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Service account
sa = ServiceAccount("app-sa")

# Role
role = (Role("app-role")
    .add_rule(["get", "list", "watch"], ["pods", "services"])
    .add_rule(["get"], ["configmaps", "secrets"])
    .add_rule(["create", "update", "patch"], ["events"]))

# Role binding
rb = (RoleBinding("app-binding")
    .add_subject("ServiceAccount", "app-sa")
    .add_role("app-role"))

# Add service account to app
app.add_service_account(sa)
```

## Observability and Monitoring

### Comprehensive Monitoring

```python
from celestra import App, Observability

# Application with observability
app = (App("monitored-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Observability configuration
observability = (Observability("app-observability")
    .prometheus_metrics(True)
    .custom_metrics({
        "http_requests_total": "counter",
        "http_request_duration_seconds": "histogram",
        "active_connections": "gauge"
    })
    .logging_config({
        "level": "info",
        "format": "json",
        "output": "stdout"
    })
    .tracing_config({
        "enabled": True,
        "sampling_rate": 0.1,
        "jaeger_endpoint": "jaeger-agent:6831"
    })
    .alerting_config({
        "high_error_rate": {
            "threshold": 0.05,
            "duration": "2m"
        },
        "high_latency": {
            "threshold": 1000,
            "duration": "5m"
        }
    }))
```

### Custom Metrics

```python
from celestra import App, Observability

# Application with custom metrics
app = (App("metrics-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Custom metrics configuration
metrics = (Observability("custom-metrics")
    .add_metric("business_transactions_total", "counter", "Total business transactions")
    .add_metric("cache_hit_ratio", "gauge", "Cache hit ratio percentage")
    .add_metric("database_connection_pool", "gauge", "Active database connections")
    .add_metric("api_response_time", "histogram", "API response time distribution")
    .add_metric("queue_size", "gauge", "Message queue size")
    .add_metric("user_sessions", "gauge", "Active user sessions")
    .add_metric("disk_usage_percent", "gauge", "Disk usage percentage")
    .add_metric("memory_usage_bytes", "gauge", "Memory usage in bytes"))
```

## Cost Optimization

### Resource Optimization

```python
from celestra import App, CostOptimization

# Application with cost optimization
app = (App("cost-optimized-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Cost optimization configuration
cost_opt = (CostOptimization("app-cost-optimization")
    .resource_optimization({
        "cpu": {
            "request": "100m",
            "limit": "500m",
            "target_utilization": 70
        },
        "memory": {
            "request": "128Mi",
            "limit": "512Mi",
            "target_utilization": 80
        }
    })
    .spot_instance_config({
        "enabled": True,
        "fallback_to_on_demand": True,
        "max_price": "0.10"
    })
    .autoscaling_config({
        "min_replicas": 2,
        "max_replicas": 10,
        "target_cpu_utilization": 70,
        "target_memory_utilization": 80
    })
    .storage_optimization({
        "class": "gp2",
        "encryption": True,
        "backup_retention": 7
    }))
```

### Spot Instance Management

```python
from celestra import App, CostOptimization

# Application with spot instances
app = (App("spot-app")
    .image("app:v1.0.0")
    .port(8080)
    .expose())

# Spot instance configuration
spot_config = (CostOptimization("spot-config")
    .spot_instance_management({
        "enabled": True,
        "instance_types": ["t3.medium", "t3.large"],
        "max_bid_price": "0.15",
        "fallback_strategy": "on_demand",
        "interruption_handling": "drain_and_terminate"
    })
    .node_group_config({
        "min_size": 1,
        "max_size": 5,
        "desired_size": 3,
        "spot_percentage": 80
    })
    .cost_analysis({
        "budget_limit": 1000,
        "alert_threshold": 0.8,
        "cost_allocation_tags": ["environment", "team", "project"]
    }))
```

## Custom Resource Management

### Custom Resource Definitions

```python
from celestra import CustomResource

# Custom resource definition
crd = (CustomResource("myapp.example.com")
    .api_version("example.com/v1")
    .kind("MyApp")
    .schema({
        "type": "object",
        "properties": {
            "spec": {
                "type": "object",
                "properties": {
                    "replicas": {"type": "integer"},
                    "image": {"type": "string"},
                    "port": {"type": "integer"}
                },
                "required": ["replicas", "image", "port"]
            }
        }
    })
    .webhook_config({
        "validation": True,
        "conversion": False
    })
    .printer_columns([
        {"name": "Replicas", "type": "integer", "jsonPath": ".spec.replicas"},
        {"name": "Image", "type": "string", "jsonPath": ".spec.image"},
        {"name": "Port", "type": "integer", "jsonPath": ".spec.port"}
    ]))
```

### Custom Resource Instances

```python
from celestra import CustomResource

# Custom resource instance
myapp = (CustomResource("myapp-instance")
    .api_version("example.com/v1")
    .kind("MyApp")
    .metadata({
        "name": "myapp",
        "namespace": "default"
    })
    .spec({
        "replicas": 3,
        "image": "myapp:v1.0.0",
        "port": 8080
    })
    .status({
        "available_replicas": 3,
        "ready_replicas": 3
    }))
```

## Plugin System

### Custom Plugin Development

```python
from celestra.plugins import PluginBase, PluginType, PluginMetadata

# Custom validator plugin
class CustomValidatorPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom-validator",
            version="1.0.0",
            description="Custom validation plugin",
            author="Developer",
            plugin_type=PluginType.VALIDATOR
        )
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
    
    def execute(self, context: Dict[str, Any]) -> Any:
        # Custom validation logic
        return validation_results

# Custom transformer plugin
class CustomTransformerPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom-transformer",
            version="1.0.0",
            description="Custom transformation plugin",
            author="Developer",
            plugin_type=PluginType.TRANSFORMER
        )
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
    
    def execute(self, context: Dict[str, Any]) -> Any:
        # Custom transformation logic
        return transformed_resources
```

### Template Engine Plugins

```python
from celestra.plugins import TemplatePlugin

# Custom template plugin
class CustomTemplatePlugin(TemplatePlugin):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="custom-template",
            version="1.0.0",
            description="Custom template engine",
            author="Developer",
            plugin_type=PluginType.TEMPLATE
        )
    
    def get_template_engine(self) -> str:
        return "custom-engine"
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        # Custom template rendering logic
        return rendered_template
    
    def get_supported_extensions(self) -> List[str]:
        return [".custom", ".template"]
```

## Advanced Configuration Patterns

### Environment-Specific Configuration

```python
from celestra import App, ConfigMap, Secret

# Environment-specific configuration
def create_app_for_environment(env: str):
    if env == "development":
        return (App("app-dev")
            .image("app:dev")
            .replicas(1)
            .resources(cpu="100m", memory="128Mi"))
    
    elif env == "staging":
        return (App("app-staging")
            .image("app:staging")
            .replicas(2)
            .resources(cpu="200m", memory="256Mi"))
    
    elif env == "production":
        return (App("app-prod")
            .image("app:latest")
            .replicas(5)
            .resources(cpu="500m", memory="512Mi")
            .add_annotations({
                "prometheus.io/scrape": "true",
                "prometheus.io/port": "9090"
            }))

# Usage
dev_app = create_app_for_environment("development")
staging_app = create_app_for_environment("staging")
prod_app = create_app_for_environment("production")
```

### Multi-Tenant Configuration

```python
from celestra import App, ConfigMap, Secret

# Multi-tenant application
def create_tenant_app(tenant: str, config: Dict[str, Any]):
    return (App(f"app-{tenant}")
        .image("app:latest")
        .port(8080)
        .replicas(config.get("replicas", 2))
        .resources(
            cpu=config.get("cpu", "200m"),
            memory=config.get("memory", "256Mi")
        )
        .add_labels({
            "tenant": tenant,
            "environment": config.get("environment", "production")
        })
        .add_config(ConfigMap(f"config-{tenant}")
            .add("config.json", json.dumps(config))
            .mount_as_file("/app/config/config.json"))
        .expose())

# Usage
tenant1_app = create_tenant_app("tenant1", {
    "replicas": 3,
    "cpu": "500m",
    "memory": "512Mi",
    "environment": "production"
})

tenant2_app = create_tenant_app("tenant2", {
    "replicas": 1,
    "cpu": "100m",
    "memory": "128Mi",
    "environment": "development"
})
```

## Best Practices

### 1. **Security First**
```python
# ✅ Good: Use security policies
security = SecurityPolicy("app-security").pod_security_standard("restricted")
app.add_security(security)

# ❌ Bad: No security policies
app = App("app")  # No security configuration
```

### 2. **Resource Optimization**
```python
# ✅ Good: Optimize resources
cost_opt = CostOptimization("cost-opt").resource_optimization({
    "cpu": {"request": "100m", "limit": "500m"},
    "memory": {"request": "128Mi", "limit": "512Mi"}
})

# ❌ Bad: No resource optimization
app = App("app")  # No cost optimization
```

### 3. **Comprehensive Monitoring**
```python
# ✅ Good: Comprehensive observability
obs = Observability("obs").prometheus_metrics(True).tracing_config({
    "enabled": True,
    "sampling_rate": 0.1
})

# ❌ Bad: No monitoring
app = App("app")  # No observability
```

### 4. **Custom Extensions**
```python
# ✅ Good: Use plugins for custom functionality
@plugin_decorator(PluginType.VALIDATOR)
class CustomValidator(ValidatorPlugin):
    pass

# ❌ Bad: Hardcode custom logic
# Custom logic embedded in application code
```

## Next Steps

- **[Plugin System](plugin-system.md)** - Learn about the plugin system
- **[Production Deployments](../examples/production/index.md)** - Production-ready examples
- **[Complex Platforms](../examples/complex/index.md)** - Advanced multi-service platforms 