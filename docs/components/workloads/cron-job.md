# CronJob Component

The `CronJob` component runs jobs on a scheduled basis using cron syntax. It's perfect for recurring tasks like backups, reports, and maintenance operations.

## Overview

Use `CronJob` for:
- **Scheduled Backups** - Database and file system backups
- **Data Processing** - ETL jobs, report generation
- **Maintenance Tasks** - Log cleanup, cache warming
- **Monitoring Jobs** - Health checks, data validation
- **Recurring Reports** - Daily/weekly/monthly reports

## Basic Usage

```python
from src.k8s_gen import CronJob

# Daily backup job
backup_job = (CronJob("daily-backup")
    .schedule("0 2 * * *")  # Every day at 2 AM
    .image("backup-tool:latest")
    .command(["sh", "-c", "pg_dump mydb > /backup/$(date +%Y%m%d).sql"])
    .timeout(3600)  # 1 hour timeout
    .history_limits(success=3, failed=1))
```

## Schedule Configuration

### Cron Schedule Syntax

```python
# Common schedule patterns
daily = CronJob("daily-task").schedule("0 2 * * *")        # Daily at 2 AM
hourly = CronJob("hourly-task").schedule("0 * * * *")      # Every hour
weekly = CronJob("weekly-task").schedule("0 2 * * 0")      # Sunday at 2 AM
monthly = CronJob("monthly-task").schedule("0 2 1 * *")    # 1st of month at 2 AM
workdays = CronJob("workday-task").schedule("0 9 * * 1-5") # Weekdays at 9 AM

# Complex schedules
every_15_min = CronJob("frequent-task").schedule("*/15 * * * *")  # Every 15 minutes
twice_daily = CronJob("twice-daily").schedule("0 6,18 * * *")     # 6 AM and 6 PM
```

### Schedule Examples

| Schedule | Cron Expression | Description |
|----------|-----------------|-------------|
| Every minute | `* * * * *` | Testing only |
| Every 5 minutes | `*/5 * * * *` | Frequent monitoring |
| Every hour | `0 * * * *` | Hourly tasks |
| Daily at midnight | `0 0 * * *` | Daily maintenance |
| Daily at 2:30 AM | `30 2 * * *` | Backup window |
| Every Sunday | `0 0 * * 0` | Weekly reports |
| First of month | `0 0 1 * *` | Monthly billing |
| Weekdays at 9 AM | `0 9 * * 1-5` | Business hours |

## Configuration Methods

### Basic CronJob Setup

```python
# Basic scheduled job
cronjob = (CronJob("log-cleanup")
    .schedule("0 3 * * *")  # Daily at 3 AM
    .image("busybox:latest")
    .command(["sh", "-c", "find /logs -name '*.log' -mtime +7 -delete"])
    .timeout(1800)  # 30 minutes
    .restart_policy("OnFailure")
    .concurrency_policy("Forbid"))  # Don't run concurrent jobs
```

### Advanced Configuration

```python
# Advanced CronJob with full configuration
advanced_cronjob = (CronJob("data-sync")
    .schedule("0 */6 * * *")  # Every 6 hours
    .timezone("America/New_York")  # Specific timezone
    .image("data-sync:v2.1.0")
    .command(["python", "sync_data.py"])
    .args(["--mode", "incremental", "--verify"])
    
    # Job behavior
    .concurrency_policy("Replace")  # Replace running job if new one starts
    .starting_deadline_seconds(300)  # Start within 5 minutes or skip
    .suspend(False)  # Job is active
    
    # History management
    .history_limits(success=5, failed=3)
    
    # Resource management
    .resources(cpu="1000m", memory="2Gi")
    .timeout(7200)  # 2 hours
    .retry_limit(2)
    
    # Storage and configuration
    .storage("/data", "50Gi")
    .env("SYNC_MODE", "incremental")
    .env_from_secret("api-credentials", "API_KEY", "sync-api-key"))
```

## Complete Examples

### Database Backup CronJob

