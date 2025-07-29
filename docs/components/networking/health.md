# Health Class

The `Health` class manages health checks and probes in Kubernetes. It provides comprehensive health monitoring capabilities including liveness probes, readiness probes, startup probes, and custom health check endpoints.

## Overview

```python
from celestra import Health

# Basic health check
health = Health("app-health").liveness_probe("/health").readiness_probe("/ready")

# Production health monitoring
health = (Health("production-health")
    .liveness_probe("/health", 8080, 30, 10)
    .readiness_probe("/ready", 8080, 5, 5)
    .startup_probe("/startup", 8080, 30, 10)
    .custom_health_check("/custom", "GET"))
```

## Core API Functions

### Liveness Probe

#### Basic Liveness Probe
Configure liveness probe.

```python
# Basic liveness probe
health = Health("app-health").liveness_probe("/health")

# Detailed liveness probe
health = Health("app-health").liveness_probe("/health", 8080, 30, 10, 5, 3)
```

#### HTTP GET Liveness Probe
Configure HTTP GET liveness probe.

```python
# HTTP GET liveness probe
health = Health("app-health").liveness_http_get("/health", 8080)

# With custom headers
headers = {"Authorization": "Bearer token"}
health = Health("app-health").liveness_http_get("/health", 8080, headers)
```

#### TCP Socket Liveness Probe
Configure TCP socket liveness probe.

```python
# TCP socket liveness probe
health = Health("app-health").liveness_tcp_socket(8080)
```

#### Exec Command Liveness Probe
Configure exec command liveness probe.

```python
# Exec command liveness probe
health = Health("app-health").liveness_exec_command(["pgrep", "app"])
```

### Readiness Probe

#### Basic Readiness Probe
Configure readiness probe.

```python
# Basic readiness probe
health = Health("app-health").readiness_probe("/ready")

# Detailed readiness probe
health = Health("app-health").readiness_probe("/ready", 8080, 5, 5, 3, 3)
```

#### HTTP GET Readiness Probe
Configure HTTP GET readiness probe.

```python
# HTTP GET readiness probe
health = Health("app-health").readiness_http_get("/ready", 8080)

# With custom headers
headers = {"X-Health-Check": "true"}
health = Health("app-health").readiness_http_get("/ready", 8080, headers)
```

#### TCP Socket Readiness Probe
Configure TCP socket readiness probe.

```python
# TCP socket readiness probe
health = Health("app-health").readiness_tcp_socket(8080)
```

#### Exec Command Readiness Probe
Configure exec command readiness probe.

```python
# Exec command readiness probe
health = Health("app-health").readiness_exec_command(["test", "-f", "/ready"])
```

### Startup Probe

#### Basic Startup Probe
Configure startup probe.

```python
# Basic startup probe
health = Health("app-health").startup_probe("/startup")

# Detailed startup probe
health = Health("app-health").startup_probe("/startup", 8080, 30, 10, 5, 30)
```

#### HTTP GET Startup Probe
Configure HTTP GET startup probe.

```python
# HTTP GET startup probe
health = Health("app-health").startup_http_get("/startup", 8080)
```

#### TCP Socket Startup Probe
Configure TCP socket startup probe.

```python
# TCP socket startup probe
health = Health("app-health").startup_tcp_socket(8080)
```

#### Exec Command Startup Probe
Configure exec command startup probe.

```python
# Exec command startup probe
health = Health("app-health").startup_exec_command(["pgrep", "app"])
```

### Custom Health Checks

#### Custom Health Check Endpoint
Configure custom health check endpoint.

```python
# Custom health check
health = Health("app-health").custom_health_check("/custom", "GET")

# Custom health check with specific port
health = Health("app-health").custom_health_check("/custom", "POST", 8080)
```

#### Health Check Path
Set the health check path.

```python
health = Health("app-health").health_check_path("/health")
```

#### Health Check Port
Set the health check port.

```python
health = Health("app-health").health_check_port(8080)
```

#### Health Check Method
Set the health check HTTP method.

```python
health = Health("app-health").health_check_method("POST")
```

### Probe Configuration

#### Initial Delay Seconds
Set initial delay for probes.

```python
# 30 second initial delay
health = Health("app-health").initial_delay_seconds(30)

# 60 second initial delay for slow starting apps
health = Health("app-health").initial_delay_seconds(60)
```

#### Period Seconds
Set period for probe checks.

