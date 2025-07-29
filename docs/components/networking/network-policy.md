# NetworkPolicy Class

The `NetworkPolicy` class manages network security policies in Kubernetes. It provides fine-grained control over pod-to-pod communication, ingress/egress traffic, and network isolation.

## Overview

```python
from celestra import NetworkPolicy

# Basic network policy
np = NetworkPolicy("api-network-policy").deny_all().allow_from_pods({"app": "frontend"})

# Production network policy with multiple rules
np = (NetworkPolicy("production-network-policy")
    .deny_all()
    .allow_from_pods({"app": "frontend"}, ports=[80, 443])
    .allow_from_namespace("monitoring", ports=[9090])
    .allow_egress_to_pods({"app": "database"}, ports=[5432]))
```

## Core API Functions

### Policy Configuration

#### Policy Type
Set the policy type (Ingress, Egress, or both).

```python
# Ingress only
np = NetworkPolicy("api-policy").policy_type("Ingress")

# Egress only
np = NetworkPolicy("api-policy").policy_type("Egress")

# Both Ingress and Egress
np = NetworkPolicy("api-policy").policy_type("Ingress,Egress")
```

#### Ingress Policy
Enable or disable ingress policy.

```python
# Enable ingress policy
np = NetworkPolicy("api-policy").ingress_policy(True)

# Disable ingress policy
np = NetworkPolicy("api-policy").ingress_policy(False)
```

#### Egress Policy
Enable or disable egress policy.

```python
# Enable egress policy
np = NetworkPolicy("api-policy").egress_policy(True)

# Disable egress policy
np = NetworkPolicy("api-policy").egress_policy(False)
```

### Ingress Rules

#### Allow From Pods
Allow traffic from pods matching selector.

```python
# Allow from frontend pods
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend"})

# Allow from frontend pods on specific ports
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend"}, ports=[80, 443])

# Allow from frontend pods on specific protocols
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend"}, protocols=["TCP", "UDP"])
```

#### Allow From Namespace
Allow traffic from specific namespace.

```python
# Allow from monitoring namespace
np = NetworkPolicy("api-policy").allow_from_namespace("monitoring")

# Allow from monitoring namespace on specific ports
np = NetworkPolicy("api-policy").allow_from_namespace("monitoring", ports=[9090])
```

#### Allow From Namespaces
Allow traffic from multiple namespaces.

```python
# Allow from multiple namespaces
np = NetworkPolicy("api-policy").allow_from_namespaces(["frontend", "monitoring"])

# Allow from multiple namespaces on specific ports
np = NetworkPolicy("api-policy").allow_from_namespaces(["frontend", "monitoring"], ports=[80, 443, 9090])
```

#### Allow From IP Blocks
Allow traffic from specific IP blocks.

```python
# Allow from specific IP ranges
np = NetworkPolicy("api-policy").allow_from_ip_blocks(["10.0.0.0/8", "192.168.1.0/24"])

# Allow from IP blocks on specific ports
np = NetworkPolicy("api-policy").allow_from_ip_blocks(["10.0.0.0/8"], ports=[80, 443])
```

#### Allow From Service Accounts
Allow traffic from specific service accounts.

```python
# Allow from service accounts
np = NetworkPolicy("api-policy").allow_from_service_accounts(["frontend-sa", "monitoring-sa"])

# Allow from service accounts on specific ports
np = NetworkPolicy("api-policy").allow_from_service_accounts(["frontend-sa"], ports=[80, 443])
```

### Egress Rules

#### Allow Egress to Pods
Allow egress traffic to pods matching selector.

```python
# Allow egress to database pods
np = NetworkPolicy("api-policy").allow_egress_to_pods({"app": "database"})

# Allow egress to database pods on specific ports
np = NetworkPolicy("api-policy").allow_egress_to_pods({"app": "database"}, ports=[5432])
```

#### Allow Egress to Namespace
Allow egress traffic to specific namespace.

```python
# Allow egress to database namespace
np = NetworkPolicy("api-policy").allow_egress_to_namespace("database")

# Allow egress to database namespace on specific ports
np = NetworkPolicy("api-policy").allow_egress_to_namespace("database", ports=[5432])
```

#### Allow Egress to Namespaces
Allow egress traffic to multiple namespaces.

```python
# Allow egress to multiple namespaces
np = NetworkPolicy("api-policy").allow_egress_to_namespaces(["database", "cache"])

# Allow egress to multiple namespaces on specific ports
np = NetworkPolicy("api-policy").allow_egress_to_namespaces(["database", "cache"], ports=[5432, 6379])
```

#### Allow Egress to IP Blocks
Allow egress traffic to specific IP blocks.