```python
#!/usr/bin/env python3
"""
Database Backup CronJob Example
"""

from src.k8s_gen import CronJob, Secret, ConfigMap, KubernetesOutput

def create_backup_cronjob():
    # Backup credentials
    backup_secret = (Secret("backup-credentials")
        .add_data("db-url", "postgresql://backup_user:secret@postgres:5432/myapp")
        .add_data("s3-access-key", "AKIA...")
        .add_data("s3-secret-key", "secret...")
        .add_data("encryption-key", "backup-encryption-key"))
    
    # Backup configuration
    backup_config = (ConfigMap("backup-config")
        .add_data("S3_BUCKET", "company-db-backups")
        .add_data("S3_REGION", "us-west-2")
        .add_data("RETENTION_DAYS", "30")
        .add_data("COMPRESSION", "gzip")
        .add_file("backup.sh", """#!/bin/bash
set -e

echo "Starting backup at $(date)"

# Create timestamped backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="backup_${TIMESTAMP}.sql"

# Dump database
pg_dump "${DATABASE_URL}" > "/tmp/${BACKUP_FILE}"

# Compress backup
gzip "/tmp/${BACKUP_FILE}"
BACKUP_FILE="${BACKUP_FILE}.gz"

# Encrypt backup
gpg --symmetric --cipher-algo AES256 --compress-algo 1 --s2k-mode 3 \\
    --s2k-digest-algo SHA512 --s2k-count 65536 --force-mdc \\
    --passphrase "${ENCRYPTION_KEY}" \\
    --output "/tmp/${BACKUP_FILE}.gpg" "/tmp/${BACKUP_FILE}"

# Upload to S3
aws s3 cp "/tmp/${BACKUP_FILE}.gpg" "s3://${S3_BUCKET}/daily/${BACKUP_FILE}.gpg"

# Cleanup old backups
aws s3 ls "s3://${S3_BUCKET}/daily/" | \\
    awk '{print $4}' | \\
    head -n -${RETENTION_DAYS} | \\
    xargs -I {} aws s3 rm "s3://${S3_BUCKET}/daily/{}"

# Cleanup local files
rm -f "/tmp/${BACKUP_FILE}" "/tmp/${BACKUP_FILE}.gpg"

echo "Backup completed successfully at $(date)"
"""))
    
    # Daily backup CronJob
    backup_cronjob = (CronJob("database-backup")
        .schedule("0 2 * * *")  # Daily at 2 AM
        .timezone("UTC")
        .image("backup-tool:v1.2.0")
        .command(["sh", "/scripts/backup.sh"])
        
        # Environment
        .env_from_secret("backup-credentials", "DATABASE_URL", "db-url")
        .env_from_secret("backup-credentials", "AWS_ACCESS_KEY_ID", "s3-access-key")
        .env_from_secret("backup-credentials", "AWS_SECRET_ACCESS_KEY", "s3-secret-key")
        .env_from_secret("backup-credentials", "ENCRYPTION_KEY", "encryption-key")
        .env_from_configmap("backup-config", "S3_BUCKET")
        .env_from_configmap("backup-config", "S3_REGION")
        .env_from_configmap("backup-config", "RETENTION_DAYS")
        
        # Resources
        .resources(cpu="500m", memory="1Gi")
        .storage("/tmp", "10Gi")  # Temporary storage for backup files
        .config_volume("/scripts", "backup-config")
        
        # Job configuration
        .timeout(3600)  # 1 hour timeout
        .retry_limit(2)
        .restart_policy("OnFailure")
        .concurrency_policy("Forbid")  # Don't run overlapping backups
        .starting_deadline_seconds(300)  # Start within 5 minutes
        
        # History
        .history_limits(success=7, failed=3)  # Keep 7 successful, 3 failed
        
        # Metadata
        .label("type", "backup")
        .label("database", "postgresql")
        .annotation("backup.io/schedule", "daily")
        .annotation("backup.io/retention", "30-days"))
    
    return backup_secret, backup_config, backup_cronjob

if __name__ == "__main__":
    secret, config, cronjob = create_backup_cronjob()
    
    components = [secret, config, cronjob]
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "backup-cronjob/")
    
    print("✅ Backup CronJob generated!")
    print("🚀 Deploy: kubectl apply -f backup-cronjob/")
```

### Report Generation CronJob

```python
def create_report_cronjobs():
    """Create multiple report generation CronJobs"""
    
    # Daily sales report
    daily_report = (CronJob("daily-sales-report")
        .schedule("0 6 * * *")  # 6 AM daily
        .image("reporter:latest")
        .command(["python", "generate_report.py"])
        .args(["--type", "sales", "--period", "daily"])
        .env("OUTPUT_FORMAT", "pdf")
        .env("EMAIL_RECIPIENTS", "sales@company.com,management@company.com")
        .env_from_secret("email-config", "SMTP_PASSWORD", "smtp-password")
        .resources(cpu="500m", memory="1Gi")
        .timeout(1800)  # 30 minutes
        .concurrency_policy("Forbid"))
    
    # Weekly analytics report
    weekly_report = (CronJob("weekly-analytics-report")
        .schedule("0 8 * * 1")  # Monday at 8 AM
        .image("analytics:latest")
        .command(["python", "analytics_report.py"])
        .args(["--period", "weekly", "--include-trends"])
        .env("DATABASE_POOL_SIZE", "10")
        .env("CACHE_TTL", "3600")
        .resources(cpu="2000m", memory="4Gi")  # More resources for analytics
        .timeout(7200)  # 2 hours
        .storage("/cache", "20Gi")  # Cache for analytics data
        .concurrency_policy("Forbid"))
    
    # Monthly billing report
    monthly_report = (CronJob("monthly-billing-report")
        .schedule("0 9 1 * *")  # 1st of month at 9 AM
        .image("billing:latest")
        .command(["python", "billing_report.py"])
        .args(["--month", "previous"])
        .env("BILLING_SYSTEM", "stripe")
        .env("CURRENCY", "USD")
        .env_from_secret("billing-secret", "STRIPE_API_KEY", "api-key")
        .resources(cpu="1000m", memory="2Gi")
        .timeout(3600)
        .concurrency_policy("Forbid")
        .starting_deadline_seconds(86400))  # Can start within 24 hours
    
    return daily_report, weekly_report, monthly_report
```

