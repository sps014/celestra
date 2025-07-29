# Secret Class

The `Secret` class manages Kubernetes secrets for sensitive data like passwords, API keys, and certificates.

## Overview

```python
from celestra import Secret

# Basic usage
secret = Secret("db-secret").add("password", "secret123").add("username", "admin")
```

## Functions

### add(key: str, value: str) -> Secret
Add a key-value pair to the secret.

```python
# Basic secret
secret = Secret("app-secret").add("password", "secret123")

# Multiple values
secret = (Secret("api-secrets")
    .add("username", "admin")
    .add("password", "secret123")
    .add("api_key", "sk_live_..."))
```

### add_binary(key: str, value: bytes) -> Secret
Add binary data to the secret (automatically base64 encoded).

```python
# Add binary certificate
with open("cert.pem", "rb") as f:
    cert_data = f.read()
secret = Secret("tls-secret").add_binary("cert.pem", cert_data)

# Add private key
with open("private.key", "rb") as f:
    key_data = f.read()
secret = Secret("tls-secret").add_binary("private.key", key_data)
```

### from_file(key: str, file_path: str) -> Secret
Add data from a file.

```python
# Add certificate from file
secret = Secret("tls-secret").from_file("cert.pem", "certs/cert.pem")

# Add private key from file
secret = Secret("tls-secret").from_file("private.key", "certs/private.key")

# Add configuration file
secret = Secret("config-secret").from_file("config.json", "config/app.json")
```

### from_env_file(file_path: str, prefix: str = "") -> Secret
Load secrets from an environment file.

```python
# Load from .env file
secret = Secret("app-secrets").from_env_file(".env.secrets")

# Load with prefix
secret = Secret("app-secrets").from_env_file(".env.secrets", prefix="APP_")

# Example .env.secrets file:
# DB_PASSWORD=secret123
# API_KEY=sk_live_...
# JWT_SECRET=jwt-signing-key
```

### from_vault(path: str, mapping: Dict[str, str] = None, auth_method: str = "token", **auth_config) -> Secret
Load secrets from HashiCorp Vault.

```python
# Load from Vault with token auth
secret = (Secret("vault-secrets")
    .from_vault("secret/data/myapp", auth_method="token", token="hvs.xxx"))

# Load with custom mapping
mapping = {
    "db_password": "database/password",
    "api_key": "api/secret_key"
}
secret = (Secret("vault-secrets")
    .from_vault("secret/data/myapp", mapping=mapping, auth_method="token", token="hvs.xxx"))

# Load with Kubernetes auth
secret = (Secret("vault-secrets")
    .from_vault("secret/data/myapp", auth_method="kubernetes", role="myapp"))
```

### vault_auth(method: str, **config) -> Secret
Configure Vault authentication method.

```python
# Token authentication
secret = Secret("vault-secrets").vault_auth("token", token="hvs.xxx")

# Kubernetes authentication
secret = Secret("vault-secrets").vault_auth("kubernetes", role="myapp")

# AppRole authentication
secret = Secret("vault-secrets").vault_auth("approle", role_id="xxx", secret_id="yyy")
```

### from_cloud_parameter_store(path_prefix: str, **config) -> Secret
Load secrets from AWS Parameter Store.

```python
# Load from AWS Parameter Store
secret = (Secret("aws-secrets")
    .from_cloud_parameter_store("/myapp/prod", region="us-west-2"))

# Load with specific parameters
secret = (Secret("aws-secrets")
    .from_cloud_parameter_store("/myapp/prod", 
        region="us-west-2",
        with_decryption=True))
```

### from_cloud_secrets_manager(secret_name: str, **config) -> Secret
Load secrets from AWS Secrets Manager.

```python
# Load from AWS Secrets Manager
secret = (Secret("aws-secrets")
    .from_cloud_secrets_manager("myapp/prod/database", region="us-west-2"))

# Load with version
secret = (Secret("aws-secrets")
    .from_cloud_secrets_manager("myapp/prod/database", 
        region="us-west-2",
        version_id="12345678-1234-1234-1234-123456789012"))
```

### generate_password(key: str, length: int = 32, include_special: bool = True) -> Secret
Generate a secure random password.

