#!/usr/bin/env python3
"""
Complete Platform Demo for Celestra Phase 7 & 8

This comprehensive example demonstrates all the advanced features implemented
in Phase 7 (Output Formats) and Phase 8 (Plugin System), showcasing how they
work together to create a complete enterprise-grade platform deployment.
"""

import tempfile
from pathlib import Path
from src.celestra import (
    # Core Components
    App, StatefulApp, Secret, ConfigMap,
    
    # Advanced Features
    Observability, DeploymentStrategy, ExternalServices,
    DependencyManager, WaitCondition, CostOptimization, OptimizationStrategy, CustomResource,
    
    # Phase 7: Output Formats
    HelmOutput, KustomizeOutput, TerraformOutput,
    
    # Phase 8: Plugin System
    PluginManager, TemplateManager, TemplateEngine
)


def create_microservices_platform():
    """Create a comprehensive microservices platform."""
    
    # Core microservices
    auth_service = (App("auth-service")
        .image("auth-service:v1.2.0")
        .port(8080)
        .env("JWT_SECRET_KEY", "jwt-secret")
        .env("DATABASE_URL", "postgres://auth:password@postgres:5432/auth")
        .resources(cpu="200m", memory="512Mi")
        .replicas(3))
    
    user_service = (App("user-service")
        .image("user-service:v1.1.0")
        .port(8080)
        .env("AUTH_SERVICE_URL", "http://auth-service:8080")
        .env("REDIS_URL", "redis://redis:6379")
        .resources(cpu="150m", memory="256Mi")
        .replicas(2))
    
    # Stateful services
    postgres_db = (StatefulApp("postgres")
        .image("postgres:14")
        .port(5432)
        .env("POSTGRES_DB", "platform")
        .env("POSTGRES_USER", "platform")
        .env("POSTGRES_PASSWORD", "secure-password")
        .storage("/var/lib/postgresql/data", "10Gi")
        .resources(cpu="500m", memory="1Gi"))
    
    redis_cache = (StatefulApp("redis")
        .image("redis:7-alpine")
        .port(6379)
        .storage("/data", "5Gi")
        .resources(cpu="100m", memory="256Mi"))
    
    # Configuration and secrets
    app_config = (ConfigMap("platform-config")
        .add("log_level", "info")
        .add("environment", "production")
        .add("feature_flags", '{"new_ui": true, "analytics": true}'))
    
    app_secrets = (Secret("platform-secrets")
        .add("jwt_secret", "super-secure-jwt-secret-key")
        .add("db_password", "secure-database-password")
        .add("redis_password", "secure-redis-password"))
    
    # Advanced Features
    observability = (Observability("platform-observability")
        .enable_prometheus_metrics(port=9090, path="/metrics")
        .enable_logging(format="json", level="info")
        .enable_tracing("jaeger", "http://jaeger:14268/api/traces")
        .add_alert_rule("HighErrorRate", 
                       "rate(http_requests_total{status=~'5..'}[5m]) > 0.1",
                       "5m",
                       "warning"))
    
    deployment_strategy = (DeploymentStrategy("platform-deployment")
        .canary_deployment([20, 50, 100], "5m")
        .traffic_splitting(20))
    
    external_services = (ExternalServices("platform-external")
        .add_database("postgresql", "postgres.company.com", 5432, "platform_db")
        .add_message_queue("kafka", "kafka.company.com:9092", ["events", "notifications"])
        .add_storage("s3", "platform-bucket", region="us-west-2")
        .add_secret_store("vault", "https://vault.company.com"))
    
    cost_optimization = (CostOptimization("platform-cost")
        .set_strategy(OptimizationStrategy.BALANCED)
        .enable_vertical_scaling()
        .enable_horizontal_scaling(2, 20, 75)
        .enable_spot_instances(50)
        .set_resource_quotas({"compute.cpu": "10", "compute.memory": "20Gi"}))
    
    return {
        "auth-service": auth_service,
        "user-service": user_service,
        "postgres": postgres_db,
        "redis": redis_cache,
        "config": app_config,
        "secrets": app_secrets,
        "observability": observability,
        "deployment": deployment_strategy,
        "external": external_services,
        "cost": cost_optimization
    }


