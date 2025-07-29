# App Class

The `App` class represents stateless applications that can be horizontally scaled without persistent storage concerns. It's the primary component for deploying web applications, APIs, microservices, and other stateless workloads.

## Overview

```python
from celestra import App

# Basic usage
app = App("my-app").image("nginx:latest").port(8080).replicas(3)

# Production-ready application
app = (App("production-api")
    .image("myapp/api:v1.0")
    .port(8080)
    .replicas(5)
    .resources(cpu="500m", memory="1Gi")
    .env("NODE_ENV", "production")
    .expose())
```

## Core API Functions

### Container Configuration

#### Image
Set the container image for the application.

```python
app = App("web").image("nginx:1.21")
app = App("api").image("myapp:v2.1.0")
app = App("service").image("gcr.io/myproject/service:latest")
```

#### Build
Build container from local Dockerfile instead of using pre-built image.

```python
# Build from current directory
app = App("myapp").build(".", "Dockerfile", VERSION="1.0")

# Build from subdirectory with custom Dockerfile
app = App("backend").build("./backend", "Dockerfile.dev", ENV="development")
```

#### From Dockerfile
Use a custom Dockerfile for building the container.

```python
# Use custom Dockerfile
app = App("api").from_dockerfile("Dockerfile.prod", ".", ENV="production")

# Multi-stage build
app = App("optimized").from_dockerfile("Dockerfile.multi", ".", TARGET="production")
```

#### Command
Set the command to run in the container.

```python
app = App("api").image("node:16").command(["npm", "start"])
app = App("worker").image("python:3.9").command(["python", "worker.py"])
```

#### Arguments
Set the arguments for the container command.

```python
app = App("api").image("myapp:latest").args(["--port", "8080", "--env", "prod"])
```

### Port Configuration

#### Port
Add a port to the application.

```python
# Basic HTTP port
app = App("web").port(8080, "http")

# Multiple ports
app = (App("api")
    .port(8080, "http")
    .port(8443, "https")
    .port(9090, "metrics"))

# Custom protocol
app = App("dns").port(53, "dns", "UDP")
```

#### Add Port
Add a port to the application (alias for port()).

```python
# Add multiple ports
app = (App("multi-service")
    .add_port(8080, "http")
    .add_port(8443, "https")
    .add_port(9090, "metrics"))
```

#### Ports
Add multiple ports at once.

```python
# Bulk port configuration
ports_config = [
    {"port": 8080, "name": "http"},
    {"port": 8443, "name": "https"},
    {"port": 9090, "name": "metrics"}
]
app = App("api").ports(ports_config)
```

### Convenience Port Methods

#### HTTP Port
```python
app = App("web").http_port(8080)
```

#### HTTPS Port
```python
app = App("secure").https_port(8443)
```

#### Metrics Port
```python
app = App("monitored").metrics_port(9090)
```

#### Health Port
```python
app = App("healthy").health_port(8081)
```

#### Admin Port
```python
app = App("managed").admin_port(9000)
```

#### GRPC Port
```python
app = App("grpc-service").grpc_port(9090)
```

#### Debug Port
```python
app = App("debuggable").debug_port(5005)
```

#### Common Ports
Add standard ports for web applications.

```python
# Standard web app ports
app = App("web-app").common_ports()

# Custom ports
app = App("api").common_ports(http=3000, metrics=9090, health=8081)
```

### Environment Configuration

#### Environment
Set multiple environment variables at once.

```python
# Bulk environment variables
env_config = {
    "NODE_ENV": "production",
    "DATABASE_URL": "postgres://user:pass@db:5432/myapp",
    "REDIS_URL": "redis://redis:6379",
    "LOG_LEVEL": "info"
}
app = App("api").environment(env_config)
```

#### Environment Variable
Add a single environment variable.

```python
# Single environment variable
app = App("api").env("DEBUG", "true")

# Multiple individual variables
app = (App("web")
    .env("NODE_ENV", "production")
    .env("PORT", "3000")
    .env("API_URL", "https://api.example.com"))
```

