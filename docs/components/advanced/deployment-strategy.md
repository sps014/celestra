# DeploymentStrategy Class

The `DeploymentStrategy` class manages deployment strategies and patterns in Kubernetes. It provides capabilities for rolling updates, blue-green deployments, canary deployments, and advanced deployment patterns.

## Overview

```python
from celestra import DeploymentStrategy

# Basic rolling update
strategy = DeploymentStrategy("app-strategy").rolling_update().max_surge(1).max_unavailable(0)

# Production blue-green deployment
strategy = (DeploymentStrategy("production-strategy")
    .blue_green_deployment()
    .traffic_shift(50)
    .health_check("/health")
    .rollback_enabled(True))
```

## Core API Functions

### Rolling Update Strategy

#### rolling_update() -> DeploymentStrategy
Configure rolling update strategy.

```python
# Basic rolling update
strategy = DeploymentStrategy("app-strategy").rolling_update()

# Rolling update with specific settings
strategy = DeploymentStrategy("app-strategy").rolling_update().max_surge(1).max_unavailable(0)
```

#### max_surge(surge: int) -> DeploymentStrategy
Set maximum surge during rolling update.

```python
# Allow 1 extra pod during update
strategy = DeploymentStrategy("app-strategy").max_surge(1)

# Allow 25% extra pods
strategy = DeploymentStrategy("app-strategy").max_surge("25%")

# No surge
strategy = DeploymentStrategy("app-strategy").max_surge(0)
```

#### max_unavailable(unavailable: int) -> DeploymentStrategy
Set maximum unavailable pods during rolling update.

```python
# Allow 0 unavailable pods
strategy = DeploymentStrategy("app-strategy").max_unavailable(0)

# Allow 25% unavailable pods
strategy = DeploymentStrategy("app-strategy").max_unavailable("25%")

# Allow 1 unavailable pod
strategy = DeploymentStrategy("app-strategy").max_unavailable(1)
```

#### update_period_seconds(seconds: int) -> DeploymentStrategy
Set update period in seconds.

```python
# 30 second update period
strategy = DeploymentStrategy("app-strategy").update_period_seconds(30)

# 60 second update period
strategy = DeploymentStrategy("app-strategy").update_period_seconds(60)
```

#### progress_deadline_seconds(seconds: int) -> DeploymentStrategy
Set progress deadline in seconds.

```python
# 10 minute deadline
strategy = DeploymentStrategy("app-strategy").progress_deadline_seconds(600)

# 5 minute deadline
strategy = DeploymentStrategy("app-strategy").progress_deadline_seconds(300)
```

### Blue-Green Deployment Strategy

#### blue_green_deployment() -> DeploymentStrategy
Configure blue-green deployment strategy.

```python
# Basic blue-green deployment
strategy = DeploymentStrategy("app-strategy").blue_green_deployment()

# Blue-green with traffic shift
strategy = DeploymentStrategy("app-strategy").blue_green_deployment().traffic_shift(100)
```

#### traffic_shift(percentage: int) -> DeploymentStrategy
Set traffic shift percentage for blue-green deployment.

```python
# 100% traffic shift
strategy = DeploymentStrategy("app-strategy").traffic_shift(100)

# 50% traffic shift
strategy = DeploymentStrategy("app-strategy").traffic_shift(50)

# Gradual traffic shift
strategy = DeploymentStrategy("app-strategy").traffic_shift(25)
```

#### blue_green_health_check(path: str) -> DeploymentStrategy
Set health check path for blue-green deployment.

```python
# Health check path
strategy = DeploymentStrategy("app-strategy").blue_green_health_check("/health")

# Custom health check
strategy = DeploymentStrategy("app-strategy").blue_green_health_check("/api/health")
```

#### blue_green_timeout(seconds: int) -> DeploymentStrategy
Set timeout for blue-green deployment.

```python
# 5 minute timeout
strategy = DeploymentStrategy("app-strategy").blue_green_timeout(300)

# 10 minute timeout
strategy = DeploymentStrategy("app-strategy").blue_green_timeout(600)
```

#### blue_green_rollback_enabled(enabled: bool = True) -> DeploymentStrategy
Enable or disable rollback for blue-green deployment.

```python
# Enable rollback
strategy = DeploymentStrategy("app-strategy").blue_green_rollback_enabled(True)

# Disable rollback
strategy = DeploymentStrategy("app-strategy").blue_green_rollback_enabled(False)
```

### Canary Deployment Strategy

#### canary_deployment() -> DeploymentStrategy
Configure canary deployment strategy.

```python
# Basic canary deployment
strategy = DeploymentStrategy("app-strategy").canary_deployment()

# Canary with traffic percentage
strategy = DeploymentStrategy("app-strategy").canary_deployment().canary_traffic(10)
```

