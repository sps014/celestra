# CustomResource Class

The `CustomResource` class manages custom Kubernetes resources and Custom Resource Definitions (CRDs). It provides capabilities for defining custom resources, operators, and extending Kubernetes functionality.

## Overview

```python
from celestra import CustomResource

# Basic custom resource
cr = CustomResource("my-app").api_version("apps/v1").kind("CustomApp")

# Production custom resource with validation
cr = (CustomResource("production-app")
    .api_version("apps/v1")
    .kind("CustomApp")
    .schema_validation(True)
    .webhook_validation(True))
```

## Core API Functions

### Basic Configuration

#### api_version(version: str) -> CustomResource
Set the API version for the custom resource.

```python
# Apps API version
cr = CustomResource("my-app").api_version("apps/v1")

# Custom API version
cr = CustomResource("my-app").api_version("mycompany.com/v1")

# Operator API version
cr = CustomResource("my-app").api_version("operators.coreos.com/v1")
```

#### kind(kind: str) -> CustomResource
Set the kind for the custom resource.

```python
# Custom app kind
cr = CustomResource("my-app").kind("CustomApp")

# Database kind
cr = CustomResource("my-db").kind("Database")

# Operator kind
cr = CustomResource("my-operator").kind("Subscription")
```

#### group(group: str) -> CustomResource
Set the API group for the custom resource.

```python
# Apps group
cr = CustomResource("my-app").group("apps")

# Custom group
cr = CustomResource("my-app").group("mycompany.com")

# Operator group
cr = CustomResource("my-operator").group("operators.coreos.com")
```

#### version(version: str) -> CustomResource
Set the version for the custom resource.

```python
# v1 version
cr = CustomResource("my-app").version("v1")

# v1alpha1 version
cr = CustomResource("my-app").version("v1alpha1")

# v1beta1 version
cr = CustomResource("my-app").version("v1beta1")
```

### Schema Configuration

#### schema_validation(enabled: bool = True) -> CustomResource
Enable or disable schema validation.

```python
# Enable schema validation
cr = CustomResource("my-app").schema_validation(True)

# Disable schema validation
cr = CustomResource("my-app").schema_validation(False)
```

#### schema_properties(properties: Dict[str, Any]) -> CustomResource
Set schema properties for the custom resource.

```python
# Set schema properties
properties = {
    "spec": {
        "type": "object",
        "properties": {
            "replicas": {"type": "integer", "minimum": 1},
            "image": {"type": "string"},
            "port": {"type": "integer", "minimum": 1, "maximum": 65535}
        },
        "required": ["replicas", "image"]
    }
}
cr = CustomResource("my-app").schema_properties(properties)
```

#### schema_required(required: List[str]) -> CustomResource
Set required fields for the schema.

```python
# Set required fields
cr = CustomResource("my-app").schema_required(["replicas", "image", "port"])
```

#### schema_additional_properties(additional: bool = False) -> CustomResource
Allow additional properties in schema.

```python
# Allow additional properties
cr = CustomResource("my-app").schema_additional_properties(True)

# Disallow additional properties
cr = CustomResource("my-app").schema_additional_properties(False)
```

### Webhook Configuration

#### webhook_validation(enabled: bool = True) -> CustomResource
Enable or disable webhook validation.

```python
# Enable webhook validation
cr = CustomResource("my-app").webhook_validation(True)

# Disable webhook validation
cr = CustomResource("my-app").webhook_validation(False)
```

#### webhook_url(url: str) -> CustomResource
Set webhook URL for validation.

```python
# Set webhook URL
cr = CustomResource("my-app").webhook_url("https://webhook.example.com/validate")

# Local webhook URL
cr = CustomResource("my-app").webhook_url("https://webhook-service.default.svc/validate")
```

#### webhook_timeout(seconds: int) -> CustomResource
Set webhook timeout.

```python
# 30 second timeout
cr = CustomResource("my-app").webhook_timeout(30)

# 60 second timeout
cr = CustomResource("my-app").webhook_timeout(60)
```

#### webhook_failure_policy(policy: str) -> CustomResource
Set webhook failure policy.

```python
# Ignore failures
cr = CustomResource("my-app").webhook_failure_policy("Ignore")

# Fail on webhook failure
cr = CustomResource("my-app").webhook_failure_policy("Fail")
```

