# Extensions

Plugin system and customization guide for extending K8s-Gen functionality.

## Plugin System

K8s-Gen features a powerful plugin architecture that allows you to extend the DSL with custom functionality, integrations, and domain-specific abstractions.

### Plugin Architecture

The plugin system is built around three core concepts:

1. **Custom Builders** - Extend the DSL with new resource types
2. **Template Extensions** - Customize output generation
3. **Validation Extensions** - Add custom validation rules

```python
from k8s_gen import PluginManager, Plugin

# Initialize plugin manager
plugins = PluginManager()

# Register plugins
plugins.register("database_cluster", "./plugins/database.py")
plugins.register("monitoring_stack", "./plugins/monitoring.py")
plugins.register("ml_pipeline", "./plugins/ml_workloads.py")

# Load and use plugins
plugins.load_all()
```

### Creating Custom Plugins

```python
# plugins/database_cluster.py
from k8s_gen import Plugin, StatefulApp, ConfigMap, Secret

class DatabaseCluster(Plugin):
    """Custom database cluster with automatic failover and backups."""
    
    def __init__(self, name):
        super().__init__(name)
        self.cluster_size = 3
        self.version = "latest"
        self.backup_schedule = "0 2 * * *"
        self.high_availability = True
        
    def cluster_size(self, size):
        """Set the number of database replicas."""
        self.cluster_size = size
        return self
        
    def version(self, version):
        """Set the database version."""
        self.version = version
        return self
        
    def backup_schedule(self, schedule):
        """Set the backup cron schedule."""
        self.backup_schedule = schedule
        return self
        
    def generate_resources(self):
        """Generate the Kubernetes resources for the database cluster."""
        resources = []
        
        # Primary database
        primary = (StatefulApp(f"{self.name}-primary")
            .image(f"database-server:{self.version}")
            .port(5432)
            .storage("100Gi")
            .environment({
                "ROLE": "primary",
                "CLUSTER_SIZE": str(self.cluster_size)
            }))
        resources.append(primary)
        
        # Read replicas
        for i in range(self.cluster_size - 1):
            replica = (StatefulApp(f"{self.name}-replica-{i}")
                .image(f"database-server:{self.version}")
                .port(5432)
                .storage("100Gi")
                .environment({
                    "ROLE": "replica",
                    "PRIMARY_HOST": f"{self.name}-primary"
                }))
            resources.append(replica)
        
        # Configuration
        config = (ConfigMap(f"{self.name}-config")
            .add("replication_mode", "streaming")
            .add("max_connections", "200")
            .add("shared_buffers", "256MB"))
        resources.append(config)
        
        # Secrets
        secret = (Secret(f"{self.name}-credentials")
            .generate_password("db_password", length=32)
            .add("username", "admin"))
        resources.append(secret)
        
        return resources

# Usage
from plugins.database_cluster import DatabaseCluster

db_cluster = (DatabaseCluster("app-database")
    .cluster_size(5)
    .version("13.7")
    .backup_schedule("0 1 * * *"))

app.add_database(db_cluster)
```

## Custom Builders

Create domain-specific builders for specialized workloads.

### Machine Learning Workloads

