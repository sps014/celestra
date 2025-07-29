# Job Class

The `Job` class manages Kubernetes Jobs for batch processing workloads that run to completion.

## Overview

```python
from celestra import Job

# Basic usage
job = Job("data-migration").image("migrator:latest").command(["python", "migrate.py"])
```

## Functions

### image(image: str) -> Job
Set the container image for the job.

```python
# Basic image
job = Job("migration").image("migrator:latest")

# Specific version
job = Job("backup").image("backup-tool:v1.2.0")

# Custom registry
job = Job("processor").image("gcr.io/myproject/processor:latest")
```

### command(command: List[str]) -> Job
Set the command to run in the container.

```python
# Simple command
job = Job("migration").command(["python", "migrate.py"])

# Complex command
job = Job("backup").command(["bash", "-c", "pg_dump | gzip > backup.sql.gz"])

# Shell command
job = Job("cleanup").command(["sh", "-c", "rm -rf /tmp/* && echo 'Cleanup complete'"])
```

### args(args: List[str]) -> Job
Set the arguments for the command.

```python
# Command with arguments
job = Job("migration").command(["python"]).args(["migrate.py", "--env", "production"])

# Multiple arguments
job = Job("backup").command(["pg_dump"]).args(["--host", "postgres", "--port", "5432", "myapp"])
```

### environment(env_vars: Dict[str, str]) -> Job
Set multiple environment variables at once.

```python
# Bulk environment variables
env_config = {
    "DATABASE_URL": "postgres://localhost:5432/myapp",
    "BACKUP_PATH": "/backups",
    "LOG_LEVEL": "info"
}
job = Job("backup").environment(env_config)
```

### env(key: str, value: str) -> Job
Add a single environment variable.

```python
# Single environment variable
job = Job("migration").env("DATABASE_URL", "postgres://localhost:5432/myapp")

# Multiple individual variables
job = (Job("backup")
    .env("BACKUP_PATH", "/backups")
    .env("RETENTION_DAYS", "30")
    .env("COMPRESSION", "gzip"))
```

### resources(cpu: str = None, memory: str = None, cpu_limit: str = None, memory_limit: str = None, gpu: int = None) -> Job
Set resource requests and limits for the job.

```python
# Basic resources
job = Job("migration").resources(cpu="500m", memory="1Gi")

# With limits
job = (Job("backup")
    .resources(
        cpu="1000m", 
        memory="2Gi",
        cpu_limit="2000m",
        memory_limit="4Gi"
    ))

# GPU-enabled job
job = Job("ml-training").resources(cpu="4", memory="16Gi", gpu=2)
```

### parallelism(count: int) -> Job
Set the number of parallel pods to run.

```python
# Single pod
job = Job("migration").parallelism(1)

# Parallel processing
job = Job("data-processing").parallelism(5)

# High parallelism
job = Job("batch-processing").parallelism(20)
```

### completions(count: int) -> Job
Set the number of successful completions required.

```python
# Single completion
job = Job("migration").completions(1)

# Multiple completions
job = Job("data-processing").completions(10)

# All pods must complete
job = Job("batch-job").completions(100)
```

### retry_limit(limit: int) -> Job
Set the number of retries for failed pods.

```python
# No retries
job = Job("critical-job").retry_limit(0)

# Default retries
job = Job("migration").retry_limit(6)

# Many retries
job = Job("unreliable-job").retry_limit(10)
```

### timeout(timeout: Union[str, int]) -> Job
Set the timeout for the job.

```python
# Timeout in seconds
job = Job("migration").timeout(3600)

# Timeout as string
job = Job("backup").timeout("2h")

# Short timeout
job = Job("quick-job").timeout("5m")

# Long timeout
job = Job("long-job").timeout("24h")
```

### restart_policy(policy: str) -> Job
Set the restart policy for the job.

