# DependencyManager Class

The `DependencyManager` class manages dependencies and resource ordering in Kubernetes. It provides capabilities for managing resource dependencies, ensuring proper deployment order, and handling complex dependency chains.

## Overview

```python
from celestra import DependencyManager

# Basic dependency management
deps = DependencyManager("app-deps").depends_on("database").depends_on("redis")

# Production dependency management with ordering
deps = (DependencyManager("production-deps")
    .depends_on("database")
    .depends_on("redis")
    .depends_on("app")
    .dependency_order(["database", "redis", "app"])
    .timeout(600))
```

## Core API Functions

### Basic Dependency Management

#### depends_on(resource: str) -> DependencyManager
Add a dependency on another resource.

```python
# Single dependency
deps = DependencyManager("app-deps").depends_on("database")

# Multiple dependencies
deps = DependencyManager("app-deps").depends_on("database").depends_on("redis")
```

#### dependency_order(order: List[str]) -> DependencyManager
Set the order of dependencies.

```python
# Set dependency order
deps = DependencyManager("app-deps").dependency_order(["database", "redis", "app"])

# Complex dependency order
deps = DependencyManager("app-deps").dependency_order([
    "namespace",
    "configmap",
    "secret",
    "database",
    "redis",
    "app"
])
```

#### dependency_type(type: str) -> DependencyManager
Set the type of dependency.

```python
# Hard dependency (must exist)
deps = DependencyManager("app-deps").dependency_type("hard")

# Soft dependency (optional)
deps = DependencyManager("app-deps").dependency_type("soft")

# Conditional dependency
deps = DependencyManager("app-deps").dependency_type("conditional")
```

### Resource Type Dependencies

#### depends_on_deployment(name: str) -> DependencyManager
Add dependency on a deployment.

```python
# Dependency on app deployment
deps = DependencyManager("app-deps").depends_on_deployment("app")

# Dependency on multiple deployments
deps = DependencyManager("app-deps").depends_on_deployment("frontend").depends_on_deployment("backend")
```

#### depends_on_service(name: str) -> DependencyManager
Add dependency on a service.

```python
# Dependency on app service
deps = DependencyManager("app-deps").depends_on_service("app-service")

# Dependency on database service
deps = DependencyManager("app-deps").depends_on_service("database-service")
```

#### depends_on_configmap(name: str) -> DependencyManager
Add dependency on a ConfigMap.

```python
# Dependency on app config
deps = DependencyManager("app-deps").depends_on_configmap("app-config")

# Dependency on database config
deps = DependencyManager("app-deps").depends_on_configmap("db-config")
```

#### depends_on_secret(name: str) -> DependencyManager
Add dependency on a secret.

```python
# Dependency on app secret
deps = DependencyManager("app-deps").depends_on_secret("app-secret")

# Dependency on database secret
deps = DependencyManager("app-deps").depends_on_secret("db-secret")
```

#### depends_on_persistent_volume_claim(name: str) -> DependencyManager
Add dependency on a PersistentVolumeClaim.

```python
# Dependency on database PVC
deps = DependencyManager("app-deps").depends_on_persistent_volume_claim("db-pvc")

# Dependency on app data PVC
deps = DependencyManager("app-deps").depends_on_persistent_volume_claim("app-data")
```

#### depends_on_namespace(name: str) -> DependencyManager
Add dependency on a namespace.

```python
# Dependency on namespace
deps = DependencyManager("app-deps").depends_on_namespace("production")

# Dependency on multiple namespaces
deps = DependencyManager("app-deps").depends_on_namespace("monitoring").depends_on_namespace("logging")
```

### Advanced Dependency Patterns

#### depends_on_custom_resource(api_version: str, kind: str, name: str) -> DependencyManager
Add dependency on a custom resource.

```python
# Dependency on custom app
deps = DependencyManager("app-deps").depends_on_custom_resource("apps/v1", "CustomApp", "my-app")

# Dependency on operator
deps = DependencyManager("app-deps").depends_on_custom_resource("operators.coreos.com/v1", "Subscription", "my-operator")
```

