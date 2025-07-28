# Quick Start Guide

Get started with K8s-Gen DSL in just a few minutes! This guide will walk you through creating your first Kubernetes application.

## Installation

=== "pip install"

    ```bash
    # Install from source
    git clone https://github.com/your-username/k8s-gen.git
    cd k8s-gen
    pip install -r src/requirements.txt
    ```

=== "Development Setup"

    ```bash
    # Clone and setup for development
    git clone https://github.com/your-username/k8s-gen.git
    cd k8s-gen
    pip install -r src/requirements.txt
    
    # Run tests to verify installation
    python run_tests.py
    ```

## Your First Application

Let's create a simple web application:

### 1. Create a Basic Web App

```python
from src.k8s_gen import App, KubernetesOutput

# Create a simple NGINX web application
web_app = (App("my-web-app")
    .image("nginx:1.21")
    .port(80, "http")
    .replicas(3)
    .resources(cpu="100m", memory="128Mi")
    .expose())

print("✅ Web app created!")
```

### 2. Generate Kubernetes YAML

```python
# Generate Kubernetes resources
resources = web_app.generate_kubernetes_resources()

# Output to files
output = KubernetesOutput()
output.generate(web_app, "k8s-manifests/")

print(f"📄 Generated {len(resources)} Kubernetes resources")
```

### 3. Deploy to Kubernetes

```bash
# Apply the generated manifests
kubectl apply -f k8s-manifests/

# Check deployment status
kubectl get deployments,services,pods
```

## Complete Example

Here's a complete example file (`my_first_app.py`):

```python
#!/usr/bin/env python3
"""
My First K8s-Gen Application
"""

import os
from src.k8s_gen import App, KubernetesOutput

def main():
    print("🚀 Creating your first K8s-Gen application...")
    
    # Create the application
    web_app = (App("my-web-app")
        .image("nginx:1.21")
        .port(80, "http")
        .replicas(3)
        .resources(cpu="100m", memory="128Mi")
        .env("ENV", "production")
        .expose())
    
    # Generate Kubernetes resources
    resources = web_app.generate_kubernetes_resources()
    
    # Ensure output directory exists
    os.makedirs("k8s-manifests", exist_ok=True)
    
    # Generate YAML files
    output = KubernetesOutput()
    output.generate(web_app, "k8s-manifests/")
    
    print(f"✅ Generated {len(resources)} Kubernetes resources:")
    for resource in resources:
        kind = resource.get("kind", "Unknown")
        name = resource.get("metadata", {}).get("name", "unnamed")
        print(f"   - {kind}: {name}")
    
    print("\n📁 Files created in k8s-manifests/")
    print("🚀 Deploy with: kubectl apply -f k8s-manifests/")

if __name__ == "__main__":
    main()
```

### Run the Example

```bash
python my_first_app.py
```

Expected output:
```
🚀 Creating your first K8s-Gen application...
✅ Generated 2 Kubernetes resources:
   - Deployment: my-web-app
   - Service: my-web-app
   
📁 Files created in k8s-manifests/
🚀 Deploy with: kubectl apply -f k8s-manifests/
```

## Next Steps

🎯 **Congratulations!** You've created your first K8s-Gen application. Here's what to explore next:

### Immediate Next Steps

<div class="grid cards" markdown>

-   **[Add a Database](tutorials/basic-web-app.md#adding-a-database)**
    
    Learn how to add PostgreSQL or MySQL to your application

-   **[Configure Multiple Environments](tutorials/multi-environment.md)**
    
    Set up dev, staging, and production configurations

-   **[Add Health Checks](configuration/health-checks.md)**
    
    Configure liveness and readiness probes

-   **[Enable Monitoring](components/advanced/observability.md)**
    
    Add metrics, logging, and tracing

</div>

### Popular Tutorials

| Tutorial | Complexity | Time | Description |
|----------|------------|------|-------------|
| [Kafka Deployment](tutorials/kafka-deployment.md) | ⭐⭐⭐ | 15 min | Deploy a production Kafka cluster |
| [WordPress Platform](tutorials/wordpress-platform.md) | ⭐⭐ | 10 min | Full WordPress with MySQL |
| [Microservices](tutorials/microservices.md) | ⭐⭐⭐⭐ | 25 min | Complete microservices platform |
| [RBAC Security](tutorials/rbac-security.md) | ⭐⭐⭐ | 15 min | Implement security and access control |

### Core Concepts to Learn

1. **[Components Overview](components/index.md)** - Understand all available DSL components
2. **[Configuration](configuration/index.md)** - Learn about resource configuration options
3. **[Output Formats](advanced/output/kubernetes-yaml.md)** - Generate different output formats
4. **[Security](components/security/rbac.md)** - Implement security best practices

## Common Patterns

### Web Application with Database

```python
from src.k8s_gen import App, StatefulApp, Service

# Web application
web_app = (App("web-app")
    .image("myapp:latest")
    .port(8080, "http")
    .env("DATABASE_URL", "postgresql://postgres:5432/myapp")
    .replicas(3)
    .expose())

# Database
database = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432, "postgres")
    .env("POSTGRES_DB", "myapp")
    .env("POSTGRES_PASSWORD", "secretpassword")
    .storage("/var/lib/postgresql/data", "10Gi"))
```

### Multiple Output Formats

```python
from src.k8s_gen.output import KubernetesOutput, HelmOutput, DockerComposeOutput

# Kubernetes YAML
KubernetesOutput().generate(web_app, "k8s/")

# Helm Chart
helm_output = HelmOutput("my-app-chart")
helm_output.add_resource(web_app)
helm_output.generate("helm/")

# Docker Compose for local development
DockerComposeOutput().generate(web_app, "docker-compose.yml")
```

## Troubleshooting

### Common Issues

!!! warning "Import Errors"
    If you get import errors, make sure you're running from the project root and the `src/` directory is in your Python path:
    ```bash
    export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
    python my_first_app.py
    ```

!!! warning "Missing Dependencies"
    Install all required dependencies:
    ```bash
    pip install -r src/requirements.txt
    ```

### Getting Help

- 📖 **Documentation**: Browse the [Components](components/index.md) and [Examples](examples/index.md)
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/your-username/k8s-gen/issues)
- 💬 **Discussions**: Join conversations on [GitHub Discussions](https://github.com/your-username/k8s-gen/discussions)

---

**Ready for more?** Try the [Kafka Deployment Tutorial](tutorials/kafka-deployment.md) or explore [all available components](components/index.md)! 