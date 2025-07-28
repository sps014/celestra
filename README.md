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
    .replicas(3)
    .expose())

# Generate everything
web_app.generate().to_yaml("./k8s/")                    # Kubernetes manifests
web_app.generate().to_docker_compose("./docker-compose.yml")  # Local development
web_app.generate().to_helm_chart("./charts/")           # Helm packaging
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
# From source (recommended for development)
git clone https://github.com/your-org/k8s-gen.git
cd k8s-gen
pip install -e src/

# Or install from PyPI (when available)
pip install k8s-gen-dsl
```

### Create Your First App
```python
# app.py
from k8s_gen import App, StatefulApp, Secret

# Database with automatic backups
db = (StatefulApp("database")
    .image("postgres:15")
    .port(5432)
    .storage("20Gi"))

# Database credentials
db_secret = (Secret("db-creds")
    .add("username", "admin")
    .add("password", "secure-password"))

# Web application
app = (App("blog")
    .image("webapp:latest")
    .port(8080)
    .replicas(3)
    .expose())

# Generate and deploy
app.generate().to_yaml("./k8s/")
db.generate().to_yaml("./k8s/")
db_secret.generate().to_yaml("./k8s/")
```

### Deploy Locally
```bash
# Generate Kubernetes manifests
python app.py

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
│ • Jobs          │    │ • Optimization   │    │ • Kustomize     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🎨 Real-World Examples

### Microservices Platform
```python
from k8s_gen import AppGroup, App, StatefulApp

platform = AppGroup("ecommerce")

# Shared infrastructure
database = StatefulApp("database").image("postgres:15").port(5432).storage("100Gi")
cache = StatefulApp("cache").image("redis:7").port(6379).storage("10Gi")

# Microservices
user_service = App("users").image("myorg/users:v1.0").port(8080)
product_service = App("products").image("myorg/products:v1.0").port(8081)
order_service = App("orders").image("myorg/orders:v1.0").port(8082)

platform.add([database, cache, user_service, product_service, order_service])
platform.generate().to_yaml("./k8s/")
```

### ML Training Pipeline
```python
from k8s_gen import Job, CronJob

# One-time training job
training = (Job("model-training")
    .image("ml-framework:latest")
    .resources(cpu="4000m", memory="16Gi")
    .timeout("6h"))

# Scheduled retraining
retrain = (CronJob("model-retrain")
    .image("ml-framework:latest")
    .schedule("0 2 * * 0")  # Weekly
    .resources(cpu="8000m", memory="32Gi"))

training.generate().to_yaml("./jobs/")
retrain.generate().to_yaml("./jobs/")
```

### Complete Web Application
```python
from k8s_gen import App, StatefulApp, Secret, Service, Ingress

# Database
db_secret = Secret("db-secret").add("password", "secure-password")
database = (StatefulApp("database")
    .image("postgres:15")
    .port(5432)
    .storage("50Gi")
    .add_secrets([db_secret]))

# Backend API
api = (App("api")
    .image("myapp/api:latest")
    .port(8080)
    .replicas(3)
    .add_secrets([db_secret]))

# Frontend
frontend = (App("frontend")
    .image("myapp/frontend:latest")
    .port(80)
    .replicas(2))

# Services
api_service = Service("api-service").add_app(api)
frontend_service = Service("frontend-service").add_app(frontend)

# Ingress
ingress = (Ingress("app-ingress")
    .domain("myapp.com")
    .route("/api", api_service)
    .route("/", frontend_service))

# Generate all components
for component in [db_secret, database, api, frontend, api_service, frontend_service, ingress]:
    component.generate().to_yaml("./k8s/")
```

## 📚 Documentation

- **[📖 Complete Documentation](./docs/)** - Full documentation site
- **[🚀 Getting Started](./docs/getting-started/)** - Installation and first steps
- **[📚 API Reference](./docs/api-reference/)** - Complete API documentation
- **[🎯 Examples](./docs/examples/)** - Real-world examples and tutorials
- **[🔧 Components](./docs/components/)** - All available components
- **[⚙️ Configuration](./docs/configuration/)** - Configuration options

## 📦 Available Components

### Core Components
- **`App`** - Stateless applications (Deployments)
- **`StatefulApp`** - Stateful applications (StatefulSets)
- **`AppGroup`** - Group multiple applications together

### Workloads
- **`Job`** - One-time tasks
- **`CronJob`** - Scheduled tasks
- **`Lifecycle`** - Lifecycle hooks

### Networking
- **`Service`** - Service definitions
- **`Ingress`** - Ingress controllers
- **`NetworkPolicy`** - Network policies

### Security
- **`Secret`** - Secret management
- **`ServiceAccount`** - Service accounts
- **`Role`** / **`ClusterRole`** - RBAC roles
- **`RoleBinding`** / **`ClusterRoleBinding`** - RBAC bindings
- **`SecurityPolicy`** - Security policies

### Storage
- **`ConfigMap`** - Configuration management

### Advanced Features
- **`Observability`** - Monitoring and logging
- **`DeploymentStrategy`** - Deployment strategies
- **`CostOptimization`** - Resource optimization
- **`CustomResource`** - Custom resource definitions

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

## 🧪 Running Examples

```bash
# Run comprehensive examples
cd src/examples

# Multiple ports showcase
python multiple_ports_showcase.py

# Enterprise validation demo
python enterprise_validation_demo.py

# Complete platform demo
python complete_platform_demo.py

# RBAC security demo
python rbac_security_demo.py

# Kubernetes YAML generation example
python kubernetes_yaml_generation_example.py
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run tests**: `python run_tests.py`
5. **Submit a pull request**

See our [Contributing Guide](./CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🎉 Get Started Now

```bash
# Install K8s-Gen from source
git clone https://github.com/your-org/k8s-gen.git
cd k8s-gen
pip install -e src/

# Create your first application
cat > my_app.py << EOF
from k8s_gen import App

app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .replicas(2)
    .expose())

app.generate().to_yaml("./k8s/")
print("✅ Kubernetes manifests generated in ./k8s/")
EOF

# Generate and deploy
python my_app.py
kubectl apply -f ./k8s/
```

**Ready to simplify your Kubernetes deployments?** [Check out the complete documentation](./docs/) and join thousands of developers already using K8s-Gen! 🚀

---

<div align="center">

**[Documentation](./docs/) • [Examples](./docs/examples/) • [API Reference](./docs/api-reference/) • [Components](./docs/components/)**

Made with ❤️ by the K8s-Gen community

</div>