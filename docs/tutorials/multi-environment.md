# Multi-Environment Deployment Tutorial

This tutorial will guide you through setting up a complete multi-environment deployment strategy using Celestra, covering development, staging, and production environments with environment-specific configurations.

## 🎯 What You'll Build

By the end of this tutorial, you'll have:

- **Development environment** - Fast iteration with minimal resources
- **Staging environment** - Production-like testing environment
- **Production environment** - High-availability production deployment
- **Environment-specific configurations** - Different settings per environment
- **Automated deployment pipeline** - CI/CD integration
- **Environment isolation** - Proper namespace and network separation

## 📋 Prerequisites

Before starting, ensure you have:

- Celestra installed (`pip install celestra`)
- Multiple Kubernetes clusters or namespaces
- kubectl configured for each environment
- Git repository for version control

## 🏗️ Step 1: Environment Structure

Let's create a structured approach for managing multiple environments:

```python
# environments.py
from celestra import App, StatefulApp, ConfigMap, Secret, AppGroup
from typing import Dict, Any
import os

class EnvironmentManager:
    def __init__(self):
        self.environments = {
            'development': {
                'namespace': 'dev',
                'replicas': 1,
                'resources': {'cpu': '100m', 'memory': '256Mi'},
                'storage': '1Gi',
                'debug': True,
                'monitoring': False
            },
            'staging': {
                'namespace': 'staging',
                'replicas': 2,
                'resources': {'cpu': '250m', 'memory': '512Mi'},
                'storage': '5Gi',
                'debug': False,
                'monitoring': True
            },
            'production': {
                'namespace': 'prod',
                'replicas': 5,
                'resources': {'cpu': '500m', 'memory': '1Gi'},
                'storage': '20Gi',
                'debug': False,
                'monitoring': True
            }
        }
    
    def get_config(self, env: str) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        return self.environments.get(env, self.environments['development'])
    
    def create_app(self, name: str, env: str) -> App:
        """Create an application with environment-specific settings"""
        config = self.get_config(env)
        
        app = (App(f"{name}-{env}")
            .namespace(config['namespace'])
            .replicas(config['replicas'])
            .resources(**config['resources']))
        
        if config['debug']:
            app = app.env("DEBUG", "true").env("LOG_LEVEL", "debug")
        else:
            app = app.env("DEBUG", "false").env("LOG_LEVEL", "info")
        
        return app
    
    def create_database(self, name: str, env: str) -> StatefulApp:
        """Create a database with environment-specific settings"""
        config = self.get_config(env)
        
        return (StatefulApp(f"{name}-{env}")
            .namespace(config['namespace'])
            .replicas(min(config['replicas'], 3))  # Max 3 DB replicas
            .storage(config['storage']))
```

## 🚀 Step 2: Application Definition

Now let's define our applications with environment-specific configurations:

