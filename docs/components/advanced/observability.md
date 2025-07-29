# Observability Class

The `Observability` class provides comprehensive monitoring, logging, and tracing capabilities for your applications. It integrates with popular observability tools like Prometheus, Grafana, Jaeger, and ELK stack.

## Overview

```python
from celestra import Observability

# Basic observability setup
obs = Observability("app-monitoring").enable_metrics().enable_logging()

# Production observability with full stack
obs = (Observability("production-monitoring")
    .enable_metrics(port=9090)
    .enable_logging(log_format="json")
    .enable_tracing(tracing_backend="jaeger")
    .add_alert_rules()
    .add_dashboards())
```

## Core API Functions

### Metrics Configuration

#### Enable Metrics
Enable metrics collection for the application.

```python
# Basic metrics
obs = Observability("app-monitoring").enable_metrics()

# Custom metrics configuration
obs = Observability("app-monitoring").enable_metrics(port=9090, path="/metrics")
```

#### Metrics Port
Set the metrics port.

```python
obs = Observability("app-monitoring").metrics_port(9090)
```

#### Metrics Path
Set the metrics endpoint path.

```python
obs = Observability("app-monitoring").metrics_path("/metrics")
```

#### Custom Metrics
Add custom metrics to the application.

```python
# Custom metrics
custom_metrics = [
    {"name": "http_requests_total", "type": "counter", "help": "Total HTTP requests"},
    {"name": "http_request_duration_seconds", "type": "histogram", "help": "HTTP request duration"}
]
obs = Observability("app-monitoring").custom_metrics(custom_metrics)
```

#### Business Metrics
Add business-specific metrics.

```python
# Business metrics
business_metrics = [
    {"name": "orders_processed", "type": "counter", "help": "Total orders processed"},
    {"name": "revenue_total", "type": "counter", "help": "Total revenue generated"}
]
obs = Observability("app-monitoring").business_metrics(business_metrics)
```

### Logging Configuration

#### Enable Logging
Enable structured logging for the application.

```python
# Basic logging
obs = Observability("app-monitoring").enable_logging()

# Custom logging configuration
obs = Observability("app-monitoring").enable_logging(log_format="json", log_level="debug")
```

#### Log Format
Set the log format.

```python
# JSON format
obs = Observability("app-monitoring").log_format("json")

# Text format
obs = Observability("app-monitoring").log_format("text")
```

#### Log Level
Set the log level.

```python
obs = Observability("app-monitoring").log_level("debug")
obs = Observability("app-monitoring").log_level("info")
obs = Observability("app-monitoring").log_level("warn")
obs = Observability("app-monitoring").log_level("error")
```

#### Log Fields
Add custom log fields.

```python
# Custom log fields
log_fields = {
    "service": "api-service",
    "version": "v1.0.0",
    "environment": "production"
}
obs = Observability("app-monitoring").log_fields(log_fields)
```

#### Log Rotation
Configure log rotation.

```python
obs = Observability("app-monitoring").log_rotation(
    max_size="100MB",
    max_age="7d",
    max_backups=5
)
```

### Tracing Configuration

#### Enable Tracing
Enable distributed tracing.

```python
# Basic tracing
obs = Observability("app-monitoring").enable_tracing()

# Custom tracing configuration
obs = Observability("app-monitoring").enable_tracing(
    tracing_backend="jaeger",
    sampling_rate=0.1
)
```

#### Tracing Backend
Set the tracing backend.

```python
# Jaeger
obs = Observability("app-monitoring").tracing_backend("jaeger")

# Zipkin
obs = Observability("app-monitoring").tracing_backend("zipkin")

# OpenTelemetry
obs = Observability("app-monitoring").tracing_backend("opentelemetry")
```

#### Sampling Rate
Set the sampling rate for traces.

```python
# 10% sampling
obs = Observability("app-monitoring").sampling_rate(0.1)

# 100% sampling
obs = Observability("app-monitoring").sampling_rate(1.0)
```

#### Trace Context Propagation
Enable trace context propagation.

```python
obs = Observability("app-monitoring").trace_context_propagation(True)
```

### Alerting Configuration

#### Add Alert Rules
Add alerting rules for monitoring.

```python
# Default alert rules
obs = Observability("app-monitoring").add_alert_rules()

# Custom alert rules
alert_rules = [
    {
        "name": "HighCPUUsage",
        "expr": "cpu_usage > 80",
        "for": "5m",
        "severity": "warning"
    },
    {
        "name": "HighMemoryUsage",
        "expr": "memory_usage > 90",
        "for": "5m",
        "severity": "critical"
    }
]
obs = Observability("app-monitoring").add_alert_rules(alert_rules)
```

#### Alert Rule
Add a single alert rule.

```python
obs = Observability("app-monitoring").alert_rule(
    "HighCPUUsage",
    "cpu_usage > 80",
    "5m",
    "warning"
)
```

#### alert_manager(url: str) -> Observability
Configure AlertManager URL.

```python
obs = Observability("app-monitoring").alert_manager("http://alertmanager:9093")
```