```python
# plugins/ml_workloads.py
from k8s_gen import Plugin, Job, StatefulApp

class MLPipeline(Plugin):
    """Machine Learning training and inference pipeline."""
    
    def __init__(self, name):
        super().__init__(name)
        self.framework = "pytorch"
        self.gpu_count = 1
        self.distributed = False
        
    def framework(self, framework):
        """Set ML framework (pytorch, tensorflow, sklearn)."""
        self.framework = framework
        return self
        
    def gpu_resources(self, count):
        """Set number of GPUs required."""
        self.gpu_count = count
        return self
        
    def distributed_training(self, enabled=True, workers=4):
        """Enable distributed training across multiple nodes."""
        self.distributed = enabled
        self.worker_count = workers if enabled else 1
        return self
        
    def data_source(self, type, config):
        """Configure data source (s3, gcs, nfs, etc.)."""
        self.data_source_type = type
        self.data_config = config
        return self
        
    def model_registry(self, registry_url):
        """Set model registry for storing trained models."""
        self.model_registry = registry_url
        return self
        
    def generate_training_job(self):
        """Generate training job resource."""
        return (Job(f"{self.name}-training")
            .image(f"ml-framework:{self.framework}")
            .resources(
                cpu="4000m",
                memory="16Gi",
                gpu=self.gpu_count
            )
            .command([
                "python", "train.py",
                f"--framework={self.framework}",
                f"--data-source={self.data_source_type}",
                f"--distributed={self.distributed}"
            ])
            .timeout("6h"))
    
    def generate_inference_service(self):
        """Generate inference service resource."""
        return (StatefulApp(f"{self.name}-inference")
            .image(f"ml-serving:{self.framework}")
            .port(8080)
            .resources(
                cpu="2000m",
                memory="8Gi",
                gpu=1 if self.gpu_count > 0 else 0
            )
            .health_checks(
                readiness_probe="/health",
                liveness_probe="/health"
            ))

# Usage
ml_pipeline = (MLPipeline("text-classification")
    .framework("pytorch")
    .gpu_resources(2)
    .distributed_training(enabled=True, workers=4)
    .data_source("s3", {"bucket": "training-data", "path": "/datasets/"})
    .model_registry("https://registry.company.com"))

app.add_ml_pipeline(ml_pipeline)
```

### Data Processing Pipelines

```python
# plugins/data_pipeline.py
from k8s_gen import Plugin, Job, CronJob, ConfigMap

class DataPipeline(Plugin):
    """Data processing pipeline with Apache Spark or similar."""
    
    def __init__(self, name):
        super().__init__(name)
        self.engine = "spark"
        self.driver_resources = {"cpu": "1000m", "memory": "2Gi"}
        self.executor_resources = {"cpu": "500m", "memory": "1Gi"}
        self.executor_count = 3
        
    def engine(self, engine):
        """Set processing engine (spark, flink, airflow)."""
        self.engine = engine
        return self
        
    def driver_resources(self, cpu, memory):
        """Set driver pod resources."""
        self.driver_resources = {"cpu": cpu, "memory": memory}
        return self
        
    def executor_resources(self, cpu, memory, count=3):
        """Set executor pod resources and count."""
        self.executor_resources = {"cpu": cpu, "memory": memory}
        self.executor_count = count
        return self
        
    def schedule(self, cron_schedule):
        """Make this a scheduled pipeline."""
        self.schedule = cron_schedule
        return self
        
    def input_source(self, type, config):
        """Configure input data source."""
        self.input_type = type
        self.input_config = config
        return self
        
    def output_destination(self, type, config):
        """Configure output destination."""
        self.output_type = type
        self.output_config = config
        return self

# Usage
etl_pipeline = (DataPipeline("user-analytics")
    .engine("spark")
    .driver_resources("2000m", "4Gi")
    .executor_resources("1000m", "2Gi", count=5)
    .schedule("0 2 * * *")
    .input_source("database", {"table": "user_events"})
    .output_destination("warehouse", {"table": "user_metrics"}))

app.add_data_pipeline(etl_pipeline)
```

### IoT and Edge Computing

