"""
Decorators for Celestraa DSL method annotations.

This module provides decorators to mark methods as specific to certain
output formats or deployment targets.
"""

import functools
import warnings
from typing import Set, Callable, Any, List


def docker_compose_only(func: Callable) -> Callable:
    """
    Decorator to mark methods that only apply to Docker Compose output.
    
    Methods marked with this decorator will show warnings when used
    with Kubernetes output generation.
    
    Example:
        ```python
        @docker_compose_only
        def port_mapping(self, host_port: int, container_port: int):
            # This method only makes sense for Docker Compose
            pass
        ```
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # Mark this instance as having Docker Compose-specific config
        if not hasattr(self, '_docker_compose_methods'):
            self._docker_compose_methods = set()
        self._docker_compose_methods.add(func.__name__)
        
        return func(self, *args, **kwargs)
    
    # Add metadata to the function
    wrapper._output_formats = ['docker-compose']
    wrapper._format_restriction = 'docker-compose-only'
    return wrapper


def kubernetes_only(func: Callable) -> Callable:
    """
    Decorator to mark methods that only apply to Kubernetes output.
    
    Example:
        ```python
        @kubernetes_only
        def node_selector(self, selectors: dict):
            # This method only makes sense for Kubernetes
            pass
        ```
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, '_kubernetes_methods'):
            self._kubernetes_methods = set()
        self._kubernetes_methods.add(func.__name__)
        
        return func(self, *args, **kwargs)
    
    wrapper._output_formats = ['kubernetes']
    wrapper._format_restriction = 'kubernetes-only'
    return wrapper


def output_formats(*formats: str) -> Callable:
    """
    Decorator to specify which output formats support a method.
    
    Args:
        *formats: Supported output formats ('kubernetes', 'docker-compose', 'helm', etc.)
        
    Example:
        ```python
        @output_formats('kubernetes', 'helm')
        def node_affinity(self, affinity: dict):
            pass
        ```
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            if not hasattr(self, '_format_methods'):
                self._format_methods = {}
            self._format_methods[func.__name__] = set(formats)
            
            return func(self, *args, **kwargs)
        
        wrapper._output_formats = list(formats)
        wrapper._format_restriction = f"formats: {', '.join(formats)}"
        return wrapper
    
    return decorator


def format_warning(builder, output_format: str) -> List[str]:
    """
    Generate warnings for methods that don't apply to the specified output format.
    
    Args:
        builder: The builder instance
        output_format: Target output format ('kubernetes', 'docker-compose', etc.)
        
    Returns:
        List[str]: List of warning messages
    """
    warnings_list = []
    
    # Check Docker Compose-only methods used with Kubernetes
    if output_format == 'kubernetes' and hasattr(builder, '_docker_compose_methods'):
        for method in builder._docker_compose_methods:
            warnings_list.append(
                f"⚠️  Method '{method}()' is Docker Compose-specific and will be ignored in Kubernetes output. "
                f"For Kubernetes, use 'port()' + 'Service' instead of 'port_mapping()'."
            )
    
    # Check Kubernetes-only methods used with Docker Compose
    if output_format == 'docker-compose' and hasattr(builder, '_kubernetes_methods'):
        for method in builder._kubernetes_methods:
            warnings_list.append(
                f"⚠️  Method '{method}()' is Kubernetes-specific and will be ignored in Docker Compose output."
            )
    
    # Check format-specific methods
    if hasattr(builder, '_format_methods'):
        for method, supported_formats in builder._format_methods.items():
            if output_format not in supported_formats:
                warnings_list.append(
                    f"⚠️  Method '{method}()' only supports: {', '.join(supported_formats)}. "
                    f"Will be ignored in {output_format} output."
                )
    
    return warnings_list


def show_format_warnings(builder, output_format: str) -> None:
    """
    Show warnings for incompatible methods.
    
    Args:
        builder: The builder instance
        output_format: Target output format
    """
    warnings_list = format_warning(builder, output_format)
    for warning in warnings_list:
        warnings.warn(warning, UserWarning)
        print(warning) 