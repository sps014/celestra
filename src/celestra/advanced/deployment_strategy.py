"""
DeploymentStrategy class for advanced deployment strategies in Celestraa DSL.

This module provides support for blue-green deployments, canary deployments,
and rolling updates with advanced configuration options.
"""

from typing import Dict, List, Any, Optional, Union
from ..core.base_builder import BaseBuilder


class DeploymentStrategy(BaseBuilder):
    """
    Builder class for advanced deployment strategies.
    
    Supports blue-green deployments, canary deployments, and advanced
    rolling update configurations.
    
    Example:
        ```python
        strategy = (DeploymentStrategy("app-strategy")
            .canary_deployment(steps=[25, 50, 75, 100])
            .analysis(success_rate=99.5, duration="5m")
            .traffic_splitting(method="istio")
            .rollback_conditions(error_rate=5.0))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the DeploymentStrategy builder.
        
        Args:
            name: Name of the deployment strategy
        """
        super().__init__(name)
        self._strategy_type: str = "rolling"
        self._rolling_config: Dict[str, Any] = {}
        self._canary_config: Dict[str, Any] = {}
        self._blue_green_config: Dict[str, Any] = {}
        self._analysis_config: Dict[str, Any] = {}
        self._traffic_config: Dict[str, Any] = {}
        self._rollback_config: Dict[str, Any] = {}
        self._promotion_config: Dict[str, Any] = {}
    
    def rolling_update(
        self,
        max_surge: Union[int, str] = "25%",
        max_unavailable: Union[int, str] = "25%",
        revision_history_limit: int = 10
    ) -> "DeploymentStrategy":
        """
        Configure rolling update strategy.
        
        Args:
            max_surge: Maximum number of pods above desired replica count
            max_unavailable: Maximum number of unavailable pods
            revision_history_limit: Number of old ReplicaSets to retain
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._strategy_type = "rolling"
        self._rolling_config = {
            "maxSurge": max_surge,
            "maxUnavailable": max_unavailable,
            "revisionHistoryLimit": revision_history_limit
        }
        return self
    
    def canary_deployment(
        self,
        steps: List[int],
        promotion_strategy: str = "manual",
        analysis_interval: str = "1m"
    ) -> "DeploymentStrategy":
        """
        Configure canary deployment strategy.
        
        Args:
            steps: List of traffic percentage steps (e.g., [25, 50, 75, 100])
            promotion_strategy: Promotion strategy (manual, automatic)
            analysis_interval: Analysis interval between steps
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._strategy_type = "canary"
        self._canary_config = {
            "steps": steps,
            "promotionStrategy": promotion_strategy,
            "analysisInterval": analysis_interval
        }
        return self
    
    def blue_green_deployment(
        self,
        auto_promotion: bool = False,
        scale_down_delay: str = "30m",
        preview_replicas: Optional[int] = None
    ) -> "DeploymentStrategy":
        """
        Configure blue-green deployment strategy.
        
        Args:
            auto_promotion: Enable automatic promotion
            scale_down_delay: Delay before scaling down old version
            preview_replicas: Number of preview replicas
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._strategy_type = "bluegreen"
        self._blue_green_config = {
            "autoPromotion": auto_promotion,
            "scaleDownDelay": scale_down_delay,
            "previewReplicas": preview_replicas
        }
        return self
    
    def analysis(
        self,
        success_rate: Optional[float] = None,
        error_rate: Optional[float] = None,
        duration: str = "5m",
        failure_limit: int = 5
    ) -> "DeploymentStrategy":
        """
        Configure deployment analysis.
        
        Args:
            success_rate: Minimum success rate percentage
            error_rate: Maximum error rate percentage
            duration: Analysis duration
            failure_limit: Number of failures before rollback
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._analysis_config = {
            "successRate": success_rate,
            "errorRate": error_rate,
            "duration": duration,
            "failureLimit": failure_limit
        }
        return self
    
    def traffic_splitting(
        self,
        method: str = "istio",
        mirror_traffic: bool = False,
        sticky_session: bool = False
    ) -> "DeploymentStrategy":
        """
        Configure traffic splitting.
        
        Args:
            method: Traffic splitting method (istio, nginx, ambassador)
            mirror_traffic: Enable traffic mirroring
            sticky_session: Enable sticky sessions
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._traffic_config = {
            "method": method,
            "mirrorTraffic": mirror_traffic,
            "stickySession": sticky_session
        }
        return self
    
    def rollback_conditions(
        self,
        error_rate: Optional[float] = None,
        response_time: Optional[str] = None,
        availability: Optional[float] = None
    ) -> "DeploymentStrategy":
        """
        Configure automatic rollback conditions.
        
        Args:
            error_rate: Maximum error rate before rollback
            response_time: Maximum response time before rollback
            availability: Minimum availability before rollback
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._rollback_config = {
            "errorRate": error_rate,
            "responseTime": response_time,
            "availability": availability
        }
        return self
    
    def promotion_gate(
        self,
        approval_required: bool = True,
        timeout: str = "1h",
        conditions: Optional[List[Dict[str, Any]]] = None
    ) -> "DeploymentStrategy":
        """
        Configure promotion gates.
        
        Args:
            approval_required: Require manual approval
            timeout: Promotion timeout
            conditions: List of promotion conditions
            
        Returns:
            DeploymentStrategy: Self for method chaining
        """
        self._promotion_config = {
            "approvalRequired": approval_required,
            "timeout": timeout,
            "conditions": conditions or []
        }
        return self
    
    # Preset strategies
    
    @classmethod
    def safe_canary(cls, name: str = "safe-canary") -> "DeploymentStrategy":
        """
        Create a safe canary deployment strategy.
        
        Args:
            name: Strategy name
            
        Returns:
            DeploymentStrategy: Configured strategy
        """
        return (cls(name)
            .canary_deployment(steps=[10, 25, 50, 75, 100], promotion_strategy="manual")
            .analysis(success_rate=99.0, error_rate=1.0, duration="5m")
            .rollback_conditions(error_rate=2.0)
            .promotion_gate(approval_required=True))
    
    @classmethod
    def fast_canary(cls, name: str = "fast-canary") -> "DeploymentStrategy":
        """
        Create a fast canary deployment strategy.
        
        Args:
            name: Strategy name
            
        Returns:
            DeploymentStrategy: Configured strategy
        """
        return (cls(name)
            .canary_deployment(steps=[25, 50, 100], promotion_strategy="automatic")
            .analysis(success_rate=98.0, duration="2m")
            .rollback_conditions(error_rate=3.0))
    
    @classmethod
    def blue_green_safe(cls, name: str = "blue-green-safe") -> "DeploymentStrategy":
        """
        Create a safe blue-green deployment strategy.
        
        Args:
            name: Strategy name
            
        Returns:
            DeploymentStrategy: Configured strategy
        """
        return (cls(name)
            .blue_green_deployment(auto_promotion=False, scale_down_delay="1h")
            .analysis(success_rate=99.5, duration="10m")
            .promotion_gate(approval_required=True))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for deployment strategy.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        if self._strategy_type == "canary" or self._strategy_type == "bluegreen":
            # Generate Argo Rollout resource
            rollout = {
                "apiVersion": "argoproj.io/v1alpha1",
                "kind": "Rollout",
                "metadata": {
                    "name": self._name,
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "strategy": {}
                }
            }
            
            if self._namespace:
                rollout["metadata"]["namespace"] = self._namespace
            
            # Configure strategy
            if self._strategy_type == "canary":
                rollout["spec"]["strategy"]["canary"] = {}
                
                if "steps" in self._canary_config:
                    steps = []
                    for step_weight in self._canary_config["steps"]:
                        step = {"setWeight": step_weight}
                        if self._analysis_config:
                            step["analysis"] = {
                                "templates": [{
                                    "templateName": f"{self._name}-analysis"
                                }],
                                "args": []
                            }
                        steps.append(step)
                    rollout["spec"]["strategy"]["canary"]["steps"] = steps
                
                if self._traffic_config.get("method"):
                    rollout["spec"]["strategy"]["canary"]["trafficRouting"] = {
                        self._traffic_config["method"]: {}
                    }
            
            elif self._strategy_type == "bluegreen":
                rollout["spec"]["strategy"]["blueGreen"] = {}
                
                if self._blue_green_config.get("autoPromotion") is not None:
                    rollout["spec"]["strategy"]["blueGreen"]["autoPromotionEnabled"] = self._blue_green_config["autoPromotion"]
                
                if self._blue_green_config.get("scaleDownDelay"):
                    rollout["spec"]["strategy"]["blueGreen"]["scaleDownDelaySeconds"] = self._parse_duration(self._blue_green_config["scaleDownDelay"])
                
                if self._blue_green_config.get("previewReplicas"):
                    rollout["spec"]["strategy"]["blueGreen"]["previewReplicaCount"] = self._blue_green_config["previewReplicas"]
            
            resources.append(rollout)
            
            # Generate AnalysisTemplate if analysis is configured
            if self._analysis_config:
                analysis_template = {
                    "apiVersion": "argoproj.io/v1alpha1",
                    "kind": "AnalysisTemplate",
                    "metadata": {
                        "name": f"{self._name}-analysis",
                        "labels": self._labels,
                        "annotations": self._annotations
                    },
                    "spec": {
                        "metrics": []
                    }
                }
                
                if self._namespace:
                    analysis_template["metadata"]["namespace"] = self._namespace
                
                # Add success rate metric
                if self._analysis_config.get("successRate"):
                    success_metric = {
                        "name": "success-rate",
                        "interval": self._analysis_config.get("duration", "5m"),
                        "successCondition": f"result[0] >= {self._analysis_config['successRate']}",
                        "provider": {
                            "prometheus": {
                                "address": "http://prometheus:9090",
                                "query": "sum(rate(http_requests_total{status!~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"
                            }
                        }
                    }
                    analysis_template["spec"]["metrics"].append(success_metric)
                
                # Add error rate metric
                if self._analysis_config.get("errorRate"):
                    error_metric = {
                        "name": "error-rate",
                        "interval": self._analysis_config.get("duration", "5m"),
                        "successCondition": f"result[0] <= {self._analysis_config['errorRate']}",
                        "provider": {
                            "prometheus": {
                                "address": "http://prometheus:9090",
                                "query": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) / sum(rate(http_requests_total[5m])) * 100"
                            }
                        }
                    }
                    analysis_template["spec"]["metrics"].append(error_metric)
                
                resources.append(analysis_template)
        
        return resources
    
    def _parse_duration(self, duration: str) -> int:
        """
        Parse duration string to seconds.
        
        Args:
            duration: Duration string (e.g., "30m", "1h")
            
        Returns:
            int: Duration in seconds
        """
        if duration.endswith("s"):
            return int(duration[:-1])
        elif duration.endswith("m"):
            return int(duration[:-1]) * 60
        elif duration.endswith("h"):
            return int(duration[:-1]) * 3600
        elif duration.endswith("d"):
            return int(duration[:-1]) * 86400
        else:
            return int(duration) 