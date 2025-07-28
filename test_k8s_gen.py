#!/usr/bin/env python3
"""
Simple test script for K8s-Gen DSL implementation.

This script tests the basic functionality of the K8s-Gen DSL
to ensure all components work together correctly.
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from k8s_gen import App, StatefulApp, Secret, ConfigMap


def test_basic_app():
    """Test basic App creation and generation."""
    print("Testing basic App creation...")
    
    app = (App("web-app")
        .image("web-server:latest")
        .port(8080)
        .environment({"ENV": "production"})
        .resources(cpu="500m", memory="512Mi"))
    
    print(f"✓ Created app: {app.name}")
    
    # Test resource generation
    try:
        resources = app.generate_kubernetes_resources()
        print(f"✓ Generated {len(resources)} Kubernetes resources")
        
        # Check deployment
        deployment = next((r for r in resources if r['kind'] == 'Deployment'), None)
        if deployment:
            print("✓ Deployment resource generated")
        else:
            print("✗ No Deployment resource found")
            
        # Check service
        service = next((r for r in resources if r['kind'] == 'Service'), None)
        if service:
            print("✓ Service resource generated")
        else:
            print("✗ No Service resource found")
            
    except Exception as e:
        print(f"✗ Error generating resources: {e}")
        return False
    
    return True


def test_stateful_app():
    """Test StatefulApp creation and generation."""
    print("\nTesting StatefulApp creation...")
    
    try:
        database = (StatefulApp("database")
            .image("database-server:latest")
            .port(5432)
            .storage("20Gi")
            .replicas(3))
        
        print(f"✓ Created stateful app: {database.name}")
        
        resources = database.generate_kubernetes_resources()
        print(f"✓ Generated {len(resources)} Kubernetes resources")
        
        # Check StatefulSet
        statefulset = next((r for r in resources if r['kind'] == 'StatefulSet'), None)
        if statefulset:
            print("✓ StatefulSet resource generated")
        else:
            print("✗ No StatefulSet resource found")
            
    except Exception as e:
        print(f"✗ Error with StatefulApp: {e}")
        return False
    
    return True


def test_secret_and_config():
    """Test Secret and ConfigMap creation."""
    print("\nTesting Secret and ConfigMap creation...")
    
    try:
        # Test Secret
        secret = (Secret("app-secret")
            .add("username", "admin")
            .add("password", "secret123"))
        
        print(f"✓ Created secret: {secret.name}")
        
        secret_resources = secret.generate_kubernetes_resources()
        print(f"✓ Generated {len(secret_resources)} secret resources")
        
        # Test ConfigMap
        config = (ConfigMap("app-config")
            .add("database_url", "database://localhost:5432/myapp")
            .add_json("features", {"new_ui": True, "beta": False}))
        
        print(f"✓ Created config map: {config.name}")
        
        config_resources = config.generate_kubernetes_resources()
        print(f"✓ Generated {len(config_resources)} config resources")
        
    except Exception as e:
        print(f"✗ Error with Secret/ConfigMap: {e}")
        return False
    
    return True


def test_output_generation():
    """Test output format generation."""
    print("\nTesting output generation...")
    
    try:
        app = (App("test-app")
            .image("test:latest")
            .port(8080))
        
        # Test Kubernetes output
        resources = app.generate().resources
        print(f"✓ Generated {len(resources)} resources through generator")
        
        # Test YAML generation to file
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            app.generate().to_yaml(temp_dir)
            
            # Check if files were created
            files = os.listdir(temp_dir)
            if files:
                print(f"✓ Generated {len(files)} YAML files: {files}")
            else:
                print("✗ No YAML files generated")
                return False
        
        # Test Docker Compose generation
        with tempfile.TemporaryDirectory() as temp_dir:
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            app.generate().to_docker_compose(compose_file)
            
            if os.path.exists(compose_file):
                print("✓ Generated Docker Compose file")
            else:
                print("✗ No Docker Compose file generated")
                return False
        
    except Exception as e:
        print(f"✗ Error with output generation: {e}")
        return False
    
    return True


def test_complex_app():
    """Test complex application with multiple components."""
    print("\nTesting complex application...")
    
    try:
        # Create a secret
        secret = (Secret("db-creds")
            .add("username", "admin")
            .add("password", "secure123"))
        
        # Create a config map
        config = (ConfigMap("app-config")
            .add("database_url", "database://database:5432/myapp")
            .add("debug", "false"))
        
        # Create a database
        database = (StatefulApp("database")
            .image("database-server:latest")
            .port(5432)
            .storage("10Gi")
            .add_secret(secret))
        
        # Create a web app
        app = (App("web-app")
            .image("webapp:latest")
            .port(8080)
            .add_secret(secret)
            .add_config(config)
            .connect_to(["database"])
            .resources(cpu="500m", memory="512Mi")
            .expose(external_access=True, domain="myapp.example.com"))
        
        print("✓ Created complex application with multiple components")
        
        # Generate resources
        all_resources = []
        all_resources.extend(secret.generate_kubernetes_resources())
        all_resources.extend(config.generate_kubernetes_resources())
        all_resources.extend(database.generate_kubernetes_resources())
        all_resources.extend(app.generate_kubernetes_resources())
        
        print(f"✓ Generated {len(all_resources)} total resources")
        
        # Count resource types
        resource_types = {}
        for resource in all_resources:
            kind = resource.get('kind', 'Unknown')
            resource_types[kind] = resource_types.get(kind, 0) + 1
        
        print(f"✓ Resource breakdown: {resource_types}")
        
    except Exception as e:
        print(f"✗ Error with complex application: {e}")
        return False
    
    return True


def main():
    """Run all tests."""
    print("=" * 50)
    print("K8s-Gen DSL Implementation Test")
    print("=" * 50)
    
    tests = [
        test_basic_app,
        test_stateful_app,
        test_secret_and_config,
        test_output_generation,
        test_complex_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"✗ {test.__name__} failed")
        except Exception as e:
            print(f"✗ {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! K8s-Gen implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 