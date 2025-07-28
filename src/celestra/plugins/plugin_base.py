"""
PluginBase class for plugin development framework in Celestraa DSL.

This module provides the base classes and interfaces for developing
custom plugins that extend the Celestraa DSL functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Type, Union
from enum import Enum
from dataclasses import dataclass
import inspect


class PluginType(Enum):
    """Types of plugins."""
    BUILDER = "builder"           # Custom resource builders
    OUTPUT = "output"             # Custom output formats
    VALIDATOR = "validator"       # Custom validation logic
    TRANSFORMER = "transformer"  # Resource transformers
    HOOK = "hook"                # Lifecycle hooks
    TEMPLATE = "template"         # Template engines


@dataclass
class PluginMetadata:
    """Plugin metadata information."""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = None
    tags: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []


class PluginBase(ABC):
    """
    Base class for all Celestra plugins.
    
    Provides the foundational interface and common functionality
    that all plugins must implement.
    
    Example:
        ```python
        class MyCustomPlugin(PluginBase):
            def get_metadata(self) -> PluginMetadata:
                return PluginMetadata(
                    name="my-custom-plugin",
                    version="1.0.0",
                    description="My custom plugin",
                    author="Developer",
                    plugin_type=PluginType.BUILDER
                )
            
            def initialize(self, config: Dict[str, Any]) -> None:
                self.config = config
            
            def execute(self, context: Dict[str, Any]) -> Any:
                # Plugin implementation
                return result
        ```
    """
    
    def __init__(self):
        """Initialize the plugin."""
        self._metadata: Optional[PluginMetadata] = None
        self._config: Dict[str, Any] = {}
        self._enabled: bool = True
        self._context: Dict[str, Any] = {}
    
    @abstractmethod
    def get_metadata(self) -> PluginMetadata:
        """
        Get plugin metadata.
        
        Returns:
            PluginMetadata: Plugin metadata information
        """
        pass
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the plugin with configuration.
        
        Args:
            config: Plugin configuration
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute the plugin with given context.
        
        Args:
            context: Execution context
            
        Returns:
            Any: Plugin execution result
        """
        pass
    
    def validate_config(self, config: Dict[str, Any]) -> List[str]:
        """
        Validate plugin configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            List[str]: List of validation errors
        """
        return []
    
    def get_dependencies(self) -> List[str]:
        """
        Get plugin dependencies.
        
        Returns:
            List[str]: List of required dependencies
        """
        metadata = self.get_metadata()
        return metadata.dependencies if metadata else []
    
    def is_compatible(self, version: str) -> bool:
        """
        Check if plugin is compatible with given Celestra version.
        
        Args:
            version: Celestra version
            
        Returns:
            bool: True if compatible
        """
        return True  # Default implementation
    
    def pre_execute(self, context: Dict[str, Any]) -> None:
        """
        Pre-execution hook.
        
        Args:
            context: Execution context
        """
        pass
    
    def post_execute(self, context: Dict[str, Any], result: Any) -> None:
        """
        Post-execution hook.
        
        Args:
            context: Execution context
            result: Execution result
        """
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        pass
    
    @property
    def enabled(self) -> bool:
        """Check if plugin is enabled."""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Set plugin enabled state."""
        self._enabled = value
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get plugin configuration."""
        return self._config.copy()
    
    @property
    def context(self) -> Dict[str, Any]:
        """Get plugin context."""
        return self._context.copy()


class BuilderPlugin(PluginBase):
    """
    Base class for builder plugins.
    
    Builder plugins create custom resource builders that extend
    the core Celestraa DSL with new resource types.
    """
    
    @abstractmethod
    def get_builder_class(self) -> Type:
        """
        Get the builder class provided by this plugin.
        
        Returns:
            Type: Builder class
        """
        pass
    
    @abstractmethod
    def get_resource_types(self) -> List[str]:
        """
        Get the resource types this plugin can build.
        
        Returns:
            List[str]: List of resource types
        """
        pass


class OutputPlugin(PluginBase):
    """
    Base class for output format plugins.
    
    Output plugins provide custom output formats beyond the
    built-in Kubernetes YAML and Docker Compose formats.
    """
    
    @abstractmethod
    def get_output_format(self) -> str:
        """
        Get the output format name.
        
        Returns:
            str: Output format name
        """
        pass
    
    @abstractmethod
    def generate_output(self, resources: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        """
        Generate output in the plugin's format.
        
        Args:
            resources: List of Kubernetes resources
            config: Output configuration
            
        Returns:
            str: Generated output
        """
        pass
    
    def get_file_extension(self) -> str:
        """
        Get the file extension for this output format.
        
        Returns:
            str: File extension
        """
        return ".yaml"


class ValidatorPlugin(PluginBase):
    """
    Base class for validator plugins.
    
    Validator plugins provide custom validation logic for
    resources and configurations.
    """
    
    @abstractmethod
    def validate_resource(self, resource: Dict[str, Any]) -> List[str]:
        """
        Validate a Kubernetes resource.
        
        Args:
            resource: Kubernetes resource to validate
            
        Returns:
            List[str]: List of validation errors
        """
        pass
    
    def get_validation_scope(self) -> List[str]:
        """
        Get the resource types this validator can validate.
        
        Returns:
            List[str]: List of resource types
        """
        return ["*"]  # All resources by default


class TransformerPlugin(PluginBase):
    """
    Base class for transformer plugins.
    
    Transformer plugins modify resources before they are output,
    allowing for custom transformations and modifications.
    """
    
    @abstractmethod
    def transform_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a Kubernetes resource.
        
        Args:
            resource: Resource to transform
            
        Returns:
            Dict[str, Any]: Transformed resource
        """
        pass
    
    def get_transformation_order(self) -> int:
        """
        Get the execution order for this transformer.
        
        Returns:
            int: Execution order (lower numbers execute first)
        """
        return 100


class HookPlugin(PluginBase):
    """
    Base class for lifecycle hook plugins.
    
    Hook plugins provide lifecycle hooks that execute at specific
    points during the resource generation process.
    """
    
    @abstractmethod
    def get_hook_points(self) -> List[str]:
        """
        Get the hook points this plugin handles.
        
        Returns:
            List[str]: List of hook points (e.g., "pre_generate", "post_generate")
        """
        pass
    
    @abstractmethod
    def execute_hook(self, hook_point: str, context: Dict[str, Any]) -> None:
        """
        Execute hook at the specified point.
        
        Args:
            hook_point: Hook point name
            context: Hook execution context
        """
        pass


class TemplatePlugin(PluginBase):
    """
    Base class for template engine plugins.
    
    Template plugins provide custom template engines for
    generating resources from templates.
    """
    
    @abstractmethod
    def get_template_engine(self) -> str:
        """
        Get the template engine name.
        
        Returns:
            str: Template engine name
        """
        pass
    
    @abstractmethod
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
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
    def get_supported_extensions(self) -> List[str]:
        """
        Get supported template file extensions.
        
        Returns:
            List[str]: List of file extensions
        """
        pass


# Plugin registry for built-in plugins
_PLUGIN_REGISTRY: Dict[str, Type[PluginBase]] = {}


def register_plugin(plugin_class: Type[PluginBase]) -> None:
    """
    Register a plugin class.
    
    Args:
        plugin_class: Plugin class to register
    """
    if not issubclass(plugin_class, PluginBase):
        raise ValueError("Plugin class must inherit from PluginBase")
    
    plugin_instance = plugin_class()
    metadata = plugin_instance.get_metadata()
    _PLUGIN_REGISTRY[metadata.name] = plugin_class


def get_registered_plugins() -> Dict[str, Type[PluginBase]]:
    """
    Get all registered plugins.
    
    Returns:
        Dict[str, Type[PluginBase]]: Dictionary of plugin name to plugin class
    """
    return _PLUGIN_REGISTRY.copy()


def plugin_decorator(plugin_type: PluginType):
    """
    Decorator for automatically registering plugins.
    
    Args:
        plugin_type: Type of plugin
        
    Returns:
        Decorator function
    """
    def decorator(cls):
        if not issubclass(cls, PluginBase):
            raise ValueError("Class must inherit from PluginBase")
        
        register_plugin(cls)
        return cls
    
    return decorator


# Example plugin implementations

@plugin_decorator(PluginType.VALIDATOR)
class ResourceNameValidator(ValidatorPlugin):
    """Example validator plugin for resource names."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="resource-name-validator",
            version="1.0.0",
            description="Validates Kubernetes resource names",
            author="Celestra Team",
            plugin_type=PluginType.VALIDATOR,
            tags=["validation", "naming"]
        )
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config
        self._max_length = config.get("max_length", 63)
        self._allowed_pattern = config.get("pattern", r"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$")
    
    def execute(self, context: Dict[str, Any]) -> Any:
        resources = context.get("resources", [])
        errors = []
        
        for resource in resources:
            resource_errors = self.validate_resource(resource)
            errors.extend(resource_errors)
        
        return errors
    
    def validate_resource(self, resource: Dict[str, Any]) -> List[str]:
        import re
        
        errors = []
        name = resource.get("metadata", {}).get("name", "")
        
        if not name:
            errors.append("Resource name is required")
            return errors
        
        if len(name) > self._max_length:
            errors.append(f"Resource name '{name}' exceeds maximum length of {self._max_length}")
        
        if not re.match(self._allowed_pattern, name):
            errors.append(f"Resource name '{name}' does not match required pattern")
        
        return errors


@plugin_decorator(PluginType.TRANSFORMER)
class LabelTransformer(TransformerPlugin):
    """Example transformer plugin for adding standard labels."""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="label-transformer",
            version="1.0.0",
            description="Adds standard labels to all resources",
            author="Celestra Team",
            plugin_type=PluginType.TRANSFORMER,
            tags=["labels", "transformation"]
        )
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self._config = config
        self._standard_labels = config.get("labels", {
            "app.kubernetes.io/managed-by": "Celestra",
            "app.kubernetes.io/created-by": "Celestra-dsl"
        })
    
    def execute(self, context: Dict[str, Any]) -> Any:
        resources = context.get("resources", [])
        transformed_resources = []
        
        for resource in resources:
            transformed_resource = self.transform_resource(resource)
            transformed_resources.append(transformed_resource)
        
        return transformed_resources
    
    def transform_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        # Add standard labels to metadata
        if "metadata" not in resource:
            resource["metadata"] = {}
        
        if "labels" not in resource["metadata"]:
            resource["metadata"]["labels"] = {}
        
        # Merge standard labels (don't override existing ones)
        for key, value in self._standard_labels.items():
            if key not in resource["metadata"]["labels"]:
                resource["metadata"]["labels"][key] = value
        
        return resource
    
    def get_transformation_order(self) -> int:
        return 10  # Execute early in the transformation pipeline 