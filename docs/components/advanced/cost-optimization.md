# CostOptimization Class

The `CostOptimization` class provides comprehensive cost optimization capabilities for Kubernetes workloads. It includes resource optimization, spot instance management, autoscaling strategies, and cost analysis tools.

## Overview

```python
from celestra import CostOptimization

# Basic cost optimization
cost_opt = CostOptimization("app-optimization").resource_optimization().spot_instance_recommendation()

# Production cost optimization
cost_opt = (CostOptimization("production-optimization")
    .resource_optimization()
    .spot_instance_recommendation()
    .autoscaling_optimization()
    .cost_analysis()
    .budget_alerts())
```

## Core API Functions

### Resource Optimization

#### resource_optimization(enabled: bool = True) -> CostOptimization
Enable resource optimization analysis.

```python
# Basic resource optimization
cost_opt = CostOptimization("app-optimization").resource_optimization()

# Disable resource optimization
cost_opt = CostOptimization("app-optimization").resource_optimization(False)
```

#### cpu_optimization(target_utilization: float = 0.7) -> CostOptimization
Optimize CPU resource allocation.

```python
# Optimize CPU with 70% target utilization
cost_opt = CostOptimization("app-optimization").cpu_optimization(0.7)

# Conservative CPU optimization
cost_opt = CostOptimization("app-optimization").cpu_optimization(0.5)
```

#### memory_optimization(target_utilization: float = 0.8) -> CostOptimization
Optimize memory resource allocation.

```python
# Optimize memory with 80% target utilization
cost_opt = CostOptimization("app-optimization").memory_optimization(0.8)

# Conservative memory optimization
cost_opt = CostOptimization("app-optimization").memory_optimization(0.6)
```

#### storage_optimization(compression: bool = True, deduplication: bool = True) -> CostOptimization
Optimize storage costs.

```python
# Enable storage optimization
cost_opt = CostOptimization("app-optimization").storage_optimization()

# Custom storage optimization
cost_opt = CostOptimization("app-optimization").storage_optimization(
    compression=True,
    deduplication=True
)
```

#### network_optimization(bandwidth_optimization: bool = True) -> CostOptimization
Optimize network costs.

```python
# Enable network optimization
cost_opt = CostOptimization("app-optimization").network_optimization()

# Disable bandwidth optimization
cost_opt = CostOptimization("app-optimization").network_optimization(False)
```

### Spot Instance Management

#### spot_instance_recommendation(enabled: bool = True) -> CostOptimization
Enable spot instance recommendations.

```python
# Enable spot instance recommendations
cost_opt = CostOptimization("app-optimization").spot_instance_recommendation()

# Disable spot instance recommendations
cost_opt = CostOptimization("app-optimization").spot_instance_recommendation(False)
```

#### spot_instance_strategy(strategy: str = "balanced") -> CostOptimization
Set spot instance strategy.

```python
# Balanced strategy (default)
cost_opt = CostOptimization("app-optimization").spot_instance_strategy("balanced")

# Cost-optimized strategy
cost_opt = CostOptimization("app-optimization").spot_instance_strategy("cost-optimized")

# Availability-optimized strategy
cost_opt = CostOptimization("app-optimization").spot_instance_strategy("availability-optimized")
```

#### spot_instance_mix(spot_percentage: float = 0.5) -> CostOptimization
Set the percentage of spot instances in the workload.

```python
# 50% spot instances
cost_opt = CostOptimization("app-optimization").spot_instance_mix(0.5)

# 80% spot instances for cost optimization
cost_opt = CostOptimization("app-optimization").spot_instance_mix(0.8)

# 20% spot instances for availability
cost_opt = CostOptimization("app-optimization").spot_instance_mix(0.2)
```

#### spot_instance_fallback(enabled: bool = True) -> CostOptimization
Enable fallback to on-demand instances when spot instances are unavailable.

```python
# Enable fallback
cost_opt = CostOptimization("app-optimization").spot_instance_fallback(True)

# Disable fallback
cost_opt = CostOptimization("app-optimization").spot_instance_fallback(False)
```

### Autoscaling Optimization

#### autoscaling_optimization(enabled: bool = True) -> CostOptimization
Enable autoscaling optimization.

```python
# Enable autoscaling optimization
cost_opt = CostOptimization("app-optimization").autoscaling_optimization()

# Disable autoscaling optimization
cost_opt = CostOptimization("app-optimization").autoscaling_optimization(False)
```

#### horizontal_scaling_optimization(min_replicas: int = 1, max_replicas: int = 10) -> CostOptimization
Optimize horizontal pod autoscaling.

