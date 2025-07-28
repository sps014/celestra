#!/usr/bin/env python3
"""
Advanced Application Demo for Celestra.

This example demonstrates advanced application patterns including
sidecar containers, init containers, lifecycle hooks, and health checks.
"""

from ..celestra import (
    App, StatefulApp, Service, Ingress, Secret, ConfigMap,
    Companion, Health, Lifecycle, Scaling,
    KubernetesOutput
)


def create_advanced_microservices_platform():
    """
    Create a comprehensive microservices platform with all advanced features.
    
    This example demonstrates:
    - Multi-service architecture with dependencies
    - Full observability stack
    - Canary deployment strategies  
    - External service integrations
    - Cost optimization
    - Custom resources for workflow management
    - Comprehensive security
    """
    
    # 1. Custom Resource for Application Management
    print("📋 Creating Application CRD...")
    app_crd = (CustomResource("microservice")
        .group("platform.company.com")
        .version("v1")
        .scope(CRDScope.NAMESPACED)
        .names(plural="microservices", kind="Microservice", 
               short_names=["ms"], categories=["all"])
        .add_property("image", "string", "Container image", required=True)
        .add_property("replicas", "integer", "Number of replicas", required=True, minimum=1)
        .add_property("resources", "object", "Resource requirements")
        .add_property("dependencies", "array", "Service dependencies")
        .add_status_property("phase", "string", "Current phase")
        .add_status_property("readyReplicas", "integer", "Ready replicas")
        .add_printer_column("Image", ".spec.image")
        .add_printer_column("Replicas", ".spec.replicas", "integer")
        .add_printer_column("Ready", ".status.readyReplicas", "integer")
        .add_printer_column("Phase", ".status.phase")
        .enable_subresources(status=True, scale=True)
        .add_controller("microservice-controller:v1.2.0"))
    
    # 2. External Services Configuration
    print("🌐 Configuring external services...")
    external_services = (ExternalServices("platform-externals")
        .add_database("postgres", host="postgres.rds.amazonaws.com", 
                     port=5432, ssl_enabled=True)
        .add_database("redis", type="redis", host="redis.elasticache.amazonaws.com", 
                     port=6379)
        .add_message_queue("kafka", type="kafka", 
                          endpoint="kafka.msk.amazonaws.com:9092")
        .add_storage("s3", bucket="company-microservices-data", 
                    region="us-west-2")
        .add_secret_store("vault", endpoint="vault.company.com")
        .add_monitoring_service("datadog", api_key_secret="datadog-secret")
        .add_api_service("payment-gateway", "https://api.payments.company.com",
                        timeout=30, auth_secret="payment-auth")
        .enable_service_mesh(type="istio", mutual_tls=True, 
                           circuit_breaker=True, rate_limiting=True))
    
    # 3. Observability Stack
    print("📊 Setting up observability...")
    observability = (Observability("platform-observability")
        .enable_prometheus_metrics(port=9090, path="/metrics")
        .enable_logging(level="info", format="json", retention_days=30)
        .enable_tracing(jaeger_endpoint="http://jaeger-collector:14268")
        .add_alert_rule("high_cpu", "avg(cpu_usage) > 80", severity="warning", 
                       duration="5m")
        .add_alert_rule("high_memory", "avg(memory_usage) > 90", severity="critical", 
                       duration="2m")
        .add_alert_rule("error_rate", "rate(http_requests_total{status=~'5..'}[5m]) > 0.1", 
                       severity="critical")
        .add_alert_rule("response_time", "avg(http_request_duration_seconds) > 1", 
                       severity="warning")
        .add_dashboard("platform-overview", {
            "title": "Microservices Platform Overview",
            "panels": ["cpu", "memory", "requests", "errors"]
        })
        .enable_log_aggregation(backend="elasticsearch", 
                               endpoint="elasticsearch.company.com"))
    
    # 4. Cost Optimization
    print("💰 Setting up cost optimization...")
    cost_optimization = (CostOptimization("platform-cost-optimization")
        .set_strategy(OptimizationStrategy.BALANCED)
        .set_resource_requests(cpu="100m", memory="128Mi")
        .set_resource_limits(cpu="1", memory="1Gi")
        .enable_vertical_scaling(min_cpu="50m", max_cpu="2", 
                               min_memory="64Mi", max_memory="2Gi")
        .enable_horizontal_scaling(min_replicas=2, max_replicas=20, 
                                 target_cpu=70, target_memory=80)
        .enable_spot_instances(enabled=True, fallback_to_on_demand=True)
        .set_resource_quotas(cpu="50", memory="100Gi", pods=200)
        .add_node_affinity(preferred_instances=["m5.large", "m5.xlarge"],
                          required_zones=["us-west-2a", "us-west-2b"])
        .add_cost_alert("high_hourly_cost", 500.0, "cost_per_hour")
        .add_priority_class("platform-critical", 2000)
        .add_priority_class("platform-high", 1000)
        .add_priority_class("platform-normal", 500, global_default=True))
    
    # 5. Security Configuration
    print("🔐 Configuring security...")
    security_policy = (SecurityPolicy("platform-security")
        .enable_rbac()
        .set_pod_security_standard("restricted")
        .enable_network_policies()
        .set_default_security_context(run_as_non_root=True, 
                                    read_only_root_filesystem=True))
    
    # 6. Dependency Management
    print("🔗 Setting up dependency management...")
    dependencies = (DependencyManager("platform-dependencies")
        .add_database_dependency("postgres", host="postgres.rds.amazonaws.com")
        .add_message_queue_dependency("kafka", endpoint="kafka.msk.amazonaws.com:9092", 
                                    queue_type="kafka")
        .add_service_dependency("auth-service", service_name="auth-service", 
                              health_check="/health")
        .add_api_dependency("payment-gateway", 
                           base_url="https://api.payments.company.com")
        .set_timeout("10m")
        .enable_retry(max_attempts=5, backoff="exponential")
        .enable_circuit_breaker(failure_threshold=3, timeout="60s"))
    
    # 7. Wait Conditions
    print("⏳ Setting up wait conditions...")
    wait_conditions = (WaitCondition("platform-startup-wait")
        .wait_for_tcp_connect("postgres.rds.amazonaws.com", 5432)
        .wait_for_tcp_connect("kafka.msk.amazonaws.com", 9092)
        .wait_for_deployment_ready("auth-service")
        .wait_for_http_success("http://auth-service/health")
        .wait_for_custom_command(["vault", "status"])
        .set_timeout("15m")
        .enable_parallel_checks()
        .enable_retry(max_attempts=10, delay="30s"))
    
    # 8. Deployment Strategy
    print("🚀 Configuring deployment strategy...")
    deployment_strategy = (DeploymentStrategy("platform-deployment")
        .canary_deployment(steps=[10, 25, 50, 75, 100], 
                          promotion_strategy="manual")
        .analysis(success_rate=99.0, error_rate=1.0, duration="5m")
        .traffic_splitting(method="istio", mirror_traffic=True)
        .rollback_conditions(error_rate=2.0, availability=99.0)
        .promotion_gate(approval_required=True, timeout="1h"))
    
    # 9. Core Services
    print("🏗️ Creating core services...")
    
    # Auth Service
    auth_service = (App("auth-service")
        .image("auth-service:v2.1.0")
        .port(8080, name="http")
        .port(9090, name="metrics")
        .env("LOG_LEVEL", "info")
        .env("METRICS_ENABLED", "true")
        .resources(cpu="200m", memory="256Mi")
        .scale(replicas=3)
        .health_check("/health", port=8080)
        .security_context(run_as_non_root=True))
    
    # User Service  
    user_service = (App("user-service")
        .image("user-service:v1.8.0")
        .port(8080, name="http")
        .port(9090, name="metrics")
        .env("DATABASE_URL", "postgres://postgres.rds.amazonaws.com:5432/users")
        .env("REDIS_URL", "redis://redis.elasticache.amazonaws.com:6379")
        .resources(cpu="300m", memory="512Mi")
        .scale(replicas=5)
        .health_check("/health", port=8080)
        .depends_on("auth-service"))
    
    # API Gateway
    api_gateway = (App("api-gateway")
        .image("api-gateway:v3.0.0")
        .port(8080, name="http")
        .port(9090, name="metrics")
        .env("AUTH_SERVICE_URL", "http://auth-service:8080")
        .env("USER_SERVICE_URL", "http://user-service:8080")
        .resources(cpu="500m", memory="1Gi")
        .scale(replicas=4)
        .health_check("/health", port=8080)
        .depends_on("auth-service", "user-service"))
    
    # Data Processing Service (StatefulApp)
    data_processor = (StatefulApp("data-processor")
        .image("data-processor:v1.5.0")
        .port(8080, name="http")
        .env("KAFKA_BROKERS", "kafka.msk.amazonaws.com:9092")
        .env("S3_BUCKET", "company-microservices-data")
        .resources(cpu="1", memory="2Gi")
        .scale(replicas=3)
        .storage("data", size="10Gi", storage_class="gp3")
        .backup_schedule("0 2 * * *"))
    
    # 10. Application Group
    print("📦 Creating application group...")
    platform = (AppGroup("microservices-platform")
        .add_app(auth_service)
        .add_app(user_service)
        .add_app(api_gateway)
        .add_stateful_app(data_processor)
        .set_namespace("platform")
        .add_shared_secret(Secret("platform-secrets")
            .add_data("database-password", "super-secret-password")
            .add_data("jwt-secret", "jwt-signing-key"))
        .add_shared_config(ConfigMap("platform-config")
            .add_data("environment", "production")
            .add_data("region", "us-west-2"))
        .enable_network_policies()
        .set_resource_quota(cpu="20", memory="40Gi", pods=100))
    
    # 11. Ingress
    print("🌍 Setting up ingress...")
    ingress = (Ingress("platform-ingress")
        .host("api.company.com")
        .route("/auth", "auth-service", 8080)
        .route("/users", "user-service", 8080)
        .route("/", "api-gateway", 8080)
        .enable_tls("platform-tls-cert"))
    
    # 12. Create microservice instances using custom resource
    app_crd.create_instance("auth-microservice", {
        "image": "auth-service:v2.1.0",
        "replicas": 3,
        "resources": {"cpu": "200m", "memory": "256Mi"},
        "dependencies": []
    })
    
    app_crd.create_instance("user-microservice", {
        "image": "user-service:v1.8.0", 
        "replicas": 5,
        "resources": {"cpu": "300m", "memory": "512Mi"},
        "dependencies": ["auth-service"]
    })
    
    return {
        "app_crd": app_crd,
        "external_services": external_services,
        "observability": observability,
        "cost_optimization": cost_optimization,
        "security_policy": security_policy,
        "dependencies": dependencies,
        "wait_conditions": wait_conditions,
        "deployment_strategy": deployment_strategy,
        "platform": platform,
        "ingress": ingress
    }