#### depends_on_job(name: str) -> DependencyManager
Add dependency on a job.

```python
# Dependency on migration job
deps = DependencyManager("app-deps").depends_on_job("db-migration")

# Dependency on backup job
deps = DependencyManager("app-deps").depends_on_job("backup-job")
```

#### depends_on_cron_job(name: str) -> DependencyManager
Add dependency on a CronJob.

```python
# Dependency on cleanup cron job
deps = DependencyManager("app-deps").depends_on_cron_job("cleanup-job")

# Dependency on backup cron job
deps = DependencyManager("app-deps").depends_on_cron_job("backup-cron")
```

### Dependency Conditions

#### dependency_condition(condition: str) -> DependencyManager
Set a condition for the dependency.

```python
# Wait for ready condition
deps = DependencyManager("app-deps").dependency_condition("Ready")

# Wait for available condition
deps = DependencyManager("app-deps").dependency_condition("Available")

# Wait for complete condition
deps = DependencyManager("app-deps").dependency_condition("Complete")
```

#### dependency_timeout(seconds: int) -> DependencyManager
Set timeout for dependency resolution.

```python
# 5 minute timeout
deps = DependencyManager("app-deps").dependency_timeout(300)

# 10 minute timeout
deps = DependencyManager("app-deps").dependency_timeout(600)
```

#### dependency_retry_interval(seconds: int) -> DependencyManager
Set retry interval for dependency checks.

```python
# 10 second retry interval
deps = DependencyManager("app-deps").dependency_retry_interval(10)

# 30 second retry interval
deps = DependencyManager("app-deps").dependency_retry_interval(30)
```

#### dependency_max_retries(retries: int) -> DependencyManager
Set maximum number of retries for dependency checks.

```python
# 10 retries
deps = DependencyManager("app-deps").dependency_max_retries(10)

# 30 retries
deps = DependencyManager("app-deps").dependency_max_retries(30)
```

### Parallel and Sequential Dependencies

#### parallel_dependencies(enabled: bool = True) -> DependencyManager
Enable or disable parallel dependency resolution.

```python
# Enable parallel dependencies
deps = DependencyManager("app-deps").parallel_dependencies(True)

# Disable parallel dependencies
deps = DependencyManager("app-deps").parallel_dependencies(False)
```

#### sequential_dependencies(enabled: bool = True) -> DependencyManager
Enable or disable sequential dependency resolution.

```python
# Enable sequential dependencies
deps = DependencyManager("app-deps").sequential_dependencies(True)

# Disable sequential dependencies
deps = DependencyManager("app-deps").sequential_dependencies(False)
```

#### dependency_group(group: str) -> DependencyManager
Group dependencies together.

```python
# Infrastructure group
deps = DependencyManager("app-deps").dependency_group("infrastructure")

# Application group
deps = DependencyManager("app-deps").dependency_group("application")
```

### Health Check Dependencies

#### depends_on_health_check(url: str) -> DependencyManager
Add dependency on a health check endpoint.

```python
# Dependency on app health check
deps = DependencyManager("app-deps").depends_on_health_check("http://app:8080/health")

# Dependency on database health check
deps = DependencyManager("app-deps").depends_on_health_check("http://db:5432/health")
```

#### health_check_method(method: str) -> DependencyManager
Set HTTP method for health checks.

```python
# GET method
deps = DependencyManager("app-deps").health_check_method("GET")

# POST method
deps = DependencyManager("app-deps").health_check_method("POST")
```

#### health_check_headers(headers: Dict[str, str]) -> DependencyManager
Set headers for health checks.

```python
# Set health check headers
headers = {
    "Authorization": "Bearer token",
    "Content-Type": "application/json"
}
deps = DependencyManager("app-deps").health_check_headers(headers)
```

