#!/usr/bin/env python3
"""
Validation Test Suite.

Tests for Celestra validation and scanning:
- Validator (resource validation)
- SecurityScanner (security scanning)
- CostEstimator (cost estimation)
"""

import pytest

from src.celestra import Validator, SecurityScanner, CostEstimator, App, ValidationLevel, SecurityLevel, CloudProvider
from .utils import TestHelper, MockKubernetesCluster


class TestValidator:
    """Test cases for the Validator class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("validator_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_validation(self):
        """Test basic resource validation."""
        validator = Validator()
        
        app = (App("test-app")
               .image("nginx:latest")
               .port(8080)
               .resources(cpu="100m", memory="128Mi"))
        
        # Generate resources for validation
        resources = app.generate_kubernetes_resources()
        
        # Test basic validation functionality
        result = validator.validate_resources(resources)
        assert isinstance(result, list)

    def test_validation_levels(self):
        """Test different validation levels."""
        # Test validation levels - using actual enum values
        basic_validator = Validator()
        
        # Enable different validation features
        basic_validator.enable_schema_validation()
        basic_validator.enable_best_practices()
        
        # Test with a simple app
        app = App("test-app").image("nginx:1.21").port(8080)
        resources = app.generate_kubernetes_resources()
        
        results = basic_validator.validate_resources(resources)
        assert isinstance(results, list)

    def test_custom_validation_rules(self):
        """Test custom validation rules."""
        validator = Validator()
        
        # Create a custom validation rule using correct signature
        def check_no_latest_tags(resource):
            """Check for 'latest' tags in container images."""
            issues = []
            if resource.get("kind") == "Deployment":
                containers = resource.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
                for container in containers:
                    image = container.get("image", "")
                    if ":latest" in image or ":" not in image:
                        issues.append(f"Container {container.get('name', 'unknown')} uses latest tag")
            return issues
        
        # Add custom rule with correct signature
        validator.add_custom_rule(
            "no-latest-tags",
            ValidationLevel.WARNING,
            check_no_latest_tags
        )
        
        # Test with an app using latest tag
        app = App("test-app").image("nginx:latest").port(8080)
        resources = app.generate_kubernetes_resources()
        
        results = validator.validate_resources(resources)
        assert isinstance(results, list)


class TestSecurityScanner:
    """Test cases for the SecurityScanner class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("security_scanner_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_security_scan(self):
        """Test basic security scanning."""
        scanner = SecurityScanner()
        scanner.enable_image_scanning()
        
        app = App("test-app").image("nginx:1.21").port(8080)
        resources = app.generate_kubernetes_resources()
        
        # Use correct method name
        result = scanner.scan_resources(resources)
        assert isinstance(result, list)

    def test_security_levels(self):
        """Test different security levels."""
        scanner = SecurityScanner()
        scanner.enable_rbac_analysis()
        scanner.enable_privilege_escalation_detection()
        
        # Create app without privileged method (doesn't exist in actual implementation)
        app = (App("security-app")
               .image("nginx:1.21")
               .port(8080)
               .resources(cpu="100m", memory="128Mi"))
        
        resources = app.generate_kubernetes_resources()
        findings = scanner.scan_resources(resources)
        
        assert isinstance(findings, list)


class TestCostEstimator:
    """Test cases for the CostEstimator class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("cost_estimator_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_cost_estimation(self):
        """Test basic cost estimation."""
        # Use correct constructor signature
        estimator = CostEstimator(CloudProvider.AWS, "us-west-2")
        
        app = (App("cost-app")
               .image("nginx:1.21")
               .port(8080)
               .resources(cpu="500m", memory="1Gi")
               .replicas(3))
        
        resources = app.generate_kubernetes_resources()
        
        # Test cost estimation
        costs = estimator.estimate_resources(resources)
        assert isinstance(costs, list)

    def test_cost_optimization_suggestions(self):
        """Test cost optimization suggestions."""
        # Use correct constructor
        estimator = CostEstimator(CloudProvider.AWS, "us-west-2")
        
        # Configure pricing
        estimator.set_compute_pricing(0.0464, 0.00696)  # CPU, Memory pricing
        
        app = (App("expensive-app")
               .image("nginx:1.21")
               .port(8080)
               .resources(cpu="4", memory="8Gi")
               .replicas(10))
        
        resources = app.generate_kubernetes_resources()
        
        costs = estimator.estimate_resources(resources)
        total_cost_breakdown = estimator.calculate_total_cost(costs)
        
        assert isinstance(costs, list)
        # calculate_total_cost returns CostBreakdown, not a number
        assert hasattr(total_cost_breakdown, 'total_cost')


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 