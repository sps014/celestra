"""
Secret class for managing Kubernetes secrets in Celestraa DSL.

This module contains the Secret class for handling sensitive data like passwords,
API keys, and certificates with multiple sources and mounting options.
"""

import base64
import secrets
import string
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..core.base_builder import BaseBuilder
from ..utils.helpers import validate_name, sanitize_env_var_name


class Secret(BaseBuilder):
    """
    Builder class for Kubernetes secrets.
    
    The Secret class provides a fluent API for managing sensitive data
    with support for multiple data sources, mounting options, and
    automatic secret generation.
    
    Example:
        ```python
        secret = (Secret("app-secrets")
            .add("username", "admin")
            .add("password", "secret123")
            .from_env_file(".env.secrets")
            .mount_path("/etc/secrets")
            .mount_as_env_vars(prefix="APP_"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the Secret builder.
        
        Args:
            name: Name of the secret
        """
        super().__init__(name)
        self._data: Dict[str, str] = {}
        self._string_data: Dict[str, str] = {}
        self._files: Dict[str, str] = {}
        self._secret_type: str = "Opaque"
        self._mount_path: Optional[str] = None
        self._mount_as_env: bool = False
        self._env_prefix: str = ""
        self._external_sources: List[Dict[str, Any]] = []
        self._generated_secrets: Dict[str, Dict[str, Any]] = {}
        self._vault_config: Optional[Dict[str, Any]] = None
        self._cloud_config: Optional[Dict[str, Any]] = None
    
    def add(self, key: str, value: str) -> "Secret":
        """
        Add a key-value pair to the secret.
        
        Args:
            key: Secret key
            value: Secret value
            
        Returns:
            Secret: Self for method chaining
        """
        self._string_data[key] = value
        return self
    
    def add_binary(self, key: str, value: bytes) -> "Secret":
        """
        Add binary data to the secret.
        
        Args:
            key: Secret key
            value: Binary data
            
        Returns:
            Secret: Self for method chaining
        """
        encoded_value = base64.b64encode(value).decode('utf-8')
        self._data[key] = encoded_value
        return self
    
    def from_file(self, key: str, file_path: str) -> "Secret":
        """
        Add data from a file.
        
        Args:
            key: Secret key
            file_path: Path to the file
            
        Returns:
            Secret: Self for method chaining
        """
        self._files[key] = file_path
        return self
    
    def from_env_file(self, file_path: str, prefix: str = "") -> "Secret":
        """
        Load secrets from an environment file.
        
        Args:
            file_path: Path to the environment file
            prefix: Prefix to add to environment variable names
            
        Returns:
            Secret: Self for method chaining
        """
        self._external_sources.append({
            "type": "env_file",
            "path": file_path,
            "prefix": prefix
        })
        return self
    
    def from_vault(
        self, 
        path: str,
        mapping: Optional[Dict[str, str]] = None,
        auth_method: str = "token",
        **auth_config
    ) -> "Secret":
        """
        Load secrets from HashiCorp Vault.
        
        Args:
            path: Vault secret path
            mapping: Mapping of Vault keys to secret keys
            auth_method: Vault authentication method
            **auth_config: Authentication configuration
            
        Returns:
            Secret: Self for method chaining
        """
        self._vault_config = {
            "path": path,
            "mapping": mapping or {},
            "auth_method": auth_method,
            "auth_config": auth_config
        }
        return self
    
    def vault_auth(self, method: str, **config) -> "Secret":
        """
        Configure Vault authentication.
        
        Args:
            method: Authentication method (token, kubernetes, etc.)
            **config: Authentication configuration
            
        Returns:
            Secret: Self for method chaining
        """
        if self._vault_config:
            self._vault_config["auth_method"] = method
            self._vault_config["auth_config"] = config
        return self
    
    def from_cloud_parameter_store(self, path_prefix: str, **config) -> "Secret":
        """
        Load secrets from cloud parameter store.
        
        Args:
            path_prefix: Parameter path prefix
            **config: Cloud provider configuration
            
        Returns:
            Secret: Self for method chaining
        """
        self._cloud_config = {
            "type": "parameter_store",
            "path_prefix": path_prefix,
            "config": config
        }
        return self
    
    def from_cloud_secrets_manager(self, secret_name: str, **config) -> "Secret":
        """
        Load secrets from cloud secrets manager.
        
        Args:
            secret_name: Name of the secret in cloud provider
            **config: Cloud provider configuration
            
        Returns:
            Secret: Self for method chaining
        """
        self._cloud_config = {
            "type": "secrets_manager",
            "secret_name": secret_name,
            "config": config
        }
        return self
    
    def generate_password(
        self, 
        key: str,
        length: int = 32,
        include_special: bool = True
    ) -> "Secret":
        """
        Generate a random password.
        
        Args:
            key: Secret key for the password
            length: Password length
            include_special: Include special characters
            
        Returns:
            Secret: Self for method chaining
        """
        self._generated_secrets[key] = {
            "type": "password",
            "length": length,
            "include_special": include_special
        }
        return self
    
    def generate_rsa_key_pair(
        self, 
        private_key: str,
        public_key: str,
        key_size: int = 2048
    ) -> "Secret":
        """
        Generate RSA key pair.
        
        Args:
            private_key: Key name for private key
            public_key: Key name for public key
            key_size: RSA key size in bits
            
        Returns:
            Secret: Self for method chaining
        """
        self._generated_secrets[f"{private_key}_pair"] = {
            "type": "rsa_key_pair",
            "private_key": private_key,
            "public_key": public_key,
            "key_size": key_size
        }
        return self
    
    def generate_random(self, key: str, length: int = 64) -> "Secret":
        """
        Generate random bytes encoded as base64.
        
        Args:
            key: Secret key
            length: Number of random bytes
            
        Returns:
            Secret: Self for method chaining
        """
        self._generated_secrets[key] = {
            "type": "random",
            "length": length
        }
        return self
    
    def type(self, secret_type: str) -> "Secret":
        """
        Set the secret type.
        
        Args:
            secret_type: Kubernetes secret type (Opaque, TLS, etc.)
            
        Returns:
            Secret: Self for method chaining
        """
        self._secret_type = secret_type
        return self
    
    def mount_path(self, path: str) -> "Secret":
        """
        Set the mount path for the secret as a volume.
        
        Args:
            path: Mount path in the container
            
        Returns:
            Secret: Self for method chaining
        """
        self._mount_path = path
        return self
    
    def mount_as_env_vars(self, prefix: str = "") -> "Secret":
        """
        Mount secret data as environment variables.
        
        Args:
            prefix: Prefix for environment variable names
            
        Returns:
            Secret: Self for method chaining
        """
        self._mount_as_env = True
        self._env_prefix = prefix
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes Secret resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the Secret resource
        """
        # Process external sources and generated secrets
        self._process_external_sources()
        self._process_generated_secrets()
        self._process_files()
        
        secret = {
            "apiVersion": "v1",
            "kind": "Secret",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "type": self._secret_type
        }
        
        if self._namespace:
            secret["metadata"]["namespace"] = self._namespace
        
        # Add data
        if self._data:
            secret["data"] = self._data
        
        if self._string_data:
            secret["stringData"] = self._string_data
        
        return [secret]
    
    def _process_external_sources(self) -> None:
        """Process external secret sources."""
        for source in self._external_sources:
            if source["type"] == "env_file":
                self._load_from_env_file(source["path"], source.get("prefix", ""))
    
    def _process_generated_secrets(self) -> None:
        """Process generated secrets."""
        for key, config in self._generated_secrets.items():
            if config["type"] == "password":
                password = self._generate_password(
                    config["length"], 
                    config["include_special"]
                )
                self._string_data[key] = password
            
            elif config["type"] == "rsa_key_pair":
                private_key, public_key = self._generate_rsa_key_pair(config["key_size"])
                self._string_data[config["private_key"]] = private_key
                self._string_data[config["public_key"]] = public_key
            
            elif config["type"] == "random":
                random_data = self._generate_random_bytes(config["length"])
                self._data[key] = base64.b64encode(random_data).decode('utf-8')
    
    def _process_files(self) -> None:
        """Process file sources."""
        for key, file_path in self._files.items():
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                    self._data[key] = base64.b64encode(content).decode('utf-8')
            except FileNotFoundError:
                # In a real implementation, this would be handled differently
                # For now, we'll add a placeholder
                self._string_data[key] = f"# File not found: {file_path}"
    
    def _load_from_env_file(self, file_path: str, prefix: str) -> None:
        """Load environment variables from file."""
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        
                        if prefix:
                            key = f"{prefix}{key}"
                        
                        self._string_data[key] = value
        except FileNotFoundError:
            # In a real implementation, this would be handled differently
            pass
    
    def _generate_password(self, length: int, include_special: bool) -> str:
        """Generate a random password."""
        chars = string.ascii_letters + string.digits
        if include_special:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    def _generate_rsa_key_pair(self, key_size: int) -> tuple:
        """Generate RSA key pair."""
        # In a real implementation, this would use a proper crypto library
        # For now, returning placeholders
        private_key = f"-----BEGIN RSA PRIVATE KEY-----\n(Generated {key_size}-bit private key)\n-----END RSA PRIVATE KEY-----"
        public_key = f"-----BEGIN PUBLIC KEY-----\n(Generated {key_size}-bit public key)\n-----END PUBLIC KEY-----"
        return private_key, public_key
    
    def _generate_random_bytes(self, length: int) -> bytes:
        """Generate random bytes."""
        return secrets.token_bytes(length)
    
    def get_env_var_mappings(self) -> List[Dict[str, Any]]:
        """
        Get environment variable mappings for container specs.
        
        Returns:
            List[Dict[str, Any]]: List of env var configurations
        """
        if not self._mount_as_env:
            return []
        
        env_vars = []
        
        # Add string data
        for key in self._string_data.keys():
            env_name = sanitize_env_var_name(f"{self._env_prefix}{key}")
            env_vars.append({
                "name": env_name,
                "valueFrom": {
                    "secretKeyRef": {
                        "name": self._name,
                        "key": key
                    }
                }
            })
        
        # Add binary data
        for key in self._data.keys():
            env_name = sanitize_env_var_name(f"{self._env_prefix}{key}")
            env_vars.append({
                "name": env_name,
                "valueFrom": {
                    "secretKeyRef": {
                        "name": self._name,
                        "key": key
                    }
                }
            })
        
        return env_vars
    
    def get_volume_mount(self) -> Optional[Dict[str, Any]]:
        """
        Get volume mount configuration.
        
        Returns:
            Optional[Dict[str, Any]]: Volume mount configuration if mount_path is set
        """
        if not self._mount_path:
            return None
        
        return {
            "name": f"{self._name}-volume",
            "mountPath": self._mount_path,
            "readOnly": True
        }
    
    def get_volume(self) -> Optional[Dict[str, Any]]:
        """
        Get volume configuration.
        
        Returns:
            Optional[Dict[str, Any]]: Volume configuration if mount_path is set
        """
        if not self._mount_path:
            return None
        
        return {
            "name": f"{self._name}-volume",
            "secret": {
                "secretName": self._name
            }
        }
    
    def validate(self) -> List[str]:
        """
        Validate the secret configuration.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = super().validate()
        
        # Check if secret has any data
        has_data = (
            self._data or 
            self._string_data or 
            self._files or 
            self._external_sources or 
            self._generated_secrets or
            self._vault_config or
            self._cloud_config
        )
        
        if not has_data:
            errors.append("Secret must contain at least one data source")
        
        # Validate TLS secrets
        if self._secret_type == "kubernetes.io/tls":
            if "tls.crt" not in self._files and "tls.crt" not in self._string_data:
                errors.append("TLS secret must contain 'tls.crt'")
            if "tls.key" not in self._files and "tls.key" not in self._string_data:
                errors.append("TLS secret must contain 'tls.key'")
        
        return errors 