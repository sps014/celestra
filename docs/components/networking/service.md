# Service Class

The `Service` class manages network access to applications by creating Kubernetes Services. It provides load balancing, service discovery, and network policies for your applications.

## Overview

```python
from celestra import Service

# Basic usage
service = Service("web-service").type("ClusterIP").add_port("http", 80, 8080)

# Production service with load balancer
service = (Service("api-service")
    .type("LoadBalancer")
    .add_port("https", 443, 8443)
    .selector({"app": "api"}))
```

## Core API Functions

### Service Type Configuration

#### Type
Set the service type (ClusterIP, NodePort, LoadBalancer, ExternalName).

```python
# ClusterIP (default) - internal access only
service = Service("internal-service").type("ClusterIP")

# NodePort - accessible via node IP
service = Service("node-service").type("NodePort")

# LoadBalancer - external access via cloud load balancer
service = Service("external-service").type("LoadBalancer")

# ExternalName - DNS alias to external service
service = Service("external-api").type("ExternalName")
```

### Port Configuration

#### Add Port
Add a port to the service with name, port, target port, and protocol.

```python
# Basic port configuration
service = Service("web-service").add_port("http", 80, 8080)

# Named port with protocol
service = Service("api-service").add_port("https", 443, 8443, "TCP")

# Multiple ports
service = (Service("multi-service")
    .add_port("http", 80, 8080, "TCP")
    .add_port("https", 443, 8443, "TCP")
    .add_port("metrics", 9090, 9090, "TCP"))
```

### Selector Configuration

#### Selector
Set the pod selector to determine which pods the service targets.

```python
# Select by app label
service = Service("api-service").selector({"app": "api"})

# Select by multiple labels
service = Service("web-service").selector({
    "app": "web",
    "tier": "frontend",
    "environment": "production"
})

# Select by component label
service = Service("database-service").selector({"component": "database"})
```

### Advanced Configuration

#### Namespace
Set the namespace for the service.

```python
service = Service("api-service").namespace("production")
```

#### Add Label
Add a label to the service.

```python
service = Service("api-service").add_label("environment", "production")
service = Service("api-service").add_label("tier", "backend")
```

#### Add Labels
Add multiple labels to the service.

```python
labels = {
    "environment": "production",
    "tier": "backend",
    "team": "platform"
}
service = Service("api-service").add_labels(labels)
```

#### Add Annotation
Add an annotation to the service.

```python
service = Service("api-service").add_annotation("description", "API service")
```

#### Add Annotations
Add multiple annotations to the service.

```python
annotations = {
    "description": "API service for production",
    "owner": "platform-team",
    "service-type": "load-balanced"
}
service = Service("api-service").add_annotations(annotations)
```

### Output Generation

#### Generate Configuration
Generate the service configuration.

```python
# Generate Kubernetes YAML
service.generate().to_yaml("./k8s/")

# Generate Helm values
service.generate().to_helm_values("./helm/")

# Generate Terraform
service.generate().to_terraform("./terraform/")
```

## Usage Examples

### Basic Service Types

```python
from celestra import Service

# ClusterIP (default) - internal access only
internal_service = Service("api-internal").type("ClusterIP")

# NodePort - accessible via node IP
node_service = Service("api-node").type("NodePort")

# LoadBalancer - external access via cloud load balancer
external_service = Service("api-external").type("LoadBalancer")

# ExternalName - DNS alias to external service
external_api = Service("external-api").type("ExternalName")
```

### Port Configuration Examples

```python
# Basic port
service = Service("web-service").add_port("http", 80, 8080)

# Named port with protocol
service = Service("api-service").add_port("https", 443, 8443, "TCP")

# Multiple ports
service = (Service("multi-service")
    .add_port("http", 80, 8080, "TCP")
    .add_port("https", 443, 8443, "TCP")
    .add_port("metrics", 9090, 9090, "TCP"))
```

### Selector Examples

```python
# Select by app label
service = Service("api-service").selector({"app": "api"})

# Select by multiple labels
service = Service("web-service").selector({
    "app": "web",
    "tier": "frontend",
    "environment": "production"
})

# Select by component label
service = Service("database-service").selector({"component": "database"})
```

### Complete Production Example

