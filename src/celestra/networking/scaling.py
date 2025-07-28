"""
Scaling class for horizontal and vertical pod autoscaling in Celestraa DSL.

This module contains the Scaling class for managing pod autoscaling
based on CPU, memory, and custom metrics.
"""

from typing import Dict, List, Any, Optional, Union


class Scaling:
    """
    Builder class for pod autoscaling configuration.
    
    The Scaling class manages horizontal and vertical pod autoscaling
    based on resource utilization and custom metrics.
    
    Example:
        ```python
        scaling = (Scaling()
            .horizontal(min_replicas=2, max_replicas=10)
            .cpu_target(70)
            .memory_target(80)
            .custom_metric("requests_per_second", 100)
            .scale_down_stabilization("5m"))
        ```
    """
    
    def __init__(self):
        """Initialize the Scaling builder."""
        self.replicas: Optional[int] = None
        self.auto_scale_enabled: bool = False
        self.min_replicas: int = 1
        self.max_replicas: int = 10
        self.cpu_target: Optional[int] = None
        self.memory_target: Optional[int] = None
        self.custom_metrics: List[Dict[str, Any]] = []
        self.behavior: Dict[str, Any] = {}
        self.vertical_scaling: bool = False
        self.vpa_config: Dict[str, Any] = {}
    
    def horizontal(self, min_replicas: int = 1, max_replicas: int = 10) -> "Scaling":
        """
        Enable horizontal pod autoscaling.
        
        Args:
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas
            
        Returns:
            Scaling: Self for method chaining
        """
        self.auto_scale_enabled = True
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        return self
    
    def vertical(
        self, 
        mode: str = "Auto",
        cpu_policy: str = "Auto",
        memory_policy: str = "Auto"
    ) -> "Scaling":
        """
        Enable vertical pod autoscaling.
        
        Args:
            mode: VPA mode ("Off", "Initial", "Auto")
            cpu_policy: CPU scaling policy ("Off", "Auto")
            memory_policy: Memory scaling policy ("Off", "Auto")
            
        Returns:
            Scaling: Self for method chaining
        """
        self.vertical_scaling = True
        self.vpa_config = {
            "updateMode": mode,
            "resourcePolicy": {
                "containerPolicies": [{
                    "containerName": "*",
                    "controlledResources": [],
                    "maxAllowed": {},
                    "minAllowed": {}
                }]
            }
        }
        
        if cpu_policy != "Off":
            self.vpa_config["resourcePolicy"]["containerPolicies"][0]["controlledResources"].append("cpu")
        
        if memory_policy != "Off":
            self.vpa_config["resourcePolicy"]["containerPolicies"][0]["controlledResources"].append("memory")
        
        return self
    
    def cpu_target(self, percentage: int) -> "Scaling":
        """
        Set CPU utilization target for autoscaling.
        
        Args:
            percentage: Target CPU utilization percentage (1-100)
            
        Returns:
            Scaling: Self for method chaining
        """
        if not 1 <= percentage <= 100:
            raise ValueError("CPU target percentage must be between 1 and 100")
        
        self.cpu_target = percentage
        self.auto_scale_enabled = True
        return self
    
    def memory_target(self, percentage: int) -> "Scaling":
        """
        Set memory utilization target for autoscaling.
        
        Args:
            percentage: Target memory utilization percentage (1-100)
            
        Returns:
            Scaling: Self for method chaining
        """
        if not 1 <= percentage <= 100:
            raise ValueError("Memory target percentage must be between 1 and 100")
        
        self.memory_target = percentage
        self.auto_scale_enabled = True
        return self
    
    def custom_metric(
        self, 
        metric_name: str,
        target_value: Union[int, float],
        metric_type: str = "Object"
    ) -> "Scaling":
        """
        Add custom metric for autoscaling.
        
        Args:
            metric_name: Name of the custom metric
            target_value: Target value for the metric
            metric_type: Type of metric ("Object", "Pods", "External")
            
        Returns:
            Scaling: Self for method chaining
        """
        custom_metric = {
            "type": metric_type,
            "object": {
                "metric": {"name": metric_name},
                "target": {
                    "type": "Value",
                    "value": str(target_value)
                }
            }
        }
        
        if metric_type == "Pods":
            custom_metric = {
                "type": "Pods",
                "pods": {
                    "metric": {"name": metric_name},
                    "target": {
                        "type": "AverageValue",
                        "averageValue": str(target_value)
                    }
                }
            }
        elif metric_type == "External":
            custom_metric = {
                "type": "External",
                "external": {
                    "metric": {"name": metric_name},
                    "target": {
                        "type": "Value", 
                        "value": str(target_value)
                    }
                }
            }
        
        self.custom_metrics.append(custom_metric)
        self.auto_scale_enabled = True
        return self
    
    def requests_per_second(self, target_rps: Union[int, float]) -> "Scaling":
        """
        Scale based on requests per second.
        
        Args:
            target_rps: Target requests per second per pod
            
        Returns:
            Scaling: Self for method chaining
        """
        return self.custom_metric("http_requests_per_second", target_rps, "Pods")
    
    def queue_length(self, target_length: int) -> "Scaling":
        """
        Scale based on queue length.
        
        Args:
            target_length: Target queue length
            
        Returns:
            Scaling: Self for method chaining
        """
        return self.custom_metric("queue_length", target_length, "Object")
    
    def scale_up_behavior(
        self,
        stabilization_window: str = "0s",
        max_replicas_per_period: int = 4,
        period_seconds: int = 60
    ) -> "Scaling":
        """
        Configure scale-up behavior.
        
        Args:
            stabilization_window: Stabilization window for scale up
            max_replicas_per_period: Max replicas to add per period
            period_seconds: Period duration in seconds
            
        Returns:
            Scaling: Self for method chaining
        """
        self.behavior.setdefault("scaleUp", {})
        self.behavior["scaleUp"]["stabilizationWindowSeconds"] = self._parse_duration(stabilization_window)
        self.behavior["scaleUp"]["policies"] = [{
            "type": "Pods",
            "value": max_replicas_per_period,
            "periodSeconds": period_seconds
        }]
        return self
    
    def scale_down_behavior(
        self,
        stabilization_window: str = "300s",
        max_replicas_per_period: int = 2,
        period_seconds: int = 60
    ) -> "Scaling":
        """
        Configure scale-down behavior.
        
        Args:
            stabilization_window: Stabilization window for scale down
            max_replicas_per_period: Max replicas to remove per period
            period_seconds: Period duration in seconds
            
        Returns:
            Scaling: Self for method chaining
        """
        self.behavior.setdefault("scaleDown", {})
        self.behavior["scaleDown"]["stabilizationWindowSeconds"] = self._parse_duration(stabilization_window)
        self.behavior["scaleDown"]["policies"] = [{
            "type": "Pods",
            "value": max_replicas_per_period,
            "periodSeconds": period_seconds
        }]
        return self
    
    def scale_down_stabilization(self, window: str) -> "Scaling":
        """
        Set scale-down stabilization window.
        
        Args:
            window: Stabilization window duration (e.g., "5m", "300s")
            
        Returns:
            Scaling: Self for method chaining
        """
        return self.scale_down_behavior(stabilization_window=window)
    
    def conservative_scaling(self) -> "Scaling":
        """
        Configure conservative scaling behavior.
        
        Returns:
            Scaling: Self for method chaining
        """
        return (self
            .scale_up_behavior(stabilization_window="30s", max_replicas_per_period=2, period_seconds=60)
            .scale_down_behavior(stabilization_window="600s", max_replicas_per_period=1, period_seconds=60))
    
    def aggressive_scaling(self) -> "Scaling":
        """
        Configure aggressive scaling behavior.
        
        Returns:
            Scaling: Self for method chaining
        """
        return (self
            .scale_up_behavior(stabilization_window="0s", max_replicas_per_period=10, period_seconds=30)
            .scale_down_behavior(stabilization_window="60s", max_replicas_per_period=5, period_seconds=30))
    
    def predictive_scaling(self, time_window: str = "1h") -> "Scaling":
        """
        Enable predictive scaling (placeholder for future implementation).
        
        Args:
            time_window: Time window for prediction
            
        Returns:
            Scaling: Self for method chaining
        """
        # This would integrate with predictive scaling systems
        # For now, just add it as an annotation
        return self
    
    def cost_optimized(self, max_cost_per_hour: float = None) -> "Scaling":
        """
        Configure cost-optimized scaling.
        
        Args:
            max_cost_per_hour: Maximum cost per hour
            
        Returns:
            Scaling: Self for method chaining
        """
        # Conservative scaling to minimize costs
        self.conservative_scaling()
        
        # Prefer scale-down over scale-up
        return self.scale_down_behavior(
            stabilization_window="60s", 
            max_replicas_per_period=3, 
            period_seconds=30
        )
    
    def vpa_resource_limits(
        self,
        cpu_min: str = "100m",
        cpu_max: str = "2000m", 
        memory_min: str = "128Mi",
        memory_max: str = "4Gi"
    ) -> "Scaling":
        """
        Set VPA resource limits.
        
        Args:
            cpu_min: Minimum CPU allocation
            cpu_max: Maximum CPU allocation
            memory_min: Minimum memory allocation
            memory_max: Maximum memory allocation
            
        Returns:
            Scaling: Self for method chaining
        """
        if not self.vertical_scaling:
            self.vertical()
        
        container_policy = self.vpa_config["resourcePolicy"]["containerPolicies"][0]
        container_policy["minAllowed"] = {
            "cpu": cpu_min,
            "memory": memory_min
        }
        container_policy["maxAllowed"] = {
            "cpu": cpu_max,
            "memory": memory_max
        }
        
        return self
    
    def _parse_duration(self, duration: str) -> int:
        """Parse duration string to seconds."""
        duration = duration.strip().lower()
        
        if duration.endswith('s'):
            return int(duration[:-1])
        elif duration.endswith('m'):
            return int(duration[:-1]) * 60
        elif duration.endswith('h'):
            return int(duration[:-1]) * 3600
        elif duration.endswith('d'):
            return int(duration[:-1]) * 86400
        else:
            # Assume seconds if no unit
            return int(duration)
    
    def get_hpa_spec(self, target_name: str) -> Optional[Dict[str, Any]]:
        """
        Get HorizontalPodAutoscaler specification.
        
        Args:
            target_name: Name of the target deployment/statefulset
            
        Returns:
            Optional[Dict[str, Any]]: HPA specification
        """
        if not self.auto_scale_enabled:
            return None
        
        hpa_spec = {
            "scaleTargetRef": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": target_name
            },
            "minReplicas": self.min_replicas,
            "maxReplicas": self.max_replicas,
            "metrics": []
        }
        
        # Add CPU metric
        if self.cpu_target:
            hpa_spec["metrics"].append({
                "type": "Resource",
                "resource": {
                    "name": "cpu",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": self.cpu_target
                    }
                }
            })
        
        # Add memory metric
        if self.memory_target:
            hpa_spec["metrics"].append({
                "type": "Resource",
                "resource": {
                    "name": "memory",
                    "target": {
                        "type": "Utilization",
                        "averageUtilization": self.memory_target
                    }
                }
            })
        
        # Add custom metrics
        hpa_spec["metrics"].extend(self.custom_metrics)
        
        # Add behavior configuration
        if self.behavior:
            hpa_spec["behavior"] = self.behavior
        
        return hpa_spec
    
    def get_vpa_spec(self, target_name: str) -> Optional[Dict[str, Any]]:
        """
        Get VerticalPodAutoscaler specification.
        
        Args:
            target_name: Name of the target deployment/statefulset
            
        Returns:
            Optional[Dict[str, Any]]: VPA specification
        """
        if not self.vertical_scaling:
            return None
        
        vpa_spec = {
            "targetRef": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": target_name
            },
            "updatePolicy": {
                "updateMode": self.vpa_config.get("updateMode", "Auto")
            },
            "resourcePolicy": self.vpa_config.get("resourcePolicy", {})
        }
        
        return vpa_spec 