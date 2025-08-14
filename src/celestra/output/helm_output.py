"""
HelmOutput class for generating Helm charts in Celestra DSL.

This module provides Helm chart generation with templates, values files,
and proper chart structure following Helm best practices.
"""

import os
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from .base_output import OutputFormat


class HelmOutput(OutputFormat):
    
    def generate(self, output_dir: str) -> None:
        """Generate method required by OutputFormat base class."""
        return self.generate_files(output_dir)
    """
    Output format for generating Helm charts.
    
    Generates proper Helm chart structure with templates, values.yaml,
    Chart.yaml, and other Helm-specific files.
    
    Example:
        ```python
        helm_output = (HelmOutput("my-app")
            .set_version("1.0.0")
            .set_app_version("2.1.0")
            .set_description("My application Helm chart")
            .add_dependency("postgresql", "11.6.12", "https://charts.bitnami.com/bitnami")
            .add_values_override("replicaCount", 3)
            .enable_ingress(True))
        ```
    """
    
    def __init__(self, chart_name: str):
        """
        Initialize the Helm output formatter.
        
        Args:
            chart_name: Name of the Helm chart
        """
        super().__init__()
        self._name = chart_name
        self._chart_version: str = "0.1.0"
        self._app_version: str = "1.0.0"
        self._description: str = f"A Helm chart for {chart_name}"
        self._keywords: List[str] = []
        self._maintainers: List[Dict[str, str]] = []
        self._dependencies: List[Dict[str, Any]] = []
        self._values_overrides: Dict[str, Any] = {}
        self._custom_templates: Dict[str, str] = {}
        self._notes_template: Optional[str] = None
        self._hooks: List[Dict[str, Any]] = []
        self._tests: List[Dict[str, Any]] = []
        self._resources: List[Any] = []
        
        # Default values
        self._default_values = {
            "replicaCount": 1,
            "image": {
                "repository": "nginx",
                "pullPolicy": "IfNotPresent",
                "tag": "latest"
            },
            "nameOverride": "",
            "fullnameOverride": "",
            "serviceAccount": {
                "create": True,
                "annotations": {},
                "name": ""
            },
            "podAnnotations": {},
            "podSecurityContext": {},
            "securityContext": {},
            "service": {
                "type": "ClusterIP",
                "port": 80
            },
            "ingress": {
                "enabled": False,
                "className": "",
                "annotations": {},
                "hosts": [],
                "tls": []
            },
            "resources": {},
            "autoscaling": {
                "enabled": False,
                "minReplicas": 1,
                "maxReplicas": 100,
                "targetCPUUtilizationPercentage": 80
            },
            "nodeSelector": {},
            "tolerations": [],
            "affinity": {}
        }
    
    def set_version(self, version: str) -> "HelmOutput":
        """
        Set the chart version.
        
        Args:
            version: Chart version (SemVer)
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._chart_version = version
        return self
    
    def set_app_version(self, app_version: str) -> "HelmOutput":
        """
        Set the application version.
        
        Args:
            app_version: Application version
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._app_version = app_version
        return self
    
    def set_description(self, description: str) -> "HelmOutput":
        """
        Set the chart description.
        
        Args:
            description: Chart description
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._description = description
        return self
    
    def add_keywords(self, *keywords: str) -> "HelmOutput":
        """
        Add keywords to the chart.
        
        Args:
            *keywords: Chart keywords
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._keywords.extend(keywords)
        return self
    
    def add_maintainer(self, name: str, email: Optional[str] = None, url: Optional[str] = None) -> "HelmOutput":
        """
        Add a chart maintainer.
        
        Args:
            name: Maintainer name
            email: Maintainer email
            url: Maintainer URL
            
        Returns:
            HelmOutput: Self for method chaining
        """
        maintainer = {"name": name}
        if email:
            maintainer["email"] = email
        if url:
            maintainer["url"] = url
        
        self._maintainers.append(maintainer)
        return self
    
    def add_dependency(
        self,
        name: str,
        version: str,
        repository: str,
        condition: Optional[str] = None,
        enabled: bool = True
    ) -> "HelmOutput":
        """
        Add a chart dependency.
        
        Args:
            name: Dependency chart name
            version: Dependency version
            repository: Repository URL
            condition: Condition for enabling dependency
            enabled: Whether dependency is enabled by default
            
        Returns:
            HelmOutput: Self for method chaining
        """
        dependency = {
            "name": name,
            "version": version,
            "repository": repository
        }
        
        if condition:
            dependency["condition"] = condition
        
        # Add to values if not enabled by default
        if not enabled and condition:
            keys = condition.split(".")
            current = self._default_values
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = False
        
        self._dependencies.append(dependency)
        return self
    
    def add_values_override(self, key: str, value: Any) -> "HelmOutput":
        """
        Add a values override.
        
        Args:
            key: Values key (supports dot notation)
            value: Value to set
            
        Returns:
            HelmOutput: Self for method chaining
        """
        keys = key.split(".")
        current = self._values_overrides
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        return self
    
    def add_custom_template(self, name: str, template: str) -> "HelmOutput":
        """
        Add a custom template file.
        
        Args:
            name: Template file name
            template: Template content
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._custom_templates[name] = template
        return self
    
    def set_notes_template(self, notes: str) -> "HelmOutput":
        """
        Set the NOTES.txt template.
        
        Args:
            notes: Notes template content
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._notes_template = notes
        return self
    
    def add_hook(
        self,
        name: str,
        hook_type: str,
        weight: int = 0,
        delete_policy: str = "before-hook-creation"
    ) -> "HelmOutput":
        """
        Add a Helm hook.
        
        Args:
            name: Hook name
            hook_type: Hook type (pre-install, post-install, etc.)
            weight: Hook weight
            delete_policy: Hook deletion policy
            
        Returns:
            HelmOutput: Self for method chaining
        """
        hook = {
            "name": name,
            "type": hook_type,
            "weight": weight,
            "delete_policy": delete_policy
        }
        self._hooks.append(hook)
        return self
    
    def add_test(self, name: str, command: List[str]) -> "HelmOutput":
        """
        Add a Helm test.
        
        Args:
            name: Test name
            command: Test command
            
        Returns:
            HelmOutput: Self for method chaining
        """
        test = {
            "name": name,
            "command": command
        }
        self._tests.append(test)
        return self
    
    def add_resource(self, resource: Any) -> "HelmOutput":
        """
        Add a resource to the Helm chart.
        
        Args:
            resource: Resource to add
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self._resources.append(resource)
        return self
    
    # Convenience methods for common configurations
    
    def enable_ingress(self, enabled: bool = True, host: Optional[str] = None) -> "HelmOutput":
        """
        Enable ingress configuration.
        
        Args:
            enabled: Whether to enable ingress
            host: Default host
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self.add_values_override("ingress.enabled", enabled)
        if host:
            self.add_values_override("ingress.hosts", [{"host": host, "paths": [{"path": "/", "pathType": "Prefix"}]}])
        return self
    
    def enable_autoscaling(self, min_replicas: int = 1, max_replicas: int = 10, target_cpu: int = 80) -> "HelmOutput":
        """
        Enable autoscaling configuration.
        
        Args:
            min_replicas: Minimum replicas
            max_replicas: Maximum replicas
            target_cpu: Target CPU utilization
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self.add_values_override("autoscaling.enabled", True)
        self.add_values_override("autoscaling.minReplicas", min_replicas)
        self.add_values_override("autoscaling.maxReplicas", max_replicas)
        self.add_values_override("autoscaling.targetCPUUtilizationPercentage", target_cpu)
        return self
    
    def set_image(self, repository: str, tag: str = "latest", pull_policy: str = "IfNotPresent") -> "HelmOutput":
        """
        Set image configuration.
        
        Args:
            repository: Image repository
            tag: Image tag
            pull_policy: Image pull policy
            
        Returns:
            HelmOutput: Self for method chaining
        """
        self.add_values_override("image.repository", repository)
        self.add_values_override("image.tag", tag)
        self.add_values_override("image.pullPolicy", pull_policy)
        return self
    
    def generate_files(self, output_dir: str) -> None:
        """
        Generate Helm chart files.
        
        Args:
            output_dir: Output directory path
        """
        chart_dir = Path(output_dir) / self._name
        chart_dir.mkdir(parents=True, exist_ok=True)
        
        # Create chart structure
        (chart_dir / "templates").mkdir(exist_ok=True)
        (chart_dir / "charts").mkdir(exist_ok=True)
        
        # Generate Chart.yaml
        self._generate_chart_yaml(chart_dir)
        
        # Generate values.yaml
        self._generate_values_yaml(chart_dir)
        
        # Generate templates
        self._generate_templates(chart_dir)
        
        # Generate dependencies file if needed
        if self._dependencies:
            self._generate_requirements_yaml(chart_dir)
        
        # Generate NOTES.txt if provided
        if self._notes_template:
            self._generate_notes(chart_dir)
        
        # Generate custom templates
        self._generate_custom_templates(chart_dir)
        
        # Generate tests
        if self._tests:
            self._generate_tests(chart_dir)
        
        print(f"✅ Helm chart generated in: {chart_dir}")
    
    def _generate_chart_yaml(self, chart_dir: Path) -> None:
        """Generate Chart.yaml file."""
        chart_yaml = {
            "apiVersion": "v2",
            "name": self._name,
            "description": self._description,
            "type": "application",
            "version": self._chart_version,
            "appVersion": self._app_version
        }
        
        if self._keywords:
            chart_yaml["keywords"] = self._keywords
        
        if self._maintainers:
            chart_yaml["maintainers"] = self._maintainers
        
        if self._dependencies:
            chart_yaml["dependencies"] = self._dependencies
        
        with open(chart_dir / "Chart.yaml", "w") as f:
            yaml.dump(chart_yaml, f, default_flow_style=False, sort_keys=False)
    
    def _generate_values_yaml(self, chart_dir: Path) -> None:
        """Generate values.yaml file."""
        # Merge default values with overrides
        values = self._merge_dictionaries(self._default_values, self._values_overrides)
        
        with open(chart_dir / "values.yaml", "w") as f:
            yaml.dump(values, f, default_flow_style=False, sort_keys=False)
    
    def _generate_templates(self, chart_dir: Path) -> None:
        """Generate basic template files."""
        templates_dir = chart_dir / "templates"
        
        # Generate basic templates for common resources
        self._generate_deployment_template(templates_dir)
        self._generate_service_template(templates_dir)
        self._generate_serviceaccount_template(templates_dir)
        self._generate_ingress_template(templates_dir)
        self._generate_hpa_template(templates_dir)
        self._generate_helpers_template(templates_dir)
        
        # Process resources from added components
        for resource in self._resources:
            k8s_resources = resource.generate_kubernetes_resources()
            for k8s_resource in k8s_resources:
                self._generate_resource_template(templates_dir, k8s_resource)
    
    def _generate_deployment_template(self, templates_dir: Path) -> None:
        """Generate deployment template."""
        deployment_template = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "{chart_name}.fullname" . }}
  labels:
    {{{{ include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  {{{{- if not .Values.autoscaling.enabled }}}}
  replicas: {{ .Values.replicaCount }}
  {{{{- end }}}}
  selector:
    matchLabels:
      {{{{ include "{chart_name}.selectorLabels" . | nindent 6 }}}}
  template:
    metadata:
      {{{{- with .Values.podAnnotations }}}}
      annotations:
        {{{{ toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      labels:
        {{{{ include "{chart_name}.selectorLabels" . | nindent 8 }}}}
    spec:
      {{{{- with .Values.imagePullSecrets }}}}
      imagePullSecrets:
        {{{{ toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      serviceAccountName: {{ include "{chart_name}.serviceAccountName" . }}
      securityContext:
        {{{{ toYaml .Values.podSecurityContext | nindent 8 }}}}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{{{ toYaml .Values.securityContext | nindent 12 }}}}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 80
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /
              port: http
          readinessProbe:
            httpGet:
              path: /
              port: http
          resources:
            {{{{ toYaml .Values.resources | nindent 12 }}}}
      {{{{- with .Values.nodeSelector }}}}
      nodeSelector:
        {{{{ toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      {{{{- with .Values.affinity }}}}
      affinity:
        {{{{ toYaml . | nindent 8 }}}}
      {{{{- end }}}}
      {{{{- with .Values.tolerations }}}}
      tolerations:
        {{{{ toYaml . | nindent 8 }}}}
      {{{{- end }}}}
'''.format(chart_name=self._name)
        
        with open(templates_dir / "deployment.yaml", "w") as f:
            f.write(deployment_template)
    
    def _generate_service_template(self, templates_dir: Path) -> None:
        """Generate service template."""
        service_template = '''apiVersion: v1
kind: Service
metadata:
  name: {{ include "{chart_name}.fullname" . }}
  labels:
    {{{{ include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{{{ include "{chart_name}.selectorLabels" . | nindent 4 }}}}
'''.format(chart_name=self._name)
        
        with open(templates_dir / "service.yaml", "w") as f:
            f.write(service_template)
    
    def _generate_serviceaccount_template(self, templates_dir: Path) -> None:
        """Generate service account template."""
        sa_template = '''{{{{- if .Values.serviceAccount.create -}}}}
apiVersion: v1
kind: ServiceAccount
metadata:
  name: {{ include "{chart_name}.serviceAccountName" . }}
  labels:
    {{{{ include "{chart_name}.labels" . | nindent 4 }}}}
  {{{{- with .Values.serviceAccount.annotations }}}}
  annotations:
    {{{{ toYaml . | nindent 4 }}}}
  {{{{- end }}}}
{{{{- end }}}}
'''.format(chart_name=self._name)
        
        with open(templates_dir / "serviceaccount.yaml", "w") as f:
            f.write(sa_template)
    
    def _generate_ingress_template(self, templates_dir: Path) -> None:
        """Generate ingress template."""
        ingress_template = '''{{{{- if .Values.ingress.enabled -}}}}
{{{{- $fullName := include "{chart_name}.fullname" . -}}}}
{{{{- $svcPort := .Values.service.port -}}}}
{{{{- if and .Values.ingress.className (not (hasKey .Values.ingress.annotations "kubernetes.io/ingress.class")) }}}}
  {{{{- $_ := set .Values.ingress.annotations "kubernetes.io/ingress.class" .Values.ingress.className}}}}
{{{{- end }}}}
{{{{- if semverCompare ">=1.19-0" .Capabilities.KubeVersion.GitVersion -}}}}
apiVersion: networking.k8s.io/v1
{{{{- else if semverCompare ">=1.14-0" .Capabilities.KubeVersion.GitVersion -}}}}
apiVersion: networking.k8s.io/v1beta1
{{{{- else -}}}}
apiVersion: extensions/v1beta1
{{{{- end }}}}
kind: Ingress
metadata:
  name: {{ $fullName }}
  labels:
    {{{{ include "{chart_name}.labels" . | nindent 4 }}}}
  {{{{- with .Values.ingress.annotations }}}}
  annotations:
    {{{{ toYaml . | nindent 4 }}}}
  {{{{- end }}}}
spec:
  {{{{- if and .Values.ingress.className (semverCompare ">=1.18-0" .Capabilities.KubeVersion.GitVersion) }}}}
  ingressClassName: {{ .Values.ingress.className }}
  {{{{- end }}}}
  {{{{- if .Values.ingress.tls }}}}
  tls:
    {{{{- range .Values.ingress.tls }}}}
    - hosts:
        {{{{- range .hosts }}}}
        - {{ . | quote }}
        {{{{- end }}}}
      secretName: {{ .secretName }}
    {{{{- end }}}}
  {{{{- end }}}}
  rules:
    {{{{- range .Values.ingress.hosts }}}}
    - host: {{ .host | quote }}
      http:
        paths:
          {{{{- range .paths }}}}
          - path: {{ .path }}
            {{{{- if and .pathType (semverCompare ">=1.18-0" $.Capabilities.KubeVersion.GitVersion) }}}}
            pathType: {{ .pathType }}
            {{{{- end }}}}
            backend:
              {{{{- if semverCompare ">=1.19-0" $.Capabilities.KubeVersion.GitVersion }}}}
              service:
                name: {{ $fullName }}
                port:
                  number: {{ $svcPort }}
              {{{{- else }}}}
              serviceName: {{ $fullName }}
              servicePort: {{ $svcPort }}
              {{{{- end }}}}
          {{{{- end }}}}
    {{{{- end }}}}
{{{{- end }}}}
'''.format(chart_name=self._name)
        
        with open(templates_dir / "ingress.yaml", "w") as f:
            f.write(ingress_template)
    
    def _generate_hpa_template(self, templates_dir: Path) -> None:
        """Generate HPA template."""
        hpa_template = '''{{{{- if .Values.autoscaling.enabled }}}}
apiVersion: autoscaling/v2beta1
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "{chart_name}.fullname" . }}
  labels:
    {{{{ include "{chart_name}.labels" . | nindent 4 }}}}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "{chart_name}.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{{{- if .Values.autoscaling.targetCPUUtilizationPercentage }}}}
    - type: Resource
      resource:
        name: cpu
        targetAverageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{{{- end }}}}
    {{{{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}}}
    - type: Resource
      resource:
        name: memory
        targetAverageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{{{- end }}}}
{{{{- end }}}}
'''.format(chart_name=self._name)
        
        with open(templates_dir / "hpa.yaml", "w") as f:
            f.write(hpa_template)
    
    def _generate_helpers_template(self, templates_dir: Path) -> None:
        """Generate _helpers.tpl template."""
        helpers_template = '''{{{{/*
Expand the name of the chart.
*/}}}}
{{{{- define "{chart_name}.name" -}}}}
{{{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}

{{{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}}}
{{{{- define "{chart_name}.fullname" -}}}}
{{{{- if .Values.fullnameOverride }}}}
{{{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}}}
{{{{- else }}}}
{{{{- $name := default .Chart.Name .Values.nameOverride }}}}
{{{{- if contains $name .Release.Name }}}}
{{{{- .Release.Name | trunc 63 | trimSuffix "-" }}}}
{{{{- else }}}}
{{{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}
{{{{- end }}}}
{{{{- end }}}}

{{{{/*
Create chart name and version as used by the chart label.
*/}}}}
{{{{- define "{chart_name}.chart" -}}}}
{{{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}}}
{{{{- end }}}}

{{{{/*
Common labels
*/}}}}
{{{{- define "{chart_name}.labels" -}}}}
helm.sh/chart: {{ include "{chart_name}.chart" . }}
{{ include "{chart_name}.selectorLabels" . }}
{{{{- if .Chart.AppVersion }}}}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{{{- end }}}}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{{{- end }}}}

{{{{/*
Selector labels
*/}}}}
{{{{- define "{chart_name}.selectorLabels" -}}}}
app.kubernetes.io/name: {{ include "{chart_name}.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{{{- end }}}}

{{{{/*
Create the name of the service account to use
*/}}}}
{{{{- define "{chart_name}.serviceAccountName" -}}}}
{{{{- if .Values.serviceAccount.create }}}}
{{{{- default (include "{chart_name}.fullname" .) .Values.serviceAccount.name }}}}
{{{{- else }}}}
{{{{- default "default" .Values.serviceAccount.name }}}}
{{{{- end }}}}
{{{{- end }}}}
'''.format(chart_name=self._name)
        
        with open(templates_dir / "_helpers.tpl", "w") as f:
            f.write(helpers_template)
    
    def _generate_resource_template(self, templates_dir: Path, resource: Dict[str, Any]) -> None:
        """Generate template for a specific resource."""
        kind = resource.get("kind", "unknown").lower()
        filename = f"{kind}-{resource.get('metadata', {}).get('name', 'resource')}.yaml"
        
        with open(templates_dir / filename, "w") as f:
            yaml.dump(resource, f, default_flow_style=False, sort_keys=False)
    
    def _generate_requirements_yaml(self, chart_dir: Path) -> None:
        """Generate requirements.yaml for Helm v2 compatibility."""
        requirements = {
            "dependencies": self._dependencies
        }
        
        with open(chart_dir / "requirements.yaml", "w") as f:
            yaml.dump(requirements, f, default_flow_style=False, sort_keys=False)
    
    def _generate_notes(self, chart_dir: Path) -> None:
        """Generate NOTES.txt file."""
        templates_dir = chart_dir / "templates"
        
        with open(templates_dir / "NOTES.txt", "w") as f:
            f.write(self._notes_template)
    
    def _generate_custom_templates(self, chart_dir: Path) -> None:
        """Generate custom template files."""
        templates_dir = chart_dir / "templates"
        
        for name, template in self._custom_templates.items():
            with open(templates_dir / name, "w") as f:
                f.write(template)
    
    def _generate_tests(self, chart_dir: Path) -> None:
        """Generate test files."""
        tests_dir = chart_dir / "templates" / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        for test in self._tests:
            test_template = f'''apiVersion: v1
kind: Pod
metadata:
  name: "{{{{ include "{self._name}.fullname" . }}}}-test-{test['name']}"
  labels:
    {{{{ include "{self._name}.labels" . | nindent 4 }}}}
  annotations:
    "helm.sh/hook": test
spec:
  restartPolicy: Never
  containers:
    - name: {test['name']}
      image: busybox
      command: {test['command']}
'''
            
            with open(tests_dir / f"test-{test['name']}.yaml", "w") as f:
                f.write(test_template)
    
    def _merge_dictionaries(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            dict1: Base dictionary
            dict2: Override dictionary
            
        Returns:
            Dict[str, Any]: Merged dictionary
        """
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dictionaries(result[key], value)
            else:
                result[key] = value
        
        return result 