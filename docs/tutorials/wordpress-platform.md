# WordPress Platform Tutorial

**⭐ Difficulty:** Easy | **⏱️ Time:** 15 minutes

Deploy a complete WordPress platform with MySQL database, persistent storage, and proper security using K8s-Gen DSL.

## What You'll Build

A production-ready WordPress platform featuring:
- **WordPress Application** - Latest WordPress with PHP-FPM
- **MySQL Database** - Persistent MySQL database
- **Persistent Storage** - WordPress files and database data
- **Load Balancer** - External access with SSL termination
- **Security** - Secrets management and RBAC
- **Backup** - Database backup strategy

## Prerequisites

- K8s-Gen DSL installed
- Kubernetes cluster with persistent volume support
- Basic understanding of WordPress and MySQL

## Architecture Overview

```
Internet → LoadBalancer → WordPress → MySQL Database
                           ↓           ↓
                    WordPress Files  Database Data
                    (Persistent)     (Persistent)
```

## Step 1: Create Database Secrets

Start with secure credential management:

```python
from k8s_gen import Secret

# Database credentials
db_secret = (Secret("wordpress-db-secret")
    .add_data("mysql-root-password", "super-secure-root-password")
    .add_data("mysql-database", "wordpress")
    .add_data("mysql-user", "wordpress")
    .add_data("mysql-password", "wordpress-secure-password"))

# WordPress secrets
wp_secret = (Secret("wordpress-secret")
    .add_data("wordpress-db-host", "mysql")
    .add_data("wordpress-db-name", "wordpress")
    .add_data("wordpress-db-user", "wordpress")
    .add_data("wordpress-db-password", "wordpress-secure-password")
    .add_data("wordpress-auth-key", "your-unique-auth-key-here")
    .add_data("wordpress-secure-auth-key", "your-unique-secure-auth-key")
    .add_data("wordpress-logged-in-key", "your-unique-logged-in-key")
    .add_data("wordpress-nonce-key", "your-unique-nonce-key"))

print("✅ Secrets created")
```

## Step 2: Create MySQL Database

Set up the MySQL database with persistent storage:

```python
from k8s_gen import StatefulApp

# MySQL database
mysql_db = (StatefulApp("mysql")
    .image("mysql:8.0")
    .port(3306, "mysql")
    .env_from_secret("MYSQL_ROOT_PASSWORD", "wordpress-db-secret", "mysql-root-password")
    .env_from_secret("MYSQL_DATABASE", "wordpress-db-secret", "mysql-database")
    .env_from_secret("MYSQL_USER", "wordpress-db-secret", "mysql-user")
    .env_from_secret("MYSQL_PASSWORD", "wordpress-db-secret", "mysql-password")
    .storage("/var/lib/mysql", "20Gi")
    .resources(cpu="500m", memory="1Gi")
    .health_check_command(["mysqladmin", "ping", "-h", "localhost"]))

print("✅ MySQL database configured")
```

## Step 3: Create WordPress Application

Set up WordPress with persistent storage for uploads:

```python
from k8s_gen import App

# WordPress application
wordpress = (App("wordpress")
    .image("wordpress:6.1-php8.1-fpm")
    .port(80, "http")
    .env_from_secret("WORDPRESS_DB_HOST", "wordpress-secret", "wordpress-db-host")
    .env_from_secret("WORDPRESS_DB_NAME", "wordpress-secret", "wordpress-db-name")
    .env_from_secret("WORDPRESS_DB_USER", "wordpress-secret", "wordpress-db-user")
    .env_from_secret("WORDPRESS_DB_PASSWORD", "wordpress-secret", "wordpress-db-password")
    .env_from_secret("WORDPRESS_AUTH_KEY", "wordpress-secret", "wordpress-auth-key")
    .env_from_secret("WORDPRESS_SECURE_AUTH_KEY", "wordpress-secret", "wordpress-secure-auth-key")
    .env_from_secret("WORDPRESS_LOGGED_IN_KEY", "wordpress-secret", "wordpress-logged-in-key")
    .env_from_secret("WORDPRESS_NONCE_KEY", "wordpress-secret", "wordpress-nonce-key")
    .env("WORDPRESS_TABLE_PREFIX", "wp_")
    .env("WORDPRESS_DEBUG", "0")
    .storage("/var/www/html", "10Gi")
    .resources(cpu="300m", memory="512Mi")
    .replicas(2)
    .health_check("/wp-admin/install.php", 80))

print("✅ WordPress application configured")
```

## Step 4: Add NGINX Web Server

Add NGINX as a reverse proxy for better performance:

```python
from k8s_gen import ConfigMap

# NGINX configuration
nginx_config = (ConfigMap("nginx-config")
    .add_data("default.conf", """
upstream wordpress {
    server wordpress:80;
}

server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://wordpress;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location ~ /\.ht {
        deny all;
    }
}
    """))

# NGINX web server
nginx = (App("nginx")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .mount_config_map("nginx-config", "/etc/nginx/conf.d")
    .resources(cpu="100m", memory="128Mi")
    .replicas(2)
    .health_check("/", 80))

print("✅ NGINX web server configured")
```

## Step 5: Set Up Services

Create services for database and web access:

```python
from k8s_gen import Service

# MySQL service (internal only)
mysql_service = (Service("mysql")
    .selector({"app": "mysql"})
    .add_port("mysql", 3306, 3306)
    .type("ClusterIP"))

# WordPress service (internal only)
wordpress_service = (Service("wordpress")
    .selector({"app": "wordpress"})
    .add_port("http", 80, 80)
    .type("ClusterIP"))

# NGINX service (external access)
nginx_service = (Service("nginx")
    .selector({"app": "nginx"})
    .add_port("http", 80, 80)
    .type("LoadBalancer"))

print("✅ Services configured")
```

## Step 6: Add Ingress for SSL

Configure ingress with SSL termination:

```python
from k8s_gen import Ingress

# Ingress for external access with SSL
wordpress_ingress = (Ingress("wordpress-ingress")
    .host("wordpress.example.com")
    .route("/", "nginx", 80)
    .tls("wordpress-tls")
    .add_annotation("nginx.ingress.kubernetes.io/proxy-body-size", "100m")
    .add_annotation("cert-manager.io/cluster-issuer", "letsencrypt-prod"))

print("✅ Ingress configured")
```

## Step 7: Add Security and RBAC

Implement proper security:

```python
from k8s_gen import ServiceAccount, Role, RoleBinding, SecurityPolicy

# Service accounts
wordpress_sa = (ServiceAccount("wordpress-sa")
    .add_label("app", "wordpress"))

mysql_sa = (ServiceAccount("mysql-sa")
    .add_label("app", "mysql")
    .automount_token(False))

# Roles
wordpress_role = (Role("wordpress-role")
    .allow_get("configmaps", "secrets")
    .allow_list("services"))

mysql_role = (Role("mysql-role")
    .allow_get("persistentvolumeclaims")
    .allow_create("events"))

# Role bindings
wordpress_binding = RoleBinding("wordpress-binding", wordpress_role, wordpress_sa)
mysql_binding = RoleBinding("mysql-binding", mysql_role, mysql_sa)

# Apply service accounts to applications
wordpress.service_account(wordpress_sa)
mysql_db.service_account(mysql_sa)

# Security policy
security_policy = (SecurityPolicy("wordpress-security")
    .enable_rbac()
    .pod_security_standards("baseline")
    .network_policies(enabled=True))

print("✅ Security configured")
```

## Step 8: Add Backup Strategy

Implement database backup:

```python
from k8s_gen import CronJob

# Database backup job
db_backup = (CronJob("mysql-backup")
    .schedule("0 2 * * *")  # Daily at 2 AM
    .image("mysql:8.0")
    .command([
        "sh", "-c",
        "mysqldump -h mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE > /backup/wordpress-$(date +%Y%m%d-%H%M%S).sql"
    ])
    .env_from_secret("MYSQL_USER", "wordpress-db-secret", "mysql-user")
    .env_from_secret("MYSQL_PASSWORD", "wordpress-db-secret", "mysql-password")
    .env_from_secret("MYSQL_DATABASE", "wordpress-db-secret", "mysql-database")
    .storage("/backup", "50Gi")
    .resources(cpu="100m", memory="256Mi")
    .restart_policy("OnFailure"))

print("✅ Backup strategy configured")
```

## Step 9: Complete WordPress Platform

Here's the complete platform code:

```python
#!/usr/bin/env python3
"""
WordPress Platform - Complete WordPress deployment with MySQL and NGINX
"""

from k8s_gen import (
    App, StatefulApp, Secret, ConfigMap, Service, Ingress, CronJob,
    ServiceAccount, Role, RoleBinding, SecurityPolicy,
    KubernetesOutput
)

def create_wordpress_platform():
    """Create a complete WordPress platform."""
    
    # 1. Secrets
    db_secret = (Secret("wordpress-db-secret")
        .add_data("mysql-root-password", "super-secure-root-password")
        .add_data("mysql-database", "wordpress")
        .add_data("mysql-user", "wordpress")
        .add_data("mysql-password", "wordpress-secure-password"))
    
    wp_secret = (Secret("wordpress-secret")
        .add_data("wordpress-db-host", "mysql")
        .add_data("wordpress-db-name", "wordpress")
        .add_data("wordpress-db-user", "wordpress")
        .add_data("wordpress-db-password", "wordpress-secure-password")
        .add_data("wordpress-auth-key", "your-unique-auth-key-here")
        .add_data("wordpress-secure-auth-key", "your-unique-secure-auth-key")
        .add_data("wordpress-logged-in-key", "your-unique-logged-in-key")
        .add_data("wordpress-nonce-key", "your-unique-nonce-key"))
    
    # 2. Database
    mysql_db = (StatefulApp("mysql")
        .image("mysql:8.0")
        .port(3306, "mysql")
        .env_from_secret("MYSQL_ROOT_PASSWORD", "wordpress-db-secret", "mysql-root-password")
        .env_from_secret("MYSQL_DATABASE", "wordpress-db-secret", "mysql-database")
        .env_from_secret("MYSQL_USER", "wordpress-db-secret", "mysql-user")
        .env_from_secret("MYSQL_PASSWORD", "wordpress-db-secret", "mysql-password")
        .storage("/var/lib/mysql", "20Gi")
        .resources(cpu="500m", memory="1Gi")
        .health_check_command(["mysqladmin", "ping", "-h", "localhost"]))
    
    # 3. WordPress
    wordpress = (App("wordpress")
        .image("wordpress:6.1-php8.1-fpm")
        .port(80, "http")
        .env_from_secret("WORDPRESS_DB_HOST", "wordpress-secret", "wordpress-db-host")
        .env_from_secret("WORDPRESS_DB_NAME", "wordpress-secret", "wordpress-db-name")
        .env_from_secret("WORDPRESS_DB_USER", "wordpress-secret", "wordpress-db-user")
        .env_from_secret("WORDPRESS_DB_PASSWORD", "wordpress-secret", "wordpress-db-password")
        .env("WORDPRESS_TABLE_PREFIX", "wp_")
        .storage("/var/www/html", "10Gi")
        .resources(cpu="300m", memory="512Mi")
        .replicas(2)
        .health_check("/wp-admin/install.php", 80))
    
    # 4. NGINX
    nginx_config = (ConfigMap("nginx-config")
        .add_data("default.conf", """
upstream wordpress {
    server wordpress:80;
}
server {
    listen 80;
    server_name _;
    client_max_body_size 100M;
    location / {
        proxy_pass http://wordpress;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
        """))
    
    nginx = (App("nginx")
        .image("nginx:1.21-alpine")
        .port(80, "http")
        .mount_config_map("nginx-config", "/etc/nginx/conf.d")
        .resources(cpu="100m", memory="128Mi")
        .replicas(2)
        .health_check("/", 80))
    
    # 5. Services
    mysql_service = (Service("mysql")
        .selector({"app": "mysql"})
        .add_port("mysql", 3306, 3306))
    
    wordpress_service = (Service("wordpress")
        .selector({"app": "wordpress"})
        .add_port("http", 80, 80))
    
    nginx_service = (Service("nginx")
        .selector({"app": "nginx"})
        .add_port("http", 80, 80)
        .type("LoadBalancer"))
    
    # 6. Ingress
    wordpress_ingress = (Ingress("wordpress-ingress")
        .host("wordpress.example.com")
        .route("/", "nginx", 80)
        .tls("wordpress-tls"))
    
    # 7. Backup
    db_backup = (CronJob("mysql-backup")
        .schedule("0 2 * * *")
        .image("mysql:8.0")
        .command(["sh", "-c", "mysqldump -h mysql -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE > /backup/wordpress-$(date +%Y%m%d-%H%M%S).sql"])
        .env_from_secret("MYSQL_USER", "wordpress-db-secret", "mysql-user")
        .env_from_secret("MYSQL_PASSWORD", "wordpress-db-secret", "mysql-password")
        .env_from_secret("MYSQL_DATABASE", "wordpress-db-secret", "mysql-database")
        .storage("/backup", "50Gi")
        .resources(cpu="100m", memory="256Mi"))
    
    # 8. Security
    wordpress_sa = ServiceAccount("wordpress-sa")
    mysql_sa = ServiceAccount("mysql-sa")
    
    wordpress_role = (Role("wordpress-role")
        .allow_get("configmaps", "secrets")
        .allow_list("services"))
    
    mysql_role = (Role("mysql-role")
        .allow_get("persistentvolumeclaims")
        .allow_create("events"))
    
    wordpress_binding = RoleBinding("wordpress-binding", wordpress_role, wordpress_sa)
    mysql_binding = RoleBinding("mysql-binding", mysql_role, mysql_sa)
    
    wordpress.service_account(wordpress_sa)
    mysql_db.service_account(mysql_sa)
    
    return [
        # Secrets
        db_secret, wp_secret,
        # Applications
        mysql_db, wordpress, nginx,
        # Configuration
        nginx_config,
        # Services
        mysql_service, wordpress_service, nginx_service,
        # Ingress
        wordpress_ingress,
        # Backup
        db_backup,
        # Security
        wordpress_sa, mysql_sa, wordpress_role, mysql_role,
        wordpress_binding, mysql_binding
    ]

def main():
    """Generate the WordPress platform."""
    print("📝 Creating WordPress Platform")
    print("=" * 35)
    
    # Create all components
    components = create_wordpress_platform()
    
    # Generate manifests
    output = KubernetesOutput()
    all_resources = []
    
    for component in components:
        resources = component.generate_kubernetes_resources()
        all_resources.extend(resources)
    
    # Save to file
    output.write_all_resources(all_resources, "wordpress-platform.yaml")
    
    print(f"✅ Generated {len(all_resources)} Kubernetes resources")
    print("📄 Saved to: wordpress-platform.yaml")
    print("\n📝 WordPress platform components:")
    print("   • MySQL database with persistent storage")
    print("   • WordPress application with PHP-FPM")
    print("   • NGINX reverse proxy")
    print("   • Secrets management")
    print("   • Daily database backups")
    print("   • RBAC security")
    print("   • SSL-ready ingress")
    print("\n🚀 Deploy with:")
    print("   kubectl apply -f wordpress-platform.yaml")
    print("\n🌐 Access WordPress:")
    print("   kubectl get service nginx -w")
    print("   Visit: http://<EXTERNAL-IP>")

if __name__ == "__main__":
    main()
```

