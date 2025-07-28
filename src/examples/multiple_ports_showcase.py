#!/usr/bin/env python3
"""
Comprehensive Multiple Ports Showcase for Celestra.

This example demonstrates the enhanced multiple ports support across all
components that support ports: App, StatefulApp, Job, CronJob, and Service.
"""

from ..celestra import (
    App, StatefulApp, Job, CronJob, Service, 
    KubernetesOutput, HelmOutput, Secret, ConfigMap
)

def create_microservices_with_multiple_ports():
    """Create a complete microservices architecture with multiple ports."""
    print("🏗️ Creating Microservices Platform with Multiple Ports...")
    
    components = []
    
    # 1. API Gateway with comprehensive port configuration
    api_gateway = (App("api-gateway")
        .image("nginx:1.23-alpine")
        .http_port(8080, "gateway")
        .https_port(8443, "gateway-tls") 
        .metrics_port(9113, "nginx-metrics")
        .health_port(8081, "nginx-health")
        .admin_port(8082, "nginx-admin")
        .env("NGINX_HOST", "api.company.com")
        .env("NGINX_PORT", "8080")
        .resources(cpu="200m", memory="256Mi")
        .replicas(2))
    
    # 2. Authentication Service with mixed port approaches
    auth_service = (App("auth-service")
        .image("auth-server:3.2.0")
        .common_ports(http=8080, metrics=9090, health=8081)  # Use convenience method
        .grpc_port(9091, "auth-grpc")
        .debug_port(5005, "remote-debug")
        .add_port(8090, "webhooks")  # Custom webhook port
        .env("JWT_SECRET", "$(SECRET_VALUE)")
        .env("LOG_LEVEL", "info")
        .resources(cpu="500m", memory="1Gi")
        .replicas(3))
    
    # 3. User Service with bulk port configuration
    user_service = (App("user-service")
        .image("user-mgmt:2.8.0")
        .ports([
            {"port": 8080, "name": "rest-api"},
            {"port": 9090, "name": "grpc-api"},
            {"port": 9091, "name": "metrics"},
            {"port": 8081, "name": "health"},
            {"port": 9000, "name": "admin"},
            {"port": 8082, "name": "websocket"}
        ])
        .env("DATABASE_URL", "$(SECRET_VALUE)")
        .resources(cpu="300m", memory="512Mi")
        .replicas(2))
    
    # 4. PostgreSQL Database Cluster with database-specific ports
    postgres_primary = (StatefulApp("postgres-primary")
        .image("postgres:15.2-alpine")
        .postgres_port(5432, "postgres")
        .metrics_port(9187, "postgres-exporter")
        .admin_port(8080, "pgadmin")
        .cluster_port(5433, "replication")
        .add_port(5434, "backup-stream")
        .env("POSTGRES_DB", "company_db")
        .env("POSTGRES_USER", "app_user")
        .env("POSTGRES_PASSWORD", "$(SECRET_VALUE)")
        .storage("/var/lib/postgresql/data", "200Gi", "fast-ssd")
        .resources(cpu="2", memory="8Gi")
        .replicas(1))
    
    # 5. Redis Cluster with cluster communication ports
    redis_cluster = (StatefulApp("redis-cluster")
        .image("redis:7.0.8-alpine")
        .redis_port(6379, "redis")
        .add_port(16379, "cluster-bus")
        .metrics_port(9121, "redis-exporter")
        .admin_port(8080, "redis-commander")
        .storage("/data", "50Gi")
        .resources(cpu="1", memory="4Gi")
        .replicas(6))
    
    # 6. Elasticsearch Cluster with comprehensive search platform ports
    elasticsearch = (StatefulApp("elasticsearch")
        .image("elasticsearch:8.6.0")
        .elasticsearch_port(9200, "http-api")
        .add_port(9300, "transport")
        .metrics_port(9114, "es-exporter")
        .admin_port(5601, "kibana")
        .cluster_port(9400, "cluster-coordination")
        .storage("/usr/share/elasticsearch/data", "500Gi")
        .resources(cpu="2", memory="16Gi")
        .replicas(3))
    
    # 7. Apache Kafka with multiple protocols
    kafka_cluster = (StatefulApp("kafka-cluster")
        .image("kafka:3.4.0")
        .kafka_port(9092, "kafka-internal")
        .add_port(9093, "kafka-external")
        .add_port(9094, "kafka-ssl")
        .metrics_port(9308, "kafka-exporter")
        .admin_port(8080, "kafka-ui")
        .add_port(9999, "jmx-metrics")
        .storage("/kafka/logs", "1Ti")
        .resources(cpu="2", memory="8Gi")
        .replicas(3))
    
    # 8. Data Processing Job with monitoring
    data_processing_job = (Job("data-migration")
        .image("data-processor:2.1.0")
        .command(["python", "process_data.py"])
        .web_port(8080, "job-ui")
        .metrics_port(9090, "job-metrics")
        .status_port(8081, "job-status")
        .env("DATA_SOURCE", "$(SECRET_VALUE)")
        .env("BATCH_SIZE", "1000")
        .resources(cpu="2", memory="4Gi")
        .parallelism(3)
        .completions(3)
        .timeout("2h"))
    
    # 9. Backup CronJob with web interface
    backup_cronjob = (CronJob("daily-backup")
        .schedule("0 2 * * *")  # Daily at 2 AM
        .image("backup-tool:1.8.0")
        .command(["backup.sh"])
        .web_port(8080, "backup-ui")
        .metrics_port(9090, "backup-metrics")
        .status_port(8081, "backup-status")
        .env("BACKUP_TARGET", "s3://company-backups/")
        .env("RETENTION_DAYS", "30")
        .resources(cpu="1", memory="2Gi")
        .timeout("4h"))
    
    # 10. Log Processing CronJob
    log_processor = (CronJob("log-aggregation")
        .schedule("*/15 * * * *")  # Every 15 minutes
        .image("log-processor:2.0.0")
        .command(["aggregate_logs.py"])
        .ports([
            {"port": 8080, "name": "web-ui"},
            {"port": 9090, "name": "metrics"},
            {"port": 8081, "name": "health"}
        ])
        .env("LOG_SOURCE", "/var/log/apps")
        .resources(cpu="500m", memory="1Gi"))
    
    components = [
        api_gateway, auth_service, user_service,
        postgres_primary, redis_cluster, elasticsearch, kafka_cluster,
        data_processing_job, backup_cronjob, log_processor
    ]
    
    return components


