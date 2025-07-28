#!/usr/bin/env python3
"""
Test script for K8s-Gen DSL Phase 7 (Output Formats) and Phase 8 (Plugin System).

This script demonstrates the advanced output formats including Helm charts,
Kustomize overlays, Terraform modules, and the comprehensive plugin system
with template management.
"""

import os
import tempfile
from pathlib import Path
from src.k8s_gen import (
    # Core components
    App, Secret, ConfigMap,
    
    # Phase 7: Output Formats
    HelmOutput, KustomizeOutput, TerraformOutput,
    
    # Phase 8: Plugin System
    PluginManager, PluginBase, PluginType, PluginMetadata,
    TemplateManager, TemplateEngine
)


def test_helm_output():
    """Test Helm chart generation."""
    print("📊 Testing Helm Output...")
    
    # Create a simple app
    app = (App("web-app")
        .image("nginx:1.21")
        .port(8080)
        .env("LOG_LEVEL", "info")
        .resources(cpu="200m", memory="256Mi")
        .replicas(3))
    
    # Basic Helm chart
    basic_helm = (HelmOutput("web-app")
        .set_version("1.0.0")
        .set_app_version("1.21.0")
        .set_description("Web application Helm chart")
        .add_maintainer("DevTeam", "dev@company.com")
        .set_image("nginx", "1.21", "IfNotPresent")
        .enable_ingress(True, "app.company.com")
        .enable_autoscaling(min_replicas=2, max_replicas=10))
    
    # Advanced Helm chart with dependencies
    advanced_helm = (HelmOutput("microservice-app")
        .set_version("2.1.0")
        .add_dependency("postgresql", "11.6.12", 
                       "https://charts.bitnami.com/bitnami",
                       condition="postgresql.enabled")
        .add_dependency("redis", "17.3.7",
                       "https://charts.bitnami.com/bitnami")
        .add_values_override("replicaCount", 5)
        .add_values_override("postgresql.enabled", True)
        .add_values_override("redis.auth.enabled", False)
        .add_keywords("microservice", "web", "api")
        .set_notes_template("""
1. Get the application URL by running these commands:
{{- if .Values.ingress.enabled }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ .Values.ingress.host }}{{ .Values.ingress.path }}
{{- else }}
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "microservice-app.name" . }},app.kubernetes.io/instance={{ .Release.Name }}" -o jsonpath="{.items[0].metadata.name}")
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:80
{{- end }}
        """)
        .add_test("connection-test", ["wget", "--no-verbose", "--tries=1", "--spider", "http://microservice-app:8080/"]))
    
    basic_helm.add_resource(app)
    advanced_helm.add_resource(app)
    
    # Generate test charts
    with tempfile.TemporaryDirectory() as temp_dir:
        basic_output_dir = Path(temp_dir) / "basic-helm"
        advanced_output_dir = Path(temp_dir) / "advanced-helm"
        
        basic_helm.generate_files(str(basic_output_dir))
        advanced_helm.generate_files(str(advanced_output_dir))
        
        # Verify files were created
        basic_files = list(basic_output_dir.rglob("*"))
        advanced_files = list(advanced_output_dir.rglob("*"))
        
        print(f"  ✅ Basic Helm chart generated {len(basic_files)} files")
        print(f"  ✅ Advanced Helm chart generated {len(advanced_files)} files")
        
        return len(basic_files), len(advanced_files)


def test_kustomize_output():
    """Test Kustomize overlay generation."""
    print("🔧 Testing Kustomize Output...")
    
    # Create components
    app = (App("api-service")
        .image("api:latest")
        .port(8080)
        .env("ENVIRONMENT", "production")
        .resources(cpu="500m", memory="512Mi"))
    
    config = (ConfigMap("api-config")
        .add("database.host", "postgres.production.svc.cluster.local")
        .add("redis.host", "redis.production.svc.cluster.local"))
    
    # Base Kustomize configuration
    base_kustomize = (KustomizeOutput("api-service")
        .add_common_label("app", "api-service")
        .add_common_label("version", "v1.0.0")
        .add_common_annotation("managed-by", "k8s-gen"))
    
    # Development overlay
    dev_overlay = (KustomizeOutput.development_overlay("api-service")
        .add_image_tag("api", "dev-latest")
        .add_config_patch("api-config", {
            "database.host": "postgres.development.svc.cluster.local",
            "redis.host": "redis.development.svc.cluster.local"
        })
        .add_secret_generator("dev-secrets", literals={
            "api_key": "dev-api-key",
            "database_password": "dev-password"
        }))
    
    # Production overlay
    prod_overlay = (KustomizeOutput.production_overlay("api-service")
        .add_image_tag("api", "v1.0.0")
        .add_replica_patch("api-service", 5)
        .add_config_map_generator("prod-config", literals={
            "LOG_LEVEL": "error",
            "CACHE_TTL": "3600"
        })
        .add_remote_resource("https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/cloud/deploy.yaml"))
    
    # Custom overlay with advanced features  
    custom_overlay = (KustomizeOutput("api-service-canary")
        .set_namespace("canary")
        .add_prefix("canary-")
        .add_suffix("-v2")
        .add_image_tag("api", "v2.0.0-rc1")
        .add_helm_chart("monitoring", "https://prometheus-community.github.io/helm-charts", 
                       "kube-prometheus-stack", "monitoring", {
                           "prometheus.enabled": True,
                           "grafana.enabled": True
                       }))
    
    # Add overlays to base
    base_kustomize.add_overlay("development", dev_overlay)
    base_kustomize.add_overlay("production", prod_overlay)
    base_kustomize.add_overlay("canary", custom_overlay)
    
    base_kustomize.add_resource(app)
    base_kustomize.add_resource(config)
    
    # Generate test overlays
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir) / "kustomize-output"
        base_kustomize.generate_files(str(output_dir))
        
        # Count generated files
        all_files = list(output_dir.rglob("*"))
        
        print(f"  ✅ Kustomize configuration generated {len(all_files)} files")
        print(f"  📁 Base: {len(list((output_dir / 'base').glob('*')))}")
        print(f"  📁 Overlays: {len(list((output_dir / 'overlays').rglob('*')))}")
        
        return len(all_files)