```python
# applications.py
from environments import EnvironmentManager

class ApplicationBuilder:
    def __init__(self):
        self.env_manager = EnvironmentManager()
    
    def build_web_application(self, env: str):
        """Build web application for specific environment"""
        config = self.env_manager.get_config(env)
        
        # Web application
        web_app = (self.env_manager.create_app("web", env)
            .image("myapp/web:latest")
            .port(80)
            .expose())
        
        # Database
        database = (self.env_manager.create_database("db", env)
            .image("postgres:15")
            .port(5432))
        
        # Database credentials
        db_secret = (Secret(f"db-secret-{env}")
            .namespace(config['namespace'])
            .add("username", "admin")
            .add("password", f"password-{env}"))
        
        # Application configuration
        app_config = (ConfigMap(f"app-config-{env}")
            .namespace(config['namespace'])
            .add("environment", env)
            .add("debug", str(config['debug']).lower())
            .add("database_url", f"postgresql://db-{env}:5432/myapp"))
        
        # Add configurations to app
        web_app = (web_app
            .add_secret(db_secret)
            .add_config(app_config))
        
        return web_app, database, db_secret, app_config
    
    def build_api_application(self, env: str):
        """Build API application for specific environment"""
        config = self.env_manager.get_config(env)
        
        # API application
        api = (self.env_manager.create_app("api", env)
            .image("myapp/api:latest")
            .port(8080)
            .expose())
        
        # API configuration
        api_config = (ConfigMap(f"api-config-{env}")
            .namespace(config['namespace'])
            .add("environment", env)
            .add("rate_limit", "1000")
            .add("timeout", "30s"))
        
        # API secrets
        api_secret = (Secret(f"api-secret-{env}")
            .namespace(config['namespace'])
            .add("jwt_secret", f"jwt-secret-{env}")
            .add("api_key", f"api-key-{env}"))
        
        api = api.add_config(api_config).add_secret(api_secret)
        
        return api, api_config, api_secret
    
    def build_monitoring_stack(self, env: str):
        """Build monitoring stack for staging and production"""
        config = self.env_manager.get_config(env)
        
        if not config['monitoring']:
            return []
        
        # Prometheus
        prometheus = (App(f"prometheus-{env}")
            .namespace(config['namespace'])
            .image("prom/prometheus:latest")
            .port(9090)
            .resources(cpu="200m", memory="512Mi")
            .expose())
        
        # Grafana
        grafana = (App(f"grafana-{env}")
            .namespace(config['namespace'])
            .image("grafana/grafana:latest")
            .port(3000)
            .env("GF_SECURITY_ADMIN_PASSWORD", "admin")
            .resources(cpu="100m", memory="256Mi")
            .expose())
        
        return [prometheus, grafana]
```

## 🔧 Step 3: Environment-Specific Deployments

Let's create deployment scripts for each environment:

```python
# deploy.py
from applications import ApplicationBuilder
from celestra import AppGroup
import sys

def deploy_environment(env: str):
    """Deploy to specific environment"""
    builder = ApplicationBuilder()
    
    # Build applications
    web_app, database, db_secret, app_config = builder.build_web_application(env)
    api, api_config, api_secret = builder.build_api_application(env)
    monitoring_components = builder.build_monitoring_stack(env)
    
    # Create application group
    platform = AppGroup(f"platform-{env}")
    
    # Add all components
    components = [
        web_app, database, db_secret, app_config,
        api, api_config, api_secret
    ] + monitoring_components
    
    platform.add(components)
    
    # Generate manifests
    output_dir = f"./manifests/{env}"
    platform.generate().to_yaml(output_dir)
    
    print(f"✅ Generated manifests for {env} environment in {output_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python deploy.py <environment>")
        print("Environments: development, staging, production")
        sys.exit(1)
    
    env = sys.argv[1]
    if env not in ['development', 'staging', 'production']:
        print("Invalid environment. Use: development, staging, production")
        sys.exit(1)
    
    deploy_environment(env)
```

## 🎯 Step 4: Environment-Specific Configurations

Create environment-specific configuration files:

```python
# configs/development.yaml
development:
  database:
    image: "postgres:15"
    storage: "1Gi"
    replicas: 1
  
  web:
    image: "myapp/web:dev"
    replicas: 1
    resources:
      cpu: "100m"
      memory: "256Mi"
  
  api:
    image: "myapp/api:dev"
    replicas: 1
    resources:
      cpu: "100m"
      memory: "256Mi"
  
  monitoring: false
  debug: true
  log_level: "debug"

# configs/staging.yaml
staging:
  database:
    image: "postgres:15"
    storage: "5Gi"
    replicas: 2
  
  web:
    image: "myapp/web:staging"
    replicas: 2
    resources:
      cpu: "250m"
      memory: "512Mi"
  
  api:
    image: "myapp/api:staging"
    replicas: 2
    resources:
      cpu: "250m"
      memory: "512Mi"
  
  monitoring: true
  debug: false
  log_level: "info"

# configs/production.yaml
production:
  database:
    image: "postgres:15"
    storage: "20Gi"
    replicas: 3
  
  web:
    image: "myapp/web:latest"
    replicas: 5
    resources:
      cpu: "500m"
      memory: "1Gi"
  
  api:
    image: "myapp/api:latest"
    replicas: 5
    resources:
      cpu: "500m"
      memory: "1Gi"
  
  monitoring: true
  debug: false
  log_level: "warn"
```

