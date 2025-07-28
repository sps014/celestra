# Ingress Component

The `Ingress` component provides HTTP and HTTPS routing to services within your cluster, acting as a smart load balancer with SSL termination, path-based routing, and host-based routing capabilities.

## Overview

Use `Ingress` for:
- **HTTP/HTTPS Routing** - External access to cluster services
- **SSL Termination** - TLS certificate management
- **Load Balancing** - Traffic distribution across pods
- **Virtual Hosting** - Multiple domains on one IP
- **Path-Based Routing** - Route by URL path

## Basic Usage

```python
from celestra import Ingress

# Simple HTTP ingress
ingress = (Ingress("web-ingress")
    .host("myapp.example.com")
    .path("/", "web-service", 80)
    .path("/api", "api-service", 8080))
```

## Configuration Methods

### Host-Based Routing

```python
# Single host
single_host = (Ingress("single-host")
    .host("app.example.com")
    .path("/", "frontend-service", 80)
    .path("/api", "backend-service", 8080)
    .path("/admin", "admin-service", 9000))

# Multiple hosts
multi_host = (Ingress("multi-host")
    .host("app.example.com")
    .path("/", "app-service", 80)
    .host("admin.example.com") 
    .path("/", "admin-service", 80)
    .host("api.example.com")
    .path("/", "api-service", 8080))
```

### Path-Based Routing

```python
# Different path types
path_routing = (Ingress("path-routing")
    .host("myapp.com")
    .path("/", "frontend", 80, path_type="Prefix")           # Default
    .path("/api/v1", "api-v1", 8080, path_type="Prefix")
    .path("/api/v2", "api-v2", 8080, path_type="Prefix")
    .path("/exact-match", "special", 80, path_type="Exact")
    .path("/health", "health", 8080, path_type="Exact"))
```

### HTTPS and TLS

```python
# HTTPS with TLS certificate
https_ingress = (Ingress("https-app")
    .host("secure.example.com")
    .tls("secure.example.com", "tls-secret")  # TLS certificate
    .path("/", "app-service", 80)
    .path("/api", "api-service", 8080))

# Multiple TLS certificates
multi_tls = (Ingress("multi-tls")
    .host("app.example.com")
    .tls("app.example.com", "app-tls-cert")
    .path("/", "app-service", 80)
    .host("api.example.com")
    .tls("api.example.com", "api-tls-cert")
    .path("/", "api-service", 8080))

# Wildcard certificate
wildcard_tls = (Ingress("wildcard")
    .host("app.example.com")
    .host("api.example.com") 
    .host("admin.example.com")
    .tls("*.example.com", "wildcard-cert")  # Covers all subdomains
    .path("/", "default-service", 80))
```

### Advanced Configuration

```python
# Advanced ingress with annotations
advanced_ingress = (Ingress("advanced-app")
    .host("myapp.example.com")
    .tls("myapp.example.com", "tls-cert")
    
    # Routing
    .path("/", "frontend", 80)
    .path("/api", "backend", 8080)
    .path("/static", "cdn", 80)
    
    # NGINX-specific annotations
    .add_annotation("nginx.ingress.kubernetes.io/rewrite-target", "/")
    .add_annotation("nginx.ingress.kubernetes.io/ssl-redirect", "true")
    .add_annotation("nginx.ingress.kubernetes.io/force-ssl-redirect", "true")
    .add_annotation("nginx.ingress.kubernetes.io/proxy-body-size", "50m")
    .add_annotation("nginx.ingress.kubernetes.io/proxy-read-timeout", "300")
    .add_annotation("nginx.ingress.kubernetes.io/rate-limit", "100")
    
    # CORS support
    .add_annotation("nginx.ingress.kubernetes.io/enable-cors", "true")
    .add_annotation("nginx.ingress.kubernetes.io/cors-allow-origin", "*")
    .add_annotation("nginx.ingress.kubernetes.io/cors-allow-methods", "GET, POST, PUT, DELETE")
    
    # Metadata
    .label("app", "myapp")
    .label("environment", "production")
    .annotation("cert-manager.io/cluster-issuer", "letsencrypt-prod"))
```

## Complete Examples

### Production Web Application