#### health_check_status_code(status_code: int) -> DependencyManager
Set expected status code for health checks.

```python
# Expect 200 status code
deps = DependencyManager("app-deps").health_check_status_code(200)

# Expect 201 status code
deps = DependencyManager("app-deps").health_check_status_code(201)
```

### Dependency Resolution

#### resolve_dependencies() -> DependencyManager
Resolve all dependencies.

```python
# Resolve dependencies
deps = DependencyManager("app-deps").resolve_dependencies()
```

#### validate_dependencies() -> DependencyManager
Validate dependency configuration.

```python
# Validate dependencies
deps = DependencyManager("app-deps").validate_dependencies()
```

#### check_dependency_cycles() -> DependencyManager
Check for dependency cycles.

```python
# Check for cycles
deps = DependencyManager("app-deps").check_dependency_cycles()
```

#### generate_dependency_graph() -> DependencyManager
Generate dependency graph.

```python
# Generate dependency graph
deps = DependencyManager("app-deps").generate_dependency_graph()
```

### Advanced Configuration

#### namespace(namespace: str) -> DependencyManager
Set the namespace for the dependency manager.

```python
deps = DependencyManager("app-deps").namespace("production")
```

#### add_label(key: str, value: str) -> DependencyManager
Add a label to the dependency manager.

```python
deps = DependencyManager("app-deps").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> DependencyManager
Add multiple labels to the dependency manager.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "dependency"
}
deps = DependencyManager("app-deps").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> DependencyManager
Add an annotation to the dependency manager.

```python
deps = DependencyManager("app-deps").add_annotation("description", "Application dependencies")
```

#### add_annotations(annotations: Dict[str, str]) -> DependencyManager
Add multiple annotations to the dependency manager.

```python
annotations = {
    "description": "Application dependencies for production",
    "owner": "platform-team",
    "dependency-type": "application"
}
deps = DependencyManager("app-deps").add_annotations(annotations)
```

#### failure_action(action: str) -> DependencyManager
Set action on dependency failure.

```python
# Retry on failure
deps = DependencyManager("app-deps").failure_action("retry")

# Fail on dependency failure
deps = DependencyManager("app-deps").failure_action("fail")

# Continue on failure
deps = DependencyManager("app-deps").failure_action("continue")
```

#### success_action(action: str) -> DependencyManager
Set action on dependency success.

```python
# Continue on success
deps = DependencyManager("app-deps").success_action("continue")

# Notify on success
deps = DependencyManager("app-deps").success_action("notify")
```

### Output Generation

#### generate() -> DependencyManagerGenerator
Generate the dependency manager configuration.

```python
# Generate Kubernetes YAML
deps.generate().to_yaml("./k8s/")

# Generate Helm values
deps.generate().to_helm_values("./helm/")

# Generate Terraform
deps.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready dependency manager configuration:

```python
from celestra import DependencyManager

# Create comprehensive dependency manager configuration
production_deps = (DependencyManager("production-deps")
    .depends_on_namespace("production")
    .depends_on_configmap("app-config")
    .depends_on_secret("app-secret")
    .depends_on_persistent_volume_claim("db-pvc")
    .depends_on_deployment("database")
    .depends_on_service("database-service")
    .depends_on_deployment("redis")
    .depends_on_service("redis-service")
    .depends_on_job("db-migration")
    .depends_on_custom_resource("apps/v1", "CustomApp", "my-app")
    .depends_on_health_check("http://database:5432/health")
    .health_check_method("GET")
    .health_check_status_code(200)
    .health_check_headers({
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
    })
    .dependency_order([
        "namespace",
        "configmap",
        "secret",
        "persistent-volume-claim",
        "database",
        "database-service",
        "redis",
        "redis-service",
        "job",
        "custom-resource",
        "health-check"
    ])
    .dependency_type("hard")
    .dependency_condition("Ready")
    .dependency_timeout(600)
    .dependency_retry_interval(10)
    .dependency_max_retries(30)
    .parallel_dependencies(False)
    .sequential_dependencies(True)
    .dependency_group("infrastructure")
    .resolve_dependencies()
    .validate_dependencies()
    .check_dependency_cycles()
    .generate_dependency_graph()
    .failure_action("retry")
    .success_action("continue")
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "dependency"
    })
    .add_annotations({
        "description": "Production dependency manager",
        "owner": "platform-team@company.com",
        "dependency-type": "application"
    }))

# Generate manifests
production_deps.generate().to_yaml("./k8s/")
```