def create_services_for_apps(apps):
    """Create corresponding services for apps with multiple ports."""
    print("🌐 Creating Services with Multiple Port Mappings...")
    
    services = []
    
    # Service for API Gateway
    api_gateway_service = (Service("api-gateway-service")
        .selector({"app": "api-gateway"})
        .add_port("http", 80, 8080)
        .add_port("https", 443, 8443)
        .add_port("metrics", 9113, 9113)
        .add_port("health", 8081, 8081)
        .type("LoadBalancer"))
    
    # Service for Auth Service
    auth_service_svc = (Service("auth-service")
        .selector({"app": "auth-service"})
        .add_port("http", 80, 8080)
        .add_port("grpc", 9091, 9091)
        .add_port("metrics", 9090, 9090)
        .add_port("health", 8081, 8081)
        .add_port("webhooks", 8090, 8090))
    
    # Service for User Service
    user_service_svc = (Service("user-service")
        .selector({"app": "user-service"})
        .add_port("rest", 80, 8080)
        .add_port("grpc", 9090, 9090)
        .add_port("metrics", 9091, 9091)
        .add_port("websocket", 8082, 8082))
    
    # Service for Postgres Primary
    postgres_service = (Service("postgres-primary")
        .selector({"app": "postgres-primary"})
        .add_port("postgres", 5432, 5432)
        .add_port("metrics", 9187, 9187)
        .add_port("admin", 8080, 8080))
    
    # Service for Redis Cluster
    redis_service = (Service("redis-cluster")
        .selector({"app": "redis-cluster"})
        .add_port("redis", 6379, 6379)
        .add_port("cluster", 16379, 16379)
        .add_port("metrics", 9121, 9121))
    
    # Service for Data Processing Job
    job_service = (Service("data-processing-job")
        .selector({"app": "data-migration"})
        .add_port("web", 8080, 8080)
        .add_port("metrics", 9090, 9090)
        .add_port("status", 8081, 8081))
    
    services = [
        api_gateway_service, auth_service_svc, user_service_svc,
        postgres_service, redis_service, job_service
    ]
    
    return services


