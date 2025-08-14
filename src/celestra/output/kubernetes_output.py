"""
Kubernetes YAML output format for Celestra DSL.

This module contains the KubernetesOutput class for generating Kubernetes YAML
manifests from DSL builders.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import subprocess
import os

from .base_output import FileOutputFormat
from ..utils.decorators import show_format_warnings


class KubernetesOutput(FileOutputFormat):
    """
    Output format for generating Kubernetes YAML manifests.
    
    This class generates Kubernetes YAML files from DSL builders,
    with options for file organization and manifest structure.
    
    Example:
        ```python
        output = KubernetesOutput()
        output.set_option("separate_files", True)
        output.set_option("sort_resources", True)
        output.generate(app, "./k8s/")
        ```
    """
    
    def __init__(self):
        """Initialize the Kubernetes output format."""
        super().__init__()
        # Set default options
        self.set_options({
            "separate_files": True,  # Generate separate files for each resource
            "single_file": False,    # Generate single file with all resources
            "sort_resources": True,  # Sort resources by deployment order
            "include_namespace": True,  # Include namespace in manifests
            "add_labels": True,      # Add standard labels
            "add_annotations": True, # Add standard annotations
            "validate_resources": True,  # Validate resources before generation
            "filename_template": "{kind}-{name}.yaml",  # Template for filenames
            "single_filename": "manifests.yaml"  # Filename for single file output
        })
        # Store the last generated output directory
        self._last_output_dir: Optional[Path] = None
    
    def generate(
        self, 
        resources_or_builder: Union[List[Dict[str, Any]], Any],
        output_path: Union[str, Path] = "./k8s/"
    ) -> None:
        """
        Generate Kubernetes YAML manifests.
        
        Args:
            resources_or_builder: Either a list of Kubernetes resources or a builder
            output_path: Directory path to write YAML files
        """
        # Handle both resource lists and builders
        if isinstance(resources_or_builder, list):
            resources = resources_or_builder
        else:
            # Validate builder if validation is enabled
            if self.get_option("validate_resources", True):
                errors = self.validate_builder(resources_or_builder)
                if errors:
                    raise ValueError(f"Builder validation failed: {'; '.join(errors)}")
            
            resources = self._get_resources_from_builder(resources_or_builder)
        
        # Process resources
        processed_resources = self._process_resources(resources)
        
        # Create output directory
        output_dir = self._ensure_output_directory(output_path)
        
        # Generate files
        if self.get_option("single_file", False):
            self._generate_single_file(processed_resources, output_dir)
        else:
            self._generate_separate_files(processed_resources, output_dir)
        
        # Store the output directory for execution methods
        self._update_last_output_dir(output_dir)
    
    def _process_resources(self, resources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process resources before generating output.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[Dict[str, Any]]: Processed resources
        """
        processed = []
        
        for resource in resources:
            # Create a copy to avoid modifying the original
            processed_resource = self._deep_copy_resource(resource)
            
            # Add standard labels if enabled
            if self.get_option("add_labels", True):
                self._add_standard_labels(processed_resource)
            
            # Add standard annotations if enabled
            if self.get_option("add_annotations", True):
                self._add_standard_annotations(processed_resource)
            
            # Ensure namespace is included if enabled
            if self.get_option("include_namespace", True):
                self._ensure_namespace(processed_resource)
            
            processed.append(processed_resource)
        
        # Sort resources if enabled
        if self.get_option("sort_resources", True):
            processed = self._sort_resources(processed)
        
        return processed
    
    def _generate_single_file(self, resources: List[Dict[str, Any]], output_dir: Path) -> None:
        """
        Generate a single YAML file with all resources.
        
        Args:
            resources: List of Kubernetes resources
            output_dir: Output directory
        """
        filename = self.get_option("single_filename", "manifests.yaml")
        file_path = output_dir / filename
        
        self._write_resources_file(resources, file_path)
        print(f"Generated Kubernetes manifests: {file_path}")
    
    def _generate_separate_files(self, resources: List[Dict[str, Any]], output_dir: Path) -> None:
        """
        Generate separate YAML files for each resource.
        
        Args:
            resources: List of Kubernetes resources
            output_dir: Output directory
        """
        filename_template = self.get_option("filename_template", "{kind}-{name}.yaml")
        generated_files = []
        
        for resource in resources:
            file_path = self._write_resource_file(resource, output_dir, filename_template)
            generated_files.append(file_path)
        
        print(f"Generated {len(generated_files)} Kubernetes manifest files in {output_dir}")
    
    def _deep_copy_resource(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a deep copy of a resource.
        
        Args:
            resource: Resource to copy
            
        Returns:
            Dict[str, Any]: Deep copy of the resource
        """
        import copy
        return copy.deepcopy(resource)
    
    def _add_standard_labels(self, resource: Dict[str, Any]) -> None:
        """
        Add standard labels to a resource.
        
        Args:
            resource: Resource to add labels to
        """
        if "metadata" not in resource:
            resource["metadata"] = {}
        
        if "labels" not in resource["metadata"]:
            resource["metadata"]["labels"] = {}
        
        labels = resource["metadata"]["labels"]
        
        # Add standard labels if not present
        if "app.kubernetes.io/managed-by" not in labels:
            labels["app.kubernetes.io/managed-by"] = "k8s-gen"
        
        if "app.kubernetes.io/version" not in labels:
            labels["app.kubernetes.io/version"] = "1.0.0"
        
        # Add component label based on resource kind
        if "app.kubernetes.io/component" not in labels:
            kind = resource.get("kind", "").lower()
            if kind in ["deployment", "statefulset", "daemonset"]:
                labels["app.kubernetes.io/component"] = "application"
            elif kind == "service":
                labels["app.kubernetes.io/component"] = "network"
            elif kind in ["configmap", "secret"]:
                labels["app.kubernetes.io/component"] = "configuration"
            elif kind in ["job", "cronjob"]:
                labels["app.kubernetes.io/component"] = "batch"
    
    def _add_standard_annotations(self, resource: Dict[str, Any]) -> None:
        """
        Add standard annotations to a resource.
        
        Args:
            resource: Resource to add annotations to
        """
        if "metadata" not in resource:
            resource["metadata"] = {}
        
        if "annotations" not in resource["metadata"]:
            resource["metadata"]["annotations"] = {}
        
        annotations = resource["metadata"]["annotations"]
        
        # Add standard annotations if not present
        if "k8s-gen.io/generated" not in annotations:
            annotations["k8s-gen.io/generated"] = "true"
        
        if "k8s-gen.io/version" not in annotations:
            annotations["k8s-gen.io/version"] = "1.0.0"
        
        # Add generation timestamp
        if "k8s-gen.io/generated-at" not in annotations:
            from datetime import datetime
            annotations["celestra.io/generated-at"] = datetime.utcnow().isoformat() + "Z"
    
    def _ensure_namespace(self, resource: Dict[str, Any]) -> None:
        """
        Ensure namespace is set for namespaced resources.
        
        Args:
            resource: Resource to check namespace for
        """
        # Skip cluster-scoped resources
        cluster_scoped_kinds = [
            "Namespace", "ClusterRole", "ClusterRoleBinding", 
            "CustomResourceDefinition", "PersistentVolume"
        ]
        
        kind = resource.get("kind", "")
        if kind in cluster_scoped_kinds:
            return
        
        if "metadata" not in resource:
            resource["metadata"] = {}
        
        # Set default namespace if not present
        if "namespace" not in resource["metadata"]:
            resource["metadata"]["namespace"] = "default"
    
    def generate_kustomization(
        self, 
        resources: List[Dict[str, Any]],
        output_dir: Path,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Generate a kustomization.yaml file for the resources.
        
        Args:
            resources: List of Kubernetes resources
            output_dir: Output directory
            config: Kustomization configuration
        """
        # Group resources by kind to create resource list
        grouped_resources = self._group_resources_by_kind(resources)
        
        resource_files = []
        for kind, kind_resources in grouped_resources.items():
            for resource in kind_resources:
                name = resource.get("metadata", {}).get("name", "unnamed")
                filename = f"{kind.lower()}-{name}.yaml"
                resource_files.append(filename)
        
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": sorted(resource_files)
        }
        
        # Add common labels if configured
        if config and config.get("common_labels"):
            kustomization["commonLabels"] = config["common_labels"]
        
        # Add namespace if configured
        if config and config.get("namespace"):
            kustomization["namespace"] = config["namespace"]
        
        # Add name prefix if configured
        if config and config.get("name_prefix"):
            kustomization["namePrefix"] = config["name_prefix"]
        
        # Add name suffix if configured
        if config and config.get("name_suffix"):
            kustomization["nameSuffix"] = config["name_suffix"]
        
        from ..utils.helpers import format_yaml
        kustomization_content = format_yaml(kustomization)
        kustomization_path = output_dir / "kustomization.yaml"
        
        self._write_file(kustomization_path, kustomization_content)
        print(f"Generated kustomization.yaml: {kustomization_path}")
    
    def validate_generated_resources(self, resources: List[Dict[str, Any]]) -> List[str]:
        """
        Validate generated Kubernetes resources.
        
        Args:
            resources: List of Kubernetes resources to validate
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        
        for i, resource in enumerate(resources):
            resource_errors = self._validate_single_resource(resource, i)
            errors.extend(resource_errors)
        
        return errors
    
    def _validate_single_resource(self, resource: Dict[str, Any], index: int) -> List[str]:
        """
        Validate a single Kubernetes resource.
        
        Args:
            resource: Resource to validate
            index: Resource index for error reporting
            
        Returns:
            List[str]: List of validation errors
        """
        errors = []
        resource_id = f"Resource {index}"
        
        # Check required fields
        if "apiVersion" not in resource:
            errors.append(f"{resource_id}: Missing required field 'apiVersion'")
        
        if "kind" not in resource:
            errors.append(f"{resource_id}: Missing required field 'kind'")
        
        if "metadata" not in resource:
            errors.append(f"{resource_id}: Missing required field 'metadata'")
        else:
            metadata = resource["metadata"]
            if "name" not in metadata:
                errors.append(f"{resource_id}: Missing required field 'metadata.name'")
        
        # Validate resource names
        if "metadata" in resource and "name" in resource["metadata"]:
            name = resource["metadata"]["name"]
            if not self._is_valid_kubernetes_name(name):
                errors.append(f"{resource_id}: Invalid Kubernetes name '{name}'")
        
        return errors
    
    def _is_valid_kubernetes_name(self, name: str) -> bool:
        """
        Check if a name is valid for Kubernetes.
        
        Args:
            name: Name to validate
            
        Returns:
            bool: True if name is valid
        """
        import re
        # Kubernetes names must be lowercase alphanumeric with hyphens
        pattern = r'^[a-z0-9]([-a-z0-9]*[a-z0-9])?$'
        return bool(re.match(pattern, name)) and len(name) <= 253

    # ===== EXECUTION METHODS =====
    
    def run(self, command: str, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Run kubectl command with the specified options.
        
        Args:
            command: kubectl command (apply, delete, get, logs, etc.)
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional kubectl options
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        output_dir = self._get_output_dir_path(resources_dir)
        kubectl_command = self._build_kubectl_command(command, output_dir, **options)
        
        try:
            result = subprocess.run(kubectl_command, check=True, capture_output=True, text=True)
            print(f"kubectl command executed successfully: {' '.join(kubectl_command)}")
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing kubectl command: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            raise
        
        return self
    
    def apply(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Apply Kubernetes resources.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, wait, timeout, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("apply", resources_dir, **options)
    
    def delete(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Delete Kubernetes resources.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, grace_period, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("delete", resources_dir, **options)
    
    def replace(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Replace Kubernetes resources.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, wait, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("replace", resources_dir, **options)
    
    def patch(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Patch Kubernetes resources.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, type, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("patch", resources_dir, **options)
    
    def get(self, resource_type: Optional[str] = None, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Get Kubernetes resources.
        
        Args:
            resource_type: Type of resource to get (optional)
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, output, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        if resource_type:
            return self.run("get", resources_dir, resource_type=resource_type, **options)
        return self.run("get", resources_dir, **options)
    
    def describe(self, resource_type: Optional[str] = None, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Describe Kubernetes resources.
        
        Args:
            resource_type: Type of resource to describe (optional)
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, output, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        if resource_type:
            return self.run("describe", resources_dir, resource_type=resource_type, **options)
        return self.run("describe", resources_dir, **options)
    
    def edit(self, resource_type: Optional[str] = None, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Edit Kubernetes resources.
        
        Args:
            resource_type: Type of resource to edit (optional)
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        if resource_type:
            return self.run("edit", resources_dir, resource_type=resource_type, **options)
        return self.run("edit", resources_dir, **options)
    
    def logs(self, pod: Optional[str] = None, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Show Kubernetes logs.
        
        Args:
            pod: Pod name to show logs for (optional)
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, follow, tail, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        if pod:
            return self.run("logs", resources_dir, pod=pod, **options)
        return self.run("logs", resources_dir, **options)
    
    def port_forward(self, service: str, local_port: int, target_port: int, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Port forward Kubernetes services.
        
        Args:
            service: Service name to port forward
            local_port: Local port to bind to
            target_port: Target port in the service
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("port-forward", resources_dir, service=service, local_port=local_port, target_port=target_port, **options)
    
    def exec(self, pod: str, command: str, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Execute command in Kubernetes pod.
        
        Args:
            pod: Pod name to execute command in
            command: Command to execute
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, container, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("exec", resources_dir, pod=pod, exec_command=command, **options)
    
    def scale(self, deployment: str, replicas: int, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Scale Kubernetes deployments.
        
        Args:
            deployment: Deployment name to scale
            replicas: Number of replicas
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("scale", resources_dir, deployment=deployment, replicas=replicas, **options)
    
    def rollout(self, action: str, deployment: str, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Manage Kubernetes rollouts.
        
        Args:
            action: Rollout action (status, history, undo, restart, pause, resume)
            deployment: Deployment name
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("rollout", resources_dir, action=action, deployment=deployment, **options)
    
    def status(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Show Kubernetes status.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("get", resources_dir, output="wide", **options)
    
    def health(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Check Kubernetes resource health.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("get", resources_dir, output="wide", **options)
    
    def events(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Show Kubernetes events.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("get", resources_dir, resource_type="events", **options)
    
    def validate(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Validate Kubernetes resources.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("apply", resources_dir, dry_run="client", **options)
    
    def diff(self, resources_dir: Optional[str] = None, **options) -> "KubernetesOutput":
        """
        Show differences between local and cluster resources.
        
        Args:
            resources_dir: Directory containing Kubernetes resources (defaults to last generated)
            **options: Additional options like namespace, etc.
            
        Returns:
            KubernetesOutput: Self for method chaining
        """
        return self.run("diff", resources_dir, **options)
    
    # ===== PRIVATE HELPER METHODS =====
    
    def _get_output_dir_path(self, resources_dir: Optional[str] = None) -> Path:
        """
        Get the output directory path, using the last generated one if none specified.
        
        Args:
            resources_dir: Optional resources directory path
            
        Returns:
            Path: Path to the resources directory
            
        Raises:
            ValueError: If no resources directory path is available
        """
        if resources_dir:
            return Path(resources_dir)
        elif self._last_output_dir:
            return self._last_output_dir
        else:
            raise ValueError("No resources directory specified and no directory was previously generated. Call generate() first or specify a resources_dir path.")
    
    def _build_kubectl_command(self, command: str, output_dir: Path, **options) -> List[str]:
        """
        Build the kubectl command with options.
        
        Args:
            command: kubectl command
            output_dir: Directory containing the resources
            **options: Command options
            
        Returns:
            List[str]: List of command arguments
        """
        kubectl_command = ["kubectl"]
        
        # Add namespace if specified
        if "namespace" in options:
            kubectl_command.extend(["-n", options.pop("namespace")])
        
        # Add the main command
        kubectl_command.append(command)
        
        # Add resource type if specified
        if "resource_type" in options:
            kubectl_command.append(options.pop("resource_type"))
        
        # Add pod name if specified
        if "pod" in options:
            kubectl_command.append(options.pop("pod"))
        
        # Add deployment name if specified
        if "deployment" in options:
            kubectl_command.append(options.pop("deployment"))
        
        # Add service name if specified
        if "service" in options:
            kubectl_command.append(options.pop("service"))
        
        # Add exec command if specified
        if "exec_command" in options:
            kubectl_command.extend(["--", options.pop("exec_command")])
        
        # Add port-forward arguments if specified
        if "local_port" in options and "target_port" in options:
            local_port = options.pop("local_port")
            target_port = options.pop("target_port")
            kubectl_command.extend([f"{local_port}:{target_port}"])
        
        # Add replicas if specified
        if "replicas" in options:
            kubectl_command.append(str(options.pop("replicas")))
        
        # Add rollout action if specified
        if "action" in options:
            kubectl_command.append(options.pop("action"))
        
        # Add output format if specified
        if "output" in options:
            kubectl_command.extend(["-o", options.pop("output")])
        
        # Add dry-run if specified
        if "dry_run" in options:
            kubectl_command.extend(["--dry-run", options.pop("dry_run")])
        
        # Add wait if specified
        if "wait" in options and options.pop("wait"):
            kubectl_command.append("--wait")
        
        # Add timeout if specified
        if "timeout" in options:
            kubectl_command.extend(["--timeout", str(options.pop("timeout"))])
        
        # Add follow if specified
        if "follow" in options and options.pop("follow"):
            kubectl_command.append("-f")
        
        # Add tail if specified
        if "tail" in options:
            kubectl_command.extend(["--tail", str(options.pop("tail"))])
        
        # Add force if specified
        if "force" in options and options.pop("force"):
            kubectl_command.append("--force")
        
        # Add grace-period if specified
        if "grace_period" in options:
            kubectl_command.extend(["--grace-period", str(options.pop("grace_period"))])
        
        # Add cascade if specified
        if "cascade" in options and not options.pop("cascade"):
            kubectl_command.append("--cascade=false")
        
        # Add the resources directory or specific files
        if command in ["apply", "delete", "replace", "patch", "diff"]:
            kubectl_command.append("-f")
            kubectl_command.append(str(output_dir))
        
        return kubectl_command
    
    def _update_last_output_dir(self, output_dir: Union[str, Path]) -> None:
        """
        Update the last generated output directory path.
        
        Args:
            output_dir: Path to the output directory
        """
        self._last_output_dir = Path(output_dir) 