```python
# Optimize HPA
cost_opt = CostOptimization("app-optimization").horizontal_scaling_optimization(1, 10)

# Conservative scaling
cost_opt = CostOptimization("app-optimization").horizontal_scaling_optimization(2, 5)
```

#### vertical_scaling_optimization(enabled: bool = True) -> CostOptimization
Enable vertical pod autoscaling optimization.

```python
# Enable VPA optimization
cost_opt = CostOptimization("app-optimization").vertical_scaling_optimization(True)

# Disable VPA optimization
cost_opt = CostOptimization("app-optimization").vertical_scaling_optimization(False)
```

#### cluster_autoscaler_optimization(enabled: bool = True) -> CostOptimization
Enable cluster autoscaler optimization.

```python
# Enable cluster autoscaler optimization
cost_opt = CostOptimization("app-optimization").cluster_autoscaler_optimization(True)

# Disable cluster autoscaler optimization
cost_opt = CostOptimization("app-optimization").cluster_autoscaler_optimization(False)
```

### Cost Analysis

#### cost_analysis(enabled: bool = True) -> CostOptimization
Enable cost analysis and reporting.

```python
# Enable cost analysis
cost_opt = CostOptimization("app-optimization").cost_analysis()

# Disable cost analysis
cost_opt = CostOptimization("app-optimization").cost_analysis(False)
```

#### cost_breakdown(breakdown_by: List[str] = None) -> CostOptimization
Configure cost breakdown analysis.

```python
# Default cost breakdown
cost_opt = CostOptimization("app-optimization").cost_breakdown()

# Custom cost breakdown
cost_opt = CostOptimization("app-optimization").cost_breakdown([
    "namespace", "pod", "service", "storage"
])
```

#### cost_forecasting(forecast_period: str = "30d") -> CostOptimization
Enable cost forecasting.

```python
# 30-day cost forecast
cost_opt = CostOptimization("app-optimization").cost_forecasting("30d")

# 90-day cost forecast
cost_opt = CostOptimization("app-optimization").cost_forecasting("90d")
```

#### cost_anomaly_detection(enabled: bool = True) -> CostOptimization
Enable cost anomaly detection.

```python
# Enable anomaly detection
cost_opt = CostOptimization("app-optimization").cost_anomaly_detection(True)

# Disable anomaly detection
cost_opt = CostOptimization("app-optimization").cost_anomaly_detection(False)
```

### Budget Management

#### budget_alerts(budget_limit: float = None, alert_threshold: float = 0.8) -> CostOptimization
Configure budget alerts.

```python
# Default budget alerts
cost_opt = CostOptimization("app-optimization").budget_alerts()

# Custom budget alerts
cost_opt = CostOptimization("app-optimization").budget_alerts(
    budget_limit=1000.0,
    alert_threshold=0.8
)
```

#### budget_limit(limit: float) -> CostOptimization
Set budget limit.

```python
# Set $1000 monthly budget
cost_opt = CostOptimization("app-optimization").budget_limit(1000.0)

# Set $5000 monthly budget
cost_opt = CostOptimization("app-optimization").budget_limit(5000.0)
```

#### alert_threshold(threshold: float) -> CostOptimization
Set alert threshold percentage.

```python
# Alert at 80% of budget
cost_opt = CostOptimization("app-optimization").alert_threshold(0.8)

# Alert at 90% of budget
cost_opt = CostOptimization("app-optimization").alert_threshold(0.9)
```

#### cost_optimization_schedule(schedule: str = "daily") -> CostOptimization
Set cost optimization schedule.

```python
# Daily optimization
cost_opt = CostOptimization("app-optimization").cost_optimization_schedule("daily")

# Weekly optimization
cost_opt = CostOptimization("app-optimization").cost_optimization_schedule("weekly")

# Monthly optimization
cost_opt = CostOptimization("app-optimization").cost_optimization_schedule("monthly")
```

### Instance Type Optimization

#### instance_type_optimization(enabled: bool = True) -> CostOptimization
Enable instance type optimization.

```python
# Enable instance type optimization
cost_opt = CostOptimization("app-optimization").instance_type_optimization(True)

# Disable instance type optimization
cost_opt = CostOptimization("app-optimization").instance_type_optimization(False)
```

#### instance_type_recommendation(criteria: str = "cost") -> CostOptimization
Set instance type recommendation criteria.

```python
# Cost-optimized recommendations
cost_opt = CostOptimization("app-optimization").instance_type_recommendation("cost")

# Performance-optimized recommendations
cost_opt = CostOptimization("app-optimization").instance_type_recommendation("performance")

# Balanced recommendations
cost_opt = CostOptimization("app-optimization").instance_type_recommendation("balanced")
```

#### reserved_instance_recommendation(enabled: bool = True) -> CostOptimization
Enable reserved instance recommendations.

