"""
Ingress class for Kubernetes Ingress in Celestraa DSL.
"""

from typing import Dict, List, Any, Optional
from ..core.base_builder import BaseBuilder


class Ingress(BaseBuilder):
    """
    Builder class for Kubernetes Ingress.
    """
    
    def __init__(self, name: str):
        """Initialize the Ingress builder."""
        super().__init__(name)
        self._rules: List[Dict[str, Any]] = []
        self._tls: List[Dict[str, Any]] = []
        self._ingress_class: Optional[str] = None
    
    def host(self, hostname: str) -> "Ingress":
        """Set the hostname."""
        if not any(rule.get('host') == hostname for rule in self._rules):
            self._rules.append({
                "host": hostname,
                "http": {"paths": []}
            })
        return self
    
    def path(self, path: str, service_name: str, service_port: int, path_type: str = "Prefix") -> "Ingress":
        """Add a path to the ingress."""
        # Add to the last rule or create a new one
        if not self._rules:
            self._rules.append({"http": {"paths": []}})
        
        path_config = {
            "path": path,
            "pathType": path_type,
            "backend": {
                "service": {
                    "name": service_name,
                    "port": {"number": service_port}
                }
            }
        }
        
        self._rules[-1]["http"]["paths"].append(path_config)
        return self
    
    def tls(self, secret_name: str, hosts: List[str]) -> "Ingress":
        """Add TLS configuration."""
        self._tls.append({
            "secretName": secret_name,
            "hosts": hosts
        })
        return self
    
    def ingress_class(self, class_name: str) -> "Ingress":
        """Set the ingress class."""
        self._ingress_class = class_name
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """Generate Kubernetes Ingress resource."""
        ingress = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "rules": self._rules
            }
        }
        
        if self._namespace:
            ingress["metadata"]["namespace"] = self._namespace
        
        if self._tls:
            ingress["spec"]["tls"] = self._tls
        
        if self._ingress_class:
            ingress["spec"]["ingressClassName"] = self._ingress_class
        
        return [ingress] 