#### canary_traffic(percentage: int) -> DeploymentStrategy
Set canary traffic percentage.

```python
# 10% canary traffic
strategy = DeploymentStrategy("app-strategy").canary_traffic(10)

# 5% canary traffic
strategy = DeploymentStrategy("app-strategy").canary_traffic(5)

# 25% canary traffic
strategy = DeploymentStrategy("app-strategy").canary_traffic(25)
```

#### canary_duration(minutes: int) -> DeploymentStrategy
Set canary deployment duration.

```python
# 30 minute canary
strategy = DeploymentStrategy("app-strategy").canary_duration(30)

# 60 minute canary
strategy = DeploymentStrategy("app-strategy").canary_duration(60)
```

#### canary_metrics(metrics: List[str]) -> DeploymentStrategy
Set metrics to monitor during canary deployment.

```python
# Monitor error rate and latency
strategy = DeploymentStrategy("app-strategy").canary_metrics([
    "error_rate",
    "latency_p95",
    "throughput"
])

# Monitor business metrics
strategy = DeploymentStrategy("app-strategy").canary_metrics([
    "conversion_rate",
    "revenue_per_user"
])
```

#### canary_threshold(threshold: float) -> DeploymentStrategy
Set threshold for canary success/failure.

```python
# 5% error rate threshold
strategy = DeploymentStrategy("app-strategy").canary_threshold(0.05)

# 10% error rate threshold
strategy = DeploymentStrategy("app-strategy").canary_threshold(0.10)
```

### Recreate Strategy

#### recreate_strategy() -> DeploymentStrategy
Configure recreate deployment strategy.

```python
# Basic recreate strategy
strategy = DeploymentStrategy("app-strategy").recreate_strategy()

# Recreate with pre-hook
strategy = DeploymentStrategy("app-strategy").recreate_strategy().pre_hook("backup")
```

#### pre_hook(command: str) -> DeploymentStrategy
Set pre-hook command for recreate strategy.

```python
# Backup before recreate
strategy = DeploymentStrategy("app-strategy").pre_hook("backup")

# Database migration before recreate
strategy = DeploymentStrategy("app-strategy").pre_hook("migrate")
```

#### post_hook(command: str) -> DeploymentStrategy
Set post-hook command for recreate strategy.

```python
# Health check after recreate
strategy = DeploymentStrategy("app-strategy").post_hook("health-check")

# Cache warmup after recreate
strategy = DeploymentStrategy("app-strategy").post_hook("warmup")
```

### Advanced Deployment Patterns

#### progressive_deployment() -> DeploymentStrategy
Configure progressive deployment strategy.

```python
# Basic progressive deployment
strategy = DeploymentStrategy("app-strategy").progressive_deployment()

# Progressive with stages
strategy = DeploymentStrategy("app-strategy").progressive_deployment().stages([10, 25, 50, 100])
```

#### stages(percentages: List[int]) -> DeploymentStrategy
Set deployment stages for progressive deployment.

```python
# 4-stage deployment
strategy = DeploymentStrategy("app-strategy").stages([10, 25, 50, 100])

# 3-stage deployment
strategy = DeploymentStrategy("app-strategy").stages([20, 60, 100])
```

#### stage_duration(minutes: int) -> DeploymentStrategy
Set duration for each deployment stage.

```python
# 15 minute stages
strategy = DeploymentStrategy("app-strategy").stage_duration(15)

# 30 minute stages
strategy = DeploymentStrategy("app-strategy").stage_duration(30)
```

#### auto_promotion(enabled: bool = True) -> DeploymentStrategy
Enable or disable auto-promotion between stages.

```python
# Enable auto-promotion
strategy = DeploymentStrategy("app-strategy").auto_promotion(True)

# Disable auto-promotion
strategy = DeploymentStrategy("app-strategy").auto_promotion(False)
```

### Health Check Configuration

#### health_check(path: str) -> DeploymentStrategy
Set health check path for deployment strategy.

```python
# Basic health check
strategy = DeploymentStrategy("app-strategy").health_check("/health")

# Custom health check
strategy = DeploymentStrategy("app-strategy").health_check("/api/health")
```

#### health_check_timeout(seconds: int) -> DeploymentStrategy
Set health check timeout.

```python
# 30 second timeout
strategy = DeploymentStrategy("app-strategy").health_check_timeout(30)

# 60 second timeout
strategy = DeploymentStrategy("app-strategy").health_check_timeout(60)
```

#### health_check_interval(seconds: int) -> DeploymentStrategy
Set health check interval.

```python
# 10 second interval
strategy = DeploymentStrategy("app-strategy").health_check_interval(10)

# 30 second interval
strategy = DeploymentStrategy("app-strategy").health_check_interval(30)
```

