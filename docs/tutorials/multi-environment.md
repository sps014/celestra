# Multi-Environment Setup Tutorial

Learn how to configure and deploy applications across multiple environments (development, staging, and production) using K8s-Gen DSL.

!!! info "Tutorial Overview"
    **Difficulty**: ⭐⭐⭐ Intermediate  
    **Time**: 20-25 minutes  
    **Prerequisites**: Basic K8s-Gen knowledge  
    **You'll Learn**: Environment-specific configurations, GitOps workflows, CI/CD integration

## Environment Strategy

```mermaid
graph LR
    subgraph "Development"
        D1[Single Replica]
        D2[Minimal Resources]
        D3[Debug Enabled]
        D4[Local Storage]
    end
    
    subgraph "Staging"
        S1[2 Replicas]
        S2[Production-like]
        S3[Monitoring]
        S4[Persistent Storage]
    end
    
    subgraph "Production"
        P1[HA (3+ Replicas)]
        P2[Resource Limits]
        P3[Security Enabled]
        P4[Backup & Monitoring]
    end
    
    DEV[Developer] --> D1
    CI[CI/CD] --> S1
    RELEASE[Release] --> P1
```

## Environment Configuration Framework

### Base Application Configuration

Create a base configuration that all environments inherit from:

```python
#!/usr/bin/env python3
"""
Base Application Configuration
"""

from src.k8s_gen import App, StatefulApp, Service, ConfigMap, Secret
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class EnvironmentConfig:
    """Environment-specific configuration"""
    name: str
    replicas: int
    cpu: str
    memory: str
    cpu_limit: str
    memory_limit: str
    storage_size: str
    debug_enabled: bool
    monitoring_enabled: bool
    security_enabled: bool
    backup_enabled: bool
    
    # Environment-specific values
    database_host: str
    database_name: str
    redis_host: str
    log_level: str
    
    # External service endpoints
    api_base_url: str
    payment_gateway_url: str

class BaseApplication:
    """Base application builder with environment support"""
    
    def __init__(self, name: str, config: EnvironmentConfig):
        self.name = name
        self.config = config
    
    def create_web_app(self) -> App:
        """Create web application with environment-specific config"""
        app = (App(f"{self.name}-web")
            .image(f"{self.name}:latest")
            .port(8080, "http")
            .replicas(self.config.replicas)
            .resources(
                cpu=self.config.cpu,
                memory=self.config.memory,
                cpu_limit=self.config.cpu_limit,
                memory_limit=self.config.memory_limit
            )
            .env("DATABASE_HOST", self.config.database_host)
            .env("DATABASE_NAME", self.config.database_name)
            .env("REDIS_HOST", self.config.redis_host)
            .env("LOG_LEVEL", self.config.log_level)
            .env("API_BASE_URL", self.config.api_base_url)
            .env("PAYMENT_GATEWAY_URL", self.config.payment_gateway_url)
            .env("DEBUG", str(self.config.debug_enabled).lower())
            .expose())
        
        # Add health checks for non-dev environments
        if self.config.name != "development":
            app.liveness_probe("/health", initial_delay=30)
            app.readiness_probe("/ready", initial_delay=10)
        
        return app
    
    def create_database(self) -> StatefulApp:
        """Create database with environment-specific config"""
        db = (StatefulApp(f"{self.name}-postgres")
            .image("postgres:13")
            .port(5432, "postgres")
            .env("POSTGRES_DB", self.config.database_name)
            .env("POSTGRES_USER", "app_user")
            .env("POSTGRES_PASSWORD", "changeme")  # Use secrets in production
            .resources(
                cpu=self.config.cpu,
                memory=self.config.memory,
                cpu_limit=self.config.cpu_limit,
                memory_limit=self.config.memory_limit
            )
            .storage("/var/lib/postgresql/data", self.config.storage_size))
        
        # Single replica for dev/staging, HA for production
        if self.config.name == "production":
            db.replicas(3)
        else:
            db.replicas(1)
        
        return db
    
    def create_redis(self) -> StatefulApp:
        """Create Redis cache with environment-specific config"""
        redis = (StatefulApp(f"{self.name}-redis")
            .image("redis:7-alpine")
            .port(6379, "redis")
            .resources(cpu="100m", memory="128Mi")
            .storage("/data", "1Gi"))
        
        if self.config.name == "production":
            redis.replicas(3)  # Redis cluster
        else:
            redis.replicas(1)
        
        return redis
```

