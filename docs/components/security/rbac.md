# RBAC Components

The RBAC (Role-Based Access Control) components manage access control in Kubernetes. This includes `ServiceAccount`, `Role`, `ClusterRole`, `RoleBinding`, and `ClusterRoleBinding` for fine-grained access control.

## Overview

```python
from celestra import ServiceAccount, Role, RoleBinding, ClusterRole, ClusterRoleBinding

# Basic RBAC setup
sa = ServiceAccount("api-sa")
role = Role("api-role").add_policy("get", "pods").add_policy("list", "services")
binding = RoleBinding("api-binding").bind_role(role).bind_service_account(sa)

# Production RBAC with cluster roles
cluster_role = ClusterRole("api-cluster-role").add_policy("get", "pods", "services", "configmaps")
cluster_binding = ClusterRoleBinding("api-cluster-binding").bind_cluster_role(cluster_role).bind_service_account(sa)
```

## ServiceAccount Class

The `ServiceAccount` class creates Kubernetes ServiceAccounts for pod identity and authentication.

### Core API Functions

#### namespace(namespace: str) -> ServiceAccount
Set the namespace for the service account.

```python
sa = ServiceAccount("api-sa").namespace("production")
```

#### add_label(key: str, value: str) -> ServiceAccount
Add a label to the service account.

```python
sa = ServiceAccount("api-sa").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> ServiceAccount
Add multiple labels to the service account.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "backend"
}
sa = ServiceAccount("api-sa").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> ServiceAccount
Add an annotation to the service account.

```python
sa = ServiceAccount("api-sa").add_annotation("description", "API service account")
```

#### add_annotations(annotations: Dict[str, str]) -> ServiceAccount
Add multiple annotations to the service account.

```python
annotations = {
    "description": "API service account for production",
    "owner": "platform-team",
    "rotation-schedule": "monthly"
}
sa = ServiceAccount("api-sa").add_annotations(annotations)
```

#### image_pull_secrets(secrets: List[str]) -> ServiceAccount
Add image pull secrets to the service account.

```python
sa = ServiceAccount("api-sa").image_pull_secrets(["registry-secret", "gcr-secret"])
```

#### add_image_pull_secret(secret: str) -> ServiceAccount
Add a single image pull secret.

```python
sa = ServiceAccount("api-sa").add_image_pull_secret("registry-secret")
```

#### automount_service_account_token(enabled: bool = True) -> ServiceAccount
Configure automounting of service account token.

```python
sa = ServiceAccount("api-sa").automount_service_account_token(True)
```

#### generate() -> ServiceAccountGenerator
Generate the service account configuration.

```python
# Generate Kubernetes YAML
sa.generate().to_yaml("./k8s/")
```

## Role Class

The `Role` class creates Kubernetes Roles for namespace-scoped permissions.

### Core API Functions

#### namespace(namespace: str) -> Role
Set the namespace for the role.

```python
role = Role("api-role").namespace("production")
```

#### add_policy(verb: str, *resources: str) -> Role
Add a policy rule to the role.

```python
# Single resource
role = Role("api-role").add_policy("get", "pods")

# Multiple resources
role = Role("api-role").add_policy("get", "pods", "services", "configmaps")

# Multiple verbs
role = Role("api-role").add_policy("get", "pods").add_policy("list", "pods")
```

#### add_policies(policies: List[Dict[str, Any]]) -> Role
Add multiple policy rules at once.

```python
policies = [
    {"verbs": ["get", "list"], "resources": ["pods", "services"]},
    {"verbs": ["create", "update"], "resources": ["configmaps"]},
    {"verbs": ["watch"], "resources": ["events"]}
]
role = Role("api-role").add_policies(policies)
```

#### allow_all(verbs: List[str] = None, resources: List[str] = None) -> Role
Allow all operations on specified resources.

```python
# Allow all operations on all resources
role = Role("admin-role").allow_all()

# Allow specific verbs on all resources
role = Role("read-role").allow_all(verbs=["get", "list", "watch"])

