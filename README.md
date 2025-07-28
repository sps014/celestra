# K8s-Gen 🚀

> **Transform your application deployments with a simple Python DSL**

K8s-Gen is a powerful Domain-Specific Language (DSL) that lets you define cloud-native applications using simple Python code and automatically generates production-ready Kubernetes manifests, Docker Compose files, Helm charts, and more.

## ✨ Why K8s-Gen?

**Before (Traditional YAML):**
```yaml
# 100+ lines of complex YAML for a simple web app
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: web-server:latest
        ports:
        - containerPort: 8080
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
# ... and much more YAML
```

**After (K8s-Gen DSL):**
```python
from k8s_gen import App

web_app = (App("web-app")
    .image("web-server:latest")
    .port(8080)
    .resources(cpu="500m", memory="512Mi", cpu_limit="1000m", memory_limit="1Gi")
    .scale(replicas=3, auto_scale_on_cpu=70)
    .expose(external_access=True, domain="myapp.com"))

# Generate everything
web_app.generate().to_yaml("./k8s/")              # Kubernetes manifests
web_app.generate().to_docker_compose("./docker-compose.yml")  # Local development
web_app.generate().to_helm_chart("./charts/")     # Helm packaging
```

## 🎯 Key Features

- **🐍 Python-First:** Write infrastructure as code using familiar Python syntax
- **🎭 Multi-Format Output:** Generate Kubernetes, Docker Compose, Helm, Kustomize from the same code
- **🔒 Production-Ready:** Built-in security, monitoring, secrets management, and RBAC
- **🚀 Zero-Downtime Deployments:** Blue-green, canary, and rolling update strategies
- **🔧 Extensible:** Plugin system for custom requirements and integrations
- **💡 Developer Friendly:** Start with Docker Compose, deploy to Kubernetes seamlessly

## 🚀 Quick Start

### Installation
```bash
pip install k8s-gen
```

### Create Your First App
```python
# app.py
from k8s_gen import App, StatefulApp, Secret

# Database with automatic backups
db = (StatefulApp("database")
    .image("database-server:latest")
    .storage("20Gi")
    .backup_schedule("0 2 * * *"))

# Database credentials
db_secret = (Secret("db-creds")
    .add("username", "admin")
    .add("password", "secure-password"))

# Web application
app = (App("blog")
    .image("webapp:latest")
    .port(8080)
    .connect_to([db])
    .add_secrets([db_secret])
    .scale(replicas=3, auto_scale_on_cpu=70)
    .expose(external_access=True, domain="myblog.com"))

# Generate and deploy
app.generate().to_yaml("./k8s/")
```

### Deploy Locally
```bash
# Start with Docker Compose for development
k8s-gen dev app.py

# Generate Kubernetes manifests for production
k8s-gen generate app.py --output ./k8s/

# Deploy to Kubernetes
kubectl apply -f ./k8s/
```

## 🏗️ Architecture

K8s-Gen abstracts Kubernetes complexity while maintaining full power:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python DSL    │───▶│   K8s-Gen Core   │───▶│   Output Files  │
│                 │    │                  │    │                 │
│ • Apps          │    │ • Validation     │    │ • Kubernetes    │
│ • StatefulApps  │    │ • Templates      │    │ • Docker Compose│
│ • Secrets       │    │ • Plugins        │    │ • Helm Charts   │
│ • Jobs          │    │ • Optimization   │    │ • Terraform     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎨 Real-World Examples

### Microservices Platform
```python
from k8s_gen import AppGroup, App, StatefulApp

platform = AppGroup("ecommerce")

# Shared infrastructure
database = StatefulApp("database").image("database-server:latest").storage("100Gi")
cache = StatefulApp("cache").image("cache-server:latest").storage("10Gi")

# Microservices
user_service = App("users").image("myorg/users:v1.0").port(8080).connect_to([database])
product_service = App("products").image("myorg/products:v1.0").port(8081).connect_to([database])
order_service = App("orders").image("myorg/orders:v1.0").port(8082).connect_to([database, cache])

platform.add_services([database, cache, user_service, product_service, order_service])
platform.generate().to_yaml("./k8s/")
```

### ML Training Pipeline
```python
from k8s_gen import Job, CronJob

# One-time training job
training = (Job("model-training")
    .image("ml-framework:latest")
    .resources(cpu="4000m", memory="16Gi")
    .gpu_resources(2)
    .timeout("6h"))

# Scheduled retraining
retrain = (CronJob("model-retrain")
    .image("ml-framework:latest")
    .schedule("0 2 * * 0")  # Weekly
    .resources(cpu="8000m", memory="32Gi"))

training.generate().to_yaml("./jobs/")
```

## 📚 Documentation

- **[📖 Complete Specifications](./specs/)** - Comprehensive documentation
- **[🚀 Quick Start Guide](./specs/index.md)** - Get started in minutes  
- **[📚 API Reference](./specs/api-reference.md)** - Complete API documentation
- **[📤 Output Examples](./specs/output-examples.md)** - See generated manifests
- **[⚡ CLI Reference](./specs/cli.md)** - Command-line tools
- **[🔌 Extensions](./specs/extensions.md)** - Plugin system and customization

## 🌟 Why Choose K8s-Gen?

### For Developers
- **No YAML Hell** - Write infrastructure in Python
- **Fast Iteration** - Start local, deploy anywhere
- **Type Safety** - Catch errors before deployment
- **Familiar Syntax** - If you know Python, you know K8s-Gen

### For DevOps Teams
- **Standardization** - Consistent deployments across teams
- **Security Built-in** - RBAC, secrets, policies by default
- **Multi-Environment** - Dev, staging, prod from same code
- **Observability Ready** - Monitoring and logging included

### For Organizations
- **Reduced Complexity** - Abstract Kubernetes details
- **Faster Onboarding** - Developers focus on business logic  
- **Cost Optimization** - Built-in resource management
- **Compliance Ready** - Security and governance features

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `pytest`
5. **Submit a pull request**

See our [Contributing Guide](./CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🎉 Get Started Now

```bash
# Install K8s-Gen
pip install k8s-gen

# Create your first application
k8s-gen init my-app --template web

# Start developing
cd my-app
k8s-gen dev app.py
```

**Ready to simplify your Kubernetes deployments?** [Check out the complete documentation](./specs/) and join thousands of developers already using K8s-Gen! 🚀

---

<div align="center">

**[Documentation](./specs/) • [Examples](./specs/output-examples.md) • [API Reference](./specs/api-reference.md) • [CLI Guide](./specs/cli.md)**

Made with ❤️ by the K8s-Gen community

</div>