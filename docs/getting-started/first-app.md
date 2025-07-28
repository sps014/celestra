# Your First App

Build your first complete application with Celestra! This tutorial will guide you through creating a web application with a database, showing you the essential patterns and concepts.

## What We'll Build

We'll create a complete blog application consisting of:

- **Web Server**: NGINX serving a static website
- **API Server**: Python Flask API for blog posts
- **Database**: PostgreSQL for data storage
- **Cache**: Redis for session storage
- **Networking**: Services and ingress for access

## Prerequisites

- Celestra installed ([Installation Guide](installation.md))
- Basic understanding of [Core Concepts](core-concepts.md)
- Python 3.8+ environment

## Step 1: Create the Database

Let's start with the foundation - a PostgreSQL database:

```python
from celestra import StatefulApp, Secret

# Create database credentials
db_secret = (Secret("blog-db-secret")
    .add_data("username", "bloguser")
    .add_data("password", "secure-password-123")
    .add_data("database", "blogdb"))

# Create PostgreSQL database
database = (StatefulApp("blog-database")
    .image("postgres:14")
    .port(5432, "postgres")
    .env("POSTGRES_USER", "bloguser")
    .env("POSTGRES_PASSWORD", "secure-password-123")
    .env("POSTGRES_DB", "blogdb")
    .storage("/var/lib/postgresql/data", "10Gi")
    .resources(cpu="500m", memory="1Gi")
    .health_check("/", 5432))

print("✅ Database configured")
```

**Key points:**
- `StatefulApp` ensures persistent storage
- Secrets store sensitive database credentials
- Health checks ensure database reliability
- Resource limits prevent resource exhaustion

## Step 2: Add a Cache Layer

Add Redis for caching and session storage:

```python
from celestra import App

# Create Redis cache
cache = (App("blog-cache")
    .image("redis:7-alpine")
    .port(6379, "redis")
    .resources(cpu="100m", memory="256Mi")
    .replicas(1))

print("✅ Cache configured")
```

**Key points:**
- `App` is used because Redis can be stateless in this setup
- Minimal resources since it's just caching
- Single replica is sufficient for this example

## Step 3: Create the API Server

Build the backend API service:

```python
# Create the Flask API server
api_server = (App("blog-api")
    .image("python:3.9-slim")
    .port(5000, "api")
    .env("DATABASE_URL", "postgresql://bloguser:secure-password-123@blog-database:5432/blogdb")
    .env("REDIS_URL", "redis://blog-cache:6379")
    .env("FLASK_ENV", "production")
    .command([
        "sh", "-c",
        "pip install flask psycopg2-binary redis && python app.py"
    ])
    .resources(cpu="200m", memory="512Mi")
    .replicas(2)
    .health_check("/health", 5000))

print("✅ API server configured")
```

**Key points:**
- Environment variables connect to database and cache
- Health check ensures API availability
- Multiple replicas for high availability
- Startup command installs dependencies and runs the app

## Step 4: Add the Web Server

Create an NGINX frontend:

```python
# Create NGINX web server
web_server = (App("blog-web")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .port(443, "https")
    .resources(cpu="100m", memory="128Mi")
    .replicas(2)
    .health_check("/", 80))

print("✅ Web server configured")
```

## Step 5: Set Up Networking

Configure services to connect everything:

```python
from celestra import Service, Ingress

# Database service (internal only)
db_service = (Service("blog-database-service")
    .selector({"app": "blog-database"})
    .add_port("postgres", 5432, 5432)
    .type("ClusterIP"))

# Cache service (internal only)
cache_service = (Service("blog-cache-service")
    .selector({"app": "blog-cache"})
    .add_port("redis", 6379, 6379)
    .type("ClusterIP"))

# API service (internal)
api_service = (Service("blog-api-service")
    .selector({"app": "blog-api"})
    .add_port("api", 5000, 5000)
    .type("ClusterIP"))

# Web service (external)
web_service = (Service("blog-web-service")
    .selector({"app": "blog-web"})
    .add_port("http", 80, 80)
    .add_port("https", 443, 443)
    .type("LoadBalancer"))

# Ingress for external access
ingress = (Ingress("blog-ingress")
    .host("blog.example.com")
    .route("/api", "blog-api-service", 5000)
    .route("/", "blog-web-service", 80)
    .tls("blog-tls"))

print("✅ Networking configured")
```

**Key points:**
- `ClusterIP` services are internal-only
- `LoadBalancer` service provides external access
- Ingress provides HTTP routing and TLS termination

## Step 6: Add Security

Implement proper RBAC and security:

```python
from celestra import ServiceAccount, Role, RoleBinding, SecurityPolicy

# Create service account
blog_sa = (ServiceAccount("blog-service-account")
    .add_label("app", "blog"))

# Create role with minimal permissions
blog_role = (Role("blog-role")
    .allow_get("configmaps", "secrets")
    .allow_list("services"))

# Bind role to service account
blog_binding = RoleBinding("blog-role-binding", blog_role, blog_sa)

# Apply security policy
security_policy = (SecurityPolicy("blog-security")
    .enable_rbac()
    .pod_security_standards("baseline")
    .network_policies(enabled=True))

print("✅ Security configured")
```

## Step 7: Generate Deployment Files

Create all the Kubernetes manifests:

```python
from celestra import KubernetesOutput

# Collect all components
components = [
    db_secret, database, cache, api_server, web_server,
    db_service, cache_service, api_service, web_service, ingress,
    blog_sa, blog_role, blog_binding
]

# Generate Kubernetes YAML
output = KubernetesOutput()

print("📄 Generating Kubernetes manifests...")
for component in components:
    resources = component.generate_kubernetes_resources()
    output.write_resources(resources, f"blog-app-{component._name}.yaml")

print("✅ All manifests generated in current directory")
```

