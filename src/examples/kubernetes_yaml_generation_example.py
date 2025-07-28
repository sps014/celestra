#!/usr/bin/env python3
"""
Kubernetes YAML Generation Test for Multiple Ports Support.

This test generates actual Kubernetes YAML files and verifies that 
multiple ports are correctly included in all supported components.
"""

import os
import yaml
from ..celestra import (
    App, StatefulApp, Job, CronJob, Service, 
    KubernetesOutput
)

def test_app_ports_in_yaml():
    """Test App multiple ports in generated Kubernetes YAML."""
    print("🔗 Testing App Multiple Ports in Kubernetes YAML...")
    
    # Create App with multiple ports using different methods
    app = (App("test-app")
        .image("test-app:1.0.0")
        .http_port(8080, "main-api")
        .https_port(8443, "secure-api")
        .metrics_port(9090, "prometheus")
        .health_port(8081, "health-check")
        .admin_port(9000, "admin-ui")
        .grpc_port(9091, "grpc-api")
        .debug_port(5005, "remote-debug")
        .env("LOG_LEVEL", "info")
        .resources(cpu="500m", memory="1Gi")
        .replicas(3))
    
    # Generate Kubernetes resources
    k8s_resources = app.generate_kubernetes_resources()
    deployment = next(r for r in k8s_resources if r["kind"] == "Deployment")
    
    # Extract container ports
    container = deployment["spec"]["template"]["spec"]["containers"][0]
    ports = container.get("ports", [])
    
    print(f"  App '{app._name}' generated {len(ports)} ports:")
    for port in ports:
        print(f"    - {port['name']}: {port['containerPort']}/{port['protocol']}")
    
    # Verify expected ports
    expected_ports = {
        "main-api": 8080,
        "secure-api": 8443,
        "prometheus": 9090,
        "health-check": 8081,
        "admin-ui": 9000,
        "grpc-api": 9091,
        "remote-debug": 5005
    }
    
    actual_ports = {port['name']: port['containerPort'] for port in ports}
    
    assert len(ports) == 7, f"Expected 7 ports, got {len(ports)}"
    for name, expected_port in expected_ports.items():
        assert name in actual_ports, f"Port '{name}' not found"
        assert actual_ports[name] == expected_port, f"Port '{name}' has wrong number: {actual_ports[name]} != {expected_port}"
    
    print(f"  ✅ All 7 ports correctly configured in Deployment YAML")
    return deployment, ports


def test_stateful_app_ports_in_yaml():
    """Test StatefulApp multiple ports in generated Kubernetes YAML."""
    print("\n💾 Testing StatefulApp Multiple Ports in Kubernetes YAML...")
    
    # Create StatefulApp with database-specific ports
    stateful_app = (StatefulApp("postgres-cluster")
        .image("postgres:15.2")
        .postgres_port(5432, "database")
        .metrics_port(9187, "pg-exporter")
        .admin_port(8080, "pgadmin")
        .cluster_port(5433, "replication")
        .add_port(5434, "backup-stream")
        .add_port(5435, "wal-receiver")
        .env("POSTGRES_DB", "testdb")
        .storage("/var/lib/postgresql/data", "100Gi")
        .resources(cpu="2", memory="8Gi")
        .replicas(3))
    
    # Generate Kubernetes resources
    k8s_resources = stateful_app.generate_kubernetes_resources()
    statefulset = next(r for r in k8s_resources if r["kind"] == "StatefulSet")
    
    # Extract container ports
    container = statefulset["spec"]["template"]["spec"]["containers"][0]
    ports = container.get("ports", [])
    
    print(f"  StatefulApp '{stateful_app._name}' generated {len(ports)} ports:")
    for port in ports:
        print(f"    - {port['name']}: {port['containerPort']}/{port['protocol']}")
    
    # Verify expected ports
    expected_ports = {
        "database": 5432,
        "pg-exporter": 9187,
        "pgadmin": 8080,
        "replication": 5433,
        "backup-stream": 5434,
        "wal-receiver": 5435
    }
    
    actual_ports = {port['name']: port['containerPort'] for port in ports}
    
    assert len(ports) == 6, f"Expected 6 ports, got {len(ports)}"
    for name, expected_port in expected_ports.items():
        assert name in actual_ports, f"Port '{name}' not found"
        assert actual_ports[name] == expected_port, f"Port '{name}' has wrong number: {actual_ports[name]} != {expected_port}"
    
    print(f"  ✅ All 6 ports correctly configured in StatefulSet YAML")
    return statefulset, ports


