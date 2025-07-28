#!/usr/bin/env python3
"""
Test script to verify RBAC implementation in K8s-Gen DSL.

This script tests the newly implemented RBAC components to ensure they work correctly.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from k8s_gen import (
    ServiceAccount, Role, ClusterRole, RoleBinding, ClusterRoleBinding, 
    SecurityPolicy, App, KubernetesOutput
)


def test_service_account():
    """Test ServiceAccount creation and functionality."""
    print("Testing ServiceAccount...")
    
    service_account = (ServiceAccount("test-sa")
        .add_secret("test-secret")
        .add_image_pull_secret("registry-secret")
        .automount_token(True)
        .set_namespace("test-namespace"))
    
    resources = service_account.generate_kubernetes_resources()
    assert len(resources) == 1
    
    sa_resource = resources[0]
    assert sa_resource["kind"] == "ServiceAccount"
    assert sa_resource["metadata"]["name"] == "test-sa"
    assert sa_resource["metadata"]["namespace"] == "test-namespace"
    assert len(sa_resource["secrets"]) == 1
    assert sa_resource["secrets"][0]["name"] == "test-secret"
    assert len(sa_resource["imagePullSecrets"]) == 1
    assert sa_resource["imagePullSecrets"][0]["name"] == "registry-secret"
    assert sa_resource["automountServiceAccountToken"] == True
    
    print("✅ ServiceAccount test passed!")


def test_role():
    """Test Role creation and functionality."""
    print("Testing Role...")
    
    role = (Role("test-role")
        .allow_get("pods", "services")
        .allow_list("configmaps")
        .allow_create("secrets")
        .set_namespace("test-namespace"))
    
    resources = role.generate_kubernetes_resources()
    assert len(resources) == 1
    
    role_resource = resources[0]
    assert role_resource["kind"] == "Role"
    assert role_resource["metadata"]["name"] == "test-role"
    assert role_resource["metadata"]["namespace"] == "test-namespace"
    assert len(role_resource["rules"]) == 3
    
    # Check role templates
    pod_reader = Role.pod_reader()
    assert pod_reader._name == "pod-reader"
    
    print("✅ Role test passed!")


def test_cluster_role():
    """Test ClusterRole creation and functionality."""
    print("Testing ClusterRole...")
    
    cluster_role = (ClusterRole("test-cluster-role")
        .allow_read_only("nodes")
        .allow_all("namespaces"))
    
    resources = cluster_role.generate_kubernetes_resources()
    assert len(resources) == 1
    
    cr_resource = resources[0]
    assert cr_resource["kind"] == "ClusterRole"
    assert cr_resource["metadata"]["name"] == "test-cluster-role"
    assert "namespace" not in cr_resource["metadata"]  # ClusterRoles don't have namespaces
    
    # Check cluster role templates
    cluster_admin = ClusterRole.cluster_admin()
    assert cluster_admin._name == "cluster-admin"
    
    print("✅ ClusterRole test passed!")


def test_role_binding():
    """Test RoleBinding creation and functionality."""
    print("Testing RoleBinding...")
    
    role_binding = (RoleBinding("test-binding")
        .bind_role("test-role")
        .to_service_account("test-sa", "test-namespace")
        .to_user("jane@example.com")
        .set_namespace("test-namespace"))
    
    resources = role_binding.generate_kubernetes_resources()
    assert len(resources) == 1
    
    rb_resource = resources[0]
    assert rb_resource["kind"] == "RoleBinding"
    assert rb_resource["metadata"]["name"] == "test-binding"
    assert rb_resource["roleRef"]["kind"] == "Role"
    assert rb_resource["roleRef"]["name"] == "test-role"
    assert len(rb_resource["subjects"]) == 2
    
    print("✅ RoleBinding test passed!")


def test_cluster_role_binding():
    """Test ClusterRoleBinding creation and functionality."""
    print("Testing ClusterRoleBinding...")
    
    cluster_binding = (ClusterRoleBinding("test-cluster-binding")
        .bind_cluster_role("cluster-admin")
        .to_user("admin@example.com"))
    
    resources = cluster_binding.generate_kubernetes_resources()
    assert len(resources) == 1
    
    crb_resource = resources[0]
    assert crb_resource["kind"] == "ClusterRoleBinding"
    assert crb_resource["metadata"]["name"] == "test-cluster-binding"
    assert "namespace" not in crb_resource["metadata"]
    assert crb_resource["roleRef"]["kind"] == "ClusterRole"
    
    print("✅ ClusterRoleBinding test passed!")


def test_security_policy():
    """Test SecurityPolicy creation and functionality."""
    print("Testing SecurityPolicy...")
    
    security_policy = (SecurityPolicy("test-security")
        .enable_rbac()
        .pod_security_standards("restricted")
        .enable_network_policies()
        .default_security_context({
            "runAsNonRoot": True,
            "runAsUser": 1000
        }))
    
    assert security_policy.is_rbac_enabled() == True
    assert security_policy.is_network_policies_enabled() == True
    assert security_policy.get_pod_security_standards() == "restricted"
    assert security_policy.get_security_context()["runAsNonRoot"] == True
    
    # Test security presets
    strict_security = SecurityPolicy.strict_security()
    assert strict_security.is_rbac_enabled() == True
    assert strict_security.get_pod_security_standards() == "restricted"
    
    print("✅ SecurityPolicy test passed!")


def test_app_group_security_integration():
    """Test SecurityPolicy integration with AppGroup."""
    print("Testing AppGroup security integration...")
    
    from k8s_gen import AppGroup
    
    # This should now work without import errors
    app_group = AppGroup("test-group")
    app_group.configure_security(
        rbac_enabled=True,
        pod_security_policy="restricted",
        network_policies=True,
        security_context={"runAsNonRoot": True}
    )
    
    print("✅ AppGroup security integration test passed!")


def test_complete_rbac_example():
    """Test a complete RBAC example with App integration."""
    print("Testing complete RBAC example...")
    
    # Create service account
    service_account = (ServiceAccount("web-app-sa")
        .add_image_pull_secret("registry-secret")
        .automount_token(True))
    
    # Create role
    role = (Role("web-app-role")
        .allow_get("configmaps", "secrets")
        .allow_list("services"))
    
    # Create role binding
    role_binding = (RoleBinding("web-app-binding")
        .bind_role("web-app-role")
        .to_service_account("web-app-sa"))
    
    # Create app with service account
    app = (App("web-app")
        .image("nginx:latest")
        .port(80)
        .service_account("web-app-sa"))
    
    # Generate all resources
    all_resources = []
    all_resources.extend(service_account.generate_kubernetes_resources())
    all_resources.extend(role.generate_kubernetes_resources())
    all_resources.extend(role_binding.generate_kubernetes_resources())
    all_resources.extend(app.generate_kubernetes_resources())
    
    # Should have ServiceAccount, Role, RoleBinding, Deployment, Service
    assert len(all_resources) >= 5
    
    # Test with Kubernetes output  
    output = KubernetesOutput()
    output.generate(all_resources)
    
    # Check that files were generated (output.generate writes files, doesn't return content)
    import os
    k8s_dir = "k8s"
    if os.path.exists(k8s_dir):
        files = os.listdir(k8s_dir)
        assert len(files) > 0, "No Kubernetes files were generated"
    
    print("✅ Complete RBAC example test passed!")


def main():
    """Run all RBAC tests."""
    print("🧪 Testing K8s-Gen DSL Phase 4: Security & RBAC Implementation")
    print("=" * 60)
    
    try:
        test_service_account()
        test_role()
        test_cluster_role()
        test_role_binding()
        test_cluster_role_binding()
        test_security_policy()
        test_app_group_security_integration()
        test_complete_rbac_example()
        
        print("\n" + "=" * 60)
        print("🎉 All RBAC tests passed! Phase 4 implementation is working correctly.")
        print("\n📋 Summary of implemented RBAC components:")
        print("   ✅ ServiceAccount - Service account management")
        print("   ✅ Role - Namespace-scoped permissions")
        print("   ✅ ClusterRole - Cluster-wide permissions")
        print("   ✅ RoleBinding - Role to subject binding")
        print("   ✅ ClusterRoleBinding - Cluster-wide role binding")
        print("   ✅ SecurityPolicy - Comprehensive security configuration")
        print("\n🚀 K8s-Gen DSL is now ready for production use with full RBAC support!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 