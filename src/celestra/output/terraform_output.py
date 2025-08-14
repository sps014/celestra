"""
TerraformOutput class for generating Terraform modules in Celestra DSL.

This module provides Terraform module generation for Kubernetes resources
with proper HCL syntax and Terraform best practices.
"""

import os
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from .base_output import OutputFormat


class TerraformOutput(OutputFormat):
    
    def generate(self, output_dir: str) -> None:
        """Generate method required by OutputFormat base class."""
        return self.generate_files(output_dir)
    """
    Output format for generating Terraform modules.
    
    Generates Terraform configuration files with proper HCL syntax,
    variables, outputs, and provider configurations.
    
    Example:
        ```python
        terraform_output = (TerraformOutput("my-app")
            .set_provider_version("~> 2.0")
            .add_variable("namespace", "string", "production")
            .add_variable("replicas", "number", 3)
            .add_output("service_endpoint", "kubernetes_service.app.status.0.load_balancer.0.ingress.0.hostname")
            .enable_remote_state("s3", {"bucket": "tfstate", "key": "app.tfstate"}))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the Terraform output formatter.
        
        Args:
            name: Name of the Terraform module
        """
        super().__init__()
        self._name = name
        self._provider_version: str = "~> 2.0"
        self._variables: Dict[str, Dict[str, Any]] = {}
        self._outputs: Dict[str, Dict[str, Any]] = {}
        self._locals: Dict[str, Any] = {}
        self._remote_state: Optional[Dict[str, Any]] = None
        self._required_providers: Dict[str, Dict[str, Any]] = {}
        self._data_sources: List[Dict[str, Any]] = []
        self._modules: List[Dict[str, Any]] = []
        self._resources: List[Any] = []
        
        # Default required providers
        self._required_providers = {
            "kubernetes": {
                "source": "hashicorp/kubernetes",
                "version": self._provider_version
            }
        }
    
    def set_provider_version(self, version: str) -> "TerraformOutput":
        """
        Set Kubernetes provider version.
        
        Args:
            version: Provider version constraint
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        self._provider_version = version
        self._required_providers["kubernetes"]["version"] = version
        return self
    
    def add_required_provider(self, name: str, source: str, version: str) -> "TerraformOutput":
        """
        Add required provider.
        
        Args:
            name: Provider name
            source: Provider source
            version: Provider version
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        self._required_providers[name] = {
            "source": source,
            "version": version
        }
        return self
    
    def add_variable(
        self,
        name: str,
        var_type: str,
        default: Optional[Any] = None,
        description: Optional[str] = None,
        validation: Optional[Dict[str, Any]] = None
    ) -> "TerraformOutput":
        """
        Add Terraform variable.
        
        Args:
            name: Variable name
            var_type: Variable type (string, number, bool, list, map, object)
            default: Default value
            description: Variable description
            validation: Validation rules
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        variable = {"type": var_type}
        
        if default is not None:
            variable["default"] = default
        
        if description:
            variable["description"] = description
        
        if validation:
            variable["validation"] = validation
        
        self._variables[name] = variable
        return self
    
    def add_output(
        self,
        name: str,
        value: str,
        description: Optional[str] = None,
        sensitive: bool = False
    ) -> "TerraformOutput":
        """
        Add Terraform output.
        
        Args:
            name: Output name
            value: Output value expression
            description: Output description
            sensitive: Whether output is sensitive
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        output = {"value": value}
        
        if description:
            output["description"] = description
        
        if sensitive:
            output["sensitive"] = sensitive
        
        self._outputs[name] = output
        return self
    
    def add_local(self, name: str, value: Any) -> "TerraformOutput":
        """
        Add local value.
        
        Args:
            name: Local name
            value: Local value
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        self._locals[name] = value
        return self
    
    def add_data_source(
        self,
        type: str,
        name: str,
        config: Dict[str, Any]
    ) -> "TerraformOutput":
        """
        Add data source.
        
        Args:
            type: Data source type
            name: Data source name
            config: Data source configuration
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        data_source = {
            "type": type,
            "name": name,
            "config": config
        }
        self._data_sources.append(data_source)
        return self
    
    def add_module(
        self,
        name: str,
        source: str,
        version: Optional[str] = None,
        inputs: Optional[Dict[str, Any]] = None
    ) -> "TerraformOutput":
        """
        Add Terraform module.
        
        Args:
            name: Module name
            source: Module source
            version: Module version
            inputs: Module inputs
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        module = {
            "name": name,
            "source": source
        }
        
        if version:
            module["version"] = version
        
        if inputs:
            module["inputs"] = inputs
        
        self._modules.append(module)
        return self
    
    def enable_remote_state(
        self,
        backend: str,
        config: Dict[str, Any]
    ) -> "TerraformOutput":
        """
        Enable remote state backend.
        
        Args:
            backend: Backend type (s3, gcs, azurerm, etc.)
            config: Backend configuration
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        self._remote_state = {
            "backend": backend,
            "config": config
        }
        return self
    
    def add_resource(self, resource: Any) -> "TerraformOutput":
        """
        Add a resource to the Terraform module.
        
        Args:
            resource: Resource to add
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        self._resources.append(resource)
        return self
    
    # Convenience methods
    
    def add_namespace_variable(self, default: str = "default") -> "TerraformOutput":
        """
        Add namespace variable.
        
        Args:
            default: Default namespace
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        return self.add_variable(
            "namespace",
            "string",
            default,
            "Kubernetes namespace"
        )
    
    def add_replicas_variable(self, default: int = 1) -> "TerraformOutput":
        """
        Add replicas variable.
        
        Args:
            default: Default replica count
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        return self.add_variable(
            "replicas",
            "number",
            default,
            "Number of replicas",
            {
                "condition": "var.replicas > 0",
                "error_message": "Replicas must be greater than 0."
            }
        )
    
    def add_image_variable(self, default: str = "nginx:latest") -> "TerraformOutput":
        """
        Add image variable.
        
        Args:
            default: Default image
            
        Returns:
            TerraformOutput: Self for method chaining
        """
        return self.add_variable(
            "image",
            "string",
            default,
            "Container image"
        )
    
    def generate_files(self, output_dir: str) -> None:
        """
        Generate Terraform module files.
        
        Args:
            output_dir: Output directory path
        """
        module_dir = Path(output_dir)
        module_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate main.tf
        self._generate_main_tf(module_dir)
        
        # Generate variables.tf
        if self._variables:
            self._generate_variables_tf(module_dir)
        
        # Generate outputs.tf
        if self._outputs:
            self._generate_outputs_tf(module_dir)
        
        # Generate versions.tf
        self._generate_versions_tf(module_dir)
        
        # Generate providers.tf
        self._generate_providers_tf(module_dir)
        
        # Generate locals.tf
        if self._locals:
            self._generate_locals_tf(module_dir)
        
        # Generate data.tf
        if self._data_sources:
            self._generate_data_tf(module_dir)
        
        # Generate modules.tf
        if self._modules:
            self._generate_modules_tf(module_dir)
        
        # Generate backend configuration
        if self._remote_state:
            self._generate_backend_tf(module_dir)
        
        # Generate terraform.tfvars.example
        self._generate_tfvars_example(module_dir)
        
        # Generate README.md
        self._generate_readme(module_dir)
        
        print(f"✅ Terraform module generated in: {module_dir}")
    
    def _generate_main_tf(self, module_dir: Path) -> None:
        """Generate main.tf file with resources."""
        content = []
        
        for resource in self._resources:
            k8s_resources = resource.generate_kubernetes_resources()
            for k8s_resource in k8s_resources:
                tf_resource = self._convert_k8s_to_terraform(k8s_resource)
                content.append(tf_resource)
        
        with open(module_dir / "main.tf", "w") as f:
            f.write("\n\n".join(content))
    
    def _generate_variables_tf(self, module_dir: Path) -> None:
        """Generate variables.tf file."""
        content = []
        
        for name, config in self._variables.items():
            var_block = f'variable "{name}" {{\n'
            
            if "description" in config:
                var_block += f'  description = "{config["description"]}"\n'
            
            var_block += f'  type = {config["type"]}\n'
            
            if "default" in config:
                default_value = json.dumps(config["default"]) if isinstance(config["default"], (dict, list)) else config["default"]
                if isinstance(config["default"], str):
                    var_block += f'  default = "{config["default"]}"\n'
                else:
                    var_block += f'  default = {config["default"]}\n'
            
            if "validation" in config:
                var_block += f'  validation {{\n'
                var_block += f'    condition = {config["validation"]["condition"]}\n'
                var_block += f'    error_message = "{config["validation"]["error_message"]}"\n'
                var_block += f'  }}\n'
            
            var_block += "}"
            content.append(var_block)
        
        with open(module_dir / "variables.tf", "w") as f:
            f.write("\n\n".join(content))
    
    def _generate_outputs_tf(self, module_dir: Path) -> None:
        """Generate outputs.tf file."""
        content = []
        
        for name, config in self._outputs.items():
            output_block = f'output "{name}" {{\n'
            output_block += f'  value = {config["value"]}\n'
            
            if "description" in config:
                output_block += f'  description = "{config["description"]}"\n'
            
            if config.get("sensitive"):
                output_block += f'  sensitive = true\n'
            
            output_block += "}"
            content.append(output_block)
        
        with open(module_dir / "outputs.tf", "w") as f:
            f.write("\n\n".join(content))
    
    def _generate_versions_tf(self, module_dir: Path) -> None:
        """Generate versions.tf file."""
        content = f'''terraform {{
  required_version = ">= 1.0"
  
  required_providers {{
'''
        
        for name, config in self._required_providers.items():
            content += f'''    {name} = {{
      source  = "{config["source"]}"
      version = "{config["version"]}"
    }}
'''
        
        content += "  }\n}"
        
        with open(module_dir / "versions.tf", "w") as f:
            f.write(content)
    
    def _generate_providers_tf(self, module_dir: Path) -> None:
        """Generate providers.tf file."""
        content = '''provider "kubernetes" {
  # Configuration options
}
'''
        
        # Add other providers if they exist
        for name, _ in self._required_providers.items():
            if name != "kubernetes":
                content += f'\nprovider "{name}" {{\n  # Configuration options\n}}\n'
        
        with open(module_dir / "providers.tf", "w") as f:
            f.write(content)
    
    def _generate_locals_tf(self, module_dir: Path) -> None:
        """Generate locals.tf file."""
        content = "locals {\n"
        
        for name, value in self._locals.items():
            if isinstance(value, str):
                content += f'  {name} = "{value}"\n'
            else:
                content += f'  {name} = {json.dumps(value)}\n'
        
        content += "}"
        
        with open(module_dir / "locals.tf", "w") as f:
            f.write(content)
    
    def _generate_data_tf(self, module_dir: Path) -> None:
        """Generate data.tf file."""
        content = []
        
        for data_source in self._data_sources:
            data_block = f'data "{data_source["type"]}" "{data_source["name"]}" {{\n'
            
            for key, value in data_source["config"].items():
                if isinstance(value, str):
                    data_block += f'  {key} = "{value}"\n'
                else:
                    data_block += f'  {key} = {json.dumps(value)}\n'
            
            data_block += "}"
            content.append(data_block)
        
        with open(module_dir / "data.tf", "w") as f:
            f.write("\n\n".join(content))
    
    def _generate_modules_tf(self, module_dir: Path) -> None:
        """Generate modules.tf file."""
        content = []
        
        for module in self._modules:
            module_block = f'module "{module["name"]}" {{\n'
            module_block += f'  source = "{module["source"]}"\n'
            
            if "version" in module:
                module_block += f'  version = "{module["version"]}"\n'
            
            if "inputs" in module:
                for key, value in module["inputs"].items():
                    if isinstance(value, str):
                        module_block += f'  {key} = "{value}"\n'
                    else:
                        module_block += f'  {key} = {json.dumps(value)}\n'
            
            module_block += "}"
            content.append(module_block)
        
        with open(module_dir / "modules.tf", "w") as f:
            f.write("\n\n".join(content))
    
    def _generate_backend_tf(self, module_dir: Path) -> None:
        """Generate backend.tf file."""
        content = f'''terraform {{
  backend "{self._remote_state["backend"]}" {{
'''
        
        for key, value in self._remote_state["config"].items():
            if isinstance(value, str):
                content += f'    {key} = "{value}"\n'
            else:
                content += f'    {key} = {value}\n'
        
        content += "  }\n}"
        
        with open(module_dir / "backend.tf", "w") as f:
            f.write(content)
    
    def _generate_tfvars_example(self, module_dir: Path) -> None:
        """Generate terraform.tfvars.example file."""
        content = []
        
        for name, config in self._variables.items():
            if "description" in config:
                content.append(f"# {config['description']}")
            
            if "default" in config:
                default_value = config["default"]
                if isinstance(default_value, str):
                    content.append(f'{name} = "{default_value}"')
                else:
                    content.append(f'{name} = {json.dumps(default_value)}')
            else:
                content.append(f'# {name} = "value"')
            
            content.append("")
        
        with open(module_dir / "terraform.tfvars.example", "w") as f:
            f.write("\n".join(content))
    
    def _generate_readme(self, module_dir: Path) -> None:
        """Generate README.md file."""
        content = f"""# {self._name.title()} Terraform Module