### Conversion Configuration

#### conversion_enabled(enabled: bool = True) -> CustomResource
Enable or disable conversion webhook.

```python
# Enable conversion
cr = CustomResource("my-app").conversion_enabled(True)

# Disable conversion
cr = CustomResource("my-app").conversion_enabled(False)
```

#### conversion_url(url: str) -> CustomResource
Set conversion webhook URL.

```python
# Set conversion URL
cr = CustomResource("my-app").conversion_url("https://webhook.example.com/convert")

# Local conversion URL
cr = CustomResource("my-app").conversion_url("https://webhook-service.default.svc/convert")
```

#### conversion_strategy(strategy: str) -> CustomResource
Set conversion strategy.

```python
# Webhook conversion
cr = CustomResource("my-app").conversion_strategy("Webhook")

# None conversion
cr = CustomResource("my-app").conversion_strategy("None")
```

### Storage Configuration

#### storage_version(version: str) -> CustomResource
Set the storage version.

```python
# v1 storage version
cr = CustomResource("my-app").storage_version("v1")

# v1alpha1 storage version
cr = CustomResource("my-app").storage_version("v1alpha1")
```

#### served_versions(versions: List[str]) -> CustomResource
Set served versions.

```python
# Multiple served versions
cr = CustomResource("my-app").served_versions(["v1", "v1alpha1"])

# Single served version
cr = CustomResource("my-app").served_versions(["v1"])
```

#### deprecated_versions(versions: List[str]) -> CustomResource
Set deprecated versions.

```python
# Deprecated versions
cr = CustomResource("my-app").deprecated_versions(["v1alpha1"])

# No deprecated versions
cr = CustomResource("my-app").deprecated_versions([])
```

### Printer Columns

#### printer_columns(columns: List[Dict[str, Any]]) -> CustomResource
Set printer columns for kubectl output.

```python
# Set printer columns
columns = [
    {"name": "Replicas", "type": "integer", "jsonPath": ".spec.replicas"},
    {"name": "Image", "type": "string", "jsonPath": ".spec.image"},
    {"name": "Age", "type": "date", "jsonPath": ".metadata.creationTimestamp"}
]
cr = CustomResource("my-app").printer_columns(columns)
```

#### add_printer_column(name: str, type: str, json_path: str) -> CustomResource
Add a printer column.

```python
# Add replicas column
cr = CustomResource("my-app").add_printer_column("Replicas", "integer", ".spec.replicas")

# Add image column
cr = CustomResource("my-app").add_printer_column("Image", "string", ".spec.image")
```

### Subresources

#### subresources_enabled(enabled: bool = True) -> CustomResource
Enable or disable subresources.

```python
# Enable subresources
cr = CustomResource("my-app").subresources_enabled(True)

# Disable subresources
cr = CustomResource("my-app").subresources_enabled(False)
```

#### status_subresource(enabled: bool = True) -> CustomResource
Enable or disable status subresource.

```python
# Enable status subresource
cr = CustomResource("my-app").status_subresource(True)

# Disable status subresource
cr = CustomResource("my-app").status_subresource(False)
```

#### scale_subresource(enabled: bool = True) -> CustomResource
Enable or disable scale subresource.

```python
# Enable scale subresource
cr = CustomResource("my-app").scale_subresource(True)

# Disable scale subresource
cr = CustomResource("my-app").scale_subresource(False)
```

### Categories and Short Names

#### categories(categories: List[str]) -> CustomResource
Set categories for the custom resource.

```python
# Set categories
cr = CustomResource("my-app").categories(["all", "apps"])

# Single category
cr = CustomResource("my-app").categories(["all"])
```

#### short_names(short_names: List[str]) -> CustomResource
Set short names for the custom resource.

```python
# Set short names
cr = CustomResource("my-app").short_names(["app", "apps"])

# Single short name
cr = CustomResource("my-app").short_names(["app"])
```

### Operator Configuration

#### operator_enabled(enabled: bool = True) -> CustomResource
Enable or disable operator functionality.

```python
# Enable operator
cr = CustomResource("my-app").operator_enabled(True)

# Disable operator
cr = CustomResource("my-app").operator_enabled(False)
```

#### operator_reconcile_period(seconds: int) -> CustomResource
Set operator reconcile period.