## Dependency Manager Patterns

### Infrastructure Dependency Pattern
```python
# Infrastructure dependency pattern
infra_deps = (DependencyManager("infra-deps")
    .depends_on_namespace("production")
    .depends_on_configmap("infra-config")
    .depends_on_secret("infra-secret")
    .dependency_order(["namespace", "configmap", "secret"])
    .dependency_type("hard"))
```

### Application Dependency Pattern
```python
# Application dependency pattern
app_deps = (DependencyManager("app-deps")
    .depends_on_deployment("database")
    .depends_on_service("database-service")
    .depends_on_deployment("redis")
    .depends_on_service("redis-service")
    .depends_on_deployment("app")
    .dependency_order(["database", "database-service", "redis", "redis-service", "app"])
    .parallel_dependencies(True))
```

### Database Dependency Pattern
```python
# Database dependency pattern
db_deps = (DependencyManager("db-deps")
    .depends_on_persistent_volume_claim("db-pvc")
    .depends_on_deployment("database")
    .depends_on_service("database-service")
    .depends_on_job("db-migration")
    .depends_on_health_check("http://database:5432/health")
    .dependency_timeout(600))
```

### Custom Resource Dependency Pattern
```python
# Custom resource dependency pattern
cr_deps = (DependencyManager("cr-deps")
    .depends_on_custom_resource("apps/v1", "CustomApp", "my-app")
    .depends_on_custom_resource("operators.coreos.com/v1", "Subscription", "my-operator")
    .dependency_condition("Ready")
    .dependency_type("hard"))
```

## Best Practices

### 1. **Set Appropriate Timeouts**
```python
# ✅ Good: Set appropriate timeouts
deps = DependencyManager("app-deps").dependency_timeout(600)

# ❌ Bad: No timeout
deps = DependencyManager("app-deps")  # No timeout
```

### 2. **Use Dependency Order**
```python
# ✅ Good: Use dependency order
deps = DependencyManager("app-deps").dependency_order(["database", "redis", "app"])

# ❌ Bad: No dependency order
deps = DependencyManager("app-deps")  # No dependency order
```

### 3. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
deps = DependencyManager("app-deps").depends_on_health_check("http://app:8080/health")

# ❌ Bad: No health checks
deps = DependencyManager("app-deps")  # No health checks
```

### 4. **Set Dependency Types**
```python
# ✅ Good: Set dependency types
deps = DependencyManager("app-deps").dependency_type("hard")

# ❌ Bad: No dependency type
deps = DependencyManager("app-deps")  # No dependency type
```

### 5. **Use Parallel Dependencies Appropriately**
```python
# ✅ Good: Use parallel dependencies for independent resources
deps = DependencyManager("app-deps").parallel_dependencies(True)

# ❌ Bad: Use sequential for independent resources
deps = DependencyManager("app-deps").sequential_dependencies(True)  # Slower
```

### 6. **Validate Dependencies**
```python
# ✅ Good: Validate dependencies
deps = DependencyManager("app-deps").validate_dependencies()

# ❌ Bad: No validation
deps = DependencyManager("app-deps")  # No validation
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[WaitCondition](wait-condition.md)** - For wait conditions
- **[DeploymentStrategy](deployment-strategy.md)** - For deployment strategies
- **[CustomResource](custom-resource.md)** - For custom Kubernetes resources

## Next Steps

- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 