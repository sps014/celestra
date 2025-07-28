"""
TemplateManager class for custom template system in Celestraa DSL.

This module provides a comprehensive template management system with
support for multiple template engines and custom template rendering.
"""

import os
import re
import json
import yaml
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from enum import Enum
import logging
from abc import ABC, abstractmethod


class TemplateEngine(Enum):
    """Supported template engines."""
    JINJA2 = "jinja2"
    GOLANG = "golang"
    MUSTACHE = "mustache"
    SIMPLE = "simple"


class TemplateRenderer(ABC):
    """
    Abstract base class for template renderers.
    """
    
    @abstractmethod
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Render template with variables.
        
        Args:
            template: Template content
            variables: Template variables
            
        Returns:
            str: Rendered content
        """
        pass
    
    @abstractmethod
    def get_engine_name(self) -> str:
        """
        Get template engine name.
        
        Returns:
            str: Engine name
        """
        pass


class SimpleTemplateRenderer(TemplateRenderer):
    """
    Simple template renderer using Python string formatting.
    
    Supports variables in the format ${variable_name} or {variable_name}.
    """
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template using simple string substitution."""
        # Handle ${variable} format
        def replace_dollar_vars(match):
            var_name = match.group(1)
            return str(variables.get(var_name, match.group(0)))
        
        template = re.sub(r'\$\{([^}]+)\}', replace_dollar_vars, template)
        
        # Handle {variable} format with safe replacement
        try:
            return template.format(**variables)
        except KeyError as e:
            # Return template with unreplaced variables as-is
            return template
    
    def get_engine_name(self) -> str:
        return "simple"


class Jinja2TemplateRenderer(TemplateRenderer):
    """
    Jinja2 template renderer.
    
    Provides full Jinja2 template functionality with filters and functions.
    """
    
    def __init__(self):
        """Initialize Jinja2 renderer."""
        try:
            from jinja2 import Environment, BaseLoader, select_autoescape
            self.jinja_env = Environment(
                loader=BaseLoader(),
                autoescape=select_autoescape(['html', 'xml'])
            )
            
            # Add custom filters
            self._add_custom_filters()
            
        except ImportError:
            raise ImportError("jinja2 is required for Jinja2 template rendering")
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template using Jinja2."""
        jinja_template = self.jinja_env.from_string(template)
        return jinja_template.render(**variables)
    
    def get_engine_name(self) -> str:
        return "jinja2"
    
    def _add_custom_filters(self):
        """Add custom Jinja2 filters."""
        
        def to_yaml(value, indent=2):
            """Convert value to YAML format."""
            return yaml.dump(value, default_flow_style=False, indent=indent)
        
        def to_json(value, indent=2):
            """Convert value to JSON format."""
            return json.dumps(value, indent=indent)
        
        def k8s_name(value):
            """Convert value to valid Kubernetes name."""
            # Convert to lowercase and replace invalid characters
            name = str(value).lower()
            name = re.sub(r'[^a-z0-9-]', '-', name)
            name = re.sub(r'-+', '-', name)
            name = name.strip('-')
            return name[:63]  # K8s name limit
        
        def base64_encode(value):
            """Base64 encode a value."""
            import base64
            return base64.b64encode(str(value).encode()).decode()
        
        def base64_decode(value):
            """Base64 decode a value."""
            import base64
            return base64.b64decode(str(value)).decode()
        
        # Register filters
        self.jinja_env.filters['to_yaml'] = to_yaml
        self.jinja_env.filters['to_json'] = to_json
        self.jinja_env.filters['k8s_name'] = k8s_name
        self.jinja_env.filters['b64encode'] = base64_encode
        self.jinja_env.filters['b64decode'] = base64_decode


class GolangTemplateRenderer(TemplateRenderer):
    """
    Go template renderer (basic implementation).
    
    Provides basic Go template functionality using regex patterns.
    """
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template using Go template syntax."""
        # Handle {{ .Variable }} format
        def replace_go_vars(match):
            var_path = match.group(1).strip()
            if var_path.startswith('.'):
                var_path = var_path[1:]  # Remove leading dot
            
            # Navigate nested variables
            value = variables
            for part in var_path.split('.'):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)  # Return original if not found
            
            return str(value)
        
        template = re.sub(r'\{\{\s*([^}]+)\s*\}\}', replace_go_vars, template)
        return template
    
    def get_engine_name(self) -> str:
        return "golang"


