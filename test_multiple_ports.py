#!/usr/bin/env python3
"""
Test script for Multiple Ports functionality in K8s-Gen DSL.

This script demonstrates the enhanced multiple ports support for App and StatefulApp
classes, including convenience methods for common port patterns.
"""

from src.k8s_gen import (
    App, StatefulApp, Service, KubernetesOutput
)

def test_app_multiple_ports():
    """Test multiple ports functionality for App class."""
    print("🔗 Testing App Multiple Ports...")
    
    # Test 1: Basic multiple ports using individual port() calls
    basic_app = (App("api-service")
        .image("api-server:2.1.0")
        .port(8080, "http")
        .port(9090, "metrics")
        .port(8081, "health")
        .port(9000, "admin")
        .env("LOG_LEVEL", "info")
        .resources(cpu="500m", memory="1Gi")
        .replicas(3))
    
    # Test 2: Using convenience methods
    convenience_app = (App("web-service")
        .image("web-server:1.5.0")
        .http_port(8080)
        .https_port(8443)
        .metrics_port(9090)
        .health_port(8081)
        .admin_port(9000)
        .grpc_port(9091)
        .debug_port(5005)
        .env("ENVIRONMENT", "production")
        .resources(cpu="300m", memory="512Mi")
        .replicas(2))
    
    # Test 3: Using ports() method for bulk addition
    bulk_app = (App("microservice")
        .image("microservice:3.0.0")
        .ports([
            {"port": 8080, "name": "http"},
            {"port": 8443, "name": "https"},
            {"port": 9090, "name": "metrics"},
            {"port": 8081, "name": "health"},
            {"port": 9000, "name": "admin"},
            {"port": 9091, "name": "grpc"},
            {"port": 50051, "name": "grpc-internal", "protocol": "TCP"}
        ])
        .env("SERVICE_NAME", "microservice")
        .resources(cpu="1", memory="2Gi")
        .replicas(5))
    
    # Test 4: Using common_ports() convenience method
    common_app = (App("standard-service")
        .image("standard-app:1.0.0")
        .common_ports(http=8080, metrics=9090, health=8081)
        .env("PRESET", "standard")
        .replicas(3))
    
    # Test 5: Mixed approach
    mixed_app = (App("complex-service")
        .image("complex-app:2.5.0")
        .common_ports()  # Use defaults
        .grpc_port(9091)
        .admin_port(9000)
        .add_port(8082, "websocket")
        .port(1883, "mqtt", "TCP")
        .replicas(4))
    
    apps = [basic_app, convenience_app, bulk_app, common_app, mixed_app]
    
    # Generate Kubernetes resources
    total_ports = 0
    for i, app in enumerate(apps, 1):
        k8s_resources = app.generate_kubernetes_resources()
        deployment = next(r for r in k8s_resources if r["kind"] == "Deployment")
        container_ports = deployment["spec"]["template"]["spec"]["containers"][0].get("ports", [])
        
        print(f"  App {i} ({app._name}): {len(container_ports)} ports")
        for port in container_ports:
            print(f"    - {port['name']}: {port['containerPort']}/{port['protocol']}")
        
        total_ports += len(container_ports)
    
    print(f"  ✅ Total ports across all apps: {total_ports}")
    return apps, total_ports


