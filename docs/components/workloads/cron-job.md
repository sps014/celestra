# CronJob Class

The `CronJob` class manages Kubernetes CronJobs for scheduled batch workloads that run on a time-based schedule.

## Overview

```python
from celestra import CronJob

# Basic usage
backup_job = CronJob("daily-backup").schedule("0 2 * * *").image("backup-tool:latest")
```

## Functions

### schedule(cron_schedule: str) -> CronJob
Set the cron schedule for the job.

```python
# Daily at 2 AM
backup_job = CronJob("backup").schedule("0 2 * * *")

# Every 5 minutes
monitor_job = CronJob("monitor").schedule("*/5 * * * *")

# Weekly on Sunday at 3 AM
weekly_job = CronJob("weekly").schedule("0 3 * * 0")
```

### Convenience Schedule Methods

#### Daily Schedule
```python
# Daily at midnight (default)
job = CronJob("daily-job").daily()

# Daily at 2:30 AM
job = CronJob("backup").daily(hour=2, minute=30)
```

#### Weekly Schedule
```python
# Weekly on Sunday at midnight (default)
job = CronJob("weekly-job").weekly()

# Weekly on Monday at 9 AM
job = CronJob("report").weekly(day_of_week=1, hour=9)
```

#### Monthly Schedule
```python
# Monthly on 1st at midnight (default)
job = CronJob("monthly-job").monthly()

# Monthly on 15th at 6 PM
job = CronJob("billing").monthly(day=15, hour=18)
```

#### Every Minutes
```python
# Every 5 minutes
job = CronJob("monitor").every_minutes(5)

# Every 30 minutes
job = CronJob("check").every_minutes(30)
```

#### Every Hours
```python
# Every 2 hours
job = CronJob("sync").every_hours(2)

# Every 6 hours
job = CronJob("backup").every_hours(6)
```

### image(image: str) -> CronJob
Set the container image for the cron job.

```python
# Basic image
job = CronJob("backup").image("backup-tool:latest")

# Specific version
job = CronJob("cleanup").image("cleanup:v1.2.0")
```

### command(command: List[str]) -> CronJob
Set the command to run in the container.

```python
# Simple command
job = CronJob("backup").command(["backup.sh"])

# Complex command
job = CronJob("cleanup").command(["bash", "-c", "rm -rf /tmp/* && echo 'Cleanup complete'"])
```

### args(args: List[str]) -> CronJob
Set the arguments for the command.

```python
# Command with arguments
job = CronJob("backup").command(["pg_dump"]).args(["--host", "postgres", "myapp"])

# Multiple arguments
job = CronJob("report").command(["python"]).args(["generate_report.py", "--env", "production"])
```

### environment(env_vars: Dict[str, str]) -> CronJob
Set multiple environment variables at once.

```python
# Bulk environment variables
env_config = {
    "DATABASE_URL": "postgres://localhost:5432/myapp",
    "BACKUP_PATH": "/backups",
    "LOG_LEVEL": "info"
}
job = CronJob("backup").environment(env_config)
```

### env(key: str, value: str) -> CronJob
Add a single environment variable.

```python
# Single environment variable
job = CronJob("backup").env("DATABASE_URL", "postgres://localhost:5432/myapp")

# Multiple individual variables
job = (CronJob("backup")
    .env("BACKUP_PATH", "/backups")
    .env("RETENTION_DAYS", "30")
    .env("COMPRESSION", "gzip"))
```

### resources(cpu: str = None, memory: str = None, cpu_limit: str = None, memory_limit: str = None, gpu: int = None) -> CronJob
Set resource requests and limits for the cron job.

```python
# Basic resources
job = CronJob("backup").resources(cpu="500m", memory="1Gi")

# With limits
job = (CronJob("backup")
    .resources(
        cpu="500m", 
        memory="1Gi",
        cpu_limit="1000m",
        memory_limit="2Gi"
    ))
```

### concurrency_policy(policy: str) -> CronJob
Set the concurrency policy for the cron job.

```python
# Allow concurrent jobs (default)
job = CronJob("backup").concurrency_policy("Allow")

# Forbid concurrent jobs
job = CronJob("backup").concurrency_policy("Forbid")

# Replace running jobs
job = CronJob("backup").concurrency_policy("Replace")
```

### suspend(suspended: bool = True) -> CronJob
Suspend or resume the cron job.

```python
# Suspend the job
job = CronJob("backup").suspend(True)

# Resume the job
job = CronJob("backup").suspend(False)
```

