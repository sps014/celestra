# Basic Web App Tutorial

**⭐ Difficulty:** Easy | **⏱️ Time:** 10 minutes

Learn the fundamentals of Celestra by building a simple web application with load balancing and health checks.

## What You'll Build

A scalable NGINX web server with:
- Multiple replicas for high availability
- Health checks for reliability
- Load balancer service for external access
- Resource limits for stability

## Prerequisites

- Celestra installed
- Basic understanding of Kubernetes concepts
- kubectl configured (optional, for deployment)

## Architecture Overview

```
Internet → LoadBalancer Service → NGINX Pods (3 replicas)
```

## Step 1: Create the Web Application

Start with a simple NGINX web server:

```python
from celestra import App

# Create the web application
web_app = (App("simple-web-app")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .replicas(3)
    .resources(cpu="100m", memory="128Mi")
    .health_check("/", 80))

print("✅ Web application created")
```

**Key features:**
- `nginx:1.21-alpine` - Lightweight, production-ready image
- Port 80 for HTTP traffic
- 3 replicas for high availability
- Resource limits to prevent resource hogging
- Health check on root path

## Step 2: Add a Service for Load Balancing

Expose the application with a load balancer:

```python
from celestra import Service

# Create service for external access
web_service = (Service("web-app-service")
    .selector({"app": "simple-web-app"})
    .add_port("http", 80, 80)
    .type("LoadBalancer"))

print("✅ Service created")
```

**Service details:**
- Selector matches the app labels
- External port 80 maps to container port 80
- LoadBalancer type provides external IP

## Step 3: Generate and Deploy

Create the complete deployment:

```python
#!/usr/bin/env python3
"""
Basic Web App - Simple NGINX deployment with load balancing
"""

from celestra import App, Service, KubernetesOutput

def create_web_app():
    """Create a simple web application with load balancing."""
    
    # Create the web application
    web_app = (App("simple-web-app")
        .image("nginx:1.21-alpine")
        .port(80, "http")
        .replicas(3)
        .resources(cpu="100m", memory="128Mi")
        .health_check("/", 80))
    
    # Create service for external access
    web_service = (Service("web-app-service")
        .selector({"app": "simple-web-app"})
        .add_port("http", 80, 80)
        .type("LoadBalancer"))
    
    return [web_app, web_service]

def main():
    """Generate the web application deployment."""
    print("🌐 Creating Basic Web Application")
    print("=" * 40)
    
    # Create components
    components = create_web_app()
    
    # Generate Kubernetes manifests
    output = KubernetesOutput()
    all_resources = []
    
    for component in components:
        resources = component.generate_kubernetes_resources()
        all_resources.extend(resources)
    
    # Save to file
    output.write_all_resources(all_resources, "basic-web-app.yaml")
    
    print(f"✅ Generated {len(all_resources)} Kubernetes resources")
    print("📄 Saved to: basic-web-app.yaml")
    print("\n🚀 Deploy with:")
    print("   kubectl apply -f basic-web-app.yaml")
    print("   kubectl get pods")
    print("   kubectl get service web-app-service")

if __name__ == "__main__":
    main()
```

## Step 4: Deploy to Kubernetes

1. **Save the code** as `basic_web_app.py`

2. **Generate manifests:**
   ```bash
   python basic_web_app.py
   ```

3. **Deploy to cluster:**
   ```bash
   kubectl apply -f basic-web-app.yaml
   ```

4. **Check deployment:**
   ```bash
   kubectl get pods
   kubectl get services
   ```

## Step 5: Test the Application

Verify everything is working:

```bash
# Check pod status
kubectl get pods -l app=simple-web-app

# Check service
kubectl get service web-app-service

# Get external IP (may take a few minutes)
kubectl get service web-app-service -w

# Test locally with port forwarding
kubectl port-forward service/web-app-service 8080:80
```

Visit `http://localhost:8080` to see the NGINX welcome page.

## Understanding the Generated Resources

Your deployment creates these Kubernetes resources:

### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: simple-web-app
  template:
    metadata:
      labels:
        app: simple-web-app
    spec:
      containers:
      - name: simple-web-app
        image: nginx:1.21-alpine
        ports:
        - containerPort: 80
          name: http
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
```

### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app-service
spec:
  type: LoadBalancer
  selector:
    app: simple-web-app
  ports:
  - name: http
    port: 80
    targetPort: 80
```

## Enhancements

### Add Custom HTML Content
Mount custom content using ConfigMap:

```python
from celestra import ConfigMap

# Create custom content
html_config = (ConfigMap("web-content")
    .add_data("index.html", """
    <!DOCTYPE html>
    <html>
    <head><title>My App</title></head>
    <body>
        <h1>Welcome to My Web App!</h1>
        <p>Built with Celestra</p>
    </body>
    </html>
    """))

# Mount in the app
web_app = (App("simple-web-app")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .mount_config_map(html_config, "/usr/share/nginx/html")
    .replicas(3)
    .resources(cpu="100m", memory="128Mi"))
```

### Add SSL/TLS
Configure HTTPS with certificates:

```python
# Add HTTPS port
web_app = (App("simple-web-app")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .port(443, "https")
    .replicas(3))

# Update service for HTTPS
web_service = (Service("web-app-service")
    .selector({"app": "simple-web-app"})
    .add_port("http", 80, 80)
    .add_port("https", 443, 443)
    .type("LoadBalancer"))
```

### Add Ingress
Use Ingress for advanced routing:

```python
from celestra import Ingress

ingress = (Ingress("web-app-ingress")
    .host("myapp.example.com")
    .route("/", "web-app-service", 80)
    .tls("myapp-tls"))
```

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl describe pods -l app=simple-web-app

# Check logs
kubectl logs -l app=simple-web-app
```

### Service Not Accessible
```bash
# Check service endpoints
kubectl get endpoints web-app-service

# Check if LoadBalancer IP is assigned
kubectl get service web-app-service
```

### Resource Issues
```bash
# Check resource usage
kubectl top pods -l app=simple-web-app

# Check node resources
kubectl describe nodes
```

## Key Concepts Learned

✅ **App Component**: Creating stateless applications  
✅ **Service Discovery**: Exposing apps with services  
✅ **Load Balancing**: Distributing traffic across replicas  
✅ **Health Checks**: Ensuring application reliability  
✅ **Resource Management**: Setting CPU and memory limits  
✅ **Kubernetes Generation**: Converting DSL to YAML manifests  

## Next Steps

Ready for more advanced patterns?

1. **[WordPress Platform](wordpress-platform.md)** - Add a database
2. **[Multi-Environment Setup](multi-environment.md)** - Multiple environments
3. **[RBAC Security](rbac-security.md)** - Add security controls
4. **[Microservices](microservices.md)** - Build distributed systems

---

**Congratulations!** You've successfully built and deployed your first web application with Celestra. The application is now running with high availability and load balancing.
