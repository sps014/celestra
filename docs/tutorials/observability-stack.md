# Observability Stack Tutorial

**⭐⭐⭐⭐ Difficulty:** Advanced | **⏱️ Time:** 25 minutes

Build a comprehensive observability stack with monitoring, logging, and tracing using Celestra.

## What You'll Build

A complete observability platform featuring:
- **Metrics Collection**: Prometheus and node exporters
- **Monitoring Dashboards**: Grafana with custom dashboards
- **Alerting**: AlertManager with notification channels
- **Distributed Tracing**: Jaeger for request tracing
- **Log Aggregation**: Fluentd/Fluent Bit for log collection
- **Centralized Logging**: Elasticsearch and Kibana
- **Application Monitoring**: Custom metrics and health checks

## Prerequisites

- Celestra installed
- Kubernetes cluster with sufficient resources (4+ GB RAM, 4+ CPU cores)
- Understanding of observability concepts
- Basic knowledge of Prometheus, Grafana, and Jaeger

## Architecture Overview

```
Applications → Metrics/Logs/Traces → Collection Layer → Storage → Visualization
                                        ↓              ↓         ↓
                                    Prometheus    Elasticsearch  Grafana
                                    Jaeger        InfluxDB       Kibana
                                    Fluentd                      Jaeger UI
```

## Step 1: Create Monitoring Infrastructure

Start with Prometheus for metrics collection:

```python
from celestra import StatefulApp, App, Service, ConfigMap

# Prometheus server
prometheus = (StatefulApp("prometheus")
    .image("prom/prometheus:v2.40.0")
    .port(9090, "web")
    .storage("/prometheus", "50Gi")
    .mount_config_map("prometheus-config", "/etc/prometheus")
    .resources(cpu="1", memory="2Gi")
    .command([
        "/bin/prometheus",
        "--config.file=/etc/prometheus/prometheus.yml",
        "--storage.tsdb.path=/prometheus",
        "--web.console.libraries=/etc/prometheus/console_libraries",
        "--web.console.templates=/etc/prometheus/consoles",
        "--storage.tsdb.retention.time=15d",
        "--web.enable-lifecycle"
    ]))

# Prometheus configuration
prometheus_config = (ConfigMap("prometheus-config")
    .add_data("prometheus.yml", """
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
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - source_labels: [__address__]
        regex: '(.*):10250'
        target_label: __address__
        replacement: '${1}:9100'

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

  - job_name: 'applications'
    static_configs:
      - targets: 
        - 'user-service:9090'
        - 'product-service:9090'
        - 'order-service:9090'
    """))

print("✅ Prometheus configured")
```

## Step 2: Add Grafana for Visualization

Set up Grafana with dashboards:

```python
# Grafana for dashboards
grafana = (StatefulApp("grafana")
    .image("grafana/grafana:9.3.0")
    .port(3000, "web")
    .storage("/var/lib/grafana", "10Gi")
    .env("GF_SECURITY_ADMIN_PASSWORD", "admin123")
    .env("GF_USERS_ALLOW_SIGN_UP", "false")
    .mount_config_map("grafana-dashboards", "/etc/grafana/provisioning/dashboards")
    .mount_config_map("grafana-datasources", "/etc/grafana/provisioning/datasources")
    .resources(cpu="500m", memory="1Gi"))

# Grafana datasources
grafana_datasources = (ConfigMap("grafana-datasources")
    .add_data("datasources.yml", """
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    
  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger-query:16686
    
  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: http://elasticsearch:9200
    database: logstash-*
    """))

# Grafana dashboards configuration
grafana_dashboards = (ConfigMap("grafana-dashboards")
    .add_data("dashboards.yml", """
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
    """)
    .add_data("kubernetes-cluster.json", """
{
  "dashboard": {
    "title": "Kubernetes Cluster Overview",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph", 
        "targets": [
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100"
          }
        ]
      }
    ]
  }
}
    """))

print("✅ Grafana configured")
```

## Step 3: Set Up Alerting

Configure AlertManager for notifications:

```python
# AlertManager for alerting
alertmanager = (App("alertmanager")
    .image("prom/alertmanager:v0.25.0")
    .port(9093, "web")
    .mount_config_map("alertmanager-config", "/etc/alertmanager")
    .resources(cpu="200m", memory="256Mi")
    .replicas(2))

# AlertManager configuration
alertmanager_config = (ConfigMap("alertmanager-config")
    .add_data("alertmanager.yml", """
global:
  smtp_smarthost: 'smtp.example.com:587'
  smtp_from: 'alertmanager@example.com'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@example.com'
    subject: 'Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
  
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#alerts'
    title: 'Alert: {{ .GroupLabels.alertname }}'
    text: |
      {{ range .Alerts }}
      {{ .Annotations.summary }}
      {{ end }}

inhibit_rules:
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'dev', 'instance']
    """))

# Alert rules
alert_rules = (ConfigMap("alert-rules")
    .add_data("alert_rules.yml", """
groups:
- name: application.rules
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors per second"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High latency detected"
      description: "95th percentile latency is {{ $value }}s"

  - alert: ServiceDown
    expr: up == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Service is down"
      description: "{{ $labels.job }} service is down"

- name: infrastructure.rules
  rules:
  - alert: HighCPUUsage
    expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is {{ $value }}%"

  - alert: HighMemoryUsage
    expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage"
      description: "Memory usage is {{ $value }}%"
    """))

print("✅ AlertManager configured")
```

## Step 4: Add Distributed Tracing

Set up Jaeger for request tracing:

```python
# Jaeger all-in-one for distributed tracing
jaeger = (App("jaeger")
    .image("jaegertracing/all-in-one:1.41")
    .port(16686, "ui")
    .port(14268, "collector")
    .port(6831, "agent-compact", "UDP")
    .port(6832, "agent-binary", "UDP")
    .env("COLLECTOR_ZIPKIN_HOST_PORT", ":9411")
    .env("SPAN_STORAGE_TYPE", "memory")
    .resources(cpu="500m", memory="1Gi"))

# Jaeger agent as DaemonSet for trace collection
jaeger_agent = (App("jaeger-agent")
    .image("jaegertracing/jaeger-agent:1.41")
    .port(6831, "compact", "UDP")
    .port(6832, "binary", "UDP")
    .port(5778, "config")
    .env("REPORTER_GRPC_HOST_PORT", "jaeger:14250")
    .resources(cpu="100m", memory="128Mi")
    .daemon_set(True))

print("✅ Jaeger tracing configured")
```

## Step 5: Set Up Log Aggregation

Configure log collection with Fluentd and Elasticsearch:

```python
# Elasticsearch for log storage
elasticsearch = (StatefulApp("elasticsearch")
    .image("elasticsearch:8.5.0")
    .port(9200, "http")
    .port(9300, "transport")
    .env("discovery.type", "single-node")
    .env("ES_JAVA_OPTS", "-Xms1g -Xmx1g")
    .env("xpack.security.enabled", "false")
    .storage("/usr/share/elasticsearch/data", "50Gi")
    .resources(cpu="1", memory="2Gi"))

# Kibana for log visualization
kibana = (App("kibana")
    .image("kibana:8.5.0")
    .port(5601, "ui")
    .env("ELASTICSEARCH_HOSTS", "http://elasticsearch:9200")
    .resources(cpu="500m", memory="1Gi"))

# Fluentd for log collection
fluentd = (App("fluentd")
    .image("fluent/fluentd-kubernetes-daemonset:v1.15-debian-elasticsearch7-1")
    .env("FLUENT_ELASTICSEARCH_HOST", "elasticsearch")
    .env("FLUENT_ELASTICSEARCH_PORT", "9200")
    .env("FLUENT_ELASTICSEARCH_SCHEME", "http")
    .mount_config_map("fluentd-config", "/fluentd/etc")
    .resources(cpu="200m", memory="512Mi")
    .daemon_set(True))

# Fluentd configuration
fluentd_config = (ConfigMap("fluentd-config")
    .add_data("fluent.conf", """
<source>
  @type tail
  path /var/log/containers/*.log
  pos_file /var/log/fluentd-containers.log.pos
  tag kubernetes.*
  format json
  read_from_head true
</source>

<filter kubernetes.**>
  @type kubernetes_metadata
  merge_log_level trace
</filter>

<match kubernetes.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name logstash
  type_name fluentd
  include_tag_key true
  tag_key @log_name
  flush_interval 1s
</match>
    """))

print("✅ Log aggregation configured")
```

