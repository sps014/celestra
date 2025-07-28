#!/usr/bin/env python3
"""
Plugins Test Suite.

Tests for Celestra plugin system:
- PluginManager (plugin loading and management)
- PluginBase (plugin interface)
- TemplateManager (template management)
"""

import pytest
import os

from src.celestra import PluginManager, PluginBase, TemplateManager
from .utils import TestHelper, MockKubernetesCluster


class TestPluginManager:
    """Test cases for the PluginManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("plugin_manager_tests")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_plugin_loading(self):
        manager = PluginManager()
        
        # Note: PluginManager loads plugins from files, not direct registration
        # Test that the plugin manager can discover plugins
        plugins = manager.discover_plugins("./plugins")
        assert isinstance(plugins, list)
        
        # Test plugin loading functionality exists
        assert hasattr(manager, 'load_plugin')
        assert hasattr(manager, 'get_loaded_plugins')

    def test_plugin_execution(self):
        manager = PluginManager()
        
        # Test plugin execution functionality exists
        assert hasattr(manager, 'execute_plugins')
        
        # Test get loaded plugins
        loaded_plugins = manager.get_loaded_plugins()
        assert isinstance(loaded_plugins, list)


class TestTemplateManager:
    """Test cases for the TemplateManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("template_manager_tests")
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_template_rendering(self):
        template_manager = TemplateManager()
        
        # Test that template manager can add and list templates
        simple_template = "kind: Deployment"
        template_manager.add_template("simple", simple_template)
        
        # Check that template was added
        templates = template_manager.list_templates()
        assert "simple" in templates
        
        # Test basic template functionality
        rendered = template_manager.render_template("simple", {})
        assert "Deployment" in rendered


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 