### Environment-Specific Configurations

```python
#!/usr/bin/env python3
"""
Environment-Specific Configurations
"""

from base_config import EnvironmentConfig

# Development Environment
DEVELOPMENT = EnvironmentConfig(
    name="development",
    replicas=1,
    cpu="100m",
    memory="128Mi", 
    cpu_limit="500m",
    memory_limit="512Mi",
    storage_size="1Gi",
    debug_enabled=True,
    monitoring_enabled=False,
    security_enabled=False,
    backup_enabled=False,
    
    # Development-specific values
    database_host="postgres-dev",
    database_name="myapp_dev",
    redis_host="redis-dev",
    log_level="DEBUG",
    
    # Local/mock endpoints
    api_base_url="http://localhost:8080",
    payment_gateway_url="http://localhost:9000/mock"
)

# Staging Environment
STAGING = EnvironmentConfig(
    name="staging",
    replicas=2,
    cpu="200m",
    memory="256Mi",
    cpu_limit="500m", 
    memory_limit="512Mi",
    storage_size="5Gi",
    debug_enabled=False,
    monitoring_enabled=True,
    security_enabled=True,
    backup_enabled=False,
    
    # Staging-specific values
    database_host="postgres-staging",
    database_name="myapp_staging",
    redis_host="redis-staging",
    log_level="INFO",
    
    # Staging endpoints
    api_base_url="https://api-staging.mycompany.com",
    payment_gateway_url="https://sandbox.payment-provider.com"
)

# Production Environment  
PRODUCTION = EnvironmentConfig(
    name="production",
    replicas=5,
    cpu="500m",
    memory="1Gi",
    cpu_limit="1000m",
    memory_limit="2Gi", 
    storage_size="50Gi",
    debug_enabled=False,
    monitoring_enabled=True,
    security_enabled=True,
    backup_enabled=True,
    
    # Production values
    database_host="postgres-prod",
    database_name="myapp_prod", 
    redis_host="redis-prod",
    log_level="WARN",
    
    # Production endpoints
    api_base_url="https://api.mycompany.com",
    payment_gateway_url="https://api.payment-provider.com"
)
```

### Complete Multi-Environment Deployment

