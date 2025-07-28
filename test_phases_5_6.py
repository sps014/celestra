#!/usr/bin/env python3
"""
Test script for K8s-Gen DSL Phase 5 (Observability) and Phase 6 (Advanced Features).

This script demonstrates the advanced capabilities including observability,
deployment strategies, external services, dependency management, wait conditions,
cost optimization, and custom resources.
"""

from src.k8s_gen import (
    # Phase 5: Observability
    Observability,
    DeploymentStrategy,
    ExternalServices,
    
    # Phase 6: Advanced Features  
    DependencyManager,
    WaitCondition,
    CostOptimization,
    OptimizationStrategy,
    CustomResource,
    CRDScope
)


def test_observability():
    """Test Observability class functionality."""
    print("🔍 Testing Observability...")
    
    # Basic monitoring setup
    basic_obs = Observability.basic_monitoring("basic-monitoring")
    
    # Full observability stack
    full_obs = (Observability("full-observability")
        .enable_prometheus_metrics(port=9090, path="/metrics")
        .enable_logging(level="info", format="json")
        .enable_tracing(jaeger_endpoint="http://jaeger:14268")
        .add_alert_rule("high_cpu", "cpu_usage > 80", severity="warning")
        .add_alert_rule("high_memory", "memory_usage > 90", severity="critical")
        .add_dashboard("app-dashboard", {"title": "Application Dashboard"})
        .enable_log_aggregation(backend="elasticsearch"))
    
    # Generate resources
    basic_resources = basic_obs.generate_kubernetes_resources()
    full_resources = full_obs.generate_kubernetes_resources()
    
    print(f"  ✅ Basic observability generated {len(basic_resources)} resources")
    print(f"  ✅ Full observability generated {len(full_resources)} resources")
    
    return basic_resources, full_resources


def test_deployment_strategy():
    """Test DeploymentStrategy class functionality."""
    print("🚀 Testing Deployment Strategy...")
    
    # Safe canary deployment
    safe_canary = DeploymentStrategy.safe_canary("safe-canary-strategy")
    
    # Fast canary deployment  
    fast_canary = DeploymentStrategy.fast_canary("fast-canary-strategy")
    
    # Blue-green deployment
    blue_green = (DeploymentStrategy("blue-green-strategy")
        .blue_green_deployment(auto_promotion=False, scale_down_delay="1h")
        .analysis(success_rate=99.5, duration="10m")
        .traffic_splitting(method="istio")
        .rollback_conditions(error_rate=2.0))
    
    # Custom canary with advanced features
    custom_canary = (DeploymentStrategy("custom-canary")
        .canary_deployment(steps=[10, 25, 50, 75, 100])
        .analysis(success_rate=98.0, error_rate=2.0, duration="5m")
        .traffic_splitting(method="istio", mirror_traffic=True)
        .promotion_gate(approval_required=True, timeout="30m"))
    
    # Generate resources
    safe_resources = safe_canary.generate_kubernetes_resources()
    fast_resources = fast_canary.generate_kubernetes_resources()
    bg_resources = blue_green.generate_kubernetes_resources()
    custom_resources = custom_canary.generate_kubernetes_resources()
    
    print(f"  ✅ Safe canary generated {len(safe_resources)} resources")
    print(f"  ✅ Fast canary generated {len(fast_resources)} resources")
    print(f"  ✅ Blue-green generated {len(bg_resources)} resources")
    print(f"  ✅ Custom canary generated {len(custom_resources)} resources")
    
    return safe_resources, fast_resources, bg_resources, custom_resources


def test_external_services():
    """Test ExternalServices class functionality."""
    print("🌐 Testing External Services...")
    
    # Web app stack
    web_stack = ExternalServices.web_app_stack("web-app-externals")
    
    # Microservices stack
    microservices_stack = ExternalServices.microservices_stack("microservices-externals")
    
    # Custom external services configuration
    custom_externals = (ExternalServices("custom-externals")
        .add_database("postgres", host="db.example.com", port=5432, ssl_enabled=True)
        .add_database("mongodb", type="mongodb", host="mongo.example.com", port=27017)
        .add_message_queue("kafka", type="kafka", endpoint="kafka.example.com:9092")
        .add_storage("s3", bucket="my-app-bucket", region="us-west-2")
        .add_secret_store("vault", endpoint="vault.example.com")
        .add_monitoring_service("datadog", api_key_secret="datadog-api-key")
        .add_api_service("payment-api", "https://api.payment.com", timeout=30)
        .enable_service_mesh(type="istio", mutual_tls=True))
    
    # Generate resources
    web_resources = web_stack.generate_kubernetes_resources()
    micro_resources = microservices_stack.generate_kubernetes_resources()
    custom_resources = custom_externals.generate_kubernetes_resources()
    
    print(f"  ✅ Web app stack generated {len(web_resources)} resources")
    print(f"  ✅ Microservices stack generated {len(micro_resources)} resources")
    print(f"  ✅ Custom externals generated {len(custom_resources)} resources")
    
    return web_resources, micro_resources, custom_resources