def test_stateful_app_multiple_ports():
    """Test multiple ports functionality for StatefulApp class."""
    print("\n💾 Testing StatefulApp Multiple Ports...")
    
    # Test 1: Database with multiple ports
    postgres_db = (StatefulApp("postgres-cluster")
        .image("postgres:14.5")
        .postgres_port(5432)
        .metrics_port(9187)
        .admin_port(8080)
        .cluster_port(5433)
        .env("POSTGRES_DB", "myapp")
        .storage("/var/lib/postgresql/data", "100Gi")
        .resources(cpu="2", memory="8Gi")
        .replicas(3))
    
    # Test 2: Redis with custom ports
    redis_cluster = (StatefulApp("redis-cluster")
        .image("redis:7.0.5")
        .redis_port(6379)
        .add_port(16379, "cluster")
        .metrics_port(9121)
        .admin_port(8080)
        .storage("/data", "50Gi")
        .resources(cpu="1", memory="4Gi")
        .replicas(6))
    
    # Test 3: Elasticsearch with all ports
    elasticsearch = (StatefulApp("elasticsearch-cluster")
        .image("elasticsearch:8.5.0")
        .elasticsearch_port(9200)
        .add_port(9300, "transport")
        .metrics_port(9114)
        .admin_port(8080)
        .storage("/usr/share/elasticsearch/data", "200Gi")
        .resources(cpu="2", memory="16Gi")
        .replicas(3))
    
    # Test 4: MongoDB with ports() method
    mongodb = (StatefulApp("mongodb-replica")
        .image("mongo:6.0")
        .ports([
            {"port": 27017, "name": "mongodb"},
            {"port": 28017, "name": "web"},
            {"port": 9216, "name": "metrics"},
            {"port": 8080, "name": "admin"}
        ])
        .storage("/data/db", "100Gi")
        .resources(cpu="1", memory="4Gi")
        .replicas(3))
    
    # Test 5: Kafka with multiple protocols
    kafka = (StatefulApp("kafka-cluster")
        .image("kafka:3.3.0")
        .kafka_port(9092)
        .add_port(9093, "internal")
        .add_port(9094, "external")
        .metrics_port(9308)
        .admin_port(8080)
        .storage("/kafka/logs", "500Gi")
        .resources(cpu="2", memory="8Gi")
        .replicas(3))
    
    stateful_apps = [postgres_db, redis_cluster, elasticsearch, mongodb, kafka]
    
    # Generate Kubernetes resources
    total_ports = 0
    for i, app in enumerate(stateful_apps, 1):
        k8s_resources = app.generate_kubernetes_resources()
        statefulset = next(r for r in k8s_resources if r["kind"] == "StatefulSet")
        container_ports = statefulset["spec"]["template"]["spec"]["containers"][0].get("ports", [])
        
        print(f"  StatefulApp {i} ({app._name}): {len(container_ports)} ports")
        for port in container_ports:
            print(f"    - {port['name']}: {port['containerPort']}/{port['protocol']}")
        
        total_ports += len(container_ports)
    
    print(f"  ✅ Total ports across all stateful apps: {total_ports}")
    return stateful_apps, total_ports


def test_service_integration():
    """Test how multiple ports integrate with Service creation."""
    print("\n🌐 Testing Service Integration with Multiple Ports...")
    
    # Create app with multiple ports
    multi_port_app = (App("full-stack-app")
        .image("fullstack:2.0.0")
        .http_port(8080)
        .https_port(8443)
        .grpc_port(9090)
        .metrics_port(9091)
        .health_port(8081)
        .admin_port(9000)
        .debug_port(5005)
        .replicas(3))
    
    # Create corresponding service with all ports
    app_service = (Service("full-stack-service")
        .selector({"app": "full-stack-app"})
        .add_port("http", 80, 8080)
        .add_port("https", 443, 8443)
        .add_port("grpc", 9090, 9090)
        .add_port("metrics", 9091, 9091)
        .add_port("health", 8081, 8081)
        .add_port("admin", 9000, 9000))
    
    # Generate resources
    app_resources = multi_port_app.generate_kubernetes_resources()
    service_resources = app_service.generate_kubernetes_resources()
    
    deployment = next(r for r in app_resources if r["kind"] == "Deployment")
    service = service_resources[0]
    
    container_ports = deployment["spec"]["template"]["spec"]["containers"][0].get("ports", [])
    service_ports = service["spec"]["ports"]
    
    print(f"  App container ports: {len(container_ports)}")
    print(f"  Service ports: {len(service_ports)}")
    
    # Verify port mapping
    port_mappings = []
    for service_port in service_ports:
        target_port = service_port["targetPort"]
        container_port = next((cp for cp in container_ports if cp["containerPort"] == target_port), None)
        if container_port:
            port_mappings.append({
                "service_port": service_port["port"],
                "target_port": target_port,
                "container_name": container_port["name"]
            })
    
    print(f"  ✅ Successfully mapped {len(port_mappings)} ports")
    for mapping in port_mappings:
        print(f"    Service :{mapping['service_port']} -> Container :{mapping['target_port']} ({mapping['container_name']})")
    
    return len(port_mappings)