```python
# Allow egress to external services
np = NetworkPolicy("api-policy").allow_egress_to_ip_blocks(["8.8.8.8/32", "1.1.1.1/32"])

# Allow egress to external services on specific ports
np = NetworkPolicy("api-policy").allow_egress_to_ip_blocks(["8.8.8.8/32"], ports=[53])
```

#### Allow Egress to External Services
Allow egress traffic to external services.

```python
# Allow egress to external APIs
np = NetworkPolicy("api-policy").allow_egress_to_external_services(["api.example.com", "api.github.com"])

# Allow egress to external APIs on specific ports
np = NetworkPolicy("api-policy").allow_egress_to_external_services(["api.example.com"], ports=[443])
```

### Deny Rules

#### Deny All
Deny all traffic (default deny).

```python
# Deny all traffic
np = NetworkPolicy("api-policy").deny_all()
```

#### Deny From Pods
Deny traffic from pods matching selector.

```python
# Deny traffic from specific pods
np = NetworkPolicy("api-policy").deny_from_pods({"app": "malicious"})
```

#### Deny From Namespace
Deny traffic from specific namespace.

```python
# Deny traffic from specific namespace
np = NetworkPolicy("api-policy").deny_from_namespace("untrusted")
```

#### Deny Egress to Pods
Deny egress traffic to pods matching selector.

```python
# Deny egress to specific pods
np = NetworkPolicy("api-policy").deny_egress_to_pods({"app": "restricted"})
```

#### Deny Egress to Namespace
Deny egress traffic to specific namespace.

```python
# Deny egress to specific namespace
np = NetworkPolicy("api-policy").deny_egress_to_namespace("restricted")
```

### Port and Protocol Configuration

#### Ports
Set allowed ports for the policy.

```python
# Allow only specific ports
np = NetworkPolicy("api-policy").ports([80, 443, 8080])
```

#### Protocols
Set allowed protocols for the policy.

```python
# Allow only TCP
np = NetworkPolicy("api-policy").protocols(["TCP"])

# Allow TCP and UDP
np = NetworkPolicy("api-policy").protocols(["TCP", "UDP"])
```

#### HTTP Ports
Allow HTTP ports (80, 443).

```python
np = NetworkPolicy("api-policy").http_ports()
```

#### Database Ports
Allow common database ports.

```python
# Allow common database ports
np = NetworkPolicy("api-policy").database_ports()
```

#### Metrics Ports
Allow metrics ports (9090, 9100).

```python
np = NetworkPolicy("api-policy").metrics_ports()
```

### Security Configuration

#### Pod Selector
Set pod selector for the policy.

```python
# Apply policy to API pods
np = NetworkPolicy("api-policy").pod_selector({"app": "api"})
```

#### Namespace Selector
Set namespace selector for the policy.

```python
# Apply policy to production namespace
np = NetworkPolicy("api-policy").namespace_selector({"environment": "production"})
```

#### Add Label
Add a label to the network policy.

```python
np = NetworkPolicy("api-policy").add_label("environment", "production")
```

#### Add Labels
Add multiple labels to the network policy.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "security"
}
np = NetworkPolicy("api-policy").add_labels(labels)
```

#### Add Annotation
Add an annotation to the network policy.

```python
np = NetworkPolicy("api-policy").add_annotation("description", "API network policy")
```

#### Add Annotations
Add multiple annotations to the network policy.

```python
annotations = {
    "description": "API network policy for production",
    "owner": "platform-team",
    "review-date": "2024-01-01"
}
np = NetworkPolicy("api-policy").add_annotations(annotations)
```

### Advanced Configuration

#### namespace(namespace: str) -> NetworkPolicy
Set the namespace for the network policy.

```python
np = NetworkPolicy("api-policy").namespace("production")
```

#### priority(priority: int) -> NetworkPolicy
Set the priority of the network policy.

```python
# High priority policy
np = NetworkPolicy("api-policy").priority(1000)

# Low priority policy
np = NetworkPolicy("api-policy").priority(100)
```

#### log_denied_packets(enabled: bool = True) -> NetworkPolicy
Enable logging of denied packets.

```python
# Enable logging
np = NetworkPolicy("api-policy").log_denied_packets(True)

# Disable logging
np = NetworkPolicy("api-policy").log_denied_packets(False)
```

#### audit_mode(enabled: bool = True) -> NetworkPolicy
Enable audit mode (log but don't block).

```python
# Enable audit mode
np = NetworkPolicy("api-policy").audit_mode(True)

# Disable audit mode
np = NetworkPolicy("api-policy").audit_mode(False)
```

### Output Generation

#### generate() -> NetworkPolicyGenerator
Generate the network policy configuration.

```python
# Generate Kubernetes YAML
np.generate().to_yaml("./k8s/")

