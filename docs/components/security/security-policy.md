# SecurityPolicy Class

The `SecurityPolicy` class manages security policies and configurations in Kubernetes. It provides capabilities for Pod Security Standards (PSS), security contexts, security policies, and compliance configurations.

## Overview

```python
from celestra import SecurityPolicy

# Basic security policy
security = SecurityPolicy("app-security").pod_security_standard("restricted")

# Production security policy
security = (SecurityPolicy("production-security")
    .pod_security_standard("restricted")
    .security_context({
        "runAsNonRoot": True,
        "runAsUser": 1000,
        "fsGroup": 2000
    })
    .seccomp_profile("RuntimeDefault"))
```

## Core API Functions

### Pod Security Standards

#### Pod Security Standard
Set the Pod Security Standard level.

```python
# Privileged level (least secure)
security = SecurityPolicy("app-security").pod_security_standard("privileged")

# Baseline level (moderate security)
security = SecurityPolicy("app-security").pod_security_standard("baseline")

# Restricted level (most secure)
security = SecurityPolicy("app-security").pod_security_standard("restricted")
```

#### Privileged Policy
Configure privileged security policy.

```python
security = SecurityPolicy("app-security").privileged_policy()
```

#### Baseline Policy
Configure baseline security policy.

```python
security = SecurityPolicy("app-security").baseline_policy()
```

#### Restricted Policy
Configure restricted security policy.

```python
security = SecurityPolicy("app-security").restricted_policy()
```

### Security Context Configuration

#### Security Context
Set the security context.

```python
# Basic security context
security_context = {
    "runAsNonRoot": True,
    "runAsUser": 1000,
    "fsGroup": 2000
}
security = SecurityPolicy("app-security").security_context(security_context)
```

#### Run As User
Set the user ID to run as.

```python
# Run as non-root user
security = SecurityPolicy("app-security").run_as_user(1000)

# Run as specific user
security = SecurityPolicy("app-security").run_as_user(2000)
```

#### Run As Group
Set the group ID to run as.

```python
# Run as specific group
security = SecurityPolicy("app-security").run_as_group(2000)

# Run as root group
security = SecurityPolicy("app-security").run_as_group(0)
```

#### Run As Non Root
Set whether to run as non-root.

```python
# Run as non-root
security = SecurityPolicy("app-security").run_as_non_root(True)

# Allow root (not recommended)
security = SecurityPolicy("app-security").run_as_non_root(False)
```

#### Read Only Root Filesystem
Set read-only root filesystem.

```python
# Read-only root filesystem
security = SecurityPolicy("app-security").read_only_root_filesystem(True)

# Read-write root filesystem
security = SecurityPolicy("app-security").read_only_root_filesystem(False)
```

#### allow_privilege_escalation(enabled: bool = False) -> SecurityPolicy
Allow privilege escalation.

```python
# Disable privilege escalation
security = SecurityPolicy("app-security").allow_privilege_escalation(False)

# Allow privilege escalation (not recommended)
security = SecurityPolicy("app-security").allow_privilege_escalation(True)
```

#### privileged_container(enabled: bool = False) -> SecurityPolicy
Allow privileged containers.

```python
# Disable privileged containers
security = SecurityPolicy("app-security").privileged_container(False)

# Allow privileged containers (not recommended)
security = SecurityPolicy("app-security").privileged_container(True)
```

### Capabilities Configuration

#### drop_capabilities(capabilities: List[str]) -> SecurityPolicy
Drop Linux capabilities.

```python
# Drop dangerous capabilities
security = SecurityPolicy("app-security").drop_capabilities([
    "ALL"
])

# Drop specific capabilities
security = SecurityPolicy("app-security").drop_capabilities([
    "NET_RAW",
    "SYS_ADMIN",
    "SYS_CHROOT"
])
```

#### add_capabilities(capabilities: List[str]) -> SecurityPolicy
Add Linux capabilities.

```python
# Add specific capabilities
security = SecurityPolicy("app-security").add_capabilities([
    "NET_BIND_SERVICE",
    "CHOWN"
])
```

#### required_capabilities(capabilities: List[str]) -> SecurityPolicy
Set required capabilities.