def test_real_world_scenarios():
    """Test real-world microservices scenarios with multiple ports."""
    print("\n🏗️ Testing Real-World Scenarios...")
    
    # Scenario 1: Complete microservices platform
    scenarios = []
    
    # API Gateway
    api_gateway = (App("api-gateway")
        .image("nginx:1.23")
        .http_port(8080, "gateway")
        .https_port(8443, "gateway-tls")
        .metrics_port(9113, "nginx-metrics")
        .health_port(8081, "nginx-health")
        .admin_port(8082, "nginx-admin")
        .replicas(2))
    
    # Authentication Service
    auth_service = (App("auth-service")
        .image("auth-server:3.0.0")
        .http_port(8080, "auth-api")
        .grpc_port(9090, "auth-grpc")
        .metrics_port(9091, "auth-metrics")
        .health_port(8081, "auth-health")
        .debug_port(5005, "auth-debug")
        .replicas(3))
    
    # User Service
    user_service = (App("user-service")
        .image("user-mgmt:2.5.0")
        .common_ports()
        .grpc_port(9090)
        .admin_port(9000)
        .replicas(2))
    
    # Database Cluster
    postgres_cluster = (StatefulApp("postgres-primary")
        .image("postgres:14.5")
        .postgres_port(5432)
        .metrics_port(9187, "postgres-exporter")
        .admin_port(8080, "pgadmin")
        .cluster_port(5433, "replication")
        .storage("/var/lib/postgresql/data", "200Gi")
        .replicas(1))
    
    # Cache Cluster
    redis_cluster = (StatefulApp("redis-cluster")
        .image("redis:7.0.5")
        .redis_port(6379)
        .add_port(16379, "cluster-bus")
        .metrics_port(9121, "redis-exporter")
        .storage("/data", "50Gi")
        .replicas(6))
    
    # Message Queue
    kafka_cluster = (StatefulApp("kafka-cluster")
        .image("kafka:3.3.0")
        .kafka_port(9092, "kafka")
        .add_port(9093, "kafka-internal")
        .add_port(9094, "kafka-external")
        .metrics_port(9308, "kafka-exporter")
        .admin_port(8080, "kafka-ui")
        .storage("/kafka/logs", "1Ti")
        .replicas(3))
    
    # Search Engine
    elasticsearch = (StatefulApp("elasticsearch")
        .image("elasticsearch:8.5.0")
        .elasticsearch_port(9200, "http")
        .add_port(9300, "transport")
        .metrics_port(9114, "es-exporter")
        .storage("/usr/share/elasticsearch/data", "500Gi")
        .replicas(3))
    
    scenarios = [
        api_gateway, auth_service, user_service,
        postgres_cluster, redis_cluster, kafka_cluster, elasticsearch
    ]
    
    total_components = len(scenarios)
    total_ports = 0
    
    for component in scenarios:
        k8s_resources = component.generate_kubernetes_resources()
        workload = next(r for r in k8s_resources if r["kind"] in ["Deployment", "StatefulSet"])
        container_ports = workload["spec"]["template"]["spec"]["containers"][0].get("ports", [])
        total_ports += len(container_ports)
    
    print(f"  ✅ Platform components: {total_components}")
    print(f"  ✅ Total ports configured: {total_ports}")
    print(f"  ✅ Average ports per component: {total_ports / total_components:.1f}")
    
    return scenarios, total_components, total_ports


