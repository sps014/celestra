# Advanced Features

Production-ready features and integrations for enterprise Kubernetes deployments.

## Multi-Format Output

The DSL can generate multiple deployment formats from the same code:

- **Kubernetes YAML** - For production deployment to K8s clusters
- **Docker Compose** - For local development and testing
- **Helm Charts** - For templated K8s deployments
- **Kustomize** - For environment-specific overlays
- **Terraform** - For infrastructure as code

This allows developers to:
- Start development locally with Docker Compose
- Test the same application structure in different environments
- Gradually migrate from Docker Compose to Kubernetes
- Maintain consistency across development and production

## Observability and Monitoring

Comprehensive observability stack integration for production workloads.

```python
from k8s_gen import Observability

app.observability(
    Observability()
        .logging(
            level="INFO",
            format="json",
            output=["stdout", "fluentd"],
            structured_fields=["timestamp", "level", "message", "trace_id", "user_id"],
            retention_days=30,
            sampling_rate=1.0
        )
        .metrics(
            prometheus_scraping=True,
            scrape_interval="15s",
            metrics_path="/metrics",
            custom_metrics=[
                "http_requests_total",
                "http_request_duration_seconds",
                "db_connection_pool_size",
                "business_events_total"
            ],
            dashboards=[
                "grafana://app-dashboard",
                "grafana://business-metrics"
            ],
            recording_rules={
                "job:http_requests:rate5m": "rate(http_requests_total[5m])",
                "job:http_request_duration:p99": "histogram_quantile(0.99, http_request_duration_seconds_bucket)"
            }
        )
        .tracing(
            enabled=True,
            jaeger_endpoint="http://jaeger:14268/api/traces",
            sampling_rate=0.1,
            trace_headers=["x-trace-id", "x-request-id", "x-correlation-id"],
            service_name="myapp"
        )
        .alerting(
            slack_webhook="https://hooks.slack.com/services/...",
            pagerduty_integration_key="...",
            email_recipients=["ops@company.com"],
            rules={
                "high_error_rate": {
                    "condition": "rate(http_errors_total[5m]) > 0.05",
                    "for": "2m",
                    "severity": "critical",
                    "description": "Error rate is above 5% for 2 minutes"
                },
                "high_latency": {
                    "condition": "histogram_quantile(0.99, http_request_duration_seconds_bucket) > 2",
                    "for": "5m", 
                    "severity": "warning",
                    "description": "99th percentile latency is above 2 seconds"
                },
                "pod_crash_looping": {
                    "condition": "rate(kube_pod_container_status_restarts_total[15m]) > 0",
                    "for": "1m",
                    "severity": "critical"
                }
            }
        )
        .health_checks(
            startup_probe="/health/startup",
            readiness_probe="/health/ready", 
            liveness_probe="/health/live",
            custom_probes={
                "database": "SELECT 1",
                "redis": "PING",
                "external_api": "GET https://api.external.com/health"
            }
        )
)
```

### Generated Observability Resources

This configuration generates:
- **ServiceMonitor** for Prometheus scraping
- **PrometheusRule** for alerting rules and recording rules
- **Grafana Dashboard** ConfigMaps
- **Jaeger** tracing configuration
- **Fluentd/Fluent Bit** logging configuration
- **Alert Manager** notification configuration

## Advanced Deployment Strategies

Zero-downtime deployments with sophisticated rollout strategies.

```python
from k8s_gen import DeploymentStrategy

app.deployment_strategy(
    DeploymentStrategy()
        .blue_green(
            enabled=True,
            switch_traffic_on_success=True,
            rollback_on_failure=True,
            test_suite="./tests/smoke_tests.py",
            success_criteria=[
                "error_rate < 1%",
                "latency_p99 < 500ms",
                "all_health_checks_pass"
            ],
            pre_switch_hook="./scripts/pre_switch.sh",
            post_switch_hook="./scripts/post_switch.sh"
        )
        .canary(
            enabled=True,
            initial_percentage=5,
            increment_percentage=10,
            success_criteria=[
                "error_rate < 0.5%",
                "latency_p95 < 200ms"
            ],
            analysis_duration="5m",
            automated_promotion=True,
            max_percentage=50,
            rollback_on_failure=True
        )
        .rolling_update(
            max_unavailable="25%",
            max_surge="25%",
            readiness_timeout="5m",
            progress_deadline="10m",
            revision_history_limit=5
        )
        .feature_flags(
            provider="launchdarkly",
            flags={
                "new_algorithm": {"default": False, "canary": True},
                "enhanced_ui": {"default": False, "percentage": 10}
            }
        )
)
```

### Deployment Strategy Features

- **Blue-Green Deployments** - Zero downtime with traffic switching
- **Canary Releases** - Gradual rollout with automated promotion/rollback
- **Rolling Updates** - Standard Kubernetes rolling update with fine-tuning
- **Feature Flags** - Integration with feature flag providers
- **Automated Testing** - Run test suites during deployment
- **Success Criteria** - Define metrics-based success conditions