### Dashboard Configuration

#### add_dashboards(dashboards: List[Dict[str, Any]] = None) -> Observability
Add Grafana dashboards for visualization.

```python
# Default dashboards
obs = Observability("app-monitoring").add_dashboards()

# Custom dashboards
dashboards = [
    {
        "name": "Application Overview",
        "panels": ["cpu", "memory", "requests", "errors"]
    },
    {
        "name": "Business Metrics",
        "panels": ["orders", "revenue", "users"]
    }
]
obs = Observability("app-monitoring").add_dashboards(dashboards)
```

#### dashboard(name: str, panels: List[str]) -> Observability
Add a single dashboard.

```python
obs = Observability("app-monitoring").dashboard(
    "Application Overview",
    ["cpu", "memory", "requests", "errors"]
)
```

#### grafana_url(url: str) -> Observability
Configure Grafana URL.

```python
obs = Observability("app-monitoring").grafana_url("http://grafana:3000")
```

### Health Checks

#### health_check_endpoint(path: str = "/health") -> Observability
Configure health check endpoint.

```python
obs = Observability("app-monitoring").health_check_endpoint("/health")
```

#### readiness_endpoint(path: str = "/ready") -> Observability
Configure readiness endpoint.

```python
obs = Observability("app-monitoring").readiness_endpoint("/ready")
```

#### liveness_endpoint(path: str = "/live") -> Observability
Configure liveness endpoint.

```python
obs = Observability("app-monitoring").liveness_endpoint("/live")
```

### Performance Monitoring

#### enable_apm(apm_type: str = "elastic") -> Observability
Enable Application Performance Monitoring.

```python
# Elastic APM
obs = Observability("app-monitoring").enable_apm("elastic")

# New Relic APM
obs = Observability("app-monitoring").enable_apm("newrelic")

# Datadog APM
obs = Observability("app-monitoring").enable_apm("datadog")
```

#### performance_monitoring(enabled: bool = True) -> Observability
Enable performance monitoring.

```python
obs = Observability("app-monitoring").performance_monitoring(True)
```

#### error_tracking(enabled: bool = True) -> Observability
Enable error tracking.

```python
obs = Observability("app-monitoring").error_tracking(True)
```

### Integration Configuration

#### prometheus_integration(enabled: bool = True) -> Observability
Enable Prometheus integration.

```python
obs = Observability("app-monitoring").prometheus_integration(True)
```

#### grafana_integration(enabled: bool = True) -> Observability
Enable Grafana integration.

```python
obs = Observability("app-monitoring").grafana_integration(True)
```

#### jaeger_integration(enabled: bool = True) -> Observability
Enable Jaeger integration.

```python
obs = Observability("app-monitoring").jaeger_integration(True)
```

#### elasticsearch_integration(enabled: bool = True) -> Observability
Enable Elasticsearch integration.

```python
obs = Observability("app-monitoring").elasticsearch_integration(True)
```

#### kibana_integration(enabled: bool = True) -> Observability
Enable Kibana integration.

```python
obs = Observability("app-monitoring").kibana_integration(True)
```

### Advanced Configuration

#### namespace(namespace: str) -> Observability
Set the namespace for observability components.

```python
obs = Observability("app-monitoring").namespace("monitoring")
```

#### add_label(key: str, value: str) -> Observability
Add a label to observability components.

```python
obs = Observability("app-monitoring").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> Observability
Add multiple labels to observability components.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "monitoring"
}
obs = Observability("app-monitoring").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> Observability
Add an annotation to observability components.

```python
obs = Observability("app-monitoring").add_annotation("description", "Application monitoring")
```

#### add_annotations(annotations: Dict[str, str]) -> Observability
Add multiple annotations to observability components.

```python
annotations = {
    "description": "Application monitoring for production",
    "owner": "platform-team",
    "retention": "30d"
}
obs = Observability("app-monitoring").add_annotations(annotations)
```

#### retention_period(period: str) -> Observability
Set data retention period.

```python
obs = Observability("app-monitoring").retention_period("30d")
```

#### backup_enabled(enabled: bool = True) -> Observability
Enable backup for observability data.

```python
obs = Observability("app-monitoring").backup_enabled(True)
```

### Output Generation

#### generate() -> ObservabilityGenerator
Generate the observability configuration.

```python
# Generate Kubernetes YAML
obs.generate().to_yaml("./k8s/")

# Generate Helm values
obs.generate().to_helm_values("./helm/")

# Generate Terraform
obs.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready observability setup:

```python
from celestra import Observability

# Create comprehensive observability configuration
obs = (Observability("production-monitoring")
    .enable_metrics(port=9090, path="/metrics")
    .enable_logging(log_format="json", log_level="info")
    .enable_tracing(tracing_backend="jaeger", sampling_rate=0.1)
    .log_fields({
        "service": "api-service",
        "version": "v1.0.0",
        "environment": "production"
    })
    .log_rotation(max_size="100MB", max_age="7d", max_backups=5)
    .custom_metrics([
        {"name": "http_requests_total", "type": "counter", "help": "Total HTTP requests"},
        {"name": "http_request_duration_seconds", "type": "histogram", "help": "HTTP request duration"}
    ])
    .business_metrics([
        {"name": "orders_processed", "type": "counter", "help": "Total orders processed"},
        {"name": "revenue_total", "type": "counter", "help": "Total revenue generated"}
    ])
    .add_alert_rules([
        {
            "name": "HighCPUUsage",
            "expr": "cpu_usage > 80",
            "for": "5m",
            "severity": "warning"
        },
        {
            "name": "HighMemoryUsage",
            "expr": "memory_usage > 90",
            "for": "5m",
            "severity": "critical"
        }
    ])
    .add_dashboards([
        {
            "name": "Application Overview",
            "panels": ["cpu", "memory", "requests", "errors"]
        },
        {
            "name": "Business Metrics",
            "panels": ["orders", "revenue", "users"]
        }
    ])
    .health_check_endpoint("/health")
    .readiness_endpoint("/ready")
    .liveness_endpoint("/live")
    .enable_apm("elastic")
    .performance_monitoring(True)
    .error_tracking(True)
    .prometheus_integration(True)
    .grafana_integration(True)
    .jaeger_integration(True)
    .elasticsearch_integration(True)
    .kibana_integration(True)
    .namespace("monitoring")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "monitoring"
    })
    .add_annotations({
        "description": "Production monitoring stack",
        "owner": "platform-team@company.com",
        "retention": "30d"
    })
    .retention_period("30d")
    .backup_enabled(True))

# Generate manifests
obs.generate().to_yaml("./k8s/")
```

## Observability Stack Examples

### Prometheus + Grafana Stack
```python
# Prometheus + Grafana monitoring
prometheus_obs = (Observability("prometheus-stack")
    .enable_metrics(port=9090)
    .prometheus_integration(True)
    .grafana_integration(True)
    .add_alert_rules()
    .add_dashboards()
    .namespace("monitoring"))
```

### ELK Stack
```python
# ELK stack for logging
elk_obs = (Observability("elk-stack")
    .enable_logging(log_format="json")
    .elasticsearch_integration(True)
    .kibana_integration(True)
    .log_rotation(max_size="100MB", max_age="7d")
    .namespace("logging"))
```

### Jaeger Tracing
```python
# Jaeger for distributed tracing
jaeger_obs = (Observability("jaeger-tracing")
    .enable_tracing(tracing_backend="jaeger", sampling_rate=0.1)
    .jaeger_integration(True)
    .trace_context_propagation(True)
    .namespace("tracing"))
```

### Full Stack Observability
```python
# Complete observability stack
full_obs = (Observability("full-observability")
    .enable_metrics(port=9090)
    .enable_logging(log_format="json")
    .enable_tracing(tracing_backend="jaeger")
    .prometheus_integration(True)
    .grafana_integration(True)
    .elasticsearch_integration(True)
    .kibana_integration(True)
    .jaeger_integration(True)
    .add_alert_rules()
    .add_dashboards()
    .enable_apm("elastic")
    .namespace("observability"))
```

## Best Practices

### 1. **Use Structured Logging**
```python
# ✅ Good: Use structured logging
obs = Observability("app-monitoring").enable_logging(log_format="json")

# ❌ Bad: Use unstructured logging
obs = Observability("app-monitoring").enable_logging(log_format="text")
```

### 2. **Configure Appropriate Sampling**
```python
# ✅ Good: Use appropriate sampling for production
obs = Observability("app-monitoring").enable_tracing(sampling_rate=0.1)

# ❌ Bad: Use 100% sampling in production
obs = Observability("app-monitoring").enable_tracing(sampling_rate=1.0)
```

### 3. **Set Up Alerting**
```python
# ✅ Good: Configure alerting rules
obs = Observability("app-monitoring").add_alert_rules()

# ❌ Bad: No alerting configuration
obs = Observability("app-monitoring")  # No alerting
```

### 4. **Use Business Metrics**
```python
# ✅ Good: Track business metrics
obs = Observability("app-monitoring").business_metrics([
    {"name": "orders_processed", "type": "counter"}
])

# ❌ Bad: Only technical metrics
obs = Observability("app-monitoring")  # No business metrics
```

### 5. **Configure Data Retention**
```python
# ✅ Good: Set appropriate retention
obs = Observability("app-monitoring").retention_period("30d")

# ❌ Bad: No retention policy
obs = Observability("app-monitoring")  # No retention
```

### 6. **Enable Backup**
```python
# ✅ Good: Enable backup for observability data
obs = Observability("app-monitoring").backup_enabled(True)

# ❌ Bad: No backup configuration
obs = Observability("app-monitoring")  # No backup
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Service](../networking/service.md)** - For service discovery
- **[Ingress](../networking/ingress.md)** - For external access
- **[Secret](../security/secrets.md)** - For sensitive configuration

## Next Steps

- **[Cost Optimization](cost-optimization.md)** - Learn about cost optimization
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 