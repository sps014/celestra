# Secret Component

The `Secret` component provides secure storage and management of sensitive data like passwords, API keys, certificates, and tokens in your Kubernetes applications.

## Overview

Use `Secret` for:
- **Passwords** - Database and service passwords
- **API Keys** - External service credentials
- **Certificates** - TLS certificates and keys
- **Tokens** - Authentication and authorization tokens
- **SSH Keys** - Git and deployment keys

## Basic Usage

```python
from src.k8s_gen import Secret

# Simple secret with key-value pairs
secret = (Secret("app-secret")
    .add_data("username", "admin")
    .add_data("password", "supersecret123")
    .add_data("api-key", "sk_live_abcd1234"))
```

## Secret Types

### Generic Secrets

```python
# Generic secret (default type)
app_secret = (Secret("app-credentials")
    .type("Opaque")  # Default type
    .add_data("database-url", "postgresql://user:pass@host:5432/db")
    .add_data("redis-url", "redis://host:6379")
    .add_data("jwt-secret", "very-secret-jwt-key"))
```

### Docker Registry Secrets

```python
# Docker registry authentication
registry_secret = (Secret("docker-registry")
    .type("kubernetes.io/dockerconfigjson")
    .docker_registry(
        server="https://private-registry.com",
        username="deploy-user",
        password="deploy-token",
        email="deploy@company.com"
    ))

# Multiple registries
multi_registry = (Secret("multi-registry")
    .type("kubernetes.io/dockerconfigjson")
    .docker_registry("https://registry1.com", "user1", "pass1")
    .docker_registry("https://registry2.com", "user2", "pass2"))
```

### TLS Certificates

```python
# TLS certificate secret
tls_secret = (Secret("tls-cert")
    .type("kubernetes.io/tls")
    .tls_certificate(
        cert_file="path/to/cert.pem",
        key_file="path/to/key.pem"
    ))

# From certificate content
tls_secret = (Secret("app-tls")
    .type("kubernetes.io/tls")
    .add_data("tls.crt", "-----BEGIN CERTIFICATE-----\n...")
    .add_data("tls.key", "-----BEGIN PRIVATE KEY-----\n..."))
```

### SSH Keys

```python
# SSH key for Git repositories
ssh_secret = (Secret("git-ssh-key")
    .type("kubernetes.io/ssh-auth")
    .ssh_key(
        private_key_file="path/to/id_rsa",
        known_hosts_file="path/to/known_hosts"
    ))

# From key content
ssh_secret = (Secret("deploy-key")
    .type("kubernetes.io/ssh-auth")
    .add_data("ssh-privatekey", "-----BEGIN OPENSSH PRIVATE KEY-----\n...")
    .add_data("known_hosts", "github.com ssh-rsa AAAAB3N..."))
```

### Basic Auth

```python
# HTTP basic authentication
basic_auth = (Secret("basic-auth")
    .type("kubernetes.io/basic-auth")
    .basic_auth("admin", "secret-password"))
```

## Advanced Configuration

### Base64 Encoding

```python
# Automatically encode values
secret = (Secret("encoded-secret")
    .add_data("key1", "value1")  # Automatically base64 encoded
    .add_data_raw("key2", "dmFsdWUy"))  # Already base64 encoded

# Binary data
secret = (Secret("binary-secret")
    .add_file("config.json", "/path/to/config.json")
    .add_file("certificate.p12", "/path/to/cert.p12"))
```

### Immutable Secrets

```python
# Immutable secret (cannot be updated)
immutable_secret = (Secret("immutable-config")
    .add_data("license-key", "abcd-1234-efgh-5678")
    .immutable(True))
```

### Namespace and Labels

```python
# Organized secret with metadata
secret = (Secret("production-secrets")
    .namespace("production")
    .add_data("db-password", "prod-db-secret")
    .add_data("api-key", "prod-api-key")
    .label("environment", "production")
    .label("component", "database")
    .annotation("managed-by", "k8s-gen")
    .annotation("rotation-policy", "90-days"))
```

## Complete Examples

### Database Secrets

