# Implementation Architecture

Technical details of the K8s-Gen DSL implementation including builder classes, templates, and validation.

## Core Builder Classes

### Base Builder Pattern

The foundation of the DSL is a base builder class that provides common functionality:

```python
# Base builder class
class BaseBuilder:
    def __init__(self, name):
        self.name = name
        self._config = {}
    
    def _set(self, key, value):
        self._config[key] = value
        return self
    
    def build(self):
        return self._config
```

### App Builder

The main stateless application builder:

```python
# App builder
class App(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def port(self, port_number):
        return self._set('port', port_number)
    
    def environment(self, env_vars):
        return self._set('environment', env_vars)
    
    def resources(self, cpu=None, memory=None, cpu_limit=None, memory_limit=None):
        resources = {}
        if cpu or memory:
            resources['requests'] = {}
            if cpu:
                resources['requests']['cpu'] = cpu
            if memory:
                resources['requests']['memory'] = memory
        if cpu_limit or memory_limit:
            resources['limits'] = {}
            if cpu_limit:
                resources['limits']['cpu'] = cpu_limit
            if memory_limit:
                resources['limits']['memory'] = memory_limit
        return self._set('resources', resources)
    
    def scale(self, replicas=None, auto_scale_on_cpu=None, max_replicas=None):
        scaling = {'replicas': replicas}
        if auto_scale_on_cpu:
            scaling['auto_scale'] = {
                'metric': 'cpu',
                'target': auto_scale_on_cpu,
                'max_replicas': max_replicas or replicas * 3
            }
        return self._set('scaling', scaling)
    
    def expose(self, external_access=False, domain=None, port=None):
        exposure = {
            'type': 'LoadBalancer' if external_access else 'ClusterIP',
            'port': port or self._config.get('port', 80)
        }
        if domain:
            exposure['domain'] = domain
        return self._set('exposure', exposure)
    
    def connect_to(self, services):
        return self._set('dependencies', services)
    
    def add_secrets(self, secrets):
        return self._set('secrets', secrets)
    
    def add_config(self, configs):
        return self._set('configs', configs)
    
    def add_jobs(self, jobs):
        return self._set('jobs', jobs)
    
    def lifecycle(self, lifecycle_config):
        return self._set('lifecycle', lifecycle_config)
    
    def health(self, health_config):
        return self._set('health', health_config)
    
    def security(self, security_config):
        return self._set('security', security_config)
    
    def rbac(self, **rbac_config):
        return self._set('rbac', rbac_config)
    
    def observability(self, observability_config):
        return self._set('observability', observability_config)
```

### StatefulApp Builder

Builder for stateful applications requiring persistent storage:

```python
# StatefulApp builder
class StatefulApp(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def port(self, port_number):
        return self._set('port', port_number)
    
    def storage(self, size):
        return self._set('storage_size', size)
    
    def replicas(self, count):
        return self._set('replicas', count)
    
    def environment(self, env_vars):
        return self._set('environment', env_vars)
    
    def backup_schedule(self, cron_expression):
        return self._set('backup_schedule', cron_expression)
    
    def topics(self, topic_list):
        return self._set('topics', topic_list)
    
    def retention_hours(self, hours):
        return self._set('retention_hours', hours)
    
    def cluster_mode(self):
        return self._set('cluster_mode', True)
    
    def persistence(self, save_interval):
        return self._set('persistence', save_interval)
```

### Secret Builder

Secure secrets management:

```python
# Secret builder
class Secret(BaseBuilder):
    def add(self, key, value):
        if 'data' not in self._config:
            self._config['data'] = {}
        self._config['data'][key] = value
        return self
    
    def from_env_file(self, file_path):
        return self._set('env_file', file_path)
    
    def from_vault(self, path, mapping):
        return self._set('vault_path', path).set('vault_mapping', mapping)
    
    def from_aws_parameter_store(self, path):
        return self._set('aws_parameter_store', path)
    
    def from_aws_secrets_manager(self, secret_name):
        return self._set('aws_secrets_manager', secret_name)
    
    def mount_as_env_vars(self, prefix=""):
        return self._set('mount_type', 'env').set('env_prefix', prefix)
    
    def mount_path(self, path):
        return self._set('mount_path', path)
    
    def type(self, secret_type):
        return self._set('type', secret_type)
    
    def generate_password(self, key, length=32):
        return self._set(f'generate_{key}', {'type': 'password', 'length': length})
    
    def generate_rsa_key_pair(self, private_key, public_key):
        return self._set('generate_rsa', {'private': private_key, 'public': public_key})
    
    def generate_random(self, key, length=64):
        return self._set(f'generate_{key}', {'type': 'random', 'length': length})
```