```python
# Generate 32-character password
secret = Secret("db-secret").generate_password("password")

# Generate 16-character password without special characters
secret = Secret("db-secret").generate_password("password", length=16, include_special=False)

# Generate multiple passwords
secret = (Secret("app-secrets")
    .generate_password("db_password", length=32)
    .generate_password("api_key", length=64)
    .generate_password("jwt_secret", length=128))
```

### generate_rsa_key_pair(private_key: str, public_key: str, key_size: int = 2048) -> Secret
Generate RSA key pair.

```python
# Generate 2048-bit RSA key pair
secret = Secret("tls-secret").generate_rsa_key_pair("private.key", "public.key")

# Generate 4096-bit RSA key pair
secret = Secret("tls-secret").generate_rsa_key_pair("private.key", "public.key", key_size=4096)
```

### generate_random(key: str, length: int = 64) -> Secret
Generate random bytes.

```python
# Generate 64-byte random value
secret = Secret("app-secret").generate_random("session_secret")

# Generate 32-byte random value
secret = Secret("app-secret").generate_random("encryption_key", length=32)
```

### type(secret_type: str) -> Secret
Set the secret type.

```python
# Opaque secret (default)
secret = Secret("app-secret").type("Opaque")

# TLS secret
secret = Secret("tls-secret").type("kubernetes.io/tls")

# Docker registry secret
secret = Secret("registry-secret").type("kubernetes.io/dockerconfigjson")

# Basic auth secret
secret = Secret("auth-secret").type("kubernetes.io/basic-auth")
```

### mount_path(path: str) -> Secret
Set the mount path for the secret volume.

```python
# Mount at /etc/secrets
secret = Secret("app-secret").mount_path("/etc/secrets")

# Mount at /var/secrets
secret = Secret("app-secret").mount_path("/var/secrets")
```

### mount_as_env_vars(prefix: str = "") -> Secret
Configure secret to be mounted as environment variables.

```python
# Mount as environment variables
secret = Secret("app-secret").mount_as_env_vars()

# Mount with prefix
secret = Secret("app-secret").mount_as_env_vars(prefix="APP_")

# Example: secret with keys "username" and "password"
# Will create environment variables: APP_USERNAME and APP_PASSWORD
```

## Complete Example

```python
#!/usr/bin/env python3
"""
Complete Secret Example - Production Application Secrets
"""

import os
from celestra import Secret, KubernetesOutput

def load_config(config_path: str) -> str:
    """Load configuration from external file."""
    with open(f"configs/{config_path}", "r") as f:
        return f.read()

def create_production_secrets():
    """Create production-ready secrets."""
    
    # Database secrets
    db_secret = (Secret("database-secret")
        .add("username", "myapp")
        .add("password", "secure-password-123")
        .add("database", "myapp")
        .add("host", "postgres-service")
        .add("port", "5432")
        .mount_as_env_vars(prefix="DB_"))
    
    # API secrets
    api_secret = (Secret("api-secrets")
        .add("stripe_key", "sk_live_...")
        .add("jwt_secret", "jwt-signing-key-123")
        .add("api_key", "api-key-456")
        .mount_as_env_vars(prefix="API_"))
    
    # TLS certificates
    tls_secret = (Secret("tls-secret")
        .type("kubernetes.io/tls")
        .from_file("tls.crt", "certs/cert.pem")
        .from_file("tls.key", "certs/private.key"))
    
    # Docker registry secret
    registry_secret = (Secret("registry-secret")
        .type("kubernetes.io/dockerconfigjson")
        .add(".dockerconfigjson", '{"auths":{"registry.example.com":{"username":"user","password":"pass","auth":"dXNlcjpwYXNz"}}}'))
    
    # Generated secrets
    generated_secret = (Secret("generated-secrets")
        .generate_password("session_secret", length=64)
        .generate_password("encryption_key", length=32)
        .generate_rsa_key_pair("private.key", "public.key", key_size=2048)
        .mount_as_env_vars(prefix="GEN_"))
    
    # Vault secrets
    vault_secret = (Secret("vault-secrets")
        .from_vault("secret/data/myapp/prod", 
            mapping={
                "vault_db_password": "database/password",
                "vault_api_key": "api/secret_key"
            },
            auth_method="token",
            token="hvs.xxx")
        .mount_as_env_vars(prefix="VAULT_"))
    
    return [db_secret, api_secret, tls_secret, registry_secret, generated_secret, vault_secret]

if __name__ == "__main__":
    secrets = create_production_secrets()
    
    # Generate Kubernetes resources
    output = KubernetesOutput()
    for secret in secrets:
        output.generate(secret, "production-secrets/")
    
    print("✅ Production secrets generated!")
    print("🚀 Deploy: kubectl apply -f production-secrets/")
```