```python
#!/usr/bin/env python3
"""
Production Web Application with Ingress
"""

from celestra import App, Service, Ingress, Secret, KubernetesOutput

def create_web_application():
    # Frontend application
    frontend = (App("frontend")
        .image("myapp-frontend:v1.2.0")
        .port(80, "http")
        .replicas(3)
        .resources(cpu="200m", memory="256Mi")
        .label("app", "frontend")
        .label("tier", "presentation"))
    
    # Backend API
    backend = (App("backend-api")
        .image("myapp-backend:v1.2.0")
        .port(8080, "http")
        .replicas(3)
        .resources(cpu="500m", memory="1Gi")
        .label("app", "backend")
        .label("tier", "application"))
    
    # Admin interface
    admin = (App("admin-panel")
        .image("myapp-admin:v1.2.0")
        .port(3000, "http")
        .replicas(2)
        .resources(cpu="200m", memory="512Mi")
        .label("app", "admin")
        .label("tier", "management"))
    
    # Services
    frontend_service = (Service("frontend-service")
        .selector({"app": "frontend"})
        .add_port("http", 80, 80))
    
    backend_service = (Service("backend-service")
        .selector({"app": "backend"})
        .add_port("http", 8080, 8080))
    
    admin_service = (Service("admin-service")
        .selector({"app": "admin"})
        .add_port("http", 3000, 3000))
    
    # TLS certificate secret
    tls_secret = (Secret("app-tls-cert")
        .type("kubernetes.io/tls")
        .add_data("tls.crt", "-----BEGIN CERTIFICATE-----\n...")
        .add_data("tls.key", "-----BEGIN PRIVATE KEY-----\n..."))
    
    # Main application ingress
    app_ingress = (Ingress("app-ingress")
        # Main application
        .host("myapp.example.com")
        .tls("myapp.example.com", "app-tls-cert")
        .path("/", "frontend-service", 80)
        .path("/api", "backend-service", 8080)
        .path("/api/v1", "backend-service", 8080)
        
        # Admin panel
        .host("admin.myapp.example.com")
        .tls("admin.myapp.example.com", "app-tls-cert")
        .path("/", "admin-service", 3000)
        
        # NGINX configuration
        .add_annotation("nginx.ingress.kubernetes.io/ssl-redirect", "true")
        .add_annotation("nginx.ingress.kubernetes.io/proxy-body-size", "10m")
        .add_annotation("nginx.ingress.kubernetes.io/proxy-read-timeout", "60")
        .add_annotation("nginx.ingress.kubernetes.io/proxy-send-timeout", "60")
        
        # Security headers
        .add_annotation("nginx.ingress.kubernetes.io/configuration-snippet", """
            add_header X-Frame-Options "SAMEORIGIN" always;
            add_header X-Content-Type-Options "nosniff" always;
            add_header X-XSS-Protection "1; mode=block" always;
            add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        """)
        
        # Rate limiting
        .add_annotation("nginx.ingress.kubernetes.io/rate-limit", "100")
        .add_annotation("nginx.ingress.kubernetes.io/rate-limit-window", "1m")
        
        # Cert-manager for automatic SSL
        .add_annotation("cert-manager.io/cluster-issuer", "letsencrypt-prod")
        
        # Metadata
        .label("app", "myapp")
        .label("environment", "production")
        .annotation("description", "Main application ingress"))
    
    return (frontend, backend, admin, 
            frontend_service, backend_service, admin_service,
            tls_secret, app_ingress)

if __name__ == "__main__":
    components = create_web_application()
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "web-app-ingress/")
    
    print("✅ Web application with ingress generated!")
    print("🚀 Deploy: kubectl apply -f web-app-ingress/")
    print("🌐 Access: https://myapp.example.com")
    print("⚙️ Admin: https://admin.myapp.example.com")
```

### Microservices API Gateway