```python
#!/usr/bin/env python3
"""
Multi-Environment Deployment Script
"""

import os
import argparse
from base_config import BaseApplication
from env_configs import DEVELOPMENT, STAGING, PRODUCTION
from src.k8s_gen import KubernetesOutput, HelmOutput, Secret, ConfigMap

class MultiEnvironmentDeployer:
    """Handles deployment across multiple environments"""
    
    def __init__(self, app_name: str):
        self.app_name = app_name
        self.environments = {
            "dev": DEVELOPMENT,
            "staging": STAGING, 
            "prod": PRODUCTION
        }
    
    def create_secrets(self, env_name: str, config) -> Dict[str, Secret]:
        """Create environment-specific secrets"""
        secrets = {}
        
        # Database secrets
        db_secret = Secret(f"{self.app_name}-db-{env_name}")
        if env_name == "prod":
            db_secret.add_data("password", "super-secure-prod-password")
        elif env_name == "staging":
            db_secret.add_data("password", "staging-password")
        else:
            db_secret.add_data("password", "dev-password")
        
        secrets["database"] = db_secret
        
        # API Keys
        api_secret = Secret(f"{self.app_name}-api-{env_name}")
        if env_name == "prod":
            api_secret.add_data("api_key", "prod-api-key")
            api_secret.add_data("payment_key", "prod-payment-key")
        elif env_name == "staging":
            api_secret.add_data("api_key", "staging-api-key")
            api_secret.add_data("payment_key", "staging-payment-key")
        else:
            api_secret.add_data("api_key", "dev-api-key")
            api_secret.add_data("payment_key", "mock-payment-key")
        
        secrets["api"] = api_secret
        
        return secrets
    
    def create_config_maps(self, env_name: str, config) -> Dict[str, ConfigMap]:
        """Create environment-specific config maps"""
        configs = {}
        
        # Application configuration
        app_config = ConfigMap(f"{self.app_name}-config-{env_name}")
        app_config.add_data("app.properties", f"""
# {env_name.upper()} Environment Configuration
app.name={self.app_name}
app.environment={env_name}
app.debug={str(config.debug_enabled).lower()}
app.log.level={config.log_level}

# Database Configuration
db.host={config.database_host}
db.name={config.database_name}
db.pool.min=5
db.pool.max={10 if env_name == 'prod' else 5}

# Cache Configuration
redis.host={config.redis_host}
redis.port=6379
redis.timeout=5000

# External Services
api.base.url={config.api_base_url}
payment.gateway.url={config.payment_gateway_url}

# Feature Flags
features.monitoring={str(config.monitoring_enabled).lower()}
features.security={str(config.security_enabled).lower()}
features.backup={str(config.backup_enabled).lower()}
""")
        
        configs["app"] = app_config
        
        # Nginx configuration for web tier
        nginx_config = ConfigMap(f"{self.app_name}-nginx-{env_name}")
        nginx_config.add_data("nginx.conf", f"""
events {{
    worker_connections 1024;
}}

http {{
    upstream backend {{
        server {self.app_name}-web:8080;
    }}
    
    server {{
        listen 80;
        
        location / {{
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }}
        
        location /health {{
            access_log off;
            return 200 "healthy\\n";
        }}
    }}
}}
""")
        
        configs["nginx"] = nginx_config
        
        return configs
    
    def deploy_environment(self, env_name: str, output_format: str = "kubernetes"):
        """Deploy specific environment"""
        if env_name not in self.environments:
            raise ValueError(f"Unknown environment: {env_name}")
        
        config = self.environments[env_name]
        print(f"🚀 Deploying {self.app_name} to {env_name} environment...")
        
        # Create application components
        app_builder = BaseApplication(self.app_name, config)
        web_app = app_builder.create_web_app()
        database = app_builder.create_database()
        redis = app_builder.create_redis()
        
        # Create secrets and config maps
        secrets = self.create_secrets(env_name, config)
        configs = self.create_config_maps(env_name, config)
        
        # Collect all components
        components = [web_app, database, redis]
        components.extend(secrets.values())
        components.extend(configs.values())
        
        # Generate output
        output_dir = f"deployments/{env_name}"
        os.makedirs(output_dir, exist_ok=True)
        
        if output_format == "kubernetes":
            output = KubernetesOutput()
            for component in components:
                output.generate(component, output_dir)
            print(f"📄 Generated Kubernetes YAML in {output_dir}/")
            
        elif output_format == "helm":
            helm_output = HelmOutput(f"{self.app_name}-{env_name}")
            for component in components:
                helm_output.add_resource(component)
            helm_output.generate(output_dir)
            print(f"📦 Generated Helm chart in {output_dir}/")
        
        return components
    
    def deploy_all_environments(self):
        """Deploy to all environments"""
        for env_name in self.environments.keys():
            self.deploy_environment(env_name)
    
    def compare_environments(self, env1: str, env2: str):
        """Compare configurations between environments"""
        config1 = self.environments[env1]
        config2 = self.environments[env2]
        
        print(f"\n🔍 Comparing {env1} vs {env2}:")
        print(f"{'Setting':<20} {env1:<15} {env2:<15}")
        print("-" * 50)
        print(f"{'Replicas':<20} {config1.replicas:<15} {config2.replicas:<15}")
        print(f"{'CPU':<20} {config1.cpu:<15} {config2.cpu:<15}")
        print(f"{'Memory':<20} {config1.memory:<15} {config2.memory:<15}")
        print(f"{'Storage':<20} {config1.storage_size:<15} {config2.storage_size:<15}")
        print(f"{'Debug':<20} {config1.debug_enabled:<15} {config2.debug_enabled:<15}")
        print(f"{'Monitoring':<20} {config1.monitoring_enabled:<15} {config2.monitoring_enabled:<15}")
        print(f"{'Security':<20} {config1.security_enabled:<15} {config2.security_enabled:<15}")

def main():
    parser = argparse.ArgumentParser(description='Multi-environment deployment tool')
    parser.add_argument('--app', required=True, help='Application name')
    parser.add_argument('--env', choices=['dev', 'staging', 'prod', 'all'], 
                       default='all', help='Environment to deploy')
    parser.add_argument('--format', choices=['kubernetes', 'helm'], 
                       default='kubernetes', help='Output format')
    parser.add_argument('--compare', nargs=2, metavar=('ENV1', 'ENV2'),
                       help='Compare two environments')
    
    args = parser.parse_args()
    
    deployer = MultiEnvironmentDeployer(args.app)
    
    if args.compare:
        deployer.compare_environments(args.compare[0], args.compare[1])
        return
    
    if args.env == 'all':
        deployer.deploy_all_environments()
    else:
        deployer.deploy_environment(args.env, args.format)
    
    print(f"\n✅ Deployment complete!")
    print(f"📁 Check deployments/ directory for generated files")

if __name__ == "__main__":
    main()
```