### history_limits(successful: int = 3, failed: int = 1) -> CronJob
Set the number of successful and failed jobs to keep.

```python
# Keep 5 successful and 2 failed jobs
job = CronJob("backup").history_limits(successful=5, failed=2)

# Keep only 1 successful job
job = CronJob("backup").history_limits(successful=1, failed=1)
```

### starting_deadline(deadline_seconds: int) -> CronJob
Set the deadline for starting the job.

```python
# 5 minute deadline
job = CronJob("backup").starting_deadline(300)

# 1 hour deadline
job = CronJob("backup").starting_deadline(3600)
```

### timeout(timeout: Union[str, int]) -> CronJob
Set the timeout for the job.

```python
# Timeout in seconds
job = CronJob("backup").timeout(1800)

# Timeout as string
job = CronJob("backup").timeout("30m")

# Long timeout
job = CronJob("backup").timeout("2h")
```

### retry_limit(limit: int) -> CronJob
Set the number of retries for failed jobs.

```python
# No retries
job = CronJob("critical").retry_limit(0)

# Default retries
job = CronJob("backup").retry_limit(6)

# Many retries
job = CronJob("unreliable").retry_limit(10)
```

### timezone(tz: str) -> CronJob
Set the timezone for the cron schedule.

```python
# UTC timezone
job = CronJob("backup").timezone("UTC")

# Local timezone
job = CronJob("backup").timezone("America/New_York")

# Custom timezone
job = CronJob("backup").timezone("Europe/London")
```

### restart_policy(policy: str) -> CronJob
Set the restart policy for the job.

```python
# On failure (default)
job = CronJob("backup").restart_policy("OnFailure")

# Never restart
job = CronJob("critical").restart_policy("Never")

# Always restart
job = CronJob("monitoring").restart_policy("Always")
```

### port(port: int, name: str = "http", protocol: str = "TCP") -> CronJob
Add a port to the cron job.

```python
# Basic port
job = CronJob("web-job").port(8080, "http")

# Multiple ports
job = (CronJob("api-job")
    .port(8080, "http")
    .port(8443, "https")
    .port(9090, "metrics"))
```

### Convenience Port Methods

#### Metrics Port
```python
job = CronJob("monitoring-job").metrics_port(9090)
```

#### Web Port
```python
job = CronJob("web-job").web_port(8080)
```

#### Status Port
```python
job = CronJob("status-job").status_port(8081)
```

### add_secret(secret: Secret) -> CronJob
Add a secret to the cron job.

```python
# Add database secret
db_secret = Secret("db-secret").add("password", "secret123")
job = CronJob("backup").add_secret(db_secret)
```

### add_config(config_map: ConfigMap) -> CronJob
Add a ConfigMap to the cron job.

```python
# Add configuration
config = ConfigMap("backup-config").add("retention", "30")
job = CronJob("backup").add_config(config)
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete CronJob Example - Production Scheduled Jobs
"""

import os
from celestra import CronJob, Secret, ConfigMap, KubernetesOutput

def load_config(config_path: str) -> str:
    """Load configuration from external file."""
    with open(f"configs/{config_path}", "r") as f:
        return f.read()

def create_production_cronjobs():
    """Create production-ready cron jobs."""
    
    # Load external configurations
    backup_config = load_config("jobs/backup.conf")
    
    # Daily database backup
    backup_job = (CronJob("daily-backup")
        .schedule("0 2 * * *")  # Daily at 2 AM
        .image("backup-tool:v2.1.0")
        .command(["backup.sh"])
        .args(["--database", "myapp", "--compress"])
        .env("DATABASE_URL", "postgres://postgres-service:5432/myapp")
        .env("BACKUP_PATH", "/backups")
        .env("RETENTION_DAYS", "30")
        .resources(cpu="500m", memory="1Gi", cpu_limit="1000m", memory_limit="2Gi")
        .timeout("1h")
        .retry_limit(3)
        .concurrency_policy("Forbid")
        .history_limits(successful=7, failed=3)
        .add_secret(Secret("backup-secret").add("password", "backup-password"))
        .add_config(ConfigMap("backup-config").add_data("backup.conf", backup_config)))
    
    # Weekly cleanup job
    cleanup_job = (CronJob("weekly-cleanup")
        .weekly(day_of_week=0, hour=3)  # Sunday at 3 AM
        .image("cleanup-tool:v1.0.0")
        .command(["cleanup.sh"])
        .env("CLEANUP_PATH", "/tmp")
        .env("MAX_AGE_DAYS", "7")
        .resources(cpu="200m", memory="512Mi")
        .timeout("30m")
        .retry_limit(2)
        .concurrency_policy("Allow"))
    
    # Hourly monitoring check
    monitor_job = (CronJob("hourly-monitor")
        .every_hours(1)
        .image("monitor:v1.0.0")
        .command(["health_check.py"])
        .env("CHECK_INTERVAL", "3600")
        .env("TIMEOUT", "300")
        .resources(cpu="100m", memory="256Mi")
        .timeout("10m")
        .retry_limit(1)
        .concurrency_policy("Forbid"))
    
    # Monthly billing report
    billing_job = (CronJob("monthly-billing")
        .monthly(day=1, hour=6)  # 1st of month at 6 AM
        .image("billing:v1.0.0")
        .command(["generate_billing_report.py"])
        .args(["--month", "previous", "--format", "pdf"])
        .env("BILLING_API_URL", "https://billing-api.example.com")
        .env("REPORT_PATH", "/reports")
        .resources(cpu="1000m", memory="2Gi")
        .timeout("2h")
        .retry_limit(5)
        .concurrency_policy("Forbid")
        .add_secret(Secret("billing-secret").add("api_key", "billing-api-key")))
    
    return [backup_job, cleanup_job, monitor_job, billing_job]

if __name__ == "__main__":
    cronjobs = create_production_cronjobs()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    for job in cronjobs:
        output.generate(job, "production-cronjobs/")
    
    print("✅ Production cron jobs generated!")
    print("🚀 Deploy: kubectl apply -f production-cronjobs/")
```