# Allow all verbs on specific resources
role = Role("pod-role").allow_all(resources=["pods", "pods/log"])
```

#### allow_read_only() -> Role
Allow read-only access to all resources.

```python
role = Role("read-only-role").allow_read_only()
```

#### allow_pod_access() -> Role
Allow pod-related operations.

```python
role = Role("pod-role").allow_pod_access()
```

#### allow_service_access() -> Role
Allow service-related operations.

```python
role = Role("service-role").allow_service_access()
```

#### allow_configmap_access() -> Role
Allow ConfigMap-related operations.

```python
role = Role("config-role").allow_configmap_access()
```

#### allow_secret_access() -> Role
Allow Secret-related operations.

```python
role = Role("secret-role").allow_secret_access()
```

#### allow_network_policy_access() -> Role
Allow NetworkPolicy-related operations.

```python
role = Role("network-role").allow_network_policy_access()
```

#### allow_ingress_access() -> Role
Allow Ingress-related operations.

```python
role = Role("ingress-role").allow_ingress_access()
```

#### add_label(key: str, value: str) -> Role
Add a label to the role.

```python
role = Role("api-role").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> Role
Add multiple labels to the role.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "backend"
}
role = Role("api-role").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> Role
Add an annotation to the role.

```python
role = Role("api-role").add_annotation("description", "API role")
```

#### add_annotations(annotations: Dict[str, str]) -> Role
Add multiple annotations to the role.

```python
annotations = {
    "description": "API role for production",
    "owner": "platform-team",
    "permissions": "read-only"
}
role = Role("api-role").add_annotations(annotations)
```

#### generate() -> RoleGenerator
Generate the role configuration.

```python
# Generate Kubernetes YAML
role.generate().to_yaml("./k8s/")
```

## ClusterRole Class

The `ClusterRole` class creates Kubernetes ClusterRoles for cluster-wide permissions.

### Core API Functions

#### add_policy(verb: str, *resources: str) -> ClusterRole
Add a policy rule to the cluster role.

```python
# Single resource
cluster_role = ClusterRole("api-cluster-role").add_policy("get", "pods")

# Multiple resources
cluster_role = ClusterRole("api-cluster-role").add_policy("get", "pods", "services", "configmaps")

# Multiple verbs
cluster_role = ClusterRole("api-cluster-role").add_policy("get", "pods").add_policy("list", "pods")
```

#### add_policies(policies: List[Dict[str, Any]]) -> ClusterRole
Add multiple policy rules at once.

```python
policies = [
    {"verbs": ["get", "list"], "resources": ["pods", "services"]},
    {"verbs": ["create", "update"], "resources": ["configmaps"]},
    {"verbs": ["watch"], "resources": ["events"]}
]
cluster_role = ClusterRole("api-cluster-role").add_policies(policies)
```

#### allow_all(verbs: List[str] = None, resources: List[str] = None) -> ClusterRole
Allow all operations on specified resources.

```python
# Allow all operations on all resources
cluster_role = ClusterRole("admin-cluster-role").allow_all()

# Allow specific verbs on all resources
cluster_role = ClusterRole("read-cluster-role").allow_all(verbs=["get", "list", "watch"])

# Allow all verbs on specific resources
cluster_role = ClusterRole("pod-cluster-role").allow_all(resources=["pods", "pods/log"])
```

#### allow_read_only() -> ClusterRole
Allow read-only access to all resources.

```python
cluster_role = ClusterRole("read-only-cluster-role").allow_read_only()
```

#### allow_pod_access() -> ClusterRole
Allow pod-related operations.

```python
cluster_role = ClusterRole("pod-cluster-role").allow_pod_access()
```

#### allow_service_access() -> ClusterRole
Allow service-related operations.

```python
cluster_role = ClusterRole("service-cluster-role").allow_service_access()
```

#### allow_configmap_access() -> ClusterRole
Allow ConfigMap-related operations.

```python
cluster_role = ClusterRole("config-cluster-role").allow_configmap_access()
```

#### allow_secret_access() -> ClusterRole
Allow Secret-related operations.

```python
cluster_role = ClusterRole("secret-cluster-role").allow_secret_access()
```

#### allow_network_policy_access() -> ClusterRole
Allow NetworkPolicy-related operations.

```python
cluster_role = ClusterRole("network-cluster-role").allow_network_policy_access()
```

#### allow_ingress_access() -> ClusterRole
Allow Ingress-related operations.

```python
cluster_role = ClusterRole("ingress-cluster-role").allow_ingress_access()
```

#### allow_node_access() -> ClusterRole
Allow node-related operations.

```python
cluster_role = ClusterRole("node-cluster-role").allow_node_access()
```

