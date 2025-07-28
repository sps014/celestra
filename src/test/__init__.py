"""
Comprehensive test suite for Celestra.

This package contains comprehensive tests covering all components and scenarios
defined in the Celestra specifications.

Test Structure:
- test_core_components.py: App, StatefulApp, AppGroup, Secret, ConfigMap
- test_workloads.py: Job, CronJob, Lifecycle
- test_networking.py: Service, Ingress, Companion, Scaling, Health
- test_security.py: RBAC, ServiceAccount, Role, SecurityPolicy
- test_observability.py: Monitoring, alerting, tracing
- test_advanced_features.py: Dependencies, CustomResource, CostOptimization
- test_output_formats.py: YAML, Helm, Docker Compose, Terraform
- test_plugins.py: Plugin system and template management
- test_validation.py: Validation, security scanning, cost estimation
- test_integration.py: End-to-end integration tests
- test_examples.py: Real-world example scenarios
"""

__version__ = "1.0.0"
__author__ = "Celestra Team"

# Test configuration
TEST_CONFIG = {
    "output_dir": "test_output",
    "clean_after_test": True,
    "verbose_output": True,
    "parallel_execution": False,
}

# Import test utilities
from .utils import TestHelper, MockKubernetesCluster, AssertionHelper

__all__ = [
    "TEST_CONFIG",
    "TestHelper", 
    "MockKubernetesCluster",
    "AssertionHelper"
] 