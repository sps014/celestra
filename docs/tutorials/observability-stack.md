# Observability Stack Tutorial

This tutorial demonstrates how to set up a complete observability stack with monitoring, logging, and tracing using Celestra DSL.

## Overview

This tutorial shows how to:
- Deploy Prometheus for metrics collection
- Set up Grafana for visualization
- Configure Elasticsearch for log aggregation
- Deploy Jaeger for distributed tracing
- Set up alerting with AlertManager
- Configure application instrumentation

## Architecture

Our observability stack will include:

- **Prometheus** - Metrics collection and storage
- **Grafana** - Metrics visualization and dashboards
- **Elasticsearch** - Log aggregation and search
- **Kibana** - Log visualization and analysis
- **Jaeger** - Distributed tracing
- **AlertManager** - Alert routing and notification
- **Fluentd** - Log collection and forwarding

## Implementation

### 1. Prometheus Stack

```python
from celestra import StatefulApp, App, ConfigMap, Secret

# Prometheus server
prometheus = (StatefulApp("prometheus")
    .image("prom/prometheus:v2.45.0")
    .port(9090)
    .storage("50Gi")
    .resources(cpu="500m", memory="1Gi")
    .environment({
        "PROMETHEUS_CONFIG": "/etc/prometheus/prometheus.yml"
    })
    .expose())

# Prometheus configuration
prometheus_config = (ConfigMap("prometheus-config")
    .add("prometheus.yml", """
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_pod_name]
        action: replace
        target_label: kubernetes_pod_name

  - job_name: 'kubernetes-service-endpoints'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scheme]
        action: replace
        target_label: __scheme__
        regex: (https?)
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_service_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
      - action: labelmap
        regex: __meta_kubernetes_service_label_(.+)
      - source_labels: [__meta_kubernetes_namespace]
        action: replace
        target_label: kubernetes_namespace
      - source_labels: [__meta_kubernetes_service_name]
        action: replace
        target_label: kubernetes_name

  - job_name: 'kube-state-metrics'
    static_configs:
      - targets: ['kube-state-metrics.kube-system.svc.cluster.local:8080']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter.kube-system.svc.cluster.local:9100']
""")
    .mount_as_file("/etc/prometheus/prometheus.yml"))

# Alert rules
alert_rules = (ConfigMap("alert-rules")
    .add("alert_rules.yml", """
groups:
  - name: kubernetes
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for 5 minutes"

      - alert: PodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[15m]) * 60 > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod is crash looping"
          description: "Pod {{ $labels.pod }} is restarting frequently"

      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m]) * 100 > 5
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is above 5% for 2 minutes"
""")
    .mount_as_file("/etc/prometheus/alert_rules.yml"))

prometheus.add_config(prometheus_config)
prometheus.add_config(alert_rules)
```

### 2. Grafana

```python
from celestra import App, ConfigMap, Secret

# Grafana
grafana = (App("grafana")
    .image("grafana/grafana:9.5.0")
    .port(3000)
    .replicas(2)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "GF_SECURITY_ADMIN_PASSWORD": "admin123",
        "GF_USERS_ALLOW_SIGN_UP": "false"
    })
    .expose())

# Grafana configuration
grafana_config = (ConfigMap("grafana-config")
    .add("grafana.ini", """
[server]
http_port = 3000

[security]
admin_password = admin123

[database]
type = sqlite3
path = /var/lib/grafana/grafana.db

[users]
allow_sign_up = false

[auth.anonymous]
enabled = false
""")
    .mount_as_file("/etc/grafana/grafana.ini"))

# Dashboard configuration
dashboard_config = (ConfigMap("dashboard-config")
    .add("dashboards.yaml", """
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
""")
    .mount_as_file("/etc/grafana/provisioning/dashboards/dashboards.yaml"))

grafana.add_config(grafana_config)
grafana.add_config(dashboard_config)
```

### 3. Elasticsearch Stack

