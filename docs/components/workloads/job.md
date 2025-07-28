# Job Component

The `Job` component is designed for running batch jobs and one-time tasks in Kubernetes. It ensures that a specified number of pods successfully complete their work.

## Overview

Use `Job` for:
- **Data Processing** - ETL jobs, data migrations
- **Batch Operations** - Image processing, report generation
- **Maintenance Tasks** - Database cleanup, backup operations
- **One-time Setup** - Initial configuration, database seeding

## Basic Usage

```python
from src.k8s_gen import Job

# Simple batch job
job = (Job("data-migration")
    .image("migrator:latest")
    .command(["python", "migrate.py"])
    .timeout(3600)  # 1 hour timeout
    .retry_limit(3))
```

## Configuration Methods

### Basic Job Setup

```python
# Basic job configuration
job = (Job("backup-job")
    .image("backup:v1.0.0")
    .command(["sh", "-c", "pg_dump mydb > /backup/backup.sql"])
    .working_dir("/app")
    .timeout(1800)  # 30 minutes
    .retry_limit(2))
```

### Parallel Jobs

```python
# Parallel processing job
parallel_job = (Job("parallel-processor")
    .image("processor:latest")
    .parallelism(5)  # Run 5 pods in parallel
    .completions(100)  # Process 100 items total
    .completion_mode("Indexed")  # Each pod gets an index
    .timeout(7200))  # 2 hours total
```

### Resource Management

```python
# Resource-intensive job
heavy_job = (Job("ml-training")
    .image("tensorflow:latest")
    .command(["python", "train_model.py"])
    .resources(
        cpu="4000m",
        memory="8Gi",
        cpu_limit="8000m",
        memory_limit="16Gi"
    )
    .gpu_resources(nvidia_gpu=2)  # Request 2 GPUs
    .timeout(14400))  # 4 hours
```

### Environment and Configuration

```python
# Job with environment configuration
config_job = (Job("config-processor")
    .image("processor:latest")
    .env("BATCH_SIZE", "1000")
    .env("OUTPUT_FORMAT", "json")
    .env("LOG_LEVEL", "info")
    .env_from_secret("db-secret", "DATABASE_URL", "connection-string")
    .env_from_configmap("app-config", "API_ENDPOINT", "api.url")
    .storage("/data", "10Gi")  # Temporary storage
    .config_volume("/config", "job-config"))
```

## Complete Examples

### Database Migration Job

```python
#!/usr/bin/env python3
"""
Database Migration Job Example
"""

from src.k8s_gen import Job, Secret, ConfigMap, KubernetesOutput

def create_migration_job():
    # Database credentials
    db_secret = (Secret("migration-secret")
        .add_data("source-db-url", "postgresql://user:pass@source:5432/olddb")
        .add_data("target-db-url", "postgresql://user:pass@target:5432/newdb")
        .add_data("migration-key", "secret-migration-key"))
    
    # Migration configuration
    migration_config = (ConfigMap("migration-config")
        .add_data("BATCH_SIZE", "1000")
        .add_data("PARALLEL_WORKERS", "4")
        .add_data("MIGRATION_MODE", "incremental")
        .add_file("migration.sql", """
-- Migration script
ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT NOW();
UPDATE users SET created_at = NOW() WHERE created_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);
"""))
    
    # Migration job
    migration_job = (Job("database-migration")
        .image("migration-tool:v2.1.0")
        .command(["python", "migrate.py"])
        .args(["--mode", "full", "--verify", "true"])
        
        # Environment
        .env_from_secret("migration-secret", "SOURCE_DB_URL", "source-db-url")
        .env_from_secret("migration-secret", "TARGET_DB_URL", "target-db-url")
        .env_from_secret("migration-secret", "MIGRATION_KEY", "migration-key")
        .env_from_configmap("migration-config", "BATCH_SIZE")
        .env_from_configmap("migration-config", "PARALLEL_WORKERS")
        .env_from_configmap("migration-config", "MIGRATION_MODE")
        
        # Resources
        .resources(cpu="2000m", memory="4Gi")
        .storage("/temp", "20Gi")  # Temporary storage for migration
        .config_volume("/scripts", "migration-config")
        
        # Job configuration
        .timeout(7200)  # 2 hours
        .retry_limit(1)  # Don't retry migrations
        .restart_policy("Never")
        
        # Cleanup
        .ttl_after_finished(86400)  # Clean up after 24 hours
        
        # Metadata
        .label("type", "migration")
        .label("version", "v2.1.0")
        .annotation("migration.io/source", "olddb")
        .annotation("migration.io/target", "newdb"))
    
    return db_secret, migration_config, migration_job

if __name__ == "__main__":
    secret, config, job = create_migration_job()
    
    components = [secret, config, job]
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "migration-job/")
    
    print("✅ Migration job generated!")
    print("🚀 Deploy: kubectl apply -f migration-job/")
```