```python
# On failure (default)
job = Job("migration").restart_policy("OnFailure")

# Never restart
job = Job("critical-job").restart_policy("Never")

# Always restart
job = Job("monitoring-job").restart_policy("Always")
```

### port(port: int, name: str = "http", protocol: str = "TCP") -> Job
Add a port to the job.

```python
# Basic port
job = Job("web-job").port(8080, "http")

# Multiple ports
job = (Job("api-job")
    .port(8080, "http")
    .port(8443, "https")
    .port(9090, "metrics"))
```

### add_port(port: int, name: str = "http", protocol: str = "TCP") -> Job
Add a port to the job (alias for port()).

```python
# Add multiple ports
job = (Job("multi-port-job")
    .add_port(8080, "http")
    .add_port(8443, "https")
    .add_port(9090, "metrics"))
```

### ports(ports: List[Dict[str, Any]]) -> Job
Add multiple ports at once.

```python
# Bulk port configuration
ports_config = [
    {"port": 8080, "name": "http"},
    {"port": 8443, "name": "https"},
    {"port": 9090, "name": "metrics"}
]
job = Job("api-job").ports(ports_config)
```

### Convenience Port Methods

#### Metrics Port
```python
job = Job("monitoring-job").metrics_port(9090)
```

#### Web Port
```python
job = Job("web-job").web_port(8080)
```

#### Status Port
```python
job = Job("status-job").status_port(8081)
```

### add_secret(secret: Secret) -> Job
Add a secret to the job.

```python
# Add database secret
db_secret = Secret("db-secret").add("password", "secret123")
job = Job("migration").add_secret(db_secret)

# Add API key secret
api_secret = Secret("api-keys").add("stripe_key", "sk_live_...")
job = Job("payment-job").add_secret(api_secret)
```

### add_config(config_map: ConfigMap) -> Job
Add a ConfigMap to the job.

```python
# Add configuration
app_config = ConfigMap("app-config").add("debug", "true")
job = Job("migration").add_config(app_config)

# Add configuration file
config_map = ConfigMap("migration-config").from_file("migrate.conf", "configs/migrate.conf")
job = Job("migration").add_config(config_map)
```

### add_volume(name: str, volume_spec: Dict[str, Any]) -> Job
Add a volume to the job.

```python
# Add persistent volume
job = Job("backup").add_volume("backup-storage", {
    "persistentVolumeClaim": {
        "claimName": "backup-pvc"
    }
})

# Add empty directory
job = Job("temp-job").add_volume("temp-dir", {
    "emptyDir": {}
})
```

### mount_volume(volume_name: str, mount_path: str, read_only: bool = False) -> Job
Mount a volume in the job.

```python
# Mount volume
job = Job("backup").mount_volume("backup-storage", "/backups")

# Read-only mount
job = Job("read-job").mount_volume("config-volume", "/config", read_only=True)
```

### security_context(context: Dict[str, Any]) -> Job
Set security context for the job.

```python
# Non-root user
job = Job("secure-job").security_context({
    "runAsNonRoot": True,
    "runAsUser": 1000,
    "fsGroup": 1000
})
```

### node_selector(selector: Dict[str, str]) -> Job
Set node selectors for pod placement.

```python
# GPU nodes
job = Job("ml-job").node_selector({"accelerator": "gpu"})

# High-memory nodes
job = Job("memory-job").node_selector({"node-type": "high-memory"})
```

### toleration(key: str, operator: str = "Equal", value: str = "", effect: str = "NoSchedule") -> Job
Add a toleration for node taints.

```python
# Tolerate GPU taints
job = Job("ml-job").toleration("nvidia.com/gpu", "Equal", "present", "NoSchedule")

# Tolerate spot instances
job = Job("batch-job").toleration("spot", "Equal", "true", "NoSchedule")
```

### affinity(affinity_spec: Dict[str, Any]) -> Job
Set pod affinity rules.