#### allow_namespace_access() -> ClusterRole
Allow namespace-related operations.

```python
cluster_role = ClusterRole("namespace-cluster-role").allow_namespace_access()
```

#### allow_persistent_volume_access() -> ClusterRole
Allow PersistentVolume-related operations.

```python
cluster_role = ClusterRole("pv-cluster-role").allow_persistent_volume_access()
```

#### allow_storage_class_access() -> ClusterRole
Allow StorageClass-related operations.

```python
cluster_role = ClusterRole("sc-cluster-role").allow_storage_class_access()
```

#### add_label(key: str, value: str) -> ClusterRole
Add a label to the cluster role.

```python
cluster_role = ClusterRole("api-cluster-role").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> ClusterRole
Add multiple labels to the cluster role.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "backend"
}
cluster_role = ClusterRole("api-cluster-role").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> ClusterRole
Add an annotation to the cluster role.

```python
cluster_role = ClusterRole("api-cluster-role").add_annotation("description", "API cluster role")
```

#### add_annotations(annotations: Dict[str, str]) -> ClusterRole
Add multiple annotations to the cluster role.

```python
annotations = {
    "description": "API cluster role for production",
    "owner": "platform-team",
    "permissions": "read-only"
}
cluster_role = ClusterRole("api-cluster-role").add_annotations(annotations)
```

#### generate() -> ClusterRoleGenerator
Generate the cluster role configuration.

```python
# Generate Kubernetes YAML
cluster_role.generate().to_yaml("./k8s/")
```

## RoleBinding Class

The `RoleBinding` class creates Kubernetes RoleBindings to bind roles to subjects.

### Core API Functions

#### namespace(namespace: str) -> RoleBinding
Set the namespace for the role binding.

```python
binding = RoleBinding("api-binding").namespace("production")
```

#### bind_role(role: Role) -> RoleBinding
Bind a role to the role binding.

```python
role = Role("api-role").add_policy("get", "pods")
binding = RoleBinding("api-binding").bind_role(role)
```

#### bind_service_account(service_account: ServiceAccount) -> RoleBinding
Bind a service account to the role binding.

```python
sa = ServiceAccount("api-sa")
binding = RoleBinding("api-binding").bind_service_account(sa)
```

#### bind_service_accounts(service_accounts: List[ServiceAccount]) -> RoleBinding
Bind multiple service accounts to the role binding.

```python
sa1 = ServiceAccount("api-sa")
sa2 = ServiceAccount("worker-sa")
binding = RoleBinding("api-binding").bind_service_accounts([sa1, sa2])
```

#### bind_user(user: str) -> RoleBinding
Bind a user to the role binding.

```python
binding = RoleBinding("api-binding").bind_user("john.doe@company.com")
```

#### bind_users(users: List[str]) -> RoleBinding
Bind multiple users to the role binding.

```python
binding = RoleBinding("api-binding").bind_users(["john.doe@company.com", "jane.smith@company.com"])
```

#### bind_group(group: str) -> RoleBinding
Bind a group to the role binding.

```python
binding = RoleBinding("api-binding").bind_group("developers")
```

#### bind_groups(groups: List[str]) -> RoleBinding
Bind multiple groups to the role binding.

```python
binding = RoleBinding("api-binding").bind_groups(["developers", "platform-team"])
```

#### add_label(key: str, value: str) -> RoleBinding
Add a label to the role binding.

```python
binding = RoleBinding("api-binding").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> RoleBinding
Add multiple labels to the role binding.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "backend"
}
binding = RoleBinding("api-binding").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> RoleBinding
Add an annotation to the role binding.

```python
binding = RoleBinding("api-binding").add_annotation("description", "API role binding")
```

#### add_annotations(annotations: Dict[str, str]) -> RoleBinding
Add multiple annotations to the role binding.

```python
annotations = {
    "description": "API role binding for production",
    "owner": "platform-team",
    "permissions": "read-only"
}
binding = RoleBinding("api-binding").add_annotations(annotations)
```

#### generate() -> RoleBindingGenerator
Generate the role binding configuration.

```python
# Generate Kubernetes YAML
binding.generate().to_yaml("./k8s/")
```

## ClusterRoleBinding Class

The `ClusterRoleBinding` class creates Kubernetes ClusterRoleBindings to bind cluster roles to subjects.

### Core API Functions

