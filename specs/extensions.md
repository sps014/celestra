# Extensions and Customization

Guide to extending K8s-Gen with plugins, custom builders, and advanced customization options.

## Plugin System

The K8s-Gen plugin system allows you to extend functionality without modifying the core codebase.

### Plugin Architecture

```python
from k8s_gen.plugins import Plugin

class BasePlugin(Plugin):
    def __init__(self, config=None):
        self.config = config or {}
    
    def apply(self, app):
        """Apply plugin modifications to the application configuration"""
        raise NotImplementedError("Plugins must implement apply method")
    
    def validate(self, app_config):
        """Validate plugin-specific configuration"""
        return []  # Return list of validation errors
    
    def generate_resources(self, app_config):
        """Generate additional Kubernetes resources"""
        return []  # Return list of additional resources
```

### Creating Custom Plugins

#### Example: Custom Logging Plugin

```python
from k8s_gen.plugins import Plugin
from k8s_gen import Companion, ConfigMap

class CustomLogPlugin(Plugin):
    """Plugin to add standardized logging sidecar to all applications"""
    
    def __init__(self, config):
        super().__init__(config)
        self.log_level = config.get('log_level', 'INFO')
        self.log_format = config.get('log_format', 'json')
        self.output_destination = config.get('output', 'stdout')
    
    def apply(self, app):
        # Add logging sidecar
        log_collector = (Companion("log-collector")
            .image("fluent/fluent-bit:latest")
            .type("sidecar")
            .mount_shared_volume("/var/log")
            .environment({
                "LOG_LEVEL": self.log_level,
                "LOG_FORMAT": self.log_format,
                "OUTPUT": self.output_destination
            }))
        
        app.add_companion(log_collector)
        
        # Add logging configuration
        log_config = (ConfigMap("logging-config")
            .add("fluent-bit.conf", self._generate_fluent_bit_config())
            .mount_path("/fluent-bit/etc"))
        
        app.add_config([log_config])
    
    def _generate_fluent_bit_config(self):
        return f"""
[SERVICE]
    Flush         1
    Log_Level     {self.log_level.lower()}
    Daemon        off
    Parsers_File  parsers.conf

[INPUT]
    Name              tail
    Path              /var/log/*.log
    Parser            {self.log_format}
    Tag               app.*

[OUTPUT]
    Name              {self.output_destination}
    Match             *
    Format            {self.log_format}
"""

# Usage
app.use_plugin(
    CustomLogPlugin(config={
        "log_level": "INFO",
        "log_format": "json",
        "output": "elasticsearch"
    })
)
```

#### Example: Monitoring Plugin

```python
class PrometheusPlugin(Plugin):
    """Plugin to add Prometheus monitoring to applications"""
    
    def apply(self, app):
        # Add Prometheus annotations
        app._config.setdefault('annotations', {}).update({
            'prometheus.io/scrape': 'true',
            'prometheus.io/port': str(self.config.get('metrics_port', 8080)),
            'prometheus.io/path': self.config.get('metrics_path', '/metrics')
        })
        
        # Add metrics endpoint to health checks
        if hasattr(app, 'health'):
            app.health().add_metrics_endpoint(
                path=self.config.get('metrics_path', '/metrics'),
                port=self.config.get('metrics_port', 8080)
            )
    
    def generate_resources(self, app_config):
        # Generate ServiceMonitor for Prometheus Operator
        service_monitor = {
            'apiVersion': 'monitoring.coreos.com/v1',
            'kind': 'ServiceMonitor',
            'metadata': {
                'name': f"{app_config['name']}-metrics",
                'labels': {'app': app_config['name']}
            },
            'spec': {
                'selector': {
                    'matchLabels': {'app': app_config['name']}
                },
                'endpoints': [{
                    'port': 'http',
                    'path': self.config.get('metrics_path', '/metrics'),
                    'interval': self.config.get('scrape_interval', '30s')
                }]
            }
        }
        return [service_monitor]
```

#### Example: Security Plugin

```python
class SecurityHardeningPlugin(Plugin):
    """Plugin to apply security best practices"""
    
    def apply(self, app):
        # Apply security context
        security_context = {
            'runAsNonRoot': True,
            'runAsUser': 1000,
            'fsGroup': 2000,
            'readOnlyRootFilesystem': True,
            'allowPrivilegeEscalation': False,
            'capabilities': {
                'drop': ['ALL']
            }
        }
        
        app._config['security_context'] = security_context
        
        # Add network policies
        if self.config.get('network_isolation', True):
            self._add_network_policy(app)
        
        # Add pod security policy
        if self.config.get('pod_security_policy', True):
            self._add_pod_security_policy(app)
    
    def _add_network_policy(self, app):
        # Implementation for network policy
        pass
    
    def _add_pod_security_policy(self, app):
        # Implementation for pod security policy
        pass
```

