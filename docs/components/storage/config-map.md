# ConfigMap Class

The `ConfigMap` class manages Kubernetes ConfigMaps for configuration data like application settings, environment variables, and configuration files.

## Overview

```python
from celestra import ConfigMap

# Basic usage
config = ConfigMap("app-config").add("debug", "true").add("port", "8080")
```

## Functions

### add(key: str, value: str) -> ConfigMap
Add a key-value pair to the ConfigMap.

```python
# Basic configuration
config = ConfigMap("app-config").add("debug", "true")

# Multiple values
config = (ConfigMap("app-config")
    .add("debug", "true")
    .add("port", "8080")
    .add("log_level", "info")
    .add("database_url", "postgres://localhost:5432/myapp"))
```

### add_json(key: str, data: Dict[str, Any]) -> ConfigMap
Add JSON data to the ConfigMap.

```python
# Add JSON configuration
config = ConfigMap("app-config").add_json("features", {
    "new_ui": True,
    "beta": False,
    "max_users": 1000
})

# Add complex JSON
config = ConfigMap("api-config").add_json("endpoints", {
    "users": {
        "url": "/api/users",
        "methods": ["GET", "POST", "PUT", "DELETE"]
    },
    "products": {
        "url": "/api/products",
        "methods": ["GET", "POST"]
    }
})
```

### add_yaml(key: str, data: Union[Dict[str, Any], str]) -> ConfigMap
Add YAML data to the ConfigMap.

```python
# Add YAML from dictionary
config = ConfigMap("app-config").add_yaml("settings", {
    "server": {
        "port": 8080,
        "host": "0.0.0.0"
    },
    "database": {
        "host": "localhost",
        "port": 5432
    }
})

# Add YAML string
yaml_content = """
server:
  port: 8080
  host: 0.0.0.0
database:
  host: localhost
  port: 5432
"""
config = ConfigMap("app-config").add_yaml("config.yaml", yaml_content)
```

### add_properties(key: str, properties: Dict[str, str]) -> ConfigMap
Add properties file format data.

```python
# Add properties configuration
config = ConfigMap("app-config").add_properties("application.properties", {
    "server.port": "8080",
    "spring.datasource.url": "jdbc:postgresql://localhost:5432/myapp",
    "logging.level.root": "INFO",
    "app.feature.new_ui": "true"
})
```

### add_ini(key: str, sections: Dict[str, Dict[str, str]]) -> ConfigMap
Add INI file format data.

```python
# Add INI configuration
config = ConfigMap("app-config").add_ini("config.ini", {
    "database": {
        "host": "localhost",
        "port": "5432",
        "name": "myapp"
    },
    "server": {
        "port": "8080",
        "host": "0.0.0.0"
    },
    "logging": {
        "level": "INFO",
        "format": "json"
    }
})
```

### add_toml(key: str, data: Dict[str, Any]) -> ConfigMap
Add TOML file format data.

```python
# Add TOML configuration
config = ConfigMap("app-config").add_toml("config.toml", {
    "server": {
        "port": 8080,
        "host": "0.0.0.0"
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "myapp"
    },
    "features": {
        "new_ui": True,
        "beta": False
    }
})
```

### from_file(key: str, file_path: str) -> ConfigMap
Add data from a file.

```python
# Add configuration from file
config = ConfigMap("app-config").from_file("nginx.conf", "configs/nginx.conf")

# Add JSON from file
config = ConfigMap("app-config").from_file("config.json", "configs/app.json")

# Add YAML from file
config = ConfigMap("app-config").from_file("config.yaml", "configs/app.yaml")
```

### from_directory(directory_path: str, pattern: str = "*", recursive: bool = False) -> ConfigMap
Add all files from a directory.

```python
# Add all files from directory
config = ConfigMap("app-config").from_directory("configs/")

# Add specific pattern files
config = ConfigMap("app-config").from_directory("configs/", "*.yaml")

# Add recursively
config = ConfigMap("app-config").from_directory("configs/", "*.conf", recursive=True)
```

### from_env_file(file_path: str, prefix: str = "") -> ConfigMap
Load configuration from an environment file.

```python
# Load from .env file
config = ConfigMap("app-config").from_env_file(".env")

# Load with prefix
config = ConfigMap("app-config").from_env_file(".env", prefix="APP_")

# Example .env file:
# DEBUG=true
# PORT=8080
# LOG_LEVEL=info
# DATABASE_URL=postgres://localhost:5432/myapp
```

