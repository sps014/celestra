# Microservices Tutorial

This tutorial demonstrates how to build a complete microservices architecture using Celestra DSL.

## Overview

This tutorial shows how to:
- Design microservices architecture
- Implement service discovery
- Set up API gateway
- Configure inter-service communication
- Deploy with proper monitoring

## Architecture

Our microservices platform will include:

- **API Gateway** - Centralized routing and authentication
- **User Service** - User management and authentication
- **Product Service** - Product catalog and inventory
- **Order Service** - Order processing and management
- **Payment Service** - Payment processing
- **Notification Service** - Email and SMS notifications
- **Database Services** - PostgreSQL and Redis

## Implementation

### 1. API Gateway

```python
from celestra import App, Ingress, Secret, ConfigMap

# API Gateway
gateway = (App("api-gateway")
    .image("nginx:alpine")
    .port(80)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .expose())

# Gateway configuration
gateway_config = (ConfigMap("gateway-config")
    .add("nginx.conf", """
events {
    worker_connections 1024;
}

http {
    upstream user-service {
        server user-service:3001;
    }
    
    upstream product-service {
        server product-service:3002;
    }
    
    upstream order-service {
        server order-service:3003;
    }
    
    server {
        listen 80;
        
        location /api/users {
            proxy_pass http://user-service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/products {
            proxy_pass http://product-service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location /api/orders {
            proxy_pass http://order-service;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}""")
    .mount_as_file("/etc/nginx/nginx.conf"))

gateway.add_config(gateway_config)

# Ingress for external access
ingress = (Ingress("api-ingress")
    .add_rule("api.example.com", "/api", "api-gateway", 80)
    .tls_enabled(True)
    .add_tls_secret("api-tls"))
```

### 2. User Service

```python
from celestra import App, StatefulApp, Secret, ConfigMap

# PostgreSQL database for users
user_db = (StatefulApp("user-db")
    .image("postgres:14")
    .port(5432)
    .storage("10Gi")
    .environment({
        "POSTGRES_DB": "users",
        "POSTGRES_USER": "user_service"
    })
    .expose())

# User service
user_service = (App("user-service")
    .image("user-service:1.0.0")
    .port(3001)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3001",
        "DB_HOST": "user-db",
        "DB_PORT": "5432"
    })
    .expose())

# Database secret
db_secret = (Secret("user-db-secret")
    .add("password", "secure-password")
    .mount_as_env_vars(prefix="DB_"))

user_service.add_secret(db_secret)
```

### 3. Product Service

```python
from celestra import App, StatefulApp, Secret

# PostgreSQL database for products
product_db = (StatefulApp("product-db")
    .image("postgres:14")
    .port(5432)
    .storage("10Gi")
    .environment({
        "POSTGRES_DB": "products",
        "POSTGRES_USER": "product_service"
    })
    .expose())

# Product service
product_service = (App("product-service")
    .image("product-service:1.0.0")
    .port(3002)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3002",
        "DB_HOST": "product-db",
        "DB_PORT": "5432"
    })
    .expose())

# Database secret
product_db_secret = (Secret("product-db-secret")
    .add("password", "secure-password")
    .mount_as_env_vars(prefix="DB_"))

product_service.add_secret(product_db_secret)
```

### 4. Order Service

```python
from celestra import App, StatefulApp, Secret

# PostgreSQL database for orders
order_db = (StatefulApp("order-db")
    .image("postgres:14")
    .port(5432)
    .storage("10Gi")
    .environment({
        "POSTGRES_DB": "orders",
        "POSTGRES_USER": "order_service"
    })
    .expose())

# Order service
order_service = (App("order-service")
    .image("order-service:1.0.0")
    .port(3003)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3003",
        "DB_HOST": "order-db",
        "DB_PORT": "5432"
    })
    .expose())

# Database secret
order_db_secret = (Secret("order-db-secret")
    .add("password", "secure-password")
    .mount_as_env_vars(prefix="DB_"))

order_service.add_secret(order_db_secret)
```

### 5. Payment Service

```python
from celestra import App, Secret

# Payment service
payment_service = (App("payment-service")
    .image("payment-service:1.0.0")
    .port(3004)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3004"
    })
    .expose())

# Payment API secrets
payment_secret = (Secret("payment-secret")
    .add("stripe_key", "sk_live_...")
    .add("paypal_client_id", "client_id")
    .add("paypal_secret", "secret")
    .mount_as_env_vars(prefix="PAYMENT_"))

payment_service.add_secret(payment_secret)
```