### Plugin Registration

#### Auto-Discovery

Plugins can be automatically discovered using entry points:

```python
# setup.py
setup(
    name="my-k8s-gen-plugin",
    entry_points={
        'k8s_gen.plugins': [
            'logging = my_plugin.logging:CustomLogPlugin',
            'monitoring = my_plugin.monitoring:PrometheusPlugin',
        ]
    }
)
```

#### Manual Registration

```python
from k8s_gen import PluginManager

plugin_manager = PluginManager()
plugin_manager.register_plugin(CustomLogPlugin(config))
plugin_manager.register_plugin(PrometheusPlugin(config))

# Apply all registered plugins
plugin_manager.apply_plugins(app)
```

## Custom Builders

Extend the DSL with domain-specific builders for specialized workloads.

### Machine Learning Workload Builder

```python
class MLWorkloadBuilder(BaseBuilder):
    """Builder for machine learning workloads with GPU support"""
    
    def gpu_resources(self, gpu_count, gpu_type="nvidia.com/gpu"):
        return self._set('gpu', {
            'count': gpu_count, 
            'type': gpu_type
        })
    
    def model_storage(self, model_path, size="100Gi"):
        return self._set('model_storage', {
            'path': model_path, 
            'size': size
        })
    
    def training_dataset(self, dataset_config):
        return self._set('dataset', dataset_config)
    
    def distributed_training(self, workers=1, parameter_servers=1):
        return self._set('distributed', {
            'workers': workers,
            'parameter_servers': parameter_servers
        })
    
    def tensorboard(self, enabled=True, port=6006):
        if enabled:
            return self._set('tensorboard', {
                'enabled': True,
                'port': port
            })
        return self
    
    def model_serving(self, serving_config):
        return self._set('serving', serving_config)

# Usage
ml_app = (App("model-training")
    .image("tensorflow/tensorflow:latest-gpu")
    .extend_with(MLWorkloadBuilder())
    .gpu_resources(2)
    .model_storage("/models", "200Gi")
    .training_dataset({
        "source": "s3://my-bucket/training-data",
        "format": "tfrecord"
    })
    .distributed_training(workers=4, parameter_servers=2)
    .tensorboard(enabled=True)
    .model_serving({
        "framework": "tensorflow-serving",
        "model_name": "my_model",
        "version": "1"
    }))
```

### Data Pipeline Builder

```python
class DataPipelineBuilder(BaseBuilder):
    """Builder for data processing pipelines"""
    
    def data_source(self, source_type, config):
        sources = self._config.get('data_sources', [])
        sources.append({
            'type': source_type,
            'config': config
        })
        return self._set('data_sources', sources)
    
    def data_sink(self, sink_type, config):
        sinks = self._config.get('data_sinks', [])
        sinks.append({
            'type': sink_type,
            'config': config
        })
        return self._set('data_sinks', sinks)
    
    def processing_step(self, step_name, config):
        steps = self._config.get('processing_steps', [])
        steps.append({
            'name': step_name,
            'config': config
        })
        return self._set('processing_steps', steps)
    
    def batch_schedule(self, cron_expression):
        return self._set('batch_schedule', cron_expression)
    
    def streaming_config(self, window_size, watermark):
        return self._set('streaming', {
            'window_size': window_size,
            'watermark': watermark
        })
    
    def retry_policy(self, max_retries=3, backoff_factor=2):
        return self._set('retry_policy', {
            'max_retries': max_retries,
            'backoff_factor': backoff_factor
        })

# Usage
pipeline = (App("data-pipeline")
    .image("apache/spark:latest")
    .extend_with(DataPipelineBuilder())
    .data_source("kafka", {
        "brokers": ["kafka1:9092", "kafka2:9092"],
        "topic": "raw-events"
    })
    .processing_step("cleansing", {
        "remove_duplicates": True,
        "validate_schema": True
    })
    .processing_step("enrichment", {
        "lookup_table": "user_profiles",
        "join_key": "user_id"
    })
    .data_sink("s3", {
        "bucket": "processed-data",
        "format": "parquet",
        "partition_by": ["date", "region"]
    })
    .streaming_config(window_size="5m", watermark="1m")
    .retry_policy(max_retries=5))
```