```python
from celestra import Service

# Production API service
api_service = (Service("api-service")
    .type("LoadBalancer")
    .add_port("http", 80, 8080, "TCP")
    .add_port("https", 443, 8443, "TCP")
    .add_port("metrics", 9090, 9090, "TCP")
    .selector({"app": "api", "tier": "backend"})
    .add_label("environment", "production")
    .add_label("team", "platform")
    .add_annotation("description", "Production API service")
    .namespace("production"))

# Internal database service
db_service = (Service("database-service")
    .type("ClusterIP")
    .add_port("postgres", 5432, 5432, "TCP")
    .selector({"app": "database", "component": "postgres"})
    .add_label("environment", "production")
    .add_label("tier", "data")
    .namespace("databases"))

# External service alias
external_api = (Service("external-api")
    .type("ExternalName")
    .add_annotation("description", "External API service")
    .namespace("external"))
```

## Service Types

### ClusterIP
Default service type for internal communication.

```python
# Internal service
service = Service("api-internal").type("ClusterIP")
```

### NodePort
Exposes the service on each Node's IP at a static port.

```python
# Node port service
service = Service("api-node").type("NodePort")
```

### LoadBalancer
Exposes the service externally using the cloud provider's load balancer.

```python
# Load balancer service
service = Service("api-external").type("LoadBalancer")
```

### ExternalName
Maps the service to the contents of the externalName field.

```python
# External service alias
service = Service("external-api").type("ExternalName")
```

## Best Practices

### 1. **Use Appropriate Service Types**
```python
# ✅ Good: Use ClusterIP for internal services
internal_service = Service("api-internal").type("ClusterIP")

# ✅ Good: Use LoadBalancer for external services
external_service = Service("api-external").type("LoadBalancer")

# ❌ Bad: Don't use LoadBalancer for internal-only services
internal_service = Service("api-internal").type("LoadBalancer")  # Unnecessary cost
```

### 2. **Use Descriptive Port Names**
```python
# ✅ Good: Use descriptive port names
service = Service("api-service").add_port("https", 443, 8443)

# ❌ Bad: Use generic port names
service = Service("api-service").add_port("port", 443, 8443)
```

### 3. **Use Specific Selectors**
```python
# ✅ Good: Use specific selectors
service = Service("api-service").selector({
    "app": "api",
    "tier": "backend",
    "environment": "production"
})

# ❌ Bad: Use overly broad selectors
service = Service("api-service").selector({"app": "api"})  # Too broad
```

### 4. **Add Meaningful Labels and Annotations**
```python
# ✅ Good: Add meaningful metadata
service = (Service("api-service")
    .add_label("environment", "production")
    .add_label("team", "platform")
    .add_annotation("description", "Production API service"))

# ❌ Bad: No metadata
service = Service("api-service")  # No labels or annotations
```

### 5. **Use Namespaces Appropriately**
```python
# ✅ Good: Use namespaces for organization
service = Service("api-service").namespace("production")

# ❌ Bad: Always use default namespace
service = Service("api-service")  # Default namespace
```

## Generated Kubernetes Resources

The Service class generates the following Kubernetes resources:

- **Service** - Kubernetes Service with the specified type, ports, and selectors

## Usage Patterns

### Microservices Pattern

```python
# API service
api_service = (Service("api-service")
    .type("LoadBalancer")
    .add_port("http", 80, 8080)
    .selector({"app": "api"}))

# Database service
db_service = (Service("database-service")
    .type("ClusterIP")
    .add_port("postgres", 5432, 5432)
    .selector({"app": "database"}))
```

### Multi-Tier Pattern

```python
# Frontend service
frontend_service = (Service("frontend-service")
    .type("LoadBalancer")
    .add_port("http", 80, 3000)
    .selector({"tier": "frontend"}))

# Backend service
backend_service = (Service("backend-service")
    .type("ClusterIP")
    .add_port("http", 80, 8080)
    .selector({"tier": "backend"}))
```

### External Service Pattern

```python
# External API service
external_api = (Service("external-api")
    .type("ExternalName")
    .add_annotation("description", "External API service"))
```

## Related Components

- **[App](app.md)** - For stateless applications
- **[StatefulApp](stateful-app.md)** - For stateful applications
- **[Ingress](ingress.md)** - For HTTP/HTTPS routing
- **[NetworkPolicy](network-policy.md)** - For network security policies
- **[Health](health.md)** - For health check configuration

## Next Steps

- **[App](app.md)** - Learn about stateless applications
- **[StatefulApp](stateful-app.md)** - Learn about stateful applications
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 