```python
# plugins/iot_edge.py
from k8s_gen import Plugin, App, ConfigMap

class EdgeDevice(Plugin):
    """IoT edge computing device configuration."""
    
    def __init__(self, name):
        super().__init__(name)
        self.device_type = "generic"
        self.sensors = []
        self.processing_mode = "local"
        
    def device_type(self, device_type):
        """Set device type (raspberry-pi, nvidia-jetson, generic)."""
        self.device_type = device_type
        return self
        
    def add_sensor(self, sensor_type, config):
        """Add sensor configuration."""
        self.sensors.append({"type": sensor_type, "config": config})
        return self
        
    def processing_mode(self, mode):
        """Set processing mode (local, cloud, hybrid)."""
        self.processing_mode = mode
        return self
        
    def data_sync(self, interval, destination):
        """Configure data synchronization."""
        self.sync_interval = interval
        self.sync_destination = destination
        return self

# Usage
edge_device = (EdgeDevice("factory-sensor-01")
    .device_type("raspberry-pi")
    .add_sensor("temperature", {"pin": 18, "interval": "10s"})
    .add_sensor("humidity", {"pin": 19, "interval": "10s"})
    .processing_mode("hybrid")
    .data_sync("5m", "cloud-analytics"))

app.add_edge_device(edge_device)
```

## Template Customization

Customize the generated output templates for specific requirements.

### Custom Kubernetes Templates

```python
# templates/custom_deployment.yaml.j2
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ name }}
  labels:
    app: {{ name }}
    version: {{ version | default('v1.0.0') }}
    environment: {{ environment }}
    team: {{ team | default('platform') }}
  annotations:
    deployment.kubernetes.io/revision: "{{ revision | default('1') }}"
    company.com/cost-center: {{ cost_center | default('engineering') }}
spec:
  replicas: {{ replicas | default(3) }}
  selector:
    matchLabels:
      app: {{ name }}
  template:
    metadata:
      labels:
        app: {{ name }}
        version: {{ version | default('v1.0.0') }}
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "{{ metrics_port | default('9090') }}"
        prometheus.io/path: "{{ metrics_path | default('/metrics') }}"
    spec:
      serviceAccountName: {{ service_account | default(name + '-sa') }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 1001
      containers:
      - name: {{ name }}
        image: {{ image }}
        ports:
        - containerPort: {{ port }}
          name: http
        {% if metrics_port %}
        - containerPort: {{ metrics_port }}
          name: metrics
        {% endif %}
        env:
        {% for key, value in environment.items() %}
        - name: {{ key }}
          value: "{{ value }}"
        {% endfor %}
        resources:
          requests:
            cpu: {{ resources.cpu | default('100m') }}
            memory: {{ resources.memory | default('128Mi') }}
          limits:
            cpu: {{ resources.cpu_limit | default('500m') }}
            memory: {{ resources.memory_limit | default('512Mi') }}
        livenessProbe:
          httpGet:
            path: {{ health.liveness_path | default('/health') }}
            port: http
          initialDelaySeconds: {{ health.liveness_delay | default(30) }}
          periodSeconds: {{ health.liveness_period | default(10) }}
        readinessProbe:
          httpGet:
            path: {{ health.readiness_path | default('/ready') }}
            port: http
          initialDelaySeconds: {{ health.readiness_delay | default(5) }}
          periodSeconds: {{ health.readiness_period | default(5) }}
```

### Custom Docker Compose Templates

