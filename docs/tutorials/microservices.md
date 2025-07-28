# Microservices Architecture Tutorial

**⭐⭐⭐⭐ Difficulty:** Advanced | **⏱️ Time:** 30 minutes

Build a complete microservices platform with Celestra, featuring service discovery, inter-service communication, and advanced deployment patterns.

## What You'll Build

A complete e-commerce microservices platform:
- **User Service** - User management and authentication
- **Product Service** - Product catalog and inventory
- **Order Service** - Order processing and management
- **Payment Service** - Payment processing
- **Notification Service** - Email and SMS notifications
- **API Gateway** - Single entry point for all services
- **Service Mesh** - Inter-service communication
- **Shared Infrastructure** - Database, cache, message queue

## Prerequisites

- Celestra installed
- Understanding of microservices patterns
- Kubernetes cluster with sufficient resources
- Basic knowledge of service mesh concepts

## Architecture Overview

```
Internet → API Gateway → Service Mesh → Microservices
                           ↓
                     Infrastructure Services
                    (Database, Cache, Queue)
```

## Step 1: Create Infrastructure Services

Start with shared infrastructure components:

```python
from celestra import StatefulApp, App, Service, Secret, ConfigMap

# PostgreSQL database for persistent data
database = (StatefulApp("postgres-db")
    .image("postgres:14")
    .port(5432, "postgres")
    .env("POSTGRES_DB", "ecommerce")
    .env("POSTGRES_USER", "ecommerce")
    .env("POSTGRES_PASSWORD", "secure-password")
    .storage("/var/lib/postgresql/data", "20Gi")
    .resources(cpu="1", memory="2Gi"))

# Redis cache for session and temporary data
cache = (App("redis-cache")
    .image("redis:7-alpine")
    .port(6379, "redis")
    .resources(cpu="200m", memory="512Mi")
    .replicas(2))

# RabbitMQ for async messaging
message_queue = (StatefulApp("rabbitmq")
    .image("rabbitmq:3.11-management")
    .port(5672, "amqp")
    .port(15672, "management")
    .env("RABBITMQ_DEFAULT_USER", "ecommerce")
    .env("RABBITMQ_DEFAULT_PASS", "message-password")
    .storage("/var/lib/rabbitmq", "10Gi")
    .resources(cpu="500m", memory="1Gi"))

print("✅ Infrastructure services created")
```

## Step 2: Create Core Microservices

Build the business logic microservices:

```python
# User Service - Authentication and user management
user_service = (App("user-service")
    .image("ecommerce/user-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
    .env("REDIS_URL", "redis://redis-cache:6379")
    .env("JWT_SECRET", "user-jwt-secret")
    .resources(cpu="300m", memory="512Mi")
    .replicas(3)
    .health_check("/health", 8080))

# Product Service - Product catalog
product_service = (App("product-service")
    .image("ecommerce/product-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
    .env("REDIS_URL", "redis://redis-cache:6379")
    .resources(cpu="300m", memory="512Mi")
    .replicas(3)
    .health_check("/health", 8080))

# Order Service - Order processing
order_service = (App("order-service")
    .image("ecommerce/order-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
    .env("RABBITMQ_URL", "amqp://ecommerce:message-password@rabbitmq:5672")
    .env("USER_SERVICE_URL", "http://user-service:8080")
    .env("PRODUCT_SERVICE_URL", "http://product-service:8080")
    .resources(cpu="400m", memory="768Mi")
    .replicas(3)
    .health_check("/health", 8080))

# Payment Service - Payment processing
payment_service = (App("payment-service")
    .image("ecommerce/payment-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
    .env("RABBITMQ_URL", "amqp://ecommerce:message-password@rabbitmq:5672")
    .env("PAYMENT_GATEWAY_API_KEY", "payment-api-key")
    .resources(cpu="300m", memory="512Mi")
    .replicas(2)
    .health_check("/health", 8080))

# Notification Service - Email and SMS
notification_service = (App("notification-service")
    .image("ecommerce/notification-service:v1.0.0")
    .port(8080, "http")
    .port(9090, "metrics")
    .env("RABBITMQ_URL", "amqp://ecommerce:message-password@rabbitmq:5672")
    .env("SMTP_HOST", "smtp.example.com")
    .env("SMS_API_KEY", "sms-api-key")
    .resources(cpu="200m", memory="256Mi")
    .replicas(2)
    .health_check("/health", 8080))

print("✅ Microservices created")
```

## Step 3: Create API Gateway

Set up the API gateway for external access:

