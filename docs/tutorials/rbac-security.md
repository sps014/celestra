# RBAC Security Tutorial

**⭐⭐⭐ Difficulty:** Intermediate | **⏱️ Time:** 15 minutes

Implement comprehensive Role-Based Access Control (RBAC) security for your Kubernetes applications using K8s-Gen DSL.

## What You'll Learn

- Create ServiceAccounts for applications
- Define Roles and ClusterRoles with specific permissions
- Bind roles to users and service accounts
- Implement security policies and best practices
- Set up multi-tenant access control

## Prerequisites

- K8s-Gen DSL installed
- Understanding of Kubernetes RBAC concepts
- kubectl access with admin privileges

## Architecture Overview

```
Users/Apps → ServiceAccounts → RoleBindings → Roles → Resources
                               ↓
                        ClusterRoleBindings → ClusterRoles → Cluster Resources
```

## Step 1: Create Service Accounts

Start by creating service accounts for different application components:

```python
from k8s_gen import ServiceAccount

# Web application service account
web_sa = (ServiceAccount("web-app-sa")
    .add_label("app", "web-application")
    .add_label("tier", "frontend")
    .add_annotation("description", "Service account for web application")
    .automount_token(True))

# API service account
api_sa = (ServiceAccount("api-server-sa")
    .add_label("app", "api-server")
    .add_label("tier", "backend")
    .add_annotation("description", "Service account for API server")
    .automount_token(True))

# Database service account
db_sa = (ServiceAccount("database-sa")
    .add_label("app", "database")
    .add_label("tier", "data")
    .add_annotation("description", "Service account for database")
    .automount_token(False))  # Database doesn't need API access

print("✅ Service accounts created")
```

## Step 2: Define Application Roles

Create roles with specific permissions for each application tier:

```python
from k8s_gen import Role

# Web application role - minimal read permissions
web_role = (Role("web-app-role")
    .allow_get("configmaps", "secrets")
    .allow_list("services", "endpoints")
    .allow_watch("pods")
    .add_label("component", "rbac")
    .add_label("tier", "frontend"))

# API server role - broader permissions for backend operations
api_role = (Role("api-server-role")
    .allow_get("configmaps", "secrets", "services")
    .allow_list("pods", "endpoints", "persistentvolumeclaims")
    .allow_watch("pods", "services")
    .allow_create("events")
    .allow_update("configmaps")
    .add_label("component", "rbac")
    .add_label("tier", "backend"))

# Database role - storage-focused permissions
db_role = (Role("database-role")
    .allow_get("persistentvolumeclaims", "persistentvolumes")
    .allow_list("persistentvolumeclaims")
    .allow_create("events")
    .add_label("component", "rbac")
    .add_label("tier", "data"))

print("✅ Application roles defined")
```

## Step 3: Create Cluster Roles

Define cluster-wide roles for special purposes:

```python
from k8s_gen import ClusterRole

# Monitoring role - read-only access to cluster resources
monitoring_role = (ClusterRole("monitoring-role")
    .allow_read_only("nodes", "nodes/metrics", "nodes/stats")
    .allow_get("namespaces", "pods", "services", "endpoints")
    .allow_list("persistentvolumes", "storageclasses")
    .add_label("purpose", "monitoring"))

# Deployment role - for CI/CD systems
deployment_role = (ClusterRole("deployment-role")
    .allow_get("namespaces")
    .allow_create("deployments", "services", "configmaps", "secrets")
    .allow_update("deployments", "services")
    .allow_delete("deployments", "services")
    .add_label("purpose", "deployment"))

print("✅ Cluster roles defined")
```

## Step 4: Bind Roles to Service Accounts

Connect service accounts to their respective roles:

```python
from k8s_gen import RoleBinding, ClusterRoleBinding

# Bind application roles to service accounts
web_binding = RoleBinding("web-app-binding", web_role, web_sa)
api_binding = RoleBinding("api-server-binding", api_role, api_sa)
db_binding = RoleBinding("database-binding", db_role, db_sa)

# Bind cluster roles (example: monitoring service account)
monitoring_sa = ServiceAccount("monitoring-sa")
monitoring_binding = ClusterRoleBinding("monitoring-binding", monitoring_role, monitoring_sa)

print("✅ Role bindings created")
```

## Step 5: Apply Security Policies

Configure security policies for the applications:

```python
from k8s_gen import SecurityPolicy

# Application security policy
app_security = (SecurityPolicy("app-security-policy")
    .enable_rbac()
    .pod_security_standards("baseline")
    .network_policies(enabled=True)
    .admission_controllers(["PodSecurityPolicy", "ResourceQuota"])
    .audit_logging(enabled=True))

# Strict security policy for production
prod_security = (SecurityPolicy("production-security")
    .enable_rbac()
    .pod_security_standards("restricted")
    .network_policies(enabled=True)
    .admission_controllers(["PodSecurityPolicy", "ResourceQuota", "LimitRanger"])
    .audit_logging(enabled=True)
    .security_context_constraints(run_as_non_root=True))

print("✅ Security policies configured")
```