```python
# 30 second reconcile period
cr = CustomResource("my-app").operator_reconcile_period(30)

# 60 second reconcile period
cr = CustomResource("my-app").operator_reconcile_period(60)
```

#### operator_finalizers(finalizers: List[str]) -> CustomResource
Set operator finalizers.

```python
# Set finalizers
cr = CustomResource("my-app").operator_finalizers(["mycompany.com/finalizer"])

# No finalizers
cr = CustomResource("my-app").operator_finalizers([])
```

### Advanced Configuration

#### namespace(namespace: str) -> CustomResource
Set the namespace for the custom resource.

```python
cr = CustomResource("my-app").namespace("production")
```

#### add_label(key: str, value: str) -> CustomResource
Add a label to the custom resource.

```python
cr = CustomResource("my-app").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> CustomResource
Add multiple labels to the custom resource.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "custom"
}
cr = CustomResource("my-app").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> CustomResource
Add an annotation to the custom resource.

```python
cr = CustomResource("my-app").add_annotation("description", "Custom application resource")
```

#### add_annotations(annotations: Dict[str, str]) -> CustomResource
Add multiple annotations to the custom resource.

```python
annotations = {
    "description": "Custom application resource for production",
    "owner": "platform-team",
    "crd-type": "application"
}
cr = CustomResource("my-app").add_annotations(annotations)
```

#### preserve_unknown_fields(preserve: bool = True) -> CustomResource
Preserve unknown fields.

```python
# Preserve unknown fields
cr = CustomResource("my-app").preserve_unknown_fields(True)

# Don't preserve unknown fields
cr = CustomResource("my-app").preserve_unknown_fields(False)
```

#### x_kubernetes_list_type(list_type: str) -> CustomResource
Set Kubernetes list type.

```python
# Set list type
cr = CustomResource("my-app").x_kubernetes_list_type("set")

# Map list type
cr = CustomResource("my-app").x_kubernetes_list_type("map")
```

### Output Generation

#### generate() -> CustomResourceGenerator
Generate the custom resource configuration.

```python
# Generate Kubernetes YAML
cr.generate().to_yaml("./k8s/")

# Generate Helm values
cr.generate().to_helm_values("./helm/")

# Generate Terraform
cr.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready custom resource configuration:

```python
from celestra import CustomResource

# Create comprehensive custom resource configuration
production_cr = (CustomResource("production-app")
    .api_version("apps/v1")
    .kind("CustomApp")
    .group("apps")
    .version("v1")
    .schema_validation(True)
    .schema_properties({
        "spec": {
            "type": "object",
            "properties": {
                "replicas": {"type": "integer", "minimum": 1, "maximum": 10},
                "image": {"type": "string"},
                "port": {"type": "integer", "minimum": 1, "maximum": 65535},
                "resources": {
                    "type": "object",
                    "properties": {
                        "cpu": {"type": "string"},
                        "memory": {"type": "string"}
                    }
                }
            },
            "required": ["replicas", "image", "port"]
        },
        "status": {
            "type": "object",
            "properties": {
                "availableReplicas": {"type": "integer"},
                "readyReplicas": {"type": "integer"},
                "replicas": {"type": "integer"}
            }
        }
    })
    .schema_required(["replicas", "image", "port"])
    .schema_additional_properties(False)
    .webhook_validation(True)
    .webhook_url("https://webhook-service.default.svc/validate")
    .webhook_timeout(30)
    .webhook_failure_policy("Fail")
    .conversion_enabled(True)
    .conversion_url("https://webhook-service.default.svc/convert")
    .conversion_strategy("Webhook")
    .storage_version("v1")
    .served_versions(["v1", "v1alpha1"])
    .deprecated_versions(["v1alpha1"])
    .printer_columns([
        {"name": "Replicas", "type": "integer", "jsonPath": ".spec.replicas"},
        {"name": "Image", "type": "string", "jsonPath": ".spec.image"},
        {"name": "Port", "type": "integer", "jsonPath": ".spec.port"},
        {"name": "Ready", "type": "integer", "jsonPath": ".status.readyReplicas"},
        {"name": "Age", "type": "date", "jsonPath": ".metadata.creationTimestamp"}
    ])
    .subresources_enabled(True)
    .status_subresource(True)
    .scale_subresource(True)
    .categories(["all", "apps"])
    .short_names(["app", "apps"])
    .operator_enabled(True)
    .operator_reconcile_period(30)
    .operator_finalizers(["apps.mycompany.com/finalizer"])
    .preserve_unknown_fields(False)
    .x_kubernetes_list_type("set")
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "custom"
    })
    .add_annotations({
        "description": "Custom application resource for production",
        "owner": "platform-team@company.com",
        "crd-type": "application"
    }))

# Generate manifests
production_cr.generate().to_yaml("./k8s/")
```

