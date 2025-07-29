# WaitCondition Class

The `WaitCondition` class manages wait conditions and dependency checks in Kubernetes. It provides capabilities for waiting for resources to be ready, checking dependencies, and managing deployment order.

## Overview

```python
from celestra import WaitCondition

# Basic wait condition
wait = WaitCondition("app-ready").wait_for_deployment("app").timeout(300)

# Production wait condition with multiple dependencies
wait = (WaitCondition("production-ready")
    .wait_for_deployment("app")
    .wait_for_service("app-service")
    .wait_for_pod("database")
    .timeout(600)
    .retry_interval(10))
```

## Core API Functions

### Deployment Wait Conditions

#### wait_for_deployment(name: str) -> WaitCondition
Wait for a deployment to be ready.

```python
# Wait for app deployment
wait = WaitCondition("app-ready").wait_for_deployment("app")

# Wait for multiple deployments
wait = WaitCondition("all-ready").wait_for_deployment("frontend").wait_for_deployment("backend")
```

#### deployment_ready_condition(condition: str) -> WaitCondition
Set the deployment ready condition.

```python
# Wait for available condition
wait = WaitCondition("app-ready").deployment_ready_condition("Available")

# Wait for progressing condition
wait = WaitCondition("app-ready").deployment_ready_condition("Progressing")
```

#### deployment_replicas(replicas: int) -> WaitCondition
Wait for specific number of replicas.

```python
# Wait for 3 replicas
wait = WaitCondition("app-ready").deployment_replicas(3)

# Wait for 5 replicas
wait = WaitCondition("app-ready").deployment_replicas(5)
```

### Service Wait Conditions

#### wait_for_service(name: str) -> WaitCondition
Wait for a service to be ready.

```python
# Wait for app service
wait = WaitCondition("service-ready").wait_for_service("app-service")

# Wait for multiple services
wait = WaitCondition("all-services").wait_for_service("frontend").wait_for_service("backend")
```

#### service_endpoints(endpoints: int) -> WaitCondition
Wait for specific number of endpoints.

```python
# Wait for 1 endpoint
wait = WaitCondition("service-ready").service_endpoints(1)

# Wait for 3 endpoints
wait = WaitCondition("service-ready").service_endpoints(3)
```

### Pod Wait Conditions

#### wait_for_pod(name: str) -> WaitCondition
Wait for a pod to be ready.

```python
# Wait for app pod
wait = WaitCondition("pod-ready").wait_for_pod("app")

# Wait for database pod
wait = WaitCondition("db-ready").wait_for_pod("database")
```

#### pod_phase(phase: str) -> WaitCondition
Wait for specific pod phase.

```python
# Wait for running phase
wait = WaitCondition("pod-ready").pod_phase("Running")

# Wait for pending phase
wait = WaitCondition("pod-ready").pod_phase("Pending")
```

#### pod_ready_condition(condition: str) -> WaitCondition
Wait for specific pod ready condition.

```python
# Wait for ready condition
wait = WaitCondition("pod-ready").pod_ready_condition("Ready")

# Wait for scheduled condition
wait = WaitCondition("pod-ready").pod_ready_condition("PodScheduled")
```

### StatefulSet Wait Conditions

#### wait_for_statefulset(name: str) -> WaitCondition
Wait for a StatefulSet to be ready.

```python
# Wait for database StatefulSet
wait = WaitCondition("db-ready").wait_for_statefulset("database")

# Wait for cache StatefulSet
wait = WaitCondition("cache-ready").wait_for_statefulset("redis")
```

#### statefulset_replicas(replicas: int) -> WaitCondition
Wait for specific number of StatefulSet replicas.

```python
# Wait for 3 StatefulSet replicas
wait = WaitCondition("db-ready").statefulset_replicas(3)

# Wait for 1 StatefulSet replica
wait = WaitCondition("db-ready").statefulset_replicas(1)
```

### Job Wait Conditions

