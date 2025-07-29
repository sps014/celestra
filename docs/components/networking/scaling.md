# Scaling Class

The `Scaling` class manages autoscaling configurations in Kubernetes. It provides horizontal pod autoscaling (HPA), vertical pod autoscaling (VPA), and cluster autoscaling capabilities for optimal resource utilization.

## Overview

```python
from celestra import Scaling

# Basic horizontal pod autoscaler
scaling = Scaling("app-hpa").target_cpu_utilization(70).min_replicas(2).max_replicas(10)

# Production autoscaling with multiple metrics
scaling = (Scaling("production-hpa")
    .target_cpu_utilization(70)
    .target_memory_utilization(80)
    .min_replicas(3)
    .max_replicas(20)
    .scale_up_delay(60)
    .scale_down_delay(300))
```

## Core API Functions

### Horizontal Pod Autoscaler (HPA)

#### Horizontal Pod Autoscaler
Configure horizontal pod autoscaler.

```python
scaling = Scaling("app-hpa").horizontal_pod_autoscaler()
```

#### Target CPU Utilization
Set target CPU utilization percentage.

```python
# 70% CPU utilization target
scaling = Scaling("app-hpa").target_cpu_utilization(70)

# 50% CPU utilization target
scaling = Scaling("app-hpa").target_cpu_utilization(50)
```

#### Target Memory Utilization
Set target memory utilization percentage.

```python
# 80% memory utilization target
scaling = Scaling("app-hpa").target_memory_utilization(80)

# 60% memory utilization target
scaling = Scaling("app-hpa").target_memory_utilization(60)
```

#### Minimum Replicas
Set minimum number of replicas.

```python
# Minimum 2 replicas
scaling = Scaling("app-hpa").min_replicas(2)

# Minimum 5 replicas for high availability
scaling = Scaling("app-hpa").min_replicas(5)
```

#### Maximum Replicas
Set maximum number of replicas.

```python
# Maximum 10 replicas
scaling = Scaling("app-hpa").max_replicas(10)

# Maximum 50 replicas for high traffic
scaling = Scaling("app-hpa").max_replicas(50)
```

#### Scale Up Delay
Set scale up delay in seconds.

```python
# 60 second scale up delay
scaling = Scaling("app-hpa").scale_up_delay(60)

# 30 second scale up delay for responsive scaling
scaling = Scaling("app-hpa").scale_up_delay(30)
```

#### Scale Down Delay
Set scale down delay in seconds.

```python
# 300 second scale down delay
scaling = Scaling("app-hpa").scale_down_delay(300)

# 600 second scale down delay for stability
scaling = Scaling("app-hpa").scale_down_delay(600)
```

### Vertical Pod Autoscaler (VPA)

#### Vertical Pod Autoscaler
Configure vertical pod autoscaler.

```python
scaling = Scaling("app-vpa").vertical_pod_autoscaler()
```

#### VPA Mode
Set VPA mode (Auto, Initial, Off).

```python
# Auto mode - automatically adjust resources
scaling = Scaling("app-vpa").vpa_mode("Auto")

# Initial mode - only set initial requests
scaling = Scaling("app-vpa").vpa_mode("Initial")

# Off mode - only provide recommendations
scaling = Scaling("app-vpa").vpa_mode("Off")
```

#### VPA Update Policy
Set VPA update policy.

```python
# Automatic updates
scaling = Scaling("app-vpa").vpa_update_policy("Auto")

# Manual updates only
scaling = Scaling("app-vpa").vpa_update_policy("Manual")
```

#### VPA Minimum Allowed CPU
Set minimum allowed CPU.

```python
scaling = Scaling("app-vpa").vpa_min_allowed_cpu("100m")
```

#### VPA Maximum Allowed CPU
Set maximum allowed CPU.

```python
scaling = Scaling("app-vpa").vpa_max_allowed_cpu("2")
```

#### VPA Minimum Allowed Memory
Set minimum allowed memory.

```python
scaling = Scaling("app-vpa").vpa_min_allowed_memory("128Mi")
```

#### VPA Maximum Allowed Memory
Set maximum allowed memory.

```python
scaling = Scaling("app-vpa").vpa_max_allowed_memory("4Gi")
```

### Custom Metrics

#### Add Custom Metric
Add custom metric for scaling.

```python
# Custom metric for queue length
scaling = Scaling("app-hpa").add_custom_metric("queue_length", "10", "AverageValue")

# Custom metric for response time
scaling = Scaling("app-hpa").add_custom_metric("response_time", "100ms", "AverageValue")
```

#### Add Prometheus Metric
Add Prometheus metric for scaling.

```python
# Prometheus metric for request rate
scaling = Scaling("app-hpa").add_prometheus_metric("http_requests_total", "1000")
```