def test_dependency_manager():
    """Test DependencyManager class functionality."""
    print("🔗 Testing Dependency Manager...")
    
    # Web app dependencies
    web_deps = DependencyManager.web_app_dependencies("web-app-deps")
    
    # Microservices dependencies
    micro_deps = DependencyManager.microservices_dependencies("microservices-deps")
    
    # Custom dependency management
    custom_deps = (DependencyManager("custom-dependencies")
        .add_service_dependency("user-service", service_name="user-service", health_check="/health")
        .add_database_dependency("postgres", host="postgres", port=5432)
        .add_api_dependency("auth-api", base_url="https://auth.example.com")
        .add_message_queue_dependency("redis", endpoint="redis:6379", queue_type="redis")
        .add_storage_dependency("s3", bucket="app-storage", storage_type="s3")
        .add_custom_dependency("migration-check", ["./check-migration.sh"])
        .set_timeout("10m")
        .enable_retry(max_attempts=5, backoff="exponential")
        .enable_circuit_breaker(failure_threshold=3))
    
    # Generate resources
    web_resources = web_deps.generate_kubernetes_resources()
    micro_resources = micro_deps.generate_kubernetes_resources()
    custom_resources = custom_deps.generate_kubernetes_resources()
    
    print(f"  ✅ Web app dependencies generated {len(web_resources)} resources")
    print(f"  ✅ Microservices dependencies generated {len(micro_resources)} resources")
    print(f"  ✅ Custom dependencies generated {len(custom_resources)} resources")
    
    return web_resources, micro_resources, custom_resources


def test_wait_condition():
    """Test WaitCondition class functionality."""
    print("⏳ Testing Wait Condition...")
    
    # Database readiness
    db_wait = WaitCondition.database_ready("db-wait", host="postgres", port=5432)
    
    # Service stack readiness
    service_wait = WaitCondition.service_stack_ready("service-wait", 
                                                   ["user-service", "auth-service"])
    
    # Complex wait conditions
    complex_wait = (WaitCondition("complex-wait")
        .wait_for_pod_ready("app-pod", namespace="default")
        .wait_for_deployment_ready("user-service")
        .wait_for_http_success("http://auth-service/health")
        .wait_for_tcp_connect("postgres", 5432)
        .wait_for_custom_command(["curl", "-f", "http://api/ready"])
        .wait_for_log_pattern("app-deployment", "Server started successfully")
        .wait_for_metric_threshold("up{job='app'}", 1.0, ">=")
        .set_timeout("15m")
        .enable_parallel_checks()
        .enable_retry(max_attempts=10, delay="30s")
        .set_thresholds(success_threshold=2, failure_threshold=5))
    
    # Generate resources
    db_resources = db_wait.generate_kubernetes_resources()
    service_resources = service_wait.generate_kubernetes_resources()
    complex_resources = complex_wait.generate_kubernetes_resources()
    
    print(f"  ✅ Database wait generated {len(db_resources)} resources")
    print(f"  ✅ Service wait generated {len(service_resources)} resources")
    print(f"  ✅ Complex wait generated {len(complex_resources)} resources")
    
    return db_resources, service_resources, complex_resources


def test_cost_optimization():
    """Test CostOptimization class functionality."""
    print("💰 Testing Cost Optimization...")
    
    # Development optimized
    dev_cost = CostOptimization.development_optimized("dev-cost-opt")
    
    # Production optimized
    prod_cost = CostOptimization.production_optimized("prod-cost-opt")
    
    # Custom cost optimization
    custom_cost = (CostOptimization("custom-cost-optimization")
        .set_strategy(OptimizationStrategy.BALANCED)
        .set_resource_requests(cpu="200m", memory="256Mi")
        .set_resource_limits(cpu="1", memory="1Gi")
        .enable_vertical_scaling(min_cpu="100m", max_cpu="2")
        .enable_horizontal_scaling(min_replicas=2, max_replicas=15, target_cpu=70)
        .enable_spot_instances(enabled=True, fallback_to_on_demand=True)
        .set_resource_quotas(cpu="20", memory="40Gi", pods=50)
        .add_node_affinity(preferred_instances=["t3.medium", "t3.large"])
        .add_cost_alert("high-cost", 200.0, metric="cost_per_hour")
        .add_priority_class("app-high", 1000)
        .add_priority_class("app-critical", 2000, global_default=False))
    
    # Generate resources
    dev_resources = dev_cost.generate_kubernetes_resources()
    prod_resources = prod_cost.generate_kubernetes_resources()
    custom_resources = custom_cost.generate_kubernetes_resources()
    
    print(f"  ✅ Development cost optimization generated {len(dev_resources)} resources")
    print(f"  ✅ Production cost optimization generated {len(prod_resources)} resources")
    print(f"  ✅ Custom cost optimization generated {len(custom_resources)} resources")
    
    return dev_resources, prod_resources, custom_resources


