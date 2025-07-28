"""
Validator class for advanced validation engine in Celestraa DSL.

This module provides comprehensive validation capabilities including schema validation,
policy validation, best practices checking, and resource interdependency validation.
"""

import re
import yaml
import json
from typing import Dict, List, Any, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass
from ..core.base_builder import BaseBuilder


class ValidationLevel(Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationRule:
    """Validation rule definition."""
    name: str
    level: ValidationLevel
    description: str
    check_function: Callable[[Dict[str, Any]], List[str]]
    categories: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []


@dataclass
class ValidationResult:
    """Validation result."""
    rule_name: str
    level: ValidationLevel
    message: str
    resource_name: str
    resource_kind: str
    categories: List[str]
    fix_suggestion: Optional[str] = None


class Validator:
    """
    Advanced validation engine for Kubernetes resources.
    
    Provides comprehensive validation including schema validation, policy validation,
    best practices checking, and resource interdependency validation.
    
    Example:
        ```python
        validator = Validator()
        validator.enable_schema_validation()
        validator.enable_best_practices()
        validator.add_custom_rule("no-latest-tags", ValidationLevel.WARNING, 
                                lambda r: check_no_latest_tags(r))
        
        results = validator.validate_resources(resources)
        critical_issues = validator.get_issues_by_level(ValidationLevel.CRITICAL)
        ```
    """
    
    def __init__(self):
        """Initialize the validator."""
        self._rules: Dict[str, ValidationRule] = {}
        self._enabled_categories: List[str] = []
        self._schema_validation: bool = False
        self._policy_validation: bool = False
        self._best_practices: bool = False
        self._strict_mode: bool = False
        self._custom_policies: List[Dict[str, Any]] = []
        
        # Load built-in rules
        self._load_builtin_rules()
    
    def enable_schema_validation(self) -> "Validator":
        """
        Enable Kubernetes schema validation.
        
        Returns:
            Validator: Self for method chaining
        """
        self._schema_validation = True
        return self
    
    def enable_policy_validation(self) -> "Validator":
        """
        Enable policy validation (OPA/Gatekeeper style).
        
        Returns:
            Validator: Self for method chaining
        """
        self._policy_validation = True
        return self
    
    def enable_best_practices(self) -> "Validator":
        """
        Enable best practices validation.
        
        Returns:
            Validator: Self for method chaining
        """
        self._best_practices = True
        self._enabled_categories.extend(["best-practices", "security", "performance", "reliability"])
        return self
    
    def enable_strict_mode(self) -> "Validator":
        """
        Enable strict validation mode.
        
        Returns:
            Validator: Self for method chaining
        """
        self._strict_mode = True
        return self
    
    def enable_category(self, category: str) -> "Validator":
        """
        Enable validation for specific category.
        
        Args:
            category: Validation category
            
        Returns:
            Validator: Self for method chaining
        """
        if category not in self._enabled_categories:
            self._enabled_categories.append(category)
        return self
    
    def add_custom_rule(
        self,
        name: str,
        level: ValidationLevel,
        check_function: Callable[[Dict[str, Any]], List[str]],
        description: str = "",
        categories: List[str] = None
    ) -> "Validator":
        """
        Add custom validation rule.
        
        Args:
            name: Rule name
            level: Validation level
            check_function: Function that checks the rule
            description: Rule description
            categories: Rule categories
            
        Returns:
            Validator: Self for method chaining
        """
        rule = ValidationRule(
            name=name,
            level=level,
            description=description,
            check_function=check_function,
            categories=categories or ["custom"]
        )
        self._rules[name] = rule
        return self
    
    def add_policy(self, policy: Dict[str, Any]) -> "Validator":
        """
        Add custom policy for validation.
        
        Args:
            policy: Policy definition
            
        Returns:
            Validator: Self for method chaining
        """
        self._custom_policies.append(policy)
        return self
    
    def validate_resources(self, resources: List[Dict[str, Any]]) -> List[ValidationResult]:
        """
        Validate a list of Kubernetes resources.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[ValidationResult]: Validation results
        """
        results = []
        
        for resource in resources:
            resource_results = self.validate_resource(resource)
            results.extend(resource_results)
        
        # Cross-resource validation
        cross_results = self._validate_resource_dependencies(resources)
        results.extend(cross_results)
        
        return results
    
    def validate_resource(self, resource: Dict[str, Any]) -> List[ValidationResult]:
        """
        Validate a single Kubernetes resource.
        
        Args:
            resource: Kubernetes resource
            
        Returns:
            List[ValidationResult]: Validation results
        """
        results = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Schema validation
        if self._schema_validation:
            schema_results = self._validate_schema(resource)
            results.extend(schema_results)
        
        # Rule-based validation
        for rule_name, rule in self._rules.items():
            # Check if rule category is enabled
            if self._enabled_categories and not any(cat in rule.categories for cat in self._enabled_categories):
                continue
            
            try:
                violations = rule.check_function(resource)
                for violation in violations:
                    result = ValidationResult(
                        rule_name=rule_name,
                        level=rule.level,
                        message=violation,
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        categories=rule.categories
                    )
                    results.append(result)
            except Exception as e:
                # Log rule execution error
                error_result = ValidationResult(
                    rule_name=rule_name,
                    level=ValidationLevel.ERROR,
                    message=f"Validation rule execution failed: {e}",
                    resource_name=resource_name,
                    resource_kind=resource_kind,
                    categories=["internal-error"]
                )
                results.append(error_result)
        
        # Policy validation
        if self._policy_validation:
            policy_results = self._validate_policies(resource)
            results.extend(policy_results)
        
        return results
    
    def get_issues_by_level(self, results: List[ValidationResult], level: ValidationLevel) -> List[ValidationResult]:
        """
        Filter validation results by level.
        
        Args:
            results: Validation results
            level: Validation level to filter
            
        Returns:
            List[ValidationResult]: Filtered results
        """
        return [r for r in results if r.level == level]
    
    def get_issues_by_category(self, results: List[ValidationResult], category: str) -> List[ValidationResult]:
        """
        Filter validation results by category.
        
        Args:
            results: Validation results  
            category: Category to filter
            
        Returns:
            List[ValidationResult]: Filtered results
        """
        return [r for r in results if category in r.categories]
    
    def generate_report(self, results: List[ValidationResult]) -> str:
        """
        Generate validation report.
        
        Args:
            results: Validation results
            
        Returns:
            str: Formatted validation report
        """
        if not results:
            return "✅ No validation issues found!"
        
        # Group by level
        by_level = {}
        for result in results:
            level = result.level.value
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(result)
        
        report = []
        report.append("📋 VALIDATION REPORT")
        report.append("=" * 50)
        
        # Summary
        total = len(results)
        critical = len(by_level.get("critical", []))
        errors = len(by_level.get("error", []))
        warnings = len(by_level.get("warning", []))
        info = len(by_level.get("info", []))
        
        report.append(f"📊 Summary: {total} issues found")
        report.append(f"  🔴 Critical: {critical}")
        report.append(f"  ❌ Errors: {errors}")
        report.append(f"  ⚠️ Warnings: {warnings}")
        report.append(f"  ℹ️ Info: {info}")
        report.append("")
        
        # Details by level
        for level in ["critical", "error", "warning", "info"]:
            if level not in by_level:
                continue
            
            level_icon = {"critical": "🔴", "error": "❌", "warning": "⚠️", "info": "ℹ️"}[level]
            report.append(f"{level_icon} {level.upper()} ISSUES")
            report.append("-" * 30)
            
            for result in by_level[level]:
                report.append(f"• {result.resource_kind}/{result.resource_name}")
                report.append(f"  Rule: {result.rule_name}")
                report.append(f"  Issue: {result.message}")
                if result.fix_suggestion:
                    report.append(f"  Fix: {result.fix_suggestion}")
                report.append("")
        
        return "\n".join(report)
    
    def _load_builtin_rules(self) -> None:
        """Load built-in validation rules."""
        
        # Container security rules
        self._rules["no-root-user"] = ValidationRule(
            name="no-root-user",
            level=ValidationLevel.WARNING,
            description="Containers should not run as root user",
            check_function=self._check_no_root_user,
            categories=["security", "best-practices"]
        )
        
        self._rules["no-privileged-containers"] = ValidationRule(
            name="no-privileged-containers",
            level=ValidationLevel.CRITICAL,
            description="Containers should not run in privileged mode",
            check_function=self._check_no_privileged_containers,
            categories=["security"]
        )
        
        self._rules["resource-limits"] = ValidationRule(
            name="resource-limits",
            level=ValidationLevel.WARNING,
            description="Containers should have resource limits",
            check_function=self._check_resource_limits,
            categories=["best-practices", "performance"]
        )
        
        self._rules["no-latest-images"] = ValidationRule(
            name="no-latest-images",
            level=ValidationLevel.WARNING,
            description="Container images should not use 'latest' tag",
            check_function=self._check_no_latest_images,
            categories=["best-practices", "reliability"]
        )
        
        self._rules["liveness-probes"] = ValidationRule(
            name="liveness-probes",
            level=ValidationLevel.INFO,
            description="Deployments should have liveness probes",
            check_function=self._check_liveness_probes,
            categories=["best-practices", "reliability"]
        )
        
        self._rules["readiness-probes"] = ValidationRule(
            name="readiness-probes",
            level=ValidationLevel.INFO,
            description="Deployments should have readiness probes",
            check_function=self._check_readiness_probes,
            categories=["best-practices", "reliability"]
        )
        
        # Network security rules
        self._rules["network-policies"] = ValidationRule(
            name="network-policies",
            level=ValidationLevel.WARNING,
            description="Namespaces should have network policies",
            check_function=self._check_network_policies,
            categories=["security", "networking"]
        )
        
        # RBAC rules
        self._rules["no-cluster-admin"] = ValidationRule(
            name="no-cluster-admin",
            level=ValidationLevel.ERROR,
            description="Avoid using cluster-admin role",
            check_function=self._check_no_cluster_admin,
            categories=["security", "rbac"]
        )
        
        # Metadata rules
        self._rules["required-labels"] = ValidationRule(
            name="required-labels",
            level=ValidationLevel.INFO,
            description="Resources should have required labels",
            check_function=self._check_required_labels,
            categories=["best-practices", "metadata"]
        )
    
    # Built-in rule implementations
    
    def _check_no_root_user(self, resource: Dict[str, Any]) -> List[str]:
        """Check if containers run as root user."""
        issues = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                security_context = container.get("securityContext", {})
                run_as_user = security_context.get("runAsUser")
                run_as_non_root = security_context.get("runAsNonRoot")
                
                if run_as_user == 0:
                    issues.append(f"Container '{container['name']}' runs as root user (UID 0)")
                elif run_as_non_root is False:
                    issues.append(f"Container '{container['name']}' explicitly allows root user")
        
        return issues
    
    def _check_no_privileged_containers(self, resource: Dict[str, Any]) -> List[str]:
        """Check for privileged containers."""
        issues = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                security_context = container.get("securityContext", {})
                if security_context.get("privileged", False):
                    issues.append(f"Container '{container['name']}' runs in privileged mode")
        
        return issues
    
    def _check_resource_limits(self, resource: Dict[str, Any]) -> List[str]:
        """Check for resource limits."""
        issues = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                resources = container.get("resources", {})
                limits = resources.get("limits", {})
                
                if not limits.get("cpu"):
                    issues.append(f"Container '{container['name']}' missing CPU limit")
                if not limits.get("memory"):
                    issues.append(f"Container '{container['name']}' missing memory limit")
        
        return issues
    
    def _check_no_latest_images(self, resource: Dict[str, Any]) -> List[str]:
        """Check for latest image tags."""
        issues = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                image = container.get("image", "")
                if image.endswith(":latest") or ":" not in image:
                    issues.append(f"Container '{container['name']}' uses 'latest' or untagged image")
        
        return issues
    
    def _check_liveness_probes(self, resource: Dict[str, Any]) -> List[str]:
        """Check for liveness probes."""
        issues = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                if not container.get("livenessProbe"):
                    issues.append(f"Container '{container['name']}' missing liveness probe")
        
        return issues
    
    def _check_readiness_probes(self, resource: Dict[str, Any]) -> List[str]:
        """Check for readiness probes."""
        issues = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                if not container.get("readinessProbe"):
                    issues.append(f"Container '{container['name']}' missing readiness probe")
        
        return issues
    
    def _check_network_policies(self, resource: Dict[str, Any]) -> List[str]:
        """Check for network policies."""
        issues = []
        
        if resource.get("kind") == "Namespace":
            # This would need to check if NetworkPolicy exists for this namespace
            # For now, just warn about missing network policies
            issues.append("Consider adding NetworkPolicy for network segmentation")
        
        return issues
    
    def _check_no_cluster_admin(self, resource: Dict[str, Any]) -> List[str]:
        """Check for cluster-admin usage."""
        issues = []
        
        if resource.get("kind") in ["ClusterRoleBinding", "RoleBinding"]:
            role_ref = resource.get("roleRef", {})
            if role_ref.get("name") == "cluster-admin":
                issues.append("Using cluster-admin role grants excessive permissions")
        
        return issues
    
    def _check_required_labels(self, resource: Dict[str, Any]) -> List[str]:
        """Check for required labels."""
        issues = []
        required_labels = ["app.kubernetes.io/name", "app.kubernetes.io/version"]
        
        labels = resource.get("metadata", {}).get("labels", {})
        
        for required_label in required_labels:
            if required_label not in labels:
                issues.append(f"Missing required label: {required_label}")
        
        return issues
    
    def _get_containers(self, resource: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get containers from a resource."""
        containers = []
        
        # Handle different resource structures
        if resource.get("kind") == "CronJob":
            job_template = resource.get("spec", {}).get("jobTemplate", {})
            pod_spec = job_template.get("spec", {}).get("template", {}).get("spec", {})
        else:
            pod_spec = resource.get("spec", {}).get("template", {}).get("spec", {})
        
        containers.extend(pod_spec.get("containers", []))
        containers.extend(pod_spec.get("initContainers", []))
        
        return containers
    
    def _validate_schema(self, resource: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resource against Kubernetes schema."""
        # This would integrate with kubernetes-validate or similar
        # For now, basic structure validation
        results = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Basic required fields
        if not resource.get("apiVersion"):
            results.append(ValidationResult(
                rule_name="schema-validation",
                level=ValidationLevel.ERROR,
                message="Missing required field: apiVersion",
                resource_name=resource_name,
                resource_kind=resource_kind,
                categories=["schema"]
            ))
        
        if not resource.get("kind"):
            results.append(ValidationResult(
                rule_name="schema-validation",
                level=ValidationLevel.ERROR,
                message="Missing required field: kind",
                resource_name=resource_name,
                resource_kind=resource_kind,
                categories=["schema"]
            ))
        
        if not resource.get("metadata", {}).get("name"):
            results.append(ValidationResult(
                rule_name="schema-validation",
                level=ValidationLevel.ERROR,
                message="Missing required field: metadata.name",
                resource_name=resource_name,
                resource_kind=resource_kind,
                categories=["schema"]
            ))
        
        return results
    
    def _validate_policies(self, resource: Dict[str, Any]) -> List[ValidationResult]:
        """Validate resource against custom policies."""
        results = []
        
        for policy in self._custom_policies:
            # Simple policy implementation
            # In a real implementation, this would use OPA or similar
            policy_results = self._evaluate_policy(resource, policy)
            results.extend(policy_results)
        
        return results
    
    def _evaluate_policy(self, resource: Dict[str, Any], policy: Dict[str, Any]) -> List[ValidationResult]:
        """Evaluate a policy against a resource."""
        # Simplified policy evaluation
        # Real implementation would use Rego or similar policy language
        return []
    
    def _validate_resource_dependencies(self, resources: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate dependencies between resources."""
        results = []
        
        # Check for orphaned resources
        services = [r for r in resources if r.get("kind") == "Service"]
        deployments = [r for r in resources if r.get("kind") == "Deployment"]
        
        for service in services:
            selector = service.get("spec", {}).get("selector", {})
            if selector:
                # Check if any deployment matches this selector
                matching_deployment = False
                for deployment in deployments:
                    labels = deployment.get("spec", {}).get("template", {}).get("metadata", {}).get("labels", {})
                    if all(labels.get(k) == v for k, v in selector.items()):
                        matching_deployment = True
                        break
                
                if not matching_deployment:
                    results.append(ValidationResult(
                        rule_name="orphaned-service",
                        level=ValidationLevel.WARNING,
                        message="Service has no matching deployment",
                        resource_name=service.get("metadata", {}).get("name", "unknown"),
                        resource_kind="Service",
                        categories=["dependencies"]
                    ))
        
        return results 