## External Service Integration

Cloud services and third-party integrations for complete application stacks.

```python
from k8s_gen import ExternalServices

app.external_services(
    ExternalServices()
        # AWS Services
        .aws_s3_bucket("my-app-storage", 
            region="us-east-1",
            versioning=True,
            encryption="AES256",
            lifecycle_policy="./s3-lifecycle.json"
        )
        .aws_rds_instance("my-app-db",
            engine="postgres",
            version="13.7",
            instance_class="db.r5.large",
            storage="100GB",
            connection_secret="db-secret"
        )
        .aws_elasticache("my-app-cache",
            engine="redis",
            node_type="cache.r6g.large",
            num_nodes=3
        )
        .aws_sqs_queue("my-app-queue",
            visibility_timeout=300,
            message_retention=1209600
        )
        
        # Google Cloud Services
        .gcp_cloud_sql("my-app-db",
            database_version="POSTGRES_13",
            tier="db-custom-2-8192"
        )
        .gcp_pub_sub("my-app-events",
            topics=["user-events", "order-events"]
        )
        
        # Monitoring and Observability
        .datadog(
            api_key_secret="datadog-secret",
            tags=["env:production", "service:myapp"]
        )
        .new_relic(
            license_key_secret="newrelic-secret",
            app_name="MyApp Production"
        )
        
        # External APIs
        .external_api("payment-gateway",
            url="https://api.stripe.com",
            auth={"type": "bearer", "secret": "stripe-secret"},
            rate_limit=100
        )
        .external_api("notification-service",
            url="https://api.sendgrid.com",
            auth={"type": "api_key", "secret": "sendgrid-secret"}
        )
        
        # CDN and Load Balancing
        .cloudfront_distribution("my-app-cdn",
            origins=["api.mycompany.com"],
            cache_behaviors={
                "/api/*": {"ttl": 0},
                "/static/*": {"ttl": 86400}
            }
        )
)
```

### External Service Categories

- **Cloud Storage** - S3, Google Cloud Storage, Azure Blob
- **Managed Databases** - RDS, Cloud SQL, Azure Database
- **Message Queues** - SQS, Pub/Sub, Service Bus
- **Caching** - ElastiCache, Memorystore, Redis Cache
- **Monitoring** - DataDog, New Relic, Splunk
- **CDN** - CloudFront, CloudFlare, Azure CDN
- **External APIs** - Payment gateways, notification services

## Custom Resources & Operators

Integration with Kubernetes operators and custom resource definitions.

```python
# Custom resource integration
app.add_custom_resource(
    CustomResource("CertManager")
        .api_version("cert-manager.io/v1")
        .kind("Certificate")
        .spec({
            "secretName": "my-app-tls",
            "dnsNames": ["api.mycompany.com"],
            "issuerRef": {"name": "letsencrypt-prod", "kind": "ClusterIssuer"}
        })
)

# Operator pattern
app.add_operator(
    Operator("prometheus")
        .helm_chart("prometheus-community/prometheus")
        .values_file("./charts/prometheus-values.yaml")
        .namespace("monitoring")
)
```

### Supported Operators

- **Cert-Manager** - TLS certificate management
- **Prometheus Operator** - Monitoring stack
- **Istio** - Service mesh
- **ArgoCD** - GitOps deployments
- **Velero** - Backup and restore
- **External-DNS** - DNS record management

## Security Policies

Comprehensive security configuration for production workloads.

```python
app.security(
    SecurityPolicy()
        .run_as_non_root()
        .read_only_filesystem()
        .drop_capabilities(["ALL"])
        .add_capabilities(["NET_ADMIN"])  # if needed
        .security_context_constraints("restricted")
        .pod_security_policy("baseline")
)

# Network security
app.network_security(
    NetworkSecurity()
        .deny_all_ingress()
        .allow_ingress_from_namespaces(["frontend", "api-gateway"])
        .allow_egress_to_services(["database", "cache"])
        .require_tls()
)
```

### Security Features

- **Pod Security Standards** - Baseline, restricted, privileged
- **Network Policies** - Fine-grained network access control
- **Security Contexts** - Container security configuration
- **RBAC** - Role-based access control
- **Image Security** - Vulnerability scanning and admission control
- **Secrets Management** - Secure secret storage and rotation

## Cost Optimization

Built-in cost optimization features for efficient resource usage.

```python
app.cost_optimization(
    CostOptimization()
        .spot_instances(percentage=50)
        .scheduled_scaling({
            "business_hours": {"replicas": 5, "schedule": "0 8 * * 1-5"},
            "off_hours": {"replicas": 1, "schedule": "0 18 * * 1-5"}
        })
        .resource_quotas(
            cpu_limit="2000m",
            memory_limit="4Gi",
            storage_limit="100Gi"
        )
)
```