class MustacheTemplateRenderer(TemplateRenderer):
    """
    Mustache template renderer.
    
    Provides basic Mustache template functionality.
    """
    
    def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template using Mustache syntax."""
        # Handle {{ variable }} format
        def replace_mustache_vars(match):
            var_name = match.group(1).strip()
            
            # Navigate nested variables
            value = variables
            for part in var_name.split('.'):
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return ""  # Mustache returns empty string for missing vars
            
            return str(value)
        
        # Handle {{& variable }} (unescaped) - treat same as regular for now
        template = re.sub(r'\{\{\&?\s*([^}]+)\s*\}\}', replace_mustache_vars, template)
        
        # Handle {{# section }} ... {{/ section }} (basic sections)
        def replace_sections(match):
            section_name = match.group(1).strip()
            section_content = match.group(2)
            
            if section_name in variables:
                section_data = variables[section_name]
                
                if isinstance(section_data, list):
                    # Render for each item in list
                    result = ""
                    for item in section_data:
                        item_vars = dict(variables)
                        if isinstance(item, dict):
                            item_vars.update(item)
                        else:
                            item_vars['.'] = item
                        result += self.render(section_content, item_vars)
                    return result
                
                elif section_data:
                    # Render once if truthy
                    return self.render(section_content, variables)
            
            return ""  # Don't render if section is false/missing
        
        template = re.sub(r'\{\{\#\s*([^}]+)\s*\}\}(.*?)\{\{\/\s*\1\s*\}\}', 
                         replace_sections, template, flags=re.DOTALL)
        
        return template
    
    def get_engine_name(self) -> str:
        return "mustache"


class TemplateManager:
    """
    Template manager for Celestraa DSL.
    
    Provides comprehensive template management with support for multiple
    template engines, template discovery, and custom template functions.
    
    Example:
        ```python
        manager = TemplateManager()
        manager.add_template_directory("./templates")
        
        # Render with Jinja2
        result = manager.render_template("deployment.yaml.j2", {
            "app_name": "my-app",
            "replicas": 3
        })
        
        # Render with Go templates
        result = manager.render_template("service.yaml.gotmpl", variables, 
                                       engine=TemplateEngine.GOLANG)
        ```
    """
    
    def __init__(self):
        """Initialize the template manager."""
        self._templates: Dict[str, str] = {}
        self._template_dirs: List[Path] = []
        self._renderers: Dict[str, TemplateRenderer] = {}
        self._functions: Dict[str, Callable] = {}
        self._variables: Dict[str, Any] = {}
        self._logger = logging.getLogger(__name__)
        
        # Initialize default renderers
        self._init_default_renderers()
        
        # Add default functions
        self._add_default_functions()
    
    def add_template_directory(self, directory: Union[str, Path]) -> None:
        """
        Add a template directory.
        
        Args:
            directory: Directory containing templates
        """
        directory = Path(directory)
        
        if not directory.exists():
            self._logger.warning(f"Template directory does not exist: {directory}")
            return
        
        self._template_dirs.append(directory)
        self._discover_templates(directory)
        self._logger.info(f"Added template directory: {directory}")
    
    def add_template(self, name: str, content: str) -> None:
        """
        Add a template directly.
        
        Args:
            name: Template name
            content: Template content
        """
        self._templates[name] = content
        self._logger.debug(f"Added template: {name}")
    
    def get_template(self, name: str) -> Optional[str]:
        """
        Get template content by name.
        
        Args:
            name: Template name
            
        Returns:
            Optional[str]: Template content or None if not found
        """
        return self._templates.get(name)
    
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List[str]: List of template names
        """
        return list(self._templates.keys())
    
    def render_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        engine: Optional[TemplateEngine] = None
    ) -> str:
        """
        Render a template with variables.
        
        Args:
            template_name: Name of the template
            variables: Template variables
            engine: Template engine to use (auto-detected if None)
            
        Returns:
            str: Rendered content
        """
        if template_name not in self._templates:
            raise ValueError(f"Template not found: {template_name}")
        
        template_content = self._templates[template_name]
        
        # Auto-detect engine if not specified
        if engine is None:
            engine = self._detect_template_engine(template_name)
        
        # Get renderer
        renderer = self._get_renderer(engine)
        
        # Merge with global variables
        all_variables = dict(self._variables)
        all_variables.update(variables)
        
        # Add template functions
        all_variables.update(self._functions)
        
        # Render template
        try:
            rendered = renderer.render(template_content, all_variables)
            self._logger.debug(f"Rendered template: {template_name} with engine: {engine.value}")
            return rendered
            
        except Exception as e:
            self._logger.error(f"Error rendering template {template_name}: {e}")
            raise
    
    def render_string(
        self,
        template_content: str,
        variables: Dict[str, Any],
        engine: TemplateEngine = TemplateEngine.SIMPLE
    ) -> str:
        """
        Render template content directly.
        
        Args:
            template_content: Template content
            variables: Template variables
            engine: Template engine to use
            
        Returns:
            str: Rendered content
        """
        renderer = self._get_renderer(engine)
        
        # Merge with global variables
        all_variables = dict(self._variables)
        all_variables.update(variables)
        all_variables.update(self._functions)
        
        return renderer.render(template_content, all_variables)
    
    def add_renderer(self, renderer: TemplateRenderer) -> None:
        """
        Add a custom template renderer.
        
        Args:
            renderer: Template renderer
        """
        engine_name = renderer.get_engine_name()
        self._renderers[engine_name] = renderer
        self._logger.info(f"Added template renderer: {engine_name}")
    
    def add_function(self, name: str, function: Callable) -> None:
        """
        Add a template function.
        
        Args:
            name: Function name
            function: Function callable
        """
        self._functions[name] = function
        self._logger.debug(f"Added template function: {name}")
    
    def set_global_variable(self, name: str, value: Any) -> None:
        """
        Set a global template variable.
        
        Args:
            name: Variable name
            value: Variable value
        """
        self._variables[name] = value
        self._logger.debug(f"Set global variable: {name}")
    
    def get_global_variables(self) -> Dict[str, Any]:
        """
        Get global template variables.
        
        Returns:
            Dict[str, Any]: Global variables
        """
        return self._variables.copy()
    
    # Preset template generators
    
    def generate_deployment_template(self, name: str) -> str:
        """
        Generate a basic deployment template.
        
        Args:
            name: Template name
            
        Returns:
            str: Template content
        """
        template = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ app_name }}
  labels:
    app: {{ app_name }}
