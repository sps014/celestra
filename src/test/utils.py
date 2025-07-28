"""
Test utilities and helper functions for Celestraa DSL tests.
"""

import os
import yaml
import json
import tempfile
import shutil
from typing import Dict, List, Any, Optional, Union
from pathlib import Path


class TestHelper:
    """Helper class for test operations."""
    
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.temp_dirs = []
        self.created_files = []
    
    def create_temp_dir(self, suffix: str = "") -> str:
        """Create a temporary directory for test artifacts."""
        temp_dir = tempfile.mkdtemp(suffix=f"_{self.test_name}_{suffix}")
        self.temp_dirs.append(temp_dir)
        return temp_dir
    
    def create_temp_file(self, content: str, suffix: str = ".yaml") -> str:
        """Create a temporary file with given content."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=f"_{self.test_name}_{suffix}",
            delete=False
        )
        temp_file.write(content)
        temp_file.close()
        self.created_files.append(temp_file.name)
        return temp_file.name
    
    def cleanup(self):
        """Clean up all temporary files and directories."""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
        
        for temp_file in self.created_files:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    def load_yaml_file(self, filepath: str) -> Dict[str, Any]:
        """Load and parse a YAML file."""
        with open(filepath, 'r') as f:
            return yaml.safe_load(f)
    
    def load_json_file(self, filepath: str) -> Dict[str, Any]:
        """Load and parse a JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def write_yaml_file(self, data: Dict[str, Any], filepath: str):
        """Write data to a YAML file."""
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def write_json_file(self, data: Dict[str, Any], filepath: str):
        """Write data to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


class MockKubernetesCluster:
    """Mock Kubernetes cluster for testing without actual cluster."""
    
    def __init__(self):
        self.resources = {}
        self.namespaces = ["default", "kube-system"]
    
    def apply_resource(self, resource: Dict[str, Any]):
        """Apply a resource to the mock cluster."""
        kind = resource.get("kind", "Unknown")
        name = resource.get("metadata", {}).get("name", "unknown")
        namespace = resource.get("metadata", {}).get("namespace", "default")
        
        key = f"{namespace}/{kind}/{name}"
        self.resources[key] = resource
    
    def get_resource(self, kind: str, name: str, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """Get a resource from the mock cluster."""
        key = f"{namespace}/{kind}/{name}"
        return self.resources.get(key)
    
    def list_resources(self, kind: str, namespace: str = "default") -> List[Dict[str, Any]]:
        """List all resources of a given kind in a namespace."""
        return [
            resource for key, resource in self.resources.items()
            if key.startswith(f"{namespace}/{kind}/")
        ]
    
    def delete_resource(self, kind: str, name: str, namespace: str = "default"):
        """Delete a resource from the mock cluster."""
        key = f"{namespace}/{kind}/{name}"
        if key in self.resources:
            del self.resources[key]
    
    def create_namespace(self, name: str):
        """Create a namespace in the mock cluster."""
        if name not in self.namespaces:
            self.namespaces.append(name)
    
    def reset(self):
        """Reset the mock cluster to initial state."""
        self.resources = {}
        self.namespaces = ["default", "kube-system"]


class AssertionHelper:
    """Helper class for making assertions about generated resources."""
    
    @staticmethod
    def assert_resource_exists(resources: List[Dict[str, Any]], kind: str, name: str):
        """Assert that a resource of given kind and name exists."""
        matching_resources = [
            r for r in resources 
            if r.get("kind") == kind and r.get("metadata", {}).get("name") == name
        ]
        assert len(matching_resources) > 0, f"Resource {kind}/{name} not found"
        return matching_resources[0]
    
    @staticmethod
    def assert_resource_has_label(resource: Dict[str, Any], label_key: str, label_value: str):
        """Assert that a resource has a specific label."""
        labels = resource.get("metadata", {}).get("labels", {})
        assert label_key in labels, f"Label {label_key} not found in resource"
        assert labels[label_key] == label_value, f"Label {label_key} has value {labels[label_key]}, expected {label_value}"
    
    @staticmethod
    def assert_resource_has_annotation(resource: Dict[str, Any], annotation_key: str, annotation_value: str):
        """Assert that a resource has a specific annotation."""
        annotations = resource.get("metadata", {}).get("annotations", {})
        assert annotation_key in annotations, f"Annotation {annotation_key} not found in resource"
        assert annotations[annotation_key] == annotation_value, f"Annotation {annotation_key} has value {annotations[annotation_key]}, expected {annotation_value}"
    
    @staticmethod
    def assert_deployment_has_containers(deployment: Dict[str, Any], container_count: int):
        """Assert that a deployment has the expected number of containers."""
        containers = deployment.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
        assert len(containers) == container_count, f"Expected {container_count} containers, found {len(containers)}"
    
    @staticmethod
    def assert_container_has_port(container: Dict[str, Any], port: int, name: str = None):
        """Assert that a container exposes a specific port."""
        ports = container.get("ports", [])
        matching_ports = [p for p in ports if p.get("containerPort") == port]
        assert len(matching_ports) > 0, f"Port {port} not found in container"
        
        if name:
            matching_named_ports = [p for p in matching_ports if p.get("name") == name]
            assert len(matching_named_ports) > 0, f"Port {port} with name {name} not found in container"
    
    @staticmethod
    def assert_container_has_env_var(container: Dict[str, Any], env_name: str, env_value: str = None):
        """Assert that a container has a specific environment variable."""
        env_vars = container.get("env", [])
        matching_env = [e for e in env_vars if e.get("name") == env_name]
        assert len(matching_env) > 0, f"Environment variable {env_name} not found in container"
        
        if env_value:
            assert matching_env[0].get("value") == env_value, f"Environment variable {env_name} has wrong value"
    
    @staticmethod
    def assert_service_has_port(service: Dict[str, Any], port: int, target_port: int = None, name: str = None):
        """Assert that a service exposes a specific port."""
        ports = service.get("spec", {}).get("ports", [])
        matching_ports = [p for p in ports if p.get("port") == port]
        assert len(matching_ports) > 0, f"Service port {port} not found"
        
        if target_port:
            assert matching_ports[0].get("targetPort") == target_port, f"Service port {port} has wrong target port"
        
        if name:
            assert matching_ports[0].get("name") == name, f"Service port {port} has wrong name"
    
    @staticmethod
    def assert_volume_mounted(container: Dict[str, Any], volume_name: str, mount_path: str):
        """Assert that a volume is mounted in a container."""
        volume_mounts = container.get("volumeMounts", [])
        matching_mounts = [vm for vm in volume_mounts if vm.get("name") == volume_name]
        assert len(matching_mounts) > 0, f"Volume {volume_name} not mounted in container"
        assert matching_mounts[0].get("mountPath") == mount_path, f"Volume {volume_name} mounted at wrong path"
    
    @staticmethod
    def assert_resource_limits(container: Dict[str, Any], cpu: str = None, memory: str = None):
        """Assert that a container has specific resource limits."""
        resources = container.get("resources", {})
        limits = resources.get("limits", {})
        
        if cpu:
            assert "cpu" in limits, "CPU limit not set"
            assert limits["cpu"] == cpu, f"CPU limit is {limits['cpu']}, expected {cpu}"
        
        if memory:
            assert "memory" in limits, "Memory limit not set"
            assert limits["memory"] == memory, f"Memory limit is {limits['memory']}, expected {memory}"
    
    @staticmethod
    def assert_pod_security_context(pod_spec: Dict[str, Any], run_as_non_root: bool = None, fs_group: int = None):
        """Assert pod security context settings."""
        security_context = pod_spec.get("securityContext", {})
        
        if run_as_non_root is not None:
            assert security_context.get("runAsNonRoot") == run_as_non_root, f"runAsNonRoot should be {run_as_non_root}"
        
        if fs_group is not None:
            assert security_context.get("fsGroup") == fs_group, f"fsGroup should be {fs_group}"
    
    @staticmethod
    def assert_ingress_has_rule(ingress: Dict[str, Any], host: str, path: str, service_name: str, service_port: int):
        """Assert that an ingress has a specific rule."""
        rules = ingress.get("spec", {}).get("rules", [])
        matching_rules = [r for r in rules if r.get("host") == host]
        assert len(matching_rules) > 0, f"Ingress rule for host {host} not found"
        
        paths = matching_rules[0].get("http", {}).get("paths", [])
        matching_paths = [p for p in paths if p.get("path") == path]
        assert len(matching_paths) > 0, f"Ingress path {path} not found for host {host}"
        
        backend = matching_paths[0].get("backend", {}).get("service", {})
        assert backend.get("name") == service_name, f"Backend service name should be {service_name}"
        assert backend.get("port", {}).get("number") == service_port, f"Backend service port should be {service_port}"


class ResourceValidator:
    """Validates generated Kubernetes resources."""
    
    @staticmethod
    def validate_yaml_syntax(yaml_content: str) -> bool:
        """Validate YAML syntax."""
        try:
            yaml.safe_load(yaml_content)
            return True
        except yaml.YAMLError:
            return False
    
    @staticmethod
    def validate_kubernetes_resource(resource: Dict[str, Any]) -> List[str]:
        """Validate a Kubernetes resource structure."""
        errors = []
        
        # Check required fields
        if "apiVersion" not in resource:
            errors.append("Missing required field: apiVersion")
        
        if "kind" not in resource:
            errors.append("Missing required field: kind")
        
        if "metadata" not in resource:
            errors.append("Missing required field: metadata")
        elif "name" not in resource.get("metadata", {}):
            errors.append("Missing required field: metadata.name")
        
        # Validate specific resource types
        kind = resource.get("kind")
        if kind == "Deployment":
            errors.extend(ResourceValidator._validate_deployment(resource))
        elif kind == "Service":
            errors.extend(ResourceValidator._validate_service(resource))
        elif kind == "StatefulSet":
            errors.extend(ResourceValidator._validate_statefulset(resource))
        
        return errors
    
    @staticmethod
    def _validate_deployment(deployment: Dict[str, Any]) -> List[str]:
        """Validate a Deployment resource."""
        errors = []
        spec = deployment.get("spec", {})
        
        if "selector" not in spec:
            errors.append("Deployment missing spec.selector")
        
        if "template" not in spec:
            errors.append("Deployment missing spec.template")
        else:
            template_spec = spec["template"].get("spec", {})
            if "containers" not in template_spec:
                errors.append("Deployment template missing containers")
            elif not template_spec["containers"]:
                errors.append("Deployment template has empty containers list")
        
        return errors
    
    @staticmethod
    def _validate_service(service: Dict[str, Any]) -> List[str]:
        """Validate a Service resource."""
        errors = []
        spec = service.get("spec", {})
        
        if "ports" not in spec:
            errors.append("Service missing spec.ports")
        elif not spec["ports"]:
            errors.append("Service has empty ports list")
        
        if "selector" not in spec:
            errors.append("Service missing spec.selector")
        
        return errors
    
    @staticmethod
    def _validate_statefulset(statefulset: Dict[str, Any]) -> List[str]:
        """Validate a StatefulSet resource."""
        errors = []
        spec = statefulset.get("spec", {})
        
        if "serviceName" not in spec:
            errors.append("StatefulSet missing spec.serviceName")
        
        if "selector" not in spec:
            errors.append("StatefulSet missing spec.selector")
        
        if "template" not in spec:
            errors.append("StatefulSet missing spec.template")
        
        return errors


def run_test_with_cleanup(test_func):
    """Decorator to ensure test cleanup."""
    def wrapper(*args, **kwargs):
        helper = None
        try:
            result = test_func(*args, **kwargs)
            return result
        finally:
            # Clean up if helper was created
            if hasattr(test_func, '__self__') and hasattr(test_func.__self__, 'helper'):
                test_func.__self__.helper.cleanup()
            elif 'helper' in kwargs:
                kwargs['helper'].cleanup()
    return wrapper


def assert_no_yaml_errors(yaml_content: str):
    """Assert that YAML content is valid."""
    assert ResourceValidator.validate_yaml_syntax(yaml_content), "Invalid YAML syntax"


def assert_valid_kubernetes_resource(resource: Dict[str, Any]):
    """Assert that a resource is a valid Kubernetes resource."""
    errors = ResourceValidator.validate_kubernetes_resource(resource)
    assert len(errors) == 0, f"Invalid Kubernetes resource: {'; '.join(errors)}" 