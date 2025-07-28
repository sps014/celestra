"""
RBAC classes for Kubernetes Role-Based Access Control in Celestraa DSL.

This module contains classes for managing ServiceAccounts, Roles, ClusterRoles,
RoleBindings, and ClusterRoleBindings.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class ServiceAccount(BaseBuilder):
    """
    Builder class for Kubernetes ServiceAccount.
    
    ServiceAccounts provide identity for processes running in pods
    and control access to the Kubernetes API.
    
    Example:
        ```python
        sa = (ServiceAccount("app-service-account")
            .add_secret("app-token")
            .automount_token(True)
            .add_image_pull_secret("registry-secret"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the ServiceAccount builder.
        
        Args:
            name: Name of the service account
        """
        super().__init__(name)
        self._secrets: List[str] = []
        self._image_pull_secrets: List[str] = []
        self._automount_service_account_token: Optional[bool] = None
    
    def add_secret(self, secret_name: str) -> "ServiceAccount":
        """
        Add a secret to the service account.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            ServiceAccount: Self for method chaining
        """
        if secret_name not in self._secrets:
            self._secrets.append(secret_name)
        return self
    
    def add_image_pull_secret(self, secret_name: str) -> "ServiceAccount":
        """
        Add an image pull secret to the service account.
        
        Args:
            secret_name: Name of the image pull secret
            
        Returns:
            ServiceAccount: Self for method chaining
        """
        if secret_name not in self._image_pull_secrets:
            self._image_pull_secrets.append(secret_name)
        return self
    
    def automount_token(self, enabled: bool) -> "ServiceAccount":
        """
        Set whether to automount the service account token.
        
        Args:
            enabled: Whether to automount the token
            
        Returns:
            ServiceAccount: Self for method chaining
        """
        self._automount_service_account_token = enabled
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes ServiceAccount resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the ServiceAccount resource
        """
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            }
        }
        
        if self._namespace:
            service_account["metadata"]["namespace"] = self._namespace
        
        if self._secrets:
            service_account["secrets"] = [{"name": secret} for secret in self._secrets]
        
        if self._image_pull_secrets:
            service_account["imagePullSecrets"] = [{"name": secret} for secret in self._image_pull_secrets]
        
        if self._automount_service_account_token is not None:
            service_account["automountServiceAccountToken"] = self._automount_service_account_token
        
        return [service_account]


class Role(BaseBuilder):
    """
    Builder class for Kubernetes Role.
    
    Roles define permissions within a specific namespace.
    
    Example:
        ```python
        role = (Role("pod-reader")
            .allow_get("pods")
            .allow_list("pods")
            .allow_watch("pods", "services")
            .allow_create("configmaps"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the Role builder.
        
        Args:
            name: Name of the role
        """
        super().__init__(name)
        self._rules: List[Dict[str, Any]] = []
    
    def add_rule(
        self, 
        api_groups: List[str],
        resources: List[str],
        verbs: List[str],
        resource_names: Optional[List[str]] = None
    ) -> "Role":
        """
        Add a permission rule.
        
        Args:
            api_groups: List of API groups
            resources: List of resource types
            verbs: List of allowed verbs
            resource_names: Specific resource names (optional)
            
        Returns:
            Role: Self for method chaining
        """
        rule = {
            "apiGroups": api_groups,
            "resources": resources,
            "verbs": verbs
        }
        
        if resource_names:
            rule["resourceNames"] = resource_names
        
        self._rules.append(rule)
        return self
    
    def allow_get(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow GET operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["get"])
    
    def allow_list(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow LIST operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["list"])
    
    def allow_watch(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow WATCH operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["watch"])
    
    def allow_create(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow CREATE operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["create"])
    
    def allow_update(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow UPDATE operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["update"])
    
    def allow_patch(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow PATCH operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["patch"])
    
    def allow_delete(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow DELETE operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["delete"])
    
    def allow_all(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow all operations on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["*"])
    
    def allow_read_only(self, *resources: str, api_group: str = "") -> "Role":
        """
        Allow read-only operations (get, list, watch) on resources.
        
        Args:
            *resources: Resource types
            api_group: API group (default: core)
            
        Returns:
            Role: Self for method chaining
        """
        return self.add_rule([api_group], list(resources), ["get", "list", "watch"])
    
    # Common permission patterns
    
    @classmethod
    def pod_reader(cls, name: str = "pod-reader") -> "Role":
        """
        Create a role for reading pods.
        
        Args:
            name: Role name
            
        Returns:
            Role: Configured role
        """
        return (cls(name)
            .allow_read_only("pods", "pods/log", "pods/status"))
    
    @classmethod
    def secret_manager(cls, name: str = "secret-manager") -> "Role":
        """
        Create a role for managing secrets.
        
        Args:
            name: Role name
            
        Returns:
            Role: Configured role
        """
        return (cls(name)
            .allow_all("secrets"))
    
    @classmethod
    def config_reader(cls, name: str = "config-reader") -> "Role":
        """
        Create a role for reading configuration.
        
        Args:
            name: Role name
            
        Returns:
            Role: Configured role
        """
        return (cls(name)
            .allow_read_only("configmaps", "secrets"))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes Role resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the Role resource
        """
        role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "Role",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "rules": self._rules
        }
        
        if self._namespace:
            role["metadata"]["namespace"] = self._namespace
        
        return [role]


class ClusterRole(Role):
    """
    Builder class for Kubernetes ClusterRole.
    
    ClusterRoles define permissions across the entire cluster.
    
    Example:
        ```python
        cluster_role = (ClusterRole("cluster-admin")
            .allow_all("*", api_group="*")
            .allow_read_only("nodes"))
        ```
    """
    
    @classmethod
    def cluster_admin(cls, name: str = "cluster-admin") -> "ClusterRole":
        """
        Create a cluster admin role.
        
        Args:
            name: Role name
            
        Returns:
            ClusterRole: Configured cluster role
        """
        return (cls(name)
            .add_rule(["*"], ["*"], ["*"]))
    
    @classmethod
    def node_reader(cls, name: str = "node-reader") -> "ClusterRole":
        """
        Create a role for reading nodes.
        
        Args:
            name: Role name
            
        Returns:
            ClusterRole: Configured cluster role
        """
        return (cls(name)
            .allow_read_only("nodes", "nodes/status"))
    
    @classmethod
    def namespace_admin(cls, name: str = "namespace-admin") -> "ClusterRole":
        """
        Create a role for managing namespaces.
        
        Args:
            name: Role name
            
        Returns:
            ClusterRole: Configured cluster role
        """
        return (cls(name)
            .allow_all("namespaces"))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes ClusterRole resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the ClusterRole resource
        """
        cluster_role = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRole",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "rules": self._rules
        }
        
        # ClusterRoles don't have namespaces
        return [cluster_role]


class RoleBinding(BaseBuilder):
    """
    Builder class for Kubernetes RoleBinding.
    
    RoleBindings grant permissions defined in a Role to users, groups, or service accounts.
    
    Example:
        ```python
        binding = (RoleBinding("pod-reader-binding")
            .bind_role("pod-reader")
            .to_service_account("app-service-account")
            .to_user("jane@example.com"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the RoleBinding builder.
        
        Args:
            name: Name of the role binding
        """
        super().__init__(name)
        self._role_ref: Optional[Dict[str, str]] = None
        self._subjects: List[Dict[str, str]] = []
    
    def bind_role(self, role_name: str) -> "RoleBinding":
        """
        Bind to a Role.
        
        Args:
            role_name: Name of the role
            
        Returns:
            RoleBinding: Self for method chaining
        """
        self._role_ref = {
            "apiGroup": "rbac.authorization.k8s.io",
            "kind": "Role",
            "name": role_name
        }
        return self
    
    def bind_cluster_role(self, cluster_role_name: str) -> "RoleBinding":
        """
        Bind to a ClusterRole.
        
        Args:
            cluster_role_name: Name of the cluster role
            
        Returns:
            RoleBinding: Self for method chaining
        """
        self._role_ref = {
            "apiGroup": "rbac.authorization.k8s.io",
            "kind": "ClusterRole",
            "name": cluster_role_name
        }
        return self
    
    def to_service_account(self, service_account_name: str, namespace: Optional[str] = None) -> "RoleBinding":
        """
        Bind to a service account.
        
        Args:
            service_account_name: Name of the service account
            namespace: Namespace of the service account (defaults to current namespace)
            
        Returns:
            RoleBinding: Self for method chaining
        """
        subject = {
            "kind": "ServiceAccount",
            "name": service_account_name,
            "namespace": namespace or self._namespace or "default"
        }
        self._subjects.append(subject)
        return self
    
    def to_user(self, user_name: str) -> "RoleBinding":
        """
        Bind to a user.
        
        Args:
            user_name: Name of the user
            
        Returns:
            RoleBinding: Self for method chaining
        """
        subject = {
            "kind": "User",
            "name": user_name,
            "apiGroup": "rbac.authorization.k8s.io"
        }
        self._subjects.append(subject)
        return self
    
    def to_group(self, group_name: str) -> "RoleBinding":
        """
        Bind to a group.
        
        Args:
            group_name: Name of the group
            
        Returns:
            RoleBinding: Self for method chaining
        """
        subject = {
            "kind": "Group",
            "name": group_name,
            "apiGroup": "rbac.authorization.k8s.io"
        }
        self._subjects.append(subject)
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes RoleBinding resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the RoleBinding resource
        """
        if not self._role_ref:
            raise ValueError("RoleBinding must have a role reference")
        
        if not self._subjects:
            raise ValueError("RoleBinding must have at least one subject")
        
        role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "RoleBinding",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "roleRef": self._role_ref,
            "subjects": self._subjects
        }
        
        if self._namespace:
            role_binding["metadata"]["namespace"] = self._namespace
        
        return [role_binding]


class ClusterRoleBinding(RoleBinding):
    """
    Builder class for Kubernetes ClusterRoleBinding.
    
    ClusterRoleBindings grant permissions across the entire cluster.
    
    Example:
        ```python
        binding = (ClusterRoleBinding("cluster-admin-binding")
            .bind_cluster_role("cluster-admin")
            .to_user("admin@example.com"))
        ```
    """
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes ClusterRoleBinding resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the ClusterRoleBinding resource
        """
        if not self._role_ref:
            raise ValueError("ClusterRoleBinding must have a role reference")
        
        if not self._subjects:
            raise ValueError("ClusterRoleBinding must have at least one subject")
        
        cluster_role_binding = {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "roleRef": self._role_ref,
            "subjects": self._subjects
        }
        
        # ClusterRoleBindings don't have namespaces
        return [cluster_role_binding] 