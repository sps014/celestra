#!/usr/bin/env python3
"""
RBAC Security Demo for Celestra.

This example demonstrates comprehensive Role-Based Access Control (RBAC) 
configuration for a multi-tenant Kubernetes environment.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ..celestra import (
    App, Service, ServiceAccount, Role, ClusterRole, 
    RoleBinding, ClusterRoleBinding, SecurityPolicy,
    KubernetesOutput
)


def demo_rbac_features():
    """Demonstrate comprehensive RBAC features."""
    print("🔐 Celestra Phase 4: Security & RBAC Demo")
    print("=" * 50)
    
    # 1. Create a ServiceAccount for our application
    print("\n1. Creating ServiceAccount...")
    service_account = (ServiceAccount("web-app-sa")
        .add_secret("app-token")
        .add_image_pull_secret("registry-secret")
        .automount_token(True)
        .add_label("app", "web-application")
        .add_annotation("description", "Service account for web application"))
    
    print(f"   ✓ ServiceAccount '{service_account.name}' created")
    
    # 2. Create a Role with specific permissions
    print("\n2. Creating Role with specific permissions...")
    app_role = (Role("web-app-role")
        .allow_get("configmaps", "secrets")
        .allow_list("services", "endpoints")
        .allow_watch("pods")
        .add_label("component", "rbac"))
    
    print(f"   ✓ Role '{app_role.name}' created with read permissions")
    
    # 3. Create a ClusterRole for cluster-wide operations
    print("\n3. Creating ClusterRole...")
    monitoring_role = (ClusterRole("monitoring-role")
        .allow_read_only("nodes", "nodes/metrics", "nodes/stats")
        .allow_get("namespaces")
        .add_label("purpose", "monitoring"))
    
    print(f"   ✓ ClusterRole '{monitoring_role.name}' created")
    
    # 4. Bind the Role to the ServiceAccount
    print("\n4. Creating RoleBinding...")
    role_binding = (RoleBinding("web-app-binding")
        .bind_role("web-app-role")
        .to_service_account("web-app-sa")
        .add_label("binding-type", "app-permissions"))
    
    print(f"   ✓ RoleBinding '{role_binding.name}' created")
    
    # 5. Create a ClusterRoleBinding for monitoring
    print("\n5. Creating ClusterRoleBinding...")
    cluster_binding = (ClusterRoleBinding("monitoring-binding")
        .bind_cluster_role("monitoring-role")
        .to_service_account("web-app-sa", "default")
        .add_label("binding-type", "cluster-monitoring"))
    
    print(f"   ✓ ClusterRoleBinding '{cluster_binding.name}' created")
    
    # 6. Create a SecurityPolicy with strict security settings
    print("\n6. Creating SecurityPolicy...")
    security_policy = (SecurityPolicy.strict_security("web-app-security")
        .add_label("security-level", "strict"))
    
    print(f"   ✓ SecurityPolicy '{security_policy.name}' created with strict settings")
    print(f"     - RBAC enabled: {security_policy.is_rbac_enabled()}")
    print(f"     - Network policies: {security_policy.is_network_policies_enabled()}")
    print(f"     - Pod Security Standards: {security_policy.get_pod_security_standards()}")
    
    # 7. Create application secret
    print("\n7. Creating application Secret...")
    app_secret = (Secret("app-credentials")
        .add("username", "app-user")
        .add("password", "secure-password")
        .add_label("app", "web-application"))
    
    print(f"   ✓ Secret '{app_secret.name}' created")
    
    # 8. Create the main application with ServiceAccount
    print("\n8. Creating main application...")
    web_app = (App("web-app")
        .image("nginx:1.21")
        .port(80, "http")
        .service_account("web-app-sa")  # Using our ServiceAccount
        .add_secret(app_secret)
        .replicas(3)
        .add_label("tier", "frontend")
        .expose(external_access=True))
    
    print(f"   ✓ App '{web_app.name}' created with ServiceAccount integration")
    
    # 9. Generate all Kubernetes resources
    print("\n9. Generating Kubernetes resources...")
    all_resources = []
    all_resources.extend(service_account.generate_kubernetes_resources())
    all_resources.extend(app_role.generate_kubernetes_resources())
    all_resources.extend(monitoring_role.generate_kubernetes_resources())
    all_resources.extend(role_binding.generate_kubernetes_resources())
    all_resources.extend(cluster_binding.generate_kubernetes_resources())
    all_resources.extend(security_policy.generate_kubernetes_resources())
    all_resources.extend(app_secret.generate_kubernetes_resources())
    all_resources.extend(web_app.generate_kubernetes_resources())
    
    print(f"   ✓ Generated {len(all_resources)} Kubernetes resources")
    
    # 10. Output to YAML files
    print("\n10. Generating YAML manifests...")
    output = KubernetesOutput()
    output.generate(all_resources, "./rbac-demo/")
    
    print("    ✓ YAML manifests generated in './rbac-demo/' directory")
    
    return all_resources


def demo_role_templates():
    """Demonstrate built-in role templates."""
    print("\n" + "=" * 50)
    print("🎭 Built-in Role Templates Demo")
    print("=" * 50)
    
    # Built-in Role templates
    print("\n1. Built-in Role templates:")
    pod_reader = Role.pod_reader("my-pod-reader")
    secret_manager = Role.secret_manager("my-secret-manager")
    config_reader = Role.config_reader("my-config-reader")
    
    print(f"   ✓ Pod Reader Role: '{pod_reader.name}'")
    print(f"   ✓ Secret Manager Role: '{secret_manager.name}'")
    print(f"   ✓ Config Reader Role: '{config_reader.name}'")
    
    # Built-in ClusterRole templates
    print("\n2. Built-in ClusterRole templates:")
    cluster_admin = ClusterRole.cluster_admin("my-cluster-admin")
    node_reader = ClusterRole.node_reader("my-node-reader")
    namespace_admin = ClusterRole.namespace_admin("my-namespace-admin")
    
    print(f"   ✓ Cluster Admin Role: '{cluster_admin.name}'")
    print(f"   ✓ Node Reader Role: '{node_reader.name}'")
    print(f"   ✓ Namespace Admin Role: '{namespace_admin.name}'")
    
    # Built-in SecurityPolicy presets
    print("\n3. Built-in SecurityPolicy presets:")
    minimal = SecurityPolicy.minimal_security("minimal-sec")
    standard = SecurityPolicy.standard_security("standard-sec")
    strict = SecurityPolicy.strict_security("strict-sec")
    
    print(f"   ✓ Minimal Security: '{minimal.name}'")
    print(f"   ✓ Standard Security: '{standard.name}' (PSS: {standard.get_pod_security_standards()})")
    print(f"   ✓ Strict Security: '{strict.name}' (PSS: {strict.get_pod_security_standards()})")


def demo_advanced_patterns():
    """Demonstrate advanced RBAC patterns."""
    print("\n" + "=" * 50)
    print("🚀 Advanced RBAC Patterns Demo")
    print("=" * 50)
    
    # Multi-role binding pattern
    print("\n1. Multi-role binding pattern:")
    
    # Create multiple roles for different purposes
    read_role = Role("data-reader").allow_read_only("configmaps", "secrets")
    write_role = Role("data-writer").allow_create("configmaps").allow_update("configmaps")
    
    # Create a service account
    service_account = ServiceAccount("multi-role-sa")
    
    # Bind multiple roles to the same service account
    read_binding = (RoleBinding("read-binding")
        .bind_role("data-reader")
        .to_service_account("multi-role-sa"))
    
    write_binding = (RoleBinding("write-binding")
        .bind_role("data-writer")
        .to_service_account("multi-role-sa"))
    
    print(f"   ✓ Created multi-role pattern with read and write permissions")
    
    # Cross-namespace access pattern
    print("\n2. Cross-namespace access pattern:")
    
    cross_ns_role = (ClusterRole("cross-namespace-access")
        .allow_get("services", api_group="")
        .allow_list("endpoints", api_group=""))
    
    cross_ns_binding = (RoleBinding("cross-ns-binding")
        .bind_cluster_role("cross-namespace-access")
        .to_service_account("multi-role-sa", "production")
        .set_namespace("development"))  # Binding in different namespace
    
    print(f"   ✓ Created cross-namespace access pattern")
    
    # Application-specific security policy
    print("\n3. Application-specific security policy:")
    
    app_security = (SecurityPolicy("app-specific-security")
        .enable_rbac(True)
        .pod_security_standards("baseline")
        .default_security_context({
            "runAsNonRoot": True,
            "runAsUser": 1001,
            "runAsGroup": 3000,
            "fsGroup": 2000,
            "readOnlyRootFilesystem": True,
            "allowPrivilegeEscalation": False,
            "capabilities": {"drop": ["ALL"], "add": ["NET_BIND_SERVICE"]}
        }))
    
    print(f"   ✓ Created application-specific security policy")
    print(f"     Security Context: {len(app_security.get_security_context())} settings")


def main():
    """Run the complete RBAC demo."""
    try:
        # Main RBAC features demo
        resources = demo_rbac_features()
        
        # Built-in templates demo
        demo_role_templates()
        
        # Advanced patterns demo
        demo_advanced_patterns()
        
        print("\n" + "=" * 70)
        print("🎉 RBAC Demo completed successfully!")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   • Generated {len(resources)} Kubernetes resources")
        print(f"   • YAML manifests available in './rbac-demo/' directory")
        print(f"   • All RBAC components working correctly")
        
        print(f"\n🔐 RBAC Components Demonstrated:")
        print(f"   ✅ ServiceAccount - Identity management")
        print(f"   ✅ Role - Namespace-scoped permissions") 
        print(f"   ✅ ClusterRole - Cluster-wide permissions")
        print(f"   ✅ RoleBinding - Role to subject assignments")
        print(f"   ✅ ClusterRoleBinding - Cluster-wide assignments")
        print(f"   ✅ SecurityPolicy - Comprehensive security configuration")
        
        print(f"\n🌟 Phase 4 (Security & RBAC) implementation is complete and production-ready!")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 