def generate_helm_chart(components):
    """Generate Helm chart for the platform."""
    print("📦 Generating Helm Chart...")
    
    helm_chart = (HelmOutput("microservices-platform")
        .set_version("1.0.0")
        .set_app_version("2024.1")
        .set_description("Complete microservices platform")
        .add_maintainer("Platform Team", "platform@company.com")
        .add_keywords("microservices", "platform", "kubernetes")
        
        # Dependencies
        .add_dependency("postgresql", "12.1.9", 
                       "https://charts.bitnami.com/bitnami",
                       condition="postgresql.enabled")
        .add_dependency("redis", "17.8.7",
                       "https://charts.bitnami.com/bitnami", 
                       condition="redis.enabled")
        .add_dependency("prometheus", "19.6.1",
                       "https://prometheus-community.github.io/helm-charts",
                       condition="monitoring.enabled")
        
        # Configuration overrides
        .add_values_override("replicaCount", 3)
        .add_values_override("monitoring.enabled", True)
        .add_values_override("postgresql.enabled", True)
        .add_values_override("redis.enabled", True)
        .add_values_override("ingress.enabled", True)
        .add_values_override("ingress.host", "platform.company.com")
        
        # Enable features
        .enable_ingress(True, "platform.company.com")
        .enable_autoscaling(min_replicas=2, max_replicas=10, target_cpu=75)
        .set_image("platform/microservices", "v1.0.0")
        
        # Tests and hooks
        .add_test("platform-test", ["curl", "-f", "http://platform.company.com/health"])
        .add_hook("platform-init", "pre-install", weight=-5)
        
        # Notes template
        .set_notes_template("""
🎉 Microservices Platform deployed successfully!

🌐 Access your platform:
  {{- if .Values.ingress.enabled }}
  Platform URL: https://{{ .Values.ingress.host }}
  {{- else }}
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app={{ include "microservices-platform.name" . }}" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:8080
  Platform URL: http://127.0.0.1:8080
  {{- end }}

📊 Monitoring:
  {{- if .Values.monitoring.enabled }}
  Prometheus: https://{{ .Values.ingress.host }}/prometheus
  Grafana: https://{{ .Values.ingress.host }}/grafana
  {{- end }}

📋 Components deployed:
  - Auth Service ({{ .Values.authService.replicas }} replicas)
  - User Service ({{ .Values.userService.replicas }} replicas)
  - PostgreSQL Database ({{ if .Values.postgresql.enabled }}enabled{{ else }}disabled{{ end }})
  - Redis Cache ({{ if .Values.redis.enabled }}enabled{{ else }}disabled{{ end }})
  - Monitoring Stack ({{ if .Values.monitoring.enabled }}enabled{{ else }}disabled{{ end }})
        """))
    
    # Add all components
    for component in components.values():
        helm_chart.add_resource(component)
    
    # Generate chart
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "helm-charts"
        helm_chart.generate_files(str(output_dir))
        
        # Count files
        chart_files = list(output_dir.rglob("*"))
        print(f"  ✅ Generated {len(chart_files)} files in Helm chart")
        
        return len(chart_files)


