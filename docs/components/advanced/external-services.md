# ExternalServices Class

The `ExternalServices` class manages external service integrations in Kubernetes. It provides capabilities for connecting to external APIs, databases, message queues, and other services outside the cluster.

## Overview

```python
from celestra import ExternalServices

# Basic external service
external = ExternalServices("api-gateway").endpoint("https://api.example.com").timeout(30)

# Production external service with authentication
external = (ExternalServices("production-api")
    .endpoint("https://api.production.com")
    .authentication("bearer", "token")
    .timeout(60)
    .retry_policy(3, 5))
```

## Core API Functions

### Service Configuration

#### Endpoint
Set the external service endpoint.

```python
# HTTP endpoint
external = ExternalServices("api-service").endpoint("https://api.example.com")

# HTTPS endpoint
external = ExternalServices("secure-api").endpoint("https://secure-api.example.com")

# Internal service endpoint
external = ExternalServices("internal-api").endpoint("http://internal-service:8080")
```

#### Service Type
Set the external service type.

```python
# API service
external = ExternalServices("api-service").service_type("api")

# Database service
external = ExternalServices("db-service").service_type("database")

# Message queue service
external = ExternalServices("mq-service").service_type("message_queue")

# Cache service
external = ExternalServices("cache-service").service_type("cache")
```

#### Protocol
Set the communication protocol.

```python
# HTTP protocol
external = ExternalServices("api-service").protocol("http")

# HTTPS protocol
external = ExternalServices("secure-api").protocol("https")

# gRPC protocol
external = ExternalServices("grpc-service").protocol("grpc")

# WebSocket protocol
external = ExternalServices("ws-service").protocol("websocket")
```

### Authentication

#### Authentication Method
Set authentication method and credentials.

```python
# Bearer token authentication
external = ExternalServices("api-service").authentication("bearer", "your-token")

# Basic authentication
external = ExternalServices("api-service").authentication("basic", "username:password")

# API key authentication
external = ExternalServices("api-service").authentication("apikey", "your-api-key")

# OAuth2 authentication
external = ExternalServices("api-service").authentication("oauth2", "client-id:client-secret")
```

#### Bearer Token
Set bearer token authentication.

```python
external = ExternalServices("api-service").bearer_token("your-bearer-token")
```

#### API Key
Set API key authentication.

```python
external = ExternalServices("api-service").api_key("your-api-key")
```

#### Basic Auth
Set basic authentication.

```python
external = ExternalServices("api-service").basic_auth("username", "password")
```

#### OAuth2 Client
Set OAuth2 client credentials.

```python
external = ExternalServices("api-service").oauth2_client("client-id", "client-secret")
```

### Connection Configuration

#### Timeout
Set connection timeout.

```python
# 30 second timeout
external = ExternalServices("api-service").timeout(30)

# 60 second timeout for slow services
external = ExternalServices("slow-api").timeout(60)
```

#### Connection Timeout
Set connection establishment timeout.

```python
# 10 second connection timeout
external = ExternalServices("api-service").connection_timeout(10)
```

#### Read Timeout
Set read timeout.

```python
# 30 second read timeout
external = ExternalServices("api-service").read_timeout(30)
```

#### Write Timeout
Set write timeout.

```python
# 10 second write timeout
external = ExternalServices("api-service").write_timeout(10)
```

#### Keep Alive
Enable or disable keep-alive connections.

```python
# Enable keep-alive
external = ExternalServices("api-service").keep_alive(True)

# Disable keep-alive
external = ExternalServices("api-service").keep_alive(False)
```

#### Max Connections
Set maximum number of connections.

```python
# 100 maximum connections
external = ExternalServices("api-service").max_connections(100)

# 1000 maximum connections for high traffic
external = ExternalServices("high-traffic-api").max_connections(1000)
```

### Retry Configuration

#### Retry Policy
Set retry policy.

```python
# 3 retries with 5 second backoff
external = ExternalServices("api-service").retry_policy(3, 5)

# 5 retries with 10 second backoff
external = ExternalServices("unreliable-api").retry_policy(5, 10)
```

#### Max Retries
Set maximum number of retries.

```python
external = ExternalServices("api-service").max_retries(3)
```

#### Retry Backoff
Set retry backoff in seconds.