```python
# Set required capabilities
security = SecurityPolicy("app-security").required_capabilities([
    "NET_BIND_SERVICE"
])
```

### Seccomp Configuration

#### seccomp_profile(profile: str) -> SecurityPolicy
Set the seccomp profile.

```python
# Runtime default profile
security = SecurityPolicy("app-security").seccomp_profile("RuntimeDefault")

# Unconfined profile (not recommended)
security = SecurityPolicy("app-security").seccomp_profile("Unconfined")

# Localhost profile
security = SecurityPolicy("app-security").seccomp_profile("localhost/restricted")
```

#### seccomp_type(type: str) -> SecurityPolicy
Set the seccomp type.

```python
# Runtime default
security = SecurityPolicy("app-security").seccomp_type("RuntimeDefault")

# Localhost
security = SecurityPolicy("app-security").seccomp_type("Localhost")
```

### AppArmor Configuration

#### apparmor_profile(profile: str) -> SecurityPolicy
Set the AppArmor profile.

```python
# Runtime default profile
security = SecurityPolicy("app-security").apparmor_profile("runtime/default")

# Custom profile
security = SecurityPolicy("app-security").apparmor_profile("localhost/restricted")
```

#### apparmor_type(type: str) -> SecurityPolicy
Set the AppArmor type.

```python
# Runtime default
security = SecurityPolicy("app-security").apparmor_type("RuntimeDefault")

# Localhost
security = SecurityPolicy("app-security").apparmor_type("Localhost")
```

### SELinux Configuration

#### selinux_options(options: Dict[str, str]) -> SecurityPolicy
Set SELinux options.

```python
# Set SELinux options
selinux_options = {
    "level": "s0:c123,c456",
    "role": "container_r",
    "type": "container_t",
    "user": "system_u"
}
security = SecurityPolicy("app-security").selinux_options(selinux_options)
```

#### selinux_level(level: str) -> SecurityPolicy
Set SELinux level.

```python
security = SecurityPolicy("app-security").selinux_level("s0:c123,c456")
```

#### selinux_role(role: str) -> SecurityPolicy
Set SELinux role.

```python
security = SecurityPolicy("app-security").selinux_role("container_r")
```

#### selinux_type(type: str) -> SecurityPolicy
Set SELinux type.

```python
security = SecurityPolicy("app-security").selinux_type("container_t")
```

#### selinux_user(user: str) -> SecurityPolicy
Set SELinux user.

```python
security = SecurityPolicy("app-security").selinux_user("system_u")
```

### Volume Security

#### volume_security_context(context: Dict[str, Any]) -> SecurityPolicy
Set volume security context.

```python
# Volume security context
volume_context = {
    "fsGroup": 2000,
    "runAsUser": 1000,
    "runAsGroup": 2000
}
security = SecurityPolicy("app-security").volume_security_context(volume_context)
```

#### volume_fs_group(group_id: int) -> SecurityPolicy
Set volume filesystem group.

```python
security = SecurityPolicy("app-security").volume_fs_group(2000)
```

#### volume_run_as_user(user_id: int) -> SecurityPolicy
Set volume run as user.

```python
security = SecurityPolicy("app-security").volume_run_as_user(1000)
```

#### volume_run_as_group(group_id: int) -> SecurityPolicy
Set volume run as group.

```python
security = SecurityPolicy("app-security").volume_run_as_group(2000)
```

### Network Security

#### host_network(enabled: bool = False) -> SecurityPolicy
Allow host network access.

```python
# Disable host network
security = SecurityPolicy("app-security").host_network(False)

# Allow host network (not recommended)
security = SecurityPolicy("app-security").host_network(True)
```

#### host_pid(enabled: bool = False) -> SecurityPolicy
Allow host PID namespace.

```python
# Disable host PID
security = SecurityPolicy("app-security").host_pid(False)

# Allow host PID (not recommended)
security = SecurityPolicy("app-security").host_pid(True)
```

#### host_ipc(enabled: bool = False) -> SecurityPolicy
Allow host IPC namespace.

