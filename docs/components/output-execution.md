# Output Execution API

Celestra provides powerful execution capabilities that allow you to not only generate configuration files but also run them directly. This enables a seamless workflow from DSL definition to actual deployment.

## Overview

The execution API extends the existing output classes with methods to run the generated configurations:

- **Docker Compose Execution** - Run `docker-compose` commands directly
- **Kubernetes Execution** - Run `kubectl` commands directly
- **Method Chaining** - Fluent API for seamless execution workflows
- **Automatic File Tracking** - Remember last generated files for seamless execution

## Docker Compose Execution

The `DockerComposeOutput` class now includes execution methods that allow you to run Docker Compose commands directly after generation.

### Basic Usage

```python
from celestra import App, DockerComposeOutput

# Define your application
app = App("web-app").image("nginx:latest").port(8080)

# Create output instance
output = DockerComposeOutput()

# Generate and run in one workflow
output.generate(app, "docker-compose.yml").up(detached=True)
```

### Execution Methods

#### Core Execution

| Method | Description | Example |
|--------|-------------|---------|
| `run(command, **options)` | Generic command runner | `output.run("up", detached=True)` |
| `up(**options)` | Start services | `output.up(detached=True, build=True)` |
| `down(**options)` | Stop services | `output.down(volumes=True)` |
| `start(service, **options)` | Start specific service | `output.start("web-app")` |
| `stop(service, **options)` | Stop specific service | `output.stop("web-app")` |
| `restart(service, **options)` | Restart service | `output.restart("web-app")` |

#### Monitoring & Debugging

| Method | Description | Example |
|--------|-------------|---------|
| `logs(service, **options)` | Show service logs | `output.logs("web-app", follow=True)` |
| `ps(**options)` | Show service status | `output.ps()` |
| `exec(service, command, **options)` | Execute command in container | `output.exec("web-app", "bash")` |

#### Build Operations

| Method | Description | Example |
|--------|-------------|---------|
| `build(**options)` | Build service images | `output.build(no_cache=True)` |
| `pull(**options)` | Pull service images | `output.pull()` |

#### Configuration

| Method | Description | Example |
|--------|-------------|---------|
| `config(**options)` | Validate configuration | `output.config()` |
| `validate(**options)` | Validate and show config | `output.validate()` |

### Advanced Usage Examples

#### Multi-Service Application with Execution

```python
from celestra import App, AppGroup, DockerComposeOutput

# Define services
web = App("web").image("nginx:latest").port(80)
api = App("api").image("myapp/api:latest").port(3000)
db = App("db").image("postgres:13").port(5432)

# Create app group
app_group = AppGroup("myapp").add_services([web, api, db])

# Generate and run
output = DockerComposeOutput()
output.generate(app_group, "docker-compose.yml")

# Start all services
output.up(detached=True)

# Check status
output.ps()

# Show logs for specific service
output.logs("api")

# Scale a service
output.scale({"api": 3})

# Stop and clean up
output.down(volumes=True)
```

#### Development Workflow

```python
from celestra import App, DockerComposeOutput

app = App("dev-app").image("myapp:dev").port(8080)

output = DockerComposeOutput()

# Development workflow
(output
    .generate(app, "docker-compose.dev.yml")
    .build()                    # Build the image
    .up(detached=True)          # Start in background
    .logs(follow=True))         # Follow logs
```

## Kubernetes Execution

The `KubernetesOutput` class provides execution methods for running `kubectl` commands directly.

### Basic Usage

```python
from celestra import App, KubernetesOutput

# Define your application
app = App("web-app").image("nginx:latest").port(8080)

# Create output instance
output = KubernetesOutput()

# Generate and deploy
output.generate(app, "./manifests/").apply()
```

### Execution Methods

#### Core Deployment

| Method | Description | Example |
|--------|-------------|---------|
| `run(command, **options)` | Generic kubectl runner | `output.run("apply", namespace="prod")` |
| `apply(**options)` | Apply manifests | `output.apply(wait=True)` |
| `delete(**options)` | Delete resources | `output.delete(grace_period=30)` |
| `replace(**options)` | Replace resources | `output.replace(force=True)` |
| `patch(**options)` | Patch resources | `output.patch(patch_type="strategic")` |

#### Resource Management

| Method | Description | Example |
|--------|-------------|---------|
| `get(resource_type, **options)` | Get resources | `output.get("pods", namespace="default")` |
| `describe(resource_type, **options)` | Describe resources | `output.describe("deployment", "web-app")` |
| `edit(resource_type, **options)` | Edit resources | `output.edit("deployment", "web-app")` |

#### Monitoring & Debugging

| Method | Description | Example |
|--------|-------------|---------|
| `logs(pod, **options)` | Show pod logs | `output.logs("web-app-pod-123")` |
| `exec(pod, command, **options)` | Execute command in pod | `output.exec("web-app-pod-123", "bash")` |
| `port_forward(service, local_port, target_port, **options)` | Port forward service | `output.port_forward("web-app", 8080, 80)` |

#### Scaling & Operations

| Method | Description | Example |
|--------|-------------|---------|
| `scale(deployment, replicas, **options)` | Scale deployment | `output.scale("web-app", 5)` |
| `rollout(action, deployment, **options)` | Manage rollouts | `output.rollout("restart", "web-app")` |

#### Status & Health

| Method | Description | Example |
|--------|-------------|---------|
| `status(**options)` | Show cluster status | `output.status()` |
| `health(**options)` | Check resource health | `output.health()` |
| `events(**options)` | Show cluster events | `output.events()` |

#### Validation

| Method | Description | Example |
|--------|-------------|---------|
| `validate(**options)` | Validate manifests | `output.validate()` |
| `diff(**options)` | Show differences | `output.diff()` |

### Advanced Usage Examples

#### Production Deployment Workflow

```python
from celestra import App, AppGroup, KubernetesOutput

# Define production application
web = App("web-prod").image("myapp:v1.0.0").port(80).replicas(3)
api = App("api-prod").image("myapi:v1.0.0").port(3000).replicas(2)
db = App("db-prod").image("postgres:13").port(5432).replicas(1)

app_group = AppGroup("production").add_services([web, api, db])

# Production deployment workflow
output = KubernetesOutput()

(output
    .generate(app_group, "./manifests/prod/")
    .validate()                  # Validate manifests
    .diff()                      # Show what will change
    .apply(namespace="prod", wait=True)  # Deploy and wait
    .get("pods", namespace="prod")       # Check status
    .health(namespace="prod"))           # Verify health
```

#### Development to Production Pipeline

```python
from celestra import App, KubernetesOutput

app = App("myapp").image("myapp:latest").port(8080)

output = KubernetesOutput()

# Development
dev_output = output.generate(app, "./manifests/dev/")
dev_output.apply(namespace="dev")

# Staging
staging_output = output.generate(app, "./manifests/staging/")
staging_output.apply(namespace="staging")

# Production
prod_output = output.generate(app, "./manifests/prod/")
prod_output.apply(namespace="prod", wait=True)
```

#### Troubleshooting Workflow

```python
from celestra import App, KubernetesOutput

app = App("troublesome-app").image("myapp:latest").port(8080)

output = KubernetesOutput()
output.generate(app, "./manifests/").apply()

# Troubleshooting workflow
output.get("pods")              # Check pod status
output.describe("deployment")   # Get deployment details
output.logs("troublesome-app")  # Check logs
output.events()                 # Look for events
output.exec("troublesome-app", "cat /etc/config/app.conf")  # Check config
```

## Method Chaining

Both output classes support method chaining for fluent, readable workflows:

```python
# Docker Compose workflow
(output
    .generate(app, "compose.yml")
    .pull()           # Pull images
    .up(detached=True) # Start services
    .ps()             # Check status
    .logs())          # Show logs

# Kubernetes workflow
(output
    .generate(app, "./manifests/")
    .validate()       # Validate
    .apply(wait=True) # Deploy
    .get("pods")      # Check status
    .health())        # Verify health
```

## File Tracking

The execution API automatically tracks the last generated files, so you don't need to specify file paths repeatedly:

```python
output = DockerComposeOutput()

# Generate file (automatically tracked)
output.generate(app, "docker-compose.yml")

# Use tracked file automatically
output.up()      # Uses the last generated file
output.logs()    # Uses the last generated file
output.down()    # Uses the last generated file
```

## Error Handling

The execution methods provide comprehensive error handling:

```python
try:
    output.generate(app, "compose.yml").up()
except subprocess.CalledProcessError as e:
    print(f"Execution failed: {e}")
    print(f"Error output: {e.stderr}")
```

## Best Practices

### 1. **Always Validate First**
```python
# Validate before applying
output.generate(app, "./manifests/").validate().apply()
```

### 2. **Use Wait Conditions for Production**
```python
# Wait for deployment to complete
output.apply(wait=True, timeout=300)
```

### 3. **Check Status After Operations**
```python
# Verify deployment success
output.apply().get("pods").health()
```

### 4. **Clean Up Resources**
```python
# Always clean up test resources
output.delete(grace_period=0)
```

### 5. **Use Namespaces for Organization**
```python
# Organize by environment
output.apply(namespace="development")
output.apply(namespace="staging")
output.apply(namespace="production")
```

## Integration with CI/CD

The execution API integrates seamlessly with CI/CD pipelines:

```python
# CI/CD deployment script
from celestra import App, KubernetesOutput

def deploy_to_environment(app, environment):
    output = KubernetesOutput()
    
    # Generate and deploy
    output.generate(app, f"./manifests/{environment}/")
    
    if environment == "production":
        # Production deployment with extra safety
        output.validate().diff().apply(wait=True, timeout=600)
    else:
        # Development/staging deployment
        output.apply(wait=True)
    
    # Verify deployment
    output.health()
    return output

# Usage in pipeline
app = App("myapp").image("myapp:latest").port(8080)
deploy_to_environment(app, "staging")
deploy_to_environment(app, "production")
```

This execution API transforms Celestra from a configuration generator into a complete deployment tool, enabling you to go from DSL definition to running applications with just a few lines of code. 