```python
# templates/custom_docker_compose.yaml.j2
version: '3.8'

services:
  {{ name }}:
    image: {{ image }}
    container_name: {{ container_name | default(name) }}
    restart: {{ restart_policy | default('unless-stopped') }}
    {% if ports %}
    ports:
    {% for port_mapping in ports %}
      - "{{ port_mapping }}"
    {% endfor %}
    {% endif %}
    environment:
    {% for key, value in environment.items() %}
      {{ key }}: {{ value }}
    {% endfor %}
    {% if volumes %}
    volumes:
    {% for volume in volumes %}
      - {{ volume }}
    {% endfor %}
    {% endif %}
    {% if depends_on %}
    depends_on:
    {% for dep in depends_on %}
      {{ dep.name }}:
        condition: {{ dep.condition | default('service_started') }}
    {% endfor %}
    {% endif %}
    {% if networks %}
    networks:
    {% for network in networks %}
      - {{ network }}
    {% endfor %}
    {% endif %}
    {% if healthcheck %}
    healthcheck:
      test: {{ healthcheck.test }}
      interval: {{ healthcheck.interval | default('30s') }}
      timeout: {{ healthcheck.timeout | default('10s') }}
      retries: {{ healthcheck.retries | default(3) }}
      start_period: {{ healthcheck.start_period | default('40s') }}
    {% endif %}
    {% if deploy %}
    deploy:
      {% if deploy.replicas %}
      replicas: {{ deploy.replicas }}
      {% endif %}
      {% if deploy.resources %}
      resources:
        limits:
          memory: {{ deploy.resources.memory_limit }}
          cpus: '{{ deploy.resources.cpu_limit }}'
        reservations:
          memory: {{ deploy.resources.memory_request }}
          cpus: '{{ deploy.resources.cpu_request }}'
      {% endif %}
      {% if deploy.restart_policy %}
      restart_policy:
        condition: {{ deploy.restart_policy.condition }}
        delay: {{ deploy.restart_policy.delay }}
        max_attempts: {{ deploy.restart_policy.max_attempts }}
      {% endif %}
    {% endif %}

{% if volumes_section %}
volumes:
{% for volume_name, volume_config in volumes_section.items() %}
  {{ volume_name }}:
    {% if volume_config.driver %}
    driver: {{ volume_config.driver }}
    {% endif %}
    {% if volume_config.driver_opts %}
    driver_opts:
    {% for key, value in volume_config.driver_opts.items() %}
      {{ key }}: {{ value }}
    {% endfor %}
    {% endif %}
{% endfor %}
{% endif %}

{% if networks_section %}
networks:
{% for network_name, network_config in networks_section.items() %}
  {{ network_name }}:
    driver: {{ network_config.driver | default('bridge') }}
    {% if network_config.ipam %}
    ipam:
      config:
      {% for subnet in network_config.ipam.config %}
        - subnet: {{ subnet.subnet }}
      {% endfor %}
    {% endif %}
{% endfor %}
{% endif %}
```

### Template Registration

```python
from k8s_gen import TemplateManager

# Register custom templates
templates = TemplateManager()
templates.register("custom_deployment", "./templates/custom_deployment.yaml.j2")
templates.register("custom_compose", "./templates/custom_docker_compose.yaml.j2")

# Use custom templates
app.use_template("custom_deployment")
app.generate().to_yaml("./k8s/")
```

## Validation Extensions

Add custom validation rules and policies.

### Custom Validators

```python
# validators/security_validator.py
from k8s_gen import Validator, ValidationError

class SecurityValidator(Validator):
    """Custom security validation rules."""
    
    def validate_image_registry(self, app):
        """Ensure images come from approved registries."""
        approved_registries = [
            "company-registry.com",
            "docker.io",
            "gcr.io"
        ]
        
        image = app.image
        registry = image.split('/')[0] if '/' in image else 'docker.io'
        
        if registry not in approved_registries:
            raise ValidationError(
                f"Image registry '{registry}' not approved. "
                f"Use one of: {', '.join(approved_registries)}"
            )
    
    def validate_resource_limits(self, app):
        """Ensure resource limits are set."""
        if not hasattr(app, 'resources') or not app.resources:
            raise ValidationError("Resource limits must be specified")
        
        required_limits = ['cpu_limit', 'memory_limit']
        for limit in required_limits:
            if limit not in app.resources:
                raise ValidationError(f"Missing required resource limit: {limit}")
    
    def validate_security_context(self, app):
        """Ensure security context is configured."""
        if not hasattr(app, 'security_context'):
            raise ValidationError("Security context must be configured")
        
        required_settings = ['run_as_non_root', 'read_only_root_filesystem']
        for setting in required_settings:
            if not getattr(app.security_context, setting, False):
                raise ValidationError(f"Security setting required: {setting}")

# Register and use validator
from validators.security_validator import SecurityValidator

app.add_validator(SecurityValidator())
```