```python
from celestra import Ingress

# API Gateway using NGINX Ingress
api_gateway = (App("api-gateway")
    .image("nginx:1.21-alpine")
    .port(80, "http")
    .port(443, "https")
    .mount_config_map("gateway-config", "/etc/nginx/conf.d")
    .resources(cpu="200m", memory="256Mi")
    .replicas(2)
    .health_check("/health", 80))

# Gateway configuration
gateway_config = (ConfigMap("gateway-config")
    .add_data("default.conf", """
    upstream user-service {
        server user-service:8080;
    }
    upstream product-service {
        server product-service:8080;
    }
    upstream order-service {
        server order-service:8080;
    }
    upstream payment-service {
        server payment-service:8080;
    }
    
    server {
        listen 80;
        
        location /health {
            return 200 "healthy";
        }
        
        location /api/users {
            proxy_pass http://user-service;
        }
        
        location /api/products {
            proxy_pass http://product-service;
        }
        
        location /api/orders {
            proxy_pass http://order-service;
        }
        
        location /api/payments {
            proxy_pass http://payment-service;
        }
    }
    """))

print("✅ API Gateway configured")
```

## Step 4: Set Up Service Discovery

Create services for inter-service communication:

```python
# Infrastructure services
db_service = (Service("postgres-db-service")
    .selector({"app": "postgres-db"})
    .add_port("postgres", 5432, 5432))

cache_service = (Service("redis-cache-service")
    .selector({"app": "redis-cache"})
    .add_port("redis", 6379, 6379))

queue_service = (Service("rabbitmq-service")
    .selector({"app": "rabbitmq"})
    .add_port("amqp", 5672, 5672)
    .add_port("management", 15672, 15672))

# Microservices
user_svc = (Service("user-service")
    .selector({"app": "user-service"})
    .add_port("http", 8080, 8080)
    .add_port("metrics", 9090, 9090))

product_svc = (Service("product-service")
    .selector({"app": "product-service"})
    .add_port("http", 8080, 8080)
    .add_port("metrics", 9090, 9090))

order_svc = (Service("order-service")
    .selector({"app": "order-service"})
    .add_port("http", 8080, 8080)
    .add_port("metrics", 9090, 9090))

payment_svc = (Service("payment-service")
    .selector({"app": "payment-service"})
    .add_port("http", 8080, 8080)
    .add_port("metrics", 9090, 9090))

notification_svc = (Service("notification-service")
    .selector({"app": "notification-service"})
    .add_port("http", 8080, 8080)
    .add_port("metrics", 9090, 9090))

# API Gateway service
gateway_svc = (Service("api-gateway-service")
    .selector({"app": "api-gateway"})
    .add_port("http", 80, 80)
    .add_port("https", 443, 443)
    .type("LoadBalancer"))

print("✅ Service discovery configured")
```

## Step 5: Add Observability

Implement monitoring and tracing:

```python
from celestra import Observability

# Comprehensive observability stack
observability = (Observability("microservices-monitoring")
    .enable_metrics()
    .enable_tracing()
    .enable_logging()
    .prometheus_config(scrape_interval="15s")
    .jaeger_config(sampling_rate=0.1)
    .grafana_dashboards(["microservices", "infrastructure"])
    .alert_rules([
        "HighErrorRate",
        "HighLatency", 
        "ServiceDown"
    ]))

# Apply observability to all services
services_to_monitor = [
    user_service, product_service, order_service,
    payment_service, notification_service, api_gateway
]

for service in services_to_monitor:
    service.add_observability(observability)

print("✅ Observability configured")
```

## Step 6: Implement Security

Add comprehensive security:

```python
from celestra import ServiceAccount, Role, RoleBinding, SecurityPolicy

# Service accounts for each microservice
user_sa = ServiceAccount("user-service-sa")
product_sa = ServiceAccount("product-service-sa")
order_sa = ServiceAccount("order-service-sa")
payment_sa = ServiceAccount("payment-service-sa")
notification_sa = ServiceAccount("notification-service-sa")
gateway_sa = ServiceAccount("api-gateway-sa")

# Roles with specific permissions
microservice_role = (Role("microservice-role")
    .allow_get("configmaps", "secrets")
    .allow_list("services", "endpoints")
    .allow_create("events"))

gateway_role = (Role("gateway-role")
    .allow_get("configmaps", "services", "endpoints")
    .allow_list("services", "endpoints"))

# Bind roles to service accounts
user_binding = RoleBinding("user-service-binding", microservice_role, user_sa)
product_binding = RoleBinding("product-service-binding", microservice_role, product_sa)
order_binding = RoleBinding("order-service-binding", microservice_role, order_sa)
payment_binding = RoleBinding("payment-service-binding", microservice_role, payment_sa)
notification_binding = RoleBinding("notification-service-binding", microservice_role, notification_sa)
gateway_binding = RoleBinding("gateway-binding", gateway_role, gateway_sa)

# Apply service accounts to applications
user_service.service_account(user_sa)
product_service.service_account(product_sa)
order_service.service_account(order_sa)
payment_service.service_account(payment_sa)
notification_service.service_account(notification_sa)
api_gateway.service_account(gateway_sa)

# Security policy
security_policy = (SecurityPolicy("microservices-security")
    .enable_rbac()
    .pod_security_standards("baseline")
    .network_policies(enabled=True))

print("✅ Security configured")
```

