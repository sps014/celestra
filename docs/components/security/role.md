# Role Class

The `Role` class manages Kubernetes Roles that define permissions within a namespace.

## Overview

```python
from celestra import Role

# Basic usage
role = Role("app-role").allow_read_only("pods", "services")
```

## Functions

### add_rule(api_groups: List[str], resources: List[str], verbs: List[str], resource_names: Optional[List[str]] = None) -> Role
Add a rule to the role.

```python
# Add custom rule
role = Role("app-role").add_rule(
    api_groups=[""],
    resources=["pods", "services"],
    verbs=["get", "list", "watch"]
)

# Add rule with specific resource names
role = Role("secret-manager").add_rule(
    api_groups=[""],
    resources=["secrets"],
    verbs=["get", "list", "watch"],
    resource_names=["app-secret", "api-secret"]
)
```

### allow_get(*resources: str, api_group: str = "") -> Role
Allow GET operations on resources.

```python
# Allow get on pods
role = Role("pod-reader").allow_get("pods")

# Allow get on multiple resources
role = Role("app-reader").allow_get("pods", "services", "configmaps")
```

### allow_list(*resources: str, api_group: str = "") -> Role
Allow LIST operations on resources.

```python
# Allow list on pods
role = Role("pod-lister").allow_list("pods")

# Allow list on multiple resources
role = Role("app-lister").allow_list("pods", "services", "configmaps")
```

### allow_watch(*resources: str, api_group: str = "") -> Role
Allow WATCH operations on resources.

```python
# Allow watch on pods
role = Role("pod-watcher").allow_watch("pods")

# Allow watch on multiple resources
role = Role("app-watcher").allow_watch("pods", "services", "configmaps")
```

### allow_create(*resources: str, api_group: str = "") -> Role
Allow CREATE operations on resources.

```python
# Allow create on pods
role = Role("pod-creator").allow_create("pods")

# Allow create on multiple resources
role = Role("app-creator").allow_create("pods", "services", "configmaps")
```

### allow_update(*resources: str, api_group: str = "") -> Role
Allow UPDATE operations on resources.

```python
# Allow update on pods
role = Role("pod-updater").allow_update("pods")

# Allow update on multiple resources
role = Role("app-updater").allow_update("pods", "services", "configmaps")
```

### allow_patch(*resources: str, api_group: str = "") -> Role
Allow PATCH operations on resources.

```python
# Allow patch on pods
role = Role("pod-patcher").allow_patch("pods")

# Allow patch on multiple resources
role = Role("app-patcher").allow_patch("pods", "services", "configmaps")
```

### allow_delete(*resources: str, api_group: str = "") -> Role
Allow DELETE operations on resources.

```python
# Allow delete on pods
role = Role("pod-deleter").allow_delete("pods")

# Allow delete on multiple resources
role = Role("app-deleter").allow_delete("pods", "services", "configmaps")
```

### allow_all(*resources: str, api_group: str = "") -> Role
Allow all operations on resources.

```python
# Allow all operations on pods
role = Role("pod-admin").allow_all("pods")

# Allow all operations on multiple resources
role = Role("app-admin").allow_all("pods", "services", "configmaps")
```

### allow_read_only(*resources: str, api_group: str = "") -> Role
Allow read-only operations (get, list, watch) on resources.

```python
# Allow read-only on pods
role = Role("pod-reader").allow_read_only("pods")

# Allow read-only on multiple resources
role = Role("app-reader").allow_read_only("pods", "services", "configmaps")
```

### Convenience Methods

#### Pod Reader
```python
# Create pod reader role
role = Role.pod_reader("myapp-pod-reader")
```

#### Secret Manager
```python
# Create secret manager role
role = Role.secret_manager("myapp-secret-manager")
```

#### Config Reader
```python
# Create config reader role
role = Role.config_reader("myapp-config-reader")
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete Role Example - Production Application Roles
"""

from celestra import Role, KubernetesOutput

def create_production_roles():
    """Create production-ready roles."""
    
    # Application reader role
    app_reader = (Role("app-reader")
        .allow_read_only("pods", "services", "configmaps")
        .label("app", "myapp")
        .label("environment", "production"))
    
    # Application writer role
    app_writer = (Role("app-writer")
        .allow_all("pods", "services", "configmaps")
        .allow_read_only("secrets")
        .label("app", "myapp")
        .label("environment", "production"))
    
    # Secret manager role
    secret_manager = (Role("secret-manager")
        .allow_all("secrets")
        .label("app", "myapp")
        .label("environment", "production"))
    
    # Database role
    db_role = (Role("database-role")
        .allow_read_only("pods")
        .allow_create("pods")
        .allow_update("pods")
        .label("app", "database")
        .label("environment", "production"))
    
    # Monitoring role
    monitor_role = (Role("monitor-role")
        .allow_read_only("pods", "services", "nodes")
        .allow_get("metrics.k8s.io", api_group="metrics.k8s.io")
        .label("app", "monitoring")
        .label("environment", "production"))
    
    return [app_reader, app_writer, secret_manager, db_role, monitor_role]

if __name__ == "__main__":
    roles = create_production_roles()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    for role in roles:
        output.generate(role, "production-roles/")
    
    print("✅ Production roles generated!")
    print("🚀 Deploy: kubectl apply -f production-roles/")
```

## Generated Kubernetes Resources

The Role class generates the following Kubernetes resources:

- **Role** - Kubernetes Role with the specified rules and permissions

## Usage Patterns

### Read-Only Role

```python
# Read-only role for applications
reader_role = Role("app-reader").allow_read_only("pods", "services", "configmaps")
```

### Writer Role

```python
# Writer role for applications
writer_role = Role("app-writer").allow_all("pods", "services", "configmaps")
```

### Secret Manager Role

```python
# Secret management role
secret_role = Role("secret-manager").allow_all("secrets")
```

### Database Role

```python
# Database-specific role
db_role = Role("database-role").allow_read_only("pods").allow_create("pods")
```

### Monitoring Role

```python
# Monitoring role
monitor_role = Role("monitor-role").allow_read_only("pods", "services", "nodes")
```

## Best Practices

### 1. Follow Principle of Least Privilege

```python
# ✅ Good: Minimal permissions
role = Role("app-reader").allow_read_only("pods", "services")

# ❌ Bad: Too many permissions
role = Role("app-role").allow_all("pods", "services", "secrets", "nodes")
```

### 2. Use Descriptive Names

```python
# ✅ Good: Descriptive name
role = Role("myapp-pod-reader")

# ❌ Bad: Generic name
role = Role("role")
```

### 3. Group Related Resources

```python
# ✅ Good: Group related resources
role = Role("app-role").allow_read_only("pods", "services", "configmaps")

# ❌ Bad: Scattered permissions
role = Role("app-role").allow_read_only("pods")
role.allow_read_only("services")
```

### 4. Use Convenience Methods

```python
# ✅ Good: Use convenience methods
role = Role.pod_reader("myapp-pod-reader")

# ❌ Bad: Manual rule creation
role = Role("pod-reader").add_rule(["", ""], ["pods"], ["get", "list", "watch"])
```

### 5. Add Labels for Organization

```python
# ✅ Good: Add labels
role = Role("app-role").label("app", "myapp").label("environment", "production")

# ❌ Bad: No labels
role = Role("app-role")
``` 