```python
from celestra import StatefulApp, App, ConfigMap

# Elasticsearch
elasticsearch = (StatefulApp("elasticsearch")
    .image("docker.elastic.co/elasticsearch/elasticsearch:8.8.0")
    .port(9200)
    .storage("100Gi")
    .replicas(3)
    .resources(cpu="1000m", memory="2Gi")
    .environment({
        "discovery.type": "single-node",
        "xpack.security.enabled": "false",
        "ES_JAVA_OPTS": "-Xms1g -Xmx1g"
    })
    .expose())

# Kibana
kibana = (App("kibana")
    .image("docker.elastic.co/kibana/kibana:8.8.0")
    .port(5601)
    .replicas(2)
    .resources(cpu="500m", memory="1Gi")
    .environment({
        "ELASTICSEARCH_HOSTS": "http://elasticsearch:9200"
    })
    .expose())

# Fluentd for log collection
fluentd = (App("fluentd")
    .image("fluent/fluentd-kubernetes-daemonset:v1.14-debian-elasticsearch7-1")
    .port(24224)
    .replicas(1)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "FLUENT_ELASTICSEARCH_HOST": "elasticsearch",
        "FLUENT_ELASTICSEARCH_PORT": "9200"
    })
    .expose())

# Fluentd configuration
fluentd_config = (ConfigMap("fluentd-config")
    .add("fluent.conf", """
<source>
  @type tail
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.log.pos
  tag kubernetes.*
  read_from_head true
  <parse>
    @type json
    time_format %Y-%m-%dT%H:%M:%S.%NZ
  </parse>
</source>

<filter kubernetes.**>
  @type kubernetes_metadata
</filter>

<match kubernetes.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix k8s
  <buffer>
    @type file
    path /var/log/fluentd-buffers/kubernetes.system.buffer
    flush_mode interval
    retry_type exponential_backoff
    flush_interval 5s
    retry_forever false
    retry_max_interval 30
    chunk_limit_size 2M
    queue_limit_length 8
    overflow_action block
  </buffer>
</match>
""")
    .mount_as_file("/fluentd/etc/fluent.conf"))

fluentd.add_config(fluentd_config)
```

### 4. Jaeger Tracing

```python
from celestra import StatefulApp, App

# Jaeger storage (Elasticsearch)
jaeger_storage = (StatefulApp("jaeger-storage")
    .image("docker.elastic.co/elasticsearch/elasticsearch:8.8.0")
    .port(9200)
    .storage("20Gi")
    .replicas(1)
    .resources(cpu="500m", memory="1Gi")
    .environment({
        "discovery.type": "single-node",
        "xpack.security.enabled": "false"
    })
    .expose())

# Jaeger collector
jaeger_collector = (App("jaeger-collector")
    .image("jaegertracing/jaeger-collector:1.47")
    .port(14268)
    .replicas(2)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "SPAN_STORAGE_TYPE": "elasticsearch",
        "ES_SERVER_URLS": "http://jaeger-storage:9200"
    })
    .expose())

# Jaeger query
jaeger_query = (App("jaeger-query")
    .image("jaegertracing/jaeger-query:1.47")
    .port(16686)
    .replicas(2)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "SPAN_STORAGE_TYPE": "elasticsearch",
        "ES_SERVER_URLS": "http://jaeger-storage:9200"
    })
    .expose())

# Jaeger agent (DaemonSet equivalent)
jaeger_agent = (App("jaeger-agent")
    .image("jaegertracing/jaeger-agent:1.47")
    .port(6831)
    .replicas(1)
    .resources(cpu="100m", memory="128Mi")
    .environment({
        "COLLECTOR_HOST_PORT": "jaeger-collector:14268"
    })
    .expose())
```

### 5. AlertManager

