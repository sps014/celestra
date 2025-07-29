# Plugin System

The Celestra DSL includes a comprehensive plugin system that allows you to extend and customize the framework's functionality. The plugin system supports multiple plugin types, custom template engines, and provides a robust foundation for building custom extensions.

## Overview

```python
from celestra.plugins import PluginManager, PluginBase, PluginType, TemplateManager

# Basic plugin usage
manager = PluginManager()
manager.discover_plugins("./plugins")
manager.load_plugin("my-custom-plugin", {"config": "value"})

# Template management
template_manager = TemplateManager()
template_manager.add_template_directory("./templates")
rendered = template_manager.render_template("deployment.yaml", {"name": "app"})
```

## Plugin Types

The plugin system supports several types of plugins:

### 1. Builder Plugins
Extend the DSL with custom resource builders.

### 2. Output Plugins
Create custom output formats for generated resources.

### 3. Validator Plugins
Add custom validation logic for resources.

### 4. Transformer Plugins
Transform resources during generation.

### 5. Hook Plugins
Execute custom logic at specific lifecycle points.

### 6. Template Plugins
Provide custom template engines.

## Plugin Manager

The `PluginManager` class handles plugin discovery, loading, and execution.

### Basic Usage

```python
from celestra.plugins import PluginManager

# Initialize plugin manager
manager = PluginManager()

# Discover plugins in directory
discovered = manager.discover_plugins("./plugins")

# Load a specific plugin
manager.load_plugin("my-plugin", {"config": "value"})

# Execute plugins of a specific type
results = manager.execute_plugins(PluginType.VALIDATOR, {"resources": resources})
```

### Core API Functions

#### discover_plugins(plugin_dir: Union[str, Path]) -> List[str]
Discover plugins in a directory.

```python
# Discover plugins in directory
discovered = manager.discover_plugins("./plugins")

# Discover plugins in multiple directories
discovered = manager.discover_plugins(["./plugins", "./custom-plugins"])
```

#### load_plugin(plugin_name: str, config: Optional[Dict[str, Any]] = None) -> bool
Load a specific plugin with configuration.

```python
# Load plugin with configuration
success = manager.load_plugin("my-plugin", {
    "api_version": "v1",
    "namespace": "production"
})

# Load plugin without configuration
success = manager.load_plugin("my-plugin")
```

#### unload_plugin(plugin_name: str) -> bool
Unload a plugin.

```python
# Unload plugin
success = manager.unload_plugin("my-plugin")
```

#### get_loaded_plugins(plugin_type: Optional[PluginType] = None) -> List[str]
Get list of loaded plugins.

```python
# Get all loaded plugins
all_plugins = manager.get_loaded_plugins()

# Get plugins of specific type
validator_plugins = manager.get_loaded_plugins(PluginType.VALIDATOR)
```

#### get_plugin_metadata(plugin_name: str) -> Optional[PluginMetadata]
Get metadata for a plugin.

```python
# Get plugin metadata
metadata = manager.get_plugin_metadata("my-plugin")
if metadata:
    print(f"Plugin: {metadata.name}, Version: {metadata.version}")
```

#### execute_plugins(plugin_type: PluginType, context: Dict[str, Any]) -> Any
Execute plugins of a specific type.

```python
# Execute validator plugins
errors = manager.execute_plugins(PluginType.VALIDATOR, {
    "resources": resources,
    "namespace": "production"
})

# Execute transformer plugins
transformed = manager.execute_plugins(PluginType.TRANSFORMER, {
    "resources": resources
})
```

#### execute_hook(hook_point: str, context: Dict[str, Any]) -> None
Execute hook plugins at a specific point.

```python
# Execute pre-deployment hook
manager.execute_hook("pre-deploy", {
    "resources": resources,
    "environment": "production"
})

# Execute post-deployment hook
manager.execute_hook("post-deploy", {
    "resources": resources,
    "status": "success"
})
```

### Resource Management

#### get_builders() -> Dict[str, Type]
Get all registered builder plugins.

```python
# Get all builders
builders = manager.get_builders()
for name, builder_class in builders.items():
    print(f"Builder: {name}")
```

#### get_output_formats() -> Dict[str, OutputPlugin]
Get all registered output plugins.

```python
# Get all output formats
output_formats = manager.get_output_formats()
for name, plugin in output_formats.items():
    print(f"Output format: {name}")
```

#### validate_resources(resources: List[Dict[str, Any]]) -> List[str]
Validate resources using all validator plugins.

```python
# Validate resources
errors = manager.validate_resources(resources)
for error in errors:
    print(f"Validation error: {error}")
```

#### transform_resources(resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]
Transform resources using all transformer plugins.

```python
# Transform resources
transformed = manager.transform_resources(resources)
```

## Plugin Development

