# Volume Class

The `Volume` class manages persistent storage in Kubernetes. It provides volume creation, mounting, and management capabilities for applications that require persistent data storage.

## Overview

```python
from celestra import Volume

# Basic volume
volume = Volume("app-data").size("10Gi").storage_class("fast-ssd")

# Production volume with backup
volume = (Volume("production-data")
    .size("100Gi")
    .storage_class("premium-ssd")
    .backup_enabled(True)
    .encryption_enabled(True)
    .access_mode("ReadWriteOnce"))
```

## Core API Functions

### Volume Configuration

#### Volume Size
Set the volume size.

```python
# Basic size
volume = Volume("app-data").size("10Gi")

# Large volume
volume = Volume("database-data").size("1Ti")

# Small volume
volume = Volume("config-data").size("1Gi")
```

#### Storage Class
Set the storage class for the volume.

```python
# SSD storage
volume = Volume("app-data").storage_class("fast-ssd")

# HDD storage
volume = Volume("backup-data").storage_class("standard-hdd")

# Premium storage
volume = Volume("database-data").storage_class("premium-ssd")
```

#### Access Mode
Set the access mode for the volume.

```python
# Single node read/write
volume = Volume("app-data").access_mode("ReadWriteOnce")

# Multiple nodes read/write
volume = Volume("shared-data").access_mode("ReadWriteMany")

# Multiple nodes read-only
volume = Volume("config-data").access_mode("ReadOnlyMany")
```

#### Mount Path
Set the mount path for the volume.

```python
# Application data
volume = Volume("app-data").mount_path("/app/data")

# Database data
volume = Volume("database-data").mount_path("/var/lib/postgresql/data")

# Configuration data
volume = Volume("config-data").mount_path("/etc/config")
```

### Volume Types

#### Persistent Volume
Configure as persistent volume.

```python
volume = Volume("app-data").persistent_volume()
```

#### Ephemeral Volume
Configure as ephemeral volume.

```python
volume = Volume("temp-data").ephemeral_volume()
```

#### Empty Directory Volume
Configure as empty directory volume.

```python
volume = Volume("cache-data").empty_dir_volume()
```

#### Host Path Volume
Configure as host path volume.

```python
volume = Volume("host-data").host_path_volume("/host/data")
```

#### ConfigMap Volume
Configure as ConfigMap volume.

```python
volume = Volume("config-data").config_map_volume("app-config")
```

#### Secret Volume
Configure as Secret volume.

```python
volume = Volume("secret-data").secret_volume("app-secret")
```

### Storage Features

#### Backup Enabled
Enable backup for the volume.

```python
# Enable backup
volume = Volume("app-data").backup_enabled(True)

# Disable backup
volume = Volume("temp-data").backup_enabled(False)
```

#### Backup Schedule
Set backup schedule.

```python
# Daily backup
volume = Volume("app-data").backup_schedule("0 2 * * *")

# Weekly backup
volume = Volume("app-data").backup_schedule("0 2 * * 0")
```

#### Backup Retention
Set backup retention period.

```python
# 30 days retention
volume = Volume("app-data").backup_retention(30)

# 90 days retention
volume = Volume("app-data").backup_retention(90)
```

#### Encryption Enabled
Enable encryption for the volume.

```python
# Enable encryption
volume = Volume("app-data").encryption_enabled(True)

# Disable encryption
volume = Volume("temp-data").encryption_enabled(False)
```

#### Encryption Key
Set encryption key for the volume.

```python
volume = Volume("app-data").encryption_key("my-encryption-key")
```

### Performance Configuration

#### IOPS Configuration
Set IOPS for the volume.

```python
# High IOPS
volume = Volume("database-data").iops(3000)

# Standard IOPS
volume = Volume("app-data").iops(1000)
```

#### Throughput Configuration
Set throughput for the volume.

```python
# High throughput
volume = Volume("database-data").throughput("500Mi")

# Standard throughput
volume = Volume("app-data").throughput("125Mi")
```

#### Performance Tier
Set performance tier.

```python
# Premium tier
volume = Volume("database-data").performance_tier("premium")

# Standard tier
volume = Volume("app-data").performance_tier("standard")

# Basic tier
volume = Volume("backup-data").performance_tier("basic")
```

### Volume Mounting

#### Mount Options
Set mount options for the volume.

```python
# NFS mount options
volume = Volume("nfs-data").mount_options(["nfsvers=4", "noatime"])

# Local mount options
volume = Volume("local-data").mount_options(["noatime", "nodiratime"])
```

#### Sub-Path Mounting
Set sub-path for volume mounting.

```python
# Mount specific subdirectory
volume = Volume("config-data").sub_path("app/config")
```

#### Read-Only Volume
Set volume as read-only.

