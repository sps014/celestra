"""
SecurityScanner class for security vulnerability scanning in Celestraa DSL.

This module provides comprehensive security scanning including image vulnerability
scanning, security policy violations, RBAC analysis, and privilege escalation detection.
"""

import re
import base64
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass
from datetime import datetime


class SecurityLevel(Enum):
    """Security issue severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityFinding:
    """Security finding result."""
    finding_id: str
    title: str
    description: str
    level: SecurityLevel
    category: str
    resource_name: str
    resource_kind: str
    cve_id: Optional[str] = None
    fix_recommendation: Optional[str] = None
    references: List[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class ImageVulnerability:
    """Container image vulnerability."""
    cve_id: str
    severity: SecurityLevel
    package: str
    version: str
    fixed_version: Optional[str]
    description: str


class SecurityScanner:
    """
    Comprehensive security scanner for Kubernetes resources.
    
    Provides security scanning including image vulnerability scanning,
    security policy violations, RBAC analysis, and privilege escalation detection.
    
    Example:
        ```python
        scanner = SecurityScanner()
        scanner.enable_image_scanning()
        scanner.enable_rbac_analysis()
        scanner.enable_privilege_escalation_detection()
        
        findings = scanner.scan_resources(resources)
        critical_issues = scanner.get_findings_by_level(SecurityLevel.CRITICAL)
        scanner.generate_security_report(findings)
        ```
    """
    
    def __init__(self):
        """Initialize the security scanner."""
        self._image_scanning: bool = False
        self._rbac_analysis: bool = False
        self._privilege_escalation: bool = False
        self._network_analysis: bool = False
        self._secret_analysis: bool = False
        self._policy_violations: bool = False
        
        # Security databases (would be loaded from external sources)
        self._vulnerability_db: Dict[str, List[ImageVulnerability]] = {}
        self._known_malicious_images: Set[str] = set()
        self._security_benchmarks: Dict[str, Any] = {}
        
        # Load security data
        self._load_security_data()
    
    def enable_image_scanning(self) -> "SecurityScanner":
        """
        Enable container image vulnerability scanning.
        
        Returns:
            SecurityScanner: Self for method chaining
        """
        self._image_scanning = True
        return self
    
    def enable_rbac_analysis(self) -> "SecurityScanner":
        """
        Enable RBAC security analysis.
        
        Returns:
            SecurityScanner: Self for method chaining
        """
        self._rbac_analysis = True
        return self
    
    def enable_privilege_escalation_detection(self) -> "SecurityScanner":
        """
        Enable privilege escalation detection.
        
        Returns:
            SecurityScanner: Self for method chaining
        """
        self._privilege_escalation = True
        return self
    
    def enable_network_analysis(self) -> "SecurityScanner":
        """
        Enable network security analysis.
        
        Returns:
            SecurityScanner: Self for method chaining
        """
        self._network_analysis = True
        return self
    
    def enable_secret_analysis(self) -> "SecurityScanner":
        """
        Enable secret security analysis.
        
        Returns:
            SecurityScanner: Self for method chaining
        """
        self._secret_analysis = True
        return self
    
    def enable_policy_violations(self) -> "SecurityScanner":
        """
        Enable security policy violation detection.
        
        Returns:
            SecurityScanner: Self for method chaining
        """
        self._policy_violations = True
        return self
    
    def scan_resources(self, resources: List[Dict[str, Any]]) -> List[SecurityFinding]:
        """
        Scan Kubernetes resources for security issues.
        
        Args:
            resources: List of Kubernetes resources
            
        Returns:
            List[SecurityFinding]: Security findings
        """
        findings = []
        
        for resource in resources:
            resource_findings = self.scan_resource(resource)
            findings.extend(resource_findings)
        
        # Cross-resource security analysis
        cross_findings = self._analyze_cross_resource_security(resources)
        findings.extend(cross_findings)
        
        return findings
    
    def scan_resource(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """
        Scan a single Kubernetes resource.
        
        Args:
            resource: Kubernetes resource
            
        Returns:
            List[SecurityFinding]: Security findings
        """
        findings = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Image vulnerability scanning
        if self._image_scanning:
            image_findings = self._scan_images(resource)
            findings.extend(image_findings)
        
        # Privilege escalation detection
        if self._privilege_escalation:
            privilege_findings = self._detect_privilege_escalation(resource)
            findings.extend(privilege_findings)
        
        # RBAC analysis
        if self._rbac_analysis and resource_kind in ["Role", "ClusterRole", "RoleBinding", "ClusterRoleBinding"]:
            rbac_findings = self._analyze_rbac(resource)
            findings.extend(rbac_findings)
        
        # Secret analysis
        if self._secret_analysis and resource_kind == "Secret":
            secret_findings = self._analyze_secrets(resource)
            findings.extend(secret_findings)
        
        # Network analysis
        if self._network_analysis:
            network_findings = self._analyze_network_security(resource)
            findings.extend(network_findings)
        
        # Policy violations
        if self._policy_violations:
            policy_findings = self._check_policy_violations(resource)
            findings.extend(policy_findings)
        
        return findings
    
    def get_findings_by_level(self, findings: List[SecurityFinding], level: SecurityLevel) -> List[SecurityFinding]:
        """
        Filter findings by security level.
        
        Args:
            findings: Security findings
            level: Security level to filter
            
        Returns:
            List[SecurityFinding]: Filtered findings
        """
        return [f for f in findings if f.level == level]
    
    def get_findings_by_category(self, findings: List[SecurityFinding], category: str) -> List[SecurityFinding]:
        """
        Filter findings by category.
        
        Args:
            findings: Security findings
            category: Category to filter
            
        Returns:
            List[SecurityFinding]: Filtered findings
        """
        return [f for f in findings if f.category == category]
    
    def generate_security_report(self, findings: List[SecurityFinding]) -> str:
        """
        Generate security report.
        
        Args:
            findings: Security findings
            
        Returns:
            str: Formatted security report
        """
        if not findings:
            return "🔒 No security issues found!"
        
        # Group by level
        by_level = {}
        for finding in findings:
            level = finding.level.value
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(finding)
        
        # Group by category
        by_category = {}
        for finding in findings:
            category = finding.category
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(finding)
        
        report = []
        report.append("🔒 SECURITY SCAN REPORT")
        report.append("=" * 60)
        
        # Summary
        total = len(findings)
        critical = len(by_level.get("critical", []))
        high = len(by_level.get("high", []))
        medium = len(by_level.get("medium", []))
        low = len(by_level.get("low", []))
        
        report.append(f"📊 Security Summary: {total} issues found")
        report.append(f"  🔴 Critical: {critical}")
        report.append(f"  🟠 High: {high}")
        report.append(f"  🟡 Medium: {medium}")
        report.append(f"  🟢 Low: {low}")
        report.append("")
        
        # Category breakdown
        report.append("📋 Issues by Category:")
        for category, category_findings in by_category.items():
            report.append(f"  • {category}: {len(category_findings)}")
        report.append("")
        
        # Details by level
        for level in ["critical", "high", "medium", "low"]:
            if level not in by_level:
                continue
            
            level_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[level]
            report.append(f"{level_icon} {level.upper()} SECURITY ISSUES")
            report.append("-" * 40)
            
            for finding in by_level[level]:
                report.append(f"• {finding.title}")
                report.append(f"  Resource: {finding.resource_kind}/{finding.resource_name}")
                report.append(f"  Category: {finding.category}")
                report.append(f"  Description: {finding.description}")
                if finding.cve_id:
                    report.append(f"  CVE: {finding.cve_id}")
                if finding.fix_recommendation:
                    report.append(f"  Fix: {finding.fix_recommendation}")
                report.append("")
        
        # Security recommendations
        report.append("💡 SECURITY RECOMMENDATIONS")
        report.append("-" * 40)
        
        if critical > 0:
            report.append("🔴 URGENT: Address critical security issues immediately")
        if high > 0:
            report.append("🟠 HIGH: Address high-severity issues within 24 hours")
        if "image-vulnerabilities" in by_category:
            report.append("📦 Update container images to latest secure versions")
        if "rbac" in by_category:
            report.append("🔐 Review and minimize RBAC permissions")
        if "privilege-escalation" in by_category:
            report.append("⬆️ Remove unnecessary privileged access")
        if "network" in by_category:
            report.append("🌐 Implement network segmentation policies")
        
        return "\n".join(report)
    
    def _scan_images(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Scan container images for vulnerabilities."""
        findings = []
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                image = container.get("image", "")
                image_findings = self._scan_container_image(image, resource)
                findings.extend(image_findings)
        
        return findings
    
    def _scan_container_image(self, image: str, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Scan a specific container image."""
        findings = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Check for known malicious images
        if image in self._known_malicious_images:
            findings.append(SecurityFinding(
                finding_id="malicious-image",
                title="Malicious Container Image",
                description=f"Image '{image}' is known to be malicious",
                level=SecurityLevel.CRITICAL,
                category="image-vulnerabilities",
                resource_name=resource_name,
                resource_kind=resource_kind,
                fix_recommendation="Replace with a trusted image"
            ))
        
        # Check for vulnerabilities in image
        if image in self._vulnerability_db:
            vulnerabilities = self._vulnerability_db[image]
            for vuln in vulnerabilities:
                findings.append(SecurityFinding(
                    finding_id=f"cve-{vuln.cve_id}",
                    title=f"Container Image Vulnerability: {vuln.cve_id}",
                    description=f"Package {vuln.package} version {vuln.version} has {vuln.severity.value} vulnerability",
                    level=vuln.severity,
                    category="image-vulnerabilities",
                    resource_name=resource_name,
                    resource_kind=resource_kind,
                    cve_id=vuln.cve_id,
                    fix_recommendation=f"Update {vuln.package} to version {vuln.fixed_version}" if vuln.fixed_version else None
                ))
        
        # Check for insecure image configurations
        if image.endswith(":latest") or ":" not in image:
            findings.append(SecurityFinding(
                finding_id="latest-tag",
                title="Insecure Image Tag",
                description="Using 'latest' tag or untagged images is a security risk",
                level=SecurityLevel.MEDIUM,
                category="image-security",
                resource_name=resource_name,
                resource_kind=resource_kind,
                fix_recommendation="Use specific version tags for images"
            ))
        
        # Check for images from untrusted registries
        if not any(image.startswith(trusted) for trusted in ["gcr.io/", "docker.io/library/", "registry.k8s.io/"]):
            findings.append(SecurityFinding(
                finding_id="untrusted-registry",
                title="Untrusted Image Registry",
                description=f"Image from potentially untrusted registry: {image}",
                level=SecurityLevel.LOW,
                category="image-security",
                resource_name=resource_name,
                resource_kind=resource_kind,
                fix_recommendation="Use images from trusted registries"
            ))
        
        return findings
    
    def _detect_privilege_escalation(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Detect privilege escalation vulnerabilities."""
        findings = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        if resource.get("kind") in ["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"]:
            containers = self._get_containers(resource)
            
            for container in containers:
                container_name = container.get("name", "unknown")
                security_context = container.get("securityContext", {})
                
                # Check for privileged containers
                if security_context.get("privileged", False):
                    findings.append(SecurityFinding(
                        finding_id="privileged-container",
                        title="Privileged Container",
                        description=f"Container '{container_name}' runs in privileged mode",
                        level=SecurityLevel.CRITICAL,
                        category="privilege-escalation",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Remove privileged flag or use specific capabilities instead"
                    ))
                
                # Check for root user
                if security_context.get("runAsUser") == 0:
                    findings.append(SecurityFinding(
                        finding_id="root-user",
                        title="Container Running as Root",
                        description=f"Container '{container_name}' runs as root user",
                        level=SecurityLevel.HIGH,
                        category="privilege-escalation",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Use a non-root user (runAsUser > 0)"
                    ))
                
                # Check for dangerous capabilities
                capabilities = security_context.get("capabilities", {})
                dangerous_caps = ["SYS_ADMIN", "NET_ADMIN", "SYS_PTRACE", "SYS_MODULE"]
                
                add_caps = capabilities.get("add", [])
                for cap in add_caps:
                    if cap in dangerous_caps:
                        findings.append(SecurityFinding(
                            finding_id="dangerous-capability",
                            title="Dangerous Capability Added",
                            description=f"Container '{container_name}' adds dangerous capability: {cap}",
                            level=SecurityLevel.HIGH,
                            category="privilege-escalation",
                            resource_name=resource_name,
                            resource_kind=resource_kind,
                            fix_recommendation=f"Remove capability {cap} or use a more specific capability"
                        ))
                
                # Check for host network/PID/IPC
                pod_spec = self._get_pod_spec(resource)
                if pod_spec.get("hostNetwork", False):
                    findings.append(SecurityFinding(
                        finding_id="host-network",
                        title="Host Network Access",
                        description="Pod uses host network namespace",
                        level=SecurityLevel.HIGH,
                        category="privilege-escalation",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Disable hostNetwork unless absolutely necessary"
                    ))
                
                if pod_spec.get("hostPID", False):
                    findings.append(SecurityFinding(
                        finding_id="host-pid",
                        title="Host PID Access",
                        description="Pod uses host PID namespace",
                        level=SecurityLevel.HIGH,
                        category="privilege-escalation",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Disable hostPID unless absolutely necessary"
                    ))
        
        return findings
    
    def _analyze_rbac(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze RBAC configurations for security issues."""
        findings = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        if resource_kind in ["Role", "ClusterRole"]:
            rules = resource.get("rules", [])
            
            for rule in rules:
                verbs = rule.get("verbs", [])
                resources = rule.get("resources", [])
                
                # Check for overly broad permissions
                if "*" in verbs and "*" in resources:
                    findings.append(SecurityFinding(
                        finding_id="rbac-wildcard",
                        title="Overly Broad RBAC Permissions",
                        description="Role grants wildcard permissions on all resources",
                        level=SecurityLevel.CRITICAL,
                        category="rbac",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Limit permissions to specific resources and verbs"
                    ))
                
                # Check for dangerous verbs
                dangerous_verbs = ["create", "delete", "deletecollection", "*"]
                if any(verb in dangerous_verbs for verb in verbs) and "secrets" in resources:
                    findings.append(SecurityFinding(
                        finding_id="rbac-secret-access",
                        title="Dangerous Secret Access",
                        description="Role allows dangerous operations on secrets",
                        level=SecurityLevel.HIGH,
                        category="rbac",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Limit secret access to read-only when possible"
                    ))
        
        elif resource_kind in ["RoleBinding", "ClusterRoleBinding"]:
            role_ref = resource.get("roleRef", {})
            
            # Check for cluster-admin binding
            if role_ref.get("name") == "cluster-admin":
                findings.append(SecurityFinding(
                    finding_id="cluster-admin-binding",
                    title="Cluster Admin Binding",
                    description="Binding grants cluster-admin privileges",
                    level=SecurityLevel.CRITICAL,
                    category="rbac",
                    resource_name=resource_name,
                    resource_kind=resource_kind,
                    fix_recommendation="Use more specific roles instead of cluster-admin"
                ))
        
        return findings
    
    def _analyze_secrets(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze secrets for security issues."""
        findings = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Check for hardcoded secrets
        data = resource.get("data", {})
        string_data = resource.get("stringData", {})
        
        for key, value in {**data, **string_data}.items():
            # Check for suspicious patterns
            if self._is_suspicious_secret(key, value):
                findings.append(SecurityFinding(
                    finding_id="suspicious-secret",
                    title="Suspicious Secret Content",
                    description=f"Secret key '{key}' contains suspicious content",
                    level=SecurityLevel.MEDIUM,
                    category="secrets",
                    resource_name=resource_name,
                    resource_kind=resource_kind,
                    fix_recommendation="Review secret content and consider using external secret management"
                ))
        
        # Check for weak passwords (if base64 decodable)
        for key, value in data.items():
            try:
                decoded = base64.b64decode(value).decode('utf-8')
                if self._is_weak_password(decoded):
                    findings.append(SecurityFinding(
                        finding_id="weak-password",
                        title="Weak Password in Secret",
                        description=f"Secret key '{key}' contains a weak password",
                        level=SecurityLevel.HIGH,
                        category="secrets",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Use strong, randomly generated passwords"
                    ))
            except:
                pass  # Not a valid base64 string
        
        return findings
    
    def _analyze_network_security(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze network security configurations."""
        findings = []
        resource_name = resource.get("metadata", {}).get("name", "unknown")
        resource_kind = resource.get("kind", "unknown")
        
        # Check for services with insecure configurations
        if resource_kind == "Service":
            spec = resource.get("spec", {})
            service_type = spec.get("type", "ClusterIP")
            
            # Check for LoadBalancer services without proper security
            if service_type == "LoadBalancer":
                load_balancer_source_ranges = spec.get("loadBalancerSourceRanges")
                if not load_balancer_source_ranges:
                    findings.append(SecurityFinding(
                        finding_id="open-loadbalancer",
                        title="Unrestricted LoadBalancer Service",
                        description="LoadBalancer service allows access from any IP",
                        level=SecurityLevel.HIGH,
                        category="network",
                        resource_name=resource_name,
                        resource_kind=resource_kind,
                        fix_recommendation="Restrict access using loadBalancerSourceRanges"
                    ))
            
            # Check for NodePort services
            if service_type == "NodePort":
                findings.append(SecurityFinding(
                    finding_id="nodeport-service",
                    title="NodePort Service Exposure",
                    description="NodePort services expose ports on all cluster nodes",
                    level=SecurityLevel.MEDIUM,
                    category="network",
                    resource_name=resource_name,
                    resource_kind=resource_kind,
                    fix_recommendation="Consider using ClusterIP with Ingress instead"
                ))
        
        return findings
    
    def _check_policy_violations(self, resource: Dict[str, Any]) -> List[SecurityFinding]:
        """Check for security policy violations."""
        findings = []
        
        # This would integrate with security policies like Pod Security Standards
        # For now, basic checks
        
        return findings
    
    def _analyze_cross_resource_security(self, resources: List[Dict[str, Any]]) -> List[SecurityFinding]:
        """Analyze security across multiple resources."""
        findings = []
        
        # Check for missing NetworkPolicies
        namespaces = {r.get("metadata", {}).get("namespace", "default") for r in resources if r.get("metadata", {}).get("namespace")}
        network_policies = [r for r in resources if r.get("kind") == "NetworkPolicy"]
        
        for namespace in namespaces:
            namespace_has_policy = any(
                np.get("metadata", {}).get("namespace") == namespace 
                for np in network_policies
            )
            
            if not namespace_has_policy:
                findings.append(SecurityFinding(
                    finding_id="missing-network-policy",
                    title="Missing Network Policy",
                    description=f"Namespace '{namespace}' has no network policies",
                    level=SecurityLevel.MEDIUM,
                    category="network",
                    resource_name=namespace,
                    resource_kind="Namespace",
                    fix_recommendation="Add NetworkPolicy to control traffic flow"
                ))
        
        return findings
    
    def _load_security_data(self) -> None:
        """Load security databases and benchmarks."""
        # In a real implementation, this would load from external sources
        
        # Example vulnerability data
        self._vulnerability_db["nginx:1.15"] = [
            ImageVulnerability(
                cve_id="CVE-2019-20372",
                severity=SecurityLevel.HIGH,
                package="nginx",
                version="1.15",
                fixed_version="1.16.1",
                description="Buffer overflow in nginx"
            )
        ]
        
        # Example malicious images
        self._known_malicious_images.add("malicious/backdoor:latest")
    
    def _get_containers(self, resource: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get containers from a resource."""
        containers = []
        pod_spec = self._get_pod_spec(resource)
        
        containers.extend(pod_spec.get("containers", []))
        containers.extend(pod_spec.get("initContainers", []))
        
        return containers
    
    def _get_pod_spec(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        """Get pod spec from a resource."""
        if resource.get("kind") == "CronJob":
            return resource.get("spec", {}).get("jobTemplate", {}).get("spec", {}).get("template", {}).get("spec", {})
        else:
            return resource.get("spec", {}).get("template", {}).get("spec", {})
    
    def _is_suspicious_secret(self, key: str, value: str) -> bool:
        """Check if secret content is suspicious."""
        suspicious_patterns = [
            r"password.*123",
            r"admin.*admin", 
            r"root.*root",
            r"test.*test"
        ]
        
        key_lower = key.lower()
        value_lower = value.lower()
        
        return any(re.search(pattern, f"{key_lower}:{value_lower}") for pattern in suspicious_patterns)
    
    def _is_weak_password(self, password: str) -> bool:
        """Check if password is weak."""
        if len(password) < 8:
            return True
        
        weak_passwords = ["password", "123456", "admin", "root", "test"]
        return password.lower() in weak_passwords 