### Creating a Custom Plugin

To create a custom plugin, inherit from the appropriate base class:

```python
from celestra.plugins import PluginBase, PluginType, PluginMetadata

class MyCustomPlugin(PluginBase):
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-custom-plugin",
            version="1.0.0",
            description="My custom plugin",
            author="Developer",
            plugin_type=PluginType.VALIDATOR,
            dependencies=["celestra>=1.0.0"],
            tags=["validation", "custom"]
        )
    
    def initialize(self, config: Dict[str, Any]) -> None:
        self.config = config
    
    def execute(self, context: Dict[str, Any]) -> Any:
        # Plugin implementation
        return result
```

### Plugin Types and Base Classes

#### BuilderPlugin
For creating custom resource builders.

```python
from celestra.plugins import BuilderPlugin

class MyBuilderPlugin(BuilderPlugin):
    def get_builder_class(self) -> Type:
        return MyCustomBuilder
    
    def get_resource_types(self) -> List[str]:
        return ["MyCustomResource"]
```

#### OutputPlugin
For creating custom output formats.

```python
from celestra.plugins import OutputPlugin

class MyOutputPlugin(OutputPlugin):
    def get_output_format(self) -> str:
        return "my-format"
    
    def generate_output(self, resources: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
        # Generate custom output
        return output_string
    
    def get_file_extension(self) -> str:
        return ".my"
```

#### ValidatorPlugin
For custom validation logic.

```python
from celestra.plugins import ValidatorPlugin

class MyValidatorPlugin(ValidatorPlugin):
    def validate_resource(self, resource: Dict[str, Any]) -> List[str]:
        errors = []
        # Custom validation logic
        return errors
    
    def get_validation_scope(self) -> List[str]:
        return ["Deployment", "Service"]
```

#### TransformerPlugin
For transforming resources.

```python
from celestra.plugins import TransformerPlugin

class MyTransformerPlugin(TransformerPlugin):
    def transform_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        # Transform resource
        return transformed_resource
    
    def get_transformation_order(self) -> int:
        return 1  # Lower numbers execute first
```

#### HookPlugin
For lifecycle hooks.

```python
from celestra.plugins import HookPlugin

class MyHookPlugin(HookPlugin):
    def get_hook_points(self) -> List[str]:
        return ["pre-deploy", "post-deploy"]
    
    def execute_hook(self, hook_point: str, context: Dict[str, Any]) -> None:
        if hook_point == "pre-deploy":
            # Pre-deployment logic
            pass
        elif hook_point == "post-deploy":
            # Post-deployment logic
            pass
```

#### TemplatePlugin
For custom template engines.

```python
from celestra.plugins import TemplatePlugin

class MyTemplatePlugin(TemplatePlugin):
    def get_template_engine(self) -> str:
        return "my-engine"
    
    def render_template(self, template: str, variables: Dict[str, Any]) -> str:
        # Render template
        return rendered_template
    
    def get_supported_extensions(self) -> List[str]:
        return [".my", ".template"]
```

### Plugin Decorators

Use the `@plugin_decorator` to automatically register plugins:

```python
from celestra.plugins import plugin_decorator, PluginType

@plugin_decorator(PluginType.VALIDATOR)
class MyValidatorPlugin(ValidatorPlugin):
    # Plugin implementation
    pass
```

### Plugin Configuration

Plugins can be configured with custom settings:

```python
# Plugin configuration
config = {
    "api_version": "v1",
    "namespace": "production",
    "labels": {
        "environment": "production",
        "team": "platform"
    },
    "annotations": {
        "description": "Production deployment"
    }
}

# Load plugin with configuration
manager.load_plugin("my-plugin", config)
```

### Plugin Lifecycle

Plugins have a defined lifecycle:

1. **Discovery**: Plugins are discovered in directories
2. **Loading**: Plugins are loaded with configuration
3. **Initialization**: Plugins are initialized with config
4. **Execution**: Plugins are executed when needed
5. **Cleanup**: Plugins are cleaned up when unloaded

```python
# Plugin lifecycle example
plugin = MyCustomPlugin()

# Initialize
plugin.initialize({"config": "value"})

# Pre-execute
plugin.pre_execute({"context": "data"})

# Execute
result = plugin.execute({"context": "data"})

# Post-execute
plugin.post_execute({"context": "data"}, result)

# Cleanup
plugin.cleanup()
```

## Template Manager

The `TemplateManager` class provides comprehensive template management with support for multiple template engines.

### Basic Usage

```python
from celestra.plugins import TemplateManager, TemplateEngine

# Initialize template manager
template_manager = TemplateManager()

# Add template directory
template_manager.add_template_directory("./templates")

# Render template
rendered = template_manager.render_template("deployment.yaml", {
    "name": "app",
    "image": "nginx:latest",
    "replicas": 3
})
```