```python
#!/usr/bin/env python3
"""
Database Secret Management
"""

from src.k8s_gen import Secret, App, StatefulApp, KubernetesOutput

def create_database_secrets():
    # Main database credentials
    postgres_secret = (Secret("postgres-credentials")
        .namespace("database")
        .add_data("username", "postgres")
        .add_data("password", "super-secure-password-123")
        .add_data("replication-username", "replicator")
        .add_data("replication-password", "replication-secret-456")
        .add_data("database-url", "postgresql://postgres:super-secure-password-123@postgres:5432/myapp")
        .label("component", "database")
        .annotation("rotation-date", "2024-01-01"))
    
    # Application database user
    app_db_secret = (Secret("app-database-credentials")
        .namespace("application")
        .add_data("username", "app_user")
        .add_data("password", "app-user-password-789")
        .add_data("readonly-username", "readonly_user")
        .add_data("readonly-password", "readonly-password-abc")
        .label("component", "application")
        .annotation("purpose", "application-database-access"))
    
    # PostgreSQL instance
    postgres = (StatefulApp("postgres")
        .image("postgres:15")
        .namespace("database")
        .port(5432, "postgres")
        .env_from_secret("postgres-credentials", "POSTGRES_USER", "username")
        .env_from_secret("postgres-credentials", "POSTGRES_PASSWORD", "password")
        .env("POSTGRES_DB", "myapp")
        .storage("/var/lib/postgresql/data", "100Gi")
        .replicas(3))
    
    # Application using the database
    app = (App("web-app")
        .image("myapp:latest")
        .namespace("application")
        .port(8080, "http")
        .env_from_secret("app-database-credentials", "DATABASE_URL", 
                         "postgresql://app_user:app-user-password-789@postgres.database:5432/myapp")
        .replicas(3))
    
    return postgres_secret, app_db_secret, postgres, app

if __name__ == "__main__":
    components = create_database_secrets()
    
    output = KubernetesOutput()
    for component in components:
        output.generate(component, "database-setup/")
    
    print("✅ Database secrets and applications generated!")
    print("🚀 Deploy: kubectl apply -f database-setup/")
```

### Multi-Service Secrets

```python
def create_microservices_secrets():
    # Shared secrets for all services
    shared_secrets = (Secret("shared-secrets")
        .namespace("microservices")
        .add_data("jwt-secret", "shared-jwt-signing-key-xyz")
        .add_data("encryption-key", "shared-encryption-key-123")
        .add_data("service-mesh-ca", "-----BEGIN CERTIFICATE-----\n...")
        .label("scope", "shared"))
    
    # Service-specific secrets
    user_service_secret = (Secret("user-service-secrets")
        .namespace("microservices")
        .add_data("oauth-client-id", "user-service-oauth-id")
        .add_data("oauth-client-secret", "user-service-oauth-secret")
        .add_data("email-api-key", "sendgrid-api-key-for-users")
        .label("service", "user-service"))
    
    payment_service_secret = (Secret("payment-service-secrets")
        .namespace("microservices")
        .add_data("stripe-api-key", "sk_live_stripe_api_key")
        .add_data("paypal-client-id", "paypal-client-id")
        .add_data("paypal-client-secret", "paypal-client-secret")
        .label("service", "payment-service"))
    
    # External service credentials
    external_secrets = (Secret("external-api-keys")
        .namespace("microservices")
        .add_data("aws-access-key", "AKIA...")
        .add_data("aws-secret-key", "secret-key...")
        .add_data("gcp-service-account", '{"type": "service_account", ...}')
        .add_data("monitoring-api-key", "datadog-api-key")
        .label("scope", "external-services"))
    
    return shared_secrets, user_service_secret, payment_service_secret, external_secrets
```

### TLS and Certificate Management

```python
def create_tls_secrets():
    # Main application TLS certificate
    app_tls = (Secret("app-tls-cert")
        .namespace("web")
        .type("kubernetes.io/tls")
        .add_data("tls.crt", """-----BEGIN CERTIFICATE-----
MIIDXTCCAkWgAwIBAgIJAKKKKKKKKKKKMA0GCSqGSIb3DQEBCwUAMEUxCzAJBgNV
...
-----END CERTIFICATE-----""")
        .add_data("tls.key", """-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC9s9s9s9s9s9s9
...
-----END PRIVATE KEY-----""")
        .label("component", "tls")
        .annotation("cert-manager.io/cluster-issuer", "letsencrypt-prod"))
    
    # Certificate Authority for internal services
    internal_ca = (Secret("internal-ca")
        .namespace("istio-system")
        .type("kubernetes.io/tls")
        .add_data("ca.crt", "-----BEGIN CERTIFICATE-----\n...")
        .add_data("ca.key", "-----BEGIN PRIVATE KEY-----\n...")
        .label("component", "service-mesh"))
    
    # Docker registry with TLS
    registry_tls = (Secret("registry-tls")
        .namespace("registry")
        .type("kubernetes.io/tls")
        .tls_certificate(
            cert_file="certs/registry.crt",
            key_file="certs/registry.key"
        ))
    
    return app_tls, internal_ca, registry_tls
```

## Secret Usage in Applications

### Environment Variables