This Terraform module deploys {self._name} to Kubernetes.

## Usage

```hcl
module "{self._name}" {{
  source = "./{self._name}"
  
  # Variables
"""
        
        for name, config in self._variables.items():
            if "default" not in config:
                content += f"  {name} = var.{name}\n"
        
        content += "}\n```\n\n"
        
        # Variables documentation
        if self._variables:
            content += "## Variables\n\n"
            content += "| Name | Description | Type | Default | Required |\n"
            content += "|------|-------------|------|---------|:--------:|\n"
            
            for name, config in self._variables.items():
                description = config.get("description", "")
                var_type = config.get("type", "string")
                default = config.get("default", "")
                required = "no" if "default" in config else "yes"
                
                if isinstance(default, str):
                    default = f'"{default}"'
                elif default == "":
                    default = "n/a"
                else:
                    default = str(default)
                
                content += f"| {name} | {description} | {var_type} | {default} | {required} |\n"
        
        # Outputs documentation
        if self._outputs:
            content += "\n## Outputs\n\n"
            content += "| Name | Description |\n"
            content += "|------|-------------|\n"
            
            for name, config in self._outputs.items():
                description = config.get("description", "")
                content += f"| {name} | {description} |\n"
        
        with open(module_dir / "README.md", "w") as f:
            f.write(content)
    
    def _convert_k8s_to_terraform(self, k8s_resource: Dict[str, Any]) -> str:
        """
        Convert Kubernetes resource to Terraform HCL.
        
        Args:
            k8s_resource: Kubernetes resource dict
            
        Returns:
            str: Terraform HCL resource block
        """
        kind = k8s_resource.get("kind", "").lower()
        name = k8s_resource.get("metadata", {}).get("name", "resource")
        
        # Map Kubernetes kinds to Terraform resource types
        kind_mapping = {
            "deployment": "kubernetes_deployment",
            "service": "kubernetes_service",
            "configmap": "kubernetes_config_map",
            "secret": "kubernetes_secret",
            "namespace": "kubernetes_namespace",
            "serviceaccount": "kubernetes_service_account",
            "role": "kubernetes_role",
            "rolebinding": "kubernetes_role_binding",
            "clusterrole": "kubernetes_cluster_role",
            "clusterrolebinding": "kubernetes_cluster_role_binding",
            "ingress": "kubernetes_ingress_v1",
            "persistentvolumeclaim": "kubernetes_persistent_volume_claim",
            "job": "kubernetes_job",
            "cronjob": "kubernetes_cron_job_v1",
            "horizontalpodautoscaler": "kubernetes_horizontal_pod_autoscaler_v2"
        }
        
        tf_type = kind_mapping.get(kind, f"kubernetes_{kind}")
        tf_name = name.replace("-", "_")
        
        content = f'resource "{tf_type}" "{tf_name}" {{\n'
        content += self._convert_dict_to_hcl(k8s_resource, 1)
        content += "}"
        
        return content
    
    def _convert_dict_to_hcl(self, data: Any, indent: int = 0) -> str:
        """
        Convert dictionary to HCL format.
        
        Args:
            data: Data to convert
            indent: Indentation level
            
        Returns:
            str: HCL formatted string
        """
        if isinstance(data, dict):
            result = ""
            for key, value in data.items():
                spaces = "  " * indent
                
                if isinstance(value, (dict, list)):
                    result += f"{spaces}{key} {{\n"
                    result += self._convert_dict_to_hcl(value, indent + 1)
                    result += f"{spaces}}}\n"
                elif isinstance(value, str):
                    result += f'{spaces}{key} = "{value}"\n'
                elif isinstance(value, bool):
                    result += f'{spaces}{key} = {str(value).lower()}\n'
                else:
                    result += f"{spaces}{key} = {value}\n"
            
            return result
        
        elif isinstance(data, list):
            result = ""
            for item in data:
                spaces = "  " * indent
                if isinstance(item, (dict, list)):
                    result += f"{spaces}{{\n"
                    result += self._convert_dict_to_hcl(item, indent + 1)
                    result += f"{spaces}}}\n"
                elif isinstance(item, str):
                    result += f'{spaces}"{item}"\n'
                else:
                    result += f"{spaces}{item}\n"
            
            return result
        
        else:
            return str(data) 