### Core API Functions

#### add_template_directory(directory: Union[str, Path]) -> None
Add a directory containing templates.

```python
# Add template directory
template_manager.add_template_directory("./templates")

# Add multiple directories
template_manager.add_template_directory(["./templates", "./custom-templates"])
```

#### add_template(name: str, content: str) -> None
Add a template by name and content.

```python
# Add template
template_manager.add_template("deployment.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
spec:
  replicas: ${replicas}
  selector:
    matchLabels:
      app: ${name}
  template:
    metadata:
      labels:
        app: ${name}
    spec:
      containers:
      - name: ${name}
        image: ${image}
""")
```

#### get_template(name: str) -> Optional[str]
Get a template by name.

```python
# Get template
template = template_manager.get_template("deployment.yaml")
if template:
    print(f"Template: {template}")
```

#### list_templates() -> List[str]
List all available templates.

```python
# List templates
templates = template_manager.list_templates()
for template in templates:
    print(f"Template: {template}")
```

#### render_template(template_name: str, variables: Dict[str, Any], engine: Optional[TemplateEngine] = None) -> str
Render a template with variables.

```python
# Render template with variables
rendered = template_manager.render_template("deployment.yaml", {
    "name": "app",
    "image": "nginx:latest",
    "replicas": 3
})

# Render with specific engine
rendered = template_manager.render_template("deployment.yaml", {
    "name": "app"
}, engine=TemplateEngine.JINJA2)
```

#### render_string(template_content: str, variables: Dict[str, Any], engine: TemplateEngine = TemplateEngine.SIMPLE) -> str
Render template content directly.

```python
# Render template string
template_content = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
spec:
  replicas: ${replicas}
"""

rendered = template_manager.render_string(template_content, {
    "name": "app",
    "replicas": 3
})
```

### Template Engines

The template manager supports multiple template engines:

#### Simple Template Engine
Basic string substitution with `${variable}` or `{variable}` syntax.

```python
# Simple template
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
spec:
  replicas: ${replicas}
"""

rendered = template_manager.render_string(template, {
    "name": "app",
    "replicas": 3
}, engine=TemplateEngine.SIMPLE)
```

#### Jinja2 Template Engine
Full Jinja2 template functionality with filters and functions.

```python
# Jinja2 template
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ name | k8s_name }}
  labels:
    {% for key, value in labels.items() %}
    {{ key }}: {{ value }}
    {% endfor %}
spec:
  replicas: {{ replicas }}
"""

rendered = template_manager.render_string(template, {
    "name": "my-app",
    "labels": {"environment": "production"},
    "replicas": 3
}, engine=TemplateEngine.JINJA2)
```

#### Golang Template Engine
Go-style template syntax.

```python
# Golang template
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .name }}
spec:
  replicas: {{ .replicas }}
"""

rendered = template_manager.render_string(template, {
    "name": "app",
    "replicas": 3
}, engine=TemplateEngine.GOLANG)
```

#### Mustache Template Engine
Mustache template syntax.

```python
# Mustache template
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{name}}
spec:
  replicas: {{replicas}}
  {{#hasLabels}}
  labels:
    {{#labels}}
    {{key}}: {{value}}
    {{/labels}}
  {{/hasLabels}}
"""

rendered = template_manager.render_string(template, {
    "name": "app",
    "replicas": 3,
    "hasLabels": True,
    "labels": [
        {"key": "environment", "value": "production"}
    ]
}, engine=TemplateEngine.MUSTACHE)
```

### Custom Template Functions

Add custom functions to templates:

```python
# Add custom function
def custom_function(value):
    return f"custom-{value}"

template_manager.add_function("custom", custom_function)

# Use in template
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ custom(name) }}
"""
```

### Global Variables

Set global variables for all templates:

```python
# Set global variables
template_manager.set_global_variable("environment", "production")
template_manager.set_global_variable("team", "platform")

# Use in templates
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
  labels:
    environment: ${environment}
    team: ${team}
"""
```

### Built-in Template Functions

The template manager provides several built-in functions:

#### include_template(template_name: str, variables: Dict[str, Any] = None) -> str
Include another template.

```python
# Include template
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
spec:
  template:
    spec:
      containers:
      ${include_template("container.yaml", {"name": name, "image": image})}
"""
```

#### default(value: Any, default_value: Any) -> Any
Provide default value if variable is None.

```python
# Use default value
template = """
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: ${default(replicas, 1)}
"""
```

#### upper(value: str) -> str
Convert string to uppercase.

```python
# Convert to uppercase
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${upper(name)}
"""
```

#### lower(value: str) -> str
Convert string to lowercase.

```python
# Convert to lowercase
template = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${lower(name)}
"""
```