### Data Processing Pipeline

```python
def create_data_pipeline():
    """Create a multi-stage data processing pipeline"""
    
    # Stage 1: Data extraction
    extract_job = (Job("data-extract")
        .image("extractor:latest")
        .command(["python", "extract.py"])
        .env("SOURCE_API", "https://api.example.com/data")
        .env("OUTPUT_PATH", "/shared/raw-data")
        .storage("/shared", "50Gi", storage_class="fast-ssd")
        .resources(cpu="1000m", memory="2Gi")
        .timeout(3600)
        .retry_limit(3))
    
    # Stage 2: Data transformation (parallel)
    transform_job = (Job("data-transform")
        .image("transformer:latest")
        .command(["python", "transform.py"])
        .env("INPUT_PATH", "/shared/raw-data")
        .env("OUTPUT_PATH", "/shared/processed-data")
        .storage("/shared", "50Gi", storage_class="fast-ssd")
        .parallelism(5)  # Process in parallel
        .completions(10)  # 10 transformation tasks
        .resources(cpu="2000m", memory="4Gi")
        .timeout(7200)
        .retry_limit(2))
    
    # Stage 3: Data loading
    load_job = (Job("data-load")
        .image("loader:latest")
        .command(["python", "load.py"])
        .env("INPUT_PATH", "/shared/processed-data")
        .env("TARGET_DB", "postgresql://warehouse:5432/analytics")
        .storage("/shared", "50Gi", storage_class="fast-ssd")
        .resources(cpu="500m", memory="1Gi")
        .timeout(1800)
        .retry_limit(2))
    
    return extract_job, transform_job, load_job
```

### Machine Learning Training Job

```python
def create_ml_training_job():
    """Create a machine learning training job"""
    
    # Training configuration
    training_config = (ConfigMap("ml-config")
        .add_data("MODEL_TYPE", "neural_network")
        .add_data("EPOCHS", "100")
        .add_data("BATCH_SIZE", "32")
        .add_data("LEARNING_RATE", "0.001")
        .add_file("model_config.yaml", """
model:
  type: neural_network
  layers:
    - type: dense
      units: 128
      activation: relu
    - type: dropout
      rate: 0.2
    - type: dense
      units: 64
      activation: relu
    - type: dense
      units: 10
      activation: softmax
  
training:
  optimizer: adam
  loss: categorical_crossentropy
  metrics: [accuracy]
"""))
    
    # Training job
    training_job = (Job("ml-model-training")
        .image("tensorflow/tensorflow:2.12.0-gpu")
        .command(["python", "train_model.py"])
        .args(["--config", "/config/model_config.yaml"])
        
        # Environment
        .env("CUDA_VISIBLE_DEVICES", "0,1")  # Use 2 GPUs
        .env("TF_CPP_MIN_LOG_LEVEL", "1")
        .env_from_configmap("ml-config", "MODEL_TYPE")
        .env_from_configmap("ml-config", "EPOCHS")
        .env_from_configmap("ml-config", "BATCH_SIZE")
        
        # Resources
        .resources(
            cpu="8000m",
            memory="32Gi",
            cpu_limit="16000m",
            memory_limit="64Gi"
        )
        .gpu_resources(nvidia_gpu=2)  # 2 NVIDIA GPUs
        
        # Storage
        .storage("/data", "100Gi", storage_class="fast-ssd")  # Training data
        .storage("/models", "50Gi", storage_class="standard")  # Model output
        .config_volume("/config", "ml-config")
        
        # Job settings
        .timeout(28800)  # 8 hours
        .retry_limit(1)  # Don't retry training jobs
        .restart_policy("Never")
        
        # Cleanup
        .ttl_after_finished(172800)  # Clean up after 48 hours
        
        # Metadata
        .label("workload", "ml-training")
        .label("model-version", "v1.0")
        .annotation("ml.io/experiment", "experiment-123")
        .annotation("ml.io/framework", "tensorflow"))
    
    return training_config, training_job
```

## Job Patterns

### Batch Processing with Work Queue

```python
# Work queue pattern
work_queue_job = (Job("work-queue-processor")
    .image("queue-worker:latest")
    .parallelism(10)  # 10 workers
    .completions(100)  # Process 100 items
    .completion_mode("NonIndexed")  # Workers pull from queue
    .env("QUEUE_URL", "redis://queue:6379")
    .env("WORKER_ID", "$(POD_NAME)")
    .resources(cpu="500m", memory="1Gi")
    .timeout(3600))
```

### Indexed Jobs

```python
# Indexed job pattern (each pod processes specific slice)
indexed_job = (Job("indexed-processor")
    .image("processor:latest")
    .parallelism(5)
    .completions(20)  # 20 items total
    .completion_mode("Indexed")  # Each pod gets JOB_COMPLETION_INDEX
    .env("TOTAL_ITEMS", "20")
    .env("ITEMS_PER_POD", "4")  # 20/5 = 4 items per pod
    .command(["python", "process_slice.py"])
    .resources(cpu="1000m", memory="2Gi"))
```

### Cleanup Jobs

```python
# Cleanup job with cron-like behavior
cleanup_job = (Job("nightly-cleanup")
    .image("cleanup:latest")
    .command(["sh", "-c", """
        # Clean up old files
        find /data -name '*.tmp' -mtime +7 -delete
        find /logs -name '*.log' -mtime +30 -delete
        
        # Compact databases
        vacuumdb --all
        
        echo 'Cleanup completed'
    """])
    .storage("/data", "10Gi")
    .storage("/logs", "5Gi")
    .resources(cpu="200m", memory="256Mi")
    .timeout(1800)
    .ttl_after_finished(3600))  # Clean up job after 1 hour
```

## Generated YAML

### Basic Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-migration
spec:
  backoffLimit: 3
  activeDeadlineSeconds: 3600
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: data-migration
        image: migrator:latest
        command: ["python", "migrate.py"]
        resources:
          requests:
            cpu: 2000m
            memory: 4Gi
  ttlSecondsAfterFinished: 86400
```

### Parallel Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: parallel-processor
spec:
  parallelism: 5
  completions: 100
  completionMode: Indexed
  activeDeadlineSeconds: 7200
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: parallel-processor
        image: processor:latest
        env:
        - name: JOB_COMPLETION_INDEX
          valueFrom:
            fieldRef:
              fieldPath: metadata.annotations['batch.kubernetes.io/job-completion-index']
```

## Best Practices

!!! tip "Job Design Guidelines"
    
    **Resource Management:**
    - Set appropriate CPU and memory limits
    - Use resource requests for scheduling
    - Consider GPU requirements for ML workloads
    
    **Timeout and Retries:**
    - Set realistic timeouts for job completion
    - Use retry limits carefully (some jobs shouldn't retry)
    - Consider using exponential backoff for retries
    
    **Storage:**
    - Use appropriate storage classes for performance
    - Plan for temporary storage needs
    - Consider shared storage for multi-stage pipelines
    
    **Cleanup:**
    - Set TTL for automatic job cleanup
    - Clean up associated resources (PVCs, secrets)
    - Monitor job completion and failures

## Common Patterns

### Multi-Stage Pipeline

```python
# Pipeline with dependencies
stage1 = Job("extract").timeout(3600)
stage2 = Job("transform").depends_on(stage1).timeout(7200)
stage3 = Job("load").depends_on(stage2).timeout(1800)
```

### Fan-out/Fan-in Pattern

```python
# Fan-out: One job creates work for many
coordinator = Job("coordinator").parallelism(1).completions(1)

# Many workers process the work
workers = Job("workers").parallelism(10).completions(100)

# Fan-in: Aggregate results
aggregator = Job("aggregator").depends_on(workers)
```

## Troubleshooting

### Common Job Issues

!!! warning "Job Not Starting"
    ```bash
    # Check job status
    kubectl get jobs
    kubectl describe job <job-name>
    
    # Check pod status
    kubectl get pods -l job-name=<job-name>
    kubectl describe pod <pod-name>
    ```

!!! warning "Job Timeout"
    ```bash
    # Check job events
    kubectl get events --field-selector involvedObject.name=<job-name>
    
    # Check pod logs
    kubectl logs -l job-name=<job-name>
    ```

!!! warning "Failed Jobs"
    ```bash
    # Check failed pods
    kubectl get pods -l job-name=<job-name> --field-selector=status.phase=Failed
    
    # Get failure reason
    kubectl describe pod <failed-pod-name>
    kubectl logs <failed-pod-name> --previous
    ```

### Debug Commands

```bash
# Monitor job progress
kubectl get jobs -w

# Check job completion
kubectl wait --for=condition=complete job/<job-name> --timeout=3600s

# View job logs
kubectl logs -l job-name=<job-name> -f

# Clean up completed jobs
kubectl delete jobs --field-selector status.successful=1
```

## API Reference

::: src.k8s_gen.workloads.job.Job
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[CronJob](cron-job.md)** - Scheduled jobs
- **[App](../core/app.md)** - Long-running applications
- **[ConfigMap](../storage/config-map.md)** - Job configuration
- **[Secret](../security/secrets.md)** - Job credentials

---

**Next:** Learn about [CronJob](cron-job.md) for scheduled batch jobs. 