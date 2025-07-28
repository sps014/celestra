"""
Celestra Examples Package.

This package contains comprehensive examples demonstrating various features
and use cases of the Celestra Domain-Specific Language.

Available Examples:
- multiple_ports_showcase: Demonstrates multi-port configurations across all components
- enterprise_validation_demo: Shows enterprise security, validation, and compliance
- complete_platform_demo: Full cloud-native platform with microservices
- advanced_application_demo: Advanced patterns like sidecars, lifecycle hooks
- rbac_security_demo: Comprehensive RBAC configuration examples
- kubernetes_yaml_generation_example: Real YAML generation and validation

Usage:
    cd src/examples
    python -m multiple_ports_showcase
    python -m enterprise_validation_demo
    # etc.

Or run from project root:
    python -m src.examples.multiple_ports_showcase
"""

__version__ = "1.0.0"
__author__ = "Celestra Development Team"

# Make examples easily importable
from . import multiple_ports_showcase
from . import enterprise_validation_demo
from . import complete_platform_demo
from . import advanced_application_demo
from . import rbac_security_demo
from . import kubernetes_yaml_generation_example

__all__ = [
    "multiple_ports_showcase",
    "enterprise_validation_demo", 
    "complete_platform_demo",
    "advanced_application_demo",
    "rbac_security_demo",
    "kubernetes_yaml_generation_example"
] 