## Step 6: Create Applications with RBAC

Apply the security configuration to your applications:

```python
from k8s_gen import App, StatefulApp

# Web application with RBAC
web_app = (App("secure-web-app")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .service_account(web_sa)
    .security_context(run_as_non_root=True, run_as_user=1000)
    .resources(cpu="100m", memory="128Mi")
    .replicas(2))

# API server with RBAC
api_app = (App("secure-api-server")
    .image("python:3.9-slim")
    .port(8080, "api")
    .service_account(api_sa)
    .security_context(run_as_non_root=True, run_as_user=1000)
    .resources(cpu="200m", memory="512Mi")
    .replicas(2))

# Database with RBAC
database = (StatefulApp("secure-database")
    .image("postgres:14")
    .port(5432, "postgres")
    .service_account(db_sa)
    .security_context(run_as_non_root=True, run_as_user=999)
    .storage("/var/lib/postgresql/data", "10Gi")
    .resources(cpu="500m", memory="1Gi"))

print("✅ Secure applications created")
```

## Step 7: Complete RBAC Example

Here's the complete security setup:

```python
#!/usr/bin/env python3
"""
RBAC Security Demo - Comprehensive security setup with K8s-Gen DSL
"""

from k8s_gen import (
    App, StatefulApp, ServiceAccount, Role, ClusterRole,
    RoleBinding, ClusterRoleBinding, SecurityPolicy,
    KubernetesOutput
)

def create_rbac_setup():
    """Create a comprehensive RBAC security setup."""
    
    # 1. Service Accounts
    web_sa = (ServiceAccount("web-app-sa")
        .add_label("app", "web-application")
        .add_annotation("description", "Service account for web application"))
    
    api_sa = (ServiceAccount("api-server-sa")
        .add_label("app", "api-server")
        .add_annotation("description", "Service account for API server"))
    
    db_sa = (ServiceAccount("database-sa")
        .add_label("app", "database")
        .add_annotation("description", "Service account for database")
        .automount_token(False))
    
    # 2. Roles with specific permissions
    web_role = (Role("web-app-role")
        .allow_get("configmaps", "secrets")
        .allow_list("services", "endpoints"))
    
    api_role = (Role("api-server-role")
        .allow_get("configmaps", "secrets", "services")
        .allow_list("pods", "endpoints")
        .allow_create("events"))
    
    db_role = (Role("database-role")
        .allow_get("persistentvolumeclaims")
        .allow_create("events"))
    
    # 3. Cluster Role for monitoring
    monitoring_role = (ClusterRole("monitoring-role")
        .allow_read_only("nodes", "nodes/metrics")
        .allow_get("namespaces", "pods", "services"))
    
    # 4. Role Bindings
    web_binding = RoleBinding("web-app-binding", web_role, web_sa)
    api_binding = RoleBinding("api-server-binding", api_role, api_sa)
    db_binding = RoleBinding("database-binding", db_role, db_sa)
    
    monitoring_sa = ServiceAccount("monitoring-sa")
    monitoring_binding = ClusterRoleBinding("monitoring-binding", monitoring_role, monitoring_sa)
    
    # 5. Security Policy
    security_policy = (SecurityPolicy("rbac-security")
        .enable_rbac()
        .pod_security_standards("baseline")
        .network_policies(enabled=True))
    
    # 6. Secure Applications
    web_app = (App("secure-web-app")
        .image("nginx:1.21-alpine")
        .port(80, "http")
        .service_account(web_sa)
        .security_context(run_as_non_root=True, run_as_user=1000)
        .resources(cpu="100m", memory="128Mi")
        .replicas(2))
    
    api_app = (App("secure-api-server")
        .image("python:3.9-slim")
        .port(8080, "api")
        .service_account(api_sa)
        .security_context(run_as_non_root=True, run_as_user=1000)
        .resources(cpu="200m", memory="512Mi")
        .replicas(2))
    
    database = (StatefulApp("secure-database")
        .image("postgres:14")
        .port(5432, "postgres")
        .service_account(db_sa)
        .security_context(run_as_non_root=True, run_as_user=999)
        .storage("/var/lib/postgresql/data", "10Gi")
        .resources(cpu="500m", memory="1Gi"))
    
    return [
        # Service Accounts
        web_sa, api_sa, db_sa, monitoring_sa,
        # Roles
        web_role, api_role, db_role, monitoring_role,
        # Bindings
        web_binding, api_binding, db_binding, monitoring_binding,
        # Applications
        web_app, api_app, database
    ]

def main():
    """Generate RBAC security configuration."""
    print("🔒 Creating RBAC Security Configuration")
    print("=" * 45)
    
    # Create all components
    components = create_rbac_setup()
    
    # Generate manifests
    output = KubernetesOutput()
    all_resources = []
    
    for component in components:
        resources = component.generate_kubernetes_resources()
        all_resources.extend(resources)
    
    # Save to file
    output.write_all_resources(all_resources, "rbac-security.yaml")
    
    print(f"✅ Generated {len(all_resources)} Kubernetes resources")
    print("📄 Saved to: rbac-security.yaml")
    print("\n🔒 Security components created:")
    print("   • 4 ServiceAccounts")
    print("   • 3 Roles + 1 ClusterRole")
    print("   • 4 RoleBindings")
    print("   • 3 Secure Applications")
    print("\n🚀 Deploy with:")
    print("   kubectl apply -f rbac-security.yaml")

if __name__ == "__main__":
    main()
```