### IoT Workload Builder

```python
class IoTWorkloadBuilder(BaseBuilder):
    """Builder for IoT applications"""
    
    def device_gateway(self, protocol, port):
        gateways = self._config.get('device_gateways', [])
        gateways.append({
            'protocol': protocol,
            'port': port
        })
        return self._set('device_gateways', gateways)
    
    def device_registry(self, registry_type, config):
        return self._set('device_registry', {
            'type': registry_type,
            'config': config
        })
    
    def telemetry_processing(self, processing_config):
        return self._set('telemetry_processing', processing_config)
    
    def edge_deployment(self, edge_config):
        return self._set('edge_deployment', edge_config)
    
    def device_authentication(self, auth_config):
        return self._set('device_auth', auth_config)

# Usage
iot_app = (App("iot-platform")
    .image("iot-platform:latest")
    .extend_with(IoTWorkloadBuilder())
    .device_gateway("mqtt", 1883)
    .device_gateway("coap", 5683)
    .device_registry("aws-iot", {
        "region": "us-east-1",
        "thing_type": "sensor"
    })
    .telemetry_processing({
        "aggregation_window": "1m",
        "metrics": ["temperature", "humidity", "pressure"]
    })
    .edge_deployment({
        "enabled": True,
        "edge_locations": ["factory-1", "warehouse-2"]
    }))
```

## Template Customization

### Custom Templates

Create custom templates for specific use cases:

```python
# Custom template for ML workloads
# templates/ml/training-job.yaml.j2
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ name }}-training
  labels:
    app: {{ name }}
    component: training
spec:
  template:
    spec:
      restartPolicy: Never
      containers:
      - name: trainer
        image: {{ image }}
        {% if gpu.count > 0 %}
        resources:
          limits:
            {{ gpu.type }}: {{ gpu.count }}
        {% endif %}
        env:
        - name: MODEL_DIR
          value: {{ model_storage.path }}
        - name: DATASET_PATH
          value: {{ dataset.source }}
        volumeMounts:
        - name: model-storage
          mountPath: {{ model_storage.path }}
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: {{ name }}-model-storage
```

### Template Hooks

Add custom processing before and after template rendering:

```python
class TemplateProcessor:
    def __init__(self):
        self.pre_render_hooks = []
        self.post_render_hooks = []
    
    def add_pre_render_hook(self, hook_func):
        self.pre_render_hooks.append(hook_func)
    
    def add_post_render_hook(self, hook_func):
        self.post_render_hooks.append(hook_func)
    
    def render(self, template, context):
        # Apply pre-render hooks
        for hook in self.pre_render_hooks:
            context = hook(context)
        
        # Render template
        result = template.render(context)
        
        # Apply post-render hooks
        for hook in self.post_render_hooks:
            result = hook(result)
        
        return result

# Custom hooks
def add_company_labels(context):
    """Add company-specific labels to all resources"""
    context.setdefault('labels', {}).update({
        'company': 'acme-corp',
        'cost-center': 'engineering',
        'environment': context.get('environment', 'development')
    })
    return context

def optimize_resources(context):
    """Optimize resource requests based on environment"""
    if context.get('environment') == 'development':
        # Reduce resources for development
        if 'resources' in context:
            if 'requests' in context['resources']:
                context['resources']['requests']['cpu'] = '100m'
                context['resources']['requests']['memory'] = '128Mi'
    return context

# Register hooks
processor = TemplateProcessor()
processor.add_pre_render_hook(add_company_labels)
processor.add_pre_render_hook(optimize_resources)
```

## Configuration Extensions

### Environment-Specific Configurations

```python
class EnvironmentConfig:
    def __init__(self, base_config):
        self.base_config = base_config
        self.environment_overrides = {}
    
    def add_environment(self, env_name, overrides):
        self.environment_overrides[env_name] = overrides
    
    def get_config_for_environment(self, env_name):
        config = self.base_config.copy()
        if env_name in self.environment_overrides:
            config.update(self.environment_overrides[env_name])
        return config

# Usage
env_config = EnvironmentConfig({
    'replicas': 1,
    'resources': {'cpu': '100m', 'memory': '256Mi'}
})

env_config.add_environment('staging', {
    'replicas': 2,
    'resources': {'cpu': '500m', 'memory': '512Mi'}
})

env_config.add_environment('production', {
    'replicas': 5,
    'resources': {'cpu': '1000m', 'memory': '1Gi'},
    'auto_scaling': True
})
```