### Policy Validators

```python
# validators/policy_validator.py
from k8s_gen import Validator, ValidationError

class PolicyValidator(Validator):
    """Organizational policy validation."""
    
    def __init__(self, policy_config):
        self.policy_config = policy_config
    
    def validate_naming_convention(self, app):
        """Validate naming conventions."""
        pattern = self.policy_config.get('naming_pattern', r'^[a-z][a-z0-9-]*[a-z0-9]$')
        if not re.match(pattern, app.name):
            raise ValidationError(
                f"Application name '{app.name}' doesn't match naming convention"
            )
    
    def validate_labels(self, app):
        """Validate required labels."""
        required_labels = self.policy_config.get('required_labels', [])
        app_labels = getattr(app, 'labels', {})
        
        missing_labels = set(required_labels) - set(app_labels.keys())
        if missing_labels:
            raise ValidationError(
                f"Missing required labels: {', '.join(missing_labels)}"
            )
    
    def validate_resource_quotas(self, app):
        """Validate resource usage against quotas."""
        max_cpu = self.policy_config.get('max_cpu_per_app', '2000m')
        max_memory = self.policy_config.get('max_memory_per_app', '4Gi')
        
        if app.resources.get('cpu_limit', '0') > max_cpu:
            raise ValidationError(f"CPU limit exceeds maximum: {max_cpu}")
        
        if app.resources.get('memory_limit', '0') > max_memory:
            raise ValidationError(f"Memory limit exceeds maximum: {max_memory}")

# Usage
policy_config = {
    'naming_pattern': r'^[a-z][a-z0-9-]*[a-z0-9]$',
    'required_labels': ['team', 'environment', 'version'],
    'max_cpu_per_app': '2000m',
    'max_memory_per_app': '4Gi'
}

app.add_validator(PolicyValidator(policy_config))
```

## Output Format Extensions

Add support for new output formats.

### Terraform Output

```python
# output_formats/terraform.py
from k8s_gen import OutputFormat

class TerraformOutput(OutputFormat):
    """Generate Terraform modules from K8s-Gen DSL."""
    
    def generate(self, app, output_path):
        """Generate Terraform configuration."""
        terraform_config = {
            'terraform': {
                'required_version': '>= 1.0',
                'required_providers': {
                    'kubernetes': {
                        'source': 'hashicorp/kubernetes',
                        'version': '~> 2.0'
                    }
                }
            },
            'resource': self._generate_resources(app)
        }
        
        self._write_terraform_file(terraform_config, output_path)
    
    def _generate_resources(self, app):
        """Generate Terraform resources."""
        resources = {}
        
        # Deployment resource
        resources['kubernetes_deployment'] = {
            app.name: {
                'metadata': {
                    'name': app.name,
                    'labels': app.labels or {}
                },
                'spec': {
                    'replicas': app.replicas or 1,
                    'selector': {
                        'match_labels': {'app': app.name}
                    },
                    'template': {
                        'metadata': {
                            'labels': {'app': app.name}
                        },
                        'spec': {
                            'container': [{
                                'name': app.name,
                                'image': app.image,
                                'port': [{'container_port': app.port}]
                            }]
                        }
                    }
                }
            }
        }
        
        # Service resource
        resources['kubernetes_service'] = {
            app.name: {
                'metadata': {
                    'name': app.name
                },
                'spec': {
                    'selector': {'app': app.name},
                    'port': [{
                        'port': app.port,
                        'target_port': app.port
                    }]
                }
            }
        }
        
        return resources

# Register the output format
from output_formats.terraform import TerraformOutput

app.register_output_format('terraform', TerraformOutput())
app.generate().to_terraform('./terraform/')
```

### Argo Workflows Output