### Maintenance CronJobs

```python
def create_maintenance_cronjobs():
    """Create system maintenance CronJobs"""
    
    # Log cleanup (daily)
    log_cleanup = (CronJob("log-cleanup")
        .schedule("0 1 * * *")  # 1 AM daily
        .image("busybox:latest")
        .command(["sh", "-c", """
            echo "Starting log cleanup..."
            
            # Remove logs older than 7 days
            find /var/log -name "*.log" -mtime +7 -delete
            find /var/log -name "*.log.*" -mtime +7 -delete
            
            # Compress logs older than 1 day
            find /var/log -name "*.log" -mtime +1 -exec gzip {} \\;
            
            echo "Log cleanup completed"
        """])
        .storage("/var/log", "10Gi")
        .resources(cpu="100m", memory="128Mi")
        .timeout(900)  # 15 minutes
        .concurrency_policy("Forbid"))
    
    # Database maintenance (weekly)
    db_maintenance = (CronJob("database-maintenance")
        .schedule("0 3 * * 0")  # Sunday at 3 AM
        .image("postgres:13")
        .command(["sh", "-c", """
            echo "Starting database maintenance..."
            
            # Vacuum and analyze all databases
            vacuumdb --all --analyze --verbose
            
            # Reindex if needed
            reindexdb --all --verbose
            
            echo "Database maintenance completed"
        """])
        .env_from_secret("db-credentials", "PGPASSWORD", "postgres-password")
        .env("PGHOST", "postgres")
        .env("PGUSER", "postgres")
        .resources(cpu="1000m", memory="2Gi")
        .timeout(7200)  # 2 hours
        .concurrency_policy("Forbid"))
    
    # Cache warming (every 4 hours)
    cache_warming = (CronJob("cache-warming")
        .schedule("0 */4 * * *")  # Every 4 hours
        .image("cache-warmer:latest")
        .command(["python", "warm_cache.py"])
        .env("REDIS_URL", "redis://redis:6379")
        .env("CACHE_PATTERNS", "user_sessions,product_catalog,search_indexes")
        .resources(cpu="200m", memory="512Mi")
        .timeout(1800)  # 30 minutes
        .concurrency_policy("Replace"))  # Replace if still running
    
    return log_cleanup, db_maintenance, cache_warming
```

## CronJob Patterns

### Concurrency Policies

```python
# Allow concurrent runs
concurrent_job = (CronJob("data-processor")
    .schedule("*/5 * * * *")
    .concurrency_policy("Allow")  # Multiple instances can run
    .image("processor:latest"))

# Forbid concurrent runs
exclusive_job = (CronJob("critical-backup")
    .schedule("0 2 * * *")
    .concurrency_policy("Forbid")  # Wait for previous to complete
    .image("backup:latest"))

# Replace running job
replace_job = (CronJob("status-checker")
    .schedule("* * * * *")
    .concurrency_policy("Replace")  # Kill old, start new
    .image("checker:latest"))
```

### Error Handling

```python
# Retry on failure
retry_job = (CronJob("flaky-task")
    .schedule("0 * * * *")
    .retry_limit(3)  # Retry up to 3 times
    .restart_policy("OnFailure")
    .image("flaky:latest"))

# No retries for one-shot tasks
oneshot_job = (CronJob("report-sender")
    .schedule("0 9 * * *")
    .retry_limit(0)  # Don't retry
    .restart_policy("Never")
    .image("mailer:latest"))
```

### Timezone Handling

```python
# Use specific timezone
eastern_job = (CronJob("eastern-report")
    .schedule("0 9 * * 1-5")  # 9 AM weekdays
    .timezone("America/New_York")
    .image("reporter:latest"))

# UTC (default)
utc_job = (CronJob("global-sync")
    .schedule("0 0 * * *")  # Midnight UTC
    .timezone("UTC")  # Explicit UTC
    .image("sync:latest"))
```