#### wait_for_job(name: str) -> WaitCondition
Wait for a job to complete.

```python
# Wait for migration job
wait = WaitCondition("migration-ready").wait_for_job("db-migration")

# Wait for backup job
wait = WaitCondition("backup-ready").wait_for_job("backup-job")
```

#### job_completion_condition(condition: str) -> WaitCondition
Wait for specific job completion condition.

```python
# Wait for complete condition
wait = WaitCondition("job-ready").job_completion_condition("Complete")

# Wait for failed condition
wait = WaitCondition("job-ready").job_completion_condition("Failed")
```

### ConfigMap and Secret Wait Conditions

#### wait_for_configmap(name: str) -> WaitCondition
Wait for a ConfigMap to exist.

```python
# Wait for app config
wait = WaitCondition("config-ready").wait_for_configmap("app-config")

# Wait for database config
wait = WaitCondition("config-ready").wait_for_configmap("db-config")
```

#### wait_for_secret(name: str) -> WaitCondition
Wait for a secret to exist.

```python
# Wait for app secret
wait = WaitCondition("secret-ready").wait_for_secret("app-secret")

# Wait for database secret
wait = WaitCondition("secret-ready").wait_for_secret("db-secret")
```

### Custom Resource Wait Conditions

#### wait_for_custom_resource(api_version: str, kind: str, name: str) -> WaitCondition
Wait for a custom resource to be ready.

```python
# Wait for custom resource
wait = WaitCondition("cr-ready").wait_for_custom_resource("apps/v1", "CustomApp", "my-app")

# Wait for operator resource
wait = WaitCondition("operator-ready").wait_for_custom_resource("operators.coreos.com/v1", "Subscription", "my-operator")
```

#### custom_resource_condition(condition: str) -> WaitCondition
Wait for specific custom resource condition.

```python
# Wait for ready condition
wait = WaitCondition("cr-ready").custom_resource_condition("Ready")

# Wait for available condition
wait = WaitCondition("cr-ready").custom_resource_condition("Available")
```

### Timeout and Retry Configuration

#### timeout(seconds: int) -> WaitCondition
Set the timeout for wait conditions.

```python
# 5 minute timeout
wait = WaitCondition("app-ready").timeout(300)

# 10 minute timeout
wait = WaitCondition("app-ready").timeout(600)
```

#### retry_interval(seconds: int) -> WaitCondition
Set the retry interval for wait conditions.

```python
# 10 second retry interval
wait = WaitCondition("app-ready").retry_interval(10)

# 30 second retry interval
wait = WaitCondition("app-ready").retry_interval(30)
```

#### max_retries(retries: int) -> WaitCondition
Set the maximum number of retries.

```python
# 10 retries
wait = WaitCondition("app-ready").max_retries(10)

# 30 retries
wait = WaitCondition("app-ready").max_retries(30)
```

#### backoff_policy(policy: str) -> WaitCondition
Set the backoff policy for retries.

```python
# Exponential backoff
wait = WaitCondition("app-ready").backoff_policy("exponential")

# Linear backoff
wait = WaitCondition("app-ready").backoff_policy("linear")

# Fixed backoff
wait = WaitCondition("app-ready").backoff_policy("fixed")
```

### Health Check Wait Conditions

#### wait_for_health_check(url: str) -> WaitCondition
Wait for a health check endpoint to be ready.

```python
# Wait for app health check
wait = WaitCondition("health-ready").wait_for_health_check("http://app:8080/health")

# Wait for database health check
wait = WaitCondition("health-ready").wait_for_health_check("http://db:5432/health")
```

#### health_check_method(method: str) -> WaitCondition
Set the HTTP method for health checks.

```python
# GET method
wait = WaitCondition("health-ready").health_check_method("GET")

# POST method
wait = WaitCondition("health-ready").health_check_method("POST")
```

#### health_check_headers(headers: Dict[str, str]) -> WaitCondition
Set headers for health checks.