```python
# Read-only volume
volume = Volume("config-data").read_only(True)

# Read-write volume
volume = Volume("app-data").read_only(False)
```

### Volume Expansion

#### Allow Expansion
Allow volume expansion.

```python
# Allow expansion
volume = Volume("app-data").allow_expansion(True)

# Disable expansion
volume = Volume("fixed-data").allow_expansion(False)
```

#### Expansion Policy
Set expansion policy.

```python
# Automatic expansion
volume = Volume("app-data").expansion_policy("automatic")

# Manual expansion
volume = Volume("app-data").expansion_policy("manual")
```

#### Expansion Threshold
Set expansion threshold percentage.

```python
# Expand at 80% usage
volume = Volume("app-data").expansion_threshold(0.8)

# Expand at 90% usage
volume = Volume("app-data").expansion_threshold(0.9)
```

### Volume Snapshots

#### Snapshot Enabled
Enable volume snapshots.

```python
# Enable snapshots
volume = Volume("app-data").snapshot_enabled(True)

# Disable snapshots
volume = Volume("temp-data").snapshot_enabled(False)
```

#### Snapshot Schedule
Set snapshot schedule.

```python
# Daily snapshots
volume = Volume("app-data").snapshot_schedule("0 1 * * *")

# Hourly snapshots
volume = Volume("critical-data").snapshot_schedule("0 * * * *")
```

#### Snapshot Retention
Set snapshot retention count.

```python
# Keep 7 snapshots
volume = Volume("app-data").snapshot_retention(7)

# Keep 30 snapshots
volume = Volume("critical-data").snapshot_retention(30)
```

### Volume Replication

#### Replication Enabled
Enable volume replication.

```python
# Enable replication
volume = Volume("critical-data").replication_enabled(True)

# Disable replication
volume = Volume("temp-data").replication_enabled(False)
```

#### Replication Factor
Set replication factor.

```python
# 3x replication
volume = Volume("critical-data").replication_factor(3)

# 2x replication
volume = Volume("app-data").replication_factor(2)
```

#### Replication Zones
Set replication zones.

```python
# Multi-zone replication
volume = Volume("critical-data").replication_zones(["us-west1-a", "us-west1-b", "us-west1-c"])
```

### Advanced Configuration

#### Namespace
Set the namespace for the volume.

```python
volume = Volume("app-data").namespace("production")
```

#### Add Label
Add a label to the volume.

```python
volume = Volume("app-data").add_label("environment", "production")
```

#### Add Labels
Add multiple labels to the volume.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "storage"
}
volume = Volume("app-data").add_labels(labels)
```

#### Add Annotation
Add an annotation to the volume.

```python
volume = Volume("app-data").add_annotation("description", "Application data volume")
```

#### Add Annotations
Add multiple annotations to the volume.

```python
annotations = {
    "description": "Application data volume for production",
    "owner": "platform-team",
    "backup-schedule": "daily"
}
volume = Volume("app-data").add_annotations(annotations)
```

#### Node Affinity
Set node affinity for the volume.

```python
# Affinity to specific nodes
affinity = {
    "requiredDuringSchedulingIgnoredDuringExecution": {
        "nodeSelectorTerms": [{
            "matchExpressions": [{
                "key": "storage-type",
                "operator": "In",
                "values": ["ssd"]
            }]
        }]
    }
}
volume = Volume("fast-data").node_affinity(affinity)
```

#### Pod Affinity
Set pod affinity for the volume.

```python
# Affinity to specific pods
affinity = {
    "preferredDuringSchedulingIgnoredDuringExecution": [{
        "weight": 100,
        "podAffinityTerm": {
            "labelSelector": {
                "matchExpressions": [{
                    "key": "app",
                    "operator": "In",
                    "values": ["database"]
                }]
            },
            "topologyKey": "kubernetes.io/hostname"
        }
    }]
}
volume = Volume("database-data").pod_affinity(affinity)
```

### Output Generation

#### generate() -> VolumeGenerator
Generate the volume configuration.

```python
# Generate Kubernetes YAML
volume.generate().to_yaml("./k8s/")

# Generate Helm values
volume.generate().to_helm_values("./helm/")

# Generate Terraform
volume.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready volume configuration:

```python
from celestra import Volume

# Create comprehensive volume configuration
production_volume = (Volume("production-data")
    .size("100Gi")
    .storage_class("premium-ssd")
    .access_mode("ReadWriteOnce")
    .mount_path("/app/data")
    .persistent_volume()
    .backup_enabled(True)
    .backup_schedule("0 2 * * *")
    .backup_retention(30)
    .encryption_enabled(True)
    .encryption_key("production-encryption-key")
    .iops(3000)
    .throughput("500Mi")
    .performance_tier("premium")
    .mount_options(["noatime", "nodiratime"])
    .allow_expansion(True)
    .expansion_policy("automatic")
    .expansion_threshold(0.8)
    .snapshot_enabled(True)
    .snapshot_schedule("0 1 * * *")
    .snapshot_retention(7)
    .replication_enabled(True)
    .replication_factor(3)
    .replication_zones(["us-west1-a", "us-west1-b", "us-west1-c"])
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "storage"
    })
    .add_annotations({
        "description": "Production data volume",
        "owner": "platform-team@company.com",
        "backup-schedule": "daily"
    }))

# Generate manifests
production_volume.generate().to_yaml("./k8s/")
```

## Volume Patterns

### Database Volume Pattern
```python
# Database volume with high performance
db_volume = (Volume("database-data")
    .size("500Gi")
    .storage_class("premium-ssd")
    .access_mode("ReadWriteOnce")
    .mount_path("/var/lib/postgresql/data")
    .iops(5000)
    .throughput("1Gi")
    .performance_tier("premium")
    .backup_enabled(True)
    .backup_schedule("0 2 * * *")
    .backup_retention(90)
    .encryption_enabled(True)
    .replication_enabled(True)
    .replication_factor(3))
```

### Application Data Volume Pattern
```python
# Application data volume
app_volume = (Volume("app-data")
    .size("50Gi")
    .storage_class("fast-ssd")
    .access_mode("ReadWriteOnce")
    .mount_path("/app/data")
    .backup_enabled(True)
    .backup_schedule("0 3 * * *")
    .backup_retention(30)
    .encryption_enabled(True)
    .allow_expansion(True)
    .expansion_threshold(0.8))
```

### Shared Volume Pattern
```python
# Shared volume for multiple pods
shared_volume = (Volume("shared-data")
    .size("200Gi")
    .storage_class("standard-ssd")
    .access_mode("ReadWriteMany")
    .mount_path("/shared/data")
    .backup_enabled(True)
    .backup_schedule("0 4 * * *")
    .backup_retention(60)
    .replication_enabled(True)
    .replication_factor(2))
```

### Config Volume Pattern
```python
# Configuration volume
config_volume = (Volume("config-data")
    .size("1Gi")
    .storage_class("standard-ssd")
    .access_mode("ReadOnlyMany")
    .mount_path("/etc/config")
    .read_only(True)
    .backup_enabled(True)
    .backup_schedule("0 5 * * *")
    .backup_retention(90))
```

## Best Practices

### 1. **Choose Appropriate Storage Class**
```python
# ✅ Good: Use appropriate storage class
volume = Volume("database-data").storage_class("premium-ssd")  # For databases
volume = Volume("app-data").storage_class("fast-ssd")          # For applications
volume = Volume("backup-data").storage_class("standard-hdd")   # For backups

# ❌ Bad: Use wrong storage class
volume = Volume("database-data").storage_class("standard-hdd")  # Slow for database
```

### 2. **Enable Backup for Important Data**
```python
# ✅ Good: Enable backup for important data
volume = Volume("app-data").backup_enabled(True).backup_schedule("0 2 * * *")

# ❌ Bad: No backup for important data
volume = Volume("app-data")  # No backup
```

### 3. **Use Encryption for Sensitive Data**
```python
# ✅ Good: Enable encryption for sensitive data
volume = Volume("app-data").encryption_enabled(True)

# ❌ Bad: No encryption for sensitive data
volume = Volume("app-data")  # No encryption
```

### 4. **Allow Volume Expansion**
```python
# ✅ Good: Allow volume expansion
volume = Volume("app-data").allow_expansion(True).expansion_threshold(0.8)

# ❌ Bad: No expansion capability
volume = Volume("app-data")  # No expansion
```

### 5. **Use Appropriate Access Modes**
```python
# ✅ Good: Use appropriate access mode
volume = Volume("database-data").access_mode("ReadWriteOnce")  # Single node
volume = Volume("shared-data").access_mode("ReadWriteMany")    # Multiple nodes

# ❌ Bad: Use wrong access mode
volume = Volume("database-data").access_mode("ReadWriteMany")  # Can cause issues
```

### 6. **Set Appropriate Size**
```python
# ✅ Good: Set appropriate size with room for growth
volume = Volume("app-data").size("50Gi")

# ❌ Bad: Set too small size
volume = Volume("app-data").size("1Gi")  # Too small
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[ConfigMap](config-map.md)** - For configuration data
- **[Secret](../security/secrets.md)** - For sensitive data
- **[Service](../networking/service.md)** - For service discovery

## Next Steps

- **[ConfigMap](config-map.md)** - Learn about configuration management
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 