## Generated Kubernetes Resources

The CronJob class generates the following Kubernetes resources:

- **CronJob** - Kubernetes CronJob with the specified schedule and configuration
- **Secret** - Secrets (if configured)
- **ConfigMap** - ConfigMaps (if configured)

## Usage Patterns

### Database Backup Jobs

```python
# Daily backup
backup_job = (CronJob("daily-backup")
    .schedule("0 2 * * *")
    .image("backup-tool:latest")
    .command(["pg_dump"])
    .env("DATABASE_URL", "postgres://localhost:5432/myapp")
    .timeout("1h")
    .concurrency_policy("Forbid"))
```

### Cleanup Jobs

```python
# Weekly cleanup
cleanup_job = (CronJob("weekly-cleanup")
    .weekly(day_of_week=0, hour=3)
    .image("cleanup-tool:latest")
    .command(["cleanup.sh"])
    .env("CLEANUP_PATH", "/tmp")
    .timeout("30m"))
```

### Monitoring Jobs

```python
# Hourly monitoring
monitor_job = (CronJob("hourly-monitor")
    .every_hours(1)
    .image("monitor:latest")
    .command(["health_check.py"])
    .env("CHECK_INTERVAL", "3600")
    .timeout("10m"))
```

### Report Generation Jobs

```python
# Monthly report
report_job = (CronJob("monthly-report")
    .monthly(day=1, hour=6)
    .image("report-generator:latest")
    .command(["generate_report.py"])
    .env("REPORT_TYPE", "monthly")
    .timeout("2h"))
```

## Best Practices

### 1. Use Appropriate Schedules

```python
# ✅ Good: Use descriptive schedules
backup_job = CronJob("backup").daily(hour=2)  # Daily at 2 AM

# ❌ Bad: Unclear schedule
backup_job = CronJob("backup").schedule("0 2 * * *")
```

### 2. Set Concurrency Policies

```python
# ✅ Good: Set appropriate concurrency policy
backup_job = CronJob("backup").concurrency_policy("Forbid")

# ❌ Bad: Allow concurrent backups
backup_job = CronJob("backup").concurrency_policy("Allow")
```

### 3. Set Timeouts

```python
# ✅ Good: Set reasonable timeouts
backup_job = CronJob("backup").timeout("1h")

# ❌ Bad: No timeout (may run forever)
backup_job = CronJob("backup")
```

### 4. Set Retry Limits

```python
# ✅ Good: Set retry limits
backup_job = CronJob("backup").retry_limit(3)

# ❌ Bad: Too many retries
backup_job = CronJob("backup").retry_limit(100)
```

### 5. Use History Limits

```python
# ✅ Good: Set history limits
backup_job = CronJob("backup").history_limits(successful=7, failed=3)

# ❌ Bad: Keep too many jobs
backup_job = CronJob("backup").history_limits(successful=100, failed=100)
``` 