### ConfigMap Builder

Flexible configuration management:

```python
# ConfigMap builder
class ConfigMap(BaseBuilder):
    def add(self, key, value):
        if 'data' not in self._config:
            self._config['data'] = {}
        self._config['data'][key] = value
        return self
    
    def from_file(self, key, file_path):
        return self._set(f'file_{key}', file_path)
    
    def from_directory(self, directory_path):
        return self._set('directory', directory_path)
    
    def mount_path(self, path):
        return self._set('mount_path', path)
    
    def mount_as_env_vars(self):
        return self._set('mount_type', 'env')
    
    def file_mode(self, mode):
        return self._set('file_mode', mode)
    
    def add_json(self, key, data):
        import json
        return self.add(f'{key}.json', json.dumps(data, indent=2))
    
    def add_yaml(self, key, data):
        import yaml
        return self.add(f'{key}.yaml', yaml.dump(data))
    
    def add_properties(self, key, data):
        props = '\n'.join([f'{k}={v}' for k, v in data.items()])
        return self.add(key, props)
    
    def add_ini(self, key, data):
        import configparser
        import io
        config = configparser.ConfigParser()
        for section, values in data.items():
            config[section] = values
        output = io.StringIO()
        config.write(output)
        return self.add(key, output.getvalue())
    
    def add_toml(self, key, data):
        import toml
        return self.add(key, toml.dumps(data))
    
    def from_template(self, template_file, variables):
        return self._set('template', {'file': template_file, 'vars': variables})
    
    def enable_hot_reload(self, interval="30s"):
        return self._set('hot_reload', {'enabled': True, 'interval': interval})
    
    def on_change(self, restart_pods=False):
        return self._set('on_change', {'restart_pods': restart_pods})
```

### Job Builder

Batch processing and one-time tasks:

```python
# Job builder
class Job(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def command(self, command_list):
        return self._set('command', command_list)
    
    def parallelism(self, count):
        return self._set('parallelism', count)
    
    def completions(self, count):
        return self._set('completions', count)
    
    def timeout(self, duration):
        return self._set('timeout', duration)
    
    def backoff_limit(self, limit):
        return self._set('backoff_limit', limit)
    
    def run_once(self):
        return self.completions(1).parallelism(1)
    
    def depends_on(self, services):
        return self._set('depends_on', services)
    
    def environment(self, env_vars):
        return self._set('environment', env_vars)
    
    def resources(self, cpu=None, memory=None):
        resources = {}
        if cpu or memory:
            resources['requests'] = {}
            if cpu:
                resources['requests']['cpu'] = cpu
            if memory:
                resources['requests']['memory'] = memory
        return self._set('resources', resources)
    
    def on_success(self, cleanup=False):
        return self._set('on_success', {'cleanup': cleanup})
    
    def on_failure(self, restart_policy="Never"):
        return self._set('on_failure', {'restart_policy': restart_policy})
```

### CronJob Builder

Scheduled tasks and recurring jobs:

```python
# CronJob builder
class CronJob(BaseBuilder):
    def image(self, image_name):
        return self._set('image', image_name)
    
    def schedule(self, cron_expression):
        return self._set('schedule', cron_expression)
    
    def command(self, command_list):
        return self._set('command', command_list)
    
    def environment(self, env_vars):
        return self._set('environment', env_vars)
    
    def retention_limit(self, successful=3, failed=1):
        return self._set('successful_jobs_history_limit', successful).set('failed_jobs_history_limit', failed)
    
    def timezone(self, tz):
        return self._set('timezone', tz)
    
    def suspend(self, suspended):
        return self._set('suspend', suspended)
    
    def concurrent_policy(self, policy):
        return self._set('concurrency_policy', policy)
    
    def volumes(self, volume_list):
        return self._set('volumes', volume_list)
```

### Ingress Builder

Advanced HTTP routing and traffic management:

```python
# Ingress builder
class Ingress(BaseBuilder):
    def host(self, hostname):
        return self._set('host', hostname)
    
    def path(self, path, service, port, rewrite=None):
        if 'paths' not in self._config:
            self._config['paths'] = []
        self._config['paths'].append({
            'path': path, 'service': service, 'port': port, 'rewrite': rewrite
        })
        return self
    
    def ssl_certificate(self, cert_manager=None):
        return self._set('ssl', True).set('cert_manager', cert_manager)
    
    def rate_limiting(self, requests_per_minute, burst=None):
        return self._set('rate_limit', requests_per_minute).set('rate_burst', burst)
    
    def cors(self, origins=None, methods=None, headers=None):
        cors_config = {}
        if origins:
            cors_config['origins'] = origins
        if methods:
            cors_config['methods'] = methods
        if headers:
            cors_config['headers'] = headers
        return self._set('cors', cors_config)
    
    def middleware(self, middleware_list):
        return self._set('middleware', middleware_list)
    
    def load_balancer_class(self, lb_class):
        return self._set('load_balancer_class', lb_class)
    
    def ip_whitelist(self, ip_ranges):
        return self._set('ip_whitelist', ip_ranges)
    
    def redirect_http_to_https(self):
        return self._set('redirect_https', True)
    
    def custom_headers(self, headers):
        return self._set('custom_headers', headers)
    
    def timeout(self, connect=None, read=None, send=None):
        timeouts = {}
        if connect:
            timeouts['connect'] = connect
        if read:
            timeouts['read'] = read
        if send:
            timeouts['send'] = send
        return self._set('timeouts', timeouts)
    
    def annotations(self, annotation_dict):
        return self._set('annotations', annotation_dict)
```

## Template System

### Jinja2 Template Engine

The DSL uses Jinja2 templates for generating Kubernetes manifests:

```python
# Jinja2 templates for Kubernetes manifests
class TemplateRenderer:
    def __init__(self):
        self.env = jinja2.Environment(
            loader=jinja2.PackageLoader('k8s_gen', 'templates')
        )
    
    def render_deployment(self, app_config):
        template = self.env.get_template('deployment.yaml.j2')
        return template.render(app_config)
    
    def render_service(self, service_config):
        template = self.env.get_template('service.yaml.j2')
        return template.render(service_config)
    
    def render_configmap(self, config_map_config):
        template = self.env.get_template('configmap.yaml.j2')
        return template.render(config_map_config)
    
    def render_docker_compose(self, compose_config):
        template = self.env.get_template('docker-compose.yml.j2')
        return template.render(compose_config)
    
    def render_docker_compose_override(self, override_config):
        template = self.env.get_template('docker-compose.override.yml.j2')
        return template.render(override_config)
    
    def render_secret(self, secret_config):
        template = self.env.get_template('secret.yaml.j2')
        return template.render(secret_config)
    
    def render_job(self, job_config):
        template = self.env.get_template('job.yaml.j2')
        return template.render(job_config)
    
    def render_cronjob(self, cronjob_config):
        template = self.env.get_template('cronjob.yaml.j2')
        return template.render(cronjob_config)
    
    def render_ingress(self, ingress_config):
        template = self.env.get_template('ingress.yaml.j2')
        return template.render(ingress_config)
    
    def render_rbac(self, rbac_config):
        templates = ['serviceaccount.yaml.j2', 'role.yaml.j2', 'rolebinding.yaml.j2']
        return [self.env.get_template(t).render(rbac_config) for t in templates]
```

### Template Structure

Templates are organized in a hierarchical structure:

```
templates/
├── kubernetes/
│   ├── deployment.yaml.j2
│   ├── service.yaml.j2
│   ├── configmap.yaml.j2
│   ├── secret.yaml.j2
│   ├── job.yaml.j2
│   ├── cronjob.yaml.j2
│   ├── ingress.yaml.j2
│   ├── hpa.yaml.j2
│   ├── pvc.yaml.j2
│   ├── serviceaccount.yaml.j2
│   ├── role.yaml.j2
│   └── rolebinding.yaml.j2
├── docker-compose/
│   ├── docker-compose.yml.j2
│   └── docker-compose.override.yml.j2
├── helm/
│   ├── Chart.yaml.j2
│   ├── values.yaml.j2
│   └── templates/
└── kustomize/
    ├── kustomization.yaml.j2
    └── overlays/
```

### Example Template

Sample Deployment template (`deployment.yaml.j2`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ name }}
  labels:
    app: {{ name }}
    generated-by: k8s-gen