## Generated Kubernetes Resources

The Secret class generates the following Kubernetes resources:

- **Secret** - Kubernetes Secret with the specified data
- **Volume** - Volume definition for mounting secrets
- **VolumeMount** - Volume mount configuration

## Usage Patterns

### Database Secrets

```python
# PostgreSQL secrets
db_secret = (Secret("postgres-secret")
    .add("username", "postgres")
    .add("password", "secure-password")
    .add("database", "myapp")
    .mount_as_env_vars(prefix="POSTGRES_"))

# MySQL secrets
mysql_secret = (Secret("mysql-secret")
    .add("username", "root")
    .add("password", "mysql-password")
    .add("database", "myapp")
    .mount_as_env_vars(prefix="MYSQL_"))
```

### API Secrets

```python
# External API secrets
api_secret = (Secret("api-secrets")
    .add("stripe_key", "sk_live_...")
    .add("sendgrid_key", "SG.xxx")
    .add("aws_access_key", "AKIA...")
    .add("aws_secret_key", "xxx")
    .mount_as_env_vars(prefix="API_"))
```

### TLS Certificates

```python
# TLS certificate secret
tls_secret = (Secret("tls-secret")
    .type("kubernetes.io/tls")
    .from_file("tls.crt", "certs/cert.pem")
    .from_file("tls.key", "certs/private.key"))
```

### Docker Registry

```python
# Docker registry secret
registry_secret = (Secret("registry-secret")
    .type("kubernetes.io/dockerconfigjson")
    .add(".dockerconfigjson", '{"auths":{"registry.example.com":{"username":"user","password":"pass","auth":"dXNlcjpwYXNz"}}}'))
```

### Generated Secrets

```python
# Auto-generated secrets
generated_secret = (Secret("generated-secrets")
    .generate_password("db_password", length=32)
    .generate_password("jwt_secret", length=128)
    .generate_rsa_key_pair("private.key", "public.key")
    .mount_as_env_vars(prefix="GEN_"))
```

### Cloud Secrets

```python
# AWS Parameter Store
aws_secret = (Secret("aws-secrets")
    .from_cloud_parameter_store("/myapp/prod", region="us-west-2"))

# HashiCorp Vault
vault_secret = (Secret("vault-secrets")
    .from_vault("secret/data/myapp", auth_method="token", token="hvs.xxx"))
```

## Security Best Practices

### 1. Use Strong Passwords

```python
# ✅ Good: Generate strong passwords
secret = Secret("db-secret").generate_password("password", length=32, include_special=True)

# ❌ Bad: Use weak passwords
secret = Secret("db-secret").add("password", "123456")
```

### 2. Use External Files

```python
# ✅ Good: Load from external files
secret = Secret("tls-secret").from_file("cert.pem", "certs/cert.pem")

# ❌ Bad: Hardcode in code
secret = Secret("tls-secret").add("cert.pem", "-----BEGIN CERTIFICATE-----...")
```

### 3. Use Cloud Secret Managers

```python
# ✅ Good: Use cloud secret managers
secret = Secret("aws-secrets").from_cloud_secrets_manager("myapp/prod/database")

# ❌ Bad: Store secrets in code
secret = Secret("aws-secrets").add("access_key", "AKIA...")
```

### 4. Use Environment-Specific Secrets

```python
# Development
dev_secret = Secret("dev-secret").add("password", "dev-password")

# Production
prod_secret = Secret("prod-secret").from_cloud_secrets_manager("myapp/prod/database")
``` 