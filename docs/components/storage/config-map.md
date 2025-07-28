# ConfigMap Component

The `ConfigMap` component provides configuration data storage for your applications, allowing you to separate configuration from application code and manage settings externally.

## Overview

Use `ConfigMap` for:
- **Application Configuration** - App settings, feature flags
- **Environment Variables** - Non-sensitive configuration values
- **Configuration Files** - Properties, YAML, JSON configuration files
- **Script Storage** - Shell scripts, SQL scripts, configuration scripts

## Basic Usage

```python
from src.k8s_gen import ConfigMap

# Simple key-value configuration
config = (ConfigMap("app-config")
    .add_data("database.host", "postgres.default.svc.cluster.local")
    .add_data("database.port", "5432")
    .add_data("log.level", "info"))
```

## Configuration Methods

### Key-Value Data

```python
# Simple configuration values
app_config = (ConfigMap("web-app-config")
    .add_data("API_BASE_URL", "https://api.example.com")
    .add_data("MAX_CONNECTIONS", "100")
    .add_data("TIMEOUT", "30")
    .add_data("DEBUG_MODE", "false")
    .add_data("FEATURE_FLAG_X", "enabled"))
```

### Configuration Files

```python
# Complete configuration files
database_config = (ConfigMap("database-config")
    .add_file("postgresql.conf", """
# PostgreSQL Configuration
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
checkpoint_completion_target = 0.9
""")
    .add_file("pg_hba.conf", """
# PostgreSQL HBA Configuration
local   all             all                     trust
host    all             all     127.0.0.1/32    md5
host    all             all     ::1/128         md5
"""))
```

### JSON and YAML Configuration

```python
# Structured configuration
api_config = (ConfigMap("api-config")
    .add_json("config.json", {
        "server": {
            "port": 8080,
            "host": "0.0.0.0"
        },
        "database": {
            "url": "postgresql://postgres:5432/myapp",
            "pool_size": 10
        },
        "features": {
            "auth": True,
            "logging": True,
            "metrics": True
        }
    })
    .add_yaml("logging.yaml", {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default"
            }
        },
        "root": {
            "level": "INFO",
            "handlers": ["console"]
        }
    }))
```

### Scripts and Executables

```python
# Shell scripts and tools
scripts_config = (ConfigMap("init-scripts")
    .add_script("init-db.sh", """#!/bin/bash
echo "Initializing database..."
createdb myapp
psql myapp < /scripts/schema.sql
echo "Database initialized successfully"
""")
    .add_script("backup.sh", """#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump myapp > /backups/backup_$DATE.sql
echo "Backup created: backup_$DATE.sql"
""")
    .executable(True))  # Make scripts executable
```

## Advanced Configuration

### Namespace and Metadata

```python
# Organized configuration with metadata
config = (ConfigMap("production-config")
    .namespace("production")
    .add_data("environment", "production")
    .add_data("region", "us-west-2")
    .label("component", "configuration")
    .label("environment", "production")
    .annotation("managed-by", "k8s-gen")
    .annotation("last-updated", "2024-01-15"))
```

### Immutable ConfigMaps

```python
# Immutable configuration (cannot be updated)
immutable_config = (ConfigMap("app-version-config")
    .add_data("version", "v1.2.3")
    .add_data("build-id", "build-12345")
    .add_data("commit-sha", "abc123def456")
    .immutable(True))
```

### Binary Data

```python
# Binary configuration files
binary_config = (ConfigMap("binary-config")
    .add_binary_file("keystore.jks", "/path/to/keystore.jks")
    .add_binary_file("truststore.jks", "/path/to/truststore.jks"))
```

## Complete Examples

### Web Application Configuration