```python
# Disable host IPC
security = SecurityPolicy("app-security").host_ipc(False)

# Allow host IPC (not recommended)
security = SecurityPolicy("app-security").host_ipc(True)
```

### Compliance Configuration

#### compliance_standard(standard: str) -> SecurityPolicy
Set compliance standard.

```python
# CIS compliance
security = SecurityPolicy("app-security").compliance_standard("cis")

# NIST compliance
security = SecurityPolicy("app-security").compliance_standard("nist")

# PCI compliance
security = SecurityPolicy("app-security").compliance_standard("pci")
```

#### compliance_level(level: str) -> SecurityPolicy
Set compliance level.

```python
# Level 1 compliance
security = SecurityPolicy("app-security").compliance_level("level1")

# Level 2 compliance
security = SecurityPolicy("app-security").compliance_level("level2")
```

#### audit_enabled(enabled: bool = True) -> SecurityPolicy
Enable security auditing.

```python
# Enable auditing
security = SecurityPolicy("app-security").audit_enabled(True)

# Disable auditing
security = SecurityPolicy("app-security").audit_enabled(False)
```

### Advanced Configuration

#### namespace(namespace: str) -> SecurityPolicy
Set the namespace for the security policy.

```python
security = SecurityPolicy("app-security").namespace("production")
```

#### add_label(key: str, value: str) -> SecurityPolicy
Add a label to the security policy.

```python
security = SecurityPolicy("app-security").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> SecurityPolicy
Add multiple labels to the security policy.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "security"
}
security = SecurityPolicy("app-security").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> SecurityPolicy
Add an annotation to the security policy.

```python
security = SecurityPolicy("app-security").add_annotation("description", "Application security policy")
```

#### add_annotations(annotations: Dict[str, str]) -> SecurityPolicy
Add multiple annotations to the security policy.

```python
annotations = {
    "description": "Application security policy for production",
    "owner": "platform-team",
    "compliance": "cis-level2"
}
security = SecurityPolicy("app-security").add_annotations(annotations)
```

#### enforcement_mode(mode: str) -> SecurityPolicy
Set enforcement mode.

```python
# Enforce mode
security = SecurityPolicy("app-security").enforcement_mode("enforce")

# Audit mode
security = SecurityPolicy("app-security").enforcement_mode("audit")

# Warn mode
security = SecurityPolicy("app-security").enforcement_mode("warn")
```

#### violation_action(action: str) -> SecurityPolicy
Set violation action.

```python
# Deny violations
security = SecurityPolicy("app-security").violation_action("deny")

# Warn on violations
security = SecurityPolicy("app-security").violation_action("warn")

# Audit violations
security = SecurityPolicy("app-security").violation_action("audit")
```

### Output Generation

#### generate() -> SecurityPolicyGenerator
Generate the security policy configuration.

```python
# Generate Kubernetes YAML
security.generate().to_yaml("./k8s/")

# Generate Helm values
security.generate().to_helm_values("./helm/")

# Generate Terraform
security.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready security policy configuration:

```python
from celestra import SecurityPolicy

# Create comprehensive security policy configuration
production_security = (SecurityPolicy("production-security")
    .pod_security_standard("restricted")
    .security_context({
        "runAsNonRoot": True,
        "runAsUser": 1000,
        "fsGroup": 2000,
        "readOnlyRootFilesystem": True,
        "allowPrivilegeEscalation": False
    })
    .run_as_user(1000)
    .run_as_group(2000)
    .run_as_non_root(True)
    .read_only_root_filesystem(True)
    .allow_privilege_escalation(False)
    .privileged_container(False)
    .drop_capabilities(["ALL"])
    .add_capabilities(["NET_BIND_SERVICE"])
    .seccomp_profile("RuntimeDefault")
    .apparmor_profile("runtime/default")
    .selinux_options({
        "level": "s0:c123,c456",
        "role": "container_r",
        "type": "container_t",
        "user": "system_u"
    })
    .volume_security_context({
        "fsGroup": 2000,
        "runAsUser": 1000,
        "runAsGroup": 2000
    })
    .host_network(False)
    .host_pid(False)
    .host_ipc(False)
    .compliance_standard("cis")
    .compliance_level("level2")
    .audit_enabled(True)
    .enforcement_mode("enforce")
    .violation_action("deny")
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "security"
    })
    .add_annotations({
        "description": "Production security policy",
        "owner": "platform-team@company.com",
        "compliance": "cis-level2"
    }))

# Generate manifests
production_security.generate().to_yaml("./k8s/")
```