```python
from celestra import App, ConfigMap

# AlertManager
alertmanager = (App("alertmanager")
    .image("prom/alertmanager:v0.25.0")
    .port(9093)
    .replicas(2)
    .resources(cpu="200m", memory="256Mi")
    .expose())

# AlertManager configuration
alertmanager_config = (ConfigMap("alertmanager-config")
    .add("alertmanager.yml", """
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alertmanager@example.com'
  smtp_auth_username: 'alertmanager@example.com'
  smtp_auth_password: 'your-password'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://127.0.0.1:5001/'
        send_resolved: true

  - name: 'email'
    email_configs:
      - to: 'alerts@example.com'
        send_resolved: true

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
""")
    .mount_as_file("/etc/alertmanager/alertmanager.yml"))

alertmanager.add_config(alertmanager_config)
```

## Application Instrumentation

### 1. Node.js Application with Metrics

```python
from celestra import App, ConfigMap

# Node.js app with Prometheus metrics
app = (App("instrumented-app")
    .image("nodejs-app:1.0.0")
    .port(3000)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3000",
        "PROMETHEUS_METRICS_PORT": "9090"
    })
    .expose())

# Add Prometheus annotations
app.add_annotations({
    "prometheus.io/scrape": "true",
    "prometheus.io/port": "9090",
    "prometheus.io/path": "/metrics"
})

# Application configuration with tracing
app_config = (ConfigMap("app-config")
    .add("config.json", """
{
    "server": {
        "port": 3000,
        "host": "0.0.0.0"
    },
    "monitoring": {
        "metrics": {
            "enabled": true,
            "port": 9090
        },
        "tracing": {
            "enabled": true,
            "jaeger": {
                "host": "jaeger-agent",
                "port": 6831
            }
        },
        "logging": {
            "level": "info",
            "format": "json"
        }
    }
}""")
    .mount_as_file("/app/config/config.json"))

app.add_config(app_config)
```

### 2. Python Application with Instrumentation

```python
from celestra import App, ConfigMap

# Python app with instrumentation
python_app = (App("python-app")
    .image("python-app:1.0.0")
    .port(8000)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "PYTHONPATH": "/app",
        "PROMETHEUS_METRICS_PORT": "9090"
    })
    .expose())

# Add Prometheus annotations
python_app.add_annotations({
    "prometheus.io/scrape": "true",
    "prometheus.io/port": "9090",
    "prometheus.io/path": "/metrics"
})

# Python app configuration
python_config = (ConfigMap("python-config")
    .add("config.yaml", """
app:
  name: "python-app"
  version: "1.0.0"

monitoring:
  metrics:
    enabled: true
    port: 9090
    path: "/metrics"
  
  tracing:
    enabled: true
    jaeger:
      host: "jaeger-agent"
      port: 6831
  
  logging:
    level: "INFO"
    format: "json"
    output: "stdout"
""")
    .mount_as_file("/app/config/config.yaml"))

python_app.add_config(python_config)
```

## Deployment

### 1. Generate all manifests

```python
# Generate observability stack
prometheus.generate().to_yaml("./k8s/")
grafana.generate().to_yaml("./k8s/")
elasticsearch.generate().to_yaml("./k8s/")
kibana.generate().to_yaml("./k8s/")
fluentd.generate().to_yaml("./k8s/")
jaeger_storage.generate().to_yaml("./k8s/")
jaeger_collector.generate().to_yaml("./k8s/")
jaeger_query.generate().to_yaml("./k8s/")
jaeger_agent.generate().to_yaml("./k8s/")
alertmanager.generate().to_yaml("./k8s/")

# Generate instrumented applications
app.generate().to_yaml("./k8s/")
python_app.generate().to_yaml("./k8s/")
```

### 2. Apply the deployment

```bash
# Apply storage components first
kubectl apply -f k8s/elasticsearch-*.yaml
kubectl apply -f k8s/jaeger-storage-*.yaml
kubectl apply -f k8s/prometheus-*.yaml

# Wait for storage to be ready
kubectl wait --for=condition=ready pod -l app=elasticsearch --timeout=300s
kubectl wait --for=condition=ready pod -l app=jaeger-storage --timeout=300s
kubectl wait --for=condition=ready pod -l app=prometheus --timeout=300s

# Apply monitoring components
kubectl apply -f k8s/grafana-*.yaml
kubectl apply -f k8s/kibana-*.yaml
kubectl apply -f k8s/fluentd-*.yaml
kubectl apply -f k8s/jaeger-*.yaml
kubectl apply -f k8s/alertmanager-*.yaml

# Apply applications
kubectl apply -f k8s/instrumented-app-*.yaml
kubectl apply -f k8s/python-app-*.yaml

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods
```

