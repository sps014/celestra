# Service Component

The `Service` component provides stable network endpoints for your applications, enabling service discovery and load balancing in Kubernetes clusters.

## Overview

Services provide:
- **Stable IP addresses** - Even when pods restart
- **Load balancing** - Traffic distribution across pods
- **Service discovery** - DNS-based service location
- **Port mapping** - External to internal port translation

## Service Types

| Type | Use Case | Access |
|------|----------|---------|
| **ClusterIP** | Internal communication | Cluster-only |
| **NodePort** | External access via nodes | Node IP + Port |
| **LoadBalancer** | Cloud load balancer | External IP |
| **ExternalName** | Alias to external service | DNS CNAME |

## Basic Usage

```python
from src.k8s_gen import Service

# Basic ClusterIP service
service = (Service("api-service")
    .selector({"app": "api"})
    .add_port("http", 80, 8080)
    .type("ClusterIP"))
```

## Service Configuration

### Port Mapping

```python
# Single port
service = (Service("web-service")
    .add_port("http", 80, 8080))

# Multiple ports
service = (Service("api-service")
    .add_port("http", 80, 8080)
    .add_port("https", 443, 8443)
    .add_port("metrics", 9090, 9090)
    .add_port("admin", 9000, 9000))

# Different protocols
service = (Service("database-service")
    .add_port("postgres", 5432, 5432, "TCP")
    .add_port("metrics", 9187, 9187, "TCP"))
```

### Selectors and Targeting

```python
# Target specific pods
service = (Service("backend-service")
    .selector({"app": "backend", "version": "v2"})
    .add_port("api", 8080, 8080))

# Target multiple applications
service = (Service("microservices")
    .selector({"tier": "backend"})
    .add_port("http", 80, 8080))

# No selector (manual endpoints)
service = (Service("external-db")
    .add_port("postgres", 5432, 5432)
    .no_selector())  # Manage endpoints manually
```

### Service Types

```python
# ClusterIP (default)
internal_service = (Service("internal-api")
    .type("ClusterIP")
    .cluster_ip("10.0.0.100")  # Specific IP
    .selector({"app": "api"})
    .add_port("http", 8080, 8080))

# NodePort
nodeport_service = (Service("public-web")
    .type("NodePort") 
    .node_port(30080)  # Specific node port
    .selector({"app": "web"})
    .add_port("http", 80, 8080))

# LoadBalancer
lb_service = (Service("external-api")
    .type("LoadBalancer")
    .load_balancer_ip("203.0.113.10")
    .selector({"app": "api"})
    .add_port("http", 80, 8080)
    .add_port("https", 443, 8443))

# ExternalName
external_service = (Service("external-db")
    .type("ExternalName")
    .external_name("db.example.com"))
```

## Advanced Configuration

### Session Affinity

```python
# Sticky sessions
service = (Service("stateful-app")
    .selector({"app": "stateful"})
    .session_affinity("ClientIP")
    .session_affinity_timeout(10800)  # 3 hours
    .add_port("http", 8080, 8080))
```

### Load Balancer Configuration

```python
# Cloud provider specific
aws_service = (Service("aws-lb")
    .type("LoadBalancer")
    .selector({"app": "web"})
    .add_port("http", 80, 8080)
    .add_annotation("service.beta.kubernetes.io/aws-load-balancer-type", "nlb")
    .add_annotation("service.beta.kubernetes.io/aws-load-balancer-scheme", "internet-facing"))

gcp_service = (Service("gcp-lb")
    .type("LoadBalancer")
    .selector({"app": "api"})
    .add_port("http", 80, 8080)
    .add_annotation("cloud.google.com/load-balancer-type", "External"))
```

### Headless Services

```python
# For StatefulSets
headless_service = (Service("postgres-headless")
    .cluster_ip("None")  # Headless
    .selector({"app": "postgres"})
    .add_port("postgres", 5432, 5432))
```

## Complete Examples

### Web Application Service

```python
#!/usr/bin/env python3
"""
Web Application with Multiple Service Types
"""

from src.k8s_gen import App, Service, KubernetesOutput

def create_web_services():
    # Web application
    web_app = (App("web-app")
        .image("nginx:1.21")
        .port(80, "http")
        .port(443, "https")
        .replicas(3)
        .label("app", "web")
        .label("tier", "frontend"))
    
    # Internal service for cluster communication
    internal_service = (Service("web-internal")
        .type("ClusterIP")
        .selector({"app": "web"})
        .add_port("http", 80, 80)
        .add_port("https", 443, 443)
        .label("service-type", "internal"))
    
    # External service for public access
    external_service = (Service("web-external")
        .type("LoadBalancer")
        .selector({"app": "web"})
        .add_port("http", 80, 80)
        .add_port("https", 443, 443)
        .load_balancer_source_ranges(["10.0.0.0/8", "192.168.0.0/16"])
        .add_annotation("service.beta.kubernetes.io/aws-load-balancer-ssl-cert", "arn:aws:acm:...")
        .label("service-type", "external"))
    
    # Development service with NodePort
    dev_service = (Service("web-dev")
        .type("NodePort")
        .selector({"app": "web"})
        .add_port("http", 80, 80)
        .node_port(30080)
        .label("environment", "development"))
    
    return web_app, internal_service, external_service, dev_service

if __name__ == "__main__":
    components = create_web_services()
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "web-services/")
    
    print("✅ Web services generated!")
    print("🚀 Deploy: kubectl apply -f web-services/")
```

### Database Service Setup

```python
def create_database_services():
    # PostgreSQL StatefulSet
    postgres = (StatefulApp("postgres")
        .image("postgres:13")
        .port(5432, "postgres")
        .replicas(3)
        .storage("/var/lib/postgresql/data", "100Gi")
        .label("app", "postgres")
        .label("component", "database"))
    
    # Headless service for StatefulSet
    postgres_headless = (Service("postgres-headless")
        .cluster_ip("None")
        .selector({"app": "postgres"})
        .add_port("postgres", 5432, 5432)
        .label("service-type", "headless"))
    
    # Primary service (points to leader)
    postgres_primary = (Service("postgres-primary")
        .selector({"app": "postgres", "role": "primary"})
        .add_port("postgres", 5432, 5432)
        .label("service-type", "primary"))
    
    # Read-only service (points to replicas)
    postgres_read = (Service("postgres-read")
        .selector({"app": "postgres", "role": "replica"})
        .add_port("postgres", 5432, 5432)
        .label("service-type", "read-replica"))
    
    # Admin service for management tools
    postgres_admin = (Service("postgres-admin")
        .type("NodePort")
        .selector({"app": "postgres"})
        .add_port("postgres", 5432, 5432)
        .node_port(30432)
        .label("service-type", "admin"))
    
    return postgres, postgres_headless, postgres_primary, postgres_read, postgres_admin
```

### Microservices Communication

```python
def create_microservices_network():
    # User service
    user_service = (Service("user-service")
        .selector({"app": "user-service"})
        .add_port("http", 80, 8080)
        .add_port("grpc", 9090, 9090))
    
    # Order service
    order_service = (Service("order-service")
        .selector({"app": "order-service"})
        .add_port("http", 80, 8080)
        .add_port("grpc", 9090, 9090))
    
    # Payment service
    payment_service = (Service("payment-service")
        .selector({"app": "payment-service"})
        .add_port("http", 80, 8080)
        .add_port("grpc", 9090, 9090))
    
    # API Gateway (external access)
    api_gateway = (Service("api-gateway")
        .type("LoadBalancer")
        .selector({"app": "api-gateway"})
        .add_port("http", 80, 8080)
        .add_port("https", 443, 8443)
        .session_affinity("ClientIP"))
    
    return user_service, order_service, payment_service, api_gateway
```

## Service Discovery

### DNS Names