#### health_check_retries(retries: int) -> DeploymentStrategy
Set health check retries.

```python
# 3 retries
strategy = DeploymentStrategy("app-strategy").health_check_retries(3)

# 5 retries
strategy = DeploymentStrategy("app-strategy").health_check_retries(5)
```

### Rollback Configuration

#### rollback_enabled(enabled: bool = True) -> DeploymentStrategy
Enable or disable rollback.

```python
# Enable rollback
strategy = DeploymentStrategy("app-strategy").rollback_enabled(True)

# Disable rollback
strategy = DeploymentStrategy("app-strategy").rollback_enabled(False)
```

#### rollback_threshold(threshold: float) -> DeploymentStrategy
Set rollback threshold.

```python
# 5% error rate threshold
strategy = DeploymentStrategy("app-strategy").rollback_threshold(0.05)

# 10% error rate threshold
strategy = DeploymentStrategy("app-strategy").rollback_threshold(0.10)
```

#### rollback_window(minutes: int) -> DeploymentStrategy
Set rollback window in minutes.

```python
# 30 minute rollback window
strategy = DeploymentStrategy("app-strategy").rollback_window(30)

# 60 minute rollback window
strategy = DeploymentStrategy("app-strategy").rollback_window(60)
```

#### automatic_rollback(enabled: bool = True) -> DeploymentStrategy
Enable or disable automatic rollback.

```python
# Enable automatic rollback
strategy = DeploymentStrategy("app-strategy").automatic_rollback(True)

# Disable automatic rollback
strategy = DeploymentStrategy("app-strategy").automatic_rollback(False)
```

### Traffic Management

#### traffic_routing(routing: str) -> DeploymentStrategy
Set traffic routing method.

```python
# Weight-based routing
strategy = DeploymentStrategy("app-strategy").traffic_routing("weight")

# Header-based routing
strategy = DeploymentStrategy("app-strategy").traffic_routing("header")

# Cookie-based routing
strategy = DeploymentStrategy("app-strategy").traffic_routing("cookie")
```

#### traffic_headers(headers: Dict[str, str]) -> DeploymentStrategy
Set traffic routing headers.

```python
# Set routing headers
headers = {
    "X-Version": "v2",
    "X-Environment": "canary"
}
strategy = DeploymentStrategy("app-strategy").traffic_headers(headers)
```

#### traffic_cookies(cookies: Dict[str, str]) -> DeploymentStrategy
Set traffic routing cookies.

```python
# Set routing cookies
cookies = {
    "version": "v2",
    "environment": "canary"
}
strategy = DeploymentStrategy("app-strategy").traffic_cookies(cookies)
```

### Advanced Configuration

#### namespace(namespace: str) -> DeploymentStrategy
Set the namespace for the deployment strategy.

```python
strategy = DeploymentStrategy("app-strategy").namespace("production")
```

#### add_label(key: str, value: str) -> DeploymentStrategy
Add a label to the deployment strategy.

```python
strategy = DeploymentStrategy("app-strategy").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> DeploymentStrategy
Add multiple labels to the deployment strategy.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "strategy"
}
strategy = DeploymentStrategy("app-strategy").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> DeploymentStrategy
Add an annotation to the deployment strategy.

```python
strategy = DeploymentStrategy("app-strategy").add_annotation("description", "Application deployment strategy")
```

#### add_annotations(annotations: Dict[str, str]) -> DeploymentStrategy
Add multiple annotations to the deployment strategy.

```python
annotations = {
    "description": "Application deployment strategy for production",
    "owner": "platform-team",
    "strategy-type": "blue-green"
}
strategy = DeploymentStrategy("app-strategy").add_annotations(annotations)
```

#### deployment_pause(enabled: bool = True) -> DeploymentStrategy
Enable or disable deployment pause.

```python
# Enable deployment pause
strategy = DeploymentStrategy("app-strategy").deployment_pause(True)

# Disable deployment pause
strategy = DeploymentStrategy("app-strategy").deployment_pause(False)
```

#### deployment_resume() -> DeploymentStrategy
Resume paused deployment.

```python
strategy = DeploymentStrategy("app-strategy").deployment_resume()
```

### Output Generation

#### generate() -> DeploymentStrategyGenerator
Generate the deployment strategy configuration.

```python
# Generate Kubernetes YAML
strategy.generate().to_yaml("./k8s/")

# Generate Helm values
strategy.generate().to_helm_values("./helm/")

# Generate Terraform
strategy.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready deployment strategy configuration:

```python
from celestra import DeploymentStrategy

# Create comprehensive deployment strategy configuration
production_strategy = (DeploymentStrategy("production-strategy")
    .blue_green_deployment()
    .traffic_shift(100)
    .blue_green_health_check("/health")
    .blue_green_timeout(600)
    .blue_green_rollback_enabled(True)
    .canary_deployment()
    .canary_traffic(10)
    .canary_duration(30)
    .canary_metrics([
        "error_rate",
        "latency_p95",
        "throughput"
    ])
    .canary_threshold(0.05)
    .rolling_update()
    .max_surge(1)
    .max_unavailable(0)
    .update_period_seconds(30)
    .progress_deadline_seconds(600)
    .health_check("/health")
    .health_check_timeout(30)
    .health_check_interval(10)
    .health_check_retries(3)
    .rollback_enabled(True)
    .rollback_threshold(0.05)
    .rollback_window(30)
    .automatic_rollback(True)
    .traffic_routing("weight")
    .traffic_headers({
        "X-Version": "v2",
        "X-Environment": "production"
    })
    .deployment_pause(False)
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "strategy"
    })
    .add_annotations({
        "description": "Production deployment strategy",
        "owner": "platform-team@company.com",
        "strategy-type": "blue-green"
    }))

# Generate manifests
production_strategy.generate().to_yaml("./k8s/")
```

## Deployment Strategy Patterns

### Rolling Update Pattern
```python
# Rolling update pattern
rolling_strategy = (DeploymentStrategy("rolling-strategy")
    .rolling_update()
    .max_surge(1)
    .max_unavailable(0)
    .update_period_seconds(30)
    .progress_deadline_seconds(600)
    .health_check("/health"))
```

### Blue-Green Pattern
```python
# Blue-green deployment pattern
blue_green_strategy = (DeploymentStrategy("blue-green-strategy")
    .blue_green_deployment()
    .traffic_shift(100)
    .blue_green_health_check("/health")
    .blue_green_timeout(600)
    .blue_green_rollback_enabled(True))
```

### Canary Pattern
```python
# Canary deployment pattern
canary_strategy = (DeploymentStrategy("canary-strategy")
    .canary_deployment()
    .canary_traffic(10)
    .canary_duration(30)
    .canary_metrics(["error_rate", "latency_p95"])
    .canary_threshold(0.05))
```

### Progressive Pattern
```python
# Progressive deployment pattern
progressive_strategy = (DeploymentStrategy("progressive-strategy")
    .progressive_deployment()
    .stages([10, 25, 50, 100])
    .stage_duration(15)
    .auto_promotion(True))
```

### Recreate Pattern
```python
# Recreate deployment pattern
recreate_strategy = (DeploymentStrategy("recreate-strategy")
    .recreate_strategy()
    .pre_hook("backup")
    .post_hook("health-check"))
```

## Best Practices

### 1. **Use Appropriate Strategy for Application Type**
```python
# ✅ Good: Use rolling update for stateless apps
strategy = DeploymentStrategy("app-strategy").rolling_update().max_surge(1).max_unavailable(0)

# ✅ Good: Use blue-green for stateful apps
strategy = DeploymentStrategy("app-strategy").blue_green_deployment().traffic_shift(100)

# ❌ Bad: Use recreate for stateless apps
strategy = DeploymentStrategy("app-strategy").recreate_strategy()  # Downtime
```

### 2. **Set Appropriate Timeouts**
```python
# ✅ Good: Set appropriate timeouts
strategy = DeploymentStrategy("app-strategy").blue_green_timeout(600)

# ❌ Bad: No timeout
strategy = DeploymentStrategy("app-strategy")  # No timeout
```

### 3. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
strategy = DeploymentStrategy("app-strategy").health_check("/health")

# ❌ Bad: No health checks
strategy = DeploymentStrategy("app-strategy")  # No health checks
```

### 4. **Enable Rollback**
```python
# ✅ Good: Enable rollback
strategy = DeploymentStrategy("app-strategy").rollback_enabled(True)

# ❌ Bad: No rollback
strategy = DeploymentStrategy("app-strategy")  # No rollback
```

### 5. **Use Canary for High-Risk Deployments**
```python
# ✅ Good: Use canary for high-risk deployments
strategy = DeploymentStrategy("app-strategy").canary_deployment().canary_traffic(5)

# ❌ Bad: Direct deployment for high-risk changes
strategy = DeploymentStrategy("app-strategy").rolling_update()  # No testing
```

### 6. **Set Appropriate Thresholds**
```python
# ✅ Good: Set appropriate thresholds
strategy = DeploymentStrategy("app-strategy").rollback_threshold(0.05)

# ❌ Bad: No thresholds
strategy = DeploymentStrategy("app-strategy")  # No thresholds
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Deployment](../workloads/deployment.md)** - For deployment management
- **[Service](../networking/service.md)** - For service discovery
- **[WaitCondition](wait-condition.md)** - For wait conditions

## Next Steps

- **[CustomResource](custom-resource.md)** - Learn about custom Kubernetes resources
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 