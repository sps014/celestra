"""
Base builder class for Celestraa DSL.

This module contains the abstract base class for all DSL builders.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .resource_generator import ResourceGenerator

from ..utils.helpers import generate_labels, generate_annotations


class BaseBuilder(ABC):
    """
    Abstract base class for all DSL builders.
    
    This class provides common functionality and interface for all
    builder classes in the Celestraa DSL.
    """
    
    def __init__(self, name: str):
        """
        Initialize the base builder.
        
        Args:
            name: Name of the resource
        """
        self._name = name
        self._namespace = "default"
        self._labels: Dict[str, str] = {}
        self._annotations: Dict[str, str] = {}
        self._config: Dict[str, Any] = {}
        
        # Set default labels
        self._labels.update(generate_labels(name))
        
        # Set default annotations
        self._annotations.update(generate_annotations())
    
    @property
    def name(self) -> str:
        """Get the resource name."""
        return self._name
    
    @property
    def namespace(self) -> str:
        """Get the resource namespace."""
        return self._namespace
    
    @property
    def labels(self) -> Dict[str, str]:
        """Get the resource labels."""
        return self._labels.copy()
    
    @property
    def annotations(self) -> Dict[str, str]:
        """Get the resource annotations."""
        return self._annotations.copy()
    
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
            labels: Dictionary of labels
            
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
            annotations: Dictionary of annotations
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._annotations.update(annotations)
        return self
    
    def validate(self) -> List[str]:
        """
        Validate the builder configuration.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Validate name
        if not self._name:
            errors.append("Name is required")
        elif not isinstance(self._name, str):
            errors.append("Name must be a string")
        elif len(self._name) > 63:
            errors.append("Name must be 63 characters or less")
        
        # Validate namespace
        if not self._namespace:
            errors.append("Namespace is required")
        elif not isinstance(self._namespace, str):
            errors.append("Namespace must be a string")
        
        # Validate labels
        for key, value in self._labels.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append(f"Label {key} must have string key and value")
            elif len(key) > 63:
                errors.append(f"Label key {key} must be 63 characters or less")
            elif len(value) > 63:
                errors.append(f"Label value {value} must be 63 characters or less")
        
        # Validate annotations
        for key, value in self._annotations.items():
            if not isinstance(key, str) or not isinstance(value, str):
                errors.append(f"Annotation {key} must have string key and value")
        
        return errors
    
    def _get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self._config.get(key, default)
    
    def _set(self, key: str, value: Any) -> "BaseBuilder":
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
            
        Returns:
            BaseBuilder: Self for method chaining
        """
        self._config[key] = value
        return self
    
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
    
    def __repr__(self) -> str:
        """String representation of the builder."""
        return f"{self.__class__.__name__}(name='{self._name}', namespace='{self._namespace}')"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.__class__.__name__}: {self._name}" 