```python
# Set health check headers
headers = {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
}
wait = WaitCondition("health-ready").health_check_headers(headers)
```

#### health_check_status_code(status_code: int) -> WaitCondition
Set expected status code for health checks.

```python
# Expect 200 status code
wait = WaitCondition("health-ready").health_check_status_code(200)

# Expect 201 status code
wait = WaitCondition("health-ready").health_check_status_code(201)
```

### Dependency Management

#### depends_on(resource: str) -> WaitCondition
Set dependency on another resource.

```python
# Wait for database before app
wait = WaitCondition("app-ready").depends_on("database")

# Wait for multiple dependencies
wait = WaitCondition("app-ready").depends_on("database").depends_on("redis")
```

#### dependency_order(order: List[str]) -> WaitCondition
Set the order of dependencies.

```python
# Set dependency order
wait = WaitCondition("app-ready").dependency_order(["database", "redis", "app"])
```

#### parallel_wait(enabled: bool = True) -> WaitCondition
Enable or disable parallel waiting.

```python
# Enable parallel waiting
wait = WaitCondition("app-ready").parallel_wait(True)

# Disable parallel waiting
wait = WaitCondition("app-ready").parallel_wait(False)
```

### Advanced Configuration

#### namespace(namespace: str) -> WaitCondition
Set the namespace for the wait condition.

```python
wait = WaitCondition("app-ready").namespace("production")
```

#### add_label(key: str, value: str) -> WaitCondition
Add a label to the wait condition.

```python
wait = WaitCondition("app-ready").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> WaitCondition
Add multiple labels to the wait condition.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "wait"
}
wait = WaitCondition("app-ready").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> WaitCondition
Add an annotation to the wait condition.

```python
wait = WaitCondition("app-ready").add_annotation("description", "Application ready condition")
```

#### add_annotations(annotations: Dict[str, str]) -> WaitCondition
Add multiple annotations to the wait condition.

```python
annotations = {
    "description": "Application ready condition for production",
    "owner": "platform-team",
    "wait-type": "deployment"
}
wait = WaitCondition("app-ready").add_annotations(annotations)
```

#### failure_action(action: str) -> WaitCondition
Set action on wait failure.

```python
# Retry on failure
wait = WaitCondition("app-ready").failure_action("retry")

# Fail on timeout
wait = WaitCondition("app-ready").failure_action("fail")

# Continue on failure
wait = WaitCondition("app-ready").failure_action("continue")
```

#### success_action(action: str) -> WaitCondition
Set action on wait success.

```python
# Continue on success
wait = WaitCondition("app-ready").success_action("continue")

# Notify on success
wait = WaitCondition("app-ready").success_action("notify")
```

### Output Generation

#### generate() -> WaitConditionGenerator
Generate the wait condition configuration.

```python
# Generate Kubernetes YAML
wait.generate().to_yaml("./k8s/")

# Generate Helm values
wait.generate().to_helm_values("./helm/")

# Generate Terraform
wait.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready wait condition configuration:

```python
from celestra import WaitCondition

# Create comprehensive wait condition configuration
production_wait = (WaitCondition("production-ready")
    .wait_for_deployment("app")
    .deployment_ready_condition("Available")
    .deployment_replicas(3)
    .wait_for_service("app-service")
    .service_endpoints(3)
    .wait_for_pod("database")
    .pod_phase("Running")
    .pod_ready_condition("Ready")
    .wait_for_statefulset("database")
    .statefulset_replicas(3)
    .wait_for_job("db-migration")
    .job_completion_condition("Complete")
    .wait_for_configmap("app-config")
    .wait_for_secret("app-secret")
    .wait_for_custom_resource("apps/v1", "CustomApp", "my-app")
    .custom_resource_condition("Ready")
    .wait_for_health_check("http://app:8080/health")
    .health_check_method("GET")
    .health_check_status_code(200)
    .health_check_headers({
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
    })
    .depends_on("database")
    .dependency_order(["database", "redis", "app"])
    .parallel_wait(False)
    .timeout(600)
    .retry_interval(10)
    .max_retries(30)
    .backoff_policy("exponential")
    .failure_action("retry")
    .success_action("continue")
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "wait"
    })
    .add_annotations({
        "description": "Production ready condition",
        "owner": "platform-team@company.com",
        "wait-type": "deployment"
    }))

# Generate manifests
production_wait.generate().to_yaml("./k8s/")
```