```python
def create_microservices_gateway():
    """Create ingress for microservices architecture"""
    
    # API Gateway ingress
    api_gateway = (Ingress("api-gateway")
        .host("api.mycompany.com")
        .tls("api.mycompany.com", "api-tls-cert")
        
        # User service
        .path("/api/v1/users", "user-service", 8080)
        .path("/api/v1/auth", "auth-service", 8080)
        
        # Order service  
        .path("/api/v1/orders", "order-service", 8080)
        .path("/api/v1/cart", "cart-service", 8080)
        
        # Payment service
        .path("/api/v1/payments", "payment-service", 8080)
        .path("/api/v1/billing", "billing-service", 8080)
        
        # Product service
        .path("/api/v1/products", "product-service", 8080)
        .path("/api/v1/catalog", "catalog-service", 8080)
        
        # Search service
        .path("/api/v1/search", "search-service", 8080)
        
        # Recommendations
        .path("/api/v1/recommendations", "recommendation-service", 8080)
        
        # API Gateway configuration
        .add_annotation("nginx.ingress.kubernetes.io/rewrite-target", "/$2")
        .add_annotation("nginx.ingress.kubernetes.io/use-regex", "true")
        .add_annotation("nginx.ingress.kubernetes.io/proxy-read-timeout", "300")
        .add_annotation("nginx.ingress.kubernetes.io/proxy-send-timeout", "300")
        
        # CORS for API
        .add_annotation("nginx.ingress.kubernetes.io/enable-cors", "true")
        .add_annotation("nginx.ingress.kubernetes.io/cors-allow-origin", "https://app.mycompany.com")
        .add_annotation("nginx.ingress.kubernetes.io/cors-allow-methods", "GET, POST, PUT, DELETE, OPTIONS")
        .add_annotation("nginx.ingress.kubernetes.io/cors-allow-headers", "Authorization, Content-Type")
        
        # Rate limiting per service
        .add_annotation("nginx.ingress.kubernetes.io/rate-limit", "1000")
        .add_annotation("nginx.ingress.kubernetes.io/rate-limit-window", "1m")
        
        # Authentication
        .add_annotation("nginx.ingress.kubernetes.io/auth-url", "http://auth-service.default.svc.cluster.local/auth")
        .add_annotation("nginx.ingress.kubernetes.io/auth-signin", "https://auth.mycompany.com/signin")
        
        # Labels
        .label("component", "api-gateway")
        .label("tier", "networking"))
    
    # Internal API ingress (cluster-only)
    internal_api = (Ingress("internal-api-gateway")
        .host("internal-api.mycompany.local")
        
        # Internal services
        .path("/internal/metrics", "prometheus", 9090)
        .path("/internal/health", "health-service", 8080)
        .path("/internal/admin", "admin-service", 9000)
        
        # Internal only - no TLS, no external access
        .add_annotation("kubernetes.io/ingress.class", "nginx-internal")
        .add_annotation("nginx.ingress.kubernetes.io/whitelist-source-range", "10.0.0.0/8,192.168.0.0/16")
        
        .label("component", "internal-gateway")
        .label("access", "internal"))
    
    return api_gateway, internal_api
```

### Development Environment

```python
def create_dev_ingress():
    """Create development environment ingress"""
    
    # Development ingress with multiple apps
    dev_ingress = (Ingress("dev-ingress")
        .host("dev.myapp.local")
        
        # Main app branches
        .path("/main", "app-main", 80)
        .path("/feature-auth", "app-feature-auth", 80)
        .path("/feature-ui", "app-feature-ui", 80)
        
        # API versions
        .path("/api/main", "api-main", 8080)
        .path("/api/v2", "api-v2", 8080)
        
        # Development tools
        .path("/docs", "docs-service", 3000)
        .path("/storybook", "storybook", 6006)
        .path("/grafana", "grafana", 3000)
        .path("/prometheus", "prometheus", 9090)
        
        # Development-specific annotations
        .add_annotation("nginx.ingress.kubernetes.io/rewrite-target", "/$2")
        .add_annotation("nginx.ingress.kubernetes.io/use-regex", "true")
        .add_annotation("nginx.ingress.kubernetes.io/proxy-read-timeout", "3600")  # Long timeout for debugging
        
        # Basic auth for development
        .add_annotation("nginx.ingress.kubernetes.io/auth-type", "basic")
        .add_annotation("nginx.ingress.kubernetes.io/auth-secret", "dev-basic-auth")
        .add_annotation("nginx.ingress.kubernetes.io/auth-realm", "Development Environment")
        
        # Labels
        .label("environment", "development")
        .label("access", "internal"))
    
    return dev_ingress
```

## Ingress Controllers

### NGINX Ingress Controller