### from_template(template_path: str, variables: Dict[str, Any], output_key: str = None) -> ConfigMap
Generate configuration from a template.

```python
# Generate from template
variables = {
    "app_name": "myapp",
    "environment": "production",
    "database_host": "postgres-service",
    "redis_host": "redis-service"
}
config = ConfigMap("app-config").from_template("templates/app.conf.j2", variables)

# With custom output key
config = ConfigMap("app-config").from_template("templates/nginx.conf.j2", variables, "nginx.conf")
```

### mount_path(path: str) -> ConfigMap
Set the mount path for the ConfigMap volume.

```python
# Mount at /etc/config
config = ConfigMap("app-config").mount_path("/etc/config")

# Mount at /var/config
config = ConfigMap("app-config").mount_path("/var/config")
```

### mount_as_env_vars(prefix: str = "") -> ConfigMap
Configure ConfigMap to be mounted as environment variables.

```python
# Mount as environment variables
config = ConfigMap("app-config").mount_as_env_vars()

# Mount with prefix
config = ConfigMap("app-config").mount_as_env_vars(prefix="APP_")

# Example: ConfigMap with keys "debug" and "port"
# Will create environment variables: APP_DEBUG and APP_PORT
```

### file_permissions(mode: int) -> ConfigMap
Set file permissions for mounted files.

```python
# Set read-only permissions
config = ConfigMap("app-config").file_permissions(0o644)

# Set executable permissions
config = ConfigMap("app-config").file_permissions(0o755)
```

### hot_reload(enabled: bool = True, restart_policy: str = "rolling", interval: str = "30s") -> ConfigMap
Enable hot reload for configuration changes.

```python
# Enable hot reload
config = ConfigMap("app-config").hot_reload(True)

# Configure hot reload
config = ConfigMap("app-config").hot_reload(
    enabled=True,
    restart_policy="rolling",
    interval="60s"
)
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete ConfigMap Example - Production Application Configuration
"""

import os
from celestra import ConfigMap, KubernetesOutput

def load_config(config_path: str) -> str:
    """Load configuration from external file."""
    with open(f"configs/{config_path}", "r") as f:
        return f.read()

def create_production_config():
    """Create production-ready configuration."""
    
    # Load external configurations
    nginx_config = load_config("application/nginx.conf")
    app_config = load_config("application/app.json")
    postgres_config = load_config("database/postgres.conf")
    
    # Application configuration
    app_config_map = (ConfigMap("app-config")
        .add("debug", "false")
        .add("port", "8080")
        .add("log_level", "info")
        .add_json("features", {
            "new_ui": True,
            "beta": False,
            "max_users": 10000
        })
        .add_yaml("settings", {
            "server": {
                "port": 8080,
                "host": "0.0.0.0"
            },
            "database": {
                "host": "postgres-service",
                "port": 5432
            }
        })
        .mount_as_env_vars(prefix="APP_"))
    
    # NGINX configuration
    nginx_config_map = (ConfigMap("nginx-config")
        .add_data("nginx.conf", nginx_config)
        .mount_path("/etc/nginx")
        .file_permissions(0o644))
    
    # Database configuration
    db_config_map = (ConfigMap("postgres-config")
        .add_data("postgresql.conf", postgres_config)
        .mount_path("/etc/postgresql")
        .file_permissions(0o644))
    
    # Environment-specific configuration
    env_config_map = (ConfigMap("env-config")
        .from_env_file(".env.production", prefix="PROD_")
        .mount_as_env_vars(prefix="ENV_"))
    
    # Template-based configuration
    template_vars = {
        "app_name": "myapp",
        "environment": "production",
        "database_host": "postgres-service",
        "redis_host": "redis-service"
    }
    template_config_map = (ConfigMap("template-config")
        .from_template("templates/app.conf.j2", template_vars, "app.conf")
        .mount_path("/etc/app")
        .hot_reload(True, "rolling", "30s"))
    
    return [app_config_map, nginx_config_map, db_config_map, env_config_map, template_config_map]

if __name__ == "__main__":
    configs = create_production_config()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    for config in configs:
        output.generate(config, "production-config/")
    
    print("✅ Production configuration generated!")
    print("🚀 Deploy: kubectl apply -f production-config/")
```