```python
# Enable reserved instance recommendations
cost_opt = CostOptimization("app-optimization").reserved_instance_recommendation(True)

# Disable reserved instance recommendations
cost_opt = CostOptimization("app-optimization").reserved_instance_recommendation(False)
```

### Storage Optimization

#### storage_class_optimization(enabled: bool = True) -> CostOptimization
Enable storage class optimization.

```python
# Enable storage class optimization
cost_opt = CostOptimization("app-optimization").storage_class_optimization(True)

# Disable storage class optimization
cost_opt = CostOptimization("app-optimization").storage_class_optimization(False)
```

#### storage_retention_optimization(enabled: bool = True) -> CostOptimization
Enable storage retention optimization.

```python
# Enable storage retention optimization
cost_opt = CostOptimization("app-optimization").storage_retention_optimization(True)

# Disable storage retention optimization
cost_opt = CostOptimization("app-optimization").storage_retention_optimization(False)
```

#### backup_optimization(enabled: bool = True) -> CostOptimization
Enable backup cost optimization.

```python
# Enable backup optimization
cost_opt = CostOptimization("app-optimization").backup_optimization(True)

# Disable backup optimization
cost_opt = CostOptimization("app-optimization").backup_optimization(False)
```

### Network Optimization

#### network_cost_optimization(enabled: bool = True) -> CostOptimization
Enable network cost optimization.

```python
# Enable network cost optimization
cost_opt = CostOptimization("app-optimization").network_cost_optimization(True)

# Disable network cost optimization
cost_opt = CostOptimization("app-optimization").network_cost_optimization(False)
```

#### data_transfer_optimization(enabled: bool = True) -> CostOptimization
Enable data transfer cost optimization.

```python
# Enable data transfer optimization
cost_opt = CostOptimization("app-optimization").data_transfer_optimization(True)

# Disable data transfer optimization
cost_opt = CostOptimization("app-optimization").data_transfer_optimization(False)
```

### Advanced Configuration

#### namespace(namespace: str) -> CostOptimization
Set the namespace for cost optimization components.

```python
cost_opt = CostOptimization("app-optimization").namespace("cost-optimization")
```

#### add_label(key: str, value: str) -> CostOptimization
Add a label to cost optimization components.

```python
cost_opt = CostOptimization("app-optimization").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> CostOptimization
Add multiple labels to cost optimization components.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "cost-optimization"
}
cost_opt = CostOptimization("app-optimization").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> CostOptimization
Add an annotation to cost optimization components.

```python
cost_opt = CostOptimization("app-optimization").add_annotation("description", "Cost optimization")
```

#### add_annotations(annotations: Dict[str, str]) -> CostOptimization
Add multiple annotations to cost optimization components.

```python
annotations = {
    "description": "Cost optimization for production",
    "owner": "platform-team",
    "optimization-schedule": "daily"
}
cost_opt = CostOptimization("app-optimization").add_annotations(annotations)
```

#### optimization_reporting(enabled: bool = True) -> CostOptimization
Enable optimization reporting.

```python
# Enable optimization reporting
cost_opt = CostOptimization("app-optimization").optimization_reporting(True)

# Disable optimization reporting
cost_opt = CostOptimization("app-optimization").optimization_reporting(False)
```

#### cost_savings_tracking(enabled: bool = True) -> CostOptimization
Enable cost savings tracking.

```python
# Enable cost savings tracking
cost_opt = CostOptimization("app-optimization").cost_savings_tracking(True)

# Disable cost savings tracking
cost_opt = CostOptimization("app-optimization").cost_savings_tracking(False)
```

### Output Generation

#### generate() -> CostOptimizationGenerator
Generate the cost optimization configuration.

```python
# Generate Kubernetes YAML
cost_opt.generate().to_yaml("./k8s/")

# Generate cost analysis report
cost_opt.generate().to_cost_report("./reports/")

# Generate optimization recommendations
cost_opt.generate().to_recommendations("./recommendations/")
```

## Complete Example

Here's a complete example of a production-ready cost optimization setup:

```python
from celestra import CostOptimization

