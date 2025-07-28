"""
Utility helper functions for Celestra.

This module contains common utility functions used throughout the Celestra package
for validation, formatting, and common operations.
"""

import re
import yaml
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


def validate_name(name: str) -> bool:
    """
    Validate Kubernetes resource name according to RFC 1123.
    
    Args:
        name: The name to validate
        
    Returns:
        bool: True if name is valid, False otherwise
    """
    pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
    return bool(re.match(pattern, name)) and len(name) <= 253


def validate_label_key(key: str) -> bool:
    """
    Validate Kubernetes label key.
    
    Args:
        key: The label key to validate
        
    Returns:
        bool: True if key is valid, False otherwise
    """
    if '/' in key:
        prefix, name = key.rsplit('/', 1)
        return validate_dns_subdomain(prefix) and validate_label_name(name)
    return validate_label_name(key)


def validate_label_name(name: str) -> bool:
    """
    Validate Kubernetes label name part.
    
    Args:
        name: The label name to validate
        
    Returns:
        bool: True if name is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9]([-_.a-zA-Z0-9]*[a-zA-Z0-9])?$'
    return bool(re.match(pattern, name)) and len(name) <= 63


def validate_dns_subdomain(subdomain: str) -> bool:
    """
    Validate DNS subdomain.
    
    Args:
        subdomain: The subdomain to validate
        
    Returns:
        bool: True if subdomain is valid, False otherwise
    """
    pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*$'
    return bool(re.match(pattern, subdomain)) and len(subdomain) <= 253


def normalize_name(name: str) -> str:
    """
    Normalize a name to be Kubernetes-compatible.
    
    Args:
        name: The name to normalize
        
    Returns:
        str: Normalized name
    """
    # Convert to lowercase
    normalized = name.lower()
    
    # Replace invalid characters with hyphens
    normalized = re.sub(r'[^a-z0-9\-]', '-', normalized)
    
    # Remove leading/trailing hyphens
    normalized = normalized.strip('-')
    
    # Ensure it doesn't start or end with hyphen
    while normalized.startswith('-'):
        normalized = normalized[1:]
    while normalized.endswith('-'):
        normalized = normalized[:-1]
    
    # Ensure minimum length
    if not normalized:
        normalized = 'unnamed'
    
    # Truncate if too long
    if len(normalized) > 253:
        normalized = normalized[:253].rstrip('-')
    
    return normalized


def merge_dicts(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        base: Base dictionary
        override: Dictionary to merge in
        
    Returns:
        Dict[str, Any]: Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result


def parse_resource_string(resource: str) -> tuple:
    """
    Parse Kubernetes resource string (e.g., "1000m", "2Gi").
    
    Args:
        resource: Resource string to parse
        
    Returns:
        tuple: (value, unit)
    """
    match = re.match(r'^(\d+(?:\.\d+)?)\s*([a-zA-Z]*)$', resource.strip())
    if match:
        value, unit = match.groups()
        return float(value), unit
    raise ValueError(f"Invalid resource format: {resource}")


def format_yaml(data: Dict[str, Any]) -> str:
    """
    Format dictionary as YAML string.
    
    Args:
        data: Dictionary to format
        
    Returns:
        str: YAML formatted string
    """
    return yaml.dump(data, default_flow_style=False, sort_keys=False)


def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """
    Format dictionary as JSON string.
    
    Args:
        data: Dictionary to format
        indent: Indentation level
        
    Returns:
        str: JSON formatted string
    """
    return json.dumps(data, indent=indent, sort_keys=False)


def safe_load_yaml(yaml_str: str) -> Dict[str, Any]:
    """
    Safely load YAML string.
    
    Args:
        yaml_str: YAML string to load
        
    Returns:
        Dict[str, Any]: Parsed YAML data
    """
    return yaml.safe_load(yaml_str) or {}


def safe_load_json(json_str: str) -> Dict[str, Any]:
    """
    Safely load JSON string.
    
    Args:
        json_str: JSON string to load
        
    Returns:
        Dict[str, Any]: Parsed JSON data
    """
    return json.loads(json_str)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path
        
    Returns:
        Path: Path object
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def write_file(path: Union[str, Path], content: str) -> None:
    """
    Write content to file, creating directories if needed.
    
    Args:
        path: File path
        content: Content to write
    """
    path_obj = Path(path)
    path_obj.parent.mkdir(parents=True, exist_ok=True)
    path_obj.write_text(content)


def read_file(path: Union[str, Path]) -> str:
    """
    Read content from file.
    
    Args:
        path: File path
        
    Returns:
        str: File content
    """
    return Path(path).read_text()


def sanitize_env_var_name(name: str) -> str:
    """
    Sanitize environment variable name.
    
    Args:
        name: Name to sanitize
        
    Returns:
        str: Sanitized name
    """
    # Convert to uppercase
    sanitized = name.upper()
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^A-Z0-9_]', '_', sanitized)
    
    # Ensure it doesn't start with number
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    
    return sanitized


def generate_labels(name: str, app_type: str = "app", **extra_labels) -> Dict[str, str]:
    """
    Generate standard Kubernetes labels.
    
    Args:
        name: Application name
        app_type: Application type
        **extra_labels: Additional labels
        
    Returns:
        Dict[str, str]: Generated labels
    """
    labels = {
        "app": name,
        "app.kubernetes.io/name": name,
        "app.kubernetes.io/instance": name,
        "app.kubernetes.io/component": app_type,
        "app.kubernetes.io/managed-by": "Celestra",
    }
    
    labels.update(extra_labels)
    return labels


def generate_annotations(**annotations) -> Dict[str, str]:
    """
    Generate standard Kubernetes annotations.
    
    Args:
        **annotations: Annotations to include
        
    Returns:
        Dict[str, str]: Generated annotations
    """
    base_annotations = {
        "celestra.io/generated": "true",
"celestra.io/version": "1.0.0",
    }
    
    base_annotations.update({k: str(v) for k, v in annotations.items()})
    return base_annotations 