spec:
  replicas: {{ scaling.replicas | default(1) }}
  selector:
    matchLabels:
      app: {{ name }}
  template:
    metadata:
      labels:
        app: {{ name }}
    spec:
      {% if rbac.service_account %}
      serviceAccountName: {{ rbac.service_account }}
      {% endif %}
      containers:
      - name: {{ name }}
        image: {{ image }}
        {% if port %}
        ports:
        - containerPort: {{ port }}
          name: http
        {% endif %}
        {% if environment %}
        env:
        {% for key, value in environment.items() %}
        - name: {{ key }}
          value: "{{ value }}"
        {% endfor %}
        {% endif %}
        {% if secrets %}
        {% for secret in secrets %}
        {% if secret.mount_type == 'env' %}
        {% for key in secret.data.keys() %}
        - name: {{ secret.env_prefix }}{{ key | upper }}
          valueFrom:
            secretKeyRef:
              name: {{ secret.name }}
              key: {{ key }}
        {% endfor %}
        {% endif %}
        {% endfor %}
        {% endif %}
        {% if resources %}
        resources:
          {% if resources.requests %}
          requests:
            {% if resources.requests.cpu %}
            cpu: {{ resources.requests.cpu }}
            {% endif %}
            {% if resources.requests.memory %}
            memory: {{ resources.requests.memory }}
            {% endif %}
          {% endif %}
          {% if resources.limits %}
          limits:
            {% if resources.limits.cpu %}
            cpu: {{ resources.limits.cpu }}
            {% endif %}
            {% if resources.limits.memory %}
            memory: {{ resources.limits.memory }}
            {% endif %}
          {% endif %}
        {% endif %}
        {% if health %}
        {% if health.liveness_probe %}
        livenessProbe:
          httpGet:
            path: {{ health.liveness_probe.path | default('/') }}
            port: http
          initialDelaySeconds: {{ health.liveness_probe.initial_delay | default(30) }}
          periodSeconds: {{ health.liveness_probe.period | default(10) }}
        {% endif %}
        {% if health.readiness_probe %}
        readinessProbe:
          httpGet:
            path: {{ health.readiness_probe.path | default('/') }}
            port: http
          initialDelaySeconds: {{ health.readiness_probe.initial_delay | default(5) }}
          periodSeconds: {{ health.readiness_probe.period | default(5) }}
        {% endif %}
        {% endif %}
        {% if lifecycle %}
        lifecycle:
          {% if lifecycle.pre_stop %}
          preStop:
            {% if lifecycle.pre_stop.command %}
            exec:
              command: {{ lifecycle.pre_stop.command | tojson }}
            {% elif lifecycle.pre_stop.http %}
            httpGet:
              path: {{ lifecycle.pre_stop.http.path }}
              port: {{ lifecycle.pre_stop.http.port | default('http') }}
            {% endif %}
          {% endif %}
          {% if lifecycle.post_start %}
          postStart:
            {% if lifecycle.post_start.command %}
            exec:
              command: {{ lifecycle.post_start.command | tojson }}
            {% elif lifecycle.post_start.http %}
            httpGet:
              path: {{ lifecycle.post_start.http.path }}
              port: {{ lifecycle.post_start.http.port | default('http') }}
            {% endif %}
          {% endif %}
        {% endif %}
        {% if configs or secrets %}
        volumeMounts:
        {% for config in configs %}
        {% if config.mount_path %}
        - name: {{ config.name }}
          mountPath: {{ config.mount_path }}
          readOnly: true
        {% endif %}
        {% endfor %}
        {% for secret in secrets %}
        {% if secret.mount_path %}
        - name: {{ secret.name }}
          mountPath: {{ secret.mount_path }}
          readOnly: true
        {% endif %}
        {% endfor %}
        {% endif %}
      {% if lifecycle and lifecycle.termination_grace_period %}
      terminationGracePeriodSeconds: {{ lifecycle.termination_grace_period }}
      {% endif %}
      {% if configs or secrets %}
      volumes:
      {% for config in configs %}
      {% if config.mount_path %}
      - name: {{ config.name }}
        configMap:
          name: {{ config.name }}
          {% if config.file_mode %}
          defaultMode: {{ config.file_mode }}
          {% endif %}
      {% endif %}
      {% endfor %}
      {% for secret in secrets %}
      {% if secret.mount_path %}
      - name: {{ secret.name }}
        secret:
          secretName: {{ secret.name }}
      {% endif %}
      {% endfor %}
      {% endif %}