## 🔒 Step 5: Security and Isolation

Add environment-specific security configurations:

```python
# security.py
from celestra import NetworkPolicy, Role, RoleBinding, ServiceAccount

class SecurityManager:
    def __init__(self):
        self.env_manager = EnvironmentManager()
    
    def create_network_policies(self, env: str):
        """Create network policies for environment isolation"""
        config = self.env_manager.get_config(env)
        namespace = config['namespace']
        
        # Allow internal communication
        internal_policy = (NetworkPolicy(f"internal-{env}")
            .namespace(namespace)
            .allow_pods_with_label("app", f"web-{env}")
            .allow_pods_with_label("app", f"api-{env}")
            .allow_pods_with_label("app", f"db-{env}")
            .deny_all())
        
        # Allow external access to web
        web_policy = (NetworkPolicy(f"web-external-{env}")
            .namespace(namespace)
            .allow_external_traffic()
            .allow_pods_with_label("app", f"web-{env}"))
        
        return [internal_policy, web_policy]
    
    def create_rbac(self, env: str):
        """Create RBAC for environment"""
        config = self.env_manager.get_config(env)
        namespace = config['namespace']
        
        # Service accounts
        web_sa = ServiceAccount(f"web-sa-{env}").namespace(namespace)
        api_sa = ServiceAccount(f"api-sa-{env}").namespace(namespace)
        db_sa = ServiceAccount(f"db-sa-{env}").namespace(namespace)
        
        # Roles
        web_role = (Role(f"web-role-{env}")
            .namespace(namespace)
            .add_policy("get", "pods")
            .add_policy("get", "services"))
        
        api_role = (Role(f"api-role-{env}")
            .namespace(namespace)
            .add_policy("get", "pods")
            .add_policy("get", "services")
            .add_policy("list", "endpoints"))
        
        # Role bindings
        web_binding = (RoleBinding(f"web-binding-{env}")
            .namespace(namespace)
            .bind_role(web_role)
            .bind_service_account(web_sa))
        
        api_binding = (RoleBinding(f"api-binding-{env}")
            .namespace(namespace)
            .bind_role(api_role)
            .bind_service_account(api_sa))
        
        return [web_sa, api_sa, db_sa, web_role, api_role, web_binding, api_binding]
```

## 🚀 Step 6: CI/CD Integration

Create deployment scripts for CI/CD:

```python
# ci_cd.py
import subprocess
import sys
from applications import ApplicationBuilder
from security import SecurityManager

class CICDPipeline:
    def __init__(self):
        self.builder = ApplicationBuilder()
        self.security = SecurityManager()
    
    def deploy_to_environment(self, env: str, kubeconfig: str = None):
        """Deploy to specific environment"""
        print(f"🚀 Deploying to {env} environment...")
        
        # Build applications
        web_app, database, db_secret, app_config = self.builder.build_web_application(env)
        api, api_config, api_secret = self.builder.build_api_application(env)
        monitoring_components = self.builder.build_monitoring_stack(env)
        
        # Add security components
        network_policies = self.security.create_network_policies(env)
        rbac_components = self.security.create_rbac(env)
        
        # Create application group
        from celestra import AppGroup
        platform = AppGroup(f"platform-{env}")
        
        # Add all components
        all_components = [
            web_app, database, db_secret, app_config,
            api, api_config, api_secret
        ] + monitoring_components + network_policies + rbac_components
        
        platform.add(all_components)
        
        # Generate manifests
        output_dir = f"./manifests/{env}"
        platform.generate().to_yaml(output_dir)
        
        # Deploy to Kubernetes
        self.apply_manifests(output_dir, kubeconfig)
        
        print(f"✅ Successfully deployed to {env} environment")
    
    def apply_manifests(self, manifest_dir: str, kubeconfig: str = None):
        """Apply manifests to Kubernetes"""
        cmd = ["kubectl", "apply", "-f", manifest_dir]
        
        if kubeconfig:
            cmd.extend(["--kubeconfig", kubeconfig])
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ Deployment failed: {e.stderr}")
            sys.exit(1)
    
    def run_tests(self, env: str):
        """Run tests for environment"""
        print(f"🧪 Running tests for {env} environment...")
        
        # Health checks
        self.check_health(env)
        
        # Integration tests
        self.run_integration_tests(env)
        
        print(f"✅ Tests passed for {env} environment")
    
    def check_health(self, env: str):
        """Check application health"""
        # Check if pods are running
        cmd = ["kubectl", "get", "pods", "-n", env, "--field-selector=status.phase=Running"]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"Health check passed: {result.stdout}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Health check failed: {e.stderr}")
            sys.exit(1)
    
    def run_integration_tests(self, env: str):
        """Run integration tests"""
        # This would run your actual integration tests
        print(f"Running integration tests for {env}...")
        # Add your test logic here

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ci_cd.py <environment> [kubeconfig]")
        sys.exit(1)
    
    env = sys.argv[1]
    kubeconfig = sys.argv[2] if len(sys.argv) > 2 else None
    
    pipeline = CICDPipeline()
    pipeline.deploy_to_environment(env, kubeconfig)
    pipeline.run_tests(env)
```