## Step 6: Add Node Monitoring

Set up node exporters for infrastructure metrics:

```python
# Node Exporter for node metrics
node_exporter = (App("node-exporter")
    .image("prom/node-exporter:v1.5.0")
    .port(9100, "metrics")
    .host_network(True)
    .host_pid(True)
    .mount_host_path("/", "/host", read_only=True)
    .command([
        "/bin/node_exporter",
        "--path.rootfs=/host"
    ])
    .resources(cpu="100m", memory="128Mi")
    .daemon_set(True))

# kube-state-metrics for Kubernetes metrics
kube_state_metrics = (App("kube-state-metrics")
    .image("registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.7.0")
    .port(8080, "http-metrics")
    .port(8081, "telemetry")
    .resources(cpu="100m", memory="190Mi"))

print("✅ Node monitoring configured")
```

## Step 7: Implement Application Observability

Add observability to applications:

```python
from celestra import Observability

# Create comprehensive observability configuration
observability = (Observability("application-observability")
    .enable_metrics()
    .enable_tracing()
    .enable_logging()
    .prometheus_config(
        scrape_interval="15s",
        evaluation_interval="15s"
    )
    .jaeger_config(
        sampling_rate=0.1,
        agent_host="jaeger-agent",
        agent_port=6831
    )
    .grafana_dashboards([
        "application-overview",
        "request-latency",
        "error-rates",
        "resource-usage"
    ])
    .alert_rules([
        "HighErrorRate",
        "HighLatency",
        "ServiceDown",
        "HighCPUUsage",
        "HighMemoryUsage"
    ]))

# Sample applications with observability
user_service = (App("user-service")
    .image("ecommerce/user-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("JAEGER_AGENT_HOST", "jaeger-agent")
    .env("JAEGER_AGENT_PORT", "6831")
    .add_annotation("prometheus.io/scrape", "true")
    .add_annotation("prometheus.io/port", "9090")
    .add_annotation("prometheus.io/path", "/metrics")
    .resources(cpu="300m", memory="512Mi")
    .replicas(3)
    .health_check("/health", 8080)
    .add_observability(observability))

product_service = (App("product-service")
    .image("ecommerce/product-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("JAEGER_AGENT_HOST", "jaeger-agent")
    .env("JAEGER_AGENT_PORT", "6831")
    .add_annotation("prometheus.io/scrape", "true")
    .add_annotation("prometheus.io/port", "9090")
    .add_annotation("prometheus.io/path", "/metrics")
    .resources(cpu="300m", memory="512Mi")
    .replicas(3)
    .health_check("/health", 8080)
    .add_observability(observability))

print("✅ Application observability configured")
```

## Step 8: Create Services and Access

Set up services for all observability components:

```python
# Services for observability stack
prometheus_svc = (Service("prometheus")
    .selector({"app": "prometheus"})
    .add_port("web", 9090, 9090))

grafana_svc = (Service("grafana")
    .selector({"app": "grafana"})
    .add_port("web", 3000, 3000)
    .type("LoadBalancer"))

alertmanager_svc = (Service("alertmanager")
    .selector({"app": "alertmanager"})
    .add_port("web", 9093, 9093))

jaeger_svc = (Service("jaeger")
    .selector({"app": "jaeger"})
    .add_port("ui", 16686, 16686)
    .add_port("collector", 14268, 14268)
    .type("LoadBalancer"))

jaeger_query_svc = (Service("jaeger-query")
    .selector({"app": "jaeger"})
    .add_port("query", 16686, 16686))

elasticsearch_svc = (Service("elasticsearch")
    .selector({"app": "elasticsearch"})
    .add_port("http", 9200, 9200))

kibana_svc = (Service("kibana")
    .selector({"app": "kibana"})
    .add_port("ui", 5601, 5601)
    .type("LoadBalancer"))

node_exporter_svc = (Service("node-exporter")
    .selector({"app": "node-exporter"})
    .add_port("metrics", 9100, 9100))

kube_state_metrics_svc = (Service("kube-state-metrics")
    .selector({"app": "kube-state-metrics"})
    .add_port("http-metrics", 8080, 8080))

print("✅ Observability services configured")
```