Services are automatically assigned DNS names:

```python
# Service: my-service in namespace: my-namespace
# DNS names:
# - my-service (same namespace)
# - my-service.my-namespace
# - my-service.my-namespace.svc.cluster.local
```

### Environment Variables

Kubernetes injects service information as environment variables:

```bash
# For service "database-service" on port 5432
DATABASE_SERVICE_SERVICE_HOST=10.0.0.100
DATABASE_SERVICE_SERVICE_PORT=5432
DATABASE_SERVICE_PORT_5432_TCP_ADDR=10.0.0.100
DATABASE_SERVICE_PORT_5432_TCP_PORT=5432
```

## Generated YAML

### ClusterIP Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api-service
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
  - name: http
    port: 80
    targetPort: 8080
    protocol: TCP
```

### LoadBalancer Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-external
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-type: nlb
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - name: http
    port: 80
    targetPort: 80
  - name: https
    port: 443
    targetPort: 443
  loadBalancerSourceRanges:
  - 10.0.0.0/8
  - 192.168.0.0/16
```

## Best Practices

!!! tip "Service Design Guidelines"
    
    **Naming:**
    - Use descriptive, consistent names
    - Include service type or purpose
    - Follow organizational naming conventions
    
    **Port Management:**
    - Use named ports for clarity
    - Keep port mappings consistent
    - Document port purposes
    
    **Security:**
    - Limit LoadBalancer source ranges
    - Use appropriate service types
    - Consider network policies
    
    **Performance:**
    - Use session affinity when needed
    - Monitor service endpoints
    - Consider headless services for StatefulSets

## Common Patterns

### Blue-Green Deployment

```python
# Blue environment
blue_service = (Service("app-blue")
    .selector({"app": "myapp", "version": "blue"})
    .add_port("http", 80, 8080))

# Green environment
green_service = (Service("app-green")
    .selector({"app": "myapp", "version": "green"})
    .add_port("http", 80, 8080))

# Production service (switch between blue/green)
prod_service = (Service("app-production")
    .selector({"app": "myapp", "version": "blue"})  # Currently blue
    .add_port("http", 80, 8080))
```

### Canary Deployment

```python
# Stable version (90% traffic)
stable_service = (Service("app-stable")
    .selector({"app": "myapp", "version": "stable"})
    .add_port("http", 80, 8080))

# Canary version (10% traffic)
canary_service = (Service("app-canary")
    .selector({"app": "myapp", "version": "canary"})
    .add_port("http", 80, 8080))
```

## Troubleshooting

### Common Service Issues

!!! warning "Service Not Accessible"
    ```bash
    # Check service endpoints
    kubectl get endpoints my-service
    
    # Verify pod labels match service selector
    kubectl get pods --show-labels
    kubectl describe service my-service
    
    # Test service connectivity
    kubectl run test-pod --image=busybox --rm -it -- nslookup my-service
    ```

!!! warning "LoadBalancer Pending"
    ```bash
    # Check cloud provider integration
    kubectl describe service my-lb-service
    
    # Verify cloud provider permissions
    kubectl get events --field-selector involvedObject.name=my-lb-service
    ```

### Debug Commands

```bash
# Check service status
kubectl get services
kubectl describe service <service-name>

# Test service resolution
kubectl run debug --image=busybox --rm -it -- sh
# Inside pod:
nslookup service-name
wget -qO- http://service-name:port/

# Check endpoints
kubectl get endpoints <service-name>

# View service events
kubectl get events --field-selector involvedObject.name=<service-name>
```

## API Reference

::: src.celestra.networking.service.Service
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[App](../core/app.md)** - Applications that services expose
- **[Ingress](ingress.md)** - HTTP/HTTPS routing to services
- **[NetworkPolicy](network-policy.md)** - Network security
- **[StatefulApp](../core/stateful-app.md)** - Services for stateful apps

---

**Next:** Learn about [Ingress](ingress.md) for HTTP/HTTPS routing and external access. 