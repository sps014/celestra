# Ingress Class

The `Ingress` class manages external access to services by creating Kubernetes Ingress resources. It provides HTTP/HTTPS routing, SSL termination, and load balancing for web applications.

## Overview

```python
from celestra import Ingress

# Basic usage
ingress = Ingress("web-ingress").route("/", "web-service")

# Production ingress with TLS
ingress = (Ingress("api-ingress")
    .route("/api", "api-service")
    .route("/docs", "docs-service")
    .tls("api.example.com", "tls-secret")
    .annotations({"nginx.ingress.kubernetes.io/ssl-redirect": "true"}))
```

## Core API Functions

### Route Configuration

#### Adding Routes
Add a route to the ingress.

```python
# Basic route
ingress = Ingress("web-ingress").route("/", "web-service")

# Route with custom port
ingress = Ingress("api-ingress").route("/api", "api-service", 8080)

# Multiple routes
ingress = (Ingress("multi-ingress")
    .route("/", "web-service")
    .route("/api", "api-service", 8080)
    .route("/docs", "docs-service", 3000))
```

#### Alternative Route Method
Add a route to the ingress (alias for route()).

```python
ingress = Ingress("api-ingress").add_route("/api", "api-service", 8080)
```

#### Bulk Route Configuration
Add multiple routes at once.

```python
# Bulk route configuration
routes_config = [
    {"path": "/", "service": "web-service", "port": 80},
    {"path": "/api", "service": "api-service", "port": 8080},
    {"path": "/docs", "service": "docs-service", "port": 3000}
]
ingress = Ingress("multi-ingress").routes(routes_config)
```

### Host Configuration

#### Single Hostname
Set the hostname for the ingress.

```python
ingress = Ingress("api-ingress").host("api.example.com")
```

#### Multiple Hostnames
Set multiple hostnames for the ingress.

```python
ingress = Ingress("multi-host-ingress").hosts(["api.example.com", "www.example.com"])
```

### TLS Configuration

#### TLS Setup
Configure TLS for the ingress.

```python
ingress = Ingress("secure-ingress").tls("api.example.com", "tls-secret")
```

#### Multiple TLS Hosts
Configure TLS for multiple hostnames.

```python
ingress = Ingress("multi-tls-ingress").tls_multiple(
    ["api.example.com", "www.example.com"], 
    "tls-secret"
)
```

#### TLS Redirect
Enable TLS redirect.

```python
ingress = Ingress("secure-ingress").tls_redirect(True)
```

#### TLS Termination Types
Configure TLS termination type.

```python
# Edge termination (default)
ingress = Ingress("api-ingress").tls_termination("edge")

# Passthrough termination
ingress = Ingress("api-ingress").tls_termination("passthrough")

# Re-encrypt termination
ingress = Ingress("api-ingress").tls_termination("reencrypt")
```

### Path Configuration

#### Path Type
Set the path type for routes.

```python
# Exact match
ingress = Ingress("api-ingress").path_type("Exact")

# Prefix match (default)
ingress = Ingress("api-ingress").path_type("Prefix")

# Implementation specific
ingress = Ingress("api-ingress").path_type("ImplementationSpecific")
```

#### Exact Path
Add an exact path match.

```python
ingress = Ingress("api-ingress").exact_path("/api/v1", "api-v1-service")
```

#### Prefix Path
Add a prefix path match.

```python
ingress = Ingress("api-ingress").prefix_path("/api", "api-service")
```

#### Regex Path
Add a regex path match.

```python
ingress = Ingress("api-ingress").regex_path("/api/v[0-9]+", "api-service")
```

### Load Balancing

#### Load Balancer Method
Set the load balancer method.

```python
# Round robin (default)
ingress = Ingress("api-ingress").load_balancer_method("round_robin")

# Least connections
ingress = Ingress("api-ingress").load_balancer_method("least_conn")

# IP hash
ingress = Ingress("api-ingress").load_balancer_method("ip_hash")
```