```python
external = ExternalServices("api-service").retry_backoff(5)
```

#### Retry on Status Codes
Set status codes to retry on.

```python
# Retry on 5xx errors
external = ExternalServices("api-service").retry_on_status_codes([500, 502, 503, 504])

# Retry on 4xx and 5xx errors
external = ExternalServices("api-service").retry_on_status_codes([429, 500, 502, 503, 504])
```

### Circuit Breaker Configuration

#### circuit_breaker(enabled: bool = True) -> ExternalServices
Enable or disable circuit breaker.

```python
# Enable circuit breaker
external = ExternalServices("api-service").circuit_breaker(True)

# Disable circuit breaker
external = ExternalServices("critical-api").circuit_breaker(False)
```

#### circuit_breaker_threshold(threshold: int) -> ExternalServices
Set circuit breaker failure threshold.

```python
# 5 failures to open circuit
external = ExternalServices("api-service").circuit_breaker_threshold(5)
```

#### circuit_breaker_timeout(seconds: int) -> ExternalServices
Set circuit breaker timeout.

```python
# 60 second circuit breaker timeout
external = ExternalServices("api-service").circuit_breaker_timeout(60)
```

#### circuit_breaker_half_open_requests(requests: int) -> ExternalServices
Set number of requests to allow in half-open state.

```python
# Allow 3 requests in half-open state
external = ExternalServices("api-service").circuit_breaker_half_open_requests(3)
```

### Load Balancing

#### load_balancer(type: str) -> ExternalServices
Set load balancer type.

```python
# Round-robin load balancer
external = ExternalServices("api-service").load_balancer("round_robin")

# Least connections load balancer
external = ExternalServices("api-service").load_balancer("least_connections")

# Weighted load balancer
external = ExternalServices("api-service").load_balancer("weighted")
```

#### add_endpoint(url: str, weight: int = 1) -> ExternalServices
Add endpoint to load balancer.

```python
# Add primary endpoint
external = ExternalServices("api-service").add_endpoint("https://api1.example.com", 2)

# Add secondary endpoint
external = ExternalServices("api-service").add_endpoint("https://api2.example.com", 1)
```

#### health_check_endpoint(path: str) -> ExternalServices
Set health check endpoint for load balancer.

```python
external = ExternalServices("api-service").health_check_endpoint("/health")
```

### Rate Limiting

#### rate_limit(requests_per_second: int) -> ExternalServices
Set rate limit.

```python
# 100 requests per second
external = ExternalServices("api-service").rate_limit(100)

# 1000 requests per second for high traffic
external = ExternalServices("high-traffic-api").rate_limit(1000)
```

#### burst_limit(burst: int) -> ExternalServices
Set burst limit.

```python
# Allow burst of 50 requests
external = ExternalServices("api-service").burst_limit(50)
```

#### rate_limit_window(seconds: int) -> ExternalServices
Set rate limit window.

```python
# 1 second rate limit window
external = ExternalServices("api-service").rate_limit_window(1)

# 60 second rate limit window
external = ExternalServices("api-service").rate_limit_window(60)
```

### Security Configuration

#### tls_enabled(enabled: bool = True) -> ExternalServices
Enable or disable TLS.

```python
# Enable TLS
external = ExternalServices("secure-api").tls_enabled(True)

# Disable TLS for internal services
external = ExternalServices("internal-api").tls_enabled(False)
```

#### tls_verify(enabled: bool = True) -> ExternalServices
Enable or disable TLS certificate verification.

```python
# Verify TLS certificates
external = ExternalServices("secure-api").tls_verify(True)

# Skip TLS verification for self-signed certificates
external = ExternalServices("internal-api").tls_verify(False)
```

#### tls_ca_cert(cert_path: str) -> ExternalServices
Set CA certificate path.

```python
external = ExternalServices("secure-api").tls_ca_cert("/etc/ssl/certs/ca-certificates.crt")
```

#### tls_client_cert(cert_path: str) -> ExternalServices
Set client certificate path.

```python
external = ExternalServices("secure-api").tls_client_cert("/etc/ssl/certs/client.crt")
```

#### tls_client_key(key_path: str) -> ExternalServices
Set client key path.

```python
external = ExternalServices("secure-api").tls_client_key("/etc/ssl/private/client.key")
```