#### Environment from Secret
Load environment variables from a Secret.

```python
app = App("api").env_from_secret("db-secret")
app = App("api").env_from_secret("api-keys", optional=True)
```

#### Environment from ConfigMap
Load environment variables from a ConfigMap.

```python
app = App("api").env_from_config_map("app-config")
app = App("api").env_from_config_map("feature-flags", optional=True)
```

### Resource Management

#### Resources
Set resource requests and limits for the application.

```python
# Basic resources
app = App("web").resources(cpu="100m", memory="128Mi")

# With limits
app = (App("api")
    .resources(
        cpu="500m", 
        memory="1Gi",
        cpu_limit="1000m",
        memory_limit="2Gi"
    ))

# GPU-enabled
app = App("ml").resources(cpu="2", memory="8Gi", gpu=1)
```

#### Replicas
Set the number of replicas for the application.

```python
# Single instance
app = App("dev").replicas(1)

# Production scaling
app = App("prod").replicas(5)

# High availability
app = App("critical").replicas(10)
```

#### Scale
Configure horizontal pod autoscaling.

```python
# Basic autoscaling
app = App("api").scale(min_replicas=2, max_replicas=10)

# With CPU target
app = App("api").scale(min_replicas=2, max_replicas=10, target_cpu_utilization=70)
```

### Dependencies and Connections

#### Depends On
Set service dependencies for deployment ordering.

```python
# Single dependency
app = App("api").depends_on(["database"])

# Multiple dependencies
app = App("web").depends_on(["api", "cache", "database"])

# With external configuration
app = App("worker").depends_on(["postgres", "redis", "kafka"])
```

#### connect_to(services: List[str]) -> App
Establish connections to other services.

```python
# Connect to database and cache
app = App("api").connect_to(["postgres", "redis"])

# Connect to external services
app = App("payment").connect_to(["stripe-api", "webhook-service"])
```

### Container Management

#### add_companion(companion: Companion) -> App
Add sidecar or init containers.

```python
# Logging sidecar
app = (App("api")
    .add_companion(
        Companion("log-collector")
            .image("fluentd:latest")
            .type("sidecar")
            .mount_shared_volume("/var/log")
    ))

# Database migration init container
app = (App("api")
    .add_companion(
        Companion("db-migration")
            .image("migrator:latest")
            .type("init")
            .command(["python", "migrate.py"])
    ))
```

#### add_companions(companions: List[Companion]) -> App
Add multiple companion containers.

```python
# Multiple sidecars
sidecars = [
    Companion("log-collector").image("fluentd:latest").type("sidecar"),
    Companion("metrics-collector").image("prometheus:latest").type("sidecar")
]
app = App("api").add_companions(sidecars)
```

### Configuration Management

#### add_secret(secret: Secret) -> App
Add a secret to the application.

```python
# Add database secret
db_secret = Secret("db-secret").add("password", "secret123")
app = App("api").add_secret(db_secret)

# Add API key secret
api_secret = Secret("api-keys").add("stripe_key", "sk_live_...")
app = App("payment").add_secret(api_secret)
```

#### add_secrets(secrets: List[Secret]) -> App
Add multiple secrets to the application.

```python
# Multiple secrets
secrets = [
    Secret("db-secret").add("password", "secret123"),
    Secret("api-keys").add("stripe_key", "sk_live_..."),
    Secret("tls-cert").from_file("cert.pem")
]
app = App("api").add_secrets(secrets)
```

#### add_config(config_map: ConfigMap) -> App
Add a ConfigMap to the application.

```python
# Add application config
app_config = ConfigMap("app-config").add_data("config.json", '{"debug": true}')
app = App("api").add_config(app_config)

# Add nginx config
nginx_config = ConfigMap("nginx-config").add_data("nginx.conf", nginx_conf_content)
app = App("web").add_config(nginx_config)
```

#### add_configs(config_maps: List[ConfigMap]) -> App
Add multiple ConfigMaps to the application.

