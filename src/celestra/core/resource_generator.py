"""
Resource generator for Celestraa DSL.

This module contains the ResourceGenerator class that handles the generation
of multiple output formats from DSL builders.
"""

from typing import Dict, List, Any, Optional, Union, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from .base_builder import BaseBuilder

from ..utils.helpers import ensure_directory
from ..utils.decorators import show_format_warnings


class ResourceGenerator:
    """
    Generator class for converting DSL builders to various output formats.
    
    This class implements the generator pattern allowing fluent chaining
    of output format methods.
    """
    
    def __init__(self, builder: "BaseBuilder"):
        """
        Initialize the resource generator.
        
        Args:
            builder: The DSL builder to generate resources from
        """
        self._builder = builder
        self._resources: Optional[List[Dict[str, Any]]] = None
    
    @property
    def resources(self) -> List[Dict[str, Any]]:
        """
        Get the generated Kubernetes resources.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resource dictionaries
        """
        if self._resources is None:
            self._resources = self._builder.generate_kubernetes_resources()
        return self._resources
    
    def to_yaml(self, output_path: Union[str, Path] = "./k8s/") -> "ResourceGenerator":
        """
        Generate Kubernetes YAML files.
        
        Args:
            output_path: Directory path to write YAML files
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        from ..output.kubernetes_output import KubernetesOutput
        
        # Show warnings for incompatible methods
        show_format_warnings(self._builder, "kubernetes")
        
        output = KubernetesOutput()
        output.generate(self.resources, output_path)
        return self
    
    def to_docker_compose(
        self, 
        output_file: Union[str, Path] = "./docker-compose.yml",
        base_file: Optional[str] = None,
        override_files: Optional[Dict[str, str]] = None
    ) -> "ResourceGenerator":
        """
        Generate Docker Compose file.
        
        Args:
            output_file: Path to write Docker Compose file
            base_file: Base compose file path
            override_files: Environment-specific override files
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        from ..output.docker_compose_output import DockerComposeOutput
        
        # Show warnings for incompatible methods
        show_format_warnings(self._builder, "docker-compose")
        
        output = DockerComposeOutput()
        output.generate(
            self._builder, 
            output_file,
            base_file=base_file,
            override_files=override_files
        )
        return self
    
    def to_helm_chart(self, output_path: Union[str, Path] = "./charts/") -> "ResourceGenerator":
        """
        Generate Helm chart.
        
        Args:
            output_path: Directory path to write Helm chart
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        from ..output.helm_output import HelmOutput
        
        output = HelmOutput()
        output.generate(self._builder, output_path)
        return self
    
    def to_kustomize(
        self, 
        base_path: Union[str, Path] = "./k8s/base/",
        overlays: Optional[List[str]] = None
    ) -> "ResourceGenerator":
        """
        Generate Kustomize structure.
        
        Args:
            base_path: Path to write base Kustomize files
            overlays: List of overlay environments to generate
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        from ..output.kustomize_output import KustomizeOutput
        
        output = KustomizeOutput()
        output.generate(self._builder, base_path, overlays=overlays)
        return self
    
    def to_terraform(self, output_path: Union[str, Path] = "./terraform/") -> "ResourceGenerator":
        """
        Generate Terraform modules.
        
        Args:
            output_path: Directory path to write Terraform files
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        from ..output.terraform_output import TerraformOutput
        
        output = TerraformOutput()
        output.generate(self._builder, output_path)
        return self
    
    def to_all_formats(
        self, 
        output_path: Union[str, Path] = "./output/",
        formats: Optional[List[str]] = None
    ) -> "ResourceGenerator":
        """
        Generate all supported output formats.
        
        Args:
            output_path: Base directory path for all outputs
            formats: List of formats to generate (default: all)
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        if formats is None:
            formats = ["yaml", "docker-compose", "helm", "kustomize", "terraform"]
        
        output_path = Path(output_path)
        ensure_directory(output_path)
        
        if "yaml" in formats:
            self.to_yaml(output_path / "k8s")
        
        if "docker-compose" in formats:
            self.to_docker_compose(output_path / "docker-compose.yml")
        
        if "helm" in formats:
            self.to_helm_chart(output_path / "charts")
        
        if "kustomize" in formats:
            self.to_kustomize(output_path / "kustomize" / "base")
        
        if "terraform" in formats:
            self.to_terraform(output_path / "terraform")
        
        return self
    
    def to_custom_format(
        self, 
        output_format: "OutputFormat",
        *args, 
        **kwargs
    ) -> "ResourceGenerator":
        """
        Generate using a custom output format.
        
        Args:
            output_format: Custom output format instance
            *args: Positional arguments for the output format
            **kwargs: Keyword arguments for the output format
            
        Returns:
            ResourceGenerator: Self for method chaining
        """
        output_format.generate(self._builder, *args, **kwargs)
        return self
    
    def validate(self) -> List[str]:
        """
        Validate the generated resources.
        
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        # Validate the builder
        builder_errors = self._builder.validate()
        errors.extend(builder_errors)
        
        # Validate generated resources
        try:
            resources = self.resources
            for resource in resources:
                if not isinstance(resource, dict):
                    errors.append("Resource must be a dictionary")
                    continue
                
                if "apiVersion" not in resource:
                    errors.append("Resource missing apiVersion")
                
                if "kind" not in resource:
                    errors.append("Resource missing kind")
                
                if "metadata" not in resource:
                    errors.append("Resource missing metadata")
                elif "name" not in resource["metadata"]:
                    errors.append("Resource metadata missing name")
        
        except Exception as e:
            errors.append(f"Error generating resources: {str(e)}")
        
        return errors
    
    def security_scan(self) -> Dict[str, Any]:
        """
        Perform security scanning on generated resources.
        
        Returns:
            Dict[str, Any]: Security scan results
        """
        from ..validation.security_scanner import SecurityScanner
        
        scanner = SecurityScanner()
        return scanner.scan(self.resources)
    
    def cost_estimate(self) -> Dict[str, Any]:
        """
        Estimate costs for the generated resources.
        
        Returns:
            Dict[str, Any]: Cost estimation results
        """
        from ..validation.cost_estimator import CostEstimator
        
        estimator = CostEstimator()
        return estimator.estimate(self.resources)
    
    def get_resources_by_kind(self, kind: str) -> List[Dict[str, Any]]:
        """
        Get resources filtered by Kubernetes kind.
        
        Args:
            kind: Kubernetes resource kind
            
        Returns:
            List[Dict[str, Any]]: Filtered resources
        """
        return [r for r in self.resources if r.get("kind") == kind]
    
    def get_resources_by_api_version(self, api_version: str) -> List[Dict[str, Any]]:
        """
        Get resources filtered by API version.
        
        Args:
            api_version: Kubernetes API version
            
        Returns:
            List[Dict[str, Any]]: Filtered resources
        """
        return [r for r in self.resources if r.get("apiVersion") == api_version]
    
    def preview(self) -> str:
        """
        Get a preview of the generated resources as YAML.
        
        Returns:
            str: YAML representation of resources
        """
        from ..utils.helpers import format_yaml
        
        all_resources = {"---\n".join([format_yaml(r) for r in self.resources])}
        return "---\n" + all_resources.pop()
    
    def __repr__(self) -> str:
        """String representation of the generator."""
        return f"ResourceGenerator(builder={self._builder}, resources={len(self.resources)})" 