# Create comprehensive cost optimization configuration
cost_opt = (CostOptimization("production-optimization")
    .resource_optimization(True)
    .cpu_optimization(target_utilization=0.7)
    .memory_optimization(target_utilization=0.8)
    .storage_optimization(compression=True, deduplication=True)
    .network_optimization(bandwidth_optimization=True)
    .spot_instance_recommendation(True)
    .spot_instance_strategy("balanced")
    .spot_instance_mix(spot_percentage=0.5)
    .spot_instance_fallback(True)
    .autoscaling_optimization(True)
    .horizontal_scaling_optimization(min_replicas=1, max_replicas=10)
    .vertical_scaling_optimization(True)
    .cluster_autoscaler_optimization(True)
    .cost_analysis(True)
    .cost_breakdown(["namespace", "pod", "service", "storage"])
    .cost_forecasting(forecast_period="30d")
    .cost_anomaly_detection(True)
    .budget_alerts(budget_limit=5000.0, alert_threshold=0.8)
    .cost_optimization_schedule("daily")
    .instance_type_optimization(True)
    .instance_type_recommendation("cost")
    .reserved_instance_recommendation(True)
    .storage_class_optimization(True)
    .storage_retention_optimization(True)
    .backup_optimization(True)
    .network_cost_optimization(True)
    .data_transfer_optimization(True)
    .namespace("cost-optimization")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "cost-optimization"
    })
    .add_annotations({
        "description": "Production cost optimization",
        "owner": "platform-team@company.com",
        "optimization-schedule": "daily"
    })
    .optimization_reporting(True)
    .cost_savings_tracking(True))

# Generate manifests and reports
cost_opt.generate().to_yaml("./k8s/")
cost_opt.generate().to_cost_report("./reports/")
cost_opt.generate().to_recommendations("./recommendations/")
```

## Cost Optimization Strategies

### Resource Optimization Strategy
```python
# Conservative resource optimization
conservative_opt = (CostOptimization("conservative-optimization")
    .cpu_optimization(0.5)
    .memory_optimization(0.6)
    .resource_optimization(True))
```

### Spot Instance Strategy
```python
# Aggressive spot instance usage
aggressive_spot = (CostOptimization("aggressive-spot")
    .spot_instance_recommendation(True)
    .spot_instance_strategy("cost-optimized")
    .spot_instance_mix(0.8)
    .spot_instance_fallback(True))
```

### Autoscaling Strategy
```python
# Optimized autoscaling
autoscaling_opt = (CostOptimization("autoscaling-optimization")
    .autoscaling_optimization(True)
    .horizontal_scaling_optimization(2, 8)
    .vertical_scaling_optimization(True)
    .cluster_autoscaler_optimization(True))
```

### Budget Management Strategy
```python
# Strict budget management
budget_management = (CostOptimization("budget-management")
    .budget_alerts(budget_limit=1000.0, alert_threshold=0.7)
    .cost_analysis(True)
    .cost_anomaly_detection(True)
    .cost_forecasting("30d"))
```

## Best Practices

### 1. **Start with Resource Optimization**
```python
# ✅ Good: Start with resource optimization
cost_opt = CostOptimization("app-optimization").resource_optimization(True)

# ❌ Bad: Skip resource optimization
cost_opt = CostOptimization("app-optimization")  # No resource optimization
```

### 2. **Use Balanced Spot Instance Strategy**
```python
# ✅ Good: Use balanced spot instance strategy
cost_opt = CostOptimization("app-optimization").spot_instance_strategy("balanced")

# ❌ Bad: Use aggressive strategy without fallback
cost_opt = CostOptimization("app-optimization").spot_instance_strategy("cost-optimized").spot_instance_fallback(False)
```

### 3. **Set Budget Alerts**
```python
# ✅ Good: Set budget alerts
cost_opt = CostOptimization("app-optimization").budget_alerts(budget_limit=1000.0, alert_threshold=0.8)

# ❌ Bad: No budget monitoring
cost_opt = CostOptimization("app-optimization")  # No budget alerts
```

### 4. **Enable Cost Analysis**
```python
# ✅ Good: Enable cost analysis
cost_opt = CostOptimization("app-optimization").cost_analysis(True).cost_breakdown()

# ❌ Bad: No cost analysis
cost_opt = CostOptimization("app-optimization")  # No cost analysis
```

### 5. **Use Appropriate Target Utilization**
```python
# ✅ Good: Use appropriate target utilization
cost_opt = CostOptimization("app-optimization").cpu_optimization(0.7).memory_optimization(0.8)

# ❌ Bad: Use unrealistic target utilization
cost_opt = CostOptimization("app-optimization").cpu_optimization(0.95).memory_optimization(0.95)
```

### 6. **Enable Anomaly Detection**
```python
# ✅ Good: Enable anomaly detection
cost_opt = CostOptimization("app-optimization").cost_anomaly_detection(True)

# ❌ Bad: No anomaly detection
cost_opt = CostOptimization("app-optimization")  # No anomaly detection
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Observability](observability.md)** - For monitoring and metrics
- **[Service](../networking/service.md)** - For service discovery
- **[Ingress](../networking/ingress.md)** - For external access

## Next Steps

- **[Observability](observability.md)** - Learn about monitoring and observability
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 