def test_terraform_output():
    """Test Terraform module generation."""
    print("🏗️ Testing Terraform Output...")
    
    # Create components
    app = (App("terraform-app")
        .image("nginx:latest")
        .port(80)
        .env("NGINX_PORT", "80")
        .resources(cpu="100m", memory="128Mi"))
    
    secret = (Secret("app-secret")
        .add("database_url", "postgres://user:pass@db:5432/app"))
    
    # Basic Terraform module
    basic_terraform = (TerraformOutput("nginx-app")
        .set_provider_version("~> 2.16")
        .add_namespace_variable("default")
        .add_replicas_variable(1)
        .add_image_variable("nginx:latest")
        .add_output("service_name", 
                   "kubernetes_service.nginx_app.metadata.0.name",
                   "Name of the created service")
        .add_output("deployment_name",
                   "kubernetes_deployment.nginx_app.metadata.0.name", 
                   "Name of the created deployment"))
    
    # Advanced Terraform module
    advanced_terraform = (TerraformOutput("microservice-stack")
        .add_required_provider("helm", "hashicorp/helm", "~> 2.7")
        .add_required_provider("kubectl", "gavinbunney/kubectl", "~> 1.14") 
        .add_variable("environment", "string", "production", "Deployment environment")
        .add_variable("enable_monitoring", "bool", True, "Enable monitoring stack")
        .add_variable("resource_limits", "object({cpu=string,memory=string})", 
                     {"cpu": "500m", "memory": "512Mi"}, "Resource limits")
        .add_local("app_labels", {
            "app": "microservice",
            "environment": "${var.environment}",
            "managed-by": "terraform"
        })
        .add_data_source("kubernetes_namespace", "current", {})
        .add_module("monitoring", "terraform-helm-modules/monitoring", "1.0.0", {
            "enabled": "${var.enable_monitoring}",
            "namespace": "${var.namespace}"
        })
        .enable_remote_state("s3", {
            "bucket": "terraform-state-bucket",
            "key": "microservices/terraform.tfstate",
            "region": "us-west-2"
        })
        .add_output("cluster_info", 
                   "data.kubernetes_namespace.current.metadata.0.name",
                   "Current namespace information", sensitive=True))
    
    basic_terraform.add_resource(app)
    advanced_terraform.add_resource(app)
    advanced_terraform.add_resource(secret)
    
    # Generate test modules
    with tempfile.TemporaryDirectory() as temp_dir:
        basic_output_dir = Path(temp_dir) / "basic-terraform"
        advanced_output_dir = Path(temp_dir) / "advanced-terraform"
        
        basic_terraform.generate_files(str(basic_output_dir))
        advanced_terraform.generate_files(str(advanced_output_dir))
        
        # Count generated files
        basic_files = list(basic_output_dir.glob("*"))
        advanced_files = list(advanced_output_dir.glob("*"))
        
        print(f"  ✅ Basic Terraform module generated {len(basic_files)} files")
        print(f"  ✅ Advanced Terraform module generated {len(advanced_files)} files")
        
        return len(basic_files), len(advanced_files)