### Feature Flags Integration

```python
class FeatureFlagExtension:
    def __init__(self, provider, config):
        self.provider = provider
        self.config = config
    
    def is_enabled(self, flag_name, context=None):
        # Integration with feature flag providers
        if self.provider == 'launchdarkly':
            return self._check_launchdarkly(flag_name, context)
        elif self.provider == 'split':
            return self._check_split(flag_name, context)
        return False
    
    def apply_feature_flags(self, app_config):
        # Apply feature flags to configuration
        if self.is_enabled('new_monitoring_stack'):
            app_config['monitoring']['provider'] = 'prometheus'
        
        if self.is_enabled('enhanced_security'):
            app_config['security']['strict_mode'] = True
        
        return app_config
```

## Validation Extensions

### Custom Validators

```python
class CustomValidator:
    def __init__(self):
        self.rules = []
    
    def add_rule(self, rule_func, severity='error'):
        self.rules.append({
            'func': rule_func,
            'severity': severity
        })
    
    def validate(self, config):
        results = []
        for rule in self.rules:
            try:
                result = rule['func'](config)
                if result:
                    results.append({
                        'severity': rule['severity'],
                        'message': result
                    })
            except Exception as e:
                results.append({
                    'severity': 'error',
                    'message': f"Validation rule failed: {str(e)}"
                })
        return results

# Custom validation rules
def check_resource_limits(config):
    """Ensure all containers have resource limits"""
    if 'resources' not in config:
        return "Resources must be specified for all containers"
    
    if 'limits' not in config['resources']:
        return "Resource limits must be specified"
    
    return None

def check_security_context(config):
    """Ensure security context is properly configured"""
    if 'security_context' not in config:
        return "Security context must be specified"
    
    security = config['security_context']
    if not security.get('runAsNonRoot', False):
        return "Containers should run as non-root user"
    
    return None

def check_image_tags(config):
    """Ensure container images have specific tags (not latest)"""
    image = config.get('image', '')
    if image.endswith(':latest') or ':' not in image:
        return "Container images should use specific tags, not 'latest'"
    
    return None

# Register validation rules
validator = CustomValidator()
validator.add_rule(check_resource_limits, 'error')
validator.add_rule(check_security_context, 'warning')
validator.add_rule(check_image_tags, 'warning')
```

## Output Format Extensions

### Custom Output Formats

```python
class TerraformGenerator:
    """Generate Terraform modules from DSL configuration"""
    
    def generate(self, app_config):
        terraform_config = {
            'terraform': {
                'required_providers': {
                    'kubernetes': {
                        'source': 'hashicorp/kubernetes',
                        'version': '~> 2.0'
                    }
                }
            },
            'resource': self._generate_resources(app_config)
        }
        return self._format_terraform(terraform_config)
    
    def _generate_resources(self, app_config):
        resources = {}
        
        # Generate Kubernetes deployment resource
        resources['kubernetes_deployment'] = {
            app_config['name']: {
                'metadata': {
                    'name': app_config['name'],
                    'labels': {'app': app_config['name']}
                },
                'spec': {
                    'replicas': app_config.get('replicas', 1),
                    'selector': {
                        'match_labels': {'app': app_config['name']}
                    },
                    'template': self._generate_pod_template(app_config)
                }
            }
        }
        
        return resources
    
    def _format_terraform(self, config):
        # Convert to HCL format
        pass

class ArgoWorkflowGenerator:
    """Generate Argo Workflows for ML pipelines"""
    
    def generate(self, pipeline_config):
        workflow = {
            'apiVersion': 'argoproj.io/v1alpha1',
            'kind': 'Workflow',
            'metadata': {
                'name': pipeline_config['name']
            },
            'spec': {
                'entrypoint': 'pipeline',
                'templates': self._generate_templates(pipeline_config)
            }
        }
        return workflow
```

## Integration Extensions

### CI/CD Integration

