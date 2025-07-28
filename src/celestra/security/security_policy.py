"""
SecurityPolicy class for Kubernetes security configurations in Celestraa DSL.

This module contains the SecurityPolicy class for managing comprehensive security
configurations including RBAC, pod security policies, network policies, and security contexts.
"""

from typing import Dict, List, Any, Optional
from ..core.base_builder import BaseBuilder


class SecurityPolicy(BaseBuilder):
    """
    Builder class for Kubernetes security policy configurations.
    
    SecurityPolicy provides a unified interface for managing various security
    aspects including RBAC, pod security policies, network policies, and 
    security contexts.
    
    Example:
        ```python
        security = (SecurityPolicy("app-security")
            .enable_rbac()
            .pod_security_policy("restricted")
            .enable_network_policies()
            .default_security_context({
                "runAsNonRoot": True,
                "runAsUser": 1000
            }))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the SecurityPolicy builder.
        
        Args:
            name: Name of the security policy
        """
        super().__init__(name)
        self._rbac_enabled: bool = False
        self._pod_security_policy: Optional[str] = None
        self._network_policies_enabled: bool = False
        self._default_security_context: Optional[Dict[str, Any]] = None
        self._service_accounts: List[str] = []
        self._roles: List[str] = []
        self._role_bindings: List[str] = []
        self._pod_security_standards: Optional[str] = None
        self._admission_controller_config: Optional[Dict[str, Any]] = None
    
    def enable_rbac(self, enabled: bool = True) -> "SecurityPolicy":
        """
        Enable or disable RBAC policies.
        
        Args:
            enabled: Whether to enable RBAC
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        self._rbac_enabled = enabled
        return self
    
    def pod_security_policy(self, policy_name: str) -> "SecurityPolicy":
        """
        Set the pod security policy name.
        
        Args:
            policy_name: Name of the pod security policy
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        self._pod_security_policy = policy_name
        return self
    
    def pod_security_standards(self, standard: str) -> "SecurityPolicy":
        """
        Set Pod Security Standards (PSS) level.
        
        Args:
            standard: Security standard level (privileged, baseline, restricted)
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        if standard not in ["privileged", "baseline", "restricted"]:
            raise ValueError("Pod Security Standard must be one of: privileged, baseline, restricted")
        
        self._pod_security_standards = standard
        return self
    
    def enable_network_policies(self, enabled: bool = True) -> "SecurityPolicy":
        """
        Enable or disable network policies.
        
        Args:
            enabled: Whether to enable network policies
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        self._network_policies_enabled = enabled
        return self
    
    def default_security_context(self, security_context: Dict[str, Any]) -> "SecurityPolicy":
        """
        Set the default security context for containers.
        
        Args:
            security_context: Security context configuration
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        self._default_security_context = security_context
        return self
    
    def add_service_account(self, service_account_name: str) -> "SecurityPolicy":
        """
        Add a service account to this security policy.
        
        Args:
            service_account_name: Name of the service account
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        if service_account_name not in self._service_accounts:
            self._service_accounts.append(service_account_name)
        return self
    
    def add_role(self, role_name: str) -> "SecurityPolicy":
        """
        Add a role to this security policy.
        
        Args:
            role_name: Name of the role
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        if role_name not in self._roles:
            self._roles.append(role_name)
        return self
    
    def add_role_binding(self, role_binding_name: str) -> "SecurityPolicy":
        """
        Add a role binding to this security policy.
        
        Args:
            role_binding_name: Name of the role binding
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        if role_binding_name not in self._role_bindings:
            self._role_bindings.append(role_binding_name)
        return self
    
    def configure_admission_controller(self, config: Dict[str, Any]) -> "SecurityPolicy":
        """
        Configure admission controller settings.
        
        Args:
            config: Admission controller configuration
            
        Returns:
            SecurityPolicy: Self for method chaining
        """
        self._admission_controller_config = config
        return self
    
    # Preset security configurations
    
    @classmethod
    def minimal_security(cls, name: str = "minimal-security") -> "SecurityPolicy":
        """
        Create a minimal security configuration.
        
        Args:
            name: Policy name
            
        Returns:
            SecurityPolicy: Configured security policy
        """
        return cls(name)
    
    @classmethod
    def standard_security(cls, name: str = "standard-security") -> "SecurityPolicy":
        """
        Create a standard security configuration.
        
        Args:
            name: Policy name
            
        Returns:
            SecurityPolicy: Configured security policy
        """
        return (cls(name)
            .enable_rbac()
            .pod_security_standards("baseline")
            .default_security_context({
                "runAsNonRoot": True,
                "runAsUser": 1000,
                "runAsGroup": 3000,
                "fsGroup": 2000,
                "capabilities": {
                    "drop": ["ALL"]
                }
            }))
    
    @classmethod
    def strict_security(cls, name: str = "strict-security") -> "SecurityPolicy":
        """
        Create a strict security configuration.
        
        Args:
            name: Policy name
            
        Returns:
            SecurityPolicy: Configured security policy
        """
        return (cls(name)
            .enable_rbac()
            .pod_security_standards("restricted")
            .enable_network_policies()
            .default_security_context({
                "runAsNonRoot": True,
                "runAsUser": 1000,
                "runAsGroup": 3000,
                "fsGroup": 2000,
                "readOnlyRootFilesystem": True,
                "allowPrivilegeEscalation": False,
                "capabilities": {
                    "drop": ["ALL"]
                },
                "seccompProfile": {
                    "type": "RuntimeDefault"
                }
            }))
    
    def get_security_context(self) -> Optional[Dict[str, Any]]:
        """
        Get the configured security context.
        
        Returns:
            Optional[Dict[str, Any]]: Security context configuration
        """
        return self._default_security_context
    
    def is_rbac_enabled(self) -> bool:
        """
        Check if RBAC is enabled.
        
        Returns:
            bool: True if RBAC is enabled
        """
        return self._rbac_enabled
    
    def is_network_policies_enabled(self) -> bool:
        """
        Check if network policies are enabled.
        
        Returns:
            bool: True if network policies are enabled
        """
        return self._network_policies_enabled
    
    def get_pod_security_policy(self) -> Optional[str]:
        """
        Get the pod security policy name.
        
        Returns:
            Optional[str]: Pod security policy name
        """
        return self._pod_security_policy
    
    def get_pod_security_standards(self) -> Optional[str]:
        """
        Get the Pod Security Standards level.
        
        Returns:
            Optional[str]: PSS level
        """
        return self._pod_security_standards
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for the security policy.
        
        Note: SecurityPolicy is a configuration object that influences
        other resources rather than generating resources directly.
        
        Returns:
            List[Dict[str, Any]]: Empty list (no direct resources)
        """
        # SecurityPolicy doesn't generate direct resources
        # It's used to configure other resources
        resources = []
        
        # Generate namespace labels for Pod Security Standards if configured
        if self._pod_security_standards:
            namespace_patch = {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": self._namespace or "default",
                    "labels": {
                        "pod-security.kubernetes.io/enforce": self._pod_security_standards,
                        "pod-security.kubernetes.io/audit": self._pod_security_standards,
                        "pod-security.kubernetes.io/warn": self._pod_security_standards
                    }
                }
            }
            resources.append(namespace_patch)
        
        return resources 