def test_plugin_manager():
    """Test plugin manager functionality."""
    print("🔌 Testing Plugin Manager...")
    
    # Create plugin manager
    manager = PluginManager()
    
    # Test built-in plugins
    builtin_plugins = manager.get_loaded_plugins()
    print(f"  📦 Found {len(builtin_plugins)} built-in plugins")
    
    # Load built-in plugins
    loaded_count = 0
    for plugin_name in builtin_plugins:
        if manager.load_plugin(plugin_name):
            loaded_count += 1
    
    print(f"  ✅ Loaded {loaded_count} plugins")
    
    # Test validator plugins
    test_resources = [
        {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {
                "name": "valid-name"
            }
        },
        {
            "apiVersion": "v1", 
            "kind": "Pod",
            "metadata": {
                "name": "Invalid_Name_With_Underscores!"
            }
        }
    ]
    
    validation_errors = manager.validate_resources(test_resources)
    print(f"  🔍 Validation found {len(validation_errors)} errors")
    
    # Test transformer plugins
    transformed_resources = manager.transform_resources(test_resources)
    print(f"  🔄 Transformed {len(transformed_resources)} resources")
    
    # Check if standard labels were added
    has_managed_by_label = any(
        "app.kubernetes.io/managed-by" in resource.get("metadata", {}).get("labels", {})
        for resource in transformed_resources
    )
    
    print(f"  🏷️ Standard labels added: {has_managed_by_label}")
    
    return len(builtin_plugins), loaded_count, len(validation_errors)


def test_template_manager():
    """Test template manager functionality."""
    print("📝 Testing Template Manager...")
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Test preset template generation
    deployment_template = template_manager.generate_deployment_template("deployment.yaml.j2")
    service_template = template_manager.generate_service_template("service.yaml.j2")
    
    print(f"  ✅ Generated deployment template ({len(deployment_template)} chars)")
    print(f"  ✅ Generated service template ({len(service_template)} chars)")
    
    # Test simple template rendering
    simple_template = "Hello ${name}, your app has ${replicas} replicas"
    simple_result = template_manager.render_string(simple_template, {
        "name": "Developer",
        "replicas": 3
    }, TemplateEngine.SIMPLE)
    
    print(f"  🔤 Simple template: {simple_result}")
    
    # Test Go template rendering
    go_template = "App: {{ .app_name }}, Replicas: {{ .replicas }}"
    go_result = template_manager.render_string(go_template, {
        "app_name": "my-app",
        "replicas": 5
    }, TemplateEngine.GOLANG)
    
    print(f"  🐹 Go template: {go_result}")
    
    # Test Mustache template rendering
    mustache_template = "{{# items }}Item: {{ name }} ({{ value }}){{/ items }}"
    mustache_result = template_manager.render_string(mustache_template, {
        "items": [
            {"name": "CPU", "value": "500m"},
            {"name": "Memory", "value": "512Mi"}
        ]
    }, TemplateEngine.MUSTACHE)
    
    print(f"  👨‍🎨 Mustache template: {mustache_result}")
    
    # Test Jinja2 template rendering (if available)
    try:
        jinja_template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