## GitOps Workflow Integration

### Directory Structure

```
environments/
├── base/
│   ├── app.py                 # Base application configuration
│   ├── database.py            # Database configuration
│   └── kustomization.yaml     # Base kustomization
├── development/
│   ├── config.py              # Dev-specific overrides
│   ├── kustomization.yaml     # Dev kustomization
│   └── patches/               # Dev-specific patches
├── staging/
│   ├── config.py              # Staging-specific overrides
│   ├── kustomization.yaml     # Staging kustomization
│   └── patches/               # Staging-specific patches
└── production/
    ├── config.py              # Prod-specific overrides
    ├── kustomization.yaml     # Prod kustomization
    └── patches/               # Prod-specific patches
```

### Usage Examples

```bash
# Deploy to development
python multi_env_deploy.py --app myapp --env dev

# Deploy to production with Helm
python multi_env_deploy.py --app myapp --env prod --format helm

# Deploy to all environments
python multi_env_deploy.py --app myapp --env all

# Compare environments
python multi_env_deploy.py --app myapp --compare dev prod
```

### Expected Output

```
🚀 Deploying myapp to prod environment...
📄 Generated Kubernetes YAML in deployments/prod/

🔍 Comparing dev vs prod:
Setting              dev             prod           
--------------------------------------------------
Replicas             1               5              
CPU                  100m            500m           
Memory               128Mi           1Gi            
Storage              1Gi             50Gi           
Debug                True            False          
Monitoring           False           True           
Security             False           True           
```

## CI/CD Pipeline Integration

### GitHub Actions Workflow

```yaml
# .github/workflows/multi-env-deploy.yml
name: Multi-Environment Deployment

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  deploy-dev:
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r src/requirements.txt
      
      - name: Generate development manifests
        run: python multi_env_deploy.py --app myapp --env dev
      
      - name: Deploy to development
        run: |
          echo "${{ secrets.KUBECONFIG_DEV }}" | base64 -d > kubeconfig
          kubectl --kubeconfig=kubeconfig apply -f deployments/dev/

  deploy-staging:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r src/requirements.txt
      
      - name: Generate staging manifests
        run: python multi_env_deploy.py --app myapp --env staging
      
      - name: Deploy to staging
        run: |
          echo "${{ secrets.KUBECONFIG_STAGING }}" | base64 -d > kubeconfig
          kubectl --kubeconfig=kubeconfig apply -f deployments/staging/

  deploy-production:
    if: github.ref == 'refs/heads/main' && contains(github.event.head_commit.message, '[deploy-prod]')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r src/requirements.txt
      
      - name: Generate production manifests
        run: python multi_env_deploy.py --app myapp --env prod
      
      - name: Deploy to production
        run: |
          echo "${{ secrets.KUBECONFIG_PROD }}" | base64 -d > kubeconfig
          kubectl --kubeconfig=kubeconfig apply -f deployments/prod/
```

