"""
PluginManager class for plugin loading and management in Celestraa DSL.

This module provides comprehensive plugin management including discovery,
loading, configuration, and lifecycle management.
"""

import os
import sys
import importlib
import importlib.util
from typing import Dict, List, Any, Optional, Type, Callable, Union
from pathlib import Path
import logging
import traceback
from .plugin_base import (
    PluginBase, PluginType, PluginMetadata,
    BuilderPlugin, OutputPlugin, ValidatorPlugin,
    TransformerPlugin, HookPlugin, TemplatePlugin,
    get_registered_plugins
)


class PluginManager:
    """
    Plugin manager for Celestraa DSL.
    
    Manages plugin discovery, loading, configuration, and execution
    with support for different plugin types and lifecycle management.
    
    Example:
        ```python
        manager = PluginManager()
        manager.discover_plugins("./plugins")
        manager.load_plugin("my-custom-plugin", {"config": "value"})
        
        # Execute validator plugins
        errors = manager.execute_plugins(PluginType.VALIDATOR, {"resources": resources})
        
        # Transform resources
        transformed = manager.execute_plugins(PluginType.TRANSFORMER, {"resources": resources})
        ```
    """
    
    def __init__(self):
        """Initialize the plugin manager."""
        self._plugins: Dict[str, PluginBase] = {}
        self._plugin_classes: Dict[str, Type[PluginBase]] = {}
        self._plugin_configs: Dict[str, Dict[str, Any]] = {}
        self._hooks: Dict[str, List[PluginBase]] = {}
        self._logger = logging.getLogger(__name__)
        
        # Load built-in plugins
        self._load_builtin_plugins()
    
    def discover_plugins(self, plugin_dir: Union[str, Path]) -> List[str]:
        """
        Discover plugins in a directory.
        
        Args:
            plugin_dir: Directory to search for plugins
            
        Returns:
            List[str]: List of discovered plugin names
        """
        plugin_dir = Path(plugin_dir)
        discovered = []
        
        if not plugin_dir.exists():
            self._logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            return discovered
        
        # Discover Python files
        for plugin_file in plugin_dir.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            
            try:
                plugin_name = plugin_file.stem
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
                
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Look for plugin classes in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        
                        if (isinstance(attr, type) and 
                            issubclass(attr, PluginBase) and 
                            attr != PluginBase):
                            
                            plugin_instance = attr()
                            metadata = plugin_instance.get_metadata()
                            
                            self._plugin_classes[metadata.name] = attr
                            discovered.append(metadata.name)
                            
                            self._logger.info(f"Discovered plugin: {metadata.name}")
                
            except Exception as e:
                self._logger.error(f"Error discovering plugin in {plugin_file}: {e}")
                self._logger.debug(traceback.format_exc())
        
        # Discover Python packages
        for plugin_pkg in plugin_dir.iterdir():
            if (plugin_pkg.is_dir() and 
                (plugin_pkg / "__init__.py").exists() and
                not plugin_pkg.name.startswith("_")):
                
                try:
                    package_discovered = self._discover_package_plugins(plugin_pkg)
                    discovered.extend(package_discovered)
                    
                except Exception as e:
                    self._logger.error(f"Error discovering package plugin {plugin_pkg}: {e}")
                    self._logger.debug(traceback.format_exc())
        
        return discovered
    
    def load_plugin(
        self, 
        plugin_name: str, 
        config: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Load and initialize a plugin.
        
        Args:
            plugin_name: Name of the plugin to load
            config: Plugin configuration
            
        Returns:
            bool: True if plugin loaded successfully
        """
        if plugin_name in self._plugins:
            self._logger.warning(f"Plugin {plugin_name} is already loaded")
            return True
        
        if plugin_name not in self._plugin_classes:
            self._logger.error(f"Plugin {plugin_name} not found")
            return False
        
        try:
            plugin_class = self._plugin_classes[plugin_name]
            plugin = plugin_class()
            
            # Validate configuration
            config = config or {}
            config_errors = plugin.validate_config(config)
            
            if config_errors:
                self._logger.error(f"Plugin {plugin_name} configuration errors: {config_errors}")
                return False
            
            # Initialize plugin
            plugin.initialize(config)
            
            # Store plugin and configuration
            self._plugins[plugin_name] = plugin
            self._plugin_configs[plugin_name] = config
            
            # Register hooks
            if isinstance(plugin, HookPlugin):
                hook_points = plugin.get_hook_points()
                for hook_point in hook_points:
                    if hook_point not in self._hooks:
                        self._hooks[hook_point] = []
                    self._hooks[hook_point].append(plugin)
            
            self._logger.info(f"Loaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error loading plugin {plugin_name}: {e}")
            self._logger.debug(traceback.format_exc())
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            bool: True if plugin unloaded successfully
        """
        if plugin_name not in self._plugins:
            self._logger.warning(f"Plugin {plugin_name} is not loaded")
            return False
        
        try:
            plugin = self._plugins[plugin_name]
            
            # Remove from hooks
            for hook_point, hook_plugins in self._hooks.items():
                if plugin in hook_plugins:
                    hook_plugins.remove(plugin)
            
            # Cleanup plugin
            plugin.cleanup()
            
            # Remove from registry
            del self._plugins[plugin_name]
            del self._plugin_configs[plugin_name]
            
            self._logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self._logger.error(f"Error unloading plugin {plugin_name}: {e}")
            self._logger.debug(traceback.format_exc())
            return False
    
    def get_loaded_plugins(self, plugin_type: Optional[PluginType] = None) -> List[str]:
        """
        Get list of loaded plugins.
        
        Args:
            plugin_type: Filter by plugin type (optional)
            
        Returns:
            List[str]: List of loaded plugin names
        """
        if plugin_type is None:
            return list(self._plugins.keys())
        
        filtered_plugins = []
        for name, plugin in self._plugins.items():
            metadata = plugin.get_metadata()
            if metadata.plugin_type == plugin_type:
                filtered_plugins.append(name)
        
        return filtered_plugins
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """
        Get metadata for a plugin.
        
        Args:
            plugin_name: Plugin name
            
        Returns:
            Optional[PluginMetadata]: Plugin metadata or None if not found
        """
        if plugin_name in self._plugins:
            return self._plugins[plugin_name].get_metadata()
        
        if plugin_name in self._plugin_classes:
            plugin = self._plugin_classes[plugin_name]()
            return plugin.get_metadata()
        
        return None
    
    def execute_plugins(
        self, 
        plugin_type: PluginType, 
        context: Dict[str, Any]
    ) -> Any:
        """
        Execute all plugins of a specific type.
        
        Args:
            plugin_type: Type of plugins to execute
            context: Execution context
            
        Returns:
            Any: Aggregated results from plugin execution
        """
        results = []
        
        for name, plugin in self._plugins.items():
            if not plugin.enabled:
                continue
            
            metadata = plugin.get_metadata()
            if metadata.plugin_type != plugin_type:
                continue
            
            try:
                # Execute pre-hook
                plugin.pre_execute(context)
                
                # Execute plugin
                result = plugin.execute(context)
                results.append(result)
                
                # Execute post-hook
                plugin.post_execute(context, result)
                
                self._logger.debug(f"Executed plugin: {name}")
                
            except Exception as e:
                self._logger.error(f"Error executing plugin {name}: {e}")
                self._logger.debug(traceback.format_exc())
        
        return self._aggregate_results(plugin_type, results)
    
    def execute_hook(self, hook_point: str, context: Dict[str, Any]) -> None:
        """
        Execute hook plugins at a specific hook point.
        
        Args:
            hook_point: Hook point name
            context: Hook execution context
        """
        if hook_point not in self._hooks:
            return
        
        for plugin in self._hooks[hook_point]:
            if not plugin.enabled:
                continue
            
            try:
                plugin.execute_hook(hook_point, context)
                self._logger.debug(f"Executed hook {hook_point} for plugin: {plugin.get_metadata().name}")
                
            except Exception as e:
                plugin_name = plugin.get_metadata().name
                self._logger.error(f"Error executing hook {hook_point} for plugin {plugin_name}: {e}")
                self._logger.debug(traceback.format_exc())
    
    def get_builders(self) -> Dict[str, Type]:
        """
        Get all available builder classes from plugins.
        
        Returns:
            Dict[str, Type]: Dictionary of builder name to builder class
        """
        builders = {}
        
        for plugin in self._plugins.values():
            if isinstance(plugin, BuilderPlugin) and plugin.enabled:
                try:
                    builder_class = plugin.get_builder_class()
                    resource_types = plugin.get_resource_types()
                    
                    for resource_type in resource_types:
                        builders[resource_type] = builder_class
                        
                except Exception as e:
                    plugin_name = plugin.get_metadata().name
                    self._logger.error(f"Error getting builder from plugin {plugin_name}: {e}")
        
        return builders
    
    def get_output_formats(self) -> Dict[str, OutputPlugin]:
        """
        Get all available output format plugins.
        
        Returns:
            Dict[str, OutputPlugin]: Dictionary of format name to output plugin
        """
        formats = {}
        
        for plugin in self._plugins.values():
            if isinstance(plugin, OutputPlugin) and plugin.enabled:
                try:
                    format_name = plugin.get_output_format()
                    formats[format_name] = plugin
                    
                except Exception as e:
                    plugin_name = plugin.get_metadata().name
                    self._logger.error(f"Error getting output format from plugin {plugin_name}: {e}")
        
        return formats
    
    def validate_resources(self, resources: List[Dict[str, Any]]) -> List[str]:
        """
        Validate resources using validator plugins.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[str]: List of validation errors
        """
        context = {"resources": resources}
        validation_results = self.execute_plugins(PluginType.VALIDATOR, context)
        
        # Flatten results
        all_errors = []
        for result in validation_results:
            if isinstance(result, list):
                all_errors.extend(result)
            elif result:
                all_errors.append(str(result))
        
        return all_errors
    
    def transform_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform resources using transformer plugins.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[Dict[str, Any]]: Transformed resources
        """
        # Get transformer plugins sorted by execution order
        transformers = []
        for plugin in self._plugins.values():
            if isinstance(plugin, TransformerPlugin) and plugin.enabled:
                transformers.append(plugin)
        
        transformers.sort(key=lambda p: p.get_transformation_order())
        
        # Apply transformations
        transformed_resources = resources
        
        for transformer in transformers:
            try:
                new_resources = []
                for resource in transformed_resources:
                    transformed = transformer.transform_resource(resource)
                    new_resources.append(transformed)
                
                transformed_resources = new_resources
                
            except Exception as e:
                plugin_name = transformer.get_metadata().name
                self._logger.error(f"Error in transformer plugin {plugin_name}: {e}")
                self._logger.debug(traceback.format_exc())
        
        return transformed_resources
    
    def _load_builtin_plugins(self) -> None:
        """Load built-in plugins."""
        builtin_plugins = get_registered_plugins()
        
        for name, plugin_class in builtin_plugins.items():
            self._plugin_classes[name] = plugin_class
            self._logger.debug(f"Registered built-in plugin: {name}")
    
    def _discover_package_plugins(self, package_dir: Path) -> List[str]:
        """
        Discover plugins in a Python package.
        
        Args:
            package_dir: Package directory
            
        Returns:
            List[str]: List of discovered plugin names
        """
        discovered = []
        package_name = package_dir.name
        
        # Add package to path temporarily
        sys.path.insert(0, str(package_dir.parent))
        
        try:
            module = importlib.import_module(package_name)
            
            # Look for plugin classes
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                if (isinstance(attr, type) and 
                    issubclass(attr, PluginBase) and 
                    attr != PluginBase):
                    
                    plugin_instance = attr()
                    metadata = plugin_instance.get_metadata()
                    
                    self._plugin_classes[metadata.name] = attr
                    discovered.append(metadata.name)
                    
                    self._logger.info(f"Discovered package plugin: {metadata.name}")
        
        finally:
            # Remove from path
            if str(package_dir.parent) in sys.path:
                sys.path.remove(str(package_dir.parent))
        
        return discovered
    
    def _aggregate_results(self, plugin_type: PluginType, results: List[Any]) -> Any:
        """
        Aggregate results from plugin execution.
        
        Args:
            plugin_type: Type of plugins that were executed
            results: List of results from plugin execution
            
        Returns:
            Any: Aggregated result
        """
        if plugin_type == PluginType.VALIDATOR:
            # Flatten validation errors
            all_errors = []
            for result in results:
                if isinstance(result, list):
                    all_errors.extend(result)
                elif result:
                    all_errors.append(str(result))
            return all_errors
        
        elif plugin_type == PluginType.TRANSFORMER:
            # Return the last transformation result
            return results[-1] if results else []
        
        else:
            # Default aggregation
            return results 