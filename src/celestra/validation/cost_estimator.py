"""
CostEstimator class for resource cost estimation in Celestraa DSL.

This module provides comprehensive cost estimation including CPU/Memory costs,
storage costs, network costs, and cloud provider pricing integration.
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import re


class CloudProvider(Enum):
    """Supported cloud providers."""
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    ON_PREMISE = "on-premise"


@dataclass
class CostBreakdown:
    """Cost breakdown for resources."""
    compute_cost: float
    storage_cost: float
    network_cost: float
    total_cost: float
    currency: str = "USD"
    period: str = "monthly"


@dataclass
class ResourceCost:
    """Individual resource cost."""
    resource_name: str
    resource_kind: str
    cost_breakdown: CostBreakdown
    cost_factors: Dict[str, float]
    recommendations: List[str]


class CostEstimator:
    """
    Comprehensive cost estimator for Kubernetes resources.
    
    Provides cost estimation including CPU/Memory costs, storage costs,
    network costs, and cloud provider pricing integration with optimization
    recommendations.
    
    Example:
        ```python
        estimator = CostEstimator(CloudProvider.AWS, "us-west-2")
        estimator.set_compute_pricing(0.0464, 0.00696)  # CPU per vCPU/hour, Memory per GB/hour
        estimator.set_storage_pricing(0.10, 0.125)      # GP2 per GB/month, GP3 per GB/month
        
        costs = estimator.estimate_resources(resources)
        total_cost = estimator.calculate_total_cost(costs)
        report = estimator.generate_cost_report(costs)
        ```
    """
    
    def __init__(self, provider: CloudProvider = CloudProvider.AWS, region: str = "us-west-2"):
        """
        Initialize the cost estimator.
        
        Args:
            provider: Cloud provider
            region: Cloud region
        """
        self._provider = provider
        self._region = region
        
        # Pricing configuration
        self._compute_pricing: Dict[str, float] = {}
        self._storage_pricing: Dict[str, float] = {}
        self._network_pricing: Dict[str, float] = {}
        self._spot_discount: float = 0.7  # 70% discount for spot instances
        
        # Cost optimization settings
        self._enable_recommendations: bool = True
        self._target_utilization: float = 0.7  # Target 70% utilization
        
        # Load default pricing
        self._load_default_pricing()
    
    def set_compute_pricing(
        self,
        cpu_per_vcpu_hour: float,
        memory_per_gb_hour: float,
        gpu_per_hour: Optional[float] = None
    ) -> "CostEstimator":
        """
        Set compute pricing.
        
        Args:
            cpu_per_vcpu_hour: Cost per vCPU per hour
            memory_per_gb_hour: Cost per GB memory per hour
            gpu_per_hour: Cost per GPU per hour (optional)
            
        Returns:
            CostEstimator: Self for method chaining
        """
        self._compute_pricing["cpu_per_vcpu_hour"] = cpu_per_vcpu_hour
        self._compute_pricing["memory_per_gb_hour"] = memory_per_gb_hour
        if gpu_per_hour:
            self._compute_pricing["gpu_per_hour"] = gpu_per_hour
        return self
    
    def set_storage_pricing(
        self,
        ssd_per_gb_month: float,
        hdd_per_gb_month: Optional[float] = None,
        provisioned_iops_per_month: Optional[float] = None
    ) -> "CostEstimator":
        """
        Set storage pricing.
        
        Args:
            ssd_per_gb_month: Cost per GB SSD storage per month
            hdd_per_gb_month: Cost per GB HDD storage per month (optional)
            provisioned_iops_per_month: Cost per provisioned IOPS per month (optional)
            
        Returns:
            CostEstimator: Self for method chaining
        """
        self._storage_pricing["ssd_per_gb_month"] = ssd_per_gb_month
        if hdd_per_gb_month:
            self._storage_pricing["hdd_per_gb_month"] = hdd_per_gb_month
        if provisioned_iops_per_month:
            self._storage_pricing["provisioned_iops_per_month"] = provisioned_iops_per_month
        return self
    
    def set_network_pricing(
        self,
        data_transfer_per_gb: float,
        load_balancer_per_hour: Optional[float] = None
    ) -> "CostEstimator":
        """
        Set network pricing.
        
        Args:
            data_transfer_per_gb: Cost per GB data transfer
            load_balancer_per_hour: Cost per load balancer per hour (optional)
            
        Returns:
            CostEstimator: Self for method chaining
        """
        self._network_pricing["data_transfer_per_gb"] = data_transfer_per_gb
        if load_balancer_per_hour:
            self._network_pricing["load_balancer_per_hour"] = load_balancer_per_hour
        return self
    
    def enable_spot_instances(self, discount: float = 0.7) -> "CostEstimator":
        """
        Enable spot instance pricing.
        
        Args:
            discount: Spot instance discount (default 70%)
            
        Returns:
            CostEstimator: Self for method chaining
        """
        self._spot_discount = discount
        return self
    
    def set_target_utilization(self, utilization: float) -> "CostEstimator":
        """
        Set target resource utilization for recommendations.
        
        Args:
            utilization: Target utilization (0.0 to 1.0)
            
        Returns:
            CostEstimator: Self for method chaining
        """
        self._target_utilization = utilization
        return self
    
    def estimate_resources(self, resources: List[Dict[str, Any]]) -> List[ResourceCost]:
        """
        Estimate costs for Kubernetes resources.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[ResourceCost]: Cost estimates for each resource
        """
        costs = []
        
        for resource in resources:
            resource_cost = self.estimate_resource(resource)
            if resource_cost:
                costs.append(resource_cost)
        
        return costs
    
    def estimate_resource(self, resource: Dict[str, Any]) -> Optional[ResourceCost]:
        """
        Estimate cost for a single Kubernetes resource.
        
        Args:
            resource: Kubernetes resource
            
        Returns:
            Optional[ResourceCost]: Cost estimate or None if not applicable
        """
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        if resource_kind in ["Deployment", "StatefulSet", "DaemonSet"]:
            return self._estimate_workload_cost(resource)
        elif resource_kind == "PersistentVolumeClaim":
            return self._estimate_storage_cost(resource)
        elif resource_kind == "Service":
            return self._estimate_service_cost(resource)
        elif resource_kind == "Ingress":
            return self._estimate_ingress_cost(resource)
        elif resource_kind == "HorizontalPodAutoscaler":
            return self._estimate_hpa_cost(resource)
        
        return None
    
    def calculate_total_cost(self, resource_costs: List[ResourceCost]) -> CostBreakdown:
        """
        Calculate total cost from resource costs.
        
        Args:
            resource_costs: List of resource costs
            
        Returns:
            CostBreakdown: Total cost breakdown
        """
        total_compute = sum(rc.cost_breakdown.compute_cost for rc in resource_costs)
        total_storage = sum(rc.cost_breakdown.storage_cost for rc in resource_costs)
        total_network = sum(rc.cost_breakdown.network_cost for rc in resource_costs)
        total_cost = total_compute + total_storage + total_network
        
        return CostBreakdown(
            compute_cost=total_compute,
            storage_cost=total_storage,
            network_cost=total_network,
            total_cost=total_cost
        )
    
    def generate_cost_report(self, resource_costs: List[ResourceCost]) -> str:
        """
        Generate cost estimation report.
        
        Args:
            resource_costs: List of resource costs
            
        Returns:
            str: Formatted cost report
        """
        if not resource_costs:
            return "💰 No cost data available"
        
        total_cost = self.calculate_total_cost(resource_costs)
        
        report = []
        report.append("💰 COST ESTIMATION REPORT")
        report.append("=" * 50)
        
        # Summary
        report.append(f"☁️ Provider: {self._provider.value.upper()}")
        report.append(f"🌎 Region: {self._region}")
        report.append(f"📊 Total Monthly Cost: ${total_cost.total_cost:.2f} USD")
        report.append(f"  🖥️ Compute: ${total_cost.compute_cost:.2f}")
        report.append(f"  💾 Storage: ${total_cost.storage_cost:.2f}")
        report.append(f"  🌐 Network: ${total_cost.network_cost:.2f}")
        report.append("")
        
        # Annual projection
        annual_cost = total_cost.total_cost * 12
        report.append(f"📅 Annual Cost Projection: ${annual_cost:.2f} USD")
        report.append("")
        
        # Resource breakdown
        report.append("📋 COST BREAKDOWN BY RESOURCE")
        report.append("-" * 40)
        
        # Sort by total cost (descending)
        sorted_costs = sorted(resource_costs, key=lambda x: x.cost_breakdown.total_cost, reverse=True)
        
        for rc in sorted_costs:
            report.append(f"• {rc.resource_kind}/{rc.resource_name}")
            report.append(f"  Total: ${rc.cost_breakdown.total_cost:.2f}/month")
            report.append(f"  Compute: ${rc.cost_breakdown.compute_cost:.2f}")
            report.append(f"  Storage: ${rc.cost_breakdown.storage_cost:.2f}")
            report.append(f"  Network: ${rc.cost_breakdown.network_cost:.2f}")
            
            if rc.cost_factors:
                report.append("  Factors:")
                for factor, value in rc.cost_factors.items():
                    if isinstance(value, float):
                        report.append(f"    {factor}: {value:.2f}")
                    else:
                        report.append(f"    {factor}: {value}")
            
            if rc.recommendations:
                report.append("  💡 Recommendations:")
                for rec in rc.recommendations:
                    report.append(f"    • {rec}")
            
            report.append("")
        
        # Cost optimization recommendations
        if self._enable_recommendations:
            optimization_report = self._generate_optimization_recommendations(resource_costs, total_cost)
            report.extend(optimization_report)
        
        return "\n".join(report)
    
    def get_cost_by_category(self, resource_costs: List[ResourceCost]) -> Dict[str, float]:
        """
        Get costs grouped by resource category.
        
        Args:
            resource_costs: List of resource costs
            
        Returns:
            Dict[str, float]: Costs by category
        """
        categories = {}
        
        for rc in resource_costs:
            category = rc.resource_kind
            if category not in categories:
                categories[category] = 0
            categories[category] += rc.cost_breakdown.total_cost
        
        return categories
    
    def _estimate_workload_cost(self, resource: Dict[str, Any]) -> ResourceCost:
        """Estimate cost for workload resources."""
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Get replicas
        replicas = resource.get("spec", {}).get("replicas", 1)
        
        # Get resource requirements
        containers = self._get_containers(resource)
        total_cpu, total_memory = self._calculate_resource_requirements(containers)
        
        # Calculate monthly costs
        cpu_cost = total_cpu * replicas * self._compute_pricing["cpu_per_vcpu_hour"] * 24 * 30
        memory_cost = total_memory * replicas * self._compute_pricing["memory_per_gb_hour"] * 24 * 30
        
        # Apply spot discount if applicable
        if self._is_spot_eligible(resource):
            cpu_cost *= self._spot_discount
            memory_cost *= self._spot_discount
        
        compute_cost = cpu_cost + memory_cost
        
        # Generate recommendations
        recommendations = self._generate_workload_recommendations(resource, total_cpu, total_memory, replicas)
        
        cost_factors = {
            "replicas": replicas,
            "cpu_cores": total_cpu,
            "memory_gb": total_memory,
            "cpu_cost_per_hour": self._compute_pricing["cpu_per_vcpu_hour"],
            "memory_cost_per_hour": self._compute_pricing["memory_per_gb_hour"]
        }
        
        return ResourceCost(
            resource_name=resource_name,
            resource_kind=resource_kind,
            cost_breakdown=CostBreakdown(
                compute_cost=compute_cost,
                storage_cost=0.0,
                network_cost=0.0,
                total_cost=compute_cost
            ),
            cost_factors=cost_factors,
            recommendations=recommendations
        )
    
    def _estimate_storage_cost(self, resource: Dict[str, Any]) -> ResourceCost:
        """Estimate cost for storage resources."""
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Get storage size
        spec = resource.get("spec", {})
        resources = spec.get("resources", {})
        requests = resources.get("requests", {})
        storage_size = requests.get("storage", "0Gi")
        
        # Parse storage size
        size_gb = self._parse_storage_size(storage_size)
        
        # Get storage class (determines pricing)
        storage_class = spec.get("storageClassName", "gp2")
        storage_type = "ssd" if storage_class in ["gp2", "gp3", "ssd"] else "hdd"
        
        # Calculate monthly cost
        price_key = f"{storage_type}_per_gb_month"
        storage_cost = size_gb * self._storage_pricing.get(price_key, 0.1)
        
        # Generate recommendations
        recommendations = self._generate_storage_recommendations(resource, size_gb, storage_class)
        
        cost_factors = {
            "storage_gb": size_gb,
            "storage_class": storage_class,
            "price_per_gb": self._storage_pricing.get(price_key, 0.1)
        }
        
        return ResourceCost(
            resource_name=resource_name,
            resource_kind=resource_kind,
            cost_breakdown=CostBreakdown(
                compute_cost=0.0,
                storage_cost=storage_cost,
                network_cost=0.0,
                total_cost=storage_cost
            ),
            cost_factors=cost_factors,
            recommendations=recommendations
        )
    
    def _estimate_service_cost(self, resource: Dict[str, Any]) -> Optional[ResourceCost]:
        """Estimate cost for service resources."""
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        spec = resource.get("spec", {})
        service_type = spec.get("type", "ClusterIP")
        
        # Only LoadBalancer services have additional costs
        if service_type != "LoadBalancer":
            return None
        
        # Calculate load balancer cost
        lb_cost = self._network_pricing.get("load_balancer_per_hour", 0.025) * 24 * 30
        
        recommendations = ["Consider using Ingress controller instead of multiple LoadBalancer services"]
        
        cost_factors = {
            "service_type": service_type,
            "load_balancer_cost_per_hour": self._network_pricing.get("load_balancer_per_hour", 0.025)
        }
        
        return ResourceCost(
            resource_name=resource_name,
            resource_kind=resource_kind,
            cost_breakdown=CostBreakdown(
                compute_cost=0.0,
                storage_cost=0.0,
                network_cost=lb_cost,
                total_cost=lb_cost
            ),
            cost_factors=cost_factors,
            recommendations=recommendations
        )
    
    def _estimate_ingress_cost(self, resource: Dict[str, Any]) -> Optional[ResourceCost]:
        """Estimate cost for ingress resources."""
        # Ingress costs are typically covered by the ingress controller
        # which is estimated as a workload
        return None
    
    def _estimate_hpa_cost(self, resource: Dict[str, Any]) -> Optional[ResourceCost]:
        """Estimate cost impact of HPA resources."""
        # HPA itself doesn't have direct costs, but affects scaling costs
        return None
    
    def _calculate_resource_requirements(self, containers: List[Dict[str, Any]]) -> Tuple[float, float]:
        """Calculate total CPU and memory requirements."""
        total_cpu = 0.0
        total_memory = 0.0
        
        for container in containers:
            resources = container.get("resources", {})
            requests = resources.get("requests", {})
            
            # Parse CPU (convert to cores)
            cpu_str = requests.get("cpu", "100m")
            total_cpu += self._parse_cpu(cpu_str)
            
            # Parse memory (convert to GB)
            memory_str = requests.get("memory", "128Mi")
            total_memory += self._parse_memory(memory_str)
        
        return total_cpu, total_memory
    
    def _parse_cpu(self, cpu_str: str) -> float:
        """Parse CPU string to cores."""
        if cpu_str.endswith("m"):
            return float(cpu_str[:-1]) / 1000
        else:
            return float(cpu_str)
    
    def _parse_memory(self, memory_str: str) -> float:
        """Parse memory string to GB."""
        if memory_str.endswith("Mi"):
            return float(memory_str[:-2]) / 1024
        elif memory_str.endswith("Gi"):
            return float(memory_str[:-2])
        elif memory_str.endswith("Ki"):
            return float(memory_str[:-2]) / (1024 * 1024)
        else:
            # Assume bytes
            return float(memory_str) / (1024 * 1024 * 1024)
    
    def _parse_storage_size(self, storage_str: str) -> float:
        """Parse storage string to GB."""
        if storage_str.endswith("Gi"):
            return float(storage_str[:-2])
        elif storage_str.endswith("Mi"):
            return float(storage_str[:-2]) / 1024
        elif storage_str.endswith("Ti"):
            return float(storage_str[:-2]) * 1024
        else:
            # Assume GB
            return float(storage_str.replace("G", ""))
    
    def _get_containers(self, resource: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get containers from a resource."""
        containers = []
        
        if resource.get("kind") == "CronJob":
            pod_spec = resource.get("spec", {}).get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {})
        else:
            pod_spec = resource.get("spec", {}).get("template", {}).get("spec", {})
        
        containers.extend(pod_spec.get("containers", []))
        containers.extend(pod_spec.get("initContainers", []))
        
        return containers
    
    def _is_spot_eligible(self, resource: Dict[str, Any]) -> bool:
        """Check if resource is eligible for spot pricing."""
        # Check for spot instance annotations or node selectors
        annotations = resource.get("metadata", {}).get("annotations", {})
        return "spot" in annotations.get("cluster-autoscaler.kubernetes.io/safe-to-evict", "").lower()
    
    def _generate_workload_recommendations(
        self,
        resource: Dict[str, Any],
        cpu: float,
        memory: float,
        replicas: int
    ) -> List[str]:
        """Generate cost optimization recommendations for workloads."""
        recommendations = []
        
        # Resource utilization recommendations
        if cpu > 2.0:
            recommendations.append("Consider using smaller instance types with more replicas")
        
        if memory > 8.0:
            recommendations.append("Evaluate if high memory usage is necessary")
        
        # Scaling recommendations
        if replicas > 10:
            recommendations.append("Consider using HPA for dynamic scaling")
        
        # Check for resource limits
        containers = self._get_containers(resource)
        has_limits = any(
            container.get("resources", {}).get("limits")
            for container in containers
        )
        
        if not has_limits:
            recommendations.append("Add resource limits to prevent over-allocation")
        
        # Spot instance recommendation
        if not self._is_spot_eligible(resource):
            recommendations.append(f"Consider spot instances for {int(self._spot_discount * 100)}% cost savings")
        
        return recommendations
    
    def _generate_storage_recommendations(
        self,
        resource: Dict[str, Any],
        size_gb: float,
        storage_class: str
    ) -> List[str]:
        """Generate storage optimization recommendations."""
        recommendations = []
        
        if size_gb > 1000:  # > 1TB
            recommendations.append("Consider using cheaper storage class for large volumes")
        
        if storage_class == "gp2":
            recommendations.append("Consider upgrading to gp3 for better price/performance")
        
        return recommendations
    
    def _generate_optimization_recommendations(
        self,
        resource_costs: List[ResourceCost],
        total_cost: CostBreakdown
    ) -> List[str]:
        """Generate overall cost optimization recommendations."""
        report = []
        report.append("💡 COST OPTIMIZATION RECOMMENDATIONS")
        report.append("-" * 40)
        
        # Calculate potential savings
        total_monthly = total_cost.total_cost
        
        # Spot instance savings
        spot_eligible_cost = sum(
            rc.cost_breakdown.compute_cost 
            for rc in resource_costs 
            if rc.resource_kind in ["Deployment", "StatefulSet"]
        )
        spot_savings = spot_eligible_cost * (1 - self._spot_discount)
        
        if spot_savings > 10:  # > $10/month savings
            report.append(f"🏷️ Enable spot instances: Save ~${spot_savings:.2f}/month ({spot_savings/total_monthly*100:.1f}%)")
        
        # Right-sizing recommendations
        high_cost_resources = [rc for rc in resource_costs if rc.cost_breakdown.total_cost > total_monthly * 0.2]
        if high_cost_resources:
            report.append("📏 Right-size high-cost resources:")
            for rc in high_cost_resources[:3]:  # Top 3
                report.append(f"  • {rc.resource_kind}/{rc.resource_name}: ${rc.cost_breakdown.total_cost:.2f}/month")
        
        # Storage optimization
        storage_cost = total_cost.storage_cost
        if storage_cost > total_monthly * 0.3:
            storage_savings = storage_cost * 0.2  # Assume 20% savings possible
            report.append(f"💾 Optimize storage: Potential ${storage_savings:.2f}/month savings")
        
        # Load balancer optimization
        network_cost = total_cost.network_cost
        if network_cost > 50:  # > $50/month
            report.append("🌐 Consolidate LoadBalancer services using Ingress controller")
        
        # Monthly vs Annual savings
        if total_monthly > 100:  # > $100/month
            annual_savings = total_monthly * 12 * 0.15  # Assume 15% savings with annual commitment
            report.append(f"💰 Consider annual commitment: Save ~${annual_savings:.2f}/year")
        
        return report
    
    def _load_default_pricing(self) -> None:
        """Load default pricing for the configured provider."""
        if self._provider == CloudProvider.AWS:
            # AWS EC2 pricing (approximate, us-west-2)
            self._compute_pricing = {
                "cpu_per_vcpu_hour": 0.0464,  # t3.medium
                "memory_per_gb_hour": 0.00696,
                "gpu_per_hour": 0.90  # p3.2xlarge
            }
            
            self._storage_pricing = {
                "ssd_per_gb_month": 0.10,  # GP2
                "hdd_per_gb_month": 0.045,  # SC1
                "provisioned_iops_per_month": 0.065
            }
            
            self._network_pricing = {
                "data_transfer_per_gb": 0.09,
                "load_balancer_per_hour": 0.025
            }
        
        elif self._provider == CloudProvider.GCP:
            # GCP pricing (approximate, us-west1)
            self._compute_pricing = {
                "cpu_per_vcpu_hour": 0.035,
                "memory_per_gb_hour": 0.0047,
                "gpu_per_hour": 0.70
            }
            
            self._storage_pricing = {
                "ssd_per_gb_month": 0.17,  # SSD persistent disk
                "hdd_per_gb_month": 0.04,  # Standard persistent disk
            }
            
            self._network_pricing = {
                "data_transfer_per_gb": 0.085,
                "load_balancer_per_hour": 0.025
            }
        
        elif self._provider == CloudProvider.AZURE:
            # Azure pricing (approximate, West US 2)
            self._compute_pricing = {
                "cpu_per_vcpu_hour": 0.042,
                "memory_per_gb_hour": 0.0056,
                "gpu_per_hour": 0.90
            }
            
            self._storage_pricing = {
                "ssd_per_gb_month": 0.15,  # Premium SSD
                "hdd_per_gb_month": 0.05,  # Standard HDD
            }
            
            self._network_pricing = {
                "data_transfer_per_gb": 0.087,
                "load_balancer_per_hour": 0.025
            }
        
        else:  # ON_PREMISE
            # Estimated on-premise costs
            self._compute_pricing = {
                "cpu_per_vcpu_hour": 0.02,
                "memory_per_gb_hour": 0.003,
            }
            
            self._storage_pricing = {
                "ssd_per_gb_month": 0.05,
                "hdd_per_gb_month": 0.01,
            }
            
            self._network_pricing = {
                "data_transfer_per_gb": 0.01,
            } 