## 📊 Step 7: Monitoring and Observability

Add environment-specific monitoring:

```python
# monitoring.py
from celestra import Observability, ConfigMap

class MonitoringManager:
    def __init__(self):
        self.env_manager = EnvironmentManager()
    
    def create_monitoring_stack(self, env: str):
        """Create monitoring stack for environment"""
        config = self.env_manager.get_config(env)
        
        if not config['monitoring']:
            return []
        
        # Prometheus configuration
        prometheus_config = (ConfigMap(f"prometheus-config-{env}")
            .namespace(config['namespace'])
            .add_yaml("prometheus.yml", f"""
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: '{env}-web'
    static_configs:
      - targets: ['web-{env}:80']
  - job_name: '{env}-api'
    static_configs:
      - targets: ['api-{env}:8080']
  - job_name: '{env}-db'
    static_configs:
      - targets: ['db-{env}:5432']
"""))
        
        # Prometheus
        prometheus = (App(f"prometheus-{env}")
            .namespace(config['namespace'])
            .image("prom/prometheus:latest")
            .port(9090)
            .add_config(prometheus_config)
            .resources(cpu="200m", memory="512Mi")
            .expose())
        
        # Grafana
        grafana = (App(f"grafana-{env}")
            .namespace(config['namespace'])
            .image("grafana/grafana:latest")
            .port(3000)
            .env("GF_SECURITY_ADMIN_PASSWORD", "admin")
            .env("GF_INSTALL_PLUGINS", "grafana-prometheus-datasource")
            .resources(cpu="100m", memory="256Mi")
            .expose())
        
        return [prometheus, grafana, prometheus_config]
```

## 🎯 Step 8: Deployment Scripts

Create deployment scripts for each environment:

```bash
#!/bin/bash
# deploy-dev.sh

echo "🚀 Deploying to development environment..."

# Set environment variables
export ENVIRONMENT=development
export NAMESPACE=dev

# Deploy using Celestra
python deploy.py development

# Apply to Kubernetes
kubectl apply -f ./manifests/development/

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/web-development -n dev
kubectl wait --for=condition=available --timeout=300s deployment/api-development -n dev

echo "✅ Development deployment complete!"
```

```bash
#!/bin/bash
# deploy-staging.sh

echo "🚀 Deploying to staging environment..."

# Set environment variables
export ENVIRONMENT=staging
export NAMESPACE=staging

# Run tests first
python -m pytest tests/ --env=staging

# Deploy using Celestra
python deploy.py staging

# Apply to Kubernetes
kubectl apply -f ./manifests/staging/

# Wait for deployment
kubectl wait --for=condition=available --timeout=300s deployment/web-staging -n staging
kubectl wait --for=condition=available --timeout=300s deployment/api-staging -n staging

# Run smoke tests
python tests/smoke_tests.py --env=staging

echo "✅ Staging deployment complete!"
```

