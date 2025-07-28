"""
Celestra: A Python DSL for generating Kubernetes manifests with minimal complexity.

This package provides a simple, intuitive API for defining cloud-native applications
and automatically generating production-ready Kubernetes YAML, Docker Compose files,
Helm charts, and more.
"""

from .core.app import App
from .core.stateful_app import StatefulApp
from .core.app_group import AppGroup
from .core.resource_generator import ResourceGenerator

from .security.secret import Secret
from .security.rbac import ServiceAccount, Role, ClusterRole, RoleBinding, ClusterRoleBinding
from .security.security_policy import SecurityPolicy

from .storage.config_map import ConfigMap

from .workloads.job import Job
from .workloads.cron_job import CronJob
from .workloads.lifecycle import Lifecycle

from .networking.service import Service
from .networking.ingress import Ingress
from .networking.companion import Companion
from .networking.scaling import Scaling
from .networking.health import Health
from .networking.network_policy import NetworkPolicy

from .output.kubernetes_output import KubernetesOutput
from .output.docker_compose_output import DockerComposeOutput

# Phase 5: Observability
from .advanced.observability import Observability
from .advanced.deployment_strategy import DeploymentStrategy
from .advanced.external_services import ExternalServices

# Phase 6: Advanced Features
from .advanced.dependency_manager import DependencyManager
from .advanced.wait_condition import WaitCondition
from .advanced.cost_optimization import CostOptimization, OptimizationStrategy
from .advanced.custom_resource import CustomResource, CRDScope

# Phase 7: Output Formats
from .output.helm_output import HelmOutput
from .output.kustomize_output import KustomizeOutput
from .output.terraform_output import TerraformOutput

# Phase 8: Plugin System
from .plugins.plugin_manager import PluginManager
from .plugins.plugin_base import PluginBase, PluginType, PluginMetadata
from .plugins.template_manager import TemplateManager, TemplateEngine

# Validation
from .validation.validator import Validator, ValidationLevel
from .validation.security_scanner import SecurityScanner, SecurityLevel
from .validation.cost_estimator import CostEstimator, CloudProvider

# Format decorators
from .utils.decorators import docker_compose_only, kubernetes_only, output_formats

# Main exports for convenient imports
__all__ = [
    # Core components
    "App", "StatefulApp", "AppGroup", "ResourceGenerator",
    
    # Security
    "Secret", "ServiceAccount", "Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding",
    "SecurityPolicy",
    
    # Storage
    "ConfigMap",
    
    # Workloads
    "Job", "CronJob", "Lifecycle",
    
    # Networking
    "Service", "Ingress", "Companion", "Scaling", "Health", "NetworkPolicy",
    
    # Output formats
    "KubernetesOutput", "DockerComposeOutput", "HelmOutput", "KustomizeOutput", "TerraformOutput",
    
    # Advanced features
    "Observability", "DeploymentStrategy", "ExternalServices",
    "DependencyManager", "WaitCondition", "CostOptimization", "OptimizationStrategy",
    "CustomResource", "CRDScope",
    
    # Plugin system
    "PluginManager", "PluginBase", "PluginType", "PluginMetadata",
    "TemplateManager", "TemplateEngine",
    
    # Validation
    "Validator", "ValidationLevel", "SecurityScanner", "SecurityLevel", "CostEstimator", "CloudProvider",
    
    # Format decorators
    "docker_compose_only", "kubernetes_only", "output_formats"
]

# Version info
__version__ = "1.0.0"
__author__ = "Celestra Development Team" 