## Custom Resource Patterns

### Application CRD Pattern
```python
# Application CRD pattern
app_crd = (CustomResource("app")
    .api_version("apps/v1")
    .kind("CustomApp")
    .schema_validation(True)
    .schema_properties({
        "spec": {
            "type": "object",
            "properties": {
                "replicas": {"type": "integer", "minimum": 1},
                "image": {"type": "string"},
                "port": {"type": "integer"}
            },
            "required": ["replicas", "image", "port"]
        }
    })
    .printer_columns([
        {"name": "Replicas", "type": "integer", "jsonPath": ".spec.replicas"},
        {"name": "Image", "type": "string", "jsonPath": ".spec.image"}
    ]))
```

### Database CRD Pattern
```python
# Database CRD pattern
db_crd = (CustomResource("database")
    .api_version("databases/v1")
    .kind("Database")
    .schema_validation(True)
    .schema_properties({
        "spec": {
            "type": "object",
            "properties": {
                "type": {"type": "string", "enum": ["postgresql", "mysql", "redis"]},
                "version": {"type": "string"},
                "size": {"type": "string"}
            },
            "required": ["type", "version"]
        }
    })
    .status_subresource(True)
    .scale_subresource(True))
```

### Operator CRD Pattern
```python
# Operator CRD pattern
operator_crd = (CustomResource("operator")
    .api_version("operators.coreos.com/v1")
    .kind("Subscription")
    .operator_enabled(True)
    .operator_reconcile_period(30)
    .operator_finalizers(["operators.coreos.com/finalizer"])
    .webhook_validation(True)
    .conversion_enabled(True))
```

### Monitoring CRD Pattern
```python
# Monitoring CRD pattern
monitoring_crd = (CustomResource("monitoring")
    .api_version("monitoring.coreos.com/v1")
    .kind("ServiceMonitor")
    .schema_validation(True)
    .webhook_validation(True)
    .categories(["monitoring"]))
```

## Best Practices

### 1. **Use Schema Validation**
```python
# ✅ Good: Enable schema validation
cr = CustomResource("my-app").schema_validation(True)

# ❌ Bad: No schema validation
cr = CustomResource("my-app")  # No validation
```

### 2. **Set Required Fields**
```python
# ✅ Good: Set required fields
cr = CustomResource("my-app").schema_required(["replicas", "image"])

# ❌ Bad: No required fields
cr = CustomResource("my-app")  # No required fields
```

### 3. **Configure Printer Columns**
```python
# ✅ Good: Configure printer columns
cr = CustomResource("my-app").printer_columns([
    {"name": "Replicas", "type": "integer", "jsonPath": ".spec.replicas"}
])

# ❌ Bad: No printer columns
cr = CustomResource("my-app")  # No printer columns
```

### 4. **Enable Status Subresource**
```python
# ✅ Good: Enable status subresource
cr = CustomResource("my-app").status_subresource(True)

# ❌ Bad: No status subresource
cr = CustomResource("my-app")  # No status subresource
```

### 5. **Use Webhook Validation**
```python
# ✅ Good: Use webhook validation
cr = CustomResource("my-app").webhook_validation(True)

# ❌ Bad: No webhook validation
cr = CustomResource("my-app")  # No webhook validation
```

### 6. **Set Appropriate Categories**
```python
# ✅ Good: Set appropriate categories
cr = CustomResource("my-app").categories(["all", "apps"])

# ❌ Bad: No categories
cr = CustomResource("my-app")  # No categories
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Deployment](../workloads/deployment.md)** - For deployment management
- **[WaitCondition](wait-condition.md)** - For wait conditions
- **[DeploymentStrategy](deployment-strategy.md)** - For deployment strategies

## Next Steps

- **[DependencyManager](dependency-manager.md)** - Learn about dependency management
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 