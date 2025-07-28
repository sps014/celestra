"""
NetworkPolicy class for network security policies in Celestraa DSL.

This module contains the NetworkPolicy class for managing network
security policies to control traffic between pods.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class NetworkPolicy(BaseBuilder):
    """
    Builder class for Kubernetes NetworkPolicy.
    
    The NetworkPolicy class manages network security policies to control
    ingress and egress traffic between pods and external services.
    
    Example:
        ```python
        policy = (NetworkPolicy("app-network-policy")
            .apply_to_labels({"app": "web-app"})
            .allow_ingress_from_labels({"app": "frontend"})
            .allow_egress_to_labels({"app": "database"})
            .deny_all_ingress()
            .allow_egress_to_external(["0.0.0.0/0"]))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the NetworkPolicy builder.
        
        Args:
            name: Name of the network policy
        """
        super().__init__(name)
        self._pod_selector: Dict[str, Any] = {}
        self._policy_types: List[str] = []
        self._ingress_rules: List[Dict[str, Any]] = []
        self._egress_rules: List[Dict[str, Any]] = []
        self._default_deny_all = False
    
    def apply_to_labels(self, labels: Dict[str, str]) -> "NetworkPolicy":
        """
        Apply policy to pods with specific labels.
        
        Args:
            labels: Labels to match pods
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        self._pod_selector = {"matchLabels": labels}
        return self
    
    def apply_to_all_pods(self) -> "NetworkPolicy":
        """
        Apply policy to all pods in the namespace.
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        self._pod_selector = {}
        return self
    
    def apply_to_services(self, service_names: List[str]) -> "NetworkPolicy":
        """
        Apply policy to specific services.
        
        Args:
            service_names: List of service names
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        # Create selector for multiple services
        if len(service_names) == 1:
            self._pod_selector = {"matchLabels": {"app": service_names[0]}}
        else:
            self._pod_selector = {
                "matchExpressions": [{
                    "key": "app",
                    "operator": "In",
                    "values": service_names
                }]
            }
        return self
    
    def deny_all_ingress(self) -> "NetworkPolicy":
        """
        Deny all ingress traffic (default deny).
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Ingress" not in self._policy_types:
            self._policy_types.append("Ingress")
        # Empty ingress rules = deny all
        return self
    
    def deny_all_egress(self) -> "NetworkPolicy":
        """
        Deny all egress traffic (default deny).
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Egress" not in self._policy_types:
            self._policy_types.append("Egress")
        # Empty egress rules = deny all
        return self
    
    def allow_all_ingress(self) -> "NetworkPolicy":
        """
        Allow all ingress traffic.
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Ingress" not in self._policy_types:
            self._policy_types.append("Ingress")
        
        self._ingress_rules.append({})  # Empty rule = allow all
        return self
    
    def allow_all_egress(self) -> "NetworkPolicy":
        """
        Allow all egress traffic.
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Egress" not in self._policy_types:
            self._policy_types.append("Egress")
        
        self._egress_rules.append({})  # Empty rule = allow all
        return self
    
    def allow_ingress_from_labels(
        self, 
        labels: Dict[str, str],
        ports: Optional[List[Dict[str, Any]]] = None
    ) -> "NetworkPolicy":
        """
        Allow ingress from pods with specific labels.
        
        Args:
            labels: Labels to match source pods
            ports: Specific ports to allow (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Ingress" not in self._policy_types:
            self._policy_types.append("Ingress")
        
        rule = {
            "from": [{
                "podSelector": {"matchLabels": labels}
            }]
        }
        
        if ports:
            rule["ports"] = ports
        
        self._ingress_rules.append(rule)
        return self
    
    def allow_egress_to_labels(
        self, 
        labels: Dict[str, str],
        ports: Optional[List[Dict[str, Any]]] = None
    ) -> "NetworkPolicy":
        """
        Allow egress to pods with specific labels.
        
        Args:
            labels: Labels to match destination pods
            ports: Specific ports to allow (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Egress" not in self._policy_types:
            self._policy_types.append("Egress")
        
        rule = {
            "to": [{
                "podSelector": {"matchLabels": labels}
            }]
        }
        
        if ports:
            rule["ports"] = ports
        
        self._egress_rules.append(rule)
        return self
    
    def allow_ingress_from_namespace(
        self, 
        namespace_labels: Dict[str, str],
        ports: Optional[List[Dict[str, Any]]] = None
    ) -> "NetworkPolicy":
        """
        Allow ingress from specific namespace.
        
        Args:
            namespace_labels: Labels to match source namespace
            ports: Specific ports to allow (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Ingress" not in self._policy_types:
            self._policy_types.append("Ingress")
        
        rule = {
            "from": [{
                "namespaceSelector": {"matchLabels": namespace_labels}
            }]
        }
        
        if ports:
            rule["ports"] = ports
        
        self._ingress_rules.append(rule)
        return self
    
    def allow_egress_to_namespace(
        self, 
        namespace_labels: Dict[str, str],
        ports: Optional[List[Dict[str, Any]]] = None
    ) -> "NetworkPolicy":
        """
        Allow egress to specific namespace.
        
        Args:
            namespace_labels: Labels to match destination namespace
            ports: Specific ports to allow (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Egress" not in self._policy_types:
            self._policy_types.append("Egress")
        
        rule = {
            "to": [{
                "namespaceSelector": {"matchLabels": namespace_labels}
            }]
        }
        
        if ports:
            rule["ports"] = ports
        
        self._egress_rules.append(rule)
        return self
    
    def allow_ingress_from_external(
        self, 
        cidr_blocks: List[str],
        ports: Optional[List[Dict[str, Any]]] = None
    ) -> "NetworkPolicy":
        """
        Allow ingress from external IP ranges.
        
        Args:
            cidr_blocks: List of CIDR blocks to allow
            ports: Specific ports to allow (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Ingress" not in self._policy_types:
            self._policy_types.append("Ingress")
        
        rule = {
            "from": [{"ipBlock": {"cidr": cidr}} for cidr in cidr_blocks]
        }
        
        if ports:
            rule["ports"] = ports
        
        self._ingress_rules.append(rule)
        return self
    
    def allow_egress_to_external(
        self, 
        cidr_blocks: List[str],
        ports: Optional[List[Dict[str, Any]]] = None,
        except_cidrs: Optional[List[str]] = None
    ) -> "NetworkPolicy":
        """
        Allow egress to external IP ranges.
        
        Args:
            cidr_blocks: List of CIDR blocks to allow
            ports: Specific ports to allow (optional)
            except_cidrs: CIDR blocks to exclude from the allowed range
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        if "Egress" not in self._policy_types:
            self._policy_types.append("Egress")
        
        to_rules = []
        for cidr in cidr_blocks:
            ip_block = {"cidr": cidr}
            if except_cidrs:
                ip_block["except"] = except_cidrs
            to_rules.append({"ipBlock": ip_block})
        
        rule = {"to": to_rules}
        
        if ports:
            rule["ports"] = ports
        
        self._egress_rules.append(rule)
        return self
    
    def allow_dns(self) -> "NetworkPolicy":
        """
        Allow DNS traffic (UDP port 53).
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        return self.allow_egress_to_external(
            ["0.0.0.0/0"],
            ports=[{"protocol": "UDP", "port": 53}]
        )
    
    def allow_internal_communication(self) -> "NetworkPolicy":
        """
        Allow communication within the same namespace.
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        # Allow ingress from same namespace
        self.allow_ingress_from_namespace({})
        # Allow egress to same namespace
        self.allow_egress_to_namespace({})
        return self
    
    def allow_http_ingress(self, source_labels: Optional[Dict[str, str]] = None) -> "NetworkPolicy":
        """
        Allow HTTP ingress traffic.
        
        Args:
            source_labels: Labels to match source pods (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        ports = [
            {"protocol": "TCP", "port": 80},
            {"protocol": "TCP", "port": 8080}
        ]
        
        if source_labels:
            return self.allow_ingress_from_labels(source_labels, ports)
        else:
            return self.allow_ingress_from_external(["0.0.0.0/0"], ports)
    
    def allow_https_ingress(self, source_labels: Optional[Dict[str, str]] = None) -> "NetworkPolicy":
        """
        Allow HTTPS ingress traffic.
        
        Args:
            source_labels: Labels to match source pods (optional)
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        ports = [{"protocol": "TCP", "port": 443}]
        
        if source_labels:
            return self.allow_ingress_from_labels(source_labels, ports)
        else:
            return self.allow_ingress_from_external(["0.0.0.0/0"], ports)
    
    def allow_database_access(self, client_labels: Dict[str, str], port: int = 5432) -> "NetworkPolicy":
        """
        Allow database access from specific clients.
        
        Args:
            client_labels: Labels to match client pods
            port: Database port
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        return self.allow_ingress_from_labels(
            client_labels,
            ports=[{"protocol": "TCP", "port": port}]
        )
    
    def block_metadata_server(self) -> "NetworkPolicy":
        """
        Block access to cloud metadata servers.
        
        Returns:
            NetworkPolicy: Self for method chaining
        """
        # Block common metadata server IPs
        metadata_cidrs = [
            "169.254.169.254/32",  # AWS, GCP metadata
            "169.254.170.2/32",    # AWS ECS metadata
        ]
        
        return self.allow_egress_to_external(
            ["0.0.0.0/0"],
            except_cidrs=metadata_cidrs
        )
    
    def deny_external_access_except(self, allowed_services: List[str]) -> "NetworkPolicy":
        """
        Deny external access except for specific services.
        
        Args:
            allowed_services: List of service names that can accept external traffic
            
        Returns:
            NetworkPolicy: Self for method chaining
        """
        # Create a selector for services that should NOT have external access
        self._pod_selector = {
            "matchExpressions": [{
                "key": "app",
                "operator": "NotIn",
                "values": allowed_services
            }]
        }
        
        # Deny all ingress for these services
        self.deny_all_ingress()
        
        return self
    
    # Pre-configured policy patterns
    
    @classmethod
    def default_deny_all(cls, name: str = "default-deny-all") -> "NetworkPolicy":
        """
        Create a default deny-all policy.
        
        Args:
            name: Policy name
            
        Returns:
            NetworkPolicy: Configured policy
        """
        return (cls(name)
            .apply_to_all_pods()
            .deny_all_ingress()
            .deny_all_egress())
    
    @classmethod
    def web_tier_policy(
        cls, 
        name: str = "web-tier-policy",
        web_labels: Dict[str, str] = None
    ) -> "NetworkPolicy":
        """
        Create a policy for web tier applications.
        
        Args:
            name: Policy name
            web_labels: Labels for web tier pods
            
        Returns:
            NetworkPolicy: Configured policy
        """
        web_labels = web_labels or {"tier": "web"}
        
        return (cls(name)
            .apply_to_labels(web_labels)
            .allow_http_ingress()
            .allow_https_ingress()
            .allow_dns())
    
    @classmethod
    def app_tier_policy(
        cls, 
        name: str = "app-tier-policy",
        app_labels: Dict[str, str] = None,
        web_labels: Dict[str, str] = None
    ) -> "NetworkPolicy":
        """
        Create a policy for application tier.
        
        Args:
            name: Policy name
            app_labels: Labels for app tier pods
            web_labels: Labels for web tier pods that can access app tier
            
        Returns:
            NetworkPolicy: Configured policy
        """
        app_labels = app_labels or {"tier": "app"}
        web_labels = web_labels or {"tier": "web"}
        
        return (cls(name)
            .apply_to_labels(app_labels)
            .allow_ingress_from_labels(web_labels)
            .allow_dns())
    
    @classmethod
    def database_tier_policy(
        cls, 
        name: str = "database-tier-policy",
        db_labels: Dict[str, str] = None,
        app_labels: Dict[str, str] = None,
        port: int = 5432
    ) -> "NetworkPolicy":
        """
        Create a policy for database tier.
        
        Args:
            name: Policy name
            db_labels: Labels for database pods
            app_labels: Labels for app tier pods that can access database
            port: Database port
            
        Returns:
            NetworkPolicy: Configured policy
        """
        db_labels = db_labels or {"tier": "database"}
        app_labels = app_labels or {"tier": "app"}
        
        return (cls(name)
            .apply_to_labels(db_labels)
            .allow_database_access(app_labels, port)
            .deny_all_egress())  # Databases typically don't need outbound access
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes NetworkPolicy resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the NetworkPolicy resource
        """
        spec = {
            "podSelector": self._pod_selector
        }
        
        if self._policy_types:
            spec["policyTypes"] = self._policy_types
        
        if self._ingress_rules:
            spec["ingress"] = self._ingress_rules
        
        if self._egress_rules:
            spec["egress"] = self._egress_rules
        
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": spec
        }
        
        if self._namespace:
            network_policy["metadata"]["namespace"] = self._namespace
        
        return [network_policy] 