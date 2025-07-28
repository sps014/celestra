"""
CostOptimization class for resource optimization in Celestraa DSL.

This module provides cost optimization features including resource requests/limits,
vertical/horizontal scaling, spot instances, and resource scheduling.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from ..core.base_builder import BaseBuilder


class OptimizationStrategy(Enum):
    """Cost optimization strategies."""
    AGGRESSIVE = "aggressive"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"
    CUSTOM = "custom"


class CostOptimization(BaseBuilder):
    """
    Builder class for cost optimization.
    
    Provides comprehensive cost optimization features including resource
    management, scheduling, and cost monitoring.
    
    Example:
        ```python
        cost_opt = (CostOptimization("app-cost-optimization")
            .set_strategy(OptimizationStrategy.BALANCED)
            .enable_vertical_scaling(min_cpu="100m", max_cpu="2")
            .enable_spot_instances(fallback_to_on_demand=True)
            .set_resource_quotas(cpu="10", memory="20Gi")
            .enable_scheduling_optimization())
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the CostOptimization builder.
        
        Args:
            name: Name of the cost optimization configuration
        """
        super().__init__(name)
        self._strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
        self._resource_requests: Dict[str, str] = {}
        self._resource_limits: Dict[str, str] = {}
        self._vertical_scaling: Optional[Dict[str, Any]] = None
        self._horizontal_scaling: Optional[Dict[str, Any]] = None
        self._spot_instances: Optional[Dict[str, Any]] = None
        self._resource_quotas: Dict[str, str] = {}
        self._node_affinity: Optional[Dict[str, Any]] = None
        self._scheduling_rules: List[Dict[str, Any]] = []
        self._cost_alerts: List[Dict[str, Any]] = []
        self._priority_classes: List[Dict[str, Any]] = []
    
    def set_strategy(self, strategy: OptimizationStrategy) -> "CostOptimization":
        """
        Set the optimization strategy.
        
        Args:
            strategy: Optimization strategy
            
        Returns:
            CostOptimization: Self for method chaining
        """
        self._strategy = strategy
        
        # Apply preset configurations based on strategy
        if strategy == OptimizationStrategy.AGGRESSIVE:
            self._apply_aggressive_presets()
        elif strategy == OptimizationStrategy.BALANCED:
            self._apply_balanced_presets()
        elif strategy == OptimizationStrategy.CONSERVATIVE:
            self._apply_conservative_presets()
        
        return self
    
    def set_resource_requests(
        self,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        storage: Optional[str] = None
    ) -> "CostOptimization":
        """
        Set resource requests.
        
        Args:
            cpu: CPU request (e.g., "100m", "0.5")
            memory: Memory request (e.g., "128Mi", "1Gi")
            storage: Storage request (e.g., "1Gi", "10Gi")
            
        Returns:
            CostOptimization: Self for method chaining
        """
        if cpu:
            self._resource_requests["cpu"] = cpu
        if memory:
            self._resource_requests["memory"] = memory
        if storage:
            self._resource_requests["storage"] = storage
        return self
    
    def set_resource_limits(
        self,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        storage: Optional[str] = None
    ) -> "CostOptimization":
        """
        Set resource limits.
        
        Args:
            cpu: CPU limit (e.g., "500m", "2")
            memory: Memory limit (e.g., "512Mi", "2Gi")
            storage: Storage limit (e.g., "5Gi", "50Gi")
            
        Returns:
            CostOptimization: Self for method chaining
        """
        if cpu:
            self._resource_limits["cpu"] = cpu
        if memory:
            self._resource_limits["memory"] = memory
        if storage:
            self._resource_limits["storage"] = storage
        return self
    
    def enable_vertical_scaling(
        self,
        min_cpu: str = "100m",
        max_cpu: str = "1",
        min_memory: str = "128Mi",
        max_memory: str = "1Gi",
        update_mode: str = "Auto"
    ) -> "CostOptimization":
        """
        Enable Vertical Pod Autoscaler (VPA).
        
        Args:
            min_cpu: Minimum CPU allocation
            max_cpu: Maximum CPU allocation
            min_memory: Minimum memory allocation
            max_memory: Maximum memory allocation
            update_mode: VPA update mode (Auto, Recreation, Initial, Off)
            
        Returns:
            CostOptimization: Self for method chaining
        """
        self._vertical_scaling = {
            "enabled": True,
            "min_cpu": min_cpu,
            "max_cpu": max_cpu,
            "min_memory": min_memory,
            "max_memory": max_memory,
            "update_mode": update_mode
        }
        return self
    
    def enable_horizontal_scaling(
        self,
        min_replicas: int = 1,
        max_replicas: int = 10,
        target_cpu: int = 70,
        target_memory: Optional[int] = None,
        scale_down_policy: str = "conservative"
    ) -> "CostOptimization":
        """
        Enable Horizontal Pod Autoscaler (HPA).
        
        Args:
            min_replicas: Minimum number of replicas
            max_replicas: Maximum number of replicas
            target_cpu: Target CPU utilization percentage
            target_memory: Target memory utilization percentage
            scale_down_policy: Scale down policy (conservative, aggressive)
            
        Returns:
            CostOptimization: Self for method chaining
        """
        self._horizontal_scaling = {
            "enabled": True,
            "min_replicas": min_replicas,
            "max_replicas": max_replicas,
            "target_cpu": target_cpu,
            "target_memory": target_memory,
            "scale_down_policy": scale_down_policy
        }
        return self
    
    def enable_spot_instances(
        self,
        enabled: bool = True,
        node_selector: Optional[Dict[str, str]] = None,
        tolerations: Optional[List[Dict[str, Any]]] = None,
        fallback_to_on_demand: bool = True
    ) -> "CostOptimization":
        """
        Enable spot instance usage.
        
        Args:
            enabled: Whether to enable spot instances
            node_selector: Node selector for spot instances
            tolerations: Tolerations for spot instances
            fallback_to_on_demand: Whether to fallback to on-demand instances
            
        Returns:
            CostOptimization: Self for method chaining
        """
        self._spot_instances = {
            "enabled": enabled,
            "node_selector": node_selector or {"node-type": "spot"},
            "tolerations": tolerations or [
                {
                    "key": "node.kubernetes.io/instance-type",
                    "operator": "Equal",
                    "value": "spot",
                    "effect": "NoSchedule"
                }
            ],
            "fallback_to_on_demand": fallback_to_on_demand
        }
        return self
    
    def set_resource_quotas(
        self,
        cpu: Optional[str] = None,
        memory: Optional[str] = None,
        storage: Optional[str] = None,
        pods: Optional[int] = None
    ) -> "CostOptimization":
        """
        Set resource quotas for the namespace.
        
        Args:
            cpu: CPU quota (e.g., "10", "20")
            memory: Memory quota (e.g., "20Gi", "50Gi")
            storage: Storage quota (e.g., "100Gi", "1Ti")
            pods: Maximum number of pods
            
        Returns:
            CostOptimization: Self for method chaining
        """
        if cpu:
            self._resource_quotas["requests.cpu"] = cpu
            self._resource_quotas["limits.cpu"] = cpu
        if memory:
            self._resource_quotas["requests.memory"] = memory
            self._resource_quotas["limits.memory"] = memory
        if storage:
            self._resource_quotas["requests.storage"] = storage
        if pods:
            self._resource_quotas["count/pods"] = str(pods)
        return self
    
    def add_node_affinity(
        self,
        preferred_instances: Optional[List[str]] = None,
        required_zones: Optional[List[str]] = None,
        avoid_instances: Optional[List[str]] = None
    ) -> "CostOptimization":
        """
        Add node affinity rules for cost optimization.
        
        Args:
            preferred_instances: Preferred instance types
            required_zones: Required availability zones
            avoid_instances: Instance types to avoid
            
        Returns:
            CostOptimization: Self for method chaining
        """
        self._node_affinity = {
            "preferred_instances": preferred_instances or [],
            "required_zones": required_zones or [],
            "avoid_instances": avoid_instances or []
        }
        return self
    
    def add_scheduling_rule(
        self,
        name: str,
        rule_type: str,
        conditions: Dict[str, Any],
        priority: int = 0
    ) -> "CostOptimization":
        """
        Add custom scheduling rule.
        
        Args:
            name: Rule name
            rule_type: Type of rule (affinity, anti-affinity, taint-toleration)
            conditions: Rule conditions
            priority: Rule priority
            
        Returns:
            CostOptimization: Self for method chaining
        """
        rule = {
            "name": name,
            "type": rule_type,
            "conditions": conditions,
            "priority": priority
        }
        self._scheduling_rules.append(rule)
        return self
    
    def add_cost_alert(
        self,
        name: str,
        threshold: float,
        metric: str = "cost_per_hour",
        alert_manager: str = "prometheus"
    ) -> "CostOptimization":
        """
        Add cost monitoring alert.
        
        Args:
            name: Alert name
            threshold: Cost threshold
            metric: Metric to monitor
            alert_manager: Alert manager system
            
        Returns:
            CostOptimization: Self for method chaining
        """
        alert = {
            "name": name,
            "threshold": threshold,
            "metric": metric,
            "alert_manager": alert_manager
        }
        self._cost_alerts.append(alert)
        return self
    
    def add_priority_class(
        self,
        name: str,
        value: int,
        global_default: bool = False,
        description: Optional[str] = None
    ) -> "CostOptimization":
        """
        Add priority class for workload prioritization.
        
        Args:
            name: Priority class name
            value: Priority value (higher = more important)
            global_default: Whether this is the global default
            description: Priority class description
            
        Returns:
            CostOptimization: Self for method chaining
        """
        priority_class = {
            "name": name,
            "value": value,
            "global_default": global_default,
            "description": description or f"Priority class for {name} workloads"
        }
        self._priority_classes.append(priority_class)
        return self
    
    def _apply_aggressive_presets(self) -> None:
        """Apply aggressive optimization presets."""
        self.set_resource_requests(cpu="50m", memory="64Mi")
        self.set_resource_limits(cpu="200m", memory="256Mi")
        self.enable_vertical_scaling(min_cpu="50m", max_cpu="500m", update_mode="Auto")
        self.enable_horizontal_scaling(min_replicas=1, max_replicas=20, target_cpu=80)
        self.enable_spot_instances(enabled=True)
    
    def _apply_balanced_presets(self) -> None:
        """Apply balanced optimization presets."""
        self.set_resource_requests(cpu="100m", memory="128Mi")
        self.set_resource_limits(cpu="500m", memory="512Mi")
        self.enable_vertical_scaling(min_cpu="100m", max_cpu="1", update_mode="Auto")
        self.enable_horizontal_scaling(min_replicas=2, max_replicas=10, target_cpu=70)
        self.enable_spot_instances(enabled=True, fallback_to_on_demand=True)
    
    def _apply_conservative_presets(self) -> None:
        """Apply conservative optimization presets."""
        self.set_resource_requests(cpu="200m", memory="256Mi")
        self.set_resource_limits(cpu="1", memory="1Gi")
        self.enable_vertical_scaling(min_cpu="200m", max_cpu="2", update_mode="Initial")
        self.enable_horizontal_scaling(min_replicas=3, max_replicas=6, target_cpu=60)
    
    # Preset configurations
    
    @classmethod
    def development_optimized(cls, name: str = "dev-cost-optimization") -> "CostOptimization":
        """
        Create development-optimized configuration.
        
        Args:
            name: Configuration name
            
        Returns:
            CostOptimization: Configured cost optimization
        """
        return (cls(name)
            .set_strategy(OptimizationStrategy.AGGRESSIVE)
            .set_resource_quotas(cpu="5", memory="10Gi", pods=20)
            .add_priority_class("dev-low", 100)
            .enable_spot_instances(enabled=True))
    
    @classmethod
    def production_optimized(cls, name: str = "prod-cost-optimization") -> "CostOptimization":
        """
        Create production-optimized configuration.
        
        Args:
            name: Configuration name
            
        Returns:
            CostOptimization: Configured cost optimization
        """
        return (cls(name)
            .set_strategy(OptimizationStrategy.BALANCED)
            .add_cost_alert("high-cost", 100.0)
            .add_priority_class("prod-high", 1000)
            .add_priority_class("prod-critical", 2000))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for cost optimization.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        # Generate ResourceQuota
        if self._resource_quotas:
            resource_quota = {
                "apiVersion": "v1",
                "kind": "ResourceQuota",
                "metadata": {
                    "name": f"{self._name}-quota",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "hard": self._resource_quotas
                }
            }
            
            if self._namespace:
                resource_quota["metadata"]["namespace"] = self._namespace
            
            resources.append(resource_quota)
        
        # Generate VPA if enabled
        if self._vertical_scaling and self._vertical_scaling.get("enabled"):
            vpa = {
                "apiVersion": "autoscaling.k8s.io/v1",
                "kind": "VerticalPodAutoscaler",
                "metadata": {
                    "name": f"{self._name}-vpa",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "targetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": f"{self._name}-deployment"
                    },
                    "updatePolicy": {
                        "updateMode": self._vertical_scaling["update_mode"]
                    },
                    "resourcePolicy": {
                        "containerPolicies": [{
                            "containerName": "*",
                            "minAllowed": {
                                "cpu": self._vertical_scaling["min_cpu"],
                                "memory": self._vertical_scaling["min_memory"]
                            },
                            "maxAllowed": {
                                "cpu": self._vertical_scaling["max_cpu"],
                                "memory": self._vertical_scaling["max_memory"]
                            }
                        }]
                    }
                }
            }
            
            if self._namespace:
                vpa["metadata"]["namespace"] = self._namespace
            
            resources.append(vpa)
        
        # Generate HPA if enabled
        if self._horizontal_scaling and self._horizontal_scaling.get("enabled"):
            hpa = {
                "apiVersion": "autoscaling/v2",
                "kind": "HorizontalPodAutoscaler",
                "metadata": {
                    "name": f"{self._name}-hpa",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "scaleTargetRef": {
                        "apiVersion": "apps/v1",
                        "kind": "Deployment",
                        "name": f"{self._name}-deployment"
                    },
                    "minReplicas": self._horizontal_scaling["min_replicas"],
                    "maxReplicas": self._horizontal_scaling["max_replicas"],
                    "metrics": [{
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {
                                "type": "Utilization",
                                "averageUtilization": self._horizontal_scaling["target_cpu"]
                            }
                        }
                    }]
                }
            }
            
            if self._horizontal_scaling.get("target_memory"):
                hpa["spec"]["metrics"].append({
                    "type": "Resource",
                    "resource": {
                        "name": "memory",
                        "target": {
                            "type": "Utilization",
                            "averageUtilization": self._horizontal_scaling["target_memory"]
                        }
                    }
                })
            
            if self._namespace:
                hpa["metadata"]["namespace"] = self._namespace
            
            resources.append(hpa)
        
        # Generate PriorityClasses
        for priority_class in self._priority_classes:
            pc = {
                "apiVersion": "scheduling.k8s.io/v1",
                "kind": "PriorityClass",
                "metadata": {
                    "name": priority_class["name"],
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "value": priority_class["value"],
                "globalDefault": priority_class["global_default"],
                "description": priority_class["description"]
            }
            
            resources.append(pc)
        
        # Generate ConfigMap for cost optimization settings
        config_data = {
            "strategy": self._strategy.value,
            "cost_monitoring_enabled": "true" if self._cost_alerts else "false",
            "spot_instances_enabled": str(self._spot_instances.get("enabled", False) if self._spot_instances else False).lower(),
            "vertical_scaling_enabled": str(self._vertical_scaling.get("enabled", False) if self._vertical_scaling else False).lower(),
            "horizontal_scaling_enabled": str(self._horizontal_scaling.get("enabled", False) if self._horizontal_scaling else False).lower()
        }
        
        # Add resource configurations
        if self._resource_requests:
            for resource, value in self._resource_requests.items():
                config_data[f"request_{resource}"] = value
        
        if self._resource_limits:
            for resource, value in self._resource_limits.items():
                config_data[f"limit_{resource}"] = value
        
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{self._name}-config",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "data": config_data
        }
        
        if self._namespace:
            config_map["metadata"]["namespace"] = self._namespace
        
        resources.append(config_map)
        
        return resources 