## Generated Kubernetes Resources

The ConfigMap class generates the following Kubernetes resources:

- **ConfigMap** - Kubernetes ConfigMap with the specified data
- **Volume** - Volume definition for mounting ConfigMaps
- **VolumeMount** - Volume mount configuration

## Usage Patterns

### Application Configuration

```python
# Basic app config
app_config = (ConfigMap("app-config")
    .add("debug", "false")
    .add("port", "8080")
    .add("log_level", "info")
    .mount_as_env_vars(prefix="APP_"))

# JSON configuration
json_config = (ConfigMap("api-config")
    .add_json("endpoints", {
        "users": "/api/users",
        "products": "/api/products"
    })
    .mount_as_env_vars(prefix="API_"))
```

### Web Server Configuration

```python
# NGINX configuration
nginx_config = (ConfigMap("nginx-config")
    .from_file("nginx.conf", "configs/nginx.conf")
    .mount_path("/etc/nginx")
    .file_permissions(0o644))

# Apache configuration
apache_config = (ConfigMap("apache-config")
    .from_file("httpd.conf", "configs/httpd.conf")
    .mount_path("/etc/apache2")
    .file_permissions(0o644))
```

### Database Configuration

```python
# PostgreSQL configuration
postgres_config = (ConfigMap("postgres-config")
    .from_file("postgresql.conf", "configs/postgresql.conf")
    .from_file("pg_hba.conf", "configs/pg_hba.conf")
    .mount_path("/etc/postgresql")
    .file_permissions(0o644))

# MySQL configuration
mysql_config = (ConfigMap("mysql-config")
    .from_file("my.cnf", "configs/my.cnf")
    .mount_path("/etc/mysql")
    .file_permissions(0o644))
```

### Environment Configuration

```python
# Development environment
dev_config = (ConfigMap("dev-config")
    .from_env_file(".env.development", prefix="DEV_")
    .mount_as_env_vars(prefix="DEV_"))

# Production environment
prod_config = (ConfigMap("prod-config")
    .from_env_file(".env.production", prefix="PROD_")
    .mount_as_env_vars(prefix="PROD_"))
```

### Template-Based Configuration

```python
# Template with variables
template_vars = {
    "app_name": "myapp",
    "environment": "production",
    "database_host": "postgres-service"
}
template_config = (ConfigMap("template-config")
    .from_template("templates/app.conf.j2", template_vars, "app.conf")
    .mount_path("/etc/app")
    .hot_reload(True))
```

### Directory-Based Configuration

```python
# All configuration files
all_config = (ConfigMap("all-config")
    .from_directory("configs/", "*.yaml")
    .mount_path("/etc/config"))

# Recursive configuration
recursive_config = (ConfigMap("recursive-config")
    .from_directory("configs/", "*.conf", recursive=True)
    .mount_path("/etc/config"))
```

## Best Practices

### 1. Use External Files

```python
# ✅ Good: Load from external files
config = ConfigMap("app-config").from_file("config.json", "configs/app.json")

# ❌ Bad: Hardcode in code
config = ConfigMap("app-config").add("config.json", '{"debug": true}')
```

### 2. Use Environment-Specific Configs

```python
# ✅ Good: Environment-specific
dev_config = ConfigMap("dev-config").from_env_file(".env.development")
prod_config = ConfigMap("prod-config").from_env_file(".env.production")

# ❌ Bad: Same config for all environments
config = ConfigMap("app-config").add("debug", "true")
```

### 3. Use Templates for Dynamic Configs

```python
# ✅ Good: Use templates
template_vars = {"app_name": "myapp", "environment": "production"}
config = ConfigMap("app-config").from_template("templates/app.conf.j2", template_vars)

# ❌ Bad: Hardcode dynamic values
config = ConfigMap("app-config").add("app_name", "myapp")
```

### 4. Use Hot Reload for Development

```python
# ✅ Good: Enable hot reload for development
dev_config = ConfigMap("dev-config").hot_reload(True)

# ❌ Bad: Always restart for config changes
config = ConfigMap("app-config")  # No hot reload
```

### 5. Use Proper File Permissions

```python
# ✅ Good: Set appropriate permissions
config = ConfigMap("app-config").file_permissions(0o644)

# ❌ Bad: Use default permissions
config = ConfigMap("app-config")  # Default permissions
``` 