# Generate Helm values
np.generate().to_helm_values("./helm/")

# Generate Terraform
np.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready network policy:

```python
from celestra import NetworkPolicy

# Create comprehensive network policy
api_network_policy = (NetworkPolicy("api-network-policy")
    .policy_type("Ingress,Egress")
    .pod_selector({"app": "api", "tier": "backend"})
    .deny_all()
    .allow_from_pods({"app": "frontend", "tier": "frontend"}, ports=[80, 443])
    .allow_from_namespace("monitoring", ports=[9090])
    .allow_from_service_accounts(["frontend-sa", "monitoring-sa"])
    .allow_egress_to_pods({"app": "database", "tier": "data"}, ports=[5432])
    .allow_egress_to_namespace("cache", ports=[6379])
    .allow_egress_to_ip_blocks(["8.8.8.8/32", "1.1.1.1/32"], ports=[53])
    .allow_egress_to_external_services(["api.example.com", "api.github.com"], ports=[443])
    .deny_from_namespace("untrusted")
    .deny_egress_to_namespace("restricted")
    .http_ports()
    .database_ports()
    .metrics_ports()
    .protocols(["TCP"])
    .namespace("production")
    .priority(1000)
    .log_denied_packets(True)
    .audit_mode(False)
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "security"
    })
    .add_annotations({
        "description": "API network policy for production",
        "owner": "platform-team@company.com",
        "review-date": "2024-01-01"
    }))

# Generate manifests
api_network_policy.generate().to_yaml("./k8s/")
```

## Network Policy Patterns

### Default Deny Pattern
```python
# Default deny with specific allows
default_deny = (NetworkPolicy("default-deny")
    .pod_selector({"app": "api"})
    .deny_all()
    .allow_from_pods({"app": "frontend"}, ports=[80, 443])
    .allow_from_namespace("monitoring", ports=[9090]))
```

### Namespace Isolation Pattern
```python
# Isolate namespace
namespace_isolation = (NetworkPolicy("namespace-isolation")
    .pod_selector({})
    .deny_all()
    .allow_from_namespace("trusted", ports=[80, 443])
    .allow_egress_to_namespace("trusted"))
```

### Database Access Pattern
```python
# Database access control
db_access = (NetworkPolicy("db-access")
    .pod_selector({"app": "database"})
    .deny_all()
    .allow_from_pods({"app": "api"}, ports=[5432])
    .allow_from_pods({"app": "admin"}, ports=[5432]))
```

### External Service Access Pattern
```python
# External service access
external_access = (NetworkPolicy("external-access")
    .pod_selector({"app": "api"})
    .allow_egress_to_ip_blocks(["8.8.8.8/32"], ports=[53])
    .allow_egress_to_external_services(["api.example.com"], ports=[443]))
```

## Best Practices

### 1. **Use Default Deny**
```python
# ✅ Good: Start with deny all
np = NetworkPolicy("api-policy").deny_all().allow_from_pods({"app": "frontend"})

# ❌ Bad: Allow all by default
np = NetworkPolicy("api-policy")  # No deny_all()
```

### 2. **Be Specific with Selectors**
```python
# ✅ Good: Use specific selectors
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend", "tier": "frontend"})

# ❌ Bad: Use overly broad selectors
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend"})  # Too broad
```

### 3. **Specify Ports**
```python
# ✅ Good: Specify required ports
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend"}, ports=[80, 443])

# ❌ Bad: Allow all ports
np = NetworkPolicy("api-policy").allow_from_pods({"app": "frontend"})  # All ports
```

### 4. **Use Namespace Isolation**
```python
# ✅ Good: Use namespace-based rules
np = NetworkPolicy("api-policy").allow_from_namespace("frontend")

# ❌ Bad: Allow from all namespaces
np = NetworkPolicy("api-policy")  # No namespace restrictions
```

### 5. **Log Denied Packets**
```python
# ✅ Good: Enable logging for debugging
np = NetworkPolicy("api-policy").log_denied_packets(True)

# ❌ Bad: No logging
np = NetworkPolicy("api-policy")  # No logging
```

### 6. **Use Audit Mode for Testing**
```python
# ✅ Good: Use audit mode for testing
np = NetworkPolicy("api-policy").audit_mode(True)

# ❌ Bad: Block traffic without testing
np = NetworkPolicy("api-policy").audit_mode(False)  # Immediate blocking
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Service](service.md)** - For service discovery
- **[Ingress](ingress.md)** - For external access
- **[RBAC](../security/rbac.md)** - For access control

## Next Steps

- **[Service](service.md)** - Learn about service discovery
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 