```python
# Prefer nodes with SSD
job = Job("io-job").affinity({
    "nodeAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [{
            "weight": 100,
            "preference": {
                "matchExpressions": [{
                    "key": "disk-type",
                    "operator": "In",
                    "values": ["ssd"]
                }]
            }
        }]
    }
})
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete Job Example - Production Data Migration
"""

import os
from celestra import Job, Secret, ConfigMap, KubernetesOutput

def load_config(config_path: str) -> str:
    """Load configuration from external file."""
    with open(f"configs/{config_path}", "r") as f:
        return f.read()

def create_production_jobs():
    """Create production-ready jobs."""
    
    # Load external configurations
    migration_config = load_config("jobs/migration.conf")
    
    # Database migration job
    migration_job = (Job("database-migration")
        .image("migrator:v2.1.0")
        .command(["python", "migrate.py"])
        .args(["--env", "production", "--dry-run", "false"])
        .env("DATABASE_URL", "postgres://postgres-service:5432/myapp")
        .env("MIGRATION_PATH", "/migrations")
        .env("LOG_LEVEL", "info")
        .resources(cpu="1000m", memory="2Gi", cpu_limit="2000m", memory_limit="4Gi")
        .parallelism(1)
        .completions(1)
        .retry_limit(3)
        .timeout("2h")
        .restart_policy("OnFailure")
        .add_secret(Secret("db-secret").add("password", "secure-password"))
        .add_config(ConfigMap("migration-config").add_data("migration.conf", migration_config))
        .security_context({
            "runAsNonRoot": True,
            "runAsUser": 1000,
            "fsGroup": 1000
        })
        .node_selector({"node-type": "database"})
        .toleration("database", "Equal", "true", "NoSchedule"))
    
    # Data backup job
    backup_job = (Job("data-backup")
        .image("backup-tool:v1.0.0")
        .command(["bash", "-c", "pg_dump $DATABASE_URL | gzip > /backups/backup-$(date +%Y%m%d).sql.gz"])
        .env("DATABASE_URL", "postgres://postgres-service:5432/myapp")
        .env("BACKUP_RETENTION", "30")
        .resources(cpu="500m", memory="1Gi")
        .parallelism(1)
        .completions(1)
        .retry_limit(5)
        .timeout("1h")
        .add_secret(Secret("backup-secret").add("password", "backup-password"))
        .add_volume("backup-storage", {
            "persistentVolumeClaim": {
                "claimName": "backup-pvc"
            }
        })
        .mount_volume("backup-storage", "/backups"))
    
    # Batch processing job
    batch_job = (Job("batch-processing")
        .image("processor:v3.0.0")
        .command(["python", "process.py"])
        .args(["--input", "/data/input", "--output", "/data/output"])
        .env("BATCH_SIZE", "1000")
        .env("WORKERS", "4")
        .resources(cpu="2000m", memory="4Gi", cpu_limit="4000m", memory_limit="8Gi")
        .parallelism(5)
        .completions(10)
        .retry_limit(3)
        .timeout("6h")
        .add_volume("input-data", {
            "persistentVolumeClaim": {
                "claimName": "input-pvc"
            }
        })
        .add_volume("output-data", {
            "persistentVolumeClaim": {
                "claimName": "output-pvc"
            }
        })
        .mount_volume("input-data", "/data/input", read_only=True)
        .mount_volume("output-data", "/data/output"))
    
    # Monitoring job
    monitoring_job = (Job("health-check")
        .image("monitor:v1.0.0")
        .command(["python", "health_check.py"])
        .env("CHECK_INTERVAL", "30")
        .env("TIMEOUT", "10")
        .resources(cpu="100m", memory="256Mi")
        .parallelism(1)
        .completions(1)
        .retry_limit(2)
        .timeout("5m")
        .restart_policy("Never")
        .metrics_port(9090)
        .web_port(8080))
    
    return [migration_job, backup_job, batch_job, monitoring_job]

if __name__ == "__main__":
    jobs = create_production_jobs()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    for job in jobs:
        output.generate(job, "production-jobs/")
    
    print("✅ Production jobs generated!")
    print("🚀 Deploy: kubectl apply -f production-jobs/")
```