### Cost Optimization Features

- **Spot Instances** - Use cheaper spot instances where appropriate
- **Scheduled Scaling** - Scale down during off-hours
- **Resource Quotas** - Prevent resource over-allocation
- **Vertical Pod Autoscaling** - Right-size containers automatically
- **Resource Recommendations** - AI-powered resource recommendations

## Plugin System

Extensible plugin architecture for custom functionality.

```python
# Custom plugin for specific needs
from k8s_gen.plugins import Plugin

class CustomLogPlugin(Plugin):
    def apply(self, app):
        app.add_companion(
            Companion("custom-logger")
                .image("mycompany/custom-logger:latest")
                .type("sidecar")
                .environment(self.config)
        )

app.use_plugin(
    CustomLogPlugin(config={"LOG_FORMAT": "json", "LOG_LEVEL": "info"})
)
```

### Available Plugins

- **Monitoring Plugins** - DataDog, New Relic, Splunk
- **Security Plugins** - Falco, OPA Gatekeeper, Twistlock
- **Backup Plugins** - Velero, Kasten, Stash
- **CI/CD Plugins** - ArgoCD, Flux, Tekton
- **Service Mesh Plugins** - Istio, Linkerd, Consul Connect

## Environment Management

Multi-environment deployment with environment-specific configurations.

```python
# Multi-environment deployment
environments = {
    "development": {
        "replicas": 1,
        "resources": {"cpu": "100m", "memory": "256Mi"},
        "ingress": "dev-api.mycompany.com"
    },
    "staging": {
        "replicas": 2,
        "resources": {"cpu": "500m", "memory": "512Mi"},
        "ingress": "staging-api.mycompany.com"
    },
    "production": {
        "replicas": 5,
        "resources": {"cpu": "1000m", "memory": "1Gi"},
        "ingress": "api.mycompany.com",
        "auto_scaling": True
    }
}

for env_name, config in environments.items():
    env_app = app.for_environment(env_name)
    env_app.apply_config(config)
    env_app.generate().to_yaml(f"./k8s/{env_name}/")
```

### Environment Features

- **Environment-Specific Configuration** - Different settings per environment
- **Promotion Pipelines** - Automated promotion between environments
- **Configuration Drift Detection** - Detect configuration differences
- **Environment Isolation** - Network and resource isolation

## Performance Optimization

Advanced performance tuning for high-throughput applications.

```python
app.performance(
    Performance()
        .cpu_optimization(
            cpu_manager_policy="static",
            topology_spread_constraints=True
        )
        .memory_optimization(
            huge_pages="2Mi",
            numa_awareness=True
        )
        .network_optimization(
            cni="cilium",
            bandwidth_limit="1Gbps",
            latency_optimization=True
        )
        .storage_optimization(
            storage_class="ssd",
            io_priority="high",
            access_pattern="random"
        )
)
```

### Performance Features

- **CPU Optimization** - CPU pinning, topology awareness
- **Memory Optimization** - Huge pages, NUMA awareness
- **Network Optimization** - CNI selection, bandwidth limits
- **Storage Optimization** - Storage class selection, I/O optimization
- **Autoscaling Tuning** - Custom metrics, predictive scaling

## Disaster Recovery

Built-in disaster recovery and backup capabilities.

```python
app.disaster_recovery(
    DisasterRecovery()
        .backup_schedule("0 2 * * *")
        .backup_retention(days=30)
        .cross_region_replication(regions=["us-west-2", "eu-west-1"])
        .rto_target("15m")  # Recovery Time Objective
        .rpo_target("1h")   # Recovery Point Objective
        .failover_strategy("automatic")
)
```

### Disaster Recovery Features

- **Automated Backups** - Scheduled backups with retention policies
- **Cross-Region Replication** - Replicate data across regions
- **Failover Automation** - Automatic failover on failure detection
- **Recovery Testing** - Regular disaster recovery testing
- **Point-in-Time Recovery** - Restore to specific points in time

## Compliance & Governance

Built-in compliance and governance features for enterprise environments.

```python
app.compliance(
    Compliance()
        .standards(["SOC2", "HIPAA", "PCI-DSS"])
        .audit_logging(enabled=True, retention_years=7)
        .data_classification(sensitivity="confidential")
        .encryption(at_rest=True, in_transit=True)
        .access_controls(
            mfa_required=True,
            session_timeout="8h",
            privileged_access_review=True
        )
)
```

### Compliance Features

- **Standards Compliance** - SOC2, HIPAA, PCI-DSS, GDPR
- **Audit Logging** - Comprehensive audit trails
- **Data Classification** - Automatic data sensitivity labeling
- **Encryption** - End-to-end encryption
- **Access Controls** - MFA, session management, privilege review 