## Step 8: Verify RBAC Setup

After deployment, verify the security configuration:

```bash
# Deploy the configuration
kubectl apply -f rbac-security.yaml

# Check service accounts
kubectl get serviceaccounts

# Check roles and bindings
kubectl get roles
kubectl get rolebindings
kubectl get clusterroles | grep monitoring
kubectl get clusterrolebindings | grep monitoring

# Verify applications are using service accounts
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.serviceAccountName}{"\n"}{end}'

# Test permissions (example: check if web app can list secrets)
kubectl auth can-i list secrets --as=system:serviceaccount:default:web-app-sa
```

## Best Practices

### 🔒 **Principle of Least Privilege**
- Grant only the minimum permissions required
- Use namespace-scoped roles when possible
- Avoid cluster-admin unless absolutely necessary

### 🏷️ **Naming Conventions**
- Use descriptive names: `web-app-sa`, `database-role`
- Include purpose in cluster roles: `monitoring-role`, `deployment-role`
- Group related resources with labels

### 📋 **Permission Verification**
```python
# Test specific permissions
def verify_permissions():
    """Verify RBAC permissions are working correctly."""
    test_commands = [
        "kubectl auth can-i get configmaps --as=system:serviceaccount:default:web-app-sa",
        "kubectl auth can-i create deployments --as=system:serviceaccount:default:api-server-sa",
        "kubectl auth can-i delete pods --as=system:serviceaccount:default:database-sa"
    ]
    
    for cmd in test_commands:
        print(f"Testing: {cmd}")
```

### 🔄 **Regular Auditing**
- Review service account usage regularly
- Audit role permissions quarterly
- Monitor authentication and authorization events

## Advanced RBAC Patterns

### Multi-Tenant Setup
```python
# Tenant-specific roles
tenant_a_role = (Role("tenant-a-role")
    .allow_get("*")
    .allow_list("*")
    .resource_names(["tenant-a-*"]))

tenant_b_role = (Role("tenant-b-role")
    .allow_get("*")
    .allow_list("*")
    .resource_names(["tenant-b-*"]))
```

### Dynamic Role Assignment
```python
# Use labels for dynamic role assignment
dynamic_binding = (RoleBinding("dynamic-binding", api_role)
    .bind_service_accounts_with_label("tier", "backend"))
```

## Troubleshooting

### Permission Denied Errors
```bash
# Check what permissions a service account has
kubectl auth can-i --list --as=system:serviceaccount:default:web-app-sa

# Check role binding details
kubectl describe rolebinding web-app-binding
```

### Service Account Not Working
```bash
# Verify service account exists
kubectl get serviceaccount web-app-sa

# Check if pod is using correct service account
kubectl get pod <pod-name> -o yaml | grep serviceAccountName
```

## Key Concepts Learned

✅ **ServiceAccounts**: Identity for applications  
✅ **Roles**: Namespace-scoped permissions  
✅ **ClusterRoles**: Cluster-wide permissions  
✅ **RoleBindings**: Connect roles to identities  
✅ **Security Policies**: Enforce security standards  
✅ **Least Privilege**: Minimal required permissions  
✅ **Multi-tenant Security**: Isolation between tenants  

## Next Steps

Enhance your security knowledge:

1. **[Microservices Security](microservices.md)** - Multi-service RBAC
2. **[Observability Stack](observability-stack.md)** - Monitoring security
3. **[Multi-Environment](multi-environment.md)** - Environment-specific security
4. **[Advanced Features](../advanced/index.md)** - Security scanning and policies

---

**Congratulations!** You've implemented comprehensive RBAC security for your applications. Your Kubernetes workloads now follow security best practices with proper access controls.