#### Add External Metric
Add external metric for scaling.

```python
# External metric for database connections
scaling = Scaling("app-hpa").add_external_metric("database_connections", "50")
```

### Cluster Autoscaling

#### Cluster Autoscaler
Configure cluster autoscaler.

```python
scaling = Scaling("cluster-autoscaler").cluster_autoscaler()
```

#### Scale Down Enabled
Enable or disable scale down.

```python
# Enable scale down
scaling = Scaling("cluster-autoscaler").scale_down_enabled(True)

# Disable scale down
scaling = Scaling("cluster-autoscaler").scale_down_enabled(False)
```

#### Scale Down Delay After Add
Set delay after adding nodes before scaling down.

```python
# 10 minute delay
scaling = Scaling("cluster-autoscaler").scale_down_delay_after_add(600)
```

#### Scale Down Unneeded Time
Set time before scaling down unneeded nodes.

```python
# 10 minute unneeded time
scaling = Scaling("cluster-autoscaler").scale_down_unneeded_time(600)
```

#### Max Node Provision Time
Set maximum time to provision new nodes.

```python
# 15 minute provision time
scaling = Scaling("cluster-autoscaler").max_node_provision_time(900)
```

### Node Group Configuration

#### Node Group
Configure node group for autoscaling.

```python
# Node group configuration
scaling = Scaling("cluster-autoscaler").node_group("app-nodes", 3, 10)
```

#### Add Node Group
Add node group for autoscaling.

```python
# Add multiple node groups
scaling = (Scaling("cluster-autoscaler")
    .add_node_group("app-nodes", 3, 10)
    .add_node_group("db-nodes", 2, 5))
```

#### Node Group Labels
Set labels for node group.

```python
labels = {
    "node-type": "app",
    "environment": "production"
}
scaling = Scaling("cluster-autoscaler").node_group_labels(labels)
```

#### Node Group Taints
Set taints for node group.

```python
taints = [{
    "key": "dedicated",
    "value": "app",
    "effect": "NoSchedule"
}]
scaling = Scaling("cluster-autoscaler").node_group_taints(taints)
```

### Advanced Configuration

#### Namespace
Set the namespace for the scaling configuration.

```python
scaling = Scaling("app-hpa").namespace("production")
```

#### Add Label
Add a label to the scaling configuration.

```python
scaling = Scaling("app-hpa").add_label("environment", "production")
```

#### Add Labels
Add multiple labels to the scaling configuration.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "autoscaling"
}
scaling = Scaling("app-hpa").add_labels(labels)
```

#### Add Annotation
Add an annotation to the scaling configuration.

```python
scaling = Scaling("app-hpa").add_annotation("description", "Application autoscaler")
```

#### Add Annotations
Add multiple annotations to the scaling configuration.

```python
annotations = {
    "description": "Application autoscaler for production",
    "owner": "platform-team",
    "scale-policy": "conservative"
}
scaling = Scaling("app-hpa").add_annotations(annotations)
```

#### Behavior
Set scaling behavior configuration.

```python
behavior = {
    "scaleUp": {
        "stabilizationWindowSeconds": 60,
        "policies": [{
            "type": "Pods",
            "value": 2,
            "periodSeconds": 60
        }]
    },
    "scaleDown": {
        "stabilizationWindowSeconds": 300,
        "policies": [{
            "type": "Pods",
            "value": 1,
            "periodSeconds": 60
        }]
    }
}
scaling = Scaling("app-hpa").behavior(behavior)
```

#### Metrics Interval
Set metrics collection interval.

```python
# 30 second metrics interval
scaling = Scaling("app-hpa").metrics_interval(30)
```

#### Sync Period
Set sync period for autoscaler.

```python
# 15 second sync period
scaling = Scaling("app-hpa").sync_period(15)
```

### Output Generation

#### Generate
Generate the scaling configuration.

```python
# Generate Kubernetes YAML
scaling.generate().to_yaml("./k8s/")

# Generate Helm values
scaling.generate().to_helm_values("./helm/")

# Generate Terraform
scaling.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready scaling configuration:

```python
from celestra import Scaling

# Create comprehensive scaling configuration
production_scaling = (Scaling("production-hpa")
    .horizontal_pod_autoscaler()
    .target_cpu_utilization(70)
    .target_memory_utilization(80)
    .min_replicas(3)
    .max_replicas(20)
    .scale_up_delay(60)
    .scale_down_delay(300)
    .add_custom_metric("queue_length", "10", "AverageValue")
    .add_prometheus_metric("http_requests_total", "1000")
    .behavior({
        "scaleUp": {
            "stabilizationWindowSeconds": 60,
            "policies": [{
                "type": "Pods",
                "value": 2,
                "periodSeconds": 60
            }]
        },
        "scaleDown": {
            "stabilizationWindowSeconds": 300,
            "policies": [{
                "type": "Pods",
                "value": 1,
                "periodSeconds": 60
            }]
        }
    })
    .metrics_interval(30)
    .sync_period(15)
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "autoscaling"
    })
    .add_annotations({
        "description": "Production autoscaler",
        "owner": "platform-team@company.com",
        "scale-policy": "conservative"
    }))

# Generate manifests
production_scaling.generate().to_yaml("./k8s/")
```

## Scaling Patterns

### Conservative Scaling Pattern
```python
# Conservative scaling for stability
conservative_scaling = (Scaling("app-hpa")
    .target_cpu_utilization(70)
    .target_memory_utilization(80)
    .min_replicas(3)
    .max_replicas(10)
    .scale_up_delay(120)
    .scale_down_delay(600))
```

### Aggressive Scaling Pattern
```python
# Aggressive scaling for responsiveness
aggressive_scaling = (Scaling("app-hpa")
    .target_cpu_utilization(50)
    .target_memory_utilization(60)
    .min_replicas(2)
    .max_replicas(50)
    .scale_up_delay(30)
    .scale_down_delay(180))
```

### High Availability Scaling Pattern
```python
# High availability scaling
ha_scaling = (Scaling("app-hpa")
    .target_cpu_utilization(60)
    .target_memory_utilization(70)
    .min_replicas(5)
    .max_replicas(30)
    .scale_up_delay(60)
    .scale_down_delay(300))
```

### VPA Pattern
```python
# Vertical pod autoscaler
vpa_scaling = (Scaling("app-vpa")
    .vertical_pod_autoscaler()
    .vpa_mode("Auto")
    .vpa_update_policy("Auto")
    .vpa_min_allowed_cpu("100m")
    .vpa_max_allowed_cpu("2")
    .vpa_min_allowed_memory("128Mi")
    .vpa_max_allowed_memory("4Gi"))
```

### Cluster Autoscaling Pattern
```python
# Cluster autoscaler
cluster_scaling = (Scaling("cluster-autoscaler")
    .cluster_autoscaler()
    .scale_down_enabled(True)
    .scale_down_delay_after_add(600)
    .scale_down_unneeded_time(600)
    .max_node_provision_time(900)
    .add_node_group("app-nodes", 3, 10)
    .add_node_group("db-nodes", 2, 5))
```

## Best Practices

### 1. **Set Appropriate Target Utilization**
```python
# ✅ Good: Conservative target utilization
scaling = Scaling("app-hpa").target_cpu_utilization(70).target_memory_utilization(80)

# ❌ Bad: Too aggressive target utilization
scaling = Scaling("app-hpa").target_cpu_utilization(90).target_memory_utilization(95)
```

### 2. **Use Scale Down Delays**
```python
# ✅ Good: Use scale down delays for stability
scaling = Scaling("app-hpa").scale_down_delay(300)

# ❌ Bad: No scale down delay
scaling = Scaling("app-hpa")  # No delay
```

### 3. **Set Reasonable Min/Max Replicas**
```python
# ✅ Good: Reasonable replica limits
scaling = Scaling("app-hpa").min_replicas(3).max_replicas(20)

# ❌ Bad: Extreme replica limits
scaling = Scaling("app-hpa").min_replicas(1).max_replicas(1000)
```

### 4. **Use Custom Metrics for Better Scaling**
```python
# ✅ Good: Use custom metrics
scaling = Scaling("app-hpa").add_custom_metric("queue_length", "10")

# ❌ Bad: Only CPU/memory metrics
scaling = Scaling("app-hpa")  # No custom metrics
```

### 5. **Configure Scaling Behavior**
```python
# ✅ Good: Configure scaling behavior
scaling = Scaling("app-hpa").behavior({
    "scaleUp": {"stabilizationWindowSeconds": 60},
    "scaleDown": {"stabilizationWindowSeconds": 300}
})

# ❌ Bad: Default behavior
scaling = Scaling("app-hpa")  # Default behavior
```

### 6. **Use VPA for Resource Optimization**
```python
# ✅ Good: Use VPA for resource optimization
scaling = Scaling("app-vpa").vertical_pod_autoscaler().vpa_mode("Auto")

# ❌ Bad: No VPA
scaling = Scaling("app-hpa")  # No VPA
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Deployment](../workloads/deployment.md)** - For deployment management
- **[Service](service.md)** - For service discovery
- **[Observability](../advanced/observability.md)** - For monitoring and metrics

## Next Steps

- **[Health](health.md)** - Learn about health check management
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 