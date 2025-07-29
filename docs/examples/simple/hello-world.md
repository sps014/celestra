# Hello World Example

This is the simplest possible Celestra application - a basic web server that displays "Hello, World!". Perfect for getting started with Celestra.

## 🎯 What You'll Build

A simple web application that:
- Runs a basic web server
- Displays a "Hello, World!" message
- Is accessible via HTTP
- Can be scaled horizontally
- Includes basic health checks

## 📋 Prerequisites

Before starting, ensure you have:

- Celestra installed (`pip install celestra`)
- A Kubernetes cluster (minikube, kind, or cloud)
- kubectl configured
- Basic understanding of Python

## 🚀 Step 1: Create the Application

Create a file called `hello_world.py`:

```python
from celestra import App

# Create a simple web application
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .replicas(2)
    .resources(cpu="100m", memory="128Mi")
    .health_check("/")
    .expose())

# Generate Kubernetes manifests
hello_app.generate().to_yaml("./hello-world/")

print("✅ Hello World manifests generated in ./hello-world/")
```

## 🎯 Step 2: Run the Application

```bash
# Run the application
python hello_world.py

# Deploy to Kubernetes
kubectl apply -f ./hello-world/
```

## 🔍 Step 3: Verify the Deployment

```bash
# Check if pods are running
kubectl get pods

# Check if service is created
kubectl get services

# Port forward to access the application
kubectl port-forward svc/hello-world 8080:80
```

Now open your browser and go to `http://localhost:8080` to see "Hello, World!"

## 📊 What Was Created

Celestra generated the following Kubernetes resources:

### 1. **Deployment**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-world
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hello-world
  template:
    metadata:
      labels:
        app: hello-world
    spec:
      containers:
      - name: hello-world
        image: nginxdemos/hello:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
```

### 2. **Service**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: hello-world
spec:
  selector:
    app: hello-world
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

## 🔧 Customization Options

### Add Environment Variables

```python
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .replicas(2)
    .env("MESSAGE", "Hello from Celestra!")
    .env("ENVIRONMENT", "development")
    .expose())
```

### Add Configuration

```python
from celestra import ConfigMap

# Configuration
config = ConfigMap("hello-config").add("message", "Hello from ConfigMap!")

# Add to application
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .add_config(config)
    .expose())
```

### Add Health Checks

```python
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .health_check("/")
    .liveness_probe("/")
    .readiness_probe("/")
    .expose())
```

### Scale the Application

```python
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .replicas(5)  # Scale to 5 replicas
    .expose())
```

## 🎯 Advanced Features

### Add Resource Limits

```python
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .resources(
        cpu="100m",           # CPU request
        memory="128Mi",        # Memory request
        cpu_limit="200m",      # CPU limit
        memory_limit="256Mi"   # Memory limit
    )
    .expose())
```

### Add Rolling Update Strategy

```python
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .rolling_update(
        max_surge=1,
        max_unavailable=0
    )
    .expose())
```

### Add Annotations and Labels

```python
hello_app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .add_label("environment", "development")
    .add_label("team", "platform")
    .add_annotation("description", "Simple hello world application")
    .expose())
```

## 🔍 Testing the Application

### Health Check

```bash
# Check if the application is healthy
kubectl get pods -l app=hello-world

# Check logs
kubectl logs -l app=hello-world
```

### Load Testing

```bash
# Install hey for load testing
go install github.com/rakyll/hey@latest

# Test the application
hey -n 1000 -c 10 http://localhost:8080
```

### Scale Testing

```bash
# Scale the application
kubectl scale deployment hello-world --replicas=5

# Check the scaling
kubectl get pods -l app=hello-world
```

## 🚀 Generate Different Outputs

Celestra supports multiple output formats:

```python
# Kubernetes YAML
hello_app.generate().to_yaml("./k8s/")

# Docker Compose (for local development)
hello_app.generate().to_docker_compose("./docker-compose.yml")

# Helm Chart
hello_app.generate().to_helm_chart("./charts/")

# Kustomize
hello_app.generate().to_kustomize("./kustomize/")
```

## 🔧 Troubleshooting

### Common Issues

**1. Pod Not Starting**
```bash
# Check pod status
kubectl describe pod -l app=hello-world

# Check events
kubectl get events --sort-by=.metadata.creationTimestamp
```

**2. Service Not Accessible**
```bash
# Check service
kubectl get service hello-world

# Check endpoints
kubectl get endpoints hello-world
```

**3. Image Pull Issues**
```bash
# Check image pull status
kubectl describe pod -l app=hello-world | grep -A 10 Events
```

### Debug Commands

```bash
# Get detailed pod information
kubectl describe pod -l app=hello-world

# Check pod logs
kubectl logs -l app=hello-world

# Execute into pod
kubectl exec -it $(kubectl get pod -l app=hello-world -o jsonpath='{.items[0].metadata.name}') -- /bin/sh

# Check service connectivity
kubectl run test --image=busybox --rm -it --restart=Never -- wget -O- http://hello-world
```

## 🚀 Next Steps

Ready to build more complex applications? Try these examples:

1. **[NGINX Web Server](nginx-app.md)** - Deploy a web server
2. **[Node.js Application](nodejs-app.md)** - Deploy a Node.js app
3. **[Database Deployment]** - *Coming soon - Database examples will be added here*
4. **[Production Platform]** - *Coming soon - Production platform examples will be added here*

## 📚 Related Documentation

- **[Getting Started](../../getting-started/quick-start.md)** - Installation and first steps
- **[App Component](../../components/core/app.md)** - Complete App documentation
- **[Core Concepts](../../getting-started/core-concepts.md)** - Understanding Celestra fundamentals
- **[Components Guide](../../components/index.md)** - All available components

Ready to build something more complex? Check out the [NGINX Web Server](nginx-app.md) example or jump to [Production Deployments](../production/index.md)! 