def analyze_port_configuration(components):
    """Analyze the port configuration across all components."""
    print("\n📊 Analyzing Port Configuration...")
    
    total_ports = 0
    port_analysis = {
        "App": [],
        "StatefulApp": [],
        "Job": [],
        "CronJob": []
    }
    
    for component in components:
        component_type = type(component).__name__
        if component_type in port_analysis:
            # Get Kubernetes resources to extract ports
            k8s_resources = component.generate_kubernetes_resources()
            
            # Find the workload resource
            workload = None
            for resource in k8s_resources:
                if resource["kind"] in ["Deployment", "StatefulSet", "Job", "CronJob"]:
                    workload = resource
                    break
            
            if workload:
                # Extract container ports
                if workload["kind"] == "CronJob":
                    container = workload["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]
                else:
                    container = workload["spec"]["template"]["spec"]["containers"][0]
                
                ports = container.get("ports", [])
                port_count = len(ports)
                total_ports += port_count
                
                port_analysis[component_type].append({
                    "name": component._name,
                    "port_count": port_count,
                    "ports": ports
                })
    
    # Print analysis
    for component_type, components_data in port_analysis.items():
        if components_data:
            print(f"\n  📦 {component_type} Components:")
            for comp_data in components_data:
                print(f"    {comp_data['name']}: {comp_data['port_count']} ports")
                for port in comp_data['ports']:
                    print(f"      - {port['name']}: {port['containerPort']}/{port['protocol']}")
    
    print(f"\n  ✅ Total ports configured: {total_ports}")
    print(f"  📈 Average ports per component: {total_ports / len(components):.1f}")
    
    return total_ports, port_analysis


def demonstrate_port_patterns():
    """Demonstrate different port configuration patterns."""
    print("\n🎯 Demonstrating Port Configuration Patterns...")
    
    patterns = []
    
    # Pattern 1: Web Application Stack
    web_app = (App("web-app")
        .image("webapp:2.0.0")
        .common_ports()  # Standard HTTP, metrics, health
        .admin_port(9000)
        .debug_port(5005))
    patterns.append(("Web Application", web_app))
    
    # Pattern 2: Microservice with gRPC
    grpc_service = (App("grpc-service")
        .image("grpc-server:1.5.0")
        .http_port(8080, "rest-api")
        .grpc_port(9090, "grpc-api")
        .metrics_port(9091)
        .health_port(8081))
    patterns.append(("gRPC Microservice", grpc_service))
    
    # Pattern 3: Database with monitoring
    database = (StatefulApp("database")
        .image("postgres:15")
        .postgres_port(5432)
        .metrics_port(9187)
        .admin_port(8080))
    patterns.append(("Database", database))
    
    # Pattern 4: Message Queue Cluster
    message_queue = (StatefulApp("message-queue")
        .image("rabbitmq:3.11")
        .add_port(5672, "amqp")
        .add_port(15672, "management")
        .add_port(25672, "clustering")
        .metrics_port(15692))
    patterns.append(("Message Queue", message_queue))
    
    # Pattern 5: Batch Job with Monitoring
    batch_job = (Job("batch-processor")
        .image("batch:1.0.0")
        .web_port(8080)
        .metrics_port(9090)
        .status_port(8081))
    patterns.append(("Batch Job", batch_job))
    
    # Pattern 6: Scheduled Task with UI
    scheduled_task = (CronJob("report-generator")
        .schedule("0 9 * * 1")  # Monday 9 AM
        .image("reporter:2.0.0")
        .web_port(8080, "report-ui")
        .metrics_port(9090)
        .status_port(8081))
    patterns.append(("Scheduled Task", scheduled_task))
    
    for pattern_name, component in patterns:
        k8s_resources = component.generate_kubernetes_resources()
        workload = k8s_resources[0]
        
        # Extract ports based on resource type
        if workload["kind"] == "CronJob":
            container = workload["spec"]["jobTemplate"]["spec"]["template"]["spec"]["containers"][0]
        else:
            container = workload["spec"]["template"]["spec"]["containers"][0]
        
        ports = container.get("ports", [])
        print(f"  📋 {pattern_name}: {len(ports)} ports")
        for port in ports:
            print(f"    - {port['name']}: {port['containerPort']}")
    
    return patterns


def generate_comprehensive_output():
    """Generate comprehensive output in multiple formats."""
    print("\n📄 Generating Comprehensive Output...")
    
    # Create all components
    microservices = create_microservices_with_multiple_ports()
    services = create_services_for_apps(microservices)
    all_components = microservices + services
    
    # Generate Kubernetes YAML
    k8s_output = KubernetesOutput()
    all_resources = []
    
    for component in all_components:
        if hasattr(component, 'generate_kubernetes_resources'):
            all_resources.extend(component.generate_kubernetes_resources())
    
    # Generate Helm Chart
    helm_chart = (HelmOutput("microservices-platform")
        .set_version("2.0.0")
        .set_description("Microservices platform with comprehensive port configuration"))
    
    for component in all_components:
        if hasattr(component, 'generate_kubernetes_resources'):
            helm_chart.add_resource(component)
    
    import tempfile
    import os
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Generate Kubernetes YAML files
        yaml_dir = os.path.join(temp_dir, "kubernetes")
        os.makedirs(yaml_dir)
        
        for i, resource in enumerate(all_resources):
            kind = resource.get("kind", "resource").lower()
            name = resource.get("metadata", {}).get("name", f"resource-{i}")
            filename = f"{kind}-{name}.yaml"
            
            import yaml
            with open(os.path.join(yaml_dir, filename), 'w') as f:
                f.write(yaml.dump(resource, default_flow_style=False))
        
        yaml_files = len(os.listdir(yaml_dir))
        
        # Generate Helm chart
        helm_dir = os.path.join(temp_dir, "helm")
        helm_chart.generate_files(helm_dir)
        helm_files = sum(len(files) for _, _, files in os.walk(helm_dir))
        
        print(f"  ✅ Generated {yaml_files} Kubernetes YAML files")
        print(f"  ✅ Generated {helm_files} Helm chart files")
        print(f"  📁 Output location: {temp_dir}")
        
        return yaml_files, helm_files


def main():
    """Run the comprehensive multiple ports showcase."""
    print("🚀 Celestra: Comprehensive Multiple Ports Showcase")
    print("=" * 70)
    print("🎯 Demonstrating Enhanced Multiple Ports Support Across All Components")
    print("=" * 70)
    
    try:
        # Create microservices platform
        microservices = create_microservices_with_multiple_ports()
        print(f"  ✅ Created {len(microservices)} microservices components")
        
        # Create services
        services = create_services_for_apps(microservices)
        print(f"  ✅ Created {len(services)} services with port mappings")
        
        # Analyze port configuration
        total_ports, analysis = analyze_port_configuration(microservices)
        
        # Demonstrate port patterns
        patterns = demonstrate_port_patterns()
        print(f"  ✅ Demonstrated {len(patterns)} common port patterns")
        
        # Generate output
        yaml_files, helm_files = generate_comprehensive_output()
        
        # Final Summary
        print("\n🎉 MULTIPLE PORTS SHOWCASE SUMMARY")
        print("=" * 70)
        print(f"✅ All multiple ports features demonstrated successfully!")
        
        print(f"\n📊 COMPONENT BREAKDOWN:")
        total_components = len(microservices)
        for comp_type, comps in analysis.items():
            if comps:
                comp_ports = sum(c['port_count'] for c in comps)
                print(f"  📦 {comp_type}: {len(comps)} components, {comp_ports} total ports")
        
        print(f"\n🔗 PORT STATISTICS:")
        print(f"  📊 Total Components: {total_components}")
        print(f"  🔌 Total Ports: {total_ports}")
        print(f"  📈 Average Ports/Component: {total_ports / total_components:.1f}")
        print(f"  🌐 Service Mappings: {len(services)} services")
        
        print(f"\n📄 OUTPUT GENERATION:")
        print(f"  📋 Kubernetes YAML: {yaml_files} files")
        print(f"  ⎈ Helm Chart: {helm_files} files")
        
        print(f"\n✨ ENHANCED FEATURES SHOWCASED:")
        print(f"  🔧 Multiple port configuration methods")
        print(f"  📦 Convenience methods for common patterns")
        print(f"  🎯 Database-specific port helpers")
        print(f"  🌐 Service integration with port mapping")
        print(f"  📊 Job and CronJob port support")
        print(f"  🔗 Bulk port configuration")
        print(f"  ⚡ Real-world microservices scenarios")
        
        print(f"\n🌟 COMPONENTS WITH MULTIPLE PORTS SUPPORT:")
        print(f"  ✅ App - Web applications, microservices")
        print(f"  ✅ StatefulApp - Databases, message queues, search engines")
        print(f"  ✅ Job - Batch processing with monitoring")
        print(f"  ✅ CronJob - Scheduled tasks with web interfaces")
        print(f"  ✅ Service - Multi-port service mapping")
        
        print(f"\n🚀 Celestra: Complete Multiple Ports Support Ready!")
        print("    Perfect for modern microservices architectures!")
        
    except Exception as e:
        print(f"❌ Showcase failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 