# K8s-Gen DSL Specification

## Overview

K8s-Gen is a Python-based Domain-Specific Language (DSL) for generating Kubernetes manifests with minimal code complexity. The DSL abstracts away Kubernetes-specific terminology and provides an intuitive, builder-pattern API that allows developers to describe their applications and infrastructure needs without deep Kubernetes knowledge.

## Design Principles

### 1. Abstraction Over Configuration
- Users describe **what** they want, not **how** to configure it
- Business-focused terminology instead of Kubernetes jargon
- Sensible defaults for common patterns

### 2. Builder Pattern Architecture
- Fluent, chainable API
- Progressive disclosure of complexity
- Type-safe method chaining

### 3. Extensibility
- Plugin system for custom components
- Hooks for advanced configurations
- Composable patterns

## Core Concepts

### Application-Centric Model

Instead of thinking in terms of Pods, Services, and Deployments, users think in terms of:

- **Apps** - The main business logic containers (stateless)
- **StatefulApps** - Applications requiring persistent state (databases, message queues, etc.)
- **Companions** - Supporting containers (sidecars, init containers)
- **Storage** - Data persistence needs
- **Networking** - How services communicate
- **Scaling** - Performance and availability requirements
- **Lifecycle** - Container lifecycle management (hooks, signals)

## Quick Start Example

```python
from k8s_gen import App, StatefulApp, Secret, ConfigMap

# Create secrets and config
db_secret = Secret("db-creds").add("password", "secret123")
app_config = ConfigMap("app-config").add("environment", "production")

# Create database
postgres = StatefulApp("postgres").image("postgres:13").storage("20Gi")

# Create web application
web_app = (App("my-web-app")
    .image("nginx:1.21")
    .port(80)
    .connect_to([postgres])
    .add_secrets([db_secret])
    .add_config([app_config])
    .scale(replicas=3, auto_scale_on_cpu=70)
    .expose(external_access=True, domain="myapp.com"))

# Generate Kubernetes manifests
web_app.generate().to_yaml("./k8s/")

# Generate Docker Compose for local development
web_app.generate().to_docker_compose("./docker-compose.yml")
```

## Documentation Structure

- **[API Reference](./api-reference.md)** - Complete API documentation with examples
- **[Output Examples](./output-examples.md)** - Generated Kubernetes and Docker Compose examples  
- **[Advanced Features](./advanced-features.md)** - Production-ready features and integrations
- **[Implementation](./implementation.md)** - Architecture and builder pattern details
- **[CLI Reference](./cli.md)** - Command-line interface documentation
- **[Extensions](./extensions.md)** - Plugin system and customization options

## Key Benefits

### For Developers
- **Simple API** - No need to learn complex Kubernetes YAML
- **Type Safety** - Builder pattern prevents configuration errors
- **Fast Development** - Start with Docker Compose, deploy to Kubernetes
- **Consistency** - Same application structure across environments

### For DevOps
- **Production Ready** - Built-in security, monitoring, and best practices
- **Multi-Format** - Generate Kubernetes, Helm, Kustomize, Terraform
- **Extensible** - Plugin system for custom requirements
- **Validation** - Comprehensive validation and security scanning

### For Organizations
- **Reduced Complexity** - Abstract away Kubernetes details
- **Faster Onboarding** - Developers focus on business logic
- **Standardization** - Consistent deployment patterns
- **Cost Optimization** - Built-in resource management and scaling

## Getting Started

1. **Install k8s-gen:**
   ```bash
   pip install k8s-gen
   ```

2. **Initialize a new project:**
   ```bash
   k8s-gen init my-app
   cd my-app
   ```

3. **Define your application:**
   ```python
   # app.py
   from k8s_gen import App
   
   app = App("hello-world").image("nginx:alpine").port(80)
   ```

4. **Generate and deploy:**
   ```bash
   # For local development
   k8s-gen dev app.py
   
   # For production
   k8s-gen generate app.py --format kubernetes --output ./k8s/
   kubectl apply -f ./k8s/
   ```

## Next Steps

- Explore the [API Reference](./api-reference.md) for detailed examples
- Check out [Output Examples](./output-examples.md) to see generated manifests
- Learn about [Advanced Features](./advanced-features.md) for production use 