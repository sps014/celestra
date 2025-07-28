"""
K8s-Gen: A Python DSL for generating Kubernetes manifests with minimal complexity.

This package provides a simple, intuitive API for defining cloud-native applications
and automatically generating production-ready Kubernetes YAML, Docker Compose files,
Helm charts, and more.
"""

from .core.app import App
from .core.stateful_app import StatefulApp
from .core.app_group import AppGroup

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

__version__ = "1.0.0"
__author__ = "K8s-Gen Team"
__email__ = "team@k8s-gen.com"

__all__ = [
    # Core components
    "App",
    "StatefulApp", 
    "AppGroup",
    
    # Security & RBAC
    "Secret",
    "ServiceAccount",
    "Role", 
    "ClusterRole",
    "RoleBinding",
    "ClusterRoleBinding",
    "SecurityPolicy",
    
    # Storage
    "ConfigMap",
    
    # Advanced Workloads (Phase 2)
    "Job",
    "CronJob",
    "Lifecycle",
    
    # Advanced Networking (Phase 3)
    "Service",
    "Ingress", 
    "Companion",
    "Scaling",
    "Health",
    "NetworkPolicy",
    
    # Output Formats
    "KubernetesOutput",
    "DockerComposeOutput",
] 