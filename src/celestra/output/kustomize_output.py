"""
KustomizeOutput class for generating Kustomize overlays in Celestra DSL.

This module provides Kustomize overlay generation with proper structure,
patches, and resource management following Kustomize best practices.
"""

import os
import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from .base_output import OutputFormat


class KustomizeOutput(OutputFormat):
    
    def generate(self, output_dir: str) -> None:
        """Generate method required by OutputFormat base class."""
        return self.generate_files(output_dir)
    """
    Output format for generating Kustomize overlays.
    
    Generates proper Kustomize structure with base resources, overlays,
    patches, and environment-specific configurations.
    
    Example:
        ```python
        kustomize_output = (KustomizeOutput("my-app")
            .set_namespace("production")
            .add_image_tag("myapp", "v2.1.0")
            .add_replica_patch("deployment", 5)
            .add_config_patch("config", {"LOG_LEVEL": "info"})
            .add_secret_generator("app-secrets", {"API_KEY": "secret-value"})
            .add_prefix("prod-")
            .add_suffix("-v2"))
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the Kustomize output formatter.
        
        Args:
            name: Name of the Kustomize application
        """
        super().__init__()
        self._name = name
        self._namespace: Optional[str] = None
        self._name_prefix: str = ""
        self._name_suffix: str = ""
        self._common_labels: Dict[str, str] = {}
        self._common_annotations: Dict[str, str] = {}
        self._images: List[Dict[str, str]] = []
        self._patches: List[Dict[str, Any]] = []
        self._strategic_merge_patches: List[str] = []
        self._json6902_patches: List[Dict[str, Any]] = []
        self._config_map_generator: List[Dict[str, Any]] = []
        self._secret_generator: List[Dict[str, Any]] = []
        self._var_reference: List[Dict[str, Any]] = []
        self._crds: List[str] = []
        self._generators: List[str] = []
        self._transformers: List[str] = []
        self._helmcharts: List[Dict[str, Any]] = []
        self._remote_resources: List[str] = []
        self._overlays: Dict[str, "KustomizeOutput"] = {}
        self._resources: List[Any] = []
    
    def set_namespace(self, namespace: str) -> "KustomizeOutput":
        """
        Set the target namespace.
        
        Args:
            namespace: Kubernetes namespace
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._namespace = namespace
        return self
    
    def add_prefix(self, prefix: str) -> "KustomizeOutput":
        """
        Add name prefix to all resources.
        
        Args:
            prefix: Name prefix
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._name_prefix = prefix
        return self
    
    def add_suffix(self, suffix: str) -> "KustomizeOutput":
        """
        Add name suffix to all resources.
        
        Args:
            suffix: Name suffix
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._name_suffix = suffix
        return self
    
    def add_common_label(self, key: str, value: str) -> "KustomizeOutput":
        """
        Add a common label to all resources.
        
        Args:
            key: Label key
            value: Label value
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._common_labels[key] = value
        return self
    
    def add_common_annotation(self, key: str, value: str) -> "KustomizeOutput":
        """
        Add a common annotation to all resources.
        
        Args:
            key: Annotation key
            value: Annotation value
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._common_annotations[key] = value
        return self
    
    def add_image_tag(self, name: str, new_tag: str, new_name: Optional[str] = None) -> "KustomizeOutput":
        """
        Add image tag transformation.
        
        Args:
            name: Image name
            new_tag: New image tag
            new_name: New image name (optional)
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        image = {"name": name, "newTag": new_tag}
        if new_name:
            image["newName"] = new_name
        
        self._images.append(image)
        return self
    
    def add_strategic_merge_patch(self, patch_file: str, patch_content: Dict[str, Any]) -> "KustomizeOutput":
        """
        Add strategic merge patch.
        
        Args:
            patch_file: Patch file name
            patch_content: Patch content
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._strategic_merge_patches.append(patch_file)
        self._patches.append({"file": patch_file, "content": patch_content})
        return self
    
    def add_json6902_patch(
        self,
        target: Dict[str, str],
        patch: List[Dict[str, Any]],
        path: Optional[str] = None
    ) -> "KustomizeOutput":
        """
        Add JSON 6902 patch.
        
        Args:
            target: Target resource (group, version, kind, name, namespace)
            patch: JSON patch operations
            path: Patch file path (optional)
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        patch_config = {"target": target}
        
        if path:
            patch_config["path"] = path
        else:
            patch_config["patch"] = yaml.dump(patch)
        
        self._json6902_patches.append(patch_config)
        return self
    
    def add_replica_patch(self, resource_name: str, replicas: int) -> "KustomizeOutput":
        """
        Add replica count patch.
        
        Args:
            resource_name: Resource name
            replicas: Number of replicas
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        patch = [
            {
                "op": "replace",
                "path": "/spec/replicas",
                "value": replicas
            }
        ]
        
        target = {
            "group": "apps",
            "version": "v1",
            "kind": "Deployment",
            "name": resource_name
        }
        
        return self.add_json6902_patch(target, patch)
    
    def add_config_patch(self, config_name: str, data: Dict[str, str]) -> "KustomizeOutput":
        """
        Add ConfigMap data patch.
        
        Args:
            config_name: ConfigMap name
            data: New data
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        patch_content = {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": config_name
            },
            "data": data
        }
        
        return self.add_strategic_merge_patch(f"patch-{config_name}.yaml", patch_content)
    
    def add_config_map_generator(
        self,
        name: str,
        files: Optional[List[str]] = None,
        literals: Optional[Dict[str, str]] = None,
        env_files: Optional[List[str]] = None
    ) -> "KustomizeOutput":
        """
        Add ConfigMap generator.
        
        Args:
            name: ConfigMap name
            files: List of files to include
            literals: Literal key-value pairs
            env_files: List of env files
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        generator = {"name": name}
        
        if files:
            generator["files"] = files
        
        if literals:
            generator["literals"] = [f"{k}={v}" for k, v in literals.items()]
        
        if env_files:
            generator["envs"] = env_files
        
        self._config_map_generator.append(generator)
        return self
    
    def add_secret_generator(
        self,
        name: str,
        files: Optional[List[str]] = None,
        literals: Optional[Dict[str, str]] = None,
        env_files: Optional[List[str]] = None,
        secret_type: str = "Opaque"
    ) -> "KustomizeOutput":
        """
        Add Secret generator.
        
        Args:
            name: Secret name
            files: List of files to include
            literals: Literal key-value pairs
            env_files: List of env files
            secret_type: Secret type
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        generator = {"name": name, "type": secret_type}
        
        if files:
            generator["files"] = files
        
        if literals:
            generator["literals"] = [f"{k}={v}" for k, v in literals.items()]
        
        if env_files:
            generator["envs"] = env_files
        
        self._secret_generator.append(generator)
        return self
    
    def add_remote_resource(self, url: str) -> "KustomizeOutput":
        """
        Add remote resource.
        
        Args:
            url: Resource URL
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._remote_resources.append(url)
        return self
    
    def add_helm_chart(
        self,
        name: str,
        repo: str,
        version: str,
        release_name: Optional[str] = None,
        values: Optional[Dict[str, Any]] = None
    ) -> "KustomizeOutput":
        """
        Add Helm chart reference.
        
        Args:
            name: Chart name
            repo: Chart repository
            version: Chart version
            release_name: Helm release name
            values: Chart values
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        chart = {
            "name": name,
            "repo": repo,
            "version": version
        }
        
        if release_name:
            chart["releaseName"] = release_name
        
        if values:
            chart["valuesInline"] = values
        
        self._helmcharts.append(chart)
        return self
    
    def add_overlay(self, name: str, overlay: "KustomizeOutput") -> "KustomizeOutput":
        """
        Add environment overlay.
        
        Args:
            name: Overlay name
            overlay: Overlay configuration
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._overlays[name] = overlay
        return self
    
    def add_resource(self, resource: Any) -> "KustomizeOutput":
        """
        Add a resource to the Kustomize configuration.
        
        Args:
            resource: Resource to add
            
        Returns:
            KustomizeOutput: Self for method chaining
        """
        self._resources.append(resource)
        return self
    
    # Preset configurations
    
    @classmethod
    def development_overlay(cls, base_name: str) -> "KustomizeOutput":
        """
        Create development overlay.
        
        Args:
            base_name: Base application name
            
        Returns:
            KustomizeOutput: Development overlay
        """
        return (cls(f"{base_name}-dev")
            .set_namespace("development")
            .add_common_label("environment", "development")
            .add_prefix("dev-")
            .add_replica_patch("app", 1))
    
    @classmethod
    def production_overlay(cls, base_name: str) -> "KustomizeOutput":
        """
        Create production overlay.
        
        Args:
            base_name: Base application name
            
        Returns:
            KustomizeOutput: Production overlay
        """
        return (cls(f"{base_name}-prod")
            .set_namespace("production")
            .add_common_label("environment", "production")
            .add_prefix("prod-")
            .add_replica_patch("app", 5))
    
    def generate_files(self, output_dir: str) -> None:
        """
        Generate Kustomize files.
        
        Args:
            output_dir: Output directory path
        """
        base_dir = Path(output_dir) / "base"
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate base resources
        self._generate_base_resources(base_dir)
        
        # Generate base kustomization
        self._generate_base_kustomization(base_dir)
        
        # Generate overlays
        for overlay_name, overlay in self._overlays.items():
            overlay_dir = Path(output_dir) / "overlays" / overlay_name
            overlay_dir.mkdir(parents=True, exist_ok=True)
            overlay._generate_overlay(overlay_dir, "../../../base")
        
        # Generate patches
        self._generate_patches(base_dir)
        
        print(f"✅ Kustomize configuration generated in: {output_dir}")
    
    def _generate_base_resources(self, base_dir: Path) -> None:
        """Generate base resource files."""
        for i, resource in enumerate(self._resources):
            k8s_resources = resource.generate_kubernetes_resources()
            for j, k8s_resource in enumerate(k8s_resources):
                kind = k8s_resource.get("kind", "resource").lower()
                name = k8s_resource.get("metadata", {}).get("name", f"resource-{i}-{j}")
                filename = f"{kind}-{name}.yaml"
                
                with open(base_dir / filename, "w") as f:
                    yaml.dump(k8s_resource, f, default_flow_style=False, sort_keys=False)
    
    def _generate_base_kustomization(self, base_dir: Path) -> None:
        """Generate base kustomization.yaml."""
        kustomization = {"apiVersion": "kustomize.config.k8s.io/v1beta1", "kind": "Kustomization"}
        
        # Add resources
        resources = []
        for resource_file in base_dir.glob("*.yaml"):
            if resource_file.name != "kustomization.yaml":
                resources.append(resource_file.name)
        
        if resources:
            kustomization["resources"] = sorted(resources)
        
        # Add remote resources
        if self._remote_resources:
            if "resources" not in kustomization:
                kustomization["resources"] = []
            kustomization["resources"].extend(self._remote_resources)
        
        # Add common metadata
        if self._namespace:
            kustomization["namespace"] = self._namespace
        
        if self._name_prefix:
            kustomization["namePrefix"] = self._name_prefix
        
        if self._name_suffix:
            kustomization["nameSuffix"] = self._name_suffix
        
        if self._common_labels:
            kustomization["commonLabels"] = self._common_labels
        
        if self._common_annotations:
            kustomization["commonAnnotations"] = self._common_annotations
        
        # Add images
        if self._images:
            kustomization["images"] = self._images
        
        # Add patches
        if self._strategic_merge_patches:
            kustomization["patchesStrategicMerge"] = self._strategic_merge_patches
        
        if self._json6902_patches:
            kustomization["patchesJson6902"] = self._json6902_patches
        
        # Add generators
        if self._config_map_generator:
            kustomization["configMapGenerator"] = self._config_map_generator
        
        if self._secret_generator:
            kustomization["secretGenerator"] = self._secret_generator
        
        # Add Helm charts
        if self._helmcharts:
            kustomization["helmCharts"] = self._helmcharts
        
        # Add CRDs
        if self._crds:
            kustomization["crds"] = self._crds
        
        # Add generators and transformers
        if self._generators:
            kustomization["generators"] = self._generators
        
        if self._transformers:
            kustomization["transformers"] = self._transformers
        
        with open(base_dir / "kustomization.yaml", "w") as f:
            yaml.dump(kustomization, f, default_flow_style=False, sort_keys=False)
    
    def _generate_overlay(self, overlay_dir: Path, base_path: str) -> None:
        """Generate overlay kustomization."""
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "resources": [base_path]
        }
        
        # Add overlay-specific configurations
        if self._namespace:
            kustomization["namespace"] = self._namespace
        
        if self._name_prefix:
            kustomization["namePrefix"] = self._name_prefix
        
        if self._name_suffix:
            kustomization["nameSuffix"] = self._name_suffix
        
        if self._common_labels:
            kustomization["commonLabels"] = self._common_labels
        
        if self._common_annotations:
            kustomization["commonAnnotations"] = self._common_annotations
        
        if self._images:
            kustomization["images"] = self._images
        
        if self._strategic_merge_patches:
            kustomization["patchesStrategicMerge"] = self._strategic_merge_patches
        
        if self._json6902_patches:
            kustomization["patchesJson6902"] = self._json6902_patches
        
        if self._config_map_generator:
            kustomization["configMapGenerator"] = self._config_map_generator
        
        if self._secret_generator:
            kustomization["secretGenerator"] = self._secret_generator
        
        # Generate overlay patches
        self._generate_patches(overlay_dir)
        
        with open(overlay_dir / "kustomization.yaml", "w") as f:
            yaml.dump(kustomization, f, default_flow_style=False, sort_keys=False)
    
    def _generate_patches(self, output_dir: Path) -> None:
        """Generate patch files."""
        for patch in self._patches:
            patch_file = patch["file"]
            patch_content = patch["content"]
            
            with open(output_dir / patch_file, "w") as f:
                yaml.dump(patch_content, f, default_flow_style=False, sort_keys=False) 