```bash
#!/bin/bash
# deploy-production.sh

echo "🚀 Deploying to production environment..."

# Set environment variables
export ENVIRONMENT=production
export NAMESPACE=prod

# Run full test suite
python -m pytest tests/ --env=production

# Deploy using Celestra
python deploy.py production

# Apply to Kubernetes with rolling update
kubectl apply -f ./manifests/production/

# Wait for deployment
kubectl wait --for=condition=available --timeout=600s deployment/web-production -n prod
kubectl wait --for=condition=available --timeout=600s deployment/api-production -n prod

# Run production tests
python tests/production_tests.py

echo "✅ Production deployment complete!"
```

## 🔍 Step 9: Verification and Testing

Create verification scripts:

```python
# verify.py
import subprocess
import sys
import time

class EnvironmentVerifier:
    def __init__(self, env: str):
        self.env = env
        self.namespace = self.get_namespace(env)
    
    def get_namespace(self, env: str) -> str:
        """Get namespace for environment"""
        namespaces = {
            'development': 'dev',
            'staging': 'staging',
            'production': 'prod'
        }
        return namespaces.get(env, 'default')
    
    def verify_deployment(self):
        """Verify deployment is successful"""
        print(f"🔍 Verifying {self.env} deployment...")
        
        # Check if all pods are running
        self.check_pod_status()
        
        # Check if services are available
        self.check_service_status()
        
        # Check if applications are responding
        self.check_application_health()
        
        print(f"✅ {self.env} deployment verified successfully!")
    
    def check_pod_status(self):
        """Check if all pods are running"""
        cmd = [
            "kubectl", "get", "pods", "-n", self.namespace,
            "--field-selector=status.phase!=Running",
            "-o", "name"
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            if result.stdout.strip():
                print(f"❌ Some pods are not running: {result.stdout}")
                sys.exit(1)
            else:
                print("✅ All pods are running")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to check pod status: {e.stderr}")
            sys.exit(1)
    
    def check_service_status(self):
        """Check if services are available"""
        services = [f"web-{self.env}", f"api-{self.env}"]
        
        for service in services:
            cmd = ["kubectl", "get", "service", service, "-n", self.namespace]
            
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ Service {service} is available")
            except subprocess.CalledProcessError as e:
                print(f"❌ Service {service} is not available: {e.stderr}")
                sys.exit(1)
    
    def check_application_health(self):
        """Check application health endpoints"""
        # This would make HTTP requests to your applications
        print("✅ Application health checks passed")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python verify.py <environment>")
        sys.exit(1)
    
    env = sys.argv[1]
    verifier = EnvironmentVerifier(env)
    verifier.verify_deployment()
```

## 🎯 Step 10: Environment Management

Create environment management utilities:

```python
# env_manager.py
import subprocess
import sys
from typing import List

class EnvironmentManager:
    def __init__(self):
        self.environments = ['development', 'staging', 'production']
    
    def list_environments(self):
        """List all environments and their status"""
        print("📋 Environment Status:")
        print("=" * 50)
        
        for env in self.environments:
            namespace = self.get_namespace(env)
            status = self.get_environment_status(namespace)
            print(f"{env.capitalize():12} | {status}")
    
    def get_environment_status(self, namespace: str) -> str:
        """Get status of environment"""
        try:
            cmd = ["kubectl", "get", "pods", "-n", namespace, "--no-headers"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if not result.stdout.strip():
                return "Not Deployed"
            
            lines = result.stdout.strip().split('\n')
            running = sum(1 for line in lines if 'Running' in line)
            total = len(lines)
            
            if running == total:
                return f"Running ({running}/{total})"
            else:
                return f"Partial ({running}/{total})"
        except subprocess.CalledProcessError:
            return "Error"
    
    def get_namespace(self, env: str) -> str:
        """Get namespace for environment"""
        namespaces = {
            'development': 'dev',
            'staging': 'staging',
            'production': 'prod'
        }
        return namespaces.get(env, 'default')
    
    def cleanup_environment(self, env: str):
        """Clean up environment"""
        namespace = self.get_namespace(env)
        
        print(f"🧹 Cleaning up {env} environment...")
        
        cmd = ["kubectl", "delete", "namespace", namespace]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"✅ {env} environment cleaned up")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to cleanup {env}: {e.stderr}")
    
    def scale_environment(self, env: str, replicas: int):
        """Scale environment"""
        namespace = self.get_namespace(env)
        
        print(f"📈 Scaling {env} environment to {replicas} replicas...")
        
        deployments = [f"web-{env}", f"api-{env}"]
        
        for deployment in deployments:
            cmd = ["kubectl", "scale", "deployment", deployment, f"--replicas={replicas}", "-n", namespace]
            
            try:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                print(f"✅ Scaled {deployment} to {replicas} replicas")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to scale {deployment}: {e.stderr}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python env_manager.py <command> [environment] [options]")
        print("Commands: list, cleanup, scale")
        sys.exit(1)
    
    command = sys.argv[1]
    manager = EnvironmentManager()
    
    if command == "list":
        manager.list_environments()
    elif command == "cleanup" and len(sys.argv) > 2:
        env = sys.argv[2]
        manager.cleanup_environment(env)
    elif command == "scale" and len(sys.argv) > 3:
        env = sys.argv[2]
        replicas = int(sys.argv[3])
        manager.scale_environment(env, replicas)
    else:
        print("Invalid command or missing arguments")
        sys.exit(1)
```

## 🚀 Usage Examples

### Deploy to Development

```bash
# Deploy to development
python deploy.py development
kubectl apply -f ./manifests/development/

# Or use the script
./deploy-dev.sh
```

### Deploy to Staging

```bash
# Deploy to staging
python deploy.py staging
kubectl apply -f ./manifests/staging/

# Or use the script
./deploy-staging.sh
```

### Deploy to Production

```bash
# Deploy to production
python deploy.py production
kubectl apply -f ./manifests/production/

# Or use the script
./deploy-production.sh
```

### Environment Management

```bash
# List all environments
python env_manager.py list

# Clean up development environment
python env_manager.py cleanup development

# Scale staging to 3 replicas
python env_manager.py scale staging 3
```

## 🎯 Best Practices

### 1. **Environment Isolation**
- Use separate namespaces for each environment
- Implement network policies for isolation
- Use different service accounts per environment

### 2. **Configuration Management**
- Store environment-specific configs in separate files
- Use ConfigMaps for non-sensitive data
- Use Secrets for sensitive data

### 3. **Deployment Strategy**
- Use rolling updates for zero-downtime deployments
- Implement health checks and readiness probes
- Set up proper resource limits

### 4. **Monitoring and Observability**
- Enable monitoring for staging and production
- Set up alerting for critical metrics
- Use centralized logging

### 5. **Security**
- Implement RBAC for each environment
- Use network policies for traffic control
- Rotate secrets regularly

## 📚 Related Tutorials

- **[RBAC Security Tutorial](../components/security/rbac.md)** - Security and access control
- **[Production Platform Tutorial]** - *Coming soon - Production platform tutorials will be added here*
- **[Microservices Tutorial](microservices.md)** - Building microservices

## 🚀 Next Steps

Now that you have a multi-environment setup, explore:

- **[RBAC Security Tutorial](../components/security/rbac.md)** - Advanced security configuration
- **[Microservices Tutorial](microservices.md)** - Build complete microservices platforms
- **[Observability Stack Tutorial](observability-stack.md)** - Advanced monitoring setup
- **[WordPress Platform Tutorial](../examples/production/index.md)** - Complete web platform

Ready to build more complex systems? Check out the [Microservices Tutorial](microservices.md) or [Observability Stack Tutorial](observability-stack.md)! 