```python
# NGINX-specific annotations
nginx_ingress = (Ingress("nginx-app")
    .host("app.example.com")
    .path("/", "app-service", 80)
    
    # Basic NGINX configuration
    .add_annotation("kubernetes.io/ingress.class", "nginx")
    .add_annotation("nginx.ingress.kubernetes.io/ssl-redirect", "true")
    .add_annotation("nginx.ingress.kubernetes.io/proxy-body-size", "50m")
    
    # Advanced NGINX features
    .add_annotation("nginx.ingress.kubernetes.io/server-snippet", """
        location /custom {
            return 301 https://example.com/redirect;
        }
    """)
    .add_annotation("nginx.ingress.kubernetes.io/configuration-snippet", """
        add_header X-Custom-Header "Custom Value" always;
    """))
```

### Traefik Ingress

```python
# Traefik-specific annotations
traefik_ingress = (Ingress("traefik-app")
    .host("app.example.com")
    .path("/", "app-service", 80)
    
    # Traefik configuration
    .add_annotation("kubernetes.io/ingress.class", "traefik")
    .add_annotation("traefik.ingress.kubernetes.io/router.tls", "true")
    .add_annotation("traefik.ingress.kubernetes.io/router.middlewares", "default-redirect-https@kubernetescrd"))
```

### AWS ALB Ingress

```python
# AWS Application Load Balancer
alb_ingress = (Ingress("alb-app")
    .host("app.example.com")
    .path("/", "app-service", 80)
    
    # ALB-specific annotations
    .add_annotation("kubernetes.io/ingress.class", "alb")
    .add_annotation("alb.ingress.kubernetes.io/scheme", "internet-facing")
    .add_annotation("alb.ingress.kubernetes.io/target-type", "ip")
    .add_annotation("alb.ingress.kubernetes.io/certificate-arn", "arn:aws:acm:us-west-2:123456789:certificate/abc-123")
    .add_annotation("alb.ingress.kubernetes.io/listen-ports", '[{"HTTP": 80}, {"HTTPS": 443}]')
    .add_annotation("alb.ingress.kubernetes.io/ssl-redirect", "443"))
```

## Generated YAML

### Basic Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

### HTTPS Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: https-app
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - secure.example.com
    secretName: tls-secret
  rules:
  - host: secure.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: app-service
            port:
              number: 80
```

## Best Practices

!!! tip "Ingress Best Practices"
    
    **Security:**
    - Always use HTTPS in production
    - Implement proper authentication and authorization
    - Use security headers (HSTS, CSP, etc.)
    - Implement rate limiting
    
    **Performance:**
    - Configure appropriate timeouts
    - Use connection pooling
    - Implement caching where appropriate
    - Monitor ingress controller performance
    
    **SSL/TLS:**
    - Use cert-manager for automatic certificate management
    - Implement proper certificate rotation
    - Use strong cipher suites
    - Enable HSTS headers
    
    **Routing:**
    - Use meaningful path prefixes
    - Implement health checks
    - Plan for maintenance and blue-green deployments
    - Document routing rules clearly

## Troubleshooting

### Common Ingress Issues

!!! warning "502/503 Errors"
    ```bash
    # Check ingress status
    kubectl get ingress
    kubectl describe ingress <ingress-name>
    
    # Check backend services
    kubectl get services
    kubectl get endpoints <service-name>
    
    # Check ingress controller logs
    kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
    ```

!!! warning "SSL Certificate Issues"
    ```bash
    # Check TLS secret
    kubectl get secret <tls-secret-name> -o yaml
    kubectl describe certificate <cert-name>  # If using cert-manager
    
    # Check cert-manager logs
    kubectl logs -n cert-manager deployment/cert-manager
    ```

!!! warning "DNS Resolution"
    ```bash
    # Test DNS resolution
    nslookup <hostname>
    dig <hostname>
    
    # Check from inside cluster
    kubectl run test-pod --image=busybox --rm -it -- nslookup <hostname>
    ```

### Debug Commands

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller

# Test ingress routing
curl -H "Host: myapp.example.com" http://<ingress-ip>/

# Check SSL certificate
openssl s_client -connect myapp.example.com:443 -servername myapp.example.com

# View ingress events
kubectl get events --field-selector involvedObject.name=<ingress-name>
```

## API Reference

::: src.celestra.networking.ingress.Ingress
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[Service](service.md)** - Backend services for ingress
- **[App](../core/app.md)** - Applications behind ingress
- **[Secret](../security/secrets.md)** - TLS certificates
- **[NetworkPolicy](network-policy.md)** - Network security

---

**Next:** Learn about [Scaling](scaling.md) for automatic pod scaling. 