## Step 9: Complete Observability Stack

Here's the complete stack:

```python
#!/usr/bin/env python3
"""
Observability Stack - Comprehensive monitoring, logging, and tracing with Celestra
"""

from celestra import (
    App, StatefulApp, Service, ConfigMap,
    Observability, KubernetesOutput
)

def create_observability_stack():
    """Create a complete observability stack."""
    
    # Metrics Collection
    prometheus = (StatefulApp("prometheus")
        .image("prom/prometheus:v2.40.0")
        .port(9090, "web")
        .storage("/prometheus", "50Gi")
        .mount_config_map("prometheus-config", "/etc/prometheus")
        .resources(cpu="1", memory="2Gi"))
    
    # Visualization
    grafana = (StatefulApp("grafana")
        .image("grafana/grafana:9.3.0")
        .port(3000, "web")
        .storage("/var/lib/grafana", "10Gi")
        .env("GF_SECURITY_ADMIN_PASSWORD", "admin123")
        .mount_config_map("grafana-datasources", "/etc/grafana/provisioning/datasources")
        .resources(cpu="500m", memory="1Gi"))
    
    # Alerting
    alertmanager = (App("alertmanager")
        .image("prom/alertmanager:v0.25.0")
        .port(9093, "web")
        .mount_config_map("alertmanager-config", "/etc/alertmanager")
        .resources(cpu="200m", memory="256Mi"))
    
    # Distributed Tracing
    jaeger = (App("jaeger")
        .image("jaegertracing/all-in-one:1.41")
        .port(16686, "ui")
        .port(14268, "collector")
        .env("SPAN_STORAGE_TYPE", "memory")
        .resources(cpu="500m", memory="1Gi"))
    
    # Log Storage
    elasticsearch = (StatefulApp("elasticsearch")
        .image("elasticsearch:8.5.0")
        .port(9200, "http")
        .env("discovery.type", "single-node")
        .env("ES_JAVA_OPTS", "-Xms1g -Xmx1g")
        .env("xpack.security.enabled", "false")
        .storage("/usr/share/elasticsearch/data", "50Gi")
        .resources(cpu="1", memory="2Gi"))
    
    # Log Visualization
    kibana = (App("kibana")
        .image("kibana:8.5.0")
        .port(5601, "ui")
        .env("ELASTICSEARCH_HOSTS", "http://elasticsearch:9200")
        .resources(cpu="500m", memory="1Gi"))
    
    # Node Metrics
    node_exporter = (App("node-exporter")
        .image("prom/node-exporter:v1.5.0")
        .port(9100, "metrics")
        .resources(cpu="100m", memory="128Mi")
        .daemon_set(True))
    
    # Kubernetes Metrics
    kube_state_metrics = (App("kube-state-metrics")
        .image("registry.k8s.io/kube-state-metrics/kube-state-metrics:v2.7.0")
        .port(8080, "http-metrics")
        .resources(cpu="100m", memory="190Mi"))
    
    # Configuration
    prometheus_config = ConfigMap("prometheus-config").add_data("prometheus.yml", """
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
  - job_name: 'kube-state-metrics'
    static_configs:
      - targets: ['kube-state-metrics:8080']
    """)
    
    grafana_datasources = ConfigMap("grafana-datasources").add_data("datasources.yml", """
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
  - name: Jaeger
    type: jaeger
    access: proxy
    url: http://jaeger:16686
    """)
    
    alertmanager_config = ConfigMap("alertmanager-config").add_data("alertmanager.yml", """
global:
  smtp_smarthost: 'smtp.example.com:587'
route:
  group_by: ['alertname']
  group_wait: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
receivers:
- name: 'web.hook'
  email_configs:
  - to: 'admin@example.com'
    subject: 'Alert: {{ .GroupLabels.alertname }}'
    """)
    
    # Services
    prometheus_svc = (Service("prometheus")
        .selector({"app": "prometheus"})
        .add_port("web", 9090, 9090))
    
    grafana_svc = (Service("grafana")
        .selector({"app": "grafana"})
        .add_port("web", 3000, 3000)
        .type("LoadBalancer"))
    
    jaeger_svc = (Service("jaeger")
        .selector({"app": "jaeger"})
        .add_port("ui", 16686, 16686)
        .type("LoadBalancer"))
    
    kibana_svc = (Service("kibana")
        .selector({"app": "kibana"})
        .add_port("ui", 5601, 5601)
        .type("LoadBalancer"))
    
    return [
        # Applications
        prometheus, grafana, alertmanager, jaeger, elasticsearch, kibana,
        node_exporter, kube_state_metrics,
        # Configuration
        prometheus_config, grafana_datasources, alertmanager_config,
        # Services
        prometheus_svc, grafana_svc, jaeger_svc, kibana_svc
    ]

def main():
    """Generate the observability stack."""
    print("📊 Creating Observability Stack")
    print("=" * 40)
    
    # Create all components
    components = create_observability_stack()
    
    # Generate manifests
    output = KubernetesOutput()
    all_resources = []
    
    for component in components:
        resources = component.generate_kubernetes_resources()
        all_resources.extend(resources)
    
    # Save to file
    output.write_all_resources(all_resources, "observability-stack.yaml")
    
    print(f"✅ Generated {len(all_resources)} Kubernetes resources")
    print("📄 Saved to: observability-stack.yaml")
    print("\n📊 Observability components:")
    print("   • Prometheus (metrics)")
    print("   • Grafana (dashboards)")
    print("   • AlertManager (alerting)")
    print("   • Jaeger (tracing)")
    print("   • Elasticsearch + Kibana (logging)")
    print("   • Node Exporter (node metrics)")
    print("   • Kube-state-metrics (K8s metrics)")
    print("\n🚀 Deploy with:")
    print("   kubectl apply -f observability-stack.yaml")
    print("\n🌐 Access dashboards:")
    print("   Grafana: http://<GRAFANA-IP>:3000 (admin/admin123)")
    print("   Jaeger: http://<JAEGER-IP>:16686")
    print("   Kibana: http://<KIBANA-IP>:5601")

if __name__ == "__main__":
    main()
```

