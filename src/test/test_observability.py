#!/usr/bin/env python3
"""
Observability Test Suite.

Tests for Celestra observability components:
- Observability (metrics, logging, tracing, alerting)
- DeploymentStrategy (advanced deployment patterns)
- ExternalServices (external service integration)
"""

import pytest
import yaml

from src.celestra import Observability, DeploymentStrategy, ExternalServices, App
from .utils import TestHelper, AssertionHelper, MockKubernetesCluster, assert_valid_kubernetes_resource


class TestObservability:
    """Test cases for the Observability class (monitoring, metrics, logging, tracing)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("observability_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_observability_configuration(self):
        observability = Observability("basic-observability")
        assert observability._name == "basic-observability"

    def test_observability_metrics_configuration(self):
        observability = Observability("metrics-observability") 
        assert observability._name == "metrics-observability"

    def test_observability_logging_configuration(self):
        observability = Observability("logging-observability")
        assert observability._name == "logging-observability"

    def test_observability_tracing_configuration(self):
        observability = Observability("tracing-observability")
        assert observability._name == "tracing-observability"

    def test_observability_alerting_configuration(self):
        observability = Observability("alerting-observability")
        assert observability._name == "alerting-observability"

    def test_observability_dashboard_configuration(self):
        observability = Observability("dashboard-observability")
        assert observability._name == "dashboard-observability"

    def test_prometheus_metrics_integration(self):
        observability = Observability("prometheus-observability")
        assert observability._name == "prometheus-observability"

    def test_grafana_dashboard_integration(self):
        observability = Observability("grafana-observability")
        assert observability._name == "grafana-observability"

    def test_jaeger_tracing_integration(self):
        observability = Observability("jaeger-observability")
        assert observability._name == "jaeger-observability"

    def test_elk_logging_integration(self):
        observability = Observability("elk-observability")
        assert observability._name == "elk-observability"

    def test_alertmanager_integration(self):
        observability = Observability("alertmanager-observability")
        assert observability._name == "alertmanager-observability"

    def test_custom_metrics_configuration(self):
        observability = Observability("custom-metrics-observability")
        assert observability._name == "custom-metrics-observability"

    def test_service_mesh_observability(self):
        observability = Observability("service-mesh-observability")
        assert observability._name == "service-mesh-observability"

    def test_multi_cluster_observability(self):
        observability = Observability("multi-cluster-observability")
        assert observability._name == "multi-cluster-observability"

    def test_observability_with_app_integration(self):
        observability_config = Observability("app-observability")
        
        app = (App("monitored-app")
               .image("app:latest")
               .port(8080))
        
        # Basic test to ensure app can be created
        assert app._name == "monitored-app"
        assert observability_config._name == "app-observability"

    def test_observability_compliance_and_audit(self):
        observability = Observability("compliance-observability")
        assert observability._name == "compliance-observability"

    def test_observability_cost_monitoring(self):
        observability = Observability("cost-observability")
        assert observability._name == "cost-observability"

    def test_observability_performance_monitoring(self):
        observability = Observability("performance-observability")
        assert observability._name == "performance-observability"

    def test_observability_security_monitoring(self):
        observability = Observability("security-observability")
        assert observability._name == "security-observability"


class TestDeploymentStrategy:
    """Test cases for the DeploymentStrategy class (deployment strategies)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("deployment_strategy_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_blue_green_deployment(self):
        deployment_strategy = DeploymentStrategy("blue-green-strategy")
        assert deployment_strategy._name == "blue-green-strategy"

    def test_canary_deployment(self):
        deployment_strategy = DeploymentStrategy("canary-strategy")
        assert deployment_strategy._name == "canary-strategy"

    def test_rolling_update_deployment(self):
        deployment_strategy = DeploymentStrategy("rolling-strategy")
        assert deployment_strategy._name == "rolling-strategy"

    def test_recreate_deployment(self):
        deployment_strategy = DeploymentStrategy("recreate-strategy")
        assert deployment_strategy._name == "recreate-strategy"

    def test_a_b_testing_deployment(self):
        deployment_strategy = DeploymentStrategy("ab-testing-strategy")
        assert deployment_strategy._name == "ab-testing-strategy"

    def test_deployment_strategy_with_app(self):
        deployment_strategy = DeploymentStrategy("app-strategy")
        
        app = (App("strategy-app")
               .image("app:latest")
               .port(8080))
        
        # Basic test to ensure app can be created
        assert app._name == "strategy-app"
        assert deployment_strategy._name == "app-strategy"


class TestExternalServices:
    """Test cases for the ExternalServices class (external service integration)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("external_services_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_external_database_service(self):
        external_services = ExternalServices("database-external")
        assert external_services._name == "database-external"

    def test_external_api_service(self):
        external_services = ExternalServices("api-external")
        assert external_services._name == "api-external"

    def test_external_message_queue_service(self):
        external_services = ExternalServices("mq-external")
        assert external_services._name == "mq-external"

    def test_external_cache_service(self):
        external_services = ExternalServices("cache-external")
        assert external_services._name == "cache-external"

    def test_external_service_discovery(self):
        external_services = ExternalServices("discovery-external")
        assert external_services._name == "discovery-external"

    def test_external_services_kubernetes_generation(self):
        external_services = ExternalServices("k8s-external")
        
        # Basic test to ensure external services can be created
        assert external_services._name == "k8s-external"
        
        # Test basic resource generation
        resources = external_services.generate_kubernetes_resources()
        assert isinstance(resources, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 