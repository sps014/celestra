"""
Base builder class for K8s-Gen DSL.

This module contains the base builder class that provides common functionality
for all DSL builders using the builder pattern.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union, Type, TYPE_CHECKING
from pathlib import Path

from ..utils.helpers import validate_name, normalize_name, generate_labels, generate_annotations

if TYPE_CHECKING:
    from ..output.base_output import OutputFormat


class BaseBuilder(ABC):
    """
    Base class for all K8s-Gen builders.
    
    Provides common functionality and the builder pattern implementation
    for creating Kubernetes resources with a fluent API.
    """
    
    def __init__(self, name: str):
        """
        Initialize the base builder.
        
        Args:
            name: The name of the resource
        """
        if not validate_name(name):
            name = normalize_name(name)
        
        self._name = name
        self._labels: Dict[str, str] = {}
        self._annotations: Dict[str, str] = {}
        self._namespace: Optional[str] = None
        self._config: Dict[str, Any] = {}
        self._validators: List[Any] = []
        self._plugins: List[Any] = []
        
        # Initialize with default labels
        self._labels.update(generate_labels(self._name, self.__class__.__name__.lower()))
        self._annotations.update(generate_annotations())
    
    @property
    def name(self) -> str:
        """Get the resource name."""
        return self._name
    
    @property
    def labels(self) -> Dict[str, str]:
        """Get the resource labels."""
        return self._labels.copy()
    
    @property
    def annotations(self) -> Dict[str, str]:
        """Get the resource annotations."""
        return self._annotations.copy()
    
    @property
    def namespace(self) -> Optional[str]:
        """Get the resource namespace."""
        return self._namespace
    
    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration dictionary."""
        return self._config.copy()
    
    def add_label(self, key: str, value: str) -> "BaseBuilder":
        """
        Add a label to the resource.
        
        Args:
            key: Label key
            value: Label value
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._labels[key] = value
        return self
    
    def add_labels(self, labels: Dict[str, str]) -> "BaseBuilder":
        """
        Add multiple labels to the resource.
        
        Args:
            labels: Dictionary of labels to add
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._labels.update(labels)
        return self
    
    def add_annotation(self, key: str, value: str) -> "BaseBuilder":
        """
        Add an annotation to the resource.
        
        Args:
            key: Annotation key
            value: Annotation value
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._annotations[key] = value
        return self
    
    def add_annotations(self, annotations: Dict[str, str]) -> "BaseBuilder":
        """
        Add multiple annotations to the resource.
        
        Args:
            annotations: Dictionary of annotations to add
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._annotations.update(annotations)
        return self
    
    def set_namespace(self, namespace: str) -> "BaseBuilder":
        """
        Set the namespace for the resource.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._namespace = namespace
        return self
    
    def add_validator(self, validator: Any) -> "BaseBuilder":
        """
        Add a validator for this resource.
        
        Args:
            validator: Validator instance
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._validators.append(validator)
        return self
    
    def add_plugin(self, plugin: Any) -> "BaseBuilder":
        """
        Add a plugin for this resource.
        
        Args:
            plugin: Plugin instance
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._plugins.append(plugin)
        return self
    
    def validate(self) -> List[str]:
        """
        Validate the resource configuration.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Run basic validation
        if not self._name:
            errors.append("Resource name is required")
        
        # Run custom validators
        for validator in self._validators:
            try:
                validator.validate(self)
            except Exception as e:
                errors.append(str(e))
        
        return errors
    
    def _set(self, key: str, value: Any) -> "BaseBuilder":
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._config[key] = value
        return self
    
    def _get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self._config.get(key, default)
    
    def _has(self, key: str) -> bool:
        """
        Check if configuration key exists.
        
        Args:
            key: Configuration key
            
        Returns:
            bool: True if key exists
        """
        return key in self._config
    
    def _merge_config(self, config: Dict[str, Any]) -> "BaseBuilder":
        """
        Merge configuration dictionary.
        
        Args:
            config: Configuration to merge
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._config.update(config)
        return self
    
    @abstractmethod
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resource dictionaries
        """
        pass
    
    def generate(self) -> "ResourceGenerator":
        """
        Generate resources using the generator pattern.
        
        Returns:
            ResourceGenerator: Generator instance for output formatting
        """
        from .resource_generator import ResourceGenerator
        return ResourceGenerator(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the builder to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation
        """
        return {
            "name": self._name,
            "labels": self._labels,
            "annotations": self._annotations,
            "namespace": self._namespace,
            "config": self._config,
            "type": self.__class__.__name__
        }
    
    def clone(self) -> "BaseBuilder":
        """
        Create a deep copy of this builder.
        
        Returns:
            BaseBuilder: Cloned builder
        """
        cloned = self.__class__(self._name)
        cloned._labels = self._labels.copy()
        cloned._annotations = self._annotations.copy()
        cloned._namespace = self._namespace
        cloned._config = self._config.copy()
        cloned._validators = self._validators.copy()
        cloned._plugins = self._plugins.copy()
        return cloned
    
    def __repr__(self) -> str:
        """String representation of the builder."""
        return f"{self.__class__.__name__}(name='{self._name}')"
    
    def __str__(self) -> str:
        """String representation of the builder."""
        return self.__repr__() 