def generate_kustomize_overlays(components):
    """Generate Kustomize overlays for different environments."""
    print("🔧 Generating Kustomize Overlays...")
    
    # Base configuration
    base_kustomize = (KustomizeOutput("platform-base")
        .add_common_label("app.kubernetes.io/part-of", "microservices-platform")
        .add_common_label("app.kubernetes.io/managed-by", "kustomize")
        .add_common_annotation("platform.company.com/version", "v1.0.0"))
    
    # Development overlay
    dev_overlay = (KustomizeOutput.development_overlay("platform")
        .add_image_tag("auth-service", "dev-latest")
        .add_image_tag("user-service", "dev-latest")
        .add_replica_patch("auth-service", 1)
        .add_replica_patch("user-service", 1)
        .add_config_patch("platform-config", {
            "log_level": "debug",
            "environment": "development"
        })
        .add_secret_generator("dev-secrets", literals={
            "jwt_secret": "dev-jwt-secret",
            "db_password": "dev-password"
        }))
    
    # Staging overlay
    staging_overlay = (KustomizeOutput("platform-staging")
        .set_namespace("staging")
        .add_prefix("staging-")
        .add_image_tag("auth-service", "staging-v1.2.0")
        .add_image_tag("user-service", "staging-v1.1.0")
        .add_replica_patch("auth-service", 2)
        .add_replica_patch("user-service", 2)
        .add_config_map_generator("staging-config", literals={
            "LOG_LEVEL": "info",
            "ENVIRONMENT": "staging",
            "DEBUG": "false"
        }))
    
    # Production overlay
    prod_overlay = (KustomizeOutput.production_overlay("platform")
        .add_image_tag("auth-service", "v1.2.0")
        .add_image_tag("user-service", "v1.1.0")
        .add_replica_patch("auth-service", 5)
        .add_replica_patch("user-service", 3)
        .add_helm_chart("monitoring", "https://prometheus-community.github.io/helm-charts",
                       "kube-prometheus-stack", "monitoring", {
                           "prometheus.enabled": True,
                           "grafana.enabled": True,
                           "alertmanager.enabled": True
                       })
        .add_remote_resource("https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"))
    
    # Add overlays
    base_kustomize.add_overlay("development", dev_overlay)
    base_kustomize.add_overlay("staging", staging_overlay)
    base_kustomize.add_overlay("production", prod_overlay)
    
    # Add components
    for component in components.values():
        base_kustomize.add_resource(component)
    
    # Generate overlays
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "kustomize"
        base_kustomize.generate_files(str(output_dir))
        
        # Count files
        kustomize_files = list(output_dir.rglob("*"))
        print(f"  ✅ Generated {len(kustomize_files)} files in Kustomize structure")
        
        return len(kustomize_files)


