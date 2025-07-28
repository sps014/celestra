"""
CustomResource class for custom Kubernetes resources in Celestraa DSL.

This module provides support for creating and managing Custom Resource Definitions (CRDs)
and Custom Resources with validation, status management, and controller integration.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from ..core.base_builder import BaseBuilder


class CRDScope(Enum):
    """CRD scope types."""
    NAMESPACED = "Namespaced"
    CLUSTER = "Cluster"


class CustomResource(BaseBuilder):
    """
    Builder class for custom Kubernetes resources.
    
    Provides comprehensive support for Custom Resource Definitions (CRDs)
    and Custom Resources with validation, versioning, and controller integration.
    
    Example:
        ```python
        app_crd = (CustomResource("application")
            .group("example.com")
            .version("v1")
            .scope(CRDScope.NAMESPACED)
            .add_property("replicas", "integer", required=True)
            .add_property("image", "string", required=True)
            .add_status_property("phase", "string")
            .enable_validation())
        ```
    """
    
    def __init__(self, name: str):
        """
        Initialize the CustomResource builder.
        
        Args:
            name: Name of the custom resource (singular form)
        """
        super().__init__(name)
        self._group: str = "example.com"
        self._version: str = "v1"
        self._scope: CRDScope = CRDScope.NAMESPACED
        self._plural: Optional[str] = None
        self._kind: Optional[str] = None
        self._short_names: List[str] = []
        self._categories: List[str] = []
        self._spec_properties: Dict[str, Dict[str, Any]] = {}
        self._status_properties: Dict[str, Dict[str, Any]] = {}
        self._required_properties: List[str] = []
        self._validation_enabled: bool = True
        self._subresources_enabled: bool = True
        self._printer_columns: List[Dict[str, Any]] = []
        self._webhook_config: Optional[Dict[str, Any]] = None
        self._controller_config: Optional[Dict[str, Any]] = None
        self._instances: List[Dict[str, Any]] = []
    
    def group(self, group: str) -> "CustomResource":
        """
        Set the API group for the CRD.
        
        Args:
            group: API group name (e.g., "example.com")
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._group = group
        return self
    
    def version(self, version: str) -> "CustomResource":
        """
        Set the API version for the CRD.
        
        Args:
            version: API version (e.g., "v1", "v1alpha1")
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._version = version
        return self
    
    def scope(self, scope: CRDScope) -> "CustomResource":
        """
        Set the scope of the CRD.
        
        Args:
            scope: Resource scope (Namespaced or Cluster)
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._scope = scope
        return self
    
    def names(
        self,
        plural: Optional[str] = None,
        kind: Optional[str] = None,
        short_names: Optional[List[str]] = None,
        categories: Optional[List[str]] = None
    ) -> "CustomResource":
        """
        Set the resource names.
        
        Args:
            plural: Plural form of the resource name
            kind: Kind name for the resource
            short_names: Short names for kubectl
            categories: Categories for kubectl get all
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._plural = plural or f"{self._name}s"
        self._kind = kind or self._name.capitalize()
        self._short_names = short_names or []
        self._categories = categories or []
        return self
    
    def add_property(
        self,
        name: str,
        property_type: str,
        description: Optional[str] = None,
        required: bool = False,
        default: Optional[Any] = None,
        enum_values: Optional[List[str]] = None,
        pattern: Optional[str] = None,
        minimum: Optional[int] = None,
        maximum: Optional[int] = None
    ) -> "CustomResource":
        """
        Add a property to the spec schema.
        
        Args:
            name: Property name
            property_type: Property type (string, integer, boolean, object, array)
            description: Property description
            required: Whether the property is required
            default: Default value
            enum_values: List of allowed values (for enum)
            pattern: Regex pattern for string validation
            minimum: Minimum value for integer/number
            maximum: Maximum value for integer/number
            
        Returns:
            CustomResource: Self for method chaining
        """
        property_schema = {
            "type": property_type
        }
        
        if description:
            property_schema["description"] = description
        
        if default is not None:
            property_schema["default"] = default
        
        if enum_values:
            property_schema["enum"] = enum_values
        
        if pattern:
            property_schema["pattern"] = pattern
        
        if minimum is not None:
            property_schema["minimum"] = minimum
        
        if maximum is not None:
            property_schema["maximum"] = maximum
        
        self._spec_properties[name] = property_schema
        
        if required:
            self._required_properties.append(name)
        
        return self
    
    def add_object_property(
        self,
        name: str,
        properties: Dict[str, Dict[str, Any]],
        required: bool = False,
        description: Optional[str] = None
    ) -> "CustomResource":
        """
        Add an object property to the spec schema.
        
        Args:
            name: Property name
            properties: Object properties
            required: Whether the property is required
            description: Property description
            
        Returns:
            CustomResource: Self for method chaining
        """
        property_schema = {
            "type": "object",
            "properties": properties
        }
        
        if description:
            property_schema["description"] = description
        
        self._spec_properties[name] = property_schema
        
        if required:
            self._required_properties.append(name)
        
        return self
    
    def add_array_property(
        self,
        name: str,
        item_type: str,
        item_schema: Optional[Dict[str, Any]] = None,
        required: bool = False,
        description: Optional[str] = None
    ) -> "CustomResource":
        """
        Add an array property to the spec schema.
        
        Args:
            name: Property name
            item_type: Type of array items
            item_schema: Schema for array items (for object arrays)
            required: Whether the property is required
            description: Property description
            
        Returns:
            CustomResource: Self for method chaining
        """
        property_schema = {
            "type": "array",
            "items": {
                "type": item_type
            }
        }
        
        if item_schema:
            property_schema["items"].update(item_schema)
        
        if description:
            property_schema["description"] = description
        
        self._spec_properties[name] = property_schema
        
        if required:
            self._required_properties.append(name)
        
        return self
    
    def add_status_property(
        self,
        name: str,
        property_type: str,
        description: Optional[str] = None
    ) -> "CustomResource":
        """
        Add a property to the status schema.
        
        Args:
            name: Property name
            property_type: Property type
            description: Property description
            
        Returns:
            CustomResource: Self for method chaining
        """
        property_schema = {
            "type": property_type
        }
        
        if description:
            property_schema["description"] = description
        
        self._status_properties[name] = property_schema
        return self
    
    def add_printer_column(
        self,
        name: str,
        json_path: str,
        column_type: str = "string",
        description: Optional[str] = None,
        priority: int = 0
    ) -> "CustomResource":
        """
        Add a printer column for kubectl output.
        
        Args:
            name: Column name
            json_path: JSONPath to the field
            column_type: Column type (string, integer, boolean, date)
            description: Column description
            priority: Column priority (0 = always shown)
            
        Returns:
            CustomResource: Self for method chaining
        """
        column = {
            "name": name,
            "type": column_type,
            "jsonPath": json_path,
            "priority": priority
        }
        
        if description:
            column["description"] = description
        
        self._printer_columns.append(column)
        return self
    
    def enable_validation(self, enabled: bool = True) -> "CustomResource":
        """
        Enable/disable OpenAPI v3 schema validation.
        
        Args:
            enabled: Whether to enable validation
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._validation_enabled = enabled
        return self
    
    def enable_subresources(
        self,
        status: bool = True,
        scale: bool = False,
        scale_spec_path: str = ".spec.replicas",
        scale_status_path: str = ".status.replicas"
    ) -> "CustomResource":
        """
        Enable subresources (status, scale).
        
        Args:
            status: Enable status subresource
            scale: Enable scale subresource
            scale_spec_path: JSONPath to spec replicas field
            scale_status_path: JSONPath to status replicas field
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._subresources_enabled = status or scale
        
        if status:
            self.add_status_property("phase", "string", "Current phase of the resource")
            self.add_status_property("message", "string", "Human-readable message")
            self.add_status_property("lastUpdateTime", "string", "Last update timestamp")
        
        if scale:
            self.add_property("replicas", "integer", "Number of replicas", required=True, minimum=0)
            self.add_status_property("replicas", "integer", "Current number of replicas")
        
        return self
    
    def add_webhook(
        self,
        webhook_type: str,
        service_name: str,
        service_path: str,
        admission_review_versions: Optional[List[str]] = None
    ) -> "CustomResource":
        """
        Add admission webhook configuration.
        
        Args:
            webhook_type: Webhook type (validating, mutating)
            service_name: Webhook service name
            service_path: Webhook service path
            admission_review_versions: Supported AdmissionReview versions
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._webhook_config = {
            "type": webhook_type,
            "service_name": service_name,
            "service_path": service_path,
            "admission_review_versions": admission_review_versions or ["v1", "v1beta1"]
        }
        return self
    
    def add_controller(
        self,
        image: str,
        replicas: int = 1,
        service_account: Optional[str] = None,
        resources: Optional[Dict[str, str]] = None
    ) -> "CustomResource":
        """
        Add controller deployment configuration.
        
        Args:
            image: Controller image
            replicas: Number of controller replicas
            service_account: Service account for the controller
            resources: Resource requests/limits
            
        Returns:
            CustomResource: Self for method chaining
        """
        self._controller_config = {
            "image": image,
            "replicas": replicas,
            "service_account": service_account,
            "resources": resources or {"requests": {"cpu": "100m", "memory": "128Mi"}}
        }
        return self
    
    def create_instance(
        self,
        name: str,
        spec: Dict[str, Any],
        namespace: Optional[str] = None
    ) -> "CustomResource":
        """
        Create an instance of the custom resource.
        
        Args:
            name: Instance name
            spec: Instance specification
            namespace: Instance namespace (for namespaced resources)
            
        Returns:
            CustomResource: Self for method chaining
        """
        instance = {
            "name": name,
            "spec": spec,
            "namespace": namespace
        }
        self._instances.append(instance)
        return self
    
    # Preset configurations
    
    @classmethod
    def application_crd(cls, name: str = "application") -> "CustomResource":
        """
        Create an Application CRD.
        
        Args:
            name: CRD name
            
        Returns:
            CustomResource: Configured custom resource
        """
        return (cls(name)
            .group("apps.example.com")
            .names(plural="applications", kind="Application", short_names=["app"])
            .add_property("image", "string", "Container image", required=True)
            .add_property("replicas", "integer", "Number of replicas", required=True, minimum=1)
            .add_property("port", "integer", "Service port", default=8080)
            .add_printer_column("Image", ".spec.image")
            .add_printer_column("Replicas", ".spec.replicas", "integer")
            .add_printer_column("Phase", ".status.phase")
            .enable_subresources(status=True, scale=True))
    
    @classmethod
    def database_crd(cls, name: str = "database") -> "CustomResource":
        """
        Create a Database CRD.
        
        Args:
            name: CRD name
            
        Returns:
            CustomResource: Configured custom resource
        """
        return (cls(name)
            .group("data.example.com")
            .names(plural="databases", kind="Database", short_names=["db"])
            .add_property("engine", "string", "Database engine", required=True, 
                         enum_values=["postgresql", "mysql", "mongodb"])
            .add_property("version", "string", "Database version", required=True)
            .add_property("storage", "string", "Storage size", required=True, pattern=r"^\d+Gi$")
            .add_object_property("backup", {
                "enabled": {"type": "boolean", "default": True},
                "schedule": {"type": "string", "default": "0 2 * * *"},
                "retention": {"type": "string", "default": "30d"}
            })
            .add_printer_column("Engine", ".spec.engine")
            .add_printer_column("Version", ".spec.version")
            .add_printer_column("Storage", ".spec.storage")
            .add_printer_column("Status", ".status.phase"))
    
    def generate_kubernetes_resources(self) -> List[Dict[str, Any]]:
        """
        Generate Kubernetes resources for the custom resource.
        
        Returns:
            List[Dict[str, Any]]: List of Kubernetes resources
        """
        resources = []
        
        # Generate CRD
        crd = {
            "apiVersion": "apiextensions.k8s.io/v1",
            "kind": "CustomResourceDefinition",
            "metadata": {
                "name": f"{self._plural or f'{self._name}s'}.{self._group}",
                "labels": self._labels,
                "annotations": self._annotations
            },
            "spec": {
                "group": self._group,
                "versions": [{
                    "name": self._version,
                    "served": True,
                    "storage": True,
                    "schema": {
                        "openAPIV3Schema": self._generate_schema()
                    }
                }],
                "scope": self._scope.value,
                "names": {
                    "plural": self._plural or f"{self._name}s",
                    "singular": self._name,
                    "kind": self._kind or self._name.capitalize(),
                    "shortNames": self._short_names,
                    "categories": self._categories
                }
            }
        }
        
        # Add printer columns
        if self._printer_columns:
            crd["spec"]["versions"][0]["additionalPrinterColumns"] = self._printer_columns
        
        # Add subresources
        if self._subresources_enabled:
            subresources = {}
            
            if self._status_properties:
                subresources["status"] = {}
            
            # Check if scale subresource should be enabled
            if "replicas" in self._spec_properties and "replicas" in self._status_properties:
                subresources["scale"] = {
                    "specReplicasPath": ".spec.replicas",
                    "statusReplicasPath": ".status.replicas"
                }
            
            if subresources:
                crd["spec"]["versions"][0]["subresources"] = subresources
        
        resources.append(crd)
        
        # Generate RBAC for controller if configured
        if self._controller_config:
            # ServiceAccount
            service_account = {
                "apiVersion": "v1",
                "kind": "ServiceAccount",
                "metadata": {
                    "name": f"{self._name}-controller",
                    "labels": self._labels,
                    "annotations": self._annotations
                }
            }
            
            if self._namespace:
                service_account["metadata"]["namespace"] = self._namespace
            
            resources.append(service_account)
            
            # ClusterRole
            cluster_role = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRole",
                "metadata": {
                    "name": f"{self._name}-controller",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "rules": [
                    {
                        "apiGroups": [self._group],
                        "resources": [self._plural or f"{self._name}s"],
                        "verbs": ["get", "list", "watch", "create", "update", "patch", "delete"]
                    },
                    {
                        "apiGroups": [self._group],
                        "resources": [f"{self._plural or f'{self._name}s'}/status"],
                        "verbs": ["get", "update", "patch"]
                    },
                    {
                        "apiGroups": [""],
                        "resources": ["events"],
                        "verbs": ["create", "patch"]
                    }
                ]
            }
            
            resources.append(cluster_role)
            
            # ClusterRoleBinding
            cluster_role_binding = {
                "apiVersion": "rbac.authorization.k8s.io/v1",
                "kind": "ClusterRoleBinding",
                "metadata": {
                    "name": f"{self._name}-controller",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "roleRef": {
                    "apiGroup": "rbac.authorization.k8s.io",
                    "kind": "ClusterRole",
                    "name": f"{self._name}-controller"
                },
                "subjects": [{
                    "kind": "ServiceAccount",
                    "name": f"{self._name}-controller",
                    "namespace": self._namespace or "default"
                }]
            }
            
            resources.append(cluster_role_binding)
            
            # Controller Deployment
            controller_deployment = {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": f"{self._name}-controller",
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": {
                    "replicas": self._controller_config["replicas"],
                    "selector": {
                        "matchLabels": {
                            "app": f"{self._name}-controller"
                        }
                    },
                    "template": {
                        "metadata": {
                            "labels": {
                                "app": f"{self._name}-controller"
                            }
                        },
                        "spec": {
                            "serviceAccountName": f"{self._name}-controller",
                            "containers": [{
                                "name": "controller",
                                "image": self._controller_config["image"],
                                "resources": self._controller_config["resources"]
                            }]
                        }
                    }
                }
            }
            
            if self._namespace:
                controller_deployment["metadata"]["namespace"] = self._namespace
            
            resources.append(controller_deployment)
        
        # Generate custom resource instances
        for instance in self._instances:
            cr_instance = {
                "apiVersion": f"{self._group}/{self._version}",
                "kind": self._kind or self._name.capitalize(),
                "metadata": {
                    "name": instance["name"],
                    "labels": self._labels,
                    "annotations": self._annotations
                },
                "spec": instance["spec"]
            }
            
            if instance.get("namespace") and self._scope == CRDScope.NAMESPACED:
                cr_instance["metadata"]["namespace"] = instance["namespace"]
            elif self._namespace and self._scope == CRDScope.NAMESPACED:
                cr_instance["metadata"]["namespace"] = self._namespace
            
            resources.append(cr_instance)
        
        return resources
    
    def _generate_schema(self) -> Dict[str, Any]:
        """
        Generate OpenAPI v3 schema for the CRD.
        
        Returns:
            Dict[str, Any]: OpenAPI v3 schema
        """
        schema = {
            "type": "object",
            "properties": {
                "spec": {
                    "type": "object",
                    "properties": self._spec_properties
                }
            }
        }
        
        if self._required_properties:
            schema["properties"]["spec"]["required"] = self._required_properties
        
        if self._status_properties:
            schema["properties"]["status"] = {
                "type": "object",
                "properties": self._status_properties
            }
        
        return schema 