```

## Validation Engine

### Comprehensive Validation

The DSL includes extensive validation to catch errors early:

```python
class Validator:
    def validate_app(self, app_config):
        errors = []
        
        # Required fields validation
        if 'image' not in app_config:
            errors.append("App must specify a container image")
        
        # Resource validation
        if 'resources' in app_config:
            errors.extend(self._validate_resources(app_config['resources']))
        
        return ValidationResult(errors)
    
    def validate_stateful_app(self, stateful_config):
        errors = []
        
        # Stateful-specific validation
        if 'storage_size' not in stateful_config:
            errors.append("StatefulApp must specify storage size")
        
        if 'replicas' in stateful_config and stateful_config['replicas'] < 1:
            errors.append("StatefulApp must have at least 1 replica")
        
        return ValidationResult(errors)
    
    def validate_secret(self, secret_config):
        errors = []
        
        if 'data' not in secret_config or len(secret_config['data']) == 0:
            errors.append("Secret must contain at least one key-value pair")
        
        # Validate secret type
        valid_types = ['Opaque', 'kubernetes.io/tls', 'kubernetes.io/basic-auth']
        if 'type' in secret_config and secret_config['type'] not in valid_types:
            errors.append(f"Invalid secret type. Must be one of: {valid_types}")
        
        return ValidationResult(errors)
    
    def validate_job(self, job_config):
        errors = []
        
        if 'image' not in job_config:
            errors.append("Job must specify a container image")
        
        if 'parallelism' in job_config and job_config['parallelism'] < 1:
            errors.append("Job parallelism must be at least 1")
        
        if 'completions' in job_config and job_config['completions'] < 1:
            errors.append("Job completions must be at least 1")
        
        return ValidationResult(errors)
    
    def validate_cronjob(self, cronjob_config):
        errors = []
        
        if 'schedule' not in cronjob_config:
            errors.append("CronJob must specify a schedule")
        
        # Basic cron expression validation
        if 'schedule' in cronjob_config:
            schedule = cronjob_config['schedule']
            parts = schedule.split()
            if len(parts) != 5:
                errors.append("CronJob schedule must be a valid cron expression (5 fields)")
        
        return ValidationResult(errors)
    
    def validate_ingress(self, ingress_config):
        errors = []
        
        if 'host' not in ingress_config:
            errors.append("Ingress must specify a host")
        
        if 'paths' not in ingress_config or len(ingress_config['paths']) == 0:
            errors.append("Ingress must specify at least one path")
        
        # Validate paths
        for path_config in ingress_config.get('paths', []):
            if 'path' not in path_config or 'service' not in path_config:
                errors.append("Each ingress path must specify path and service")
        
        return ValidationResult(errors)
    
    def _validate_resources(self, resources):
        errors = []
        
        # Validate CPU format
        if 'requests' in resources and 'cpu' in resources['requests']:
            cpu = resources['requests']['cpu']
            if not self._is_valid_cpu(cpu):
                errors.append(f"Invalid CPU format: {cpu}")
        
        # Validate memory format
        if 'requests' in resources and 'memory' in resources['requests']:
            memory = resources['requests']['memory']
            if not self._is_valid_memory(memory):
                errors.append(f"Invalid memory format: {memory}")
        
        return errors
    
    def _is_valid_cpu(self, cpu):
        # Validate CPU format (e.g., "500m", "1", "1.5")
        import re
        return bool(re.match(r'^\d+(\.\d+)?[m]?$', str(cpu)))
    
    def _is_valid_memory(self, memory):
        # Validate memory format (e.g., "512Mi", "1Gi", "2G")
        import re
        return bool(re.match(r'^\d+[KMGTPE]?[i]?$', str(memory)))

class ValidationResult:
    def __init__(self, errors):
        self.errors = errors
        self.is_valid = len(errors) == 0
```

## Code Generation Pipeline

### Generation Process

The code generation process follows these steps:

1. **Configuration Validation** - Validate DSL configuration
2. **Template Selection** - Choose appropriate templates based on output format
3. **Data Transformation** - Transform DSL config to template variables
4. **Template Rendering** - Render templates with data
5. **Post-Processing** - Apply formatting and optimization
6. **Output Writing** - Write files to specified location

```python
class Generator:
    def __init__(self, app_config):
        self.app_config = app_config
        self.validator = Validator()
        self.renderer = TemplateRenderer()
    
    def generate(self):
        return GeneratorContext(self.app_config, self.validator, self.renderer)