### 6. Notification Service

```python
from celestra import App, Secret

# Notification service
notification_service = (App("notification-service")
    .image("notification-service:1.0.0")
    .port(3005)
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .environment({
        "NODE_ENV": "production",
        "PORT": "3005"
    })
    .expose())

# Email and SMS secrets
notification_secret = (Secret("notification-secret")
    .add("smtp_host", "smtp.gmail.com")
    .add("smtp_port", "587")
    .add("smtp_user", "notifications@example.com")
    .add("smtp_password", "secure-password")
    .add("twilio_account_sid", "account_sid")
    .add("twilio_auth_token", "auth_token")
    .mount_as_env_vars(prefix="NOTIFICATION_"))

notification_service.add_secret(notification_secret)
```

### 7. Redis Cache

```python
from celestra import StatefulApp

# Redis cache
redis = (StatefulApp("redis")
    .image("redis:7-alpine")
    .port(6379)
    .storage("5Gi")
    .replicas(3)
    .resources(cpu="200m", memory="256Mi")
    .expose())
```

## Deployment

### 1. Generate all manifests

```python
# Generate all services
gateway.generate().to_yaml("./k8s/")
user_db.generate().to_yaml("./k8s/")
user_service.generate().to_yaml("./k8s/")
product_db.generate().to_yaml("./k8s/")
product_service.generate().to_yaml("./k8s/")
order_db.generate().to_yaml("./k8s/")
order_service.generate().to_yaml("./k8s/")
payment_service.generate().to_yaml("./k8s/")
notification_service.generate().to_yaml("./k8s/")
redis.generate().to_yaml("./k8s/")
ingress.generate().to_yaml("./k8s/")
```

### 2. Apply the deployment

```bash
# Apply databases first
kubectl apply -f k8s/*-db-*.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l app=user-db --timeout=300s
kubectl wait --for=condition=ready pod -l app=product-db --timeout=300s
kubectl wait --for=condition=ready pod -l app=order-db --timeout=300s

# Apply services
kubectl apply -f k8s/*-service-*.yaml

# Apply gateway and ingress
kubectl apply -f k8s/api-gateway-*.yaml
kubectl apply -f k8s/api-ingress-*.yaml

# Check deployment status
kubectl get deployments
kubectl get services
kubectl get pods
```

### 3. Verify the deployment

```bash
# Check all services are running
kubectl get pods -l app=user-service
kubectl get pods -l app=product-service
kubectl get pods -l app=order-service
kubectl get pods -l app=payment-service
kubectl get pods -l app=notification-service

# Test API gateway
kubectl port-forward service/api-gateway 8080:80
curl http://localhost:8080/api/users/health
curl http://localhost:8080/api/products/health
curl http://localhost:8080/api/orders/health
```

## Service Communication

### 1. Service Discovery

Services communicate using Kubernetes service names:

```python
# Service URLs
USER_SERVICE_URL = "http://user-service:3001"
PRODUCT_SERVICE_URL = "http://product-service:3002"
ORDER_SERVICE_URL = "http://order-service:3003"
PAYMENT_SERVICE_URL = "http://payment-service:3004"
NOTIFICATION_SERVICE_URL = "http://notification-service:3005"
```

### 2. Inter-Service Communication

```python
# Example: Order service calling user service
import requests

def get_user(user_id):
    response = requests.get(f"{USER_SERVICE_URL}/users/{user_id}")
    return response.json()

def get_product(product_id):
    response = requests.get(f"{PRODUCT_SERVICE_URL}/products/{product_id}")
    return response.json()

def process_payment(order_id, amount):
    response = requests.post(f"{PAYMENT_SERVICE_URL}/payments", {
        "order_id": order_id,
        "amount": amount
    })
    return response.json()
```

## Monitoring and Observability

### 1. Health Checks

```python
from celestra import Health

# Add health checks to all services
health = (Health("service-health")
    .liveness_probe("/health", 3000, 30, 10, 5, 3)
    .readiness_probe("/ready", 3000, 5, 5, 3, 1))

user_service.add_health(health)
product_service.add_health(health)
order_service.add_health(health)
payment_service.add_health(health)
notification_service.add_health(health)
```