```python
#!/usr/bin/env python3
"""
Complete Web Application Configuration
"""

from src.k8s_gen import ConfigMap, App, KubernetesOutput

def create_web_app_config():
    # Main application configuration
    app_config = (ConfigMap("web-app-config")
        .namespace("web")
        .add_data("NODE_ENV", "production")
        .add_data("PORT", "8080")
        .add_data("LOG_LEVEL", "info")
        .add_data("SESSION_TIMEOUT", "3600")
        .add_data("MAX_FILE_SIZE", "10485760")  # 10MB
        .label("component", "web-app"))
    
    # Database configuration
    database_config = (ConfigMap("database-config")
        .namespace("web")
        .add_data("DATABASE_HOST", "postgres.database.svc.cluster.local")
        .add_data("DATABASE_PORT", "5432")
        .add_data("DATABASE_NAME", "webapp")
        .add_data("CONNECTION_POOL_SIZE", "20")
        .add_data("CONNECTION_TIMEOUT", "5000")
        .label("component", "database"))
    
    # Redis configuration
    redis_config = (ConfigMap("redis-config")
        .namespace("web")
        .add_data("REDIS_HOST", "redis.cache.svc.cluster.local")
        .add_data("REDIS_PORT", "6379")
        .add_data("REDIS_DB", "0")
        .add_data("REDIS_TIMEOUT", "2000")
        .label("component", "cache"))
    
    # Nginx configuration
    nginx_config = (ConfigMap("nginx-config")
        .namespace("web")
        .add_file("nginx.conf", """
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server web-app:8080;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\\n";
            add_header Content-Type text/plain;
        }
    }
}
""")
        .label("component", "proxy"))
    
    # Application using the configurations
    web_app = (App("web-app")
        .image("webapp:v1.0.0")
        .namespace("web")
        .port(8080, "http")
        .env_from_configmap("web-app-config", "NODE_ENV")
        .env_from_configmap("web-app-config", "PORT")
        .env_from_configmap("web-app-config", "LOG_LEVEL")
        .env_from_configmap("database-config", "DATABASE_HOST")
        .env_from_configmap("database-config", "DATABASE_PORT")
        .env_from_configmap("redis-config", "REDIS_HOST")
        .env_from_configmap("redis-config", "REDIS_PORT")
        .config_volume("/etc/config", "web-app-config")
        .replicas(3))
    
    # Nginx proxy
    nginx = (App("nginx")
        .image("nginx:1.21")
        .namespace("web")
        .port(80, "http")
        .config_volume("/etc/nginx", "nginx-config")
        .replicas(2)
        .expose())
    
    return app_config, database_config, redis_config, nginx_config, web_app, nginx

if __name__ == "__main__":
    components = create_web_app_config()
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "web-app-config/")
    
    print("✅ Web application configuration generated!")
    print("🚀 Deploy: kubectl apply -f web-app-config/")
```

### Microservices Configuration

```python
def create_microservices_config():
    # Shared service discovery configuration
    service_discovery = (ConfigMap("service-discovery")
        .namespace("microservices")
        .add_data("USER_SERVICE_URL", "http://user-service.microservices.svc.cluster.local:8080")
        .add_data("ORDER_SERVICE_URL", "http://order-service.microservices.svc.cluster.local:8080")
        .add_data("PAYMENT_SERVICE_URL", "http://payment-service.microservices.svc.cluster.local:8080")
        .add_data("NOTIFICATION_SERVICE_URL", "http://notification-service.microservices.svc.cluster.local:8080")
        .label("scope", "shared"))
    
    # API Gateway configuration
    api_gateway_config = (ConfigMap("api-gateway-config")
        .namespace("microservices")
        .add_file("routes.yaml", """
routes:
  - path: /api/v1/users/*
    service: user-service
    port: 8080
    timeout: 30s
  - path: /api/v1/orders/*
    service: order-service
    port: 8080
    timeout: 45s
  - path: /api/v1/payments/*
    service: payment-service
    port: 8080
    timeout: 60s
""")
        .add_data("RATE_LIMIT", "1000")
        .add_data("CORS_ENABLED", "true")
        .label("component", "api-gateway"))
    
    # Monitoring configuration
    monitoring_config = (ConfigMap("monitoring-config")
        .namespace("microservices")
        .add_data("METRICS_ENABLED", "true")
        .add_data("METRICS_PORT", "9090")
        .add_data("HEALTH_CHECK_INTERVAL", "30")
        .add_data("TRACING_ENABLED", "true")
        .add_data("JAEGER_ENDPOINT", "http://jaeger-collector:14268/api/traces")
        .label("component", "monitoring"))
    
    return service_discovery, api_gateway_config, monitoring_config
```

### Database Configuration

```python
def create_database_configs():
    # PostgreSQL configuration
    postgres_config = (ConfigMap("postgres-config")
        .namespace("database")
        .add_file("postgresql.conf", """
# Connection Settings
listen_addresses = '*'
port = 5432
max_connections = 200

# Memory Settings
shared_buffers = 512MB
effective_cache_size = 2GB
work_mem = 8MB
maintenance_work_mem = 128MB

# Checkpoint Settings
checkpoint_completion_target = 0.9
checkpoint_timeout = 15min
max_wal_size = 2GB
min_wal_size = 1GB

# Logging Settings
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
""")
        .add_file("pg_hba.conf", """
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     trust
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
host    replication     postgres        0.0.0.0/0               md5
host    all             all             0.0.0.0/0               md5
"""))
    
    # Redis configuration
    redis_config = (ConfigMap("redis-config")
        .namespace("cache")
        .add_file("redis.conf", """
# Network
bind 0.0.0.0
port 6379
timeout 300
tcp-keepalive 60

# Memory
maxmemory 1gb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000
dir /data

# Security
requirepass redis-password-change-me

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
"""))
    
    return postgres_config, redis_config
```

## ConfigMap Usage in Applications

### Environment Variables

```python
# Use entire ConfigMap as environment variables
app = (App("config-app")
    .env_from_configmap("app-config")  # All keys become env vars
    .env_from_configmap("db-config", prefix="DB_"))  # With prefix

# Use specific keys
app = (App("selective-app")
    .env_from_configmap("app-config", "LOG_LEVEL", "log.level")
    .env_from_configmap("db-config", "DATABASE_URL", "database.url"))
```

