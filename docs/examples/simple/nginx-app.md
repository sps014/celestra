# NGINX Web Server

This example demonstrates how to deploy a simple NGINX web server using Celestra DSL.

## Overview

This example shows how to:
- Deploy a basic NGINX web server
- Configure service discovery
- Set up health checks
- Manage configuration

## Prerequisites

- Kubernetes cluster
- Celestra DSL installed
- kubectl configured

## Implementation

### 1. Basic NGINX Deployment

```python
from celestra import App, ConfigMap

# Create NGINX application
nginx = (App("nginx-web")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .resources(cpu="100m", memory="128Mi")
    .expose())

# Add custom configuration
config = (ConfigMap("nginx-config")
    .add("nginx.conf", """
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html index.htm;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
    }
}""")
    .mount_as_file("/etc/nginx/nginx.conf"))

# Add configuration to app
nginx.add_config(config)

# Generate manifests
nginx.generate().to_yaml("./k8s/")
```

### 2. Production NGINX with Custom HTML

```python
from celestra import App, ConfigMap, Secret

# Create production NGINX app
nginx_prod = (App("nginx-prod")
    .image("nginx:1.25")
    .port(80)
    .replicas(5)
    .resources(cpu="200m", memory="256Mi")
    .expose()
    .namespace("production"))

# Custom HTML content
html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Welcome to NGINX</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to NGINX!</h1>
        <p>This is a custom NGINX deployment using Celestra DSL.</p>
        <p>Server: {{ server_name }}</p>
        <p>Environment: {{ environment }}</p>
    </div>
</body>
</html>
"""

# HTML configuration
html_config = (ConfigMap("nginx-html")
    .add("index.html", html_content)
    .mount_as_file("/usr/share/nginx/html/index.html"))

# NGINX configuration
nginx_config = (ConfigMap("nginx-config")
    .add("nginx.conf", """
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files $uri $uri/ =404;
        }
        
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        location /status {
            stub_status on;
            access_log off;
        }
    }
}""")
    .mount_as_file("/etc/nginx/nginx.conf"))

# Add configurations
nginx_prod.add_config(html_config)
nginx_prod.add_config(nginx_config)

# Generate manifests
nginx_prod.generate().to_yaml("./k8s/")
```

### 3. NGINX with Ingress

```python
from celestra import App, Ingress

# Create NGINX app
nginx = (App("nginx-web")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .expose())

# Create ingress
ingress = (Ingress("nginx-ingress")
    .add_rule("example.com", "/", "nginx-web", 80)
    .add_rule("api.example.com", "/api", "nginx-web", 80)
    .tls_enabled(True)
    .add_tls_secret("nginx-tls"))

# Generate manifests
nginx.generate().to_yaml("./k8s/")
ingress.generate().to_yaml("./k8s/")
```

### 4. NGINX with Health Checks

```python
from celestra import App, Health

# Create NGINX app with health checks
nginx = (App("nginx-healthy")
    .image("nginx:latest")
    .port(80)
    .replicas(3)
    .expose())

# Add health checks
health = (Health("nginx-health")
    .liveness_probe("/health", 80)
    .readiness_probe("/health", 80)
    .startup_probe("/health", 80))

# Add health checks to app
nginx.add_health(health)

# Generate manifests
nginx.generate().to_yaml("./k8s/")
```

## Deployment

### 1. Apply the manifests

```bash
# Apply the generated manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods
```

### 2. Verify the deployment

```bash
# Check if pods are running
kubectl get pods -l app=nginx-web

# Check service
kubectl get service nginx-web

# Test the application
kubectl port-forward service/nginx-web 8080:80
curl http://localhost:8080
```

### 3. Scale the deployment

```bash
# Scale up
kubectl scale deployment nginx-web --replicas=5

# Scale down
kubectl scale deployment nginx-web --replicas=2
```

## Configuration Options

### Environment Variables

```python
# Add environment variables
nginx = (App("nginx-web")
    .image("nginx:latest")
    .port(80)
    .environment({
        "NGINX_HOST": "example.com",
        "NGINX_PORT": "80",
        "NGINX_WORKER_PROCESSES": "auto"
    }))
```

### Resource Limits

```python
# Set resource limits
nginx = (App("nginx-web")
    .image("nginx:latest")
    .port(80)
    .resources(
        cpu="200m",
        memory="256Mi",
        cpu_limit="500m",
        memory_limit="512Mi"
    ))
```

### Custom Labels and Annotations

```python
# Add custom labels and annotations
nginx = (App("nginx-web")
    .image("nginx:latest")
    .port(80)
    .add_labels({
        "app": "nginx",
        "tier": "web",
        "environment": "production"
    })
    .add_annotations({
        "description": "NGINX web server",
        "owner": "platform-team"
    }))
```

## Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Service not accessible**
   ```bash
   kubectl get endpoints nginx-web
   kubectl describe service nginx-web
   ```

3. **Health checks failing**
   ```bash
   kubectl describe pod <pod-name>
   # Check if /health endpoint is accessible
   ```

### Debug Commands

```bash
# Check pod status
kubectl get pods -o wide

# Check service endpoints
kubectl get endpoints

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp

# Check logs
kubectl logs -l app=nginx-web
```

## Best Practices

### 1. **Use Specific Image Tags**
```python
# ✅ Good: Use specific version
nginx = App("nginx-web").image("nginx:1.25.3")

# ❌ Bad: Use latest tag
nginx = App("nginx-web").image("nginx:latest")
```

### 2. **Set Resource Limits**
```python
# ✅ Good: Set resource limits
nginx = App("nginx-web").resources(cpu="200m", memory="256Mi")

# ❌ Bad: No resource limits
nginx = App("nginx-web")  # No resource limits
```

### 3. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
nginx = App("nginx-web").add_health(Health("health").liveness_probe("/health"))

# ❌ Bad: No health checks
nginx = App("nginx-web")  # No health checks
```

### 4. **Use ConfigMaps for Configuration**
```python
# ✅ Good: Use ConfigMap for configuration
config = ConfigMap("nginx-config").add("nginx.conf", nginx_config)
nginx.add_config(config)

# ❌ Bad: Hardcode configuration
nginx = App("nginx-web")  # No configuration management
```

## Next Steps

1. **[Node.js Application](nodejs-app.md)** - Build a Node.js app with database
2. **[Production Deployments](../production/index.md)** - Learn about production configurations
3. **[App Component](../../components/core/app.md)** - Complete App documentation

Ready to build something more complex? Check out the [Node.js Application](nodejs-app.md) example or jump to [Production Deployments](../production/index.md)! 