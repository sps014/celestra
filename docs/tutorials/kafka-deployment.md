# Kafka Deployment Tutorial

This tutorial will guide you through deploying a production-ready Apache Kafka cluster using Celestra, including ZooKeeper, monitoring, and best practices.

## 🎯 What You'll Build

By the end of this tutorial, you'll have:

- **Apache Kafka cluster** with 3 brokers
- **Apache ZooKeeper** ensemble for coordination
- **Monitoring stack** with Prometheus and Grafana
- **Kafka UI** for management
- **Proper security** with RBAC and network policies

## 📋 Prerequisites

Before starting, ensure you have:

- Celestra installed (`pip install celestra`)
- A Kubernetes cluster (minikube, kind, or cloud)
- kubectl configured
- At least 4GB of available memory

## 🚀 Step 1: Basic Kafka Setup

Let's start with a basic Kafka deployment:

```python
from celestra import StatefulApp, ConfigMap, Secret

# ZooKeeper configuration
zookeeper_config = (ConfigMap("zookeeper-config")
    .add("dataDir", "/var/lib/zookeeper/data")
    .add("clientPort", "2181")
    .add("maxClientCnxns", "60")
    .add("tickTime", "2000")
    .add("initLimit", "10")
    .add("syncLimit", "5"))

# Kafka configuration
kafka_config = (ConfigMap("kafka-config")
    .add("broker.id", "0")
    .add("listeners", "PLAINTEXT://:9092")
    .add("advertised.listeners", "PLAINTEXT://kafka-0.kafka-headless:9092")
    .add("log.dirs", "/var/lib/kafka/data")
    .add("zookeeper.connect", "zookeeper-0.zookeeper-headless:2181")
    .add("num.partitions", "3")
    .add("default.replication.factor", "3")
    .add("min.insync.replicas", "2")
    .add("offsets.topic.replication.factor", "3")
    .add("transaction.state.log.replication.factor", "3")
    .add("transaction.state.log.min.isr", "2"))

# ZooKeeper StatefulSet
zookeeper = (StatefulApp("zookeeper")
    .image("confluentinc/cp-zookeeper:7.4.0")
    .port(2181)
    .storage("10Gi")
    .replicas(3)
    .add_config(zookeeper_config)
    .env("ZOOKEEPER_CLIENT_PORT", "2181")
    .env("ZOOKEEPER_TICK_TIME", "2000")
    .env("ZOOKEEPER_INIT_LIMIT", "10")
    .env("ZOOKEEPER_SYNC_LIMIT", "5"))

# Kafka StatefulSet
kafka = (StatefulApp("kafka")
    .image("confluentinc/cp-kafka:7.4.0")
    .kafka_port(9092)
    .storage("100Gi")
    .replicas(3)
    .add_config(kafka_config)
    .env("KAFKA_ZOOKEEPER_CONNECT", "zookeeper-0.zookeeper-headless:2181")
    .env("KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR", "3")
    .env("KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR", "3")
    .env("KAFKA_TRANSACTION_STATE_LOG_MIN_ISR", "2"))

# Generate manifests
zookeeper.generate().to_yaml("./kafka/")
kafka.generate().to_yaml("./kafka/")
zookeeper_config.generate().to_yaml("./kafka/")
kafka_config.generate().to_yaml("./kafka/")
```

## 🔒 Step 2: Add Security

Now let's add security features:

```python
from celestra import Secret, ServiceAccount, Role, RoleBinding, NetworkPolicy

# Kafka credentials
kafka_secret = (Secret("kafka-secret")
    .add("username", "kafka-user")
    .add("password", "secure-kafka-password"))

# Service accounts
kafka_sa = ServiceAccount("kafka-sa")
zookeeper_sa = ServiceAccount("zookeeper-sa")

# RBAC roles
kafka_role = (Role("kafka-role")
    .add_policy("get", "pods")
    .add_policy("get", "services")
    .add_policy("list", "endpoints"))

zookeeper_role = (Role("zookeeper-role")
    .add_policy("get", "pods")
    .add_policy("get", "services"))

# Role bindings
kafka_binding = RoleBinding("kafka-binding").bind_role(kafka_role).bind_service_account(kafka_sa)
zookeeper_binding = RoleBinding("zookeeper-binding").bind_role(zookeeper_role).bind_service_account(zookeeper_sa)

# Network policies
kafka_network_policy = (NetworkPolicy("kafka-network-policy")
    .allow_pods_with_label("app", "kafka")
    .allow_pods_with_label("app", "zookeeper")
    .deny_all())

zookeeper_network_policy = (NetworkPolicy("zookeeper-network-policy")
    .allow_pods_with_label("app", "zookeeper")
    .deny_all())

# Update applications with security
kafka = (kafka
    .add_service_account(kafka_sa)
    .add_secret(kafka_secret)
    .add_network_policy(kafka_network_policy))

zookeeper = (zookeeper
    .add_service_account(zookeeper_sa)
    .add_network_policy(zookeeper_network_policy))

# Generate security manifests
kafka_secret.generate().to_yaml("./kafka/")
kafka_sa.generate().to_yaml("./kafka/")
zookeeper_sa.generate().to_yaml("./kafka/")
kafka_role.generate().to_yaml("./kafka/")
zookeeper_role.generate().to_yaml("./kafka/")
kafka_binding.generate().to_yaml("./kafka/")
zookeeper_binding.generate().to_yaml("./kafka/")
kafka_network_policy.generate().to_yaml("./kafka/")
zookeeper_network_policy.generate().to_yaml("./kafka/")
```

## 📊 Step 3: Add Monitoring

Let's add monitoring with Prometheus and Grafana:

```python
from celestra import App, Observability

# Prometheus configuration
prometheus_config = (ConfigMap("prometheus-config")
    .add_yaml("prometheus.yml", """
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-0.kafka-headless:9092', 'kafka-1.kafka-headless:9092', 'kafka-2.kafka-headless:9092']
  - job_name: 'zookeeper'
    static_configs:
      - targets: ['zookeeper-0.zookeeper-headless:2181', 'zookeeper-1.zookeeper-headless:2181', 'zookeeper-2.zookeeper-headless:2181']
"""))

# Prometheus
prometheus = (App("prometheus")
    .image("prom/prometheus:latest")
    .port(9090)
    .add_config(prometheus_config)
    .resources(cpu="500m", memory="1Gi")
    .expose())

# Grafana
grafana = (App("grafana")
    .image("grafana/grafana:latest")
    .port(3000)
    .env("GF_SECURITY_ADMIN_PASSWORD", "admin")
    .env("GF_INSTALL_PLUGINS", "grafana-kafka-datasource")
    .resources(cpu="200m", memory="512Mi")
    .expose())

# Kafka UI for management
kafka_ui = (App("kafka-ui")
    .image("provectuslabs/kafka-ui:latest")
    .port(8080)
    .env("KAFKA_CLUSTERS_0_NAME", "local")
    .env("KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS", "kafka-0.kafka-headless:9092")
    .env("KAFKA_CLUSTERS_0_ZOOKEEPER", "zookeeper-0.zookeeper-headless:2181")
    .resources(cpu="100m", memory="256Mi")
    .expose())

# Generate monitoring manifests
prometheus.generate().to_yaml("./kafka/")
grafana.generate().to_yaml("./kafka/")
kafka_ui.generate().to_yaml("./kafka/")
prometheus_config.generate().to_yaml("./kafka/")
```

## 🔧 Step 4: Advanced Configuration

Let's add advanced features like backup scheduling and resource optimization:

```python
from celestra import CostOptimization, DeploymentStrategy

# Backup configuration
backup_config = (ConfigMap("kafka-backup-config")
    .add("backup_schedule", "0 2 * * *")  # Daily at 2 AM
    .add("retention_days", "7")
    .add("backup_location", "s3://kafka-backups"))

# Add backup scheduling to Kafka
kafka = (kafka
    .backup_schedule("0 2 * * *")
    .add_config(backup_config)
    .deployment_strategy("rolling")
    .health_check("/health")
    .liveness_probe("/health")
    .readiness_probe("/ready"))

# Cost optimization
optimizer = CostOptimization("kafka-optimizer")
optimizer.resource_optimization()
optimizer.storage_optimization()
optimizer.spot_instance_recommendation()

# Add observability
observability = Observability("kafka-monitoring")
observability.enable_metrics()
observability.enable_logging()
observability.enable_tracing()

kafka = kafka.add_observability(observability)
```

## 🚀 Step 5: Deploy Everything

Now let's create a complete deployment script:

```python
# Complete Kafka deployment
from celestra import AppGroup

# Create application group
kafka_platform = AppGroup("kafka-platform")

# Add all components
kafka_platform.add([
    zookeeper_config,
    kafka_config,
    backup_config,
    prometheus_config,
    zookeeper,
    kafka,
    prometheus,
    grafana,
    kafka_ui,
    kafka_secret,
    kafka_sa,
    zookeeper_sa,
    kafka_role,
    zookeeper_role,
    kafka_binding,
    zookeeper_binding,
    kafka_network_policy,
    zookeeper_network_policy
])

# Generate all manifests
kafka_platform.generate().to_yaml("./kafka/")

print("✅ Kafka platform manifests generated in ./kafka/")
```

## 🎯 Step 6: Deploy and Verify

Deploy the Kafka platform:

```bash
# Deploy to Kubernetes
kubectl apply -f ./kafka/

# Check deployment status
kubectl get pods -l app=kafka
kubectl get pods -l app=zookeeper
kubectl get services

# Check logs
kubectl logs -l app=kafka
kubectl logs -l app=zookeeper
```

## 🔍 Step 7: Test the Deployment

### Test Kafka Connectivity

```python
# Test script
from kafka import KafkaProducer, KafkaConsumer
import json

# Producer test
producer = KafkaProducer(
    bootstrap_servers=['kafka-0.kafka-headless:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

producer.send('test-topic', {'message': 'Hello Kafka!'})
producer.flush()

# Consumer test
consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers=['kafka-0.kafka-headless:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(f"Received: {message.value}")
    break
```

### Access the UI

```bash
# Port forward Kafka UI
kubectl port-forward svc/kafka-ui 8080:8080

# Port forward Grafana
kubectl port-forward svc/grafana 3000:3000

# Access in browser:
# Kafka UI: http://localhost:8080
# Grafana: http://localhost:3000 (admin/admin)
```

## 📊 Monitoring and Metrics

### Key Metrics to Monitor

1. **Kafka Metrics:**
   - Messages per second
   - Consumer lag
   - Partition count
   - Replication factor

2. **ZooKeeper Metrics:**
   - Connection count
   - Request latency
   - Node count

3. **System Metrics:**
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

### Grafana Dashboards

Import these dashboard IDs in Grafana:
- Kafka: `7589`
- ZooKeeper: `10466`
- System: `1860`

## 🔧 Troubleshooting

### Common Issues

**1. ZooKeeper Connection Issues**
```bash
# Check ZooKeeper status
kubectl exec -it zookeeper-0 -- zkServer.sh status

# Check logs
kubectl logs zookeeper-0
```

**2. Kafka Broker Issues**
```bash
# Check Kafka status
kubectl exec -it kafka-0 -- kafka-topics --bootstrap-server localhost:9092 --list

# Check logs
kubectl logs kafka-0
```

**3. Network Policy Issues**
```bash
# Check network policies
kubectl get networkpolicies

# Test connectivity
kubectl exec -it kafka-0 -- nc -zv zookeeper-0.zookeeper-headless 2181
```

### Performance Tuning

```python
# Optimize for high throughput
kafka = (kafka
    .resources(cpu="2000m", memory="4Gi")
    .env("KAFKA_NUM_NETWORK_THREADS", "8")
    .env("KAFKA_NUM_IO_THREADS", "8")
    .env("KAFKA_SOCKET_SEND_BUFFER_BYTES", "102400")
    .env("KAFKA_SOCKET_RECEIVE_BUFFER_BYTES", "102400")
    .env("KAFKA_SOCKET_REQUEST_MAX_BYTES", "104857600"))
```

## 🎯 Production Considerations

### 1. **Persistence**
- Use SSD storage for better performance
- Configure proper backup strategies
- Monitor disk usage

### 2. **Security**
- Enable TLS encryption
- Use SASL authentication
- Implement network policies

### 3. **Scaling**
- Monitor partition count
- Scale based on throughput
- Use auto-scaling policies

### 4. **Monitoring**
- Set up alerting
- Monitor consumer lag
- Track broker health

## 🚀 Next Steps

Now that you have a working Kafka cluster, explore:

- **[Multi-Environment Tutorial](multi-environment.md)** - Deploy to different environments
- **[RBAC Security Tutorial](../components/security/rbac.md)** - Advanced security configuration
- **[Microservices Tutorial](microservices.md)** - Build complete microservices platforms
- **[Observability Stack Tutorial](observability-stack.md)** - Advanced monitoring setup

Ready to build more complex systems? Check out the [Microservices Tutorial](microservices.md) or [Observability Stack Tutorial](observability-stack.md)! 