#### indent(value: str, spaces: int = 2) -> str
Indent text by specified number of spaces.

```python
# Indent text
template = """
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      ${indent(container_spec, 6)}
"""
```

## Complete Example

Here's a complete example of using the plugin system:

```python
from celestra.plugins import PluginManager, TemplateManager, PluginType

# Initialize managers
plugin_manager = PluginManager()
template_manager = TemplateManager()

# Discover and load plugins
plugin_manager.discover_plugins("./plugins")
plugin_manager.load_plugin("my-validator", {"strict": True})
plugin_manager.load_plugin("my-transformer", {"add-labels": True})

# Add templates
template_manager.add_template_directory("./templates")
template_manager.add_template("deployment.yaml", """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ${name}
  labels:
    app: ${name}
    environment: ${environment}
spec:
  replicas: ${replicas}
  selector:
    matchLabels:
      app: ${name}
  template:
    metadata:
      labels:
        app: ${name}
    spec:
      containers:
      - name: ${name}
        image: ${image}
        ports:
        - containerPort: ${port}
""")

# Define resources
resources = [
    {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": "app"},
        "spec": {"replicas": 3}
    }
]

# Validate resources
errors = plugin_manager.validate_resources(resources)
if errors:
    print("Validation errors:", errors)

# Transform resources
transformed = plugin_manager.transform_resources(resources)

# Render templates
for resource in transformed:
    rendered = template_manager.render_template("deployment.yaml", {
        "name": resource["metadata"]["name"],
        "environment": "production",
        "replicas": resource["spec"]["replicas"],
        "image": "nginx:latest",
        "port": 80
    })
    print(rendered)

# Execute hooks
plugin_manager.execute_hook("pre-deploy", {"resources": transformed})
plugin_manager.execute_hook("post-deploy", {"resources": transformed})
```

## Plugin Development Best Practices

### 1. **Use Appropriate Plugin Types**
```python
# ✅ Good: Use specific plugin type
class MyValidatorPlugin(ValidatorPlugin):
    def validate_resource(self, resource: Dict[str, Any]) -> List[str]:
        # Validation logic
        pass

# ❌ Bad: Use generic PluginBase for specific functionality
class MyValidatorPlugin(PluginBase):
    # Generic implementation
    pass
```

### 2. **Provide Comprehensive Metadata**
```python
# ✅ Good: Provide complete metadata
def get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        description="My custom plugin",
        author="Developer",
        plugin_type=PluginType.VALIDATOR,
        dependencies=["celestra>=1.0.0"],
        tags=["validation", "custom"]
    )

# ❌ Bad: Minimal metadata
def get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        description="My plugin",
        author="Dev",
        plugin_type=PluginType.VALIDATOR
    )
```

### 3. **Handle Configuration Properly**
```python
# ✅ Good: Validate configuration
def initialize(self, config: Dict[str, Any]) -> None:
    errors = self.validate_config(config)
    if errors:
        raise ValueError(f"Invalid configuration: {errors}")
    self.config = config

# ❌ Bad: No configuration validation
def initialize(self, config: Dict[str, Any]) -> None:
    self.config = config
```

### 4. **Use Plugin Decorators**
```python
# ✅ Good: Use decorator for automatic registration
@plugin_decorator(PluginType.VALIDATOR)
class MyValidatorPlugin(ValidatorPlugin):
    pass

# ❌ Bad: Manual registration
class MyValidatorPlugin(ValidatorPlugin):
    pass
# Manual registration required
```

### 5. **Implement Proper Error Handling**
```python
# ✅ Good: Proper error handling
def execute(self, context: Dict[str, Any]) -> Any:
    try:
        # Plugin logic
        return result
    except Exception as e:
        self._logger.error(f"Plugin execution failed: {e}")
        return None

# ❌ Bad: No error handling
def execute(self, context: Dict[str, Any]) -> Any:
    # Plugin logic without error handling
    return result
```

### 6. **Use Template Engines Appropriately**
```python
# ✅ Good: Use appropriate template engine
# Simple substitution
template_manager.render_string(template, variables, TemplateEngine.SIMPLE)

# Complex logic
template_manager.render_string(template, variables, TemplateEngine.JINJA2)

# ❌ Bad: Use complex engine for simple substitution
template_manager.render_string(simple_template, variables, TemplateEngine.JINJA2)
```

## Related Components

- **[App](../core/app.md)** - For stateless applications
- **[StatefulApp](../core/stateful-app.md)** - For stateful applications
- **[CustomResource](custom-resource.md)** - For custom Kubernetes resources
- **[Components Overview](index.md)** - Explore all available components

## Next Steps

- **[Examples](../examples/index.md)** - See real-world examples
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides
- **[Advanced Features](advanced-features.md)** - Advanced plugin development 