## Step 8: Complete Application

Here's the complete application code:

```python
#!/usr/bin/env python3
"""
Blog Application - Your First Celestra App

A complete web application with database, cache, API, and frontend.
"""

from celestra import (
    App, StatefulApp, Secret, Service, Ingress,
    ServiceAccount, Role, RoleBinding, SecurityPolicy,
    KubernetesOutput
)

def create_blog_app():
    """Create a complete blog application."""
    
    # 1. Database layer
    db_secret = (Secret("blog-db-secret")
        .add_data("username", "bloguser")
        .add_data("password", "secure-password-123")
        .add_data("database", "blogdb"))
    
    database = (StatefulApp("blog-database")
        .image("postgres:14")
        .port(5432, "postgres")
        .env("POSTGRES_USER", "bloguser")
        .env("POSTGRES_PASSWORD", "secure-password-123")
        .env("POSTGRES_DB", "blogdb")
        .storage("/var/lib/postgresql/data", "10Gi")
        .resources(cpu="500m", memory="1Gi"))
    
    # 2. Cache layer
    cache = (App("blog-cache")
        .image("redis:7-alpine")
        .port(6379, "redis")
        .resources(cpu="100m", memory="256Mi"))
    
    # 3. API server
    api_server = (App("blog-api")
        .image("python:3.9-slim")
        .port(5000, "api")
        .env("DATABASE_URL", "postgresql://bloguser:secure-password-123@blog-database:5432/blogdb")
        .env("REDIS_URL", "redis://blog-cache:6379")
        .resources(cpu="200m", memory="512Mi")
        .replicas(2)
        .health_check("/health", 5000))
    
    # 4. Web server
    web_server = (App("blog-web")
        .image("nginx:1.21-alpine")
        .port(80, "http")
        .resources(cpu="100m", memory="128Mi")
        .replicas(2))
    
    # 5. Services
    db_service = (Service("blog-database-service")
        .selector({"app": "blog-database"})
        .add_port("postgres", 5432, 5432))
    
    cache_service = (Service("blog-cache-service")
        .selector({"app": "blog-cache"})
        .add_port("redis", 6379, 6379))
    
    api_service = (Service("blog-api-service")
        .selector({"app": "blog-api"})
        .add_port("api", 5000, 5000))
    
    web_service = (Service("blog-web-service")
        .selector({"app": "blog-web"})
        .add_port("http", 80, 80)
        .type("LoadBalancer"))
    
    # 6. Ingress
    ingress = (Ingress("blog-ingress")
        .host("blog.example.com")
        .route("/api", "blog-api-service", 5000)
        .route("/", "blog-web-service", 80))
    
    # 7. Security
    service_account = ServiceAccount("blog-sa")
    role = (Role("blog-role")
        .allow_get("configmaps", "secrets")
        .allow_list("services"))
    role_binding = RoleBinding("blog-binding", role, service_account)
    
    return [
        db_secret, database, cache, api_server, web_server,
        db_service, cache_service, api_service, web_service, ingress,
        service_account, role, role_binding
    ]

def main():
    """Generate the complete blog application."""
    print("🚀 Creating Blog Application with Celestra")
    print("=" * 50)
    
    # Create all components
    components = create_blog_app()
    
    # Generate manifests
    output = KubernetesOutput()
    all_resources = []
    
    for component in components:
        resources = component.generate_kubernetes_resources()
        all_resources.extend(resources)
    
    # Write to file
    output.write_all_resources(all_resources, "blog-app-complete.yaml")
    
    print(f"✅ Generated {len(all_resources)} Kubernetes resources")
    print("📄 Saved to: blog-app-complete.yaml")
    print("\n🎯 Next steps:")
    print("   kubectl apply -f blog-app-complete.yaml")
    print("   kubectl get pods")
    print("   kubectl get services")

if __name__ == "__main__":
    main()
```

## Deployment

To deploy your first app:

1. **Save the code** to a file (e.g., `blog_app.py`)

2. **Generate manifests:**
   ```bash
   python blog_app.py
   ```

3. **Deploy to Kubernetes:**
   ```bash
   kubectl apply -f blog-app-complete.yaml
   ```

4. **Verify deployment:**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get ingress
   ```

## Testing the Application

Check that everything is running:

```bash
# Check pod status
kubectl get pods

# Check services
kubectl get services

# Check logs
kubectl logs -l app=blog-api
kubectl logs -l app=blog-web

# Port forward to test locally
kubectl port-forward service/blog-web-service 8080:80
```

Then visit `http://localhost:8080` in your browser.

## What You've Learned

Congratulations! You've built your first complete application with Celestra. You've learned:

- ✅ **Core Components**: App vs StatefulApp usage
- ✅ **Networking**: Services and ingress configuration
- ✅ **Security**: RBAC and secrets management
- ✅ **Storage**: Persistent volumes for databases
- ✅ **Output Generation**: Creating Kubernetes manifests
- ✅ **Best Practices**: Resource management and health checks

## Next Steps

Now you're ready for more advanced topics:

1. **[Tutorials](../tutorials/index.md)** - Build more complex applications
2. **[Examples](../examples/index.md)** - Explore real-world patterns
3. **[Components](../components/index.md)** - Learn about all available components
4. **[Advanced Features](../advanced/index.md)** - Observability, cost optimization, and more

---

**Ready for more?** Check out the [Kafka deployment tutorial](../tutorials/kafka-deployment.md) or explore [microservices patterns](../tutorials/microservices.md)!