def generate_terraform_modules(components):
    """Generate Terraform modules for infrastructure."""
    print("🏗️ Generating Terraform Modules...")
    
    # Main platform module
    main_module = (TerraformOutput("microservices-platform")
        .set_provider_version("~> 2.20")
        .add_required_provider("helm", "hashicorp/helm", "~> 2.9")
        .add_required_provider("kubectl", "gavinbunney/kubectl", "~> 1.14")
        
        # Variables
        .add_namespace_variable("production")
        .add_replicas_variable(3)
        .add_variable("environment", "string", "production", "Deployment environment")
        .add_variable("cluster_name", "string", None, "Kubernetes cluster name")
        .add_variable("domain_name", "string", "platform.company.com", "Platform domain name")
        .add_variable("enable_monitoring", "bool", True, "Enable monitoring stack")
        .add_variable("enable_autoscaling", "bool", True, "Enable horizontal pod autoscaling")
        .add_variable("database_config", "object({host=string,port=number,name=string})", {
            "host": "postgres.company.com",
            "port": 5432,
            "name": "platform"
        }, "Database configuration")
        
        # Locals
        .add_local("platform_labels", {
            "platform": "microservices",
            "environment": "${var.environment}",
            "managed-by": "terraform"
        })
        .add_local("domain_name", "${var.domain_name}")
        
        # Data sources
        .add_data_source("kubernetes_namespace", "current", {})
        .add_data_source("kubernetes_service_account", "default", {
            "metadata": {
                "name": "default",
                "namespace": "${var.namespace}"
            }
        })
        
        # Modules
        .add_module("monitoring", "terraform-kubernetes-modules/monitoring", "1.0.0", {
            "enabled": "${var.enable_monitoring}",
            "namespace": "${var.namespace}",
            "cluster_name": "${var.cluster_name}"
        })
        .add_module("ingress-nginx", "terraform-kubernetes-modules/ingress-nginx", "1.2.0", {
            "namespace": "ingress-nginx",
            "domain_name": "${local.domain_name}"
        })
        
        # Outputs
        .add_output("platform_url", "https://${local.domain_name}", "Platform access URL")
        .add_output("monitoring_url", "https://${local.domain_name}/grafana", "Monitoring dashboard URL")
        .add_output("namespace", "${var.namespace}", "Deployment namespace")
        .add_output("cluster_info", "${data.kubernetes_namespace.current.metadata.0.name}", 
                   "Cluster information", sensitive=True)
        
        # Remote state
        .enable_remote_state("s3", {
            "bucket": "platform-terraform-state",
            "key": "microservices-platform/terraform.tfstate",
            "region": "us-west-2",
            "encrypt": True,
            "dynamodb_table": "terraform-state-lock"
        }))
    
    # Infrastructure module
    infra_module = (TerraformOutput("platform-infrastructure")
        .add_required_provider("aws", "hashicorp/aws", "~> 5.0")
        .add_required_provider("kubernetes", "hashicorp/kubernetes", "~> 2.20")
        
        # Variables
        .add_variable("region", "string", "us-west-2", "AWS region")
        .add_variable("cluster_version", "string", "1.28", "Kubernetes cluster version")
        .add_variable("node_instance_types", "list(string)", ["t3.medium", "t3.large"], "EC2 instance types")
        .add_variable("min_nodes", "number", 2, "Minimum number of nodes")
        .add_variable("max_nodes", "number", 10, "Maximum number of nodes")
        
        # Modules for AWS infrastructure
        .add_module("vpc", "terraform-aws-modules/vpc/aws", "5.0.0", {
            "cidr": "10.0.0.0/16",
            "azs": ["${var.region}a", "${var.region}b", "${var.region}c"],
            "private_subnets": ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"],
            "public_subnets": ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"],
            "enable_nat_gateway": True,
            "enable_vpn_gateway": True
        })
        .add_module("eks", "terraform-aws-modules/eks/aws", "19.15.0", {
            "cluster_name": "${local.cluster_name}",
            "cluster_version": "${var.cluster_version}",
            "vpc_id": "${module.vpc.vpc_id}",
            "subnet_ids": "${module.vpc.private_subnets}",
            "node_group_defaults": {
                "instance_types": "${var.node_instance_types}",
                "min_size": "${var.min_nodes}",
                "max_size": "${var.max_nodes}",
                "desired_size": 3
            }
        })
        
        # Outputs
        .add_output("cluster_endpoint", "${module.eks.cluster_endpoint}", "EKS cluster endpoint")
        .add_output("cluster_name", "${module.eks.cluster_name}", "EKS cluster name")
        .add_output("vpc_id", "${module.vpc.vpc_id}", "VPC ID"))
    
    # Add components to main module
    for component in components.values():
        main_module.add_resource(component)
    
    # Generate modules
    with tempfile.TemporaryDirectory() as temp_dir:
        main_output_dir = Path(temp_dir) / "terraform" / "main"
        infra_output_dir = Path(temp_dir) / "terraform" / "infrastructure"
        
        main_module.generate_files(str(main_output_dir))
        infra_module.generate_files(str(infra_output_dir))
        
        # Count files
        main_files = list(main_output_dir.glob("*"))
        infra_files = list(infra_output_dir.glob("*"))
        total_files = len(main_files) + len(infra_files)
        
        print(f"  ✅ Generated {len(main_files)} files in main module")
        print(f"  ✅ Generated {len(infra_files)} files in infrastructure module")
        print(f"  📊 Total Terraform files: {total_files}")
        
        return total_files