## Environment-Specific Features

### Development Environment

```python
# Additional development-specific features
def create_dev_environment():
    """Create development environment with special features"""
    
    # Debug sidecar for development
    debug_sidecar = (App("debug-tools")
        .image("alpine/curl:latest")
        .command(["sleep", "infinity"])
        .resources(cpu="50m", memory="64Mi"))
    
    # Hot reload volume for development
    hot_reload_volume = {
        "name": "source-code",
        "hostPath": {"path": "/host/src", "type": "Directory"}
    }
    
    # Development-specific ingress with debug headers
    dev_ingress = (Ingress("dev-ingress")
        .host("myapp.dev.local")
        .path("/", "myapp-web", 8080)
        .add_annotation("nginx.ingress.kubernetes.io/enable-cors", "true")
        .add_annotation("nginx.ingress.kubernetes.io/cors-allow-headers", "*"))
    
    return debug_sidecar, hot_reload_volume, dev_ingress
```

### Production Environment

```python
# Additional production-specific features  
def create_prod_environment():
    """Create production environment with enterprise features"""
    
    # Production monitoring
    monitoring = (Observability("prod-monitoring")
        .enable_metrics()
        .enable_tracing() 
        .enable_logging()
        .alert_on_errors())
    
    # Production security
    security = (SecurityPolicy("prod-security")
        .enable_rbac()
        .pod_security_standards("restricted")
        .network_policies_enabled()
        .image_scanning_enabled())
    
    # Production backup
    backup = (CronJob("nightly-backup")
        .schedule("0 2 * * *")
        .image("postgres:13")
        .command(["pg_dump", "-h", "postgres", "-U", "app_user", "myapp_prod"])
        .resources(cpu="100m", memory="256Mi"))
    
    return monitoring, security, backup
```

## Best Practices

!!! tip "Multi-Environment Best Practices"
    
    **Configuration Management:**
    - Use environment-specific config files
    - Never hardcode environment values
    - Use secrets for sensitive data
    - Version control all configurations
    
    **Resource Management:**
    - Scale resources appropriately per environment
    - Use resource limits in production
    - Monitor resource usage across environments
    
    **Security:**
    - Enable security features in staging/production
    - Use different credentials per environment
    - Implement network policies
    - Regular security scanning
    
    **Deployment:**
    - Automate deployments via CI/CD
    - Test in staging before production
    - Use blue-green or canary deployments in production
    - Implement rollback strategies

## Troubleshooting

### Common Issues

!!! warning "Environment Mismatch"
    **Problem**: Configuration values not updating between environments
    
    **Solution**: Verify environment-specific config files are being loaded correctly
    ```python
    # Add environment validation
    def validate_environment(env_name: str, config: EnvironmentConfig):
        assert config.name == env_name, f"Config mismatch: expected {env_name}, got {config.name}"
    ```

!!! warning "Resource Conflicts"
    **Problem**: Resources with same names across environments
    
    **Solution**: Use environment prefixes or suffixes
    ```python
    def get_resource_name(base_name: str, env: str) -> str:
        return f"{base_name}-{env}"
    ```

## Next Steps

🎯 **Congratulations!** You now have a robust multi-environment deployment strategy. Explore these advanced topics:

- **[RBAC Security](rbac-security.md)** - Environment-specific access control
- **[Observability Stack](observability-stack.md)** - Monitor across environments
- **[Advanced Configuration](../configuration/multi-environment.md)** - Fine-tune settings
- **[CI/CD Integration](../examples/platforms/ci-cd-pipeline.md)** - Automated pipelines

---

**Need help?** Check out our [configuration guide](../configuration/multi-environment.md) or [best practices](../advanced/best-practices.md)! 