```python
# Use secrets as environment variables
app = (App("secure-app")
    .image("myapp:latest")
    .env_from_secret("app-secrets", "DATABASE_PASSWORD", "db-password")
    .env_from_secret("api-keys", "STRIPE_KEY", "stripe-api-key")
    .env_from_secret("auth-tokens", "JWT_SECRET", "jwt-secret"))
```

### Volume Mounts

```python
# Mount secrets as files
app = (App("file-based-app")
    .image("myapp:latest")
    .secret_volume("/etc/secrets", "app-secrets")
    .secret_volume("/etc/certs", "tls-certs")
    .secret_volume("/etc/ssh", "ssh-keys"))
```

### Image Pull Secrets

```python
# Use registry secrets for private images
app = (App("private-app")
    .image("private-registry.com/myapp:latest")
    .image_pull_secret("registry-credentials"))

# Service account with image pull secrets
from src.k8s_gen import ServiceAccount

sa = (ServiceAccount("app-sa")
    .add_image_pull_secret("registry-credentials")
    .add_image_pull_secret("backup-registry"))
```

## Generated YAML

### Generic Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: production
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded 'admin'
  password: c3VwZXJzZWNyZXQ=  # base64 encoded 'supersecret'
```

### Docker Registry Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: docker-registry
type: kubernetes.io/dockerconfigjson
data:
  .dockerconfigjson: eyJhdXRocyI6eyJwcml2YXRlLXJlZ2lzdHJ5LmNvbSI6eyJ1c2VybmFtZSI6ImRlcGxveS11c2VyIiwicGFzc3dvcmQiOiJkZXBsb3ktdG9rZW4iLCJhdXRoIjoiWkdWd2JHOTVMWFZ6WlhJNlpHVndiRzk1TFhSdmEyVnUifX19
```

### TLS Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-cert
type: kubernetes.io/tls
data:
  tls.crt: LS0tLS1CRUdJTi...  # base64 encoded certificate
  tls.key: LS0tLS1CRUdJTi...  # base64 encoded private key
```

## Security Best Practices

!!! tip "Secret Security Guidelines"
    
    **Access Control:**
    - Use RBAC to limit secret access
    - Follow principle of least privilege
    - Regularly audit secret permissions
    
    **Storage:**
    - Enable encryption at rest
    - Use external secret management when possible
    - Avoid storing secrets in container images
    
    **Rotation:**
    - Implement regular secret rotation
    - Use short-lived tokens where possible
    - Monitor secret usage and access
    
    **Development:**
    - Never commit secrets to version control
    - Use different secrets per environment
    - Implement secret scanning in CI/CD

## Secret Management Patterns

### Secret Rotation

```python
# Versioned secrets for rotation
current_secret = Secret("db-password-v2").add_data("password", "new-password")
old_secret = Secret("db-password-v1").add_data("password", "old-password")

# Gradual migration
app_new = App("app-new").env_from_secret("db-password-v2", "DB_PASS", "password")
app_old = App("app-old").env_from_secret("db-password-v1", "DB_PASS", "password")
```

### Environment-Specific Secrets

```python
# Different secrets per environment
dev_secrets = Secret("app-secrets-dev").namespace("development")
staging_secrets = Secret("app-secrets-staging").namespace("staging")
prod_secrets = Secret("app-secrets-prod").namespace("production")
```

### External Secret Management

```python
# Reference to external secret manager
external_secret = (Secret("external-ref")
    .annotation("external-secrets.io/backend", "vault")
    .annotation("external-secrets.io/key", "secret/myapp")
    .annotation("external-secrets.io/property", "password"))
```

## Troubleshooting

### Common Secret Issues

!!! warning "Secret Not Found"
    ```bash
    # Check if secret exists
    kubectl get secrets -n <namespace>
    kubectl describe secret <secret-name> -n <namespace>
    
    # Verify secret data
    kubectl get secret <secret-name> -o yaml
    ```

!!! warning "Permission Denied"
    ```bash
    # Check RBAC permissions
    kubectl auth can-i get secrets --as=system:serviceaccount:<namespace>:<sa-name>
    
    # Check service account
    kubectl describe serviceaccount <sa-name>
    ```

!!! warning "Mount Issues"
    ```bash
    # Check pod secret mounts
    kubectl describe pod <pod-name>
    kubectl exec <pod-name> -- ls -la /etc/secrets/
    ```

## API Reference

::: src.k8s_gen.security.secret.Secret
    options:
      show_source: false
      heading_level: 3

## Related Components

- **[App](../core/app.md)** - Using secrets in applications
- **[ServiceAccount](rbac.md#serviceaccount)** - Image pull secrets
- **[ConfigMap](../storage/config-map.md)** - Non-sensitive configuration
- **[SecurityPolicy](security-policy.md)** - Security policies

---

**Next:** Learn about [SecurityPolicy](security-policy.md) for pod security standards. 