### Monitoring and Observability

#### enable_metrics(enabled: bool = True) -> ExternalServices
Enable or disable metrics collection.

```python
# Enable metrics
external = ExternalServices("api-service").enable_metrics(True)

# Disable metrics
external = ExternalServices("api-service").enable_metrics(False)
```

#### metrics_port(port: int) -> ExternalServices
Set metrics port.

```python
external = ExternalServices("api-service").metrics_port(9090)
```

#### enable_tracing(enabled: bool = True) -> ExternalServices
Enable or disable distributed tracing.

```python
# Enable tracing
external = ExternalServices("api-service").enable_tracing(True)

# Disable tracing
external = ExternalServices("api-service").enable_tracing(False)
```

#### tracing_sampler(sampler: str) -> ExternalServices
Set tracing sampler.

```python
# Always sample
external = ExternalServices("api-service").tracing_sampler("always")

# Probabilistic sampling
external = ExternalServices("api-service").tracing_sampler("probabilistic")
```

#### tracing_sampling_rate(rate: float) -> ExternalServices
Set tracing sampling rate.

```python
# 10% sampling rate
external = ExternalServices("api-service").tracing_sampling_rate(0.1)

# 100% sampling rate
external = ExternalServices("api-service").tracing_sampling_rate(1.0)
```

### Advanced Configuration

#### namespace(namespace: str) -> ExternalServices
Set the namespace for the external service.

```python
external = ExternalServices("api-service").namespace("production")
```

#### add_label(key: str, value: str) -> ExternalServices
Add a label to the external service.

```python
external = ExternalServices("api-service").add_label("environment", "production")
```

#### add_labels(labels: Dict[str, str]) -> ExternalServices
Add multiple labels to the external service.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "tier": "external"
}
external = ExternalServices("api-service").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> ExternalServices
Add an annotation to the external service.

```python
external = ExternalServices("api-service").add_annotation("description", "External API service")
```

#### add_annotations(annotations: Dict[str, str]) -> ExternalServices
Add multiple annotations to the external service.

```python
annotations = {
    "description": "External API service for production",
    "owner": "platform-team",
    "service-type": "api-gateway"
}
external = ExternalServices("api-service").add_annotations(annotations)
```

#### service_mesh(enabled: bool = True) -> ExternalServices
Enable or disable service mesh integration.

```python
# Enable service mesh
external = ExternalServices("api-service").service_mesh(True)

# Disable service mesh
external = ExternalServices("api-service").service_mesh(False)
```

#### service_mesh_type(type: str) -> ExternalServices
Set service mesh type.

```python
# Istio service mesh
external = ExternalServices("api-service").service_mesh_type("istio")

# Linkerd service mesh
external = ExternalServices("api-service").service_mesh_type("linkerd")
```

### Output Generation

#### generate() -> ExternalServicesGenerator
Generate the external service configuration.

```python
# Generate Kubernetes YAML
external.generate().to_yaml("./k8s/")

# Generate Helm values
external.generate().to_helm_values("./helm/")

# Generate Terraform
external.generate().to_terraform("./terraform/")
```

## Complete Example

Here's a complete example of a production-ready external service configuration:

```python
from celestra import ExternalServices

# Create comprehensive external service configuration
production_external = (ExternalServices("production-api")
    .endpoint("https://api.production.com")
    .service_type("api")
    .protocol("https")
    .authentication("bearer", "production-token")
    .timeout(60)
    .connection_timeout(10)
    .read_timeout(30)
    .write_timeout(10)
    .keep_alive(True)
    .max_connections(1000)
    .retry_policy(3, 5)
    .retry_on_status_codes([500, 502, 503, 504])
    .circuit_breaker(True)
    .circuit_breaker_threshold(5)
    .circuit_breaker_timeout(60)
    .circuit_breaker_half_open_requests(3)
    .load_balancer("round_robin")
    .add_endpoint("https://api1.production.com", 2)
    .add_endpoint("https://api2.production.com", 1)
    .health_check_endpoint("/health")
    .rate_limit(1000)
    .burst_limit(100)
    .rate_limit_window(1)
    .tls_enabled(True)
    .tls_verify(True)
    .tls_ca_cert("/etc/ssl/certs/ca-certificates.crt")
    .enable_metrics(True)
    .metrics_port(9090)
    .enable_tracing(True)
    .tracing_sampler("probabilistic")
    .tracing_sampling_rate(0.1)
    .service_mesh(True)
    .service_mesh_type("istio")
    .namespace("production")
    .add_labels({
        "environment": "production",
        "team": "platform",
        "tier": "external"
    })
    .add_annotations({
        "description": "Production external API service",
        "owner": "platform-team@company.com",
        "service-type": "api-gateway"
    }))

# Generate manifests
production_external.generate().to_yaml("./k8s/")
```