class GeneratorContext:
    def __init__(self, app_config, validator, renderer):
        self.app_config = app_config
        self.validator = validator
        self.renderer = renderer
    
    def to_yaml(self, output_dir):
        # Validate configuration
        validation_result = self.validator.validate_app(self.app_config)
        if not validation_result.is_valid:
            raise ValidationError(validation_result.errors)
        
        # Generate Kubernetes manifests
        manifests = []
        
        # Deployment
        deployment = self.renderer.render_deployment(self.app_config)
        manifests.append(('deployment.yaml', deployment))
        
        # Service
        if self.app_config.get('port'):
            service = self.renderer.render_service(self.app_config)
            manifests.append(('service.yaml', service))
        
        # ConfigMaps
        for config in self.app_config.get('configs', []):
            configmap = self.renderer.render_configmap(config)
            manifests.append(f'configmap-{config.name}.yaml', configmap)
        
        # Secrets
        for secret in self.app_config.get('secrets', []):
            secret_manifest = self.renderer.render_secret(secret)
            manifests.append(f'secret-{secret.name}.yaml', secret_manifest)
        
        # Jobs
        for job in self.app_config.get('jobs', []):
            job_manifest = self.renderer.render_job(job)
            manifests.append(f'job-{job.name}.yaml', job_manifest)
        
        # Write manifests to files
        self._write_manifests(manifests, output_dir)
    
    def to_docker_compose(self, output_file, override_files=None):
        # Generate Docker Compose
        compose_config = self._transform_to_compose(self.app_config)
        compose_content = self.renderer.render_docker_compose(compose_config)
        
        # Write main compose file
        with open(output_file, 'w') as f:
            f.write(compose_content)
        
        # Generate override files if specified
        if override_files:
            for env, override_file in override_files.items():
                override_config = self._generate_override_config(env)
                override_content = self.renderer.render_docker_compose_override(override_config)
                with open(override_file, 'w') as f:
                    f.write(override_content)
    
    def to_helm_chart(self, chart_dir):
        # Generate Helm chart structure
        import os
        
        # Create chart directory
        os.makedirs(f"{chart_dir}/templates", exist_ok=True)
        
        # Generate Chart.yaml
        chart_yaml = self._generate_chart_yaml()
        with open(f"{chart_dir}/Chart.yaml", 'w') as f:
            f.write(chart_yaml)
        
        # Generate values.yaml
        values_yaml = self._generate_values_yaml()
        with open(f"{chart_dir}/values.yaml", 'w') as f:
            f.write(values_yaml)
        
        # Generate templates
        templates = self._generate_helm_templates()
        for template_name, content in templates.items():
            with open(f"{chart_dir}/templates/{template_name}", 'w') as f:
                f.write(content)
    
    def _write_manifests(self, manifests, output_dir):
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        for filename, content in manifests:
            with open(f"{output_dir}/{filename}", 'w') as f:
                f.write(content)
```

## Extension System

### Plugin Architecture

The DSL supports a plugin architecture for extensibility:

```python
class Plugin:
    def apply(self, app):
        raise NotImplementedError("Plugins must implement apply method")

class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register_plugin(self, plugin):
        self.plugins.append(plugin)
    
    def apply_plugins(self, app):
        for plugin in self.plugins:
            plugin.apply(app)
```

### Custom Builder Extensions

Users can extend builders with custom functionality:

```python
class MLWorkloadBuilder(BaseBuilder):
    def gpu_resources(self, gpu_count, gpu_type="nvidia.com/gpu"):
        return self._set('gpu', {'count': gpu_count, 'type': gpu_type})
    
    def model_storage(self, model_path, size="100Gi"):
        return self._set('model_storage', {'path': model_path, 'size': size})
    
    def training_dataset(self, dataset_config):
        return self._set('dataset', dataset_config)

# Usage
ml_app = (App("model-training")
    .image("tensorflow/tensorflow:latest-gpu")
    .extend_with(MLWorkloadBuilder())
    .gpu_resources(2)
    .model_storage("/models")
    .training_dataset({"source": "s3://my-bucket/data"}))
```

## Performance Considerations

### Optimization Strategies

- **Lazy Evaluation** - Templates are only rendered when needed
- **Caching** - Template compilation results are cached
- **Parallel Generation** - Multiple manifests can be generated in parallel
- **Incremental Updates** - Only changed resources are regenerated
- **Memory Management** - Large configurations are processed in chunks

### Scalability

The implementation is designed to handle:
- Large numbers of services (1000+)
- Complex configuration hierarchies
- Multiple output formats simultaneously
- Concurrent generation requests 