```python
class GitHubActionsExtension:
    """Generate GitHub Actions workflows"""
    
    def generate_workflow(self, app_config):
        workflow = {
            'name': f"Deploy {app_config['name']}",
            'on': {
                'push': {
                    'branches': ['main']
                }
            },
            'jobs': {
                'deploy': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {
                            'uses': 'actions/checkout@v2'
                        },
                        {
                            'name': 'Setup K8s-Gen',
                            'run': 'pip install k8s-gen'
                        },
                        {
                            'name': 'Generate manifests',
                            'run': 'k8s-gen generate app.py --output ./k8s/'
                        },
                        {
                            'name': 'Deploy to Kubernetes',
                            'run': 'kubectl apply -f ./k8s/'
                        }
                    ]
                }
            }
        }
        return workflow

class JenkinsExtension:
    """Generate Jenkins pipeline"""
    
    def generate_pipeline(self, app_config):
        pipeline = f"""
pipeline {{
    agent any
    
    stages {{
        stage('Generate') {{
            steps {{
                sh 'k8s-gen generate app.py --output ./k8s/'
            }}
        }}
        
        stage('Validate') {{
            steps {{
                sh 'k8s-gen validate app.py'
            }}
        }}
        
        stage('Deploy') {{
            steps {{
                sh 'kubectl apply -f ./k8s/'
            }}
        }}
    }}
}}
"""
        return pipeline
```

## Advanced Customization

### Dynamic Configuration

```python
class DynamicConfigBuilder:
    """Build configuration dynamically based on runtime conditions"""
    
    def __init__(self):
        self.conditions = []
        self.actions = []
    
    def when(self, condition_func):
        self.conditions.append(condition_func)
        return self
    
    def then(self, action_func):
        self.actions.append(action_func)
        return self
    
    def apply(self, app_config, context):
        for condition, action in zip(self.conditions, self.actions):
            if condition(context):
                app_config = action(app_config)
        return app_config

# Usage
dynamic_config = (DynamicConfigBuilder()
    .when(lambda ctx: ctx['environment'] == 'production')
    .then(lambda cfg: cfg.update({'replicas': 5}) or cfg)
    .when(lambda ctx: ctx['region'] == 'us-east-1')
    .then(lambda cfg: cfg.update({'availability_zones': ['us-east-1a', 'us-east-1b']}) or cfg))
```

### Resource Optimization

```python
class ResourceOptimizer:
    """Optimize resource allocation based on historical usage"""
    
    def __init__(self, metrics_source):
        self.metrics_source = metrics_source
    
    def optimize(self, app_config):
        # Get historical resource usage
        usage_data = self.metrics_source.get_usage_data(
            app_name=app_config['name'],
            period='30d'
        )
        
        # Calculate optimal resource requests
        optimal_cpu = self._calculate_optimal_cpu(usage_data)
        optimal_memory = self._calculate_optimal_memory(usage_data)
        
        # Update configuration
        app_config['resources'] = {
            'requests': {
                'cpu': optimal_cpu,
                'memory': optimal_memory
            },
            'limits': {
                'cpu': optimal_cpu * 1.5,  # 50% headroom
                'memory': optimal_memory * 1.2  # 20% headroom
            }
        }
        
        return app_config
```

## Plugin Distribution

### Plugin Packaging

```python
# setup.py for a plugin package
from setuptools import setup, find_packages

setup(
    name="k8s-gen-monitoring-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "k8s-gen>=1.0.0",
    ],
    entry_points={
        'k8s_gen.plugins': [
            'prometheus = k8s_gen_monitoring.prometheus:PrometheusPlugin',
            'grafana = k8s_gen_monitoring.grafana:GrafanaPlugin',
            'jaeger = k8s_gen_monitoring.jaeger:JaegerPlugin',
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Monitoring plugins for K8s-Gen",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/k8s-gen-monitoring-plugin",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
```

### Plugin Registry

Create a centralized plugin registry for easy discovery:

```yaml
# plugin-registry.yaml
plugins:
  monitoring:
    prometheus:
      name: "k8s-gen-prometheus-plugin"
      version: "1.0.0"
      description: "Prometheus monitoring integration"
      repository: "https://github.com/k8s-gen/prometheus-plugin"
    
  security:
    falco:
      name: "k8s-gen-falco-plugin"
      version: "1.2.0"
      description: "Falco security monitoring"
      repository: "https://github.com/k8s-gen/falco-plugin"
  
  databases:
    postgres:
      name: "k8s-gen-postgres-plugin"
      version: "2.0.0"
      description: "PostgreSQL database integration"
      repository: "https://github.com/k8s-gen/postgres-plugin"
```

This extensible architecture allows K8s-Gen to grow with the community and adapt to specific organizational needs while maintaining a clean core API. 