## External Service Patterns

### API Gateway Pattern
```python
# API gateway pattern
api_gateway = (ExternalServices("api-gateway")
    .endpoint("https://gateway.example.com")
    .service_type("api")
    .protocol("https")
    .authentication("bearer", "gateway-token")
    .timeout(30)
    .retry_policy(3, 5)
    .rate_limit(1000)
    .load_balancer("round_robin"))
```

### Database Connection Pattern
```python
# Database connection pattern
db_connection = (ExternalServices("database")
    .endpoint("postgresql://db.example.com:5432")
    .service_type("database")
    .protocol("postgresql")
    .authentication("basic", "user:password")
    .timeout(60)
    .max_connections(100)
    .circuit_breaker(True)
    .circuit_breaker_threshold(3))
```

### Message Queue Pattern
```python
# Message queue pattern
mq_connection = (ExternalServices("message-queue")
    .endpoint("amqp://mq.example.com:5672")
    .service_type("message_queue")
    .protocol("amqp")
    .authentication("basic", "user:password")
    .timeout(30)
    .max_connections(50)
    .retry_policy(5, 10))
```

### Cache Service Pattern
```python
# Cache service pattern
cache_service = (ExternalServices("cache")
    .endpoint("redis://cache.example.com:6379")
    .service_type("cache")
    .protocol("redis")
    .timeout(10)
    .max_connections(200)
    .keep_alive(True))
```

### Microservice Pattern
```python
# Microservice pattern
microservice = (ExternalServices("user-service")
    .endpoint("https://user-service.example.com")
    .service_type("api")
    .protocol("https")
    .authentication("bearer", "service-token")
    .timeout(30)
    .retry_policy(3, 5)
    .circuit_breaker(True)
    .rate_limit(500)
    .enable_metrics(True)
    .enable_tracing(True))
```

## Best Practices

### 1. **Use Appropriate Timeouts**
```python
# ✅ Good: Set appropriate timeouts
external = ExternalServices("api-service").timeout(30).connection_timeout(10)

# ❌ Bad: No timeouts
external = ExternalServices("api-service")  # No timeouts
```

### 2. **Implement Circuit Breakers**
```python
# ✅ Good: Use circuit breakers for resilience
external = ExternalServices("api-service").circuit_breaker(True).circuit_breaker_threshold(5)

# ❌ Bad: No circuit breaker
external = ExternalServices("api-service")  # No circuit breaker
```

### 3. **Use Retry Policies**
```python
# ✅ Good: Use retry policies
external = ExternalServices("api-service").retry_policy(3, 5)

# ❌ Bad: No retry policy
external = ExternalServices("api-service")  # No retry policy
```

### 4. **Enable TLS for Security**
```python
# ✅ Good: Enable TLS for security
external = ExternalServices("api-service").tls_enabled(True).tls_verify(True)

# ❌ Bad: No TLS
external = ExternalServices("api-service")  # No TLS
```

### 5. **Use Rate Limiting**
```python
# ✅ Good: Use rate limiting
external = ExternalServices("api-service").rate_limit(1000).burst_limit(100)

# ❌ Bad: No rate limiting
external = ExternalServices("api-service")  # No rate limiting
```

### 6. **Enable Monitoring**
```python
# ✅ Good: Enable monitoring
external = ExternalServices("api-service").enable_metrics(True).enable_tracing(True)

# ❌ Bad: No monitoring
external = ExternalServices("api-service")  # No monitoring
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[Service](../networking/service.md)** - For service discovery
- **[Ingress](../networking/ingress.md)** - For external access
- **[Observability](observability.md)** - For monitoring and metrics

## Next Steps

- **[CustomResource](custom-resource.md)** - Learn about custom Kubernetes resources
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 