```python
# 10 second period
health = Health("app-health").period_seconds(10)

# 30 second period for less frequent checks
health = Health("app-health").period_seconds(30)
```

#### Timeout Seconds
Set timeout for probe checks.

```python
# 5 second timeout
health = Health("app-health").timeout_seconds(5)

# 10 second timeout for slow endpoints
health = Health("app-health").timeout_seconds(10)
```

#### Failure Threshold
Set failure threshold for probes.

```python
# 3 failure threshold
health = Health("app-health").failure_threshold(3)

# 5 failure threshold for more tolerance
health = Health("app-health").failure_threshold(5)
```

#### Success Threshold
Set success threshold for probes.

```python
# 1 success threshold
health = Health("app-health").success_threshold(1)

# 2 success threshold for more confidence
health = Health("app-health").success_threshold(2)
```

### HTTP Probe Configuration

#### HTTP Headers
Set HTTP headers for probes.

```python
headers = {
    "Authorization": "Bearer token",
    "X-Health-Check": "true"
}
health = Health("app-health").http_headers(headers)
```

#### HTTP Path
Set HTTP path for probes.

```python
health = Health("app-health").http_path("/health")
```

#### HTTP Port
Set HTTP port for probes.

```python
health = Health("app-health").http_port(8080)
```

#### HTTP Scheme
Set HTTP scheme for probes.

```python
# HTTPS scheme
health = Health("app-health").http_scheme("HTTPS")

# HTTP scheme
health = Health("app-health").http_scheme("HTTP")
```

### TCP Probe Configuration

#### TCP Port
Set TCP port for probes.

```python
health = Health("app-health").tcp_port(8080)
```

#### TCP Host
Set TCP host for probes.

```python
health = Health("app-health").tcp_host("localhost")
```

### Exec Probe Configuration

#### Exec Command
Set exec command for probes.

```python
# Basic exec command
health = Health("app-health").exec_command(["pgrep", "app"])

# Complex exec command
health = Health("app-health").exec_command(["sh", "-c", "test -f /ready && echo ok"])
```

#### Exec Working Directory
Set working directory for exec probes.

```python
health = Health("app-health").exec_working_dir("/app")
```

### Health Check Patterns

#### Basic Health Check
Configure basic health check pattern.

```python
health = Health("app-health").basic_health_check()
```

#### Production Health Check
Configure production health check pattern.

```python
health = Health("app-health").production_health_check()
```

#### Database Health Check
Configure database health check pattern.

```python
health = Health("app-health").database_health_check()
```

#### Web Application Health Check
Configure web application health check pattern.

```python
health = Health("app-health").web_application_health_check()
```

### Advanced Configuration

#### Namespace
Set the namespace for the health configuration.

```python
health = Health("app-health").namespace("production")
```

#### Add Label
Add a label to the health configuration.

```python
health = Health("app-health").add_label("environment", "production")
```

#### Add Labels
Add multiple labels to the health configuration.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "health"
}
health = Health("app-health").add_labels(labels)
```

#### Add Annotation
Add an annotation to the health configuration.

```python
health = Health("app-health").add_annotation("description", "Application health checks")
```

#### Add Annotations
Add multiple annotations to the health configuration.

```python
annotations = {
    "description": "Application health checks for production",
    "owner": "platform-team",
    "health-policy": "aggressive"
}
health = Health("app-health").add_annotations(annotations)
```

#### Health Check Interval
Set health check interval.

```python
# 30 second interval
health = Health("app-health").health_check_interval(30)
```

#### Health Check Timeout
Set health check timeout.

```python
# 10 second timeout
health = Health("app-health").health_check_timeout(10)
```

#### Health Check Retries
Set health check retries.

```python
# 3 retries
health = Health("app-health").health_check_retries(3)
```

### Output Generation

#### Generate Configuration
Generate the health check configuration.

```python
# Generate Kubernetes YAML
health.generate().to_yaml("./k8s/")

# Generate Helm values
health.generate().to_helm_values("./helm/")

# Generate Terraform
health.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready health check configuration:

```python
from celestra import Health

# Create comprehensive health check configuration
production_health = (Health("production-health")
    .liveness_probe("/health", 8080, 30, 10, 5, 3)
    .readiness_probe("/ready", 8080, 5, 5, 3, 3)
    .startup_probe("/startup", 8080, 30, 10, 5, 30)
    .custom_health_check("/custom", "GET", 8080)
    .http_headers({
        "Authorization": "Bearer health-token",
        "X-Health-Check": "true"
    })
    .http_scheme("HTTPS")
    .tcp_port(8080)
    .tcp_host("localhost")
    .exec_command(["pgrep", "app"])
    .exec_working_dir("/app")
    .health_check_interval(30)
    .health_check_timeout(10)
    .health_check_retries(3)
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "health"
    })
    .add_annotations({
        "description": "Production health checks",
        "owner": "platform-team@company.com",
        "health-policy": "aggressive"
    }))

# Generate manifests
production_health.generate().to_yaml("./k8s/")
```

## Health Check Patterns

### Basic Health Check Pattern
```python
# Basic health check for simple applications
basic_health = (Health("app-health")
    .liveness_probe("/health")
    .readiness_probe("/ready"))
```

### Production Health Check Pattern
```python
# Production health check with comprehensive monitoring
production_health = (Health("app-health")
    .liveness_probe("/health", 8080, 30, 10, 5, 3)
    .readiness_probe("/ready", 8080, 5, 5, 3, 3)
    .startup_probe("/startup", 8080, 30, 10, 5, 30)
    .http_headers({"X-Health-Check": "true"})
    .health_check_interval(30)
    .health_check_timeout(10))
```

### Database Health Check Pattern
```python
# Database health check pattern
db_health = (Health("db-health")
    .liveness_tcp_socket(5432)
    .readiness_exec_command(["pg_isready", "-h", "localhost"])
    .startup_probe("/db/startup", 8080, 60, 10, 5, 60))
```

### Web Application Health Check Pattern
```python
# Web application health check pattern
web_health = (Health("web-health")
    .liveness_http_get("/health", 80)
    .readiness_http_get("/ready", 80)
    .startup_http_get("/startup", 80)
    .http_scheme("HTTP")
    .health_check_interval(15)
    .health_check_timeout(5))
```

### Microservice Health Check Pattern
```python
# Microservice health check pattern
microservice_health = (Health("api-health")
    .liveness_probe("/api/health", 8080, 30, 10, 5, 3)
    .readiness_probe("/api/ready", 8080, 5, 5, 3, 3)
    .startup_probe("/api/startup", 8080, 30, 10, 5, 30)
    .custom_health_check("/api/custom", "GET", 8080)
    .http_headers({
        "Authorization": "Bearer service-token",
        "X-Service-Name": "api-service"
    }))
```

## Best Practices

### 1. **Use All Three Probe Types**
```python
# ✅ Good: Use all three probe types
health = (Health("app-health")
    .liveness_probe("/health")
    .readiness_probe("/ready")
    .startup_probe("/startup"))

# ❌ Bad: Only use one probe type
health = Health("app-health").liveness_probe("/health")  # Missing readiness/startup
```

### 2. **Set Appropriate Timeouts**
```python
# ✅ Good: Set appropriate timeouts
health = Health("app-health").timeout_seconds(5)

# ❌ Bad: Too short timeout
health = Health("app-health").timeout_seconds(1)  # Too short
```

### 3. **Use Startup Probes for Slow Applications**
```python
# ✅ Good: Use startup probe for slow applications
health = Health("app-health").startup_probe("/startup", initial_delay=60)

# ❌ Bad: No startup probe for slow applications
health = Health("app-health")  # No startup probe
```

### 4. **Set Reasonable Failure Thresholds**
```python
# ✅ Good: Set reasonable failure thresholds
health = Health("app-health").failure_threshold(3)

# ❌ Bad: Too high failure threshold
health = Health("app-health").failure_threshold(10)  # Too high
```

### 5. **Use HTTPS for Production**
```python
# ✅ Good: Use HTTPS for production
health = Health("app-health").http_scheme("HTTPS")

# ❌ Bad: Use HTTP for production
health = Health("app-health").http_scheme("HTTP")  # Insecure
```

### 6. **Add Custom Headers for Security**
```python
# ✅ Good: Add custom headers for security
health = Health("app-health").http_headers({"Authorization": "Bearer token"})

# ❌ Bad: No security headers
health = Health("app-health")  # No security headers
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Deployment](../workloads/deployment.md)** - For deployment management
- **[Service](service.md)** - For service discovery
- **[Observability](../advanced/observability.md)** - For monitoring and metrics

## Next Steps

- **[Companion](companion.md)** - Learn about companion services
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 