#### Session Affinity
Configure session affinity.

```python
# Cookie-based affinity
ingress = Ingress("api-ingress").session_affinity("cookie")

# IP-based affinity
ingress = Ingress("api-ingress").session_affinity("ip")
```

#### Sticky Sessions
Enable sticky sessions.

```python
# Enable sticky sessions
ingress = Ingress("api-ingress").sticky_sessions(True)

# Enable with custom cookie name
ingress = Ingress("api-ingress").sticky_sessions(True, "sessionid")
```

### Rate Limiting

#### Rate Limit
Configure rate limiting.

```python
ingress = Ingress("api-ingress").rate_limit(100)
```

#### Rate Limit Burst
Configure rate limit burst size.

```python
ingress = Ingress("api-ingress").rate_limit_burst(200)
```

#### Rate Limit by IP
Enable IP-based rate limiting.

```python
ingress = Ingress("api-ingress").rate_limit_by_ip(True)
```

### Security

#### CORS
Configure CORS.

```python
# Basic CORS
ingress = Ingress("api-ingress").cors()

# Custom CORS
ingress = Ingress("api-ingress").cors(
    origins=["https://example.com", "https://www.example.com"],
    methods=["GET", "POST", "PUT", "DELETE"],
    headers=["Authorization", "Content-Type"]
)
```

#### Basic Auth
Configure basic authentication.

```python
ingress = Ingress("protected-ingress").basic_auth("auth-secret")
```

#### OAuth2
Configure OAuth2 authentication.

```python
ingress = Ingress("oauth-ingress").oauth2("google", "client-id", "client-secret")
```

#### IP Whitelist
Configure IP whitelist.

```python
ingress = Ingress("restricted-ingress").ip_whitelist(["203.0.113.0/24", "10.0.0.0/8"])
```

#### IP Blacklist
Configure IP blacklist.

```python
ingress = Ingress("protected-ingress").ip_blacklist(["192.168.1.100", "10.0.0.50"])
```

### Annotations

#### Annotation
Add an annotation to the ingress.

```python
ingress = Ingress("api-ingress").annotation("nginx.ingress.kubernetes.io/ssl-redirect", "true")
```

#### Annotations
Add multiple annotations to the ingress.

```python
annotations = {
    "nginx.ingress.kubernetes.io/ssl-redirect": "true",
    "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
    "nginx.ingress.kubernetes.io/proxy-body-size": "8m"
}
ingress = Ingress("api-ingress").annotations(annotations)
```

### Nginx-Specific Annotations

#### Nginx SSL Redirect
Enable SSL redirect for Nginx.

```python
ingress = Ingress("api-ingress").nginx_ssl_redirect(True)
```

#### Nginx Force SSL Redirect
Force SSL redirect for Nginx.

```python
ingress = Ingress("api-ingress").nginx_force_ssl_redirect(True)
```

#### Nginx Proxy Body Size
Set proxy body size for Nginx.

```python
ingress = Ingress("api-ingress").nginx_proxy_body_size("8m")
```

#### Nginx Proxy Connect Timeout
Set proxy connect timeout for Nginx.

```python
ingress = Ingress("api-ingress").nginx_proxy_connect_timeout("60s")
```

#### Nginx Proxy Read Timeout
Set proxy read timeout for Nginx.

```python
ingress = Ingress("api-ingress").nginx_proxy_read_timeout("60s")
```

#### Nginx Proxy Send Timeout
Set proxy send timeout for Nginx.

```python
ingress = Ingress("api-ingress").nginx_proxy_send_timeout("60s")
```

### AWS ALB-Specific Annotations

#### ALB SSL Policy
Set SSL policy for AWS ALB.

```python
ingress = Ingress("api-ingress").alb_ssl_policy("ELBSecurityPolicy-TLS-1-2-2017-01")
```

#### ALB Target Type
Set target type for AWS ALB.

```python
# IP target type
ingress = Ingress("api-ingress").alb_target_type("ip")

# Instance target type
ingress = Ingress("api-ingress").alb_target_type("instance")
```