### 2. Logging

```python
# Configure logging for all services
logging_config = (ConfigMap("logging-config")
    .add("logback.xml", """
<configuration>
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
        <encoder>
            <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
        </encoder>
    </appender>
    
    <root level="INFO">
        <appender-ref ref="STDOUT" />
    </root>
</configuration>""")
    .mount_as_file("/app/logback.xml"))

user_service.add_config(logging_config)
product_service.add_config(logging_config)
order_service.add_config(logging_config)
payment_service.add_config(logging_config)
notification_service.add_config(logging_config)
```

## Scaling

### 1. Horizontal Pod Autoscaling

```python
from celestra import Scaling

# Add HPA to all services
hpa = (Scaling("service-hpa")
    .target_cpu_utilization(70)
    .min_replicas(3)
    .max_replicas(10))

user_service.add_scaling(hpa)
product_service.add_scaling(hpa)
order_service.add_scaling(hpa)
payment_service.add_scaling(hpa)
notification_service.add_scaling(hpa)
```

### 2. Database Scaling

```python
# Scale databases based on usage
db_hpa = (Scaling("db-hpa")
    .target_cpu_utilization(60)
    .min_replicas(3)
    .max_replicas(5))

user_db.add_scaling(db_hpa)
product_db.add_scaling(db_hpa)
order_db.add_scaling(db_hpa)
```

## Security

### 1. Network Policies

```python
from celestra import NetworkPolicy

# Allow API gateway to access services
gateway_policy = (NetworkPolicy("gateway-policy")
    .policy_type("Ingress")
    .add_ingress_rule(
        from_pods={"app": "api-gateway"},
        ports=[{"port": 3001}, {"port": 3002}, {"port": 3003}, {"port": 3004}, {"port": 3005}]
    ))

# Allow services to access databases
db_policy = (NetworkPolicy("db-policy")
    .policy_type("Ingress")
    .add_ingress_rule(
        from_pods={"app": ["user-service", "product-service", "order-service"]},
        ports=[{"port": 5432}]
    ))
```

### 2. RBAC

```python
from celestra import ServiceAccount, Role, RoleBinding

# Create service accounts
user_sa = ServiceAccount("user-service-sa")
product_sa = ServiceAccount("product-service-sa")
order_sa = ServiceAccount("order-service-sa")

# Create roles
service_role = (Role("service-role")
    .add_rule(["get", "list", "watch"], ["pods", "services"])
    .add_rule(["get"], ["configmaps", "secrets"]))

# Bind roles to service accounts
user_binding = RoleBinding("user-service-binding").add_subject("ServiceAccount", "user-service-sa").add_role("service-role")
product_binding = RoleBinding("product-service-binding").add_subject("ServiceAccount", "product-service-sa").add_role("service-role")
order_binding = RoleBinding("order-service-binding").add_subject("ServiceAccount", "order-service-sa").add_role("service-role")
```

## Best Practices

### 1. **Service Independence**
```python
# ✅ Good: Each service has its own database
user_db = StatefulApp("user-db").storage("10Gi")
product_db = StatefulApp("product-db").storage("10Gi")

# ❌ Bad: Shared database
shared_db = StatefulApp("shared-db").storage("50Gi")
```

### 2. **Proper Resource Limits**
```python
# ✅ Good: Set appropriate resource limits
service = App("service").resources(cpu="200m", memory="256Mi")

# ❌ Bad: No resource limits
service = App("service")  # No resource limits
```

### 3. **Health Checks**
```python
# ✅ Good: Configure health checks
health = Health("health").liveness_probe("/health")
service.add_health(health)

# ❌ Bad: No health checks
service = App("service")  # No health checks
```

### 4. **Service Discovery**
```python
# ✅ Good: Use Kubernetes service names
USER_SERVICE_URL = "http://user-service:3001"

# ❌ Bad: Hardcode IP addresses
USER_SERVICE_URL = "http://10.0.0.1:3001"
```

## Next Steps

1. **[Observability Stack Tutorial](observability-stack.md)** - Add monitoring and tracing
2. **[Production Deployments](../examples/production/index.md)** - Learn about production configurations
3. **[Complex Platforms](../examples/complex/index.md)** - Advanced multi-service platforms

Ready to add monitoring and observability? Check out the [Observability Stack Tutorial](observability-stack.md)! 