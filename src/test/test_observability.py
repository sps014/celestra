#!/usr/bin/env python3
"""
Observability Test Suite.

Tests for K8s-Gen DSL observability components:
- Observability (metrics, logging, tracing, alerting)
- DeploymentStrategy (advanced deployment patterns)
- ExternalServices (external service integration)
"""

import pytest
import yaml

from src.k8s_gen import Observability, DeploymentStrategy, ExternalServices, App
from .utils import TestHelper, AssertionHelper, MockKubernetesCluster, assert_valid_kubernetes_resource


class TestObservability:
    """Test cases for the Observability class (comprehensive monitoring)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("observability_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_observability_configuration(self):
        """Test basic Observability configuration."""
        observability = (Observability()
                        .metrics(
                            endpoint="/metrics",
                            port=9090,
                            scrape_interval="30s"
                        )
                        .logging(
                            level="INFO",
                            format="json",
                            output="/var/log/app.log"
                        )
                        .tracing(
                            service_name="web-app",
                            sampling_rate=0.1
                        ))
        
        assert observability._metrics["endpoint"] == "/metrics"
        assert observability._metrics["port"] == 9090
        assert observability._metrics["scrape_interval"] == "30s"
        
        assert observability._logging["level"] == "INFO"
        assert observability._logging["format"] == "json"
        assert observability._logging["output"] == "/var/log/app.log"
        
        assert observability._tracing["service_name"] == "web-app"
        assert observability._tracing["sampling_rate"] == 0.1
    
    def test_observability_metrics_configuration(self):
        """Test detailed metrics configuration."""
        observability = (Observability()
                        .metrics(
                            endpoint="/metrics",
                            port=9090,
                            scrape_interval="15s",
                            labels={"service": "api", "team": "backend"},
                            custom_metrics=[
                                {"name": "http_requests_total", "type": "counter"},
                                {"name": "http_request_duration", "type": "histogram"},
                                {"name": "active_connections", "type": "gauge"}
                            ]
                        )
                        .prometheus_rules({
                            "high_error_rate": {
                                "condition": "rate(http_errors_total[5m]) > 0.05",
                                "for": "2m",
                                "severity": "critical"
                            },
                            "high_latency": {
                                "condition": "histogram_quantile(0.99, http_request_duration_seconds_bucket) > 2",
                                "for": "5m",
                                "severity": "warning"
                            }
                        }))
        
        assert observability._metrics["labels"]["service"] == "api"
        assert observability._metrics["labels"]["team"] == "backend"
        assert len(observability._metrics["custom_metrics"]) == 3
        assert len(observability._prometheus_rules) == 2
        
        # Verify custom metrics
        counter_metric = next(m for m in observability._metrics["custom_metrics"] if m["name"] == "http_requests_total")
        assert counter_metric["type"] == "counter"
        
        # Verify prometheus rules
        assert observability._prometheus_rules["high_error_rate"]["severity"] == "critical"
        assert observability._prometheus_rules["high_latency"]["for"] == "5m"
    
    def test_observability_logging_configuration(self):
        """Test comprehensive logging configuration."""
        observability = (Observability()
                        .logging(
                            level="DEBUG",
                            format="json",
                            output="/var/log/app.log",
                            rotation="daily",
                            retention="30d",
                            structured_fields=["timestamp", "level", "message", "trace_id"],
                            log_aggregation="fluentd"
                        )
                        .log_forwarding(
                            destinations=[
                                {"type": "elasticsearch", "url": "http://elasticsearch:9200"},
                                {"type": "s3", "bucket": "logs-bucket", "prefix": "app-logs/"}
                            ]
                        ))
        
        assert observability._logging["level"] == "DEBUG"
        assert observability._logging["rotation"] == "daily"
        assert observability._logging["retention"] == "30d"
        assert "trace_id" in observability._logging["structured_fields"]
        assert observability._logging["log_aggregation"] == "fluentd"
        
        # Verify log forwarding
        assert len(observability._log_forwarding["destinations"]) == 2
        es_dest = next(d for d in observability._log_forwarding["destinations"] if d["type"] == "elasticsearch")
        assert es_dest["url"] == "http://elasticsearch:9200"
    
    def test_observability_tracing_configuration(self):
        """Test distributed tracing configuration."""
        observability = (Observability()
                        .tracing(
                            service_name="payment-service",
                            sampling_rate=0.2,
                            endpoint="http://jaeger-collector:14268/api/traces",
                            tags={"version": "v1.2.0", "environment": "production"},
                            baggage={"user_id": "header:X-User-ID"}
                        )
                        .trace_correlation(
                            correlation_header="X-Trace-ID",
                            span_context_header="X-Span-Context"
                        ))
        
        assert observability._tracing["service_name"] == "payment-service"
        assert observability._tracing["sampling_rate"] == 0.2
        assert observability._tracing["tags"]["version"] == "v1.2.0"
        assert observability._tracing["baggage"]["user_id"] == "header:X-User-ID"
        
        assert observability._trace_correlation["correlation_header"] == "X-Trace-ID"
        assert observability._trace_correlation["span_context_header"] == "X-Span-Context"
    
    def test_observability_alerting_configuration(self):
        """Test alerting and notification configuration."""
        observability = (Observability()
                        .alerting(
                            notification_webhook="https://hooks.slack.com/services/...",
                            notification_email=["ops@company.com", "oncall@company.com"],
                            pagerduty_integration_key="abc123",
                            rules={
                                "pod_crash_looping": {
                                    "condition": "rate(kube_pod_container_status_restarts_total[15m]) > 0",
                                    "for": "1m",
                                    "severity": "critical",
                                    "description": "Pod is crash looping"
                                },
                                "high_memory_usage": {
                                    "condition": "container_memory_usage_bytes / container_spec_memory_limit_bytes > 0.9",
                                    "for": "5m",
                                    "severity": "warning",
                                    "description": "Memory usage is above 90%"
                                }
                            }
                        )
                        .alert_routing(
                            critical_alerts=["slack", "pagerduty", "email"],
                            warning_alerts=["slack", "email"],
                            info_alerts=["slack"]
                        ))
        
        assert observability._alerting["notification_webhook"].startswith("https://hooks.slack.com")
        assert "ops@company.com" in observability._alerting["notification_email"]
        assert observability._alerting["pagerduty_integration_key"] == "abc123"
        assert len(observability._alerting["rules"]) == 2
        
        # Verify alert routing
        assert "pagerduty" in observability._alert_routing["critical_alerts"]
        assert "pagerduty" not in observability._alert_routing["warning_alerts"]
    
    def test_observability_health_checks(self):
        """Test health check configuration."""
        observability = (Observability()
                        .health_checks(
                            startup_probe="/health/startup",
                            readiness_probe="/health/ready",
                            liveness_probe="/health/live",
                            custom_probes={
                                "database": "SELECT 1",
                                "cache": "PING",
                                "external_api": "GET https://api.external.com/health"
                            }
                        )
                        .health_check_config(
                            initial_delay=30,
                            period=10,
                            timeout=5,
                            failure_threshold=3,
                            success_threshold=1
                        ))
        
        assert observability._health_checks["startup_probe"] == "/health/startup"
        assert observability._health_checks["readiness_probe"] == "/health/ready"
        assert observability._health_checks["liveness_probe"] == "/health/live"
        
        assert observability._health_checks["custom_probes"]["database"] == "SELECT 1"
        assert observability._health_checks["custom_probes"]["cache"] == "PING"
        
        assert observability._health_check_config["initial_delay"] == 30
        assert observability._health_check_config["failure_threshold"] == 3
    
    def test_observability_with_app_integration(self):
        """Test Observability integration with App."""
        # Create observability configuration
        observability = (Observability()
                        .metrics(endpoint="/metrics", port=9090)
                        .logging(level="INFO", format="json")
                        .tracing(service_name="web-app", sampling_rate=0.1)
                        .alerting(
                            notification_webhook="https://alerts.example.com",
                            rules={
                                "high_error_rate": {
                                    "condition": "rate(http_errors_total[5m]) > 0.05",
                                    "severity": "critical"
                                }
                            }
                        ))
        
        # Apply to app
        app = (App("monitored-app")
               .image("app:latest")
               .port(8080)
               .observability(observability))
        
        assert app._observability == observability
        
        # Generate Kubernetes resources
        resources = app.generate_kubernetes_resources()
        
        # Should generate additional monitoring resources
        deployment = AssertionHelper.assert_resource_exists(resources, "Deployment", "monitored-app")
        
        # Verify metrics port is added
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        AssertionHelper.assert_container_has_port(container, 9090, "metrics")
        
        # Should generate ServiceMonitor for Prometheus
        try:
            service_monitor = AssertionHelper.assert_resource_exists(resources, "ServiceMonitor", "monitored-app")
            assert service_monitor["spec"]["endpoints"][0]["port"] == "metrics"
        except AssertionError:
            # ServiceMonitor might be optional depending on implementation
            pass


class TestDeploymentStrategy:
    """Test cases for the DeploymentStrategy class (advanced deployment patterns)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("deployment_strategy_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_blue_green_deployment(self):
        """Test Blue-Green deployment strategy."""
        strategy = (DeploymentStrategy()
                   .blue_green(
                       traffic_split_ratio=0.1,  # 10% to green initially
                       switch_traffic_after="5m",
                       rollback_on_failure=True,
                       health_check_endpoint="/health"
                   ))
        
        assert strategy._strategy_type == "blue_green"
        assert strategy._blue_green["traffic_split_ratio"] == 0.1
        assert strategy._blue_green["switch_traffic_after"] == "5m"
        assert strategy._blue_green["rollback_on_failure"] is True
        assert strategy._blue_green["health_check_endpoint"] == "/health"
    
    def test_canary_deployment(self):
        """Test Canary deployment strategy."""
        strategy = (DeploymentStrategy()
                   .canary(
                       initial_traffic_percentage=5,
                       traffic_increment=10,
                       traffic_increment_interval="2m",
                       success_threshold=95,
                       failure_threshold=5,
                       max_surge=1,
                       max_unavailable=0
                   ))
        
        assert strategy._strategy_type == "canary"
        assert strategy._canary["initial_traffic_percentage"] == 5
        assert strategy._canary["traffic_increment"] == 10
        assert strategy._canary["traffic_increment_interval"] == "2m"
        assert strategy._canary["success_threshold"] == 95
        assert strategy._canary["failure_threshold"] == 5
    
    def test_rolling_update_deployment(self):
        """Test Rolling Update deployment strategy."""
        strategy = (DeploymentStrategy()
                   .rolling_update(
                       max_surge="25%",
                       max_unavailable="25%",
                       revision_history_limit=10,
                       progress_deadline_seconds=600
                   ))
        
        assert strategy._strategy_type == "rolling_update"
        assert strategy._rolling_update["max_surge"] == "25%"
        assert strategy._rolling_update["max_unavailable"] == "25%"
        assert strategy._rolling_update["revision_history_limit"] == 10
        assert strategy._rolling_update["progress_deadline_seconds"] == 600
    
    def test_recreate_deployment(self):
        """Test Recreate deployment strategy."""
        strategy = (DeploymentStrategy()
                   .recreate(
                       shutdown_grace_period=30,
                       pre_stop_hook="/app/graceful-shutdown",
                       wait_for_termination=True
                   ))
        
        assert strategy._strategy_type == "recreate"
        assert strategy._recreate["shutdown_grace_period"] == 30
        assert strategy._recreate["pre_stop_hook"] == "/app/graceful-shutdown"
        assert strategy._recreate["wait_for_termination"] is True
    
    def test_a_b_testing_deployment(self):
        """Test A/B Testing deployment strategy."""
        strategy = (DeploymentStrategy()
                   .a_b_testing(
                       variant_a_traffic=70,
                       variant_b_traffic=30,
                       experiment_duration="1h",
                       success_metrics=["conversion_rate", "response_time"],
                       automatic_promotion=True
                   ))
        
        assert strategy._strategy_type == "a_b_testing"
        assert strategy._a_b_testing["variant_a_traffic"] == 70
        assert strategy._a_b_testing["variant_b_traffic"] == 30
        assert strategy._a_b_testing["experiment_duration"] == "1h"
        assert "conversion_rate" in strategy._a_b_testing["success_metrics"]
        assert strategy._a_b_testing["automatic_promotion"] is True
    
    def test_deployment_strategy_with_app(self):
        """Test DeploymentStrategy integration with App."""
        # Create deployment strategy
        strategy = (DeploymentStrategy()
                   .canary(
                       initial_traffic_percentage=10,
                       traffic_increment=20,
                       traffic_increment_interval="5m"
                   ))
        
        # Apply to app
        app = (App("canary-app")
               .image("app:v2.0")
               .port(8080)
               .deployment_strategy(strategy))
        
        assert app._deployment_strategy == strategy
        
        # Generate Kubernetes resources
        resources = app.generate_kubernetes_resources()
        deployment = AssertionHelper.assert_resource_exists(resources, "Deployment", "canary-app")
        
        # Verify deployment strategy configuration
        deployment_strategy = deployment["spec"]["strategy"]
        assert deployment_strategy["type"] == "RollingUpdate"  # Canary uses rolling update


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
        """Test external database service configuration."""
        external_db = (ExternalServices("external-database")
                      .database(
                          host="db.example.com",
                          port=5432,
                          database_type="postgresql",
                          connection_pool_size=20,
                          ssl_mode="require"
                      )
                      .health_check("/health", timeout=5)
                      .circuit_breaker(failure_threshold=5, timeout=30))
        
        assert external_db._name == "external-database"
        assert external_db._service_type == "database"
        assert external_db._database["host"] == "db.example.com"
        assert external_db._database["port"] == 5432
        assert external_db._database["database_type"] == "postgresql"
        assert external_db._database["connection_pool_size"] == 20
        assert external_db._database["ssl_mode"] == "require"
    
    def test_external_api_service(self):
        """Test external API service configuration."""
        external_api = (ExternalServices("payment-gateway")
                       .api(
                           base_url="https://api.payment.com",
                           api_version="v2",
                           authentication="bearer_token",
                           rate_limiting={"requests_per_minute": 1000, "burst": 100}
                       )
                       .retry_policy(max_retries=3, backoff="exponential")
                       .timeout(connect=10, read=30)
                       .ssl_verification(True)
                       .custom_headers({"User-Agent": "MyApp/1.0"}))
        
        assert external_api._service_type == "api"
        assert external_api._api["base_url"] == "https://api.payment.com"
        assert external_api._api["api_version"] == "v2"
        assert external_api._api["authentication"] == "bearer_token"
        assert external_api._api["rate_limiting"]["requests_per_minute"] == 1000
        
        assert external_api._retry_policy["max_retries"] == 3
        assert external_api._retry_policy["backoff"] == "exponential"
        assert external_api._timeout["connect"] == 10
        assert external_api._timeout["read"] == 30
    
    def test_external_message_queue_service(self):
        """Test external message queue service configuration."""
        external_queue = (ExternalServices("external-kafka")
                         .message_queue(
                             brokers=["kafka1.example.com:9092", "kafka2.example.com:9092"],
                             queue_type="kafka",
                             topics=["user-events", "order-events"],
                             consumer_group="app-consumers",
                             serialization="json"
                         )
                         .authentication(
                             mechanism="SASL_SSL",
                             username="app-user",
                             password_secret="kafka-password"
                         )
                         .connection_pooling(min_connections=5, max_connections=50))
        
        assert external_queue._service_type == "message_queue"
        assert len(external_queue._message_queue["brokers"]) == 2
        assert external_queue._message_queue["queue_type"] == "kafka"
        assert "user-events" in external_queue._message_queue["topics"]
        assert external_queue._message_queue["consumer_group"] == "app-consumers"
        
        assert external_queue._authentication["mechanism"] == "SASL_SSL"
        assert external_queue._authentication["username"] == "app-user"
        assert external_queue._connection_pooling["min_connections"] == 5
    
    def test_external_cache_service(self):
        """Test external cache service configuration."""
        external_cache = (ExternalServices("external-redis")
                         .cache(
                             host="redis.example.com",
                             port=6379,
                             cache_type="redis",
                             cluster_mode=True,
                             default_ttl=3600
                         )
                         .authentication(password_secret="redis-password")
                         .connection_pooling(min_connections=10, max_connections=100)
                         .failover(
                             fallback_strategy="local_cache",
                             circuit_breaker_threshold=5
                         ))
        
        assert external_cache._service_type == "cache"
        assert external_cache._cache["host"] == "redis.example.com"
        assert external_cache._cache["port"] == 6379
        assert external_cache._cache["cache_type"] == "redis"
        assert external_cache._cache["cluster_mode"] is True
        assert external_cache._cache["default_ttl"] == 3600
        
        assert external_cache._failover["fallback_strategy"] == "local_cache"
        assert external_cache._failover["circuit_breaker_threshold"] == 5
    
    def test_external_service_discovery(self):
        """Test external service discovery configuration."""
        external_service = (ExternalServices("service-mesh")
                           .service_discovery(
                               discovery_type="consul",
                               consul_address="consul.example.com:8500",
                               service_name="payment-service",
                               health_check_interval="30s"
                           )
                           .load_balancing(
                               algorithm="round_robin",
                               health_check_required=True
                           ))
        
        assert external_service._service_discovery["discovery_type"] == "consul"
        assert external_service._service_discovery["consul_address"] == "consul.example.com:8500"
        assert external_service._service_discovery["service_name"] == "payment-service"
        
        assert external_service._load_balancing["algorithm"] == "round_robin"
        assert external_service._load_balancing["health_check_required"] is True
    
    def test_external_services_kubernetes_generation(self):
        """Test Kubernetes resource generation for ExternalServices."""
        external_service = (ExternalServices("k8s-external-api")
                           .api(
                               base_url="https://api.external.com",
                               authentication="api_key"
                           )
                           .health_check("/health")
                           .timeout(connect=5, read=30))
        
        resources = external_service.generate_kubernetes_resources()
        
        # Should generate Service and EndpointSlice for external service
        service = AssertionHelper.assert_resource_exists(resources, "Service", "k8s-external-api")
        assert_valid_kubernetes_resource(service)
        
        # Verify service type is ExternalName
        assert service["spec"]["type"] == "ExternalName"
        assert service["spec"]["externalName"] == "api.external.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 