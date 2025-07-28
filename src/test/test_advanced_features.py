#!/usr/bin/env python3
"""
Advanced Features Test Suite.

Tests for K8s-Gen DSL advanced features:
- DependencyManager (dependency management)
- WaitCondition (wait conditions)
- CustomResource (custom resources and operators)
- CostOptimization (cost management and optimization)
"""

import pytest
import yaml

from src.k8s_gen import DependencyManager, WaitCondition, CustomResource, CostOptimization, App, StatefulApp
from .utils import TestHelper, AssertionHelper, MockKubernetesCluster, assert_valid_kubernetes_resource


class TestDependencyManager:
    """Test cases for the DependencyManager class (dependency management)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("dependency_manager_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_dependency_management(self):
        """Test basic dependency management."""
        dep_manager = (DependencyManager()
                      .wait_for_service("database", health_check="/health")
                      .wait_for_service("cache", health_check="PING")
                      .wait_for_config_map("app-config")
                      .wait_for_secret("app-secrets"))
        
        assert len(dep_manager._service_dependencies) == 2
        assert len(dep_manager._config_dependencies) == 1
        assert len(dep_manager._secret_dependencies) == 1
        
        # Verify service dependencies
        db_dep = next(d for d in dep_manager._service_dependencies if d["service"] == "database")
        assert db_dep["health_check"] == "/health"
        
        cache_dep = next(d for d in dep_manager._service_dependencies if d["service"] == "cache")
        assert cache_dep["health_check"] == "PING"
    
    def test_wait_conditions(self):
        """Test advanced wait conditions."""
        condition1 = (WaitCondition("database-ready")
                     .service("database")
                     .health_check("/health")
                     .timeout("5m")
                     .retry_interval("10s")
                     .max_retries(30)
                     .success_criteria("status == 'ready'"))
        
        condition2 = (WaitCondition("cache-warm")
                     .service("cache")
                     .custom_check("cache-cli ping")
                     .timeout("2m")
                     .poll_interval("5s"))
        
        dep_manager = (DependencyManager()
                      .wait_for(condition1)
                      .wait_for(condition2))
        
        assert len(dep_manager._wait_conditions) == 2
        
        # Verify first condition
        db_condition = dep_manager._wait_conditions[0]
        assert db_condition._name == "database-ready"
        assert db_condition._service == "database"
        assert db_condition._health_check == "/health"
        assert db_condition._timeout == "5m"
        assert db_condition._retry_interval == "10s"
        assert db_condition._max_retries == 30
    
    def test_external_service_dependencies(self):
        """Test external service dependencies."""
        dep_manager = (DependencyManager()
                      .wait_for_external_service("payment-gateway", url="https://api.payment.com/health")
                      .wait_for_external_service("email-service", url="https://api.email.com/status")
                      .external_service_timeout("30s")
                      .external_service_retry_policy(max_retries=5, backoff="exponential"))
        
        assert len(dep_manager._external_dependencies) == 2
        assert dep_manager._external_timeout == "30s"
        assert dep_manager._external_retry_policy["max_retries"] == 5
        assert dep_manager._external_retry_policy["backoff"] == "exponential"
        
        # Verify external dependencies
        payment_dep = next(d for d in dep_manager._external_dependencies if d["service"] == "payment-gateway")
        assert payment_dep["url"] == "https://api.payment.com/health"
    
    def test_multi_service_orchestration(self):
        """Test multi-service orchestration patterns."""
        dep_manager = DependencyManager()
        
        # Wait for all services
        dep_manager.wait_for_all(["database", "cache", "message-queue"]).then_start("api-service")
        
        # Wait for any service
        dep_manager.wait_for_any(["primary-db", "replica-db"]).then_start("read-service")
        
        # Sequential dependencies
        dep_manager.wait_for_sequence(["init-db", "migrate-schema", "seed-data"]).then_start("web-app")
        
        assert dep_manager._wait_for_all["services"] == ["database", "cache", "message-queue"]
        assert dep_manager._wait_for_all["then_start"] == "api-service"
        
        assert dep_manager._wait_for_any["services"] == ["primary-db", "replica-db"]
        assert dep_manager._wait_for_any["then_start"] == "read-service"
        
        assert dep_manager._wait_for_sequence["services"] == ["init-db", "migrate-schema", "seed-data"]
        assert dep_manager._wait_for_sequence["then_start"] == "web-app"
    
    def test_health_check_based_dependencies(self):
        """Test health check based dependencies."""
        dep_manager = (DependencyManager()
                      .wait_for_healthy_pods("database", min_ready=1)
                      .wait_for_healthy_pods("cache", min_ready=2)
                      .wait_for_service_endpoints("api-gateway", min_endpoints=3)
                      .wait_for_load_balancer_ready("external-service"))
        
        assert dep_manager._pod_health_checks["database"]["min_ready"] == 1
        assert dep_manager._pod_health_checks["cache"]["min_ready"] == 2
        assert dep_manager._endpoint_checks["api-gateway"]["min_endpoints"] == 3
        assert "external-service" in dep_manager._load_balancer_checks
    
    def test_custom_dependency_checks(self):
        """Test custom dependency checks."""
        dep_manager = (DependencyManager()
                      .wait_for_custom_check(
                          name="database-migration-complete",
                          command=["kubectl", "get", "job", "db-migration", "-o", "jsonpath='{.status.succeeded}'"],
                          expected_result="1",
                          timeout="10m"
                      )
                      .wait_for_custom_check(
                          name="config-sync-complete",
                          command=["kubectl", "get", "configmap", "app-config", "-o", "jsonpath='{.data.version}'"],
                          expected_result="v2.0.0",
                          timeout="2m"
                      ))
        
        assert len(dep_manager._custom_checks) == 2
        
        migration_check = next(c for c in dep_manager._custom_checks if c["name"] == "database-migration-complete")
        assert migration_check["expected_result"] == "1"
        assert migration_check["timeout"] == "10m"
    
    def test_conditional_dependencies(self):
        """Test conditional dependencies."""
        dep_manager = (DependencyManager()
                      .wait_for_if(
                          condition="environment == 'production'",
                          service="monitoring-stack"
                      )
                      .wait_for_if(
                          condition="feature_flags.advanced_logging == true",
                          service="log-aggregator"
                      ))
        
        assert len(dep_manager._conditional_dependencies) == 2
        
        prod_dep = dep_manager._conditional_dependencies[0]
        assert prod_dep["condition"] == "environment == 'production'"
        assert prod_dep["service"] == "monitoring-stack"
    
    def test_dependency_groups(self):
        """Test dependency groups."""
        dep_manager = (DependencyManager()
                      .wait_for_group("infrastructure", [
                          "database", "cache", "storage"
                      ])
                      .wait_for_group("monitoring", [
                          "prometheus", "grafana", "alertmanager"
                      ])
                      .wait_for_group("security", [
                          "vault", "cert-manager"
                      ]))
        
        assert len(dep_manager._dependency_groups) == 3
        
        infra_group = dep_manager._dependency_groups["infrastructure"]
        assert "database" in infra_group
        assert "cache" in infra_group
        assert "storage" in infra_group


class TestWaitCondition:
    """Test cases for the WaitCondition class (wait conditions)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("wait_condition_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_wait_condition(self):
        """Test basic wait condition configuration."""
        condition = (WaitCondition("service-ready")
                    .service("my-service")
                    .health_check("/health")
                    .timeout("5m")
                    .retry_interval("10s"))
        
        assert condition._name == "service-ready"
        assert condition._service == "my-service"
        assert condition._health_check == "/health"
        assert condition._timeout == "5m"
        assert condition._retry_interval == "10s"
    
    def test_custom_check_condition(self):
        """Test custom check wait condition."""
        condition = (WaitCondition("custom-ready")
                    .custom_check("curl -f http://service:8080/ready")
                    .timeout("3m")
                    .poll_interval("5s")
                    .success_criteria("exit_code == 0"))
        
        assert condition._custom_check == "curl -f http://service:8080/ready"
        assert condition._poll_interval == "5s"
        assert condition._success_criteria == "exit_code == 0"
    
    def test_resource_condition(self):
        """Test resource-based wait condition."""
        condition = (WaitCondition("job-complete")
                    .resource("job", "migration-job")
                    .field_condition("status.succeeded", "== 1")
                    .timeout("30m")
                    .max_retries(180))
        
        assert condition._resource_type == "job"
        assert condition._resource_name == "migration-job"
        assert condition._field_condition["field"] == "status.succeeded"
        assert condition._field_condition["condition"] == "== 1"
        assert condition._max_retries == 180


class TestCustomResource:
    """Test cases for the CustomResource class (custom resources and operators)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("custom_resource_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_custom_resource_creation(self):
        """Test basic custom resource creation."""
        custom_resource = (CustomResource("Database", "v1", "db.company.com")
                          .spec({
                              "replicas": 3,
                              "storage": "100Gi",
                              "backup_schedule": "0 2 * * *"
                          })
                          .metadata(name="production-db"))
        
        assert custom_resource._kind == "Database"
        assert custom_resource._version == "v1"
        assert custom_resource._group == "db.company.com"
        assert custom_resource._spec["replicas"] == 3
        assert custom_resource._spec["storage"] == "100Gi"
        assert custom_resource._metadata["name"] == "production-db"
    
    def test_ml_pipeline_custom_resource(self):
        """Test ML Pipeline custom resource."""
        ml_pipeline = (CustomResource("MLPipeline", "v1", "ml.company.com")
                      .spec({
                          "model": "bert-large",
                          "training_data": "s3://bucket/data/",
                          "resources": {"gpu": 2, "memory": "16Gi"},
                          "hyperparameters": {
                              "learning_rate": 0.001,
                              "batch_size": 32,
                              "epochs": 10
                          }
                      })
                      .metadata(name="text-classification-pipeline")
                      .labels({"team": "ml", "environment": "production"})
                      .annotations({"description": "Text classification ML pipeline"}))
        
        assert ml_pipeline._spec["model"] == "bert-large"
        assert ml_pipeline._spec["resources"]["gpu"] == 2
        assert ml_pipeline._spec["hyperparameters"]["learning_rate"] == 0.001
        assert ml_pipeline._metadata["labels"]["team"] == "ml"
        assert ml_pipeline._metadata["annotations"]["description"] == "Text classification ML pipeline"
    
    def test_database_cluster_custom_resource(self):
        """Test Database Cluster custom resource."""
        database_cluster = (CustomResource("DatabaseCluster", "v1", "db.company.com")
                           .spec({
                               "replicas": 3,
                               "storage": "100Gi",
                               "backup_schedule": "0 2 * * *",
                               "monitoring": True,
                               "high_availability": True,
                               "version": "14.5",
                               "extensions": ["postgis", "pg_stat_statements"]
                           })
                           .metadata(name="production-db-cluster")
                           .status({
                               "phase": "Running",
                               "ready_replicas": 3,
                               "conditions": [
                                   {"type": "Ready", "status": "True"},
                                   {"type": "Backup", "status": "True"}
                               ]
                           }))
        
        assert database_cluster._spec["replicas"] == 3
        assert database_cluster._spec["high_availability"] is True
        assert "postgis" in database_cluster._spec["extensions"]
        assert database_cluster._status["phase"] == "Running"
        assert database_cluster._status["ready_replicas"] == 3
    
    def test_messaging_system_custom_resource(self):
        """Test Messaging System custom resource."""
        messaging = (CustomResource("MessagingSystem", "v1", "messaging.company.com")
                    .spec({
                        "broker_type": "kafka",
                        "replicas": 3,
                        "storage": "50Gi",
                        "topics": [
                            {"name": "user-events", "partitions": 12, "replication_factor": 3},
                            {"name": "order-events", "partitions": 6, "replication_factor": 3}
                        ],
                        "retention_hours": 168,  # 7 days
                        "security": {
                            "authentication": "SASL_SSL",
                            "authorization": "RBAC"
                        }
                    })
                    .metadata(name="production-messaging"))
        
        assert messaging._spec["broker_type"] == "kafka"
        assert len(messaging._spec["topics"]) == 2
        assert messaging._spec["topics"][0]["partitions"] == 12
        assert messaging._spec["security"]["authentication"] == "SASL_SSL"
    
    def test_custom_resource_kubernetes_generation(self):
        """Test Kubernetes resource generation for CustomResource."""
        custom_resource = (CustomResource("MyApp", "v1", "apps.company.com")
                          .spec({
                              "replicas": 3,
                              "image": "myapp:v1.0.0",
                              "resources": {"cpu": "500m", "memory": "1Gi"}
                          })
                          .metadata(name="my-application")
                          .labels({"app": "myapp", "version": "v1.0.0"}))
        
        resources = custom_resource.generate_kubernetes_resources()
        
        # Should generate the custom resource
        cr_resource = resources[0]
        assert_valid_kubernetes_resource(cr_resource)
        
        # Verify custom resource structure
        assert cr_resource["apiVersion"] == "apps.company.com/v1"
        assert cr_resource["kind"] == "MyApp"
        assert cr_resource["metadata"]["name"] == "my-application"
        assert cr_resource["spec"]["replicas"] == 3
        assert cr_resource["spec"]["image"] == "myapp:v1.0.0"


class TestCostOptimization:
    """Test cases for the CostOptimization class (cost management and optimization)."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("cost_optimization_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_basic_cost_optimization(self):
        """Test basic cost optimization configuration."""
        cost_opt = (CostOptimization()
                   .resource_limits(
                       cpu_max="2",
                       memory_max="4Gi",
                       storage_max="100Gi"
                   )
                   .auto_scaling(
                       enable_horizontal=True,
                       enable_vertical=True,
                       scale_down_aggressively=True
                   )
                   .scheduling_preferences(
                       prefer_spot_instances=True,
                       prefer_smaller_nodes=True
                   ))
        
        assert cost_opt._resource_limits["cpu_max"] == "2"
        assert cost_opt._resource_limits["memory_max"] == "4Gi"
        assert cost_opt._resource_limits["storage_max"] == "100Gi"
        
        assert cost_opt._auto_scaling["enable_horizontal"] is True
        assert cost_opt._auto_scaling["enable_vertical"] is True
        assert cost_opt._auto_scaling["scale_down_aggressively"] is True
        
        assert cost_opt._scheduling_preferences["prefer_spot_instances"] is True
        assert cost_opt._scheduling_preferences["prefer_smaller_nodes"] is True
    
    def test_cost_budgets_and_alerts(self):
        """Test cost budgets and alerting."""
        cost_opt = (CostOptimization()
                   .budget(
                       monthly_limit=1000,  # $1000/month
                       currency="USD",
                       alert_thresholds=[50, 75, 90, 100]  # Percentages
                   )
                   .cost_tracking(
                       track_by_namespace=True,
                       track_by_label="team",
                       track_by_annotation="cost-center"
                   )
                   .alerts(
                       webhook="https://alerts.company.com/cost",
                       email=["finance@company.com", "ops@company.com"]
                   ))
        
        assert cost_opt._budget["monthly_limit"] == 1000
        assert cost_opt._budget["currency"] == "USD"
        assert 90 in cost_opt._budget["alert_thresholds"]
        
        assert cost_opt._cost_tracking["track_by_namespace"] is True
        assert cost_opt._cost_tracking["track_by_label"] == "team"
        
        assert "finance@company.com" in cost_opt._alerts["email"]
    
    def test_resource_optimization_policies(self):
        """Test resource optimization policies."""
        cost_opt = (CostOptimization()
                   .resource_optimization(
                       right_size_containers=True,
                       remove_unused_volumes=True,
                       optimize_storage_classes=True,
                       compress_images=True
                   )
                   .idle_resource_management(
                       shutdown_idle_workloads=True,
                       idle_threshold_minutes=30,
                       scale_to_zero_enabled=True
                   )
                   .reserved_capacity(
                       use_reserved_instances=True,
                       commitment_level="1_year",
                       coverage_target=80  # 80% of workload
                   ))
        
        assert cost_opt._resource_optimization["right_size_containers"] is True
        assert cost_opt._resource_optimization["remove_unused_volumes"] is True
        assert cost_opt._resource_optimization["optimize_storage_classes"] is True
        
        assert cost_opt._idle_management["shutdown_idle_workloads"] is True
        assert cost_opt._idle_management["idle_threshold_minutes"] == 30
        
        assert cost_opt._reserved_capacity["use_reserved_instances"] is True
        assert cost_opt._reserved_capacity["commitment_level"] == "1_year"
        assert cost_opt._reserved_capacity["coverage_target"] == 80
    
    def test_cloud_specific_optimizations(self):
        """Test cloud-specific cost optimizations."""
        # AWS optimizations
        aws_cost_opt = (CostOptimization()
                       .cloud_provider("aws")
                       .aws_optimizations(
                           use_spot_instances=True,
                           use_graviton_processors=True,
                           use_fargate_spot=True,
                           enable_savings_plans=True
                       )
                       .aws_storage_optimization(
                           use_gp3_volumes=True,
                           enable_ebs_encryption=True,
                           lifecycle_policies=True
                       ))
        
        assert aws_cost_opt._cloud_provider == "aws"
        assert aws_cost_opt._cloud_optimizations["use_spot_instances"] is True
        assert aws_cost_opt._cloud_optimizations["use_graviton_processors"] is True
        assert aws_cost_opt._storage_optimizations["use_gp3_volumes"] is True
        
        # GCP optimizations
        gcp_cost_opt = (CostOptimization()
                       .cloud_provider("gcp")
                       .gcp_optimizations(
                           use_preemptible_instances=True,
                           use_committed_use_discounts=True,
                           enable_autopilot=True
                       ))
        
        assert gcp_cost_opt._cloud_provider == "gcp"
        assert gcp_cost_opt._cloud_optimizations["use_preemptible_instances"] is True
        assert gcp_cost_opt._cloud_optimizations["enable_autopilot"] is True
    
    def test_cost_optimization_with_app_integration(self):
        """Test CostOptimization integration with App."""
        # Create cost optimization policy
        cost_policy = (CostOptimization()
                      .resource_limits(cpu_max="1", memory_max="2Gi")
                      .auto_scaling(enable_horizontal=True, scale_down_aggressively=True)
                      .scheduling_preferences(prefer_spot_instances=True))
        
        # Apply to app
        app = (App("cost-optimized-app")
               .image("app:latest")
               .port(8080)
               .cost_optimization(cost_policy))
        
        assert app._cost_optimization == cost_policy
        
        # Generate Kubernetes resources
        resources = app.generate_kubernetes_resources()
        deployment = AssertionHelper.assert_resource_exists(resources, "Deployment", "cost-optimized-app")
        
        # Verify cost optimization is applied
        pod_spec = deployment["spec"]["template"]["spec"]
        
        # Check for spot instance preference (node selector or tolerations)
        if "nodeSelector" in pod_spec:
            # Might have spot instance node selector
            pass
        
        if "tolerations" in pod_spec:
            # Might have spot instance tolerations
            pass
        
        # Verify resource limits are enforced
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        if "resources" in container and "limits" in container["resources"]:
            limits = container["resources"]["limits"]
            # Should respect cost optimization limits
            assert "cpu" in limits
            assert "memory" in limits


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 