## Security Policy Patterns

### Restricted Policy Pattern
```python
# Restricted security policy for production
restricted_policy = (SecurityPolicy("restricted-security")
    .pod_security_standard("restricted")
    .run_as_non_root(True)
    .read_only_root_filesystem(True)
    .allow_privilege_escalation(False)
    .privileged_container(False)
    .drop_capabilities(["ALL"])
    .seccomp_profile("RuntimeDefault")
    .apparmor_profile("runtime/default"))
```

### Baseline Policy Pattern
```python
# Baseline security policy for development
baseline_policy = (SecurityPolicy("baseline-security")
    .pod_security_standard("baseline")
    .run_as_non_root(True)
    .allow_privilege_escalation(False)
    .privileged_container(False)
    .seccomp_profile("RuntimeDefault"))
```

### Privileged Policy Pattern
```python
# Privileged security policy for system components
privileged_policy = (SecurityPolicy("privileged-security")
    .pod_security_standard("privileged")
    .privileged_container(True)
    .allow_privilege_escalation(True)
    .host_network(True)
    .host_pid(True))
```

### Compliance Policy Pattern
```python
# Compliance-focused security policy
compliance_policy = (SecurityPolicy("compliance-security")
    .pod_security_standard("restricted")
    .compliance_standard("cis")
    .compliance_level("level2")
    .audit_enabled(True)
    .enforcement_mode("enforce")
    .violation_action("deny"))
```

### Network Security Policy Pattern
```python
# Network-focused security policy
network_security = (SecurityPolicy("network-security")
    .pod_security_standard("restricted")
    .host_network(False)
    .host_pid(False)
    .host_ipc(False)
    .add_capabilities(["NET_BIND_SERVICE"]))
```

## Best Practices

### 1. **Use Restricted Pod Security Standard**
```python
# ✅ Good: Use restricted PSS
security = SecurityPolicy("app-security").pod_security_standard("restricted")

# ❌ Bad: Use privileged PSS
security = SecurityPolicy("app-security").pod_security_standard("privileged")
```

### 2. **Run as Non-Root**
```python
# ✅ Good: Run as non-root
security = SecurityPolicy("app-security").run_as_non_root(True).run_as_user(1000)

# ❌ Bad: Run as root
security = SecurityPolicy("app-security").run_as_non_root(False)
```

### 3. **Use Read-Only Root Filesystem**
```python
# ✅ Good: Use read-only root filesystem
security = SecurityPolicy("app-security").read_only_root_filesystem(True)

# ❌ Bad: Use read-write root filesystem
security = SecurityPolicy("app-security").read_only_root_filesystem(False)
```

### 4. **Drop Dangerous Capabilities**
```python
# ✅ Good: Drop all capabilities
security = SecurityPolicy("app-security").drop_capabilities(["ALL"])

# ❌ Bad: Keep all capabilities
security = SecurityPolicy("app-security")  # No capability restrictions
```

### 5. **Use Runtime Default Seccomp**
```python
# ✅ Good: Use runtime default seccomp
security = SecurityPolicy("app-security").seccomp_profile("RuntimeDefault")

# ❌ Bad: Use unconfined seccomp
security = SecurityPolicy("app-security").seccomp_profile("Unconfined")
```

### 6. **Disable Host Namespaces**
```python
# ✅ Good: Disable host namespaces
security = SecurityPolicy("app-security").host_network(False).host_pid(False).host_ipc(False)

# ❌ Bad: Allow host namespaces
security = SecurityPolicy("app-security").host_network(True)
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[RBAC](rbac.md)** - For access control
- **[NetworkPolicy](../networking/network-policy.md)** - For network security
- **[Secret](secrets.md)** - For sensitive data

## Next Steps

- **[WaitCondition](../advanced/wait-condition.md)** - Learn about wait conditions
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 