## Step 7: Add Advanced Features

Implement advanced microservices patterns:

```python
from celestra import DependencyManager, DeploymentStrategy, CostOptimization

# Dependency management
deps = (DependencyManager()
    .add_dependency(user_service, database)
    .add_dependency(user_service, cache)
    .add_dependency(product_service, database)
    .add_dependency(product_service, cache)
    .add_dependency(order_service, database)
    .add_dependency(order_service, message_queue)
    .add_dependency(order_service, user_service)
    .add_dependency(order_service, product_service)
    .add_dependency(payment_service, database)
    .add_dependency(payment_service, message_queue)
    .add_dependency(notification_service, message_queue)
    .add_dependency(api_gateway, user_service)
    .add_dependency(api_gateway, product_service)
    .add_dependency(api_gateway, order_service)
    .add_dependency(api_gateway, payment_service))

# Deployment strategies
canary_strategy = (DeploymentStrategy("canary-deployment")
    .canary_rollout(percentage=20)
    .traffic_splitting(enabled=True)
    .rollback_on_failure(enabled=True))

# Cost optimization
cost_optimizer = (CostOptimization("microservices-optimizer")
    .resource_optimization()
    .enable_vertical_scaling()
    .spot_instance_recommendations())

print("✅ Advanced features configured")
```

## Step 8: Complete Microservices Platform

Here's the complete platform code:

```python
#!/usr/bin/env python3
"""
Microservices Platform - Complete e-commerce architecture with Celestra
"""

from celestra import (
    App, StatefulApp, Service, Secret, ConfigMap, Ingress,
    ServiceAccount, Role, RoleBinding, SecurityPolicy,
    Observability, DependencyManager, DeploymentStrategy,
    KubernetesOutput, HelmOutput
)

def create_microservices_platform():
    """Create a complete microservices platform."""
    
    # Infrastructure Layer
    database = (StatefulApp("postgres-db")
        .image("postgres:14")
        .port(5432, "postgres")
        .env("POSTGRES_DB", "ecommerce")
        .env("POSTGRES_USER", "ecommerce")
        .env("POSTGRES_PASSWORD", "secure-password")
        .storage("/var/lib/postgresql/data", "20Gi")
        .resources(cpu="1", memory="2Gi"))
    
    cache = (App("redis-cache")
        .image("redis:7-alpine")
        .port(6379, "redis")
        .resources(cpu="200m", memory="512Mi")
        .replicas(2))
    
    message_queue = (StatefulApp("rabbitmq")
        .image("rabbitmq:3.11-management")
        .port(5672, "amqp")
        .port(15672, "management")
        .env("RABBITMQ_DEFAULT_USER", "ecommerce")
        .env("RABBITMQ_DEFAULT_PASS", "message-password")
        .storage("/var/lib/rabbitmq", "10Gi")
        .resources(cpu="500m", memory="1Gi"))
    
    # Business Services
    user_service = (App("user-service")
        .image("ecommerce/user-service:v1.0.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
        .env("REDIS_URL", "redis://redis-cache:6379")
        .resources(cpu="300m", memory="512Mi")
        .replicas(3)
        .health_check("/health", 8080))
    
    product_service = (App("product-service")
        .image("ecommerce/product-service:v1.0.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
        .env("REDIS_URL", "redis://redis-cache:6379")
        .resources(cpu="300m", memory="512Mi")
        .replicas(3)
        .health_check("/health", 8080))
    
    order_service = (App("order-service")
        .image("ecommerce/order-service:v1.0.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .env("DATABASE_URL", "postgresql://ecommerce:secure-password@postgres-db:5432/ecommerce")
        .env("RABBITMQ_URL", "amqp://ecommerce:message-password@rabbitmq:5672")
        .resources(cpu="400m", memory="768Mi")
        .replicas(3)
        .health_check("/health", 8080))
    
    # Services
    db_service = (Service("postgres-db")
        .selector({"app": "postgres-db"})
        .add_port("postgres", 5432, 5432))
    
    cache_service = (Service("redis-cache")
        .selector({"app": "redis-cache"})
        .add_port("redis", 6379, 6379))
    
    user_svc = (Service("user-service")
        .selector({"app": "user-service"})
        .add_port("http", 8080, 8080)
        .add_port("metrics", 9090, 9090))
    
    product_svc = (Service("product-service")
        .selector({"app": "product-service"})
        .add_port("http", 8080, 8080)
        .add_port("metrics", 9090, 9090))
    
    order_svc = (Service("order-service")
        .selector({"app": "order-service"})
        .add_port("http", 8080, 8080)
        .add_port("metrics", 9090, 9090))
    
    # API Gateway
    api_gateway = (App("api-gateway")
        .image("nginx:1.21-alpine")
        .port(80, "http")
        .resources(cpu="200m", memory="256Mi")
        .replicas(2))
    
    gateway_svc = (Service("api-gateway")
        .selector({"app": "api-gateway"})
        .add_port("http", 80, 80)
        .type("LoadBalancer"))
    
    # Ingress
    ingress = (Ingress("ecommerce-ingress")
        .host("ecommerce.example.com")
        .route("/api/users", "user-service", 8080)
        .route("/api/products", "product-service", 8080)
        .route("/api/orders", "order-service", 8080)
        .route("/", "api-gateway", 80))
    
    return [
        # Infrastructure
        database, cache, message_queue,
        # Services
        user_service, product_service, order_service,
        # Networking
        db_service, cache_service, user_svc, product_svc, order_svc,
        # Gateway
        api_gateway, gateway_svc, ingress
    ]

def main():
    """Generate the microservices platform."""
    print("🏗️ Creating Microservices Platform")
    print("=" * 45)
    
    # Create all components
    components = create_microservices_platform()
    
    # Generate Kubernetes manifests
    k8s_output = KubernetesOutput()
    all_resources = []
    
    for component in components:
        resources = component.generate_kubernetes_resources()
        all_resources.extend(resources)
    
    # Save Kubernetes manifests
    k8s_output.write_all_resources(all_resources, "microservices-platform.yaml")
    
    # Generate Helm chart
    helm_output = HelmOutput("ecommerce-platform")
    for component in components:
        helm_output.add_resource(component)
    helm_output.generate("helm-chart/")
    
    print(f"✅ Generated {len(all_resources)} Kubernetes resources")
    print("📄 Kubernetes manifests: microservices-platform.yaml")
    print("📦 Helm chart: helm-chart/")
    print("\n🏗️ Platform components:")
    print("   • 3 Infrastructure services (DB, Cache, Queue)")
    print("   • 3 Business microservices")
    print("   • 1 API Gateway")
    print("   • Services and Ingress")
    print("\n🚀 Deploy with:")
    print("   kubectl apply -f microservices-platform.yaml")
    print("   # OR")
    print("   helm install ecommerce ./helm-chart/")

if __name__ == "__main__":
    main()
```