## Wait Condition Patterns

### Deployment Ready Pattern
```python
# Wait for deployment to be ready
deployment_wait = (WaitCondition("deployment-ready")
    .wait_for_deployment("app")
    .deployment_ready_condition("Available")
    .deployment_replicas(3)
    .timeout(300)
    .retry_interval(10))
```

### Service Ready Pattern
```python
# Wait for service to be ready
service_wait = (WaitCondition("service-ready")
    .wait_for_service("app-service")
    .service_endpoints(3)
    .timeout(60)
    .retry_interval(5))
```

### Database Ready Pattern
```python
# Wait for database to be ready
db_wait = (WaitCondition("db-ready")
    .wait_for_statefulset("database")
    .statefulset_replicas(3)
    .wait_for_pod("database")
    .pod_phase("Running")
    .timeout(600)
    .retry_interval(30))
```

### Job Completion Pattern
```python
# Wait for job to complete
job_wait = (WaitCondition("job-ready")
    .wait_for_job("db-migration")
    .job_completion_condition("Complete")
    .timeout(1800)
    .retry_interval(60))
```

### Health Check Pattern
```python
# Wait for health check
health_wait = (WaitCondition("health-ready")
    .wait_for_health_check("http://app:8080/health")
    .health_check_method("GET")
    .health_check_status_code(200)
    .timeout(300)
    .retry_interval(10))
```

### Dependency Chain Pattern
```python
# Wait for dependency chain
dependency_wait = (WaitCondition("dependency-ready")
    .depends_on("database")
    .depends_on("redis")
    .dependency_order(["database", "redis", "app"])
    .parallel_wait(False)
    .timeout(900))
```

## Best Practices

### 1. **Set Appropriate Timeouts**
```python
# ✅ Good: Set appropriate timeouts
wait = WaitCondition("app-ready").timeout(300)

# ❌ Bad: No timeout
wait = WaitCondition("app-ready")  # No timeout
```

### 2. **Use Retry Intervals**
```python
# ✅ Good: Use retry intervals
wait = WaitCondition("app-ready").retry_interval(10)

# ❌ Bad: No retry interval
wait = WaitCondition("app-ready")  # No retry interval
```

### 3. **Set Maximum Retries**
```python
# ✅ Good: Set maximum retries
wait = WaitCondition("app-ready").max_retries(30)

# ❌ Bad: No retry limit
wait = WaitCondition("app-ready")  # No retry limit
```

### 4. **Use Dependency Order**
```python
# ✅ Good: Use dependency order
wait = WaitCondition("app-ready").dependency_order(["database", "redis", "app"])

# ❌ Bad: No dependency order
wait = WaitCondition("app-ready")  # No dependency order
```

### 5. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
wait = WaitCondition("app-ready").wait_for_health_check("http://app:8080/health")

# ❌ Bad: No health checks
wait = WaitCondition("app-ready")  # No health checks
```

### 6. **Set Failure Actions**
```python
# ✅ Good: Set failure actions
wait = WaitCondition("app-ready").failure_action("retry")

# ❌ Bad: No failure action
wait = WaitCondition("app-ready")  # No failure action
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Deployment](../workloads/deployment.md)** - For deployment management
- **[Service](../networking/service.md)** - For service discovery
- **[Health](../networking/health.md)** - For health checks

## Next Steps

- **[DeploymentStrategy](deployment-strategy.md)** - Learn about deployment strategies
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 