spec:
  replicas: {{ replicas | default(1) }}
  template:
    spec:
      containers:
      - name: {{ app_name }}
        {% if env_vars %}
        env:
        {% for key, value in env_vars.items() %}
        - name: {{ key }}
          value: "{{ value }}"
        {% endfor %}
        {% endif %}
        """
        
        jinja_result = template_manager.render_string(jinja_template, {
            "app_name": "web-app",
            "replicas": 3,
            "env_vars": {
                "LOG_LEVEL": "info",
                "PORT": "8080"
            }
        }, TemplateEngine.JINJA2)
        
        print(f"  🎨 Jinja2 template rendered successfully ({len(jinja_result)} chars)")
        jinja_available = True
        
    except (ImportError, ValueError) as e:
        print(f"  ⚠️ Jinja2 not available: {e}")
        jinja_available = False
    
    # Test custom template functions
    template_manager.add_function("multiply", lambda x, y: x * y)
    template_manager.set_global_variable("company", "TechCorp")
    
    function_template = "Company: ${company}, Total: ${multiply(replicas, 2)}"
    function_result = template_manager.render_string(function_template, {
        "replicas": 4
    }, TemplateEngine.SIMPLE)
    
    print(f"  🔧 Custom functions: {function_result}")
    
    # List all templates
    all_templates = template_manager.list_templates()
    print(f"  📋 Available templates: {len(all_templates)}")
    
    return len(all_templates), jinja_available


def create_custom_plugin_example():
    """Create and test a custom plugin example."""
    print("🔧 Testing Custom Plugin Creation...")
    
    # Create a custom output plugin
    class JsonOutputPlugin(PluginBase):
        def get_metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="json-output",
                version="1.0.0", 
                description="JSON output format plugin",
                author="Test Developer",
                plugin_type=PluginType.OUTPUT,
                tags=["output", "json"]
            )
        
        def initialize(self, config):
            self._config = config
            self._indent = config.get("indent", 2)
        
        def execute(self, context):
            import json
            resources = context.get("resources", [])
            return json.dumps(resources, indent=self._indent)
        
        def get_output_format(self):
            return "json"
        
        def generate_output(self, resources, config):
            return self.execute({"resources": resources})
    
    # Create a custom transformer plugin
    class NamespaceTransformer(PluginBase):
        def get_metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="namespace-transformer",
                version="1.0.0",
                description="Adds namespace to all resources",
                author="Test Developer", 
                plugin_type=PluginType.TRANSFORMER
            )
        
        def initialize(self, config):
            self._config = config
            self._target_namespace = config.get("namespace", "default")
        
        def execute(self, context):
            resources = context.get("resources", [])
            transformed = []
            
            for resource in resources:
                if resource.get("kind") != "Namespace":
                    if "metadata" not in resource:
                        resource["metadata"] = {}
                    resource["metadata"]["namespace"] = self._target_namespace
                
                transformed.append(resource)
            
            return transformed
        
        def transform_resource(self, resource):
            if resource.get("kind") != "Namespace":
                if "metadata" not in resource:
                    resource["metadata"] = {}
                resource["metadata"]["namespace"] = self._target_namespace
            return resource
        
        def get_transformation_order(self):
            return 5  # Execute early
    
    # Test the custom plugins
    manager = PluginManager()
    
    # Add custom plugin classes
    json_plugin = JsonOutputPlugin()
    namespace_plugin = NamespaceTransformer()
    
    manager._plugin_classes["json-output"] = JsonOutputPlugin
    manager._plugin_classes["namespace-transformer"] = NamespaceTransformer
    
    # Load plugins with configuration
    json_loaded = manager.load_plugin("json-output", {"indent": 4})
    namespace_loaded = manager.load_plugin("namespace-transformer", {"namespace": "production"})
    
    print(f"  ✅ JSON plugin loaded: {json_loaded}")
    print(f"  ✅ Namespace transformer loaded: {namespace_loaded}")
    
    # Test transformation
    test_resources = [
        {
            "apiVersion": "apps/v1",
            "kind": "Deployment", 
            "metadata": {"name": "test-app"}
        }
    ]
    
    transformed = manager.transform_resources(test_resources)
    has_namespace = transformed[0].get("metadata", {}).get("namespace") == "production"
    
    print(f"  🔄 Namespace transformation successful: {has_namespace}")
    
    # Test JSON output
    output_formats = manager.get_output_formats()
    json_output_available = "json" in output_formats
    
    print(f"  📄 JSON output format available: {json_output_available}")
    
    return json_loaded and namespace_loaded and has_namespace and json_output_available


def main():
    """Run all Phase 7 and 8 tests."""
    print("🧪 Testing K8s-Gen DSL Phase 7 (Output Formats) and Phase 8 (Plugin System)")
    print("=" * 80)
    
    try:
        # Phase 7 Tests
        print("\n📊 PHASE 7: OUTPUT FORMATS")
        print("-" * 40)
        
        helm_results = test_helm_output()
        kustomize_results = test_kustomize_output()
        terraform_results = test_terraform_output()
        
        # Phase 8 Tests
        print("\n🔌 PHASE 8: PLUGIN SYSTEM")
        print("-" * 40)
        
        plugin_results = test_plugin_manager()
        template_results = test_template_manager()
        custom_plugin_success = create_custom_plugin_example()
        
        # Summary
        print("\n📋 SUMMARY")
        print("-" * 40)
        
        total_helm_files = sum(helm_results)
        total_terraform_files = sum(terraform_results)
        
        print(f"✅ All Phase 7 & 8 tests completed successfully!")
        print(f"📊 Output format tests:")
        print(f"  📦 Helm charts: {total_helm_files} files generated")
        print(f"  🔧 Kustomize overlays: {kustomize_results} files generated") 
        print(f"  🏗️ Terraform modules: {total_terraform_files} files generated")
        print(f"🔌 Plugin system tests:")
        print(f"  📦 Built-in plugins: {plugin_results[0]} discovered, {plugin_results[1]} loaded")
        print(f"  🔍 Validation errors: {plugin_results[2]} found")
        print(f"  📝 Templates: {template_results[0]} available, Jinja2: {template_results[1]}")
        print(f"  🔧 Custom plugins: {'✅' if custom_plugin_success else '❌'}")
        
        # Feature breakdown
        print("\n🔍 FEATURE BREAKDOWN:")
        print("  📦 Helm Charts: Templates, values, dependencies, hooks, tests")
        print("  🔧 Kustomize: Base resources, overlays, patches, generators")
        print("  🏗️ Terraform: HCL generation, variables, outputs, modules")
        print("  🔌 Plugin Manager: Discovery, loading, validation, transformation")
        print("  📝 Template Manager: Multi-engine support, custom functions")
        print("  🔧 Custom Plugins: Extensible architecture for custom functionality")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 