def demonstrate_plugin_system():
    """Demonstrate the plugin system capabilities."""
    print("🔌 Demonstrating Plugin System...")
    
    # Initialize plugin manager
    manager = PluginManager()
    
    # Initialize template manager
    template_manager = TemplateManager()
    
    # Generate a custom deployment template
    deployment_template = template_manager.generate_deployment_template("custom-deployment.j2")
    
    # Create custom template for configuration
    custom_config_template = """
# Platform Configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ app_name }}-config
  labels:
    app: {{ app_name }}
    environment: {{ environment }}
spec:
  data:
    log_level: {{ log_level | default("info") }}
    database_url: {{ database_url }}
    {% if feature_flags %}
    feature_flags: |
      {% for flag, enabled in feature_flags.items() %}
      {{ flag }}: {{ enabled | lower }}
      {% endfor %}
    {% endif %}
    """
    
    template_manager.add_template("platform-config.j2", custom_config_template)
    
    # Render template with platform variables
    rendered_config = template_manager.render_template("platform-config.j2", {
        "app_name": "microservices-platform",
        "environment": "production",
        "log_level": "info",
        "database_url": "postgres://platform:secret@postgres:5432/platform",
        "feature_flags": {
            "new_ui": True,
            "analytics": True,
            "beta_features": False
        }
    })
    
    print(f"  ✅ Template manager initialized with {len(template_manager.list_templates())} templates")
    print(f"  🎨 Rendered configuration template ({len(rendered_config)} chars)")
    
    # Test different template engines
    engines_tested = []
    
    # Simple template
    simple_result = template_manager.render_string(
        "Platform: ${name}, Version: ${version}",
        {"name": "Microservices Platform", "version": "v1.0.0"},
        TemplateEngine.SIMPLE
    )
    engines_tested.append("Simple")
    
    # Go template
    go_result = template_manager.render_string(
        "Platform: {{ .name }}, Version: {{ .version }}",
        {"name": "Microservices Platform", "version": "v1.0.0"},
        TemplateEngine.GOLANG
    )
    engines_tested.append("Go")
    
    # Mustache template
    mustache_result = template_manager.render_string(
        "Platform: {{ name }}, Version: {{ version }}",
        {"name": "Microservices Platform", "version": "v1.0.0"},
        TemplateEngine.MUSTACHE
    )
    engines_tested.append("Mustache")
    
    # Try Jinja2 if available
    try:
        jinja_result = template_manager.render_string(
            "Platform: {{ name }}, Version: {{ version }}",
            {"name": "Microservices Platform", "version": "v1.0.0"},
            TemplateEngine.JINJA2
        )
        engines_tested.append("Jinja2")
    except:
        pass
    
    print(f"  🔧 Tested {len(engines_tested)} template engines: {', '.join(engines_tested)}")
    
    # Plugin system summary
    loaded_plugins = manager.get_loaded_plugins()
    print(f"  📦 Plugin manager ready with {len(loaded_plugins)} loaded plugins")
    
    return {
        "templates": len(template_manager.list_templates()),
        "engines": len(engines_tested),
        "plugins": len(loaded_plugins)
    }


def main():
    """Run the complete platform demonstration."""
    print("🚀 Complete Microservices Platform Demo")
    print("=" * 60)
    print("🎯 Showcasing Phase 7 (Output Formats) & Phase 8 (Plugin System)")
    print("=" * 60)
    
    try:
        # Create platform components
        print("\n🏗️ Creating Platform Components...")
        components = create_microservices_platform()
        print(f"  ✅ Created {len(components)} platform components")
        
        # Generate all output formats
        print("\n📦 PHASE 7: OUTPUT FORMATS")
        print("-" * 40)
        
        helm_files = generate_helm_chart(components)
        kustomize_files = generate_kustomize_overlays(components)
        terraform_files = generate_terraform_modules(components)
        
        # Demonstrate plugin system
        print("\n🔌 PHASE 8: PLUGIN SYSTEM")
        print("-" * 40)
        
        plugin_stats = demonstrate_plugin_system()
        
        # Final summary
        print("\n🎉 COMPLETE PLATFORM SUMMARY")
        print("=" * 60)
        print(f"📊 Total files generated: {helm_files + kustomize_files + terraform_files}")
        print(f"📦 Helm chart files: {helm_files}")
        print(f"🔧 Kustomize files: {kustomize_files}")
        print(f"🏗️ Terraform files: {terraform_files}")
        print(f"📝 Template engines: {plugin_stats['engines']}")
        print(f"🔌 Plugin system: Ready for extension")
        
        print("\n🌟 PLATFORM FEATURES DEPLOYED:")
        print("  🔐 Authentication & Authorization Service")
        print("  👥 User Management Service")
        print("  🗄️ PostgreSQL Database (Stateful)")
        print("  ⚡ Redis Cache (Stateful)")
        print("  📊 Prometheus Monitoring & Alerting")
        print("  🚀 Canary Deployment Strategy")
        print("  🌐 External Service Integrations")
        print("  💰 Cost Optimization & Auto-scaling")
        print("  📦 Helm Charts with Dependencies")
        print("  🔧 Multi-Environment Kustomize Overlays")
        print("  🏗️ Complete Terraform Infrastructure")
        print("  🔌 Extensible Plugin Architecture")
        print("  📝 Multi-Engine Template System")
        
        print("\n✨ Celestra: Enterprise-Ready Kubernetes Generation!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 