## Generated Kubernetes Resources

The Job class generates the following Kubernetes resources:

- **Job** - Kubernetes Job with the specified configuration
- **Secret** - Secrets (if configured)
- **ConfigMap** - ConfigMaps (if configured)
- **Volume** - Volumes (if configured)

## Usage Patterns

### Database Migration Jobs

```python
# Database migration
migration_job = (Job("db-migration")
    .image("migrator:latest")
    .command(["python", "migrate.py"])
    .env("DATABASE_URL", "postgres://localhost:5432/myapp")
    .resources(cpu="1000m", memory="2Gi")
    .timeout("1h")
    .retry_limit(3))
```

### Backup Jobs

```python
# Database backup
backup_job = (Job("db-backup")
    .image("backup-tool:latest")
    .command(["pg_dump", "myapp", "|", "gzip", ">", "/backups/backup.sql.gz"])
    .env("DATABASE_URL", "postgres://localhost:5432/myapp")
    .resources(cpu="500m", memory="1Gi")
    .timeout("30m")
    .add_volume("backup-storage", {"persistentVolumeClaim": {"claimName": "backup-pvc"}})
    .mount_volume("backup-storage", "/backups"))
```

### Batch Processing Jobs

```python
# Batch data processing
batch_job = (Job("data-processing")
    .image("processor:latest")
    .command(["python", "process.py"])
    .env("BATCH_SIZE", "1000")
    .resources(cpu="2000m", memory="4Gi")
    .parallelism(5)
    .completions(10)
    .timeout("6h"))
```

### Monitoring Jobs

```python
# Health check job
health_job = (Job("health-check")
    .image("monitor:latest")
    .command(["python", "health_check.py"])
    .env("CHECK_INTERVAL", "30")
    .resources(cpu="100m", memory="256Mi")
    .timeout("5m")
    .restart_policy("Never"))
```

### ML Training Jobs

```python
# Machine learning training
ml_job = (Job("ml-training")
    .image("ml-trainer:latest")
    .command(["python", "train.py"])
    .env("MODEL_TYPE", "transformer")
    .env("EPOCHS", "100")
    .resources(cpu="4000m", memory="16Gi", gpu=2)
    .timeout("24h")
    .node_selector({"accelerator": "gpu"})
    .toleration("nvidia.com/gpu", "Equal", "present", "NoSchedule"))
```

## Best Practices

### 1. Set Appropriate Timeouts

```python
# ✅ Good: Set reasonable timeouts
job = Job("migration").timeout("2h")

# ❌ Bad: No timeout (may run forever)
job = Job("migration")  # No timeout
```

### 2. Use Resource Limits

```python
# ✅ Good: Set resource limits
job = Job("processing").resources(cpu="1000m", memory="2Gi", cpu_limit="2000m", memory_limit="4Gi")

# ❌ Bad: No resource limits
job = Job("processing")  # No resource limits
```

### 3. Set Retry Limits

```python
# ✅ Good: Set retry limits
job = Job("migration").retry_limit(3)

# ❌ Bad: Too many retries
job = Job("migration").retry_limit(100)  # May cause infinite loops
```

### 4. Use Appropriate Restart Policies

```python
# ✅ Good: Use appropriate restart policy
job = Job("migration").restart_policy("OnFailure")

# ❌ Bad: Always restart for batch jobs
job = Job("migration").restart_policy("Always")  # Not suitable for batch jobs
```

### 5. Use Parallelism Wisely

```python
# ✅ Good: Use appropriate parallelism
job = Job("batch-processing").parallelism(5).completions(10)

# ❌ Bad: Too much parallelism
job = Job("batch-processing").parallelism(1000)  # May overwhelm cluster
``` 