```python
# Multiple configs
configs = [
    ConfigMap("app-config").add("debug", "false"),
    ConfigMap("feature-flags").add("new_ui", "true"),
    ConfigMap("nginx-config").from_file("nginx.conf")
]
app = App("api").add_configs(configs)
```

### Health Checks and Probes

#### health_check(path: str, port: int = None, initial_delay: int = 30, period: int = 10) -> App
Add a health check endpoint.

```python
app = App("api").health_check("/health")
app = App("api").health_check("/ready", port=8081, initial_delay=60)
```

#### liveness_probe(path: str, port: int = None, initial_delay: int = 30, period: int = 10, timeout: int = 5, failure_threshold: int = 3) -> App
Configure liveness probe.

```python
app = App("api").liveness_probe("/health")
app = App("api").liveness_probe("/alive", port=8081, initial_delay=60)
```

#### readiness_probe(path: str, port: int = None, initial_delay: int = 5, period: int = 5, timeout: int = 3, failure_threshold: int = 3) -> App
Configure readiness probe.

```python
app = App("api").readiness_probe("/ready")
app = App("api").readiness_probe("/health", port=8081, initial_delay=10)
```

#### startup_probe(path: str, port: int = None, initial_delay: int = 30, period: int = 10, timeout: int = 5, failure_threshold: int = 30) -> App
Configure startup probe.

```python
app = App("api").startup_probe("/startup")
app = App("api").startup_probe("/init", port=8081, initial_delay=60)
```

### Security and RBAC

#### add_service_account(service_account: ServiceAccount) -> App
Add a service account to the application.

```python
sa = ServiceAccount("api-sa")
app = App("api").add_service_account(sa)
```

#### add_role(role: Role) -> App
Add a role to the application.

```python
role = Role("api-role").add_policy("get", "pods").add_policy("list", "services")
app = App("api").add_role(role)
```

#### add_network_policy(network_policy: NetworkPolicy) -> App
Add a network policy to the application.

```python
policy = NetworkPolicy("api-policy").allow_pods_with_label("app", "api")
app = App("api").add_network_policy(policy)
```

#### add_security_policy(security_policy: SecurityPolicy) -> App
Add a security policy to the application.

```python
policy = SecurityPolicy("restricted").pod_security_standards("restricted")
app = App("api").add_security_policy(policy)
```

### Deployment Strategy

#### deployment_strategy(strategy: str, **kwargs) -> App
Configure deployment strategy.

```python
# Rolling update (default)
app = App("api").deployment_strategy("rolling")

# Blue-green deployment
app = App("api").deployment_strategy("blue-green", health_check="/health")

# Canary deployment
app = App("api").deployment_strategy("canary", percentage=10)
```

#### rolling_update(max_surge: int = 1, max_unavailable: int = 0, min_ready_seconds: int = 0) -> App
Configure rolling update strategy.

```python
app = App("api").rolling_update(max_surge=1, max_unavailable=0)
app = App("api").rolling_update(max_surge=2, max_unavailable=1, min_ready_seconds=30)
```

#### blue_green_deployment(health_check: str = None, rollback_on_failure: bool = True) -> App
Configure blue-green deployment.

```python
app = App("api").blue_green_deployment(health_check="/health")
app = App("api").blue_green_deployment(rollback_on_failure=True)
```

#### canary_deployment(percentage: int = 10, promotion_criteria: str = None) -> App
Configure canary deployment.

```python
app = App("api").canary_deployment(percentage=10)
app = App("api").canary_deployment(percentage=20, promotion_criteria="success_rate > 95%")
```

### Networking and Exposure

#### expose(external: bool = False, ingress: bool = False) -> App
Expose the application via Service and optionally Ingress.

```python
# Internal service only
app = App("api").expose()

# External service
app = App("web").expose(external=True)

# With ingress
app = App("web").expose(external=True, ingress=True)
```

#### add_service(service: Service) -> App
Add a custom service configuration.

```python
service = Service("api-service").type("LoadBalancer")
app = App("api").add_service(service)
```