### Volume Mounts

```python
# Mount ConfigMap as files
app = (App("file-config-app")
    .config_volume("/etc/config", "app-config")
    .config_volume("/etc/database", "db-config")
    .config_volume("/scripts", "init-scripts"))

# Mount specific keys as files
app = (App("specific-files-app")
    .config_volume("/etc/nginx", "nginx-config", 
                   files={"nginx.conf": "nginx.conf"}))
```

### Init Containers

```python
# Use ConfigMap in init containers
app = (App("init-app")
    .init_container("init", "busybox")
    .init_command(["sh", "/scripts/init.sh"])
    .init_config_volume("/scripts", "init-scripts"))
```

## Generated YAML

### Basic ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: web
data:
  database.host: "postgres.default.svc.cluster.local"
  database.port: "5432"
  log.level: "info"
```

### ConfigMap with Files

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: nginx-config
data:
  nginx.conf: |
    events {
        worker_connections 1024;
    }
    http {
        upstream backend {
            server web-app:8080;
        }
        server {
            listen 80;
            location / {
                proxy_pass http://backend;
            }
        }
    }
```

### Binary ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: binary-config
binaryData:
  keystore.jks: UEsDBBQACAgIAKhobY0AAAAAAAAAAAAAAAoAAABrZXlzdG9yZQ==
```

## Best Practices

!!! tip "ConfigMap Best Practices"
    
    **Organization:**
    - Group related configuration together
    - Use descriptive names and labels
    - Separate by component or environment
    
    **Size Management:**
    - Keep ConfigMaps under 1MB
    - Split large configurations into multiple ConfigMaps
    - Use external storage for very large files
    
    **Security:**
    - Never store sensitive data in ConfigMaps
    - Use Secrets for passwords and keys
    - Apply proper RBAC permissions
    
    **Versioning:**
    - Version ConfigMaps for rolling updates
    - Use immutable ConfigMaps for releases
    - Test configuration changes in staging

## Common Patterns

### Environment-Specific Configuration

```python
# Different configs per environment
dev_config = (ConfigMap("app-config-dev")
    .namespace("development")
    .add_data("LOG_LEVEL", "debug")
    .add_data("DEBUG", "true"))

prod_config = (ConfigMap("app-config-prod")
    .namespace("production")
    .add_data("LOG_LEVEL", "error")
    .add_data("DEBUG", "false"))
```

### Configuration Layers

```python
# Base configuration
base_config = ConfigMap("base-config").add_data("TIMEOUT", "30")

# Environment overrides
env_config = ConfigMap("env-config").add_data("TIMEOUT", "60")  # Override

# Feature flags
feature_config = ConfigMap("feature-config").add_data("NEW_FEATURE", "enabled")
```

### Shared Configuration

```python
# Shared across multiple applications
shared_config = (ConfigMap("shared-services")
    .add_data("REDIS_URL", "redis:6379")
    .add_data("ELASTIC_URL", "elasticsearch:9200")
    .add_data("JAEGER_URL", "jaeger:14268"))
```

## Troubleshooting

### Common ConfigMap Issues

!!! warning "ConfigMap Not Found"
    ```bash
    # Check if ConfigMap exists
    kubectl get configmaps -n <namespace>
    kubectl describe configmap <name> -n <namespace>
    
    # View ConfigMap data
    kubectl get configmap <name> -o yaml
    ```

!!! warning "Volume Mount Issues"
    ```bash
    # Check pod mounts
    kubectl describe pod <pod-name>
    kubectl exec <pod-name> -- ls -la /etc/config/
    
    # Check file contents
    kubectl exec <pod-name> -- cat /etc/config/app.conf
    ```

!!! warning "Environment Variable Issues"
    ```bash
    # Check environment variables in pod
    kubectl exec <pod-name> -- env | grep CONFIG
    kubectl exec <pod-name> -- printenv LOG_LEVEL
    ```

### Debug Commands

```bash
# List all ConfigMaps
kubectl get configmaps --all-namespaces

# View ConfigMap contents
kubectl get configmap <name> -o yaml
kubectl describe configmap <name>

# Check which pods use a ConfigMap
kubectl get pods -o json | jq '.items[] | select(.spec.volumes[]?.configMap.name=="<configmap-name>") | .metadata.name'

# Test configuration loading
kubectl run test-pod --image=busybox --rm -it -- sh
# Mount the ConfigMap and check files
```

## API Reference

::: src.k8s_gen.storage.config_map.ConfigMap
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[App](../core/app.md)** - Using ConfigMaps in applications
- **[Secret](../security/secrets.md)** - For sensitive configuration
- **[StatefulApp](../core/stateful-app.md)** - Configuration for stateful apps
- **[Job](../workloads/job.md)** - Configuration for batch jobs

---

**Next:** Learn about [Job](../workloads/job.md) for batch processing workloads. 