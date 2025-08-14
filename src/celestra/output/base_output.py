"""
Base output format class for Celestra DSL.

This module contains the base OutputFormat class that provides common functionality
for all output format implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..utils.helpers import ensure_directory


class OutputFormat(ABC):
    """
    Abstract base class for all output formats.
    
    This class defines the interface that all output format implementations
    must follow and provides common utility methods.
    """
    
    def __init__(self):
        """Initialize the output format."""
        self._options: Dict[str, Any] = {}
    
    def set_option(self, key: str, value: Any) -> "OutputFormat":
        """
        Set an output format option.
        
        Args:
            key: Option key
            value: Option value
            
        Returns:
            OutputFormat: Self for method chaining
        """
        self._options[key] = value
        return self
    
    def set_options(self, options: Dict[str, Any]) -> "OutputFormat":
        """
        Set multiple output format options.
        
        Args:
            options: Dictionary of options
            
        Returns:
            OutputFormat: Self for method chaining
        """
        self._options.update(options)
        return self
    
    def get_option(self, key: str, default: Any = None) -> Any:
        """
        Get an output format option.
        
        Args:
            key: Option key
            default: Default value if key not found
            
        Returns:
            Any: Option value
        """
        return self._options.get(key, default)
    
    @abstractmethod
    def generate(self, builder: Any, *args, **kwargs) -> None:
        """
        Generate output from a builder.
        
        Args:
            builder: The DSL builder to generate output from
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        pass
    
    def _ensure_output_directory(self, path: Union[str, Path]) -> Path:
        """
        Ensure output directory exists.
        
        Args:
            path: Directory path
            
        Returns:
            Path: Path object
        """
        return ensure_directory(path)
    
    def _write_file(self, path: Union[str, Path], content: str) -> None:
        """
        Write content to a file.
        
        Args:
            path: File path
            content: Content to write
        """
        from ..utils.helpers import write_file
        write_file(path, content)
    
    def _format_filename(self, name: str, extension: str) -> str:
        """
        Format a filename with proper extension.
        
        Args:
            name: Base filename
            extension: File extension (with or without dot)
            
        Returns:
            str: Formatted filename
        """
        if not extension.startswith('.'):
            extension = f'.{extension}'
        
        if name.endswith(extension):
            return name
        
        return f"{name}{extension}"
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a filename for filesystem compatibility.
        
        Args:
            filename: Original filename
            
        Returns:
            str: Sanitized filename
        """
        import re
        # Replace invalid characters with hyphens
        sanitized = re.sub(r'[<>:"/\\|?*]', '-', filename)
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        return sanitized
    
    def validate_builder(self, builder: Any) -> List[str]:
        """
        Validate a builder before generating output.
        
        Args:
            builder: Builder to validate
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        if not hasattr(builder, 'generate_kubernetes_resources'):
            errors.append("Builder must implement generate_kubernetes_resources method")
        
        if hasattr(builder, 'validate'):
            builder_errors = builder.validate()
            errors.extend(builder_errors)
        
        return errors


class ResourceOutputFormat(OutputFormat):
    """
    Base class for output formats that work with Kubernetes resources.
    
    This class provides common functionality for output formats that
    generate files from Kubernetes resource dictionaries.
    """
    
    def __init__(self):
        """Initialize the resource output format."""
        super().__init__()
    
    def _get_resources_from_builder(self, builder: Any) -> List[Dict[str, Any]]:
        """
        Get Kubernetes resources from a builder.
        
        Args:
            builder: Builder to get resources from
            
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        if hasattr(builder, 'generate_kubernetes_resources'):
            return builder.generate_kubernetes_resources()
        else:
            raise ValueError("Builder does not support Kubernetes resource generation")
    
    def _group_resources_by_kind(self, resources: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group resources by their Kubernetes kind.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Resources grouped by kind
        """
        groups = {}
        for resource in resources:
            kind = resource.get('kind', 'Unknown')
            if kind not in groups:
                groups[kind] = []
            groups[kind].append(resource)
        return groups
    
    def _sort_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort resources by deployment order.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[Dict[str, Any]]: Sorted resources
        """
        # Define deployment order
        kind_order = [
            'Namespace',
            'CustomResourceDefinition',
            'ServiceAccount',
            'Role',
            'ClusterRole',
            'RoleBinding',
            'ClusterRoleBinding',
            'ConfigMap',
            'Secret',
            'PersistentVolume',
            'PersistentVolumeClaim',
            'Service',
            'Deployment',
            'StatefulSet',
            'DaemonSet',
            'Job',
            'CronJob',
            'Ingress',
            'HorizontalPodAutoscaler',
            'NetworkPolicy',
            'ServiceMonitor'
        ]
        
        def get_sort_key(resource: Dict[str, Any]) -> tuple:
            kind = resource.get('kind', 'Unknown')
            try:
                order = kind_order.index(kind)
            except ValueError:
                order = len(kind_order)  # Unknown kinds go last
            
            name = resource.get('metadata', {}).get('name', '')
            return (order, name)
        
        return sorted(resources, key=get_sort_key)


class FileOutputFormat(ResourceOutputFormat):
    """
    Base class for output formats that generate files.
    
    This class provides common functionality for output formats that
    write files to the filesystem.
    """
    
    def __init__(self):
        """Initialize the file output format."""
        super().__init__()
    
    def _write_resource_file(
        self, 
        resource: Dict[str, Any],
        output_dir: Path,
        filename_template: str = "{kind}-{name}.yaml"
    ) -> Path:
        """
        Write a single resource to a file.
        
        Args:
            resource: Kubernetes resource
            output_dir: Output directory
            filename_template: Template for filename generation
            
        Returns:
            Path: Path to the written file
        """
        from ..utils.helpers import format_yaml
        
        kind = resource.get('kind', 'unknown').lower()
        name = resource.get('metadata', {}).get('name', 'unnamed')
        
        filename = filename_template.format(kind=kind, name=name)
        filename = self._sanitize_filename(filename)
        
        file_path = output_dir / filename
        content = format_yaml(resource)
        
        self._write_file(file_path, content)
        return file_path
    
    def _write_resources_file(
        self, 
        resources: List[Dict[str, Any]],
        file_path: Path
    ) -> Path:
        """
        Write multiple resources to a single file.
        
        Args:
            resources: List of Kubernetes resources
            file_path: Output file path
            
        Returns:
            Path: Path to the written file
        """
        from ..utils.helpers import format_yaml
        
        content_parts = []
        for resource in resources:
            content_parts.append(format_yaml(resource))
        
        content = "---\n".join(content_parts)
        self._write_file(file_path, content)
        return file_path 