#### bind_cluster_role(cluster_role: ClusterRole) -> ClusterRoleBinding
Bind a cluster role to the cluster role binding.

```python
cluster_role = ClusterRole("api-cluster-role").add_policy("get", "pods")
binding = ClusterRoleBinding("api-cluster-binding").bind_cluster_role(cluster_role)
```

#### bind_service_account(service_account: ServiceAccount) -> ClusterRoleBinding
Bind a service account to the cluster role binding.

```python
sa = ServiceAccount("api-sa")
binding = ClusterRoleBinding("api-cluster-binding").bind_service_account(sa)
```

#### bind_service_accounts(service_accounts: List[ServiceAccount]) -> ClusterRoleBinding
Bind multiple service accounts to the cluster role binding.

```python
sa1 = ServiceAccount("api-sa")
sa2 = ServiceAccount("worker-sa")
binding = ClusterRoleBinding("api-cluster-binding").bind_service_accounts([sa1, sa2])
```

#### bind_user(user: str) -> ClusterRoleBinding
Bind a user to the cluster role binding.

```python
binding = ClusterRoleBinding("api-cluster-binding").bind_user("john.doe@company.com")
```

#### bind_users(users: List[str]) -> ClusterRoleBinding
Bind multiple users to the cluster role binding.

```python
binding = ClusterRoleBinding("api-cluster-binding").bind_users(["john.doe@company.com", "jane.smith@company.com"])
```

#### bind_group(group: str) -> ClusterRoleBinding
Bind a group to the cluster role binding.

```python
binding = ClusterRoleBinding("api-cluster-binding").bind_group("developers")
```

#### bind_groups(groups: List[str]) -> ClusterRoleBinding
Bind multiple groups to the cluster role binding.

```python
binding = ClusterRoleBinding("api-cluster-binding").bind_groups(["developers", "platform-team"])
```

#### add_label(key: str, value: str) -> ClusterRoleBinding
Add a label to the cluster role binding.

```python
binding = ClusterRoleBinding("api-cluster-binding").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> ClusterRoleBinding
Add multiple labels to the cluster role binding.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "backend"
}
binding = ClusterRoleBinding("api-cluster-binding").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> ClusterRoleBinding
Add an annotation to the cluster role binding.

```python
binding = ClusterRoleBinding("api-cluster-binding").add_annotation("description", "API cluster role binding")
```

#### add_annotations(annotations: Dict[str, str]) -> ClusterRoleBinding
Add multiple annotations to the cluster role binding.

```python
annotations = {
    "description": "API cluster role binding for production",
    "owner": "platform-team",
    "permissions": "read-only"
}
binding = ClusterRoleBinding("api-cluster-binding").add_annotations(annotations)
```

#### generate() -> ClusterRoleBindingGenerator
Generate the cluster role binding configuration.

```python
# Generate Kubernetes YAML
binding.generate().to_yaml("./k8s/")
```

## Complete Example

Here's a complete example of a production RBAC setup:

```python
from celestra import ServiceAccount, Role, RoleBinding, ClusterRole, ClusterRoleBinding

# Create service account
api_sa = (ServiceAccount("api-sa")
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "backend"
    })
    .add_annotations({
        "description": "API service account for production",
        "owner": "platform-team@company.com"
    }))

# Create namespace-scoped role
api_role = (Role("api-role")
    .namespace("production")
    .add_policy("get", "pods")
    .add_policy("list", "pods", "services", "configmaps")
    .add_policy("watch", "pods", "services")
    .add_policy("create", "configmaps")
    .add_policy("update", "configmaps")
    .add_labels({
        "environment": "production",
        "team": "platform"
    })
    .add_annotations({
        "description": "API role for production",
        "permissions": "read-pods-services-configmaps"
    }))

# Create role binding
api_binding = (RoleBinding("api-binding")
    .namespace("production")
    .bind_role(api_role)
    .bind_service_account(api_sa)
    .add_labels({
        "environment": "production",
        "team": "platform"
    })
    .add_annotations({
        "description": "API role binding for production"
    }))

# Create cluster role for cross-namespace access
api_cluster_role = (ClusterRole("api-cluster-role")
    .add_policy("get", "pods")
    .add_policy("list", "pods", "services")
    .add_policy("watch", "pods", "services")
    .add_labels({
        "environment": "production",
        "team": "platform"
    })
    .add_annotations({
        "description": "API cluster role for production",
        "permissions": "read-pods-services-cluster-wide"
    }))