def test_job_ports_in_yaml():
    """Test Job multiple ports in generated Kubernetes YAML."""
    print("\n📊 Testing Job Multiple Ports in Kubernetes YAML...")
    
    # Create Job with monitoring ports
    job = (Job("data-processor")
        .image("data-processor:2.0.0")
        .command(["python", "process.py"])
        .web_port(8080, "progress-ui")
        .metrics_port(9090, "job-metrics")
        .status_port(8081, "status-api")
        .add_port(8082, "webhook-receiver")
        .env("BATCH_SIZE", "1000")
        .resources(cpu="2", memory="4Gi")
        .parallelism(3)
        .completions(3))
    
    # Generate Kubernetes resources
    k8s_resources = job.generate_kubernetes_resources()
    job_resource = k8s_resources[0]
    
    # Extract container ports
    container = job_resource["spec"]["template"]["spec"]["containers"][0]
    ports = container.get("ports", [])
    
    print(f"  Job '{job._name}' generated {len(ports)} ports:")
    for port in ports:
        print(f"    - {port['name']}: {port['containerPort']}/{port['protocol']}")
    
    # Verify expected ports
    expected_ports = {
        "progress-ui": 8080,
        "job-metrics": 9090,
        "status-api": 8081,
        "webhook-receiver": 8082
    }
    
    actual_ports = {port['name']: port['containerPort'] for port in ports}
    
    assert len(ports) == 4, f"Expected 4 ports, got {len(ports)}"
    for name, expected_port in expected_ports.items():
        assert name in actual_ports, f"Port '{name}' not found"
        assert actual_ports[name] == expected_port, f"Port '{name}' has wrong number: {actual_ports[name]} != {expected_port}"
    
    print(f"  ✅ All 4 ports correctly configured in Job YAML")
    return job_resource, ports