#### add_ingress(ingress: Ingress) -> App
Add an ingress configuration.

```python
ingress = Ingress("api-ingress").route("/api", "api-service")
app = App("api").add_ingress(ingress)
```

### Observability

#### add_observability(observability: Observability) -> App
Add observability configuration.

```python
obs = Observability("monitoring").enable_metrics().enable_logging()
app = App("api").add_observability(obs)
```

#### enable_metrics(port: int = 9090) -> App
Enable metrics collection.

```python
app = App("api").enable_metrics(port=9090)
```

#### enable_logging(log_format: str = "json") -> App
Enable structured logging.

```python
app = App("api").enable_logging(log_format="json")
```

#### enable_tracing(tracing_backend: str = "jaeger") -> App
Enable distributed tracing.

```python
app = App("api").enable_tracing(tracing_backend="jaeger")
```

### Advanced Configuration

#### namespace(namespace: str) -> App
Set the namespace for the application.

```python
app = App("api").namespace("production")
app = App("api").namespace("staging")
```

#### add_label(key: str, value: str) -> App
Add a label to the application.

```python
app = App("api").add_label("environment", "production")
app = App("api").add_label("team", "platform")
```

#### add_labels(labels: Dict[str, str]) -> App
Add multiple labels to the application.

```python
labels = {
    "environment": "production",
    "team": "platform",
    "version": "v1.0"
}
app = App("api").add_labels(labels)
```

#### add_annotation(key: str, value: str) -> App
Add an annotation to the application.

```python
app = App("api").add_annotation("description", "API service")
app = App("api").add_annotation("owner", "platform-team")
```

#### add_annotations(annotations: Dict[str, str]) -> App
Add multiple annotations to the application.

```python
annotations = {
    "description": "API service",
    "owner": "platform-team",
    "documentation": "https://docs.example.com/api"
}
app = App("api").add_annotations(annotations)
```

#### node_selector(selector: Dict[str, str]) -> App
Set node selector for pod placement.

```python
app = App("api").node_selector({"node-type": "compute"})
app = App("api").node_selector({"zone": "us-west-1"})
```

#### tolerations(tolerations: List[Dict[str, Any]]) -> App
Set tolerations for pod scheduling.

```python
tolerations = [{"key": "dedicated", "operator": "Equal", "value": "api", "effect": "NoSchedule"}]
app = App("api").tolerations(tolerations)
```

#### affinity(affinity: Dict[str, Any]) -> App
Set pod affinity rules.

```python
affinity = {
    "podAntiAffinity": {
        "preferredDuringSchedulingIgnoredDuringExecution": [{
            "weight": 100,
            "podAffinityTerm": {
                "labelSelector": {"matchExpressions": [{"key": "app", "operator": "In", "values": ["api"]}]},
                "topologyKey": "kubernetes.io/hostname"
            }
        }]
    }
}
app = App("api").affinity(affinity)
```

### Lifecycle Hooks

#### add_lifecycle(lifecycle: Lifecycle) -> App
Add lifecycle hooks to the application.

```python
lifecycle = Lifecycle("api-lifecycle")
lifecycle.pre_stop_command(["python", "cleanup.py"])
app = App("api").add_lifecycle(lifecycle)
```

#### pre_stop_command(command: List[str]) -> App
Add pre-stop command.

```python
app = App("api").pre_stop_command(["python", "cleanup.py"])
```

#### post_start_command(command: List[str]) -> App
Add post-start command.

```python
app = App("api").post_start_command(["python", "init.py"])
```

### Validation and Cost Optimization

#### add_validator(validator: Validator) -> App
Add validation to the application.

```python
validator = Validator("api-validator")
validator.security_scan()
validator.cost_optimization()
app = App("api").add_validator(validator)
```

#### add_cost_optimizer(optimizer: CostOptimization) -> App
Add cost optimization to the application.

```python
optimizer = CostOptimization("api-optimizer")
optimizer.resource_optimization()
optimizer.spot_instance_recommendation()
app = App("api").add_cost_optimizer(optimizer)
```

### Output Generation