def main():
    """Generate the complete microservices platform."""
    print("🏗️ Building Advanced Microservices Platform with Celestra")
    print("=" * 70)
    
    # Create all components
    components = create_advanced_microservices_platform()
    
    # Generate Kubernetes manifests
    print("\n📝 Generating Kubernetes manifests...")
    
    output = KubernetesOutput("microservices-platform")
    
    # Add all components to output
    for name, component in components.items():
        print(f"  ✅ Adding {name}")
        output.add_resource(component)
    
    # Generate files
    output.generate_files("output/advanced-platform")
    
    # Summary
    print(f"\n🎉 Advanced Microservices Platform Generated!")
    print(f"📊 Features included:")
    print(f"  🔧 Core Services: Auth, User, API Gateway, Data Processor")
    print(f"  📋 Custom Resources: Microservice CRD with controller")
    print(f"  🌐 External Services: PostgreSQL, Redis, Kafka, S3, Vault")
    print(f"  📊 Observability: Prometheus, Grafana, Jaeger, ELK stack")
    print(f"  🚀 Deployment: Canary strategy with traffic splitting")
    print(f"  💰 Cost Optimization: VPA, HPA, spot instances, quotas")
    print(f"  🔐 Security: RBAC, network policies, security contexts")
    print(f"  🔗 Dependencies: Health checks, retry logic, circuit breakers")
    print(f"  ⏳ Wait Conditions: Startup orchestration and readiness")
    print(f"  🌍 Ingress: TLS-enabled external access")
    print(f"\n📁 Output files generated in: output/advanced-platform/")


if __name__ == "__main__":
    main() 