def generate_output_files():
    """Generate complete Kubernetes manifests to files."""
    print("\n📄 Generating Output Files...")
    
    # Create comprehensive example
    components = []
    
    # Multi-port apps
    api_app = (App("api-server")
        .image("api:2.0.0")
        .common_ports()
        .grpc_port(9090)
        .admin_port(9000)
        .replicas(3))
    
    # Multi-port stateful app
    database = (StatefulApp("postgres-db")
        .image("postgres:14.5")
        .postgres_port(5432)
        .metrics_port(9187)
        .admin_port(8080)
        .storage("/var/lib/postgresql/data", "100Gi"))
    
    components = [api_app, database]
    
    # Generate all resources
    all_resources = []
    for component in components:
        all_resources.extend(component.generate_kubernetes_resources())
    
    # Write to files using KubernetesOutput
    output = KubernetesOutput()
    
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write individual files
        for i, resource in enumerate(all_resources):
            kind = resource.get("kind", "resource").lower()
            name = resource.get("metadata", {}).get("name", f"resource-{i}")
            filename = f"{kind}-{name}.yaml"
            
            import yaml
            with open(os.path.join(temp_dir, filename), 'w') as f:
                f.write(yaml.dump(resource, default_flow_style=False))
        
        files_created = len(os.listdir(temp_dir))
        print(f"  ✅ Generated {files_created} YAML files")
        print(f"  📁 Files location: {temp_dir}")
        
        # Show sample content
        sample_file = os.listdir(temp_dir)[0]
        with open(os.path.join(temp_dir, sample_file), 'r') as f:
            content = f.read()[:500]  # First 500 chars
            print(f"  📄 Sample content from {sample_file}:")
            print("  " + content.replace('\n', '\n  '))
    
    return files_created


def main():
    """Run all multiple ports tests."""
    print("🔗 K8s-Gen DSL Multiple Ports Test Suite")
    print("=" * 60)
    print("🎯 Testing Enhanced Multiple Ports Support")
    print("=" * 60)
    
    try:
        # Test App multiple ports
        apps, app_ports = test_app_multiple_ports()
        
        # Test StatefulApp multiple ports
        stateful_apps, stateful_ports = test_stateful_app_multiple_ports()
        
        # Test Service integration
        service_mappings = test_service_integration()
        
        # Test real-world scenarios
        scenarios, components, scenario_ports = test_real_world_scenarios()
        
        # Generate output files
        files_generated = generate_output_files()
        
        # Final Summary
        print("\n🎉 MULTIPLE PORTS TEST SUMMARY")
        print("=" * 60)
        print(f"✅ All multiple ports tests completed successfully!")
        
        print(f"\n📊 TEST RESULTS:")
        print(f"  🔗 App Components: {len(apps)} apps with {app_ports} total ports")
        print(f"  💾 StatefulApp Components: {len(stateful_apps)} apps with {stateful_ports} total ports")
        print(f"  🌐 Service Integration: {service_mappings} port mappings verified")
        print(f"  🏗️ Real-world Platform: {components} components with {scenario_ports} total ports")
        print(f"  📄 Output Files: {files_generated} YAML files generated")
        
        total_ports = app_ports + stateful_ports + scenario_ports
        total_components = len(apps) + len(stateful_apps) + components
        
        print(f"\n🔍 OVERALL STATISTICS:")
        print(f"  📊 Total Components Tested: {total_components}")
        print(f"  🔗 Total Ports Configured: {total_ports}")
        print(f"  📈 Average Ports per Component: {total_ports / total_components:.1f}")
        
        print(f"\n✨ NEW FEATURES DEMONSTRATED:")
        print(f"  🔧 Enhanced port() and add_port() methods")
        print(f"  📦 Bulk ports() configuration")
        print(f"  🎯 Convenience methods (http_port, postgres_port, etc.)")
        print(f"  🔗 Common port patterns (common_ports)")
        print(f"  🌐 Service integration with multiple ports")
        print(f"  🏗️ Real-world microservices scenarios")
        
        print(f"\n🚀 K8s-Gen DSL: Enhanced Multiple Ports Support Ready!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 