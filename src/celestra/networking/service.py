"""
Service class for Kubernetes Services in Celestraa DSL.
"""

from typing import Dict, List, Any, Optional
from ..core.base_builder import BaseBuilder


class Service(BaseBuilder):
    """
    Builder class for Kubernetes Services.
    """
    
    def __init__(self, name: str):
        """Initialize the Service builder."""
        super().__init__(name)
        self._ports: List[Dict[str, Any]] = []
        self._service_type: str = "ClusterIP"
        self._selector: Dict[str, str] = {}
        self._target_app: Optional[str] = None
    
    def add_port(self, name: str, port: int, target_port: int, protocol: str = "TCP") -> "Service":
        """Add a port to the service."""
        self._ports.append({
            "name": name,
            "port": port,
            "targetPort": target_port,
            "protocol": protocol
        })
        return self
    
    def type(self, service_type: str) -> "Service":
        """Set the service type."""
        self._service_type = service_type
        return self
    
    def selector(self, selector: Dict[str, str]) -> "Service":
        """Set the selector."""
        self._selector = selector
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """Generate Kubernetes Service resource."""
        service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "selector": self._selector,
                "ports": self._ports,
                "type": self._service_type
            }
        }
        
        if self._namespace:
            service["metadata"]["namespace"] = self._namespace
        
        return [service] 