def test_cronjob_ports_in_yaml():
    """Test CronJob multiple ports in generated Kubernetes YAML."""
    print("\n⏰ Testing CronJob Multiple Ports in Kubernetes YAML...")
    
    # Create CronJob with web interface and monitoring
    cronjob = (CronJob("backup-scheduler")
        .schedule("0 2 * * *")  # Daily at 2 AM
        .image("backup-tool:1.5.0")
        .command(["backup.sh"])
        .ports([
            {"port": 8080, "name": "backup-ui"},
            {"port": 9090, "name": "backup-metrics"},
            {"port": 8081, "name": "backup-status"},
            {"port": 8082, "name": "backup-webhook"}
        ])
        .env("BACKUP_TARGET", "s3://backups/")
        .resources(cpu="1", memory="2Gi"))
    
    # Generate Kubernetes resources
    k8s_resources = cronjob.generate_kubernetes_resources()
    cronjob_resource = k8s_resources[0]
    
    # Extract container ports
    container = cronjob_resource["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]
    ports = container.get("ports", [])
    
    print(f"  CronJob '{cronjob._name}' generated {len(ports)} ports:")
    for port in ports:
        print(f"    - {port['name']}: {port['containerPort']}/{port['protocol']}")
    
    # Verify expected ports
    expected_ports = {
        "backup-ui": 8080,
        "backup-metrics": 9090,
        "backup-status": 8081,
        "backup-webhook": 8082
    }
    
    actual_ports = {port['name']: port['containerPort'] for port in ports}
    
    assert len(ports) == 4, f"Expected 4 ports, got {len(ports)}"
    for name, expected_port in expected_ports.items():
        assert name in actual_ports, f"Port '{name}' not found"
        assert actual_ports[name] == expected_port, f"Port '{name}' has wrong number: {actual_ports[name]} != {expected_port}"
    
    print(f"  ✅ All 4 ports correctly configured in CronJob YAML")
    return cronjob_resource, ports


def test_service_port_mapping():
    """Test Service port mapping with multiple ports."""
    print("\n🌐 Testing Service Multiple Port Mapping...")
    
    # Create Service with multiple port mappings
    service = (Service("multi-port-service")
        .selector({"app": "test-app"})
        .add_port("http", 80, 8080)
        .add_port("https", 443, 8443)
        .add_port("metrics", 9090, 9090)
        .add_port("health", 8081, 8081)
        .add_port("admin", 9000, 9000)
        .add_port("grpc", 9091, 9091)
        .type("LoadBalancer"))
    
    # Generate Kubernetes resources
    k8s_resources = service.generate_kubernetes_resources()
    service_resource = k8s_resources[0]
    
    # Extract service ports
    ports = service_resource["spec"]["ports"]
    
    print(f"  Service '{service._name}' generated {len(ports)} port mappings:")
    for port in ports:
        print(f"    - {port['name']}: {port['port']} -> {port['targetPort']}")
    
    # Verify expected port mappings
    expected_mappings = {
        "http": (80, 8080),
        "https": (443, 8443),
        "metrics": (9090, 9090),
        "health": (8081, 8081),
        "admin": (9000, 9000),
        "grpc": (9091, 9091)
    }
    
    actual_mappings = {port['name']: (port['port'], port['targetPort']) for port in ports}
    
    assert len(ports) == 6, f"Expected 6 port mappings, got {len(ports)}"
    for name, (expected_service_port, expected_target_port) in expected_mappings.items():
        assert name in actual_mappings, f"Port mapping '{name}' not found"
        actual_service_port, actual_target_port = actual_mappings[name]
        assert actual_service_port == expected_service_port, f"Service port mismatch for '{name}'"
        assert actual_target_port == expected_target_port, f"Target port mismatch for '{name}'"
    
    print(f"  ✅ All 6 port mappings correctly configured in Service YAML")
    return service_resource, ports


def generate_yaml_files():
    """Generate actual YAML files and verify their contents."""
    print("\n📄 Generating Actual Kubernetes YAML Files...")
    
    # Create components with multiple ports
    components = []
    
    # Multi-port App
    api_app = (App("api-gateway")
        .image("nginx:1.23")
        .common_ports(http=8080, metrics=9113, health=8081)
        .https_port(8443)
        .admin_port(8082)
        .replicas(2))
    components.append(api_app)
    
    # Multi-port StatefulApp
    database = (StatefulApp("postgres-db")
        .image("postgres:15")
        .postgres_port(5432)
        .metrics_port(9187)
        .admin_port(8080)
        .storage("/var/lib/postgresql/data", "100Gi"))
    components.append(database)
    
    # Multi-port Job
    batch_job = (Job("data-migration")
        .image("migrator:1.0")
        .web_port(8080)
        .metrics_port(9090)
        .status_port(8081))
    components.append(batch_job)
    
    # Multi-port CronJob
    backup_job = (CronJob("nightly-backup")
        .schedule("0 1 * * *")
        .image("backup:2.0")
        .web_port(8080)
        .metrics_port(9090))
    components.append(backup_job)
    
    # Multi-port Service
    api_service = (Service("api-gateway-service")
        .selector({"app": "api-gateway"})
        .add_port("http", 80, 8080)
        .add_port("https", 443, 8443)
        .add_port("metrics", 9113, 9113)
        .add_port("health", 8081, 8081))
    components.append(api_service)
    
    # Generate all Kubernetes resources
    all_resources = []
    for component in components:
        all_resources.extend(component.generate_kubernetes_resources())
    
    # Create output directory
    output_dir = "kubernetes_manifests"
    os.makedirs(output_dir, exist_ok=True)
    
    # Write YAML files
    yaml_files = []
    for i, resource in enumerate(all_resources):
        kind = resource.get("kind", "resource").lower()
        name = resource.get("metadata", {}).get("name", f"resource-{i}")
        filename = f"{kind}-{name}.yaml"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(yaml.dump(resource, default_flow_style=False))
        
        yaml_files.append(filepath)
    
    print(f"  ✅ Generated {len(yaml_files)} YAML files in '{output_dir}/' directory")
    
    # Verify ports in generated files
    port_verification = {}
    
    for filepath in yaml_files:
        with open(filepath, 'r') as f:
            resource = yaml.safe_load(f)
        
        kind = resource.get("kind")
        name = resource.get("metadata", {}).get("name")
        
        # Extract ports based on resource type
        ports = []
        if kind == "Deployment":
            container = resource["spec"]["template"]["spec"]["containers"][0]
            ports = container.get("ports", [])
        elif kind == "StatefulSet":
            container = resource["spec"]["template"]["spec"]["containers"][0]
            ports = container.get("ports", [])
        elif kind == "Job":
            container = resource["spec"]["template"]["spec"]["containers"][0]
            ports = container.get("ports", [])
        elif kind == "CronJob":
            container = resource["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]
            ports = container.get("ports", [])
        elif kind == "Service":
            ports = resource["spec"]["ports"]
        
        if ports:
            port_verification[f"{kind}/{name}"] = len(ports)
    
    print(f"\n  📊 Port Verification Summary:")
    total_ports = 0
    for resource_name, port_count in port_verification.items():
        print(f"    {resource_name}: {port_count} ports")
        total_ports += port_count
    
    print(f"  ✅ Total ports across all resources: {total_ports}")
    
    # Show sample YAML content
    sample_file = yaml_files[0]
    print(f"\n  📄 Sample YAML content from {os.path.basename(sample_file)}:")
    with open(sample_file, 'r') as f:
        content = f.read()
        lines = content.split('\n')[:25]  # First 25 lines
        for line in lines:
            print(f"    {line}")
        if len(content.split('\n')) > 25:
            print("    ...")
    
    return yaml_files, port_verification, total_ports


def main():
    """Run comprehensive Kubernetes YAML generation test."""
    print("🧪 Kubernetes YAML Generation Test for Multiple Ports")
    print("=" * 65)
    print("🎯 Verifying Multiple Ports Support in Generated Kubernetes YAML")
    print("=" * 65)
    
    try:
        # Test each component type
        app_deployment, app_ports = test_app_ports_in_yaml()
        stateful_deployment, stateful_ports = test_stateful_app_ports_in_yaml()
        job_resource, job_ports = test_job_ports_in_yaml()
        cronjob_resource, cronjob_ports = test_cronjob_ports_in_yaml()
        service_resource, service_ports = test_service_port_mapping()
        
        # Generate actual YAML files
        yaml_files, port_verification, total_file_ports = generate_yaml_files()
        
        # Summary
        print("\n🎉 KUBERNETES YAML GENERATION TEST SUMMARY")
        print("=" * 65)
        print(f"✅ All multiple ports tests passed successfully!")
        
        print(f"\n📊 COMPONENT VERIFICATION:")
        print(f"  🔗 App (Deployment): {len(app_ports)} ports verified")
        print(f"  💾 StatefulApp (StatefulSet): {len(stateful_ports)} ports verified")
        print(f"  📊 Job: {len(job_ports)} ports verified")
        print(f"  ⏰ CronJob: {len(cronjob_ports)} ports verified")
        print(f"  🌐 Service: {len(service_ports)} port mappings verified")
        
        total_tested_ports = len(app_ports) + len(stateful_ports) + len(job_ports) + len(cronjob_ports) + len(service_ports)
        
        print(f"\n📄 FILE GENERATION:")
        print(f"  📋 YAML Files Generated: {len(yaml_files)}")
        print(f"  🔌 Total Ports in Files: {total_file_ports}")
        print(f"  📁 Output Directory: kubernetes_manifests/")
        
        print(f"\n✅ VERIFICATION RESULTS:")
        print(f"  🧪 Components Tested: 5 (App, StatefulApp, Job, CronJob, Service)")
        print(f"  🔌 Ports Tested: {total_tested_ports}")
        print(f"  📋 Kubernetes Resources Generated: {len(yaml_files)}")
        print(f"  ✨ All ports correctly included in YAML manifests!")
        
        print(f"\n🌟 MULTIPLE PORTS SUPPORT VERIFIED:")
        print(f"  ✅ App class - Deployment containers include all configured ports")
        print(f"  ✅ StatefulApp class - StatefulSet containers include all configured ports")
        print(f"  ✅ Job class - Job containers include all configured ports")
        print(f"  ✅ CronJob class - CronJob containers include all configured ports")
        print(f"  ✅ Service class - Service specs include all port mappings")
        
        print(f"\n🚀 Celestra Multiple Ports: FULLY FUNCTIONAL!")
        print("    All ports are correctly generated in Kubernetes YAML manifests!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 