## Generated YAML

### Basic CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
spec:
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      activeDeadlineSeconds: 3600
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: daily-backup
            image: backup-tool:latest
            command: ["sh", "-c", "pg_dump mydb > /backup/$(date +%Y%m%d).sql"]
```

### Advanced CronJob

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-sync
spec:
  schedule: "0 */6 * * *"
  timeZone: "America/New_York"
  concurrencyPolicy: Replace
  startingDeadlineSeconds: 300
  suspend: false
  successfulJobsHistoryLimit: 5
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      activeDeadlineSeconds: 7200
      backoffLimit: 2
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: data-sync
            image: data-sync:v2.1.0
            command: ["python", "sync_data.py"]
            args: ["--mode", "incremental", "--verify"]
            resources:
              requests:
                cpu: 1000m
                memory: 2Gi
```

## Best Practices

!!! tip "CronJob Best Practices"
    
    **Scheduling:**
    - Use UTC timezone for global applications
    - Avoid overlapping schedules for resource-intensive jobs
    - Consider business hours and maintenance windows
    
    **Concurrency:**
    - Use "Forbid" for exclusive operations (backups, migrations)
    - Use "Replace" for status checks and monitoring
    - Use "Allow" only when jobs are truly independent
    
    **Resource Management:**
    - Set appropriate timeouts for job completion
    - Monitor resource usage patterns
    - Use resource requests and limits
    
    **Error Handling:**
    - Set retry limits based on job idempotency
    - Monitor failed jobs and alerts
    - Implement proper logging and error reporting

## Monitoring and Observability

### Health Checks

```python
# CronJob with health monitoring
monitored_job = (CronJob("health-monitor")
    .schedule("*/5 * * * *")  # Every 5 minutes
    .image("health-checker:latest")
    .command(["python", "check_health.py"])
    .env("SLACK_WEBHOOK", "https://hooks.slack.com/...")
    .env("ALERT_THRESHOLD", "3")  # Alert after 3 failures
    .timeout(300)  # 5 minutes
    .concurrency_policy("Replace")
    .history_limits(success=1, failed=5))  # Keep failure history
```

### Alerting

```python
# CronJob with alerting on failure
alerting_job = (CronJob("critical-sync")
    .schedule("0 */2 * * *")  # Every 2 hours
    .image("sync:latest")
    .env("ALERT_ON_FAILURE", "true")
    .env("ALERT_EMAIL", "ops@company.com")
    .annotation("alert.io/critical", "true")
    .annotation("alert.io/runbook", "https://wiki.company.com/runbook/sync"))
```

## Troubleshooting

### Common CronJob Issues

!!! warning "Jobs Not Running"
    ```bash
    # Check CronJob status
    kubectl get cronjobs
    kubectl describe cronjob <cronjob-name>
    
    # Check recent jobs
    kubectl get jobs -l job-name=<cronjob-name>
    
    # Check if suspended
    kubectl get cronjob <cronjob-name> -o yaml | grep suspend
    ```

!!! warning "Schedule Issues"
    ```bash
    # Validate cron expression
    # Use online cron validators or:
    # https://crontab.guru/
    
    # Check timezone settings
    kubectl get cronjob <cronjob-name> -o yaml | grep timeZone
    
    # Check starting deadline
    kubectl describe cronjob <cronjob-name> | grep "Starting Deadline"
    ```

!!! warning "Concurrent Job Issues"
    ```bash
    # Check for running jobs
    kubectl get jobs -l job-name=<cronjob-name> --field-selector=status.successful!=1
    
    # Check concurrency policy
    kubectl get cronjob <cronjob-name> -o yaml | grep concurrencyPolicy
    ```

### Debug Commands

```bash
# Monitor CronJob executions
kubectl get cronjobs -w

# Check job history
kubectl get jobs -l job-name=<cronjob-name> --sort-by=.metadata.creationTimestamp

# View job logs
kubectl logs -l job-name=<cronjob-name> --tail=100

# Manually trigger a job
kubectl create job --from=cronjob/<cronjob-name> <manual-job-name>

# Suspend/resume CronJob
kubectl patch cronjob <cronjob-name> -p '{"spec":{"suspend":true}}'
kubectl patch cronjob <cronjob-name> -p '{"spec":{"suspend":false}}'
```

## API Reference

::: src.k8s_gen.workloads.cron_job.CronJob
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[Job](job.md)** - One-time batch jobs
- **[App](../core/app.md)** - Long-running applications
- **[ConfigMap](../storage/config-map.md)** - Job configuration
- **[Secret](../security/secrets.md)** - Job credentials

---

**Next:** Learn about [Lifecycle](lifecycle.md) for container lifecycle management. 