```python
# output_formats/argo_workflows.py
from k8s_gen import OutputFormat

class ArgoWorkflowsOutput(OutputFormat):
    """Generate Argo Workflows from K8s-Gen DSL."""
    
    def generate(self, jobs, output_path):
        """Generate Argo Workflow templates."""
        workflow = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'Workflow',
            'metadata': {
                'generateName': 'k8s-gen-workflow-'
            },
            'spec': {
                'entrypoint': 'main',
                'templates': self._generate_templates(jobs)
            }
        }
        
        self._write_yaml_file(workflow, output_path)
    
    def _generate_templates(self, jobs):
        """Generate workflow templates from jobs."""
        templates = []
        
        # Main template
        templates.append({
            'name': 'main',
            'dag': {
                'tasks': [
                    {
                        'name': job.name,
                        'template': job.name
                    } for job in jobs
                ]
            }
        })
        
        # Job templates
        for job in jobs:
            templates.append({
                'name': job.name,
                'container': {
                    'image': job.image,
                    'command': job.command,
                    'resources': {
                        'requests': {
                            'cpu': job.resources.get('cpu', '100m'),
                            'memory': job.resources.get('memory', '128Mi')
                        }
                    }
                }
            })
        
        return templates

# Usage
from output_formats.argo_workflows import ArgoWorkflowsOutput

workflow_output = ArgoWorkflowsOutput()
jobs = [migration_job, processing_job, cleanup_job]
workflow_output.generate(jobs, './workflows/pipeline.yaml')
```

## Plugin Registry

### Community Plugins

K8s-Gen maintains a registry of community-contributed plugins:

```python
# Install community plugins
from k8s_gen import PluginRegistry

registry = PluginRegistry()

# Database plugins
registry.install("database-cluster")     # Multi-node database clusters
registry.install("database-backup")      # Automated backup solutions
registry.install("database-migration")   # Schema migration tools

# Monitoring plugins  
registry.install("prometheus-stack")     # Complete Prometheus monitoring
registry.install("grafana-dashboards")   # Pre-built Grafana dashboards
registry.install("alerting-rules")       # Common alerting rules

# Security plugins
registry.install("rbac-generator")       # RBAC policy generator
registry.install("network-policies")     # Network security policies
registry.install("pod-security")         # Pod security standards

# CI/CD plugins
registry.install("gitops-integration")   # ArgoCD/Flux integration
registry.install("pipeline-generator")   # CI/CD pipeline generation
registry.install("deployment-strategies") # Advanced deployment patterns

# Cloud provider plugins
registry.install("cloud-integration")    # Multi-cloud resource integration
registry.install("service-mesh")         # Istio/Linkerd integration
registry.install("ingress-controllers")  # Various ingress implementations
```

### Plugin Metadata

```yaml
# Plugin metadata example (plugin.yaml)
name: database-cluster
version: 1.2.0
description: "Automated database clustering with failover and backups"
author: "Platform Team"
repository: "https://github.com/company/k8s-gen-database-plugin"
license: "MIT"
k8s_gen_version: ">=1.0.0"

dependencies:
  - name: "backup-plugin"
    version: ">=1.0.0"

categories:
  - database
  - stateful
  - high-availability

features:
  - automatic_failover
  - backup_automation
  - monitoring_integration
  - multi_cloud_support

configuration:
  required:
    - cluster_size
    - storage_size
  optional:
    - backup_schedule
    - monitoring_enabled
    - ssl_enabled

examples:
  - name: "Basic cluster"
    code: |
      db = DatabaseCluster("app-db")
        .cluster_size(3)
        .storage("100Gi")
        .backup_schedule("0 2 * * *")
  
  - name: "High availability"
    code: |
      db = DatabaseCluster("prod-db")
        .cluster_size(5)
        .high_availability(True)
        .cross_region_replication(True)
        .monitoring(True)
```

This extension system makes K8s-Gen highly customizable while maintaining the simplicity and elegance of the core DSL. Organizations can create their own plugins for specific needs while benefiting from community-contributed solutions. 