#### generate() -> AppGenerator
Generate the application configuration.

```python
# Generate Kubernetes YAML
app.generate().to_yaml("./k8s/")

# Generate Docker Compose
app.generate().to_docker_compose("./docker-compose.yml")

# Generate Helm Chart
app.generate().to_helm_chart("./charts/")

# Generate Kustomize
app.generate().to_kustomize("./kustomize/")
```

## Complete Example

Here's a complete example of a production-ready API application:

```python
from celestra import App, Secret, ConfigMap, ServiceAccount, Role, NetworkPolicy

# Create secrets
db_secret = Secret("db-secret").add("password", "secure-password")
api_secret = Secret("api-secret").add("jwt_secret", "jwt-secret-key")

# Create configuration
app_config = ConfigMap("api-config").add("debug", "false").add("log_level", "info")

# Create service account and role
sa = ServiceAccount("api-sa")
role = Role("api-role").add_policy("get", "pods").add_policy("list", "services")

# Create network policy
network_policy = NetworkPolicy("api-policy").allow_pods_with_label("app", "api")

# Create the application
api = (App("api-service")
    .image("myapp/api:v1.0")
    .port(8080)
    .replicas(5)
    .resources(cpu="500m", memory="1Gi", cpu_limit="1000m", memory_limit="2Gi")
    .env("NODE_ENV", "production")
    .env("PORT", "8080")
    .health_check("/health")
    .liveness_probe("/health")
    .readiness_probe("/ready")
    .add_secret(db_secret)
    .add_secret(api_secret)
    .add_config(app_config)
    .add_service_account(sa)
    .add_role(role)
    .add_network_policy(network_policy)
    .rolling_update(max_surge=1, max_unavailable=0)
    .expose(external=True))

# Generate manifests
api.generate().to_yaml("./k8s/")
```

## Best Practices

### 1. **Resource Management**
```python
# ✅ Good: Set appropriate resources
app = App("api").resources(cpu="500m", memory="1Gi", cpu_limit="1000m", memory_limit="2Gi")

# ❌ Bad: No resource limits
app = App("api")  # No resource limits
```

### 2. **Health Checks**
```python
# ✅ Good: Comprehensive health checks
app = (App("api")
    .health_check("/health")
    .liveness_probe("/health")
    .readiness_probe("/ready"))

# ❌ Bad: No health checks
app = App("api")  # No health checks
```

### 3. **Security**
```python
# ✅ Good: Use service accounts and RBAC
sa = ServiceAccount("api-sa")
role = Role("api-role").add_policy("get", "pods")
app = App("api").add_service_account(sa).add_role(role)

# ❌ Bad: No security configuration
app = App("api")  # No security
```

### 4. **Environment Variables**
```python
# ✅ Good: Use ConfigMaps and Secrets
config = ConfigMap("app-config").add("debug", "false")
secret = Secret("api-secret").add("password", "secret")
app = App("api").add_config(config).add_secret(secret)

# ❌ Bad: Hardcode in code
app = App("api").env("PASSWORD", "hardcoded-password")
```

### 5. **Scaling**
```python
# ✅ Good: Configure autoscaling
app = App("api").scale(min_replicas=2, max_replicas=10, target_cpu_utilization=70)

# ❌ Bad: Fixed replicas only
app = App("api").replicas(3)  # No autoscaling
```

## Related Components

- **[StatefulApp](stateful-app.md)** - For stateful applications with persistent storage
- **[Job](../workloads/job.md)** - For batch processing workloads
- **[CronJob](../workloads/cron-job.md)** - For scheduled batch jobs
- **[Secret](../security/secrets.md)** - For managing sensitive data
- **[ConfigMap](../storage/config-map.md)** - For managing configuration data
- **[ServiceAccount](../security/service-account.md)** - For RBAC identity
- **[Role](../security/role.md)** - For access control policies

## Next Steps

- **[StatefulApp](stateful-app.md)** - Learn about stateful applications
- **[Components Overview](index.md)** - Explore all available components
- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides 