"""
Simple serialization for Celestra DSL.

Just two methods: serialize() and deserialize().
"""

import json
import importlib
import inspect
from typing import Dict, Any, Union, Type, List
from pathlib import Path

from ..core.base_builder import BaseBuilder


# Global cache for discovered classes - initialized once
_CLASS_MAP: Dict[str, Type[BaseBuilder]] = None


def _discover_classes() -> Dict[str, Type[BaseBuilder]]:
    """
    Discover all BaseBuilder classes - runs only once.
    """
    global _CLASS_MAP
    
    # If already discovered, return cached result
    if _CLASS_MAP is not None:
        return _CLASS_MAP
    
    print("🔍 Discovering Celestra classes...")  # Debug info
    
    class_map = {}
    
    # Get all modules in celestra package
    celestra_module = importlib.import_module("celestra")
    
    # Recursively scan all submodules
    def scan_module(module, prefix=""):
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            
            # Check if it's a class that inherits from BaseBuilder
            if (inspect.isclass(attr) and 
                issubclass(attr, BaseBuilder) and 
                attr != BaseBuilder):
                
                class_name = attr.__name__
                class_map[class_name] = attr
                print(f"  ✓ Found: {class_name}")  # Debug info
            
            # Check if it's a submodule
            elif (inspect.ismodule(attr) and 
                  attr_name.startswith("celestra") and
                  "test" not in attr_name and
                  "example" not in attr_name):
                
                scan_module(attr, prefix + attr_name + ".")
    
    scan_module(celestra_module)
    
    print(f"🎯 Total classes discovered: {len(class_map)}")  # Debug info
    
    # Cache the result globally
    _CLASS_MAP = class_map
    return class_map


def serialize(obj: Any) -> str:
    """
    Serialize ANY DSL object to JSON.
    """
    data = {
        "type": obj.__class__.__name__,
        "name": obj.name,
        "data": {}
    }

    # Get all public attributes (non-private, non-methods)
    for attr_name in dir(obj):
        if not attr_name.startswith('_') and not callable(getattr(obj, attr_name)):
            try:
                value = getattr(obj, attr_name)
                
                # Skip labels and annotations - they'll be handled separately with filtering
                if attr_name in ['labels', 'annotations']:
                    continue
                
                data["data"][attr_name] = value
            except:
                pass

    # Get all private variables that store actual data
    for attr_name in dir(obj):
        if (attr_name.startswith('_') and 
            not attr_name.startswith('__') and 
            not callable(getattr(obj, attr_name))):
            
            try:
                value = getattr(obj, attr_name)
                
                # Skip None, empty values, and internal state
                if value is not None and value != "default":
                    # Convert private name to public name (e.g., _image -> image)
                    public_name = attr_name[1:] if attr_name.startswith('_') else attr_name
                    
                    # Skip labels and annotations - they'll be handled separately with filtering
                    if public_name in ['labels', 'annotations']:
                        continue
                    
                    # Only add if it's meaningful data
                    if (isinstance(value, (str, int, float, bool)) or
                        (isinstance(value, (dict, list)) and value)):
                        data["data"][public_name] = value
                        
            except:
                pass
    
    # Also get config and other important state
    if hasattr(obj, 'config'):
        data["data"]["config"] = obj.config
    
    # Handle labels - filter out auto-generated ones
    if hasattr(obj, 'labels'):
        labels = obj.labels
        if labels:
            # Filter out auto-generated labels
            filtered_labels = {}
            for key, value in labels.items():
                if not key.startswith('app.kubernetes.io/') and key != 'app':
                    filtered_labels[key] = value
            if filtered_labels:
                data["data"]["labels"] = filtered_labels
    
    # Handle annotations - filter out auto-generated ones
    if hasattr(obj, 'annotations'):
        annotations = obj.annotations
        if annotations:
            # Filter out auto-generated annotations
            filtered_annotations = {}
            for key, value in annotations.items():
                if not key.startswith('celestra.io/'):
                    filtered_annotations[key] = value
            if filtered_annotations:
                data["data"]["annotations"] = filtered_annotations
    
    # Handle namespace
    if hasattr(obj, 'namespace'):
        data["data"]["namespace"] = obj.namespace
    
    return json.dumps(data, indent=2, default=str)


def deserialize(json_data: Union[str, Dict[str, Any]]) -> Any:
    """
    Deserialize JSON to DSL object - uses cached class discovery.
    
    Args:
        json_data: JSON string or dict
        
    Returns:
        Any: DSL object
    """
    # Get or create class map (runs discovery only once)
    class_map = _discover_classes()
    
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json.loads(json_data)
    
    # Get class info
    obj_type = data["type"]
    name = data["name"]
    
    # Get class from cached map
    if obj_type not in class_map:
        raise ValueError(f"Unknown class type: {obj_type}. Available: {list(class_map.keys())}")
    
    cls = class_map[obj_type]
    
    # Create object
    obj = cls(name)
    
    # Restore config and other data
    if "data" in data:
        for key, value in data["data"].items():
            # Skip read-only properties like 'name'
            if key == 'name':
                continue
            
            # Handle special cases that need method calls
            if key == 'namespace' and hasattr(obj, 'set_namespace'):
                obj.set_namespace(value)
                continue
            elif key == 'labels' and hasattr(obj, 'add_labels'):
                # Clear existing labels and add new ones
                for label_key, label_value in value.items():
                    if hasattr(obj, 'add_label'):
                        obj.add_label(label_key, label_value)
                continue
            elif key == 'annotations' and hasattr(obj, 'add_annotations'):
                # Clear existing annotations and add new ones
                for ann_key, ann_value in value.items():
                    if hasattr(obj, 'add_annotation'):
                        obj.add_annotation(ann_key, ann_value)
                continue
            
            # Simple approach: restore data directly to private variables
            private_name = f"_{key}"
            if hasattr(obj, private_name):
                setattr(obj, private_name, value)
            elif hasattr(obj, key):
                # If no private attribute exists, try setting the public one
                setattr(obj, key, value)
            else:
                # Skip if neither private nor public attribute exists
                print(f"⚠️  Warning: Neither '{private_name}' nor '{key}' attribute exists on {obj.__class__.__name__}")
    
    return obj


def list_available_classes() -> List[str]:
    """List all available classes for serialization."""
    class_map = _discover_classes()  # Uses cached result
    return list(class_map.keys())


# Optional: Force refresh if needed (for testing)
def refresh_class_discovery() -> None:
    """Force refresh of class discovery (mainly for testing)."""
    global _CLASS_MAP
    _CLASS_MAP = None
    _discover_classes()