#### ALB Scheme
Set scheme for AWS ALB.

```python
# Internet-facing
ingress = Ingress("api-ingress").alb_scheme("internet-facing")

# Internal
ingress = Ingress("api-ingress").alb_scheme("internal")
```

### GCP GCE-Specific Annotations

#### GCE SSL Certificate
Set SSL certificate for GCP GCE.

```python
ingress = Ingress("api-ingress").gce_ssl_certificate("my-ssl-cert")
```

#### GCE Backend Config
Set backend config for GCP GCE.

```python
ingress = Ingress("api-ingress").gce_backend_config("my-backend-config")
```

### Azure AGIC-Specific Annotations

#### AGIC SSL Certificate
Set SSL certificate for Azure AGIC.

```python
ingress = Ingress("api-ingress").agic_ssl_certificate("my-ssl-cert")
```

#### AGIC Backend Pool
Set backend pool for Azure AGIC.

```python
ingress = Ingress("api-ingress").agic_backend_pool("my-backend-pool")
```

### Advanced Configuration

#### Namespace
Set the namespace for the ingress.

```python
ingress = Ingress("api-ingress").namespace("production")
```

#### Add Label
Add a label to the ingress.

```python
ingress = Ingress("api-ingress").add_label("environment", "production")
```

#### Add Labels
Add multiple labels to the ingress.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "frontend"
}
ingress = Ingress("api-ingress").add_labels(labels)
```

#### Ingress Class
Set the ingress class.

```python
ingress = Ingress("api-ingress").ingress_class("nginx")
ingress = Ingress("api-ingress").ingress_class("alb")
ingress = Ingress("api-ingress").ingress_class("gce")
```

#### Default Backend
Set the default backend service.

```python
ingress = Ingress("api-ingress").default_backend("default-service", 8080)
```

### Health Checks

#### Health Check Path
Set health check path.

```python
ingress = Ingress("api-ingress").health_check_path("/health")
```

#### Health Check Interval
Set health check interval.

```python
ingress = Ingress("api-ingress").health_check_interval("30s")
```

#### Health Check Timeout
Set health check timeout.

```python
ingress = Ingress("api-ingress").health_check_timeout("5s")
```

### Output Generation

#### Generate Configuration
Generate the ingress configuration.

```python
# Generate Kubernetes YAML
ingress.generate().to_yaml("./k8s/")

# Generate Helm values
ingress.generate().to_helm_values("./helm/")

# Generate Terraform
ingress.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready API ingress:

```python
from celestra import Ingress

# Create comprehensive API ingress
api_ingress = (Ingress("api-ingress")
    .host("api.example.com")
    .route("/", "api-service", 8080)
    .route("/v1", "api-v1-service", 8080)
    .route("/v2", "api-v2-service", 8080)
    .route("/docs", "docs-service", 3000)
    .tls("api.example.com", "tls-secret")
    .tls_redirect(True)
    .load_balancer_method("least_conn")
    .sticky_sessions(True, "sessionid")
    .rate_limit(100)
    .rate_limit_burst(200)
    .cors(
        origins=["https://example.com", "https://www.example.com"],
        methods=["GET", "POST", "PUT", "DELETE"],
        headers=["Authorization", "Content-Type"]
    )
    .ip_whitelist(["203.0.113.0/24", "10.0.0.0/8"])
    .annotations({
        "nginx.ingress.kubernetes.io/ssl-redirect": "true",
        "nginx.ingress.kubernetes.io/force-ssl-redirect": "true",
        "nginx.ingress.kubernetes.io/proxy-body-size": "8m",
        "nginx.ingress.kubernetes.io/proxy-connect-timeout": "60s",
        "nginx.ingress.kubernetes.io/proxy-read-timeout": "60s",
        "nginx.ingress.kubernetes.io/proxy-send-timeout": "60s"
    })
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "frontend"
    })
    .ingress_class("nginx")
    .health_check_path("/health"))

# Generate manifests
api_ingress.generate().to_yaml("./k8s/")
```

