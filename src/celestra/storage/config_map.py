"""
ConfigMap class for managing Kubernetes ConfigMaps in Celestra.

This module contains the ConfigMap class for handling configuration data
with support for multiple data sources and flexible mounting options.
"""

import json
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..core.base_builder import BaseBuilder
from ..utils.helpers import format_yaml, format_json, read_file


class ConfigMap(BaseBuilder):
    """
    Builder class for Kubernetes ConfigMaps.
    
    The ConfigMap class provides a fluent API for managing configuration data
    with support for multiple data sources, hot-reload capabilities, and
    various mounting options.
    
    Example:
        ```python
        config = (ConfigMap("app-config")
            .add("database_url", "database://localhost:5432/myapp")
            .add_json("features", {"new_ui": True, "beta": False})
            .from_file("app.properties", "./config/app.properties")
            .mount_path("/etc/config")
            .hot_reload(enabled=True))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the ConfigMap builder.
        
        Args:
            name: Name of the ConfigMap
        """
        super().__init__(name)
        self._data: Dict[str, str] = {}
        self._binary_data: Dict[str, str] = {}
        self._files: Dict[str, str] = {}
        self._directories: List[Dict[str, Any]] = []
        self._env_files: List[str] = []
        self._templates: List[Dict[str, Any]] = []
        self._mount_path: Optional[str] = None
        self._mount_as_env: bool = False
        self._env_prefix: str = ""
        self._file_permissions: int = 0o644
        self._hot_reload: bool = False
        self._hot_reload_config: Dict[str, Any] = {}
    
    def add(self, key: str, value: str) -> "ConfigMap":
        """
        Add a key-value pair to the ConfigMap.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._data[key] = str(value)
        return self
    
    def add_json(self, key: str, data: Dict[str, Any]) -> "ConfigMap":
        """
        Add JSON data to the ConfigMap.
        
        Args:
            key: Configuration key
            data: Data to serialize as JSON
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._data[key] = format_json(data)
        return self
    
    def add_yaml(self, key: str, data: Union[Dict[str, Any], str]) -> "ConfigMap":
        """
        Add YAML data to the ConfigMap.
        
        Args:
            key: Configuration key
            data: Data to serialize as YAML or YAML string
            
        Returns:
            ConfigMap: Self for method chaining
        """
        if isinstance(data, str):
            self._data[key] = data
        else:
            self._data[key] = format_yaml(data)
        return self
    
    def add_properties(self, key: str, properties: Dict[str, str]) -> "ConfigMap":
        """
        Add properties file format data to the ConfigMap.
        
        Args:
            key: Configuration key
            properties: Properties to add
            
        Returns:
            ConfigMap: Self for method chaining
        """
        properties_content = []
        for prop_key, prop_value in properties.items():
            properties_content.append(f"{prop_key}={prop_value}")
        
        self._data[key] = "\n".join(properties_content)
        return self
    
    def add_ini(self, key: str, sections: Dict[str, Dict[str, str]]) -> "ConfigMap":
        """
        Add INI file format data to the ConfigMap.
        
        Args:
            key: Configuration key
            sections: INI sections and their key-value pairs
            
        Returns:
            ConfigMap: Self for method chaining
        """
        ini_content = []
        for section_name, section_data in sections.items():
            ini_content.append(f"[{section_name}]")
            for option_key, option_value in section_data.items():
                ini_content.append(f"{option_key} = {option_value}")
            ini_content.append("")  # Empty line between sections
        
        self._data[key] = "\n".join(ini_content)
        return self
    
    def add_toml(self, key: str, data: Dict[str, Any]) -> "ConfigMap":
        """
        Add TOML format data to the ConfigMap.
        
        Args:
            key: Configuration key
            data: Data to serialize as TOML
            
        Returns:
            ConfigMap: Self for method chaining
        """
        # In a real implementation, this would use a TOML library
        # For now, we'll create a simple representation
        toml_content = []
        for toml_key, toml_value in data.items():
            if isinstance(toml_value, dict):
                toml_content.append(f"[{toml_key}]")
                for sub_key, sub_value in toml_value.items():
                    toml_content.append(f"{sub_key} = {self._format_toml_value(sub_value)}")
                toml_content.append("")
            else:
                toml_content.append(f"{toml_key} = {self._format_toml_value(toml_value)}")
        
        self._data[key] = "\n".join(toml_content)
        return self
    
    def from_file(self, key: str, file_path: str) -> "ConfigMap":
        """
        Add data from a file.
        
        Args:
            key: Configuration key
            file_path: Path to the file
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._files[key] = file_path
        return self
    
    def from_directory(
        self, 
        directory_path: str,
        pattern: str = "*",
        recursive: bool = False
    ) -> "ConfigMap":
        """
        Add all files from a directory.
        
        Args:
            directory_path: Path to the directory
            pattern: File pattern to match (default: "*")
            recursive: Whether to search recursively
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._directories.append({
            "path": directory_path,
            "pattern": pattern,
            "recursive": recursive
        })
        return self
    
    def from_env_file(self, file_path: str, prefix: str = "") -> "ConfigMap":
        """
        Load configuration from an environment file.
        
        Args:
            file_path: Path to the environment file
            prefix: Prefix to add to keys
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._env_files.append({
            "path": file_path,
            "prefix": prefix
        })
        return self
    
    def from_template(
        self, 
        template_path: str,
        variables: Dict[str, Any],
        output_key: Optional[str] = None
    ) -> "ConfigMap":
        """
        Generate configuration from a template.
        
        Args:
            template_path: Path to the template file
            variables: Variables to substitute in the template
            output_key: Key for the rendered template (default: template filename)
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._templates.append({
            "path": template_path,
            "variables": variables,
            "output_key": output_key or Path(template_path).stem
        })
        return self
    
    def mount_path(self, path: str) -> "ConfigMap":
        """
        Set the mount path for the ConfigMap as a volume.
        
        Args:
            path: Mount path in the container
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._mount_path = path
        return self
    
    def mount_as_env_vars(self, prefix: str = "") -> "ConfigMap":
        """
        Mount ConfigMap data as environment variables.
        
        Args:
            prefix: Prefix for environment variable names
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._mount_as_env = True
        self._env_prefix = prefix
        return self
    
    def file_permissions(self, mode: int) -> "ConfigMap":
        """
        Set file permissions for mounted files.
        
        Args:
            mode: Octal file permissions (e.g., 0o644)
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._file_permissions = mode
        return self
    
    def hot_reload(
        self, 
        enabled: bool = True,
        restart_policy: str = "rolling",
        interval: str = "30s"
    ) -> "ConfigMap":
        """
        Enable hot-reload for configuration changes.
        
        Args:
            enabled: Whether to enable hot-reload
            restart_policy: Restart policy (rolling, recreate)
            interval: Check interval for changes
            
        Returns:
            ConfigMap: Self for method chaining
        """
        self._hot_reload = enabled
        self._hot_reload_config = {
            "restart_policy": restart_policy,
            "interval": interval
        }
        return self
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes ConfigMap resource.
        
        Returns:
            List[Dict[str, Any]]: List containing the ConfigMap resource
        """
        # Process all data sources
        self._process_files()
        self._process_directories()
        self._process_env_files()
        self._process_templates()
        
        config_map = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": self._name,
                "labels": self._labels,
                "annotations": self._annotations
            }
        }
        
        if self._namespace:
            config_map["metadata"]["namespace"] = self._namespace
        
        # Add data
        if self._data:
            config_map["data"] = self._data
        
        if self._binary_data:
            config_map["binaryData"] = self._binary_data
        
        # Add hot-reload annotations
        if self._hot_reload:
            config_map["metadata"]["annotations"].update({
                "celestra.io/hot-reload": "true",
"celestra.io/restart-policy": self._hot_reload_config.get("restart_policy", "rolling"),
"celestra.io/check-interval": self._hot_reload_config.get("interval", "30s")
            })
        
        return [config_map]
    
    def _process_files(self) -> None:
        """Process individual file sources."""
        for key, file_path in self._files.items():
            try:
                content = read_file(file_path)
                self._data[key] = content
            except FileNotFoundError:
                # In a real implementation, this would be handled differently
                self._data[key] = f"# File not found: {file_path}"
    
    def _process_directories(self) -> None:
        """Process directory sources."""
        for dir_config in self._directories:
            directory_path = Path(dir_config["path"])
            pattern = dir_config["pattern"]
            recursive = dir_config["recursive"]
            
            if not directory_path.exists():
                continue
            
            if recursive:
                files = directory_path.rglob(pattern)
            else:
                files = directory_path.glob(pattern)
            
            for file_path in files:
                if file_path.is_file():
                    try:
                        content = file_path.read_text()
                        relative_path = file_path.relative_to(directory_path)
                        key = str(relative_path).replace('/', '.')
                        self._data[key] = content
                    except Exception:
                        # Skip files that can't be read as text
                        pass
    
    def _process_env_files(self) -> None:
        """Process environment file sources."""
        for env_config in self._env_files:
            file_path = env_config["path"]
            prefix = env_config.get("prefix", "")
            
            try:
                with open(file_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            
                            if prefix:
                                key = f"{prefix}{key}"
                            
                            self._data[key] = value
            except FileNotFoundError:
                # In a real implementation, this would be handled differently
                pass
    
    def _process_templates(self) -> None:
        """Process template sources."""
        for template_config in self._templates:
            template_path = template_config["path"]
            variables = template_config["variables"]
            output_key = template_config["output_key"]
            
            try:
                template_content = read_file(template_path)
                # Simple template substitution
                rendered_content = self._render_template(template_content, variables)
                self._data[output_key] = rendered_content
            except FileNotFoundError:
                self._data[output_key] = f"# Template not found: {template_path}"
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Simple template rendering using string substitution."""
        rendered = template
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            rendered = rendered.replace(placeholder, str(value))
        return rendered
    
    def _format_toml_value(self, value: Any) -> str:
        """Format a value for TOML output."""
        if isinstance(value, bool):
            return str(value).lower()
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, list):
            formatted_items = [self._format_toml_value(item) for item in value]
            return f"[{', '.join(formatted_items)}]"
        else:
            return f'"{str(value)}"'
    
    def get_env_var_mappings(self) -> List[Dict[str, Any]]:
        """
        Get environment variable mappings for container specs.
        
        Returns:
            List[Dict[str, Any]]: List of env var configurations
        """
        if not self._mount_as_env:
            return []
        
        env_vars = []
        
        for key in self._data.keys():
            from ..utils.helpers import sanitize_env_var_name
            env_name = sanitize_env_var_name(f"{self._env_prefix}{key}")
            env_vars.append({
                "name": env_name,
                "valueFrom": {
                    "configMapKeyRef": {
                        "name": self._name,
                        "key": key
                    }
                }
            })
        
        return env_vars
    
    def get_volume_mount(self) -> Optional[Dict[str, Any]]:
        """
        Get volume mount configuration.
        
        Returns:
            Optional[Dict[str, Any]]: Volume mount configuration if mount_path is set
        """
        if not self._mount_path:
            return None
        
        return {
            "name": f"{self._name}-volume",
            "mountPath": self._mount_path,
            "readOnly": True
        }
    
    def get_volume(self) -> Optional[Dict[str, Any]]:
        """
        Get volume configuration.
        
        Returns:
            Optional[Dict[str, Any]]: Volume configuration if mount_path is set
        """
        if not self._mount_path:
            return None
        
        volume = {
            "name": f"{self._name}-volume",
            "configMap": {
                "name": self._name
            }
        }
        
        # Set file permissions if specified
        if self._file_permissions != 0o644:
            volume["configMap"]["defaultMode"] = self._file_permissions
        
        return volume
    
    def validate(self) -> List[str]:
        """
        Validate the ConfigMap configuration.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = super().validate()
        
        # Check if ConfigMap has any data
        has_data = (
            self._data or 
            self._files or 
            self._directories or 
            self._env_files or 
            self._templates
        )
        
        if not has_data:
            errors.append("ConfigMap must contain at least one data source")
        
        # Validate file paths
        for key, file_path in self._files.items():
            if not Path(file_path).exists():
                errors.append(f"File not found: {file_path}")
        
        # Validate directory paths
        for dir_config in self._directories:
            directory_path = Path(dir_config["path"])
            if not directory_path.exists():
                errors.append(f"Directory not found: {directory_path}")
            elif not directory_path.is_dir():
                errors.append(f"Path is not a directory: {directory_path}")
        
        return errors 