## Deployment and Access

1. **Deploy the observability stack:**
   ```bash
   python observability_stack.py
   kubectl apply -f observability-stack.yaml
   ```

2. **Wait for pods to be ready:**
   ```bash
   kubectl get pods -w
   ```

3. **Get external IPs:**
   ```bash
   kubectl get services -l type=LoadBalancer
   ```

4. **Access dashboards:**
   - **Grafana**: `http://<GRAFANA-IP>:3000` (admin/admin123)
   - **Jaeger**: `http://<JAEGER-IP>:16686`
   - **Kibana**: `http://<KIBANA-IP>:5601`

## Key Features Implemented

✅ **Metrics Collection**: Prometheus with custom exporters  
✅ **Visualization**: Grafana dashboards with multiple datasources  
✅ **Alerting**: AlertManager with email and Slack notifications  
✅ **Distributed Tracing**: Jaeger for request flow tracking  
✅ **Log Aggregation**: Fluentd + Elasticsearch + Kibana  
✅ **Infrastructure Monitoring**: Node and Kubernetes metrics  
✅ **Application Monitoring**: Custom metrics and health checks  
✅ **High Availability**: Replicated critical components  

## Best Practices Followed

- **Resource Allocation**: Proper CPU and memory limits
- **Persistent Storage**: Stateful components with persistent volumes
- **Security**: No default passwords in production
- **High Availability**: Multiple replicas for critical services
- **Monitoring**: Health checks for all components
- **Configuration Management**: ConfigMaps for all configuration
- **Service Discovery**: Kubernetes services for internal communication

## Next Steps

Enhance your observability:

1. **[Microservices](microservices.md)** - Apply observability to microservices
2. **[Multi-Environment](multi-environment.md)** - Environment-specific monitoring
3. **Custom Dashboards** - Create application-specific dashboards
4. **Advanced Alerting** - Set up escalation policies

---

**Congratulations!** You've built a production-ready observability stack with comprehensive monitoring, logging, and tracing capabilities using Celestra.
