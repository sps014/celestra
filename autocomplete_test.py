"""
Autocomplete Test for K8s-Gen DSL

This file demonstrates the proper type hints and autocomplete functionality.
After our fixes, you should see autocomplete working for the .generate() chain.
"""

from src.k8s_gen import App, ResourceGenerator

def test_autocomplete():
    """Test function to verify autocomplete works properly."""
    
    # Create an app instance
    app = App("test-app")
    
    # Configure the app with method chaining
    configured_app = (app
        .image("nginx:latest")
        .port(80)
        .replicas(3)
        .expose())
    
    # Generate resources - this should show autocomplete for ResourceGenerator methods
    generator: ResourceGenerator = configured_app.generate()
    
    # Test basic output methods that should work:
    generator.to_yaml("./k8s/")
    generator.to_docker_compose("./docker-compose.yml")
    
    # You can also chain them:
    (configured_app
        .generate()
        .to_yaml("./k8s/")
        .to_docker_compose("./docker-compose.yml"))
    
    # Test validation and scanning methods:
    errors = generator.validate()
    if errors:
        print(f"⚠️  Validation errors: {errors}")
    else:
        print("✅ Validation passed!")
    
    print("✅ Autocomplete test completed!")
    print("📋 Generated files:")
    print("   - Kubernetes YAML files in ./k8s/")
    print("   - Docker Compose file: ./docker-compose.yml")

if __name__ == "__main__":
    test_autocomplete() 