def test_custom_resource():
    """Test CustomResource class functionality."""
    print("📋 Testing Custom Resource...")
    
    # Application CRD
    app_crd = CustomResource.application_crd("application")
    
    # Database CRD
    db_crd = CustomResource.database_crd("database")
    
    # Custom CRD with advanced features
    custom_crd = (CustomResource("workflow")
        .group("workflow.example.com")
        .version("v1alpha1")
        .scope(CRDScope.NAMESPACED)
        .names(plural="workflows", kind="Workflow", short_names=["wf"], categories=["all"])
        .add_property("steps", "array", "Workflow steps", required=True)
        .add_array_property("triggers", "object", {
            "type": {"type": "string", "enum": ["cron", "webhook", "manual"]},
            "schedule": {"type": "string"},
            "enabled": {"type": "boolean", "default": True}
        })
        .add_object_property("resources", {
            "cpu": {"type": "string", "default": "100m"},
            "memory": {"type": "string", "default": "128Mi"}
        }, required=True)
        .add_status_property("phase", "string", "Current workflow phase")
        .add_status_property("completedSteps", "integer", "Number of completed steps")
        .add_printer_column("Phase", ".status.phase")
        .add_printer_column("Steps", ".status.completedSteps", "integer")
        .add_printer_column("Age", ".metadata.creationTimestamp", "date")
        .enable_subresources(status=True, scale=False)
        .add_controller("workflow-controller:v1.0.0", replicas=1))
    
    # Create instances
    app_crd.create_instance("my-app", {
        "image": "nginx:1.21",
        "replicas": 3,
        "port": 80
    })
    
    custom_crd.create_instance("data-pipeline", {
        "steps": ["extract", "transform", "load"],
        "triggers": [
            {"type": "cron", "schedule": "0 2 * * *", "enabled": True}
        ],
        "resources": {
            "cpu": "500m",
            "memory": "1Gi"
        }
    })
    
    # Generate resources
    app_resources = app_crd.generate_kubernetes_resources()
    db_resources = db_crd.generate_kubernetes_resources()
    custom_resources = custom_crd.generate_kubernetes_resources()
    
    print(f"  ✅ Application CRD generated {len(app_resources)} resources")
    print(f"  ✅ Database CRD generated {len(db_resources)} resources")
    print(f"  ✅ Custom CRD generated {len(custom_resources)} resources")
    
    return app_resources, db_resources, custom_resources


def main():
    """Run all Phase 5 and 6 tests."""
    print("🧪 Testing K8s-Gen DSL Phase 5 (Observability) and Phase 6 (Advanced Features)")
    print("=" * 80)
    
    try:
        # Phase 5 Tests
        print("\n📊 PHASE 5: OBSERVABILITY")
        print("-" * 40)
        
        obs_resources = test_observability()
        strategy_resources = test_deployment_strategy()
        external_resources = test_external_services()
        
        # Phase 6 Tests
        print("\n🚀 PHASE 6: ADVANCED FEATURES")
        print("-" * 40)
        
        dependency_resources = test_dependency_manager()
        wait_resources = test_wait_condition()
        cost_resources = test_cost_optimization()
        crd_resources = test_custom_resource()
        
        # Summary
        print("\n📋 SUMMARY")
        print("-" * 40)
        
        total_resources = (
            sum(len(r) for r in obs_resources) +
            sum(len(r) for r in strategy_resources) +
            sum(len(r) for r in external_resources) +
            sum(len(r) for r in dependency_resources) +
            sum(len(r) for r in wait_resources) +
            sum(len(r) for r in cost_resources) +
            sum(len(r) for r in crd_resources)
        )
        
        print(f"✅ All Phase 5 & 6 tests completed successfully!")
        print(f"📊 Total Kubernetes resources generated: {total_resources}")
        print(f"🎯 Advanced features ready for production use")
        
        # Feature breakdown
        print("\n🔍 FEATURE BREAKDOWN:")
        print("  📊 Observability: Monitoring, logging, tracing, alerting")
        print("  🚀 Deployment Strategies: Canary, blue-green, rolling updates")
        print("  🌐 External Services: Cloud integrations, service mesh")
        print("  🔗 Dependency Management: Health checks, retry logic, circuit breakers")
        print("  ⏳ Wait Conditions: Resource readiness, custom conditions")
        print("  💰 Cost Optimization: Resource management, scaling, spot instances")
        print("  📋 Custom Resources: CRDs, validation, controllers")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 