## Deployment and Setup

1. **Deploy the platform:**
   ```bash
   python wordpress_platform.py
   kubectl apply -f wordpress-platform.yaml
   ```

2. **Wait for pods to be ready:**
   ```bash
   kubectl get pods -w
   ```

3. **Get external IP:**
   ```bash
   kubectl get service nginx
   ```

4. **Complete WordPress setup:**
   - Visit `http://<EXTERNAL-IP>`
   - Follow WordPress installation wizard
   - Create admin account
   - Configure site settings

## Testing the Platform

```bash
# Check all components
kubectl get pods
kubectl get services
kubectl get pvc
kubectl get secrets

# Check logs
kubectl logs -l app=wordpress
kubectl logs -l app=mysql
kubectl logs -l app=nginx

# Test database connection
kubectl exec -it $(kubectl get pod -l app=mysql -o jsonpath="{.items[0].metadata.name}") -- mysql -u wordpress -p

# Test backup job
kubectl create job --from=cronjob/mysql-backup manual-backup
kubectl logs job/manual-backup
```

## Key Features Implemented

✅ **Persistent Storage**: WordPress files and MySQL data  
✅ **Secrets Management**: Secure credential storage  
✅ **High Availability**: Multiple WordPress replicas  
✅ **Performance**: NGINX reverse proxy  
✅ **Security**: RBAC and security policies  
✅ **Backup Strategy**: Automated daily backups  
✅ **SSL Ready**: Ingress with TLS support  
✅ **Health Checks**: Application and database monitoring  

## Customization Options

### Performance Optimization
```python
# Add Redis caching
redis_cache = (App("redis")
    .image("redis:7-alpine")
    .port(6379, "redis")
    .resources(cpu="100m", memory="256Mi"))

# Update WordPress for Redis
wordpress.env("WORDPRESS_CACHE_ENABLED", "1")
wordpress.env("WORDPRESS_CACHE_HOST", "redis")
```

### SSL Certificate
```python
# Add cert-manager for automatic SSL
wordpress_ingress.add_annotation("cert-manager.io/cluster-issuer", "letsencrypt-prod")
```

### Monitoring
```python
# Add monitoring
wordpress.add_annotation("prometheus.io/scrape", "true")
wordpress.add_annotation("prometheus.io/port", "9090")
```

## Next Steps

Enhance your WordPress platform:

1. **[RBAC Security](rbac-security.md)** - Advanced security
2. **[Observability Stack](observability-stack.md)** - Add monitoring
3. **[Multi-Environment](multi-environment.md)** - Multiple environments
4. **Performance Optimization** - Caching and CDN

---

**Congratulations!** You've deployed a production-ready WordPress platform with MySQL, persistent storage, security, and backup capabilities using K8s-Gen DSL.
