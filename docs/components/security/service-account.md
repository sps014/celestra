# ServiceAccount Class

The `ServiceAccount` class manages Kubernetes ServiceAccounts that provide identity for processes running in pods and control access to the Kubernetes API.

## Overview

```python
from celestra import ServiceAccount

# Basic usage
sa = ServiceAccount("app-service-account").automount_token(True)
```

## Functions

### add_secret(secret_name: str) -> ServiceAccount
Add a secret to the service account.

```python
# Add a secret
sa = ServiceAccount("app-sa").add_secret("app-token")

# Add multiple secrets
sa = (ServiceAccount("app-sa")
    .add_secret("app-token")
    .add_secret("api-key")
    .add_secret("database-credentials"))
```

### add_image_pull_secret(secret_name: str) -> ServiceAccount
Add an image pull secret to the service account.

```python
# Add image pull secret
sa = ServiceAccount("app-sa").add_image_pull_secret("registry-secret")

# Add multiple image pull secrets
sa = (ServiceAccount("app-sa")
    .add_image_pull_secret("registry-secret")
    .add_image_pull_secret("gcr-secret"))
```

### automount_token(enabled: bool) -> ServiceAccount
Set whether to automount the service account token.

```python
# Enable automount (default)
sa = ServiceAccount("app-sa").automount_token(True)

# Disable automount
sa = ServiceAccount("app-sa").automount_token(False)
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete ServiceAccount Example - Production Application Service Account
"""

from celestra import ServiceAccount, KubernetesOutput

def create_production_service_accounts():
    """Create production-ready service accounts."""
    
    # Application service account
    app_sa = (ServiceAccount("app-service-account")
        .add_secret("app-token")
        .add_secret("api-credentials")
        .add_image_pull_secret("registry-secret")
        .automount_token(True)
        .label("app", "myapp")
        .label("environment", "production"))
    
    # Database service account
    db_sa = (ServiceAccount("db-service-account")
        .add_secret("db-credentials")
        .add_image_pull_secret("registry-secret")
        .automount_token(False)  # Disable for security
        .label("app", "database")
        .label("environment", "production"))
    
    # Monitoring service account
    monitor_sa = (ServiceAccount("monitor-service-account")
        .add_secret("monitor-token")
        .add_image_pull_secret("registry-secret")
        .automount_token(True)
        .label("app", "monitoring")
        .label("environment", "production"))
    
    return [app_sa, db_sa, monitor_sa]

if __name__ == "__main__":
    service_accounts = create_production_service_accounts()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    for sa in service_accounts:
        output.generate(sa, "production-service-accounts/")
    
    print("✅ Production service accounts generated!")
    print("🚀 Deploy: kubectl apply -f production-service-accounts/")
```

## Generated Kubernetes Resources

The ServiceAccount class generates the following Kubernetes resources:

- **ServiceAccount** - Kubernetes ServiceAccount with the specified configuration

## Usage Patterns

### Application Service Account

```python
# Basic application service account
app_sa = (ServiceAccount("app-sa")
    .add_secret("app-token")
    .automount_token(True))
```

### Database Service Account

```python
# Database service account with credentials
db_sa = (ServiceAccount("db-sa")
    .add_secret("db-credentials")
    .add_image_pull_secret("registry-secret")
    .automount_token(False))  # Disable for security
```

### Monitoring Service Account

```python
# Monitoring service account
monitor_sa = (ServiceAccount("monitor-sa")
    .add_secret("monitor-token")
    .add_image_pull_secret("registry-secret")
    .automount_token(True))
```

## Best Practices

### 1. Use Descriptive Names

```python
# ✅ Good: Descriptive name
sa = ServiceAccount("myapp-api-service-account")

# ❌ Bad: Generic name
sa = ServiceAccount("sa")
```

### 2. Disable Automount for Security

```python
# ✅ Good: Disable automount for sensitive workloads
db_sa = ServiceAccount("db-sa").automount_token(False)

# ❌ Bad: Always enable automount
db_sa = ServiceAccount("db-sa").automount_token(True)
```

### 3. Add Image Pull Secrets

```python
# ✅ Good: Add image pull secrets
sa = ServiceAccount("app-sa").add_image_pull_secret("registry-secret")

# ❌ Bad: No image pull secrets
sa = ServiceAccount("app-sa")
```

### 4. Use Labels for Organization

```python
# ✅ Good: Add labels
sa = ServiceAccount("app-sa").label("app", "myapp").label("environment", "production")

# ❌ Bad: No labels
sa = ServiceAccount("app-sa")
``` 