## Ingress Controllers and Use Cases

### Nginx Ingress Controller
```python
# Nginx ingress with SSL
nginx_ingress = (Ingress("web-ingress")
    .host("example.com")
    .route("/", "web-service")
    .tls("example.com", "tls-secret")
    .nginx_ssl_redirect(True)
    .nginx_proxy_body_size("8m")
    .ingress_class("nginx"))
```

### AWS ALB Ingress Controller
```python
# AWS ALB ingress
alb_ingress = (Ingress("api-ingress")
    .host("api.example.com")
    .route("/api", "api-service")
    .tls("api.example.com", "tls-secret")
    .alb_ssl_policy("ELBSecurityPolicy-TLS-1-2-2017-01")
    .alb_target_type("ip")
    .alb_scheme("internet-facing")
    .ingress_class("alb"))
```

### GCP GCE Ingress Controller
```python
# GCP GCE ingress
gce_ingress = (Ingress("api-ingress")
    .host("api.example.com")
    .route("/api", "api-service")
    .tls("api.example.com", "tls-secret")
    .gce_ssl_certificate("my-ssl-cert")
    .gce_backend_config("my-backend-config")
    .ingress_class("gce"))
```

### Azure AGIC Ingress Controller
```python
# Azure AGIC ingress
agic_ingress = (Ingress("api-ingress")
    .host("api.example.com")
    .route("/api", "api-service")
    .tls("api.example.com", "tls-secret")
    .agic_ssl_certificate("my-ssl-cert")
    .agic_backend_pool("my-backend-pool")
    .ingress_class("azure/application-gateway"))
```

## Best Practices

### 1. **Use Appropriate Ingress Class**
```python
# ✅ Good: Use appropriate ingress class for your environment
ingress = Ingress("api-ingress").ingress_class("nginx")  # For Nginx
ingress = Ingress("api-ingress").ingress_class("alb")    # For AWS ALB
ingress = Ingress("api-ingress").ingress_class("gce")    # For GCP GCE

# ❌ Bad: Use wrong ingress class
ingress = Ingress("api-ingress").ingress_class("nginx")  # On AWS without Nginx
```

### 2. **Configure TLS Properly**
```python
# ✅ Good: Configure TLS with proper secret
ingress = Ingress("api-ingress").tls("api.example.com", "tls-secret")

# ❌ Bad: No TLS configuration
ingress = Ingress("api-ingress")  # No TLS
```

### 3. **Use Rate Limiting**
```python
# ✅ Good: Configure rate limiting
ingress = Ingress("api-ingress").rate_limit(100).rate_limit_burst(200)

# ❌ Bad: No rate limiting
ingress = Ingress("api-ingress")  # No rate limiting
```

### 4. **Configure CORS**
```python
# ✅ Good: Configure CORS for web applications
ingress = Ingress("api-ingress").cors(
    origins=["https://example.com"],
    methods=["GET", "POST"],
    headers=["Authorization"]
)

# ❌ Bad: No CORS configuration
ingress = Ingress("api-ingress")  # No CORS
```

### 5. **Use IP Whitelisting**
```python
# ✅ Good: Restrict access to specific IPs
ingress = Ingress("api-ingress").ip_whitelist(["203.0.113.0/24"])

# ❌ Bad: Allow access from anywhere
ingress = Ingress("api-ingress")  # No IP restrictions
```

### 6. **Configure Health Checks**
```python
# ✅ Good: Configure health checks
ingress = Ingress("api-ingress").health_check_path("/health")

# ❌ Bad: No health checks
ingress = Ingress("api-ingress")  # No health checks
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Service](service.md)** - For internal service discovery
- **[NetworkPolicy](network-policy.md)** - For network security policies
- **[Secret](../security/secrets.md)** - For TLS certificates

## Next Steps

- **[Service](service.md)** - Learn about internal service discovery
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 