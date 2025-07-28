# Celestra 🚀

> **Transform your application deployments with a simple Python DSL**

Celestra is a powerful Domain-Specific Language (DSL) that lets you define cloud-native applications using simple Python code and automatically generates production-ready Kubernetes manifests, Docker Compose files, Helm charts, and more.

## ✨ Why Celestra?

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

**After (Celestra):**
```python
from celestra import App

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

# install from PyPI 
pip install celestra

# Or from source (recommended for development)
git clone https://github.com/your-org/celestra.git
cd celestra
pip install -e src/

```

### Create Your First App
```python
# app.py
from celestra import App, StatefulApp, Secret

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

Celestra abstracts Kubernetes complexity while maintaining full power:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Python DSL    │───▶│   Celestra Core  │───▶│   Output Files  │
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
from celestra import AppGroup, App, StatefulApp

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
from celestra import Job, CronJob

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
from celestra import App, StatefulApp, Secret, Service, Ingress

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

## 🌟 Why Choose Celestra?

### For Developers
- **No YAML Hell** - Write infrastructure in Python
- **Fast Iteration** - Start local, deploy anywhere
- **Type Safety** - Catch errors before deployment
- **Familiar Syntax - If you know Python, you know Celestra

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

## ⚠️ Format-Specific Methods & Output Awareness

Celestra supports multiple output formats (Kubernetes, Docker Compose, Helm, etc.). Some methods are only meaningful for certain formats. **Celestra will automatically warn you if you use a method that is not supported in your chosen output format!**

### 🐳 Docker Compose-Only Methods
- `.port_mapping(host_port, container_port, ...)` — Only for Docker Compose (host:container mapping)
- `.expose_port(port, ..., external_port=...)` — Only for Docker Compose

### ☸️ Kubernetes-Only Methods
- `.node_selector({...})` — Only for Kubernetes (pod scheduling)
- `.tolerations([...])` — Only for Kubernetes (taints/tolerations)

### 🔄 Universal Methods
- `.port(port)` — Works everywhere (container port)
- `.image(image)` — Works everywhere
- `.replicas(n)` — Works everywhere
- `.env(key, value)` — Works everywhere

### 🚦 How It Works
- If you use `.port_mapping()` and generate Kubernetes YAML, you will see:
  ```
  ⚠️  Method 'port_mapping()' is Docker Compose-specific and will be ignored in Kubernetes output. For Kubernetes, use 'port()' + 'Service' instead of 'port_mapping()'.
  ```
- If you use `.node_selector()` and generate Docker Compose, you will see:
  ```
  ⚠️  Method 'node_selector()' is Kubernetes-specific and will be ignored in Docker Compose output.
  ```

### 🏷️ Decorators for Custom Extensions
You can mark your own methods as format-specific using built-in decorators:
```python
from celestra import docker_compose_only, kubernetes_only, output_formats

@docker_compose_only
def my_compose_method(self, ...): ...

@kubernetes_only
def my_k8s_method(self, ...): ...

@output_formats('kubernetes', 'helm')
def my_multi_format_method(self, ...): ...
```

### 💡 Best Practice
- **For Docker Compose:** Use `.port_mapping()` for host:container mapping
- **For Kubernetes:** Use `.port()` and create a `Service` for exposure
- **Universal:** Use `.port()`, `.image()`, `.replicas()`, `.env()`, etc.

Celestra will always guide you with clear warnings and suggestions if you use a method in the wrong context!

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
# Install Celestra from source
git clone https://github.com/your-org/celestra.git
cd celestra
pip install -e src/

# Create your first application
cat > my_app.py << EOF
from celestra import App

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

**Ready to simplify your Kubernetes deployments?** [Check out the complete documentation](./docs/) and join thousands of developers already using Celestra! 🚀

---

<div align="center">

**[Documentation](./docs/) • [Examples](./docs/examples/) • [API Reference](./docs/api-reference/) • [Components](./docs/components/)**

Made with ❤️ by the Celestra community

</div>