spec:
  replicas: {{ replicas | default(1) }}
  selector:
    matchLabels:
      app: {{ app_name }}
  template:
    metadata:
      labels:
        app: {{ app_name }}
    spec:
      containers:
      - name: {{ app_name }}
        image: {{ image }}
        ports:
        - containerPort: {{ port | default(8080) }}
        {% if env_vars %}
        env:
        {% for key, value in env_vars.items() %}
        - name: {{ key }}
          value: "{{ value }}"
        {% endfor %}
        {% endif %}
        {% if resources %}
        resources:
          {{ resources | to_yaml | indent(10) }}
        {% endif %}
'''
        
        self.add_template(name, template)
        return template
    
    def generate_service_template(self, name: str) -> str:
        """
        Generate a basic service template.
        
        Args:
            name: Template name
            
        Returns:
            str: Template content
        """
        template = '''apiVersion: v1
kind: Service
metadata:
  name: {{ app_name }}
  labels:
    app: {{ app_name }}
spec:
  type: {{ service_type | default("ClusterIP") }}
  ports:
  - port: {{ service_port | default(80) }}
    targetPort: {{ target_port | default(8080) }}
    protocol: TCP
    name: http
  selector:
    app: {{ app_name }}
'''
        
        self.add_template(name, template)
        return template
    
    def _init_default_renderers(self) -> None:
        """Initialize default template renderers."""
        self._renderers["simple"] = SimpleTemplateRenderer()
        self._renderers["golang"] = GolangTemplateRenderer()
        self._renderers["mustache"] = MustacheTemplateRenderer()
        
        # Try to initialize Jinja2 renderer
        try:
            self._renderers["jinja2"] = Jinja2TemplateRenderer()
        except ImportError:
            self._logger.warning("Jinja2 not available - install jinja2 for advanced templating")
    
    def _add_default_functions(self) -> None:
        """Add default template functions."""
        
        def include_template(template_name: str, variables: Dict[str, Any] = None) -> str:
            """Include another template."""
            if variables is None:
                variables = {}
            return self.render_template(template_name, variables)
        
        def default(value: Any, default_value: Any) -> Any:
            """Return default value if value is None or empty."""
            return value if value is not None and value != "" else default_value
        
        def upper(value: str) -> str:
            """Convert to uppercase."""
            return str(value).upper()
        
        def lower(value: str) -> str:
            """Convert to lowercase."""
            return str(value).lower()
        
        def indent(value: str, spaces: int = 2) -> str:
            """Indent each line."""
            lines = str(value).split('\n')
            indented_lines = [' ' * spaces + line if line.strip() else line for line in lines]
            return '\n'.join(indented_lines)
        
        # Add functions
        self._functions.update({
            'include': include_template,
            'default': default,
            'upper': upper,
            'lower': lower,
            'indent': indent
        })
    
    def _discover_templates(self, directory: Path) -> None:
        """
        Discover templates in a directory.
        
        Args:
            directory: Directory to search
        """
        template_extensions = ['.j2', '.jinja', '.gotmpl', '.mustache', '.tmpl', '.tpl']
        
        for template_file in directory.rglob('*'):
            if template_file.is_file():
                # Check if it's a template file
                is_template = (
                    any(template_file.name.endswith(ext) for ext in template_extensions) or
                    template_file.suffix in ['.yaml', '.yml', '.json', '.toml']
                )
                
                if is_template:
                    try:
                        with open(template_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Use relative path as template name
                        template_name = str(template_file.relative_to(directory))
                        self._templates[template_name] = content
                        
                        self._logger.debug(f"Discovered template: {template_name}")
                        
                    except Exception as e:
                        self._logger.error(f"Error reading template {template_file}: {e}")
    
    def _detect_template_engine(self, template_name: str) -> TemplateEngine:
        """
        Detect template engine from template name.
        
        Args:
            template_name: Template name
            
        Returns:
            TemplateEngine: Detected engine
        """
        if template_name.endswith(('.j2', '.jinja')):
            return TemplateEngine.JINJA2
        elif template_name.endswith('.gotmpl'):
            return TemplateEngine.GOLANG
        elif template_name.endswith('.mustache'):
            return TemplateEngine.MUSTACHE
        else:
            return TemplateEngine.SIMPLE
    
    def _get_renderer(self, engine: TemplateEngine) -> TemplateRenderer:
        """
        Get template renderer for engine.
        
        Args:
            engine: Template engine
            
        Returns:
            TemplateRenderer: Template renderer
        """
        renderer_name = engine.value
        
        if renderer_name not in self._renderers:
            raise ValueError(f"Template engine not available: {renderer_name}")
        
        return self._renderers[renderer_name] 