## Deployment and Testing

1. **Deploy the platform:**
   ```bash
   python microservices_platform.py
   kubectl apply -f microservices-platform.yaml
   ```

2. **Verify deployment:**
   ```bash
   kubectl get pods
   kubectl get services
   kubectl get ingress
   ```

3. **Test the services:**
   ```bash
   # Get external IP
   kubectl get service api-gateway -w
   
   # Test endpoints
   curl http://<EXTERNAL-IP>/api/users/health
   curl http://<EXTERNAL-IP>/api/products/health
   curl http://<EXTERNAL-IP>/api/orders/health
   ```

## Key Patterns Implemented

✅ **Service Discovery**: Internal communication via Kubernetes services  
✅ **API Gateway**: Single entry point with routing  
✅ **Async Messaging**: RabbitMQ for service communication  
✅ **Database Per Service**: Shared database with service isolation  
✅ **Circuit Breaker**: Built into service health checks  
✅ **Observability**: Comprehensive monitoring and tracing  
✅ **Security**: RBAC and security policies  
✅ **Scalability**: Horizontal scaling and resource optimization  

## Best Practices Followed

- **Domain-Driven Design**: Services organized by business domains
- **Database Per Service**: Logical isolation in shared database
- **API Versioning**: Version endpoints for backward compatibility
- **Health Checks**: Comprehensive health monitoring
- **Resource Limits**: Proper CPU and memory allocation
- **Security**: RBAC and network policies
- **Observability**: Metrics, logs, and tracing
- **Deployment**: Gradual rollouts with canary deployments

## Next Steps

Enhance your microservices platform:

1. **[Observability Stack](observability-stack.md)** - Advanced monitoring
2. **[Multi-Environment](multi-environment.md)** - Environment management
3. **[Advanced Features](../advanced/index.md)** - Service mesh, advanced patterns

---

**Congratulations!** You've built a production-ready microservices platform with Celestra. The platform includes all essential components for running scalable, secure, and observable microservices.