# Create cluster role binding
api_cluster_binding = (ClusterRoleBinding("api-cluster-binding")
    .bind_cluster_role(api_cluster_role)
    .bind_service_account(api_sa)
    .add_labels({
        "environment": "production",
        "team": "platform"
    })
    .add_annotations({
        "description": "API cluster role binding for production"
    }))

# Generate manifests
api_sa.generate().to_yaml("./k8s/")
api_role.generate().to_yaml("./k8s/")
api_binding.generate().to_yaml("./k8s/")
api_cluster_role.generate().to_yaml("./k8s/")
api_cluster_binding.generate().to_yaml("./k8s/")
```

## Common RBAC Patterns

### Read-Only Access
```python
# Service account with read-only access
read_sa = ServiceAccount("read-sa").namespace("production")
read_role = Role("read-role").namespace("production").allow_read_only()
read_binding = RoleBinding("read-binding").namespace("production").bind_role(read_role).bind_service_account(read_sa)
```

### Pod Management Access
```python
# Service account with pod management access
pod_sa = ServiceAccount("pod-sa").namespace("production")
pod_role = Role("pod-role").namespace("production").allow_pod_access()
pod_binding = RoleBinding("pod-binding").namespace("production").bind_role(pod_role).bind_service_account(pod_sa)
```

### Admin Access
```python
# Service account with admin access
admin_sa = ServiceAccount("admin-sa").namespace("production")
admin_role = Role("admin-role").namespace("production").allow_all()
admin_binding = RoleBinding("admin-binding").namespace("production").bind_role(admin_role).bind_service_account(admin_sa)
```

### Cross-Namespace Access
```python
# Service account with cross-namespace access
cross_sa = ServiceAccount("cross-sa").namespace("production")
cross_cluster_role = ClusterRole("cross-cluster-role").allow_read_only()
cross_cluster_binding = ClusterRoleBinding("cross-cluster-binding").bind_cluster_role(cross_cluster_role).bind_service_account(cross_sa)
```

## Best Practices

### 1. **Use Least Privilege Principle**
```python
# ✅ Good: Grant only necessary permissions
role = Role("api-role").add_policy("get", "pods").add_policy("list", "services")

# ❌ Bad: Grant excessive permissions
role = Role("api-role").allow_all()
```

### 2. **Use Namespace-Scoped Roles When Possible**
```python
# ✅ Good: Use namespace-scoped roles for namespace-specific access
role = Role("api-role").namespace("production").add_policy("get", "pods")

# ❌ Bad: Use cluster roles for namespace-specific access
cluster_role = ClusterRole("api-cluster-role").add_policy("get", "pods")
```

### 3. **Use Descriptive Names**
```python
# ✅ Good: Use descriptive names
sa = ServiceAccount("api-production-sa")
role = Role("api-read-pods-role")

# ❌ Bad: Use generic names
sa = ServiceAccount("sa")
role = Role("role")
```

### 4. **Add Labels and Annotations**
```python
# ✅ Good: Add metadata for organization
sa = ServiceAccount("api-sa").add_labels({"environment": "production", "team": "platform"})
role = Role("api-role").add_annotations({"description": "API role for production"})

# ❌ Bad: No metadata
sa = ServiceAccount("api-sa")
role = Role("api-role")
```

### 5. **Use Service Accounts for Applications**
```python
# ✅ Good: Use service accounts for applications
sa = ServiceAccount("api-sa")
binding = RoleBinding("api-binding").bind_service_account(sa)

# ❌ Bad: Use user accounts for applications
binding = RoleBinding("api-binding").bind_user("api-user")
```

### 6. **Review and Audit Permissions**
```python
# ✅ Good: Document permissions clearly
role = Role("api-role").add_annotations({
    "description": "API role for production",
    "permissions": "read-pods-services-configmaps",
    "review-date": "2024-01-01"
})

# ❌ Bad: No documentation
role = Role("api-role")
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Secret](secrets.md)** - For managing sensitive data
- **[ConfigMap](../storage/config-map.md)** - For managing configuration data
- **[NetworkPolicy](../networking/network-policy.md)** - For network security policies

## Next Steps

- **[Secret](secrets.md)** - Learn about secret management
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 