### 3. Access the dashboards

```bash
# Access Grafana
kubectl port-forward service/grafana 3000:3000
# Open http://localhost:3000 (admin/admin123)

# Access Kibana
kubectl port-forward service/kibana 5601:5601
# Open http://localhost:5601

# Access Jaeger
kubectl port-forward service/jaeger-query 16686:16686
# Open http://localhost:16686

# Access Prometheus
kubectl port-forward service/prometheus 9090:9090
# Open http://localhost:9090

# Access AlertManager
kubectl port-forward service/alertmanager 9093:9093
# Open http://localhost:9093
```

## Dashboard Configuration

### 1. Grafana Dashboards

```python
# Kubernetes cluster dashboard
k8s_dashboard = (ConfigMap("k8s-dashboard")
    .add("kubernetes-cluster.json", """
{
    "dashboard": {
        "title": "Kubernetes Cluster",
        "panels": [
            {
                "title": "CPU Usage",
                "type": "graph",
                "targets": [
                    {
                        "expr": "100 - (avg by(instance) (irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
                    }
                ]
            },
            {
                "title": "Memory Usage",
                "type": "graph",
                "targets": [
                    {
                        "expr": "(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100"
                    }
                ]
            }
        ]
    }
}""")
    .mount_as_file("/var/lib/grafana/dashboards/kubernetes-cluster.json"))

grafana.add_config(k8s_dashboard)
```

### 2. Application Dashboards

```python
# Application metrics dashboard
app_dashboard = (ConfigMap("app-dashboard")
    .add("application-metrics.json", """
{
    "dashboard": {
        "title": "Application Metrics",
        "panels": [
            {
                "title": "Request Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(http_requests_total[5m])"
                    }
                ]
            },
            {
                "title": "Error Rate",
                "type": "graph",
                "targets": [
                    {
                        "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
                    }
                ]
            },
            {
                "title": "Response Time",
                "type": "graph",
                "targets": [
                    {
                        "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
                    }
                ]
            }
        ]
    }
}""")
    .mount_as_file("/var/lib/grafana/dashboards/application-metrics.json"))

grafana.add_config(app_dashboard)
```

## Best Practices

### 1. **Resource Limits**
```python
# ✅ Good: Set appropriate resource limits
prometheus = StatefulApp("prometheus").resources(cpu="500m", memory="1Gi")

# ❌ Bad: No resource limits
prometheus = StatefulApp("prometheus")  # No resource limits
```

### 2. **Persistent Storage**
```python
# ✅ Good: Use persistent storage for data
elasticsearch = StatefulApp("elasticsearch").storage("100Gi")

# ❌ Bad: No persistent storage
elasticsearch = App("elasticsearch")  # No persistent storage
```

### 3. **High Availability**
```python
# ✅ Good: Multiple replicas for HA
grafana = App("grafana").replicas(2)
kibana = App("kibana").replicas(2)

# ❌ Bad: Single replica
grafana = App("grafana").replicas(1)  # Single point of failure
```

### 4. **Security**
```python
# ✅ Good: Use secrets for sensitive data
alertmanager = App("alertmanager").add_secret(Secret("smtp-secret"))

# ❌ Bad: Hardcode sensitive data
alertmanager = App("alertmanager").environment({"SMTP_PASSWORD": "password"})
```

## Next Steps

1. **[Production Deployments](../examples/production/index.md)** - Learn about production configurations
2. **[Complex Platforms](../examples/complex/index.md)** - Advanced multi-service platforms
3. **[Microservices Tutorial](microservices.md)** - Build microservices architecture

Ready to deploy to production? Check out the [Production Deployments](../examples/production/index.md)! 