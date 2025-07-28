#!/usr/bin/env python3
"""
Enterprise Validation and Security Demo for Celestra.

This comprehensive example demonstrates enterprise-grade security, validation,
and compliance features suitable for production environments.
"""

from ..celestra import (
    App, StatefulApp, Job, CronJob, Service, Ingress, 
    Secret, ConfigMap, ServiceAccount, Role, ClusterRole, 
    RoleBinding, ClusterRoleBinding, SecurityPolicy, NetworkPolicy,
    Validator, SecurityScanner, CostEstimator,
    KubernetesOutput, HelmOutput, Observability
)


def create_enterprise_platform():
    """Create a comprehensive enterprise platform for validation."""
    print("🏗️ Creating Enterprise Platform Components...")
    
    # Core application services
    auth_service = (App("auth-service")
        .image("auth-server:2.1.3")  # Specific version
        .port(8080)
        .env("JWT_SECRET", "$(SECRET_VALUE)")
        .env("LOG_LEVEL", "INFO")
        .resources(cpu="500m", memory="1Gi")
        .replicas(3)
)
    
    # User management service with issues for testing
    user_service = (App("user-service")
        .image("user-mgmt:latest")  # Latest tag (validation issue)
        .port(9090)
        .env("DATABASE_PASSWORD", "admin123")  # Weak password (security issue)
        .env("debug", "true")  # Lowercase env var (validation issue)
        .resources(cpu="2", memory="4Gi")  # High resources (cost issue)
        .replicas(5))  # Many replicas (cost issue)
    
    # Database with security concerns
    postgres_db = (StatefulApp("postgres-database")
        .image("postgres:14")
        .port(5432)
        .env("POSTGRES_USER", "root")  # Root user (security issue)
        .env("POSTGRES_PASSWORD", "password123")  # Weak password
        .storage("/var/lib/postgresql/data", "500Gi", "fast-ssd")  # Expensive storage
        .resources(cpu="4", memory="16Gi")  # High resources
        .backup_schedule("0 2 * * *"))
    
    # Redis cache
    redis_cache = (StatefulApp("redis-cache")
        .image("redis:7.0.5")
        .port(6379)
        .storage("/data", "100Gi")
        .resources(cpu="1", memory="2Gi")
        .replicas(3))
    
    # Load balancer service (network cost)
    lb_service = (Service("external-lb")
        .selector({"app": "auth-service"})
        .add_port("https", 443, 8080)
        .type("LoadBalancer"))
    
    # Secrets with vulnerabilities
    database_secret = (Secret("database-credentials")
        .add("username", "admin")  # Admin username (security issue)
        .add("password", "password123")  # Weak password
        .add("root_password", "root")  # Root password (critical security issue)
        .add("api_key", "test123"))  # Test API key (security issue)
    
    # Configuration
    app_config = (ConfigMap("application-config")
        .add("database_host", "postgres-database")
        .add("redis_host", "redis-cache")
        .add("log_level", "DEBUG")  # Debug in production (validation issue)
        .add("enable_debug", "true"))  # Debug enabled (security issue)
    
    # RBAC with overly broad permissions
    admin_role = (Role("admin-role")
        .allow_all("*")  # Wildcard permissions (security issue)
        .allow_create("secrets")  # Dangerous secret access
        .allow_delete("pods", "services"))
    
    service_account = ServiceAccount("app-service-account")
    
    admin_binding = (RoleBinding("admin-role-binding")
        .bind_role("admin-role")
        .to_service_account("app-service-account"))
    
    return [
        auth_service, user_service, postgres_db, redis_cache,
        lb_service, database_secret, app_config,
        admin_role, service_account, admin_binding
    ]


def demonstrate_advanced_validation():
    """Demonstrate advanced validation capabilities."""
    print("\n🔍 ADVANCED VALIDATION ENGINE")
    print("=" * 50)
    
    # Create comprehensive validator
    validator = (Validator()
        .enable_schema_validation()
        .enable_best_practices()
        .enable_policy_validation()
        .enable_strict_mode()
        .enable_category("security")
        .enable_category("performance")
        .enable_category("compliance"))
    
    # Add custom enterprise validation rules
    def check_image_registry_compliance(resource):
        """Ensure images come from approved registries."""
        issues = []
        approved_registries = ["company.registry.com/", "gcr.io/company/", "docker.io/library/"]
        
        if resource.get("kind") in ["Deployment", "StatefulSet"]:
            containers = []
            pod_spec = resource.get("spec", {}).get("template", {}).get("spec", {})
            containers.extend(pod_spec.get("containers", []))
            
            for container in containers:
                image = container.get("image", "")
                if not any(image.startswith(registry) for registry in approved_registries):
                    issues.append(f"Image '{image}' not from approved registry")
        
        return issues
    
    def check_resource_limits_compliance(resource):
        """Ensure all containers have appropriate resource limits."""
        issues = []
        if resource.get("kind") in ["Deployment", "StatefulSet"]:
            containers = []
            pod_spec = resource.get("spec", {}).get("template", {}).get("spec", {})
            containers.extend(pod_spec.get("containers", []))
            
            for container in containers:
                resources = container.get("resources", {})
                limits = resources.get("limits", {})
                requests = resources.get("requests", {})
                
                if not limits.get("cpu"):
                    issues.append(f"Container '{container['name']}' missing CPU limit")
                if not limits.get("memory"):
                    issues.append(f"Container '{container['name']}' missing memory limit")
                if not requests.get("cpu"):
                    issues.append(f"Container '{container['name']}' missing CPU request")
                if not requests.get("memory"):
                    issues.append(f"Container '{container['name']}' missing memory request")
        
        return issues
    
    # Add custom rules
    validator.add_custom_rule(
        "image-registry-compliance",
        ValidationLevel.ERROR,
        check_image_registry_compliance,
        "Images must come from approved corporate registries",
        ["compliance", "security"]
    )
    
    validator.add_custom_rule(
        "resource-limits-compliance",
        ValidationLevel.WARNING,
        check_resource_limits_compliance,
        "All containers must have resource limits and requests",
        ["compliance", "performance"]
    )
    
    # Get platform resources
    platform_resources = create_enterprise_platform()
    k8s_resources = []
    
    for resource in platform_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Run comprehensive validation
    validation_results = validator.validate_resources(k8s_resources)
    
    # Analyze results by category
    total_issues = len(validation_results)
    critical_issues = validator.get_issues_by_level(validation_results, ValidationLevel.CRITICAL)
    error_issues = validator.get_issues_by_level(validation_results, ValidationLevel.ERROR)
    warning_issues = validator.get_issues_by_level(validation_results, ValidationLevel.WARNING)
    
    compliance_issues = validator.get_issues_by_category(validation_results, "compliance")
    security_issues = validator.get_issues_by_category(validation_results, "security")
    performance_issues = validator.get_issues_by_category(validation_results, "performance")
    
    print(f"📊 Validation Results:")
    print(f"  Total Issues: {total_issues}")
    print(f"  Critical: {len(critical_issues)}")
    print(f"  Errors: {len(error_issues)}")
    print(f"  Warnings: {len(warning_issues)}")
    print(f"")
    print(f"📋 Issues by Category:")
    print(f"  Compliance: {len(compliance_issues)}")
    print(f"  Security: {len(security_issues)}")
    print(f"  Performance: {len(performance_issues)}")
    
    # Show critical issues
    if critical_issues:
        print(f"\n🔴 CRITICAL ISSUES:")
        for issue in critical_issues[:5]:  # Show first 5
            print(f"  • {issue.resource_kind}/{issue.resource_name}: {issue.message}")
    
    # Generate compliance report
    report = validator.generate_report(validation_results)
    print(f"\n📄 Generated comprehensive validation report ({len(report)} characters)")
    
    return {
        "total_issues": total_issues,
        "critical": len(critical_issues),
        "errors": len(error_issues),
        "warnings": len(warning_issues),
        "compliance": len(compliance_issues),
        "security": len(security_issues),
        "performance": len(performance_issues)
    }


def demonstrate_enterprise_security_scanning():
    """Demonstrate enterprise security scanning."""
    print("\n🛡️ ENTERPRISE SECURITY SCANNING")
    print("=" * 50)
    
    # Create comprehensive security scanner
    scanner = (SecurityScanner()
        .enable_image_scanning()
        .enable_rbac_analysis()
        .enable_privilege_escalation_detection()
        .enable_network_analysis()
        .enable_secret_analysis()
        .enable_policy_violations())
    
    # Get platform resources
    platform_resources = create_enterprise_platform()
    k8s_resources = []
    
    for resource in platform_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Add cluster-admin binding for testing
    cluster_admin_binding = {
        "apiVersion": "rbac.authorization.k8s.io/v1",
        "kind": "ClusterRoleBinding",
        "metadata": {"name": "dangerous-cluster-admin"},
        "roleRef": {
            "apiGroup": "rbac.authorization.k8s.io",
            "kind": "ClusterRole",
            "name": "cluster-admin"
        },
        "subjects": [
            {
                "kind": "ServiceAccount",
                "name": "app-service-account",
                "namespace": "default"
            }
        ]
    }
    k8s_resources.append(cluster_admin_binding)
    
    # Run security scan
    security_findings = scanner.scan_resources(k8s_resources)
    
    # Analyze findings by severity
    total_findings = len(security_findings)
    critical_findings = scanner.get_findings_by_level(security_findings, SecurityLevel.CRITICAL)
    high_findings = scanner.get_findings_by_level(security_findings, SecurityLevel.HIGH)
    medium_findings = scanner.get_findings_by_level(security_findings, SecurityLevel.MEDIUM)
    low_findings = scanner.get_findings_by_level(security_findings, SecurityLevel.LOW)
    
    # Analyze by category
    image_findings = scanner.get_findings_by_category(security_findings, "image-security")
    rbac_findings = scanner.get_findings_by_category(security_findings, "rbac")
    secret_findings = scanner.get_findings_by_category(security_findings, "secrets")
    network_findings = scanner.get_findings_by_category(security_findings, "network")
    privilege_findings = scanner.get_findings_by_category(security_findings, "privilege-escalation")
    
    print(f"🔒 Security Scan Results:")
    print(f"  Total Findings: {total_findings}")
    print(f"  Critical: {len(critical_findings)}")
    print(f"  High: {len(high_findings)}")
    print(f"  Medium: {len(medium_findings)}")
    print(f"  Low: {len(low_findings)}")
    print(f"")
    print(f"📋 Findings by Category:")
    print(f"  Image Security: {len(image_findings)}")
    print(f"  RBAC Issues: {len(rbac_findings)}")
    print(f"  Secret Issues: {len(secret_findings)}")
    print(f"  Network Issues: {len(network_findings)}")
    print(f"  Privilege Escalation: {len(privilege_findings)}")
    
    # Show critical findings
    if critical_findings:
        print(f"\n🚨 CRITICAL SECURITY FINDINGS:")
        for finding in critical_findings[:5]:  # Show first 5
            print(f"  • {finding.title}")
            print(f"    Resource: {finding.resource_kind}/{finding.resource_name}")
            print(f"    Issue: {finding.description}")
            if finding.fix_recommendation:
                print(f"    Fix: {finding.fix_recommendation}")
            print()
    
    # Generate security report
    security_report = scanner.generate_security_report(security_findings)
    print(f"🔒 Generated comprehensive security report ({len(security_report)} characters)")
    
    return {
        "total_findings": total_findings,
        "critical": len(critical_findings),
        "high": len(high_findings),
        "medium": len(medium_findings),
        "low": len(low_findings),
        "image_issues": len(image_findings),
        "rbac_issues": len(rbac_findings),
        "secret_issues": len(secret_findings)
    }


def demonstrate_multi_cloud_cost_analysis():
    """Demonstrate multi-cloud cost analysis."""
    print("\n💰 MULTI-CLOUD COST ANALYSIS")
    print("=" * 50)
    
    # Get platform resources
    platform_resources = create_enterprise_platform()
    k8s_resources = []
    
    for resource in platform_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Test cost estimation across multiple cloud providers
    cloud_costs = {}
    
    for provider in [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]:
        print(f"  ☁️ Analyzing {provider.value.upper()} costs...")
        
        # Create cost estimator
        estimator = (CostEstimator(provider, "us-west-2")
            .enable_spot_instances(0.7)
            .set_target_utilization(0.8))
        
        # Set provider-specific pricing if needed
        if provider == CloudProvider.AWS:
            estimator.set_compute_pricing(0.0464, 0.00696, 0.90)
            estimator.set_storage_pricing(0.10, 0.045)
            estimator.set_network_pricing(0.09, 0.025)
        
        # Estimate costs
        resource_costs = estimator.estimate_resources(k8s_resources)
        total_cost = estimator.calculate_total_cost(resource_costs)
        
        cloud_costs[provider.value] = {
            "monthly": total_cost.total_cost,
            "annual": total_cost.total_cost * 12,
            "compute": total_cost.compute_cost,
            "storage": total_cost.storage_cost,
            "network": total_cost.network_cost,
            "resources": len(resource_costs)
        }
        
        print(f"    Monthly Cost: ${total_cost.total_cost:.2f}")
        print(f"    Annual Cost: ${total_cost.total_cost * 12:.2f}")
    
    # Find most cost-effective provider
    cheapest_provider = min(cloud_costs.keys(), key=lambda p: cloud_costs[p]["monthly"])
    most_expensive = max(cloud_costs.keys(), key=lambda p: cloud_costs[p]["monthly"])
    
    savings = cloud_costs[most_expensive]["monthly"] - cloud_costs[cheapest_provider]["monthly"]
    savings_percent = (savings / cloud_costs[most_expensive]["monthly"]) * 100
    
    print(f"\n💡 Cost Optimization Insights:")
    print(f"  Cheapest Provider: {cheapest_provider.upper()} (${cloud_costs[cheapest_provider]['monthly']:.2f}/month)")
    print(f"  Most Expensive: {most_expensive.upper()} (${cloud_costs[most_expensive]['monthly']:.2f}/month)")
    print(f"  Potential Savings: ${savings:.2f}/month ({savings_percent:.1f}%)")
    print(f"  Annual Savings: ${savings * 12:.2f}")
    
    # Generate detailed cost report for cheapest provider
    best_estimator = CostEstimator(CloudProvider(cheapest_provider), "us-west-2")
    best_costs = best_estimator.estimate_resources(k8s_resources)
    cost_report = best_estimator.generate_cost_report(best_costs)
    
    print(f"\n📊 Generated detailed cost report for {cheapest_provider.upper()} ({len(cost_report)} characters)")
    
    return {
        "providers_analyzed": len(cloud_costs),
        "cheapest_provider": cheapest_provider,
        "monthly_savings": savings,
        "annual_savings": savings * 12,
        "savings_percent": savings_percent,
        "total_resources": cloud_costs[cheapest_provider]["resources"]
    }


def demonstrate_integrated_governance():
    """Demonstrate integrated governance and compliance."""
    print("\n🏛️ INTEGRATED GOVERNANCE & COMPLIANCE")
    print("=" * 50)
    
    # Get platform resources
    platform_resources = create_enterprise_platform()
    k8s_resources = []
    
    for resource in platform_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Initialize all analyzers
    validator = (Validator()
        .enable_schema_validation()
        .enable_best_practices()
        .enable_strict_mode())
    
    scanner = (SecurityScanner()
        .enable_image_scanning()
        .enable_rbac_analysis()
        .enable_secret_analysis()
        .enable_privilege_escalation_detection())
    
    estimator = (CostEstimator(CloudProvider.AWS, "us-west-2")
        .enable_spot_instances())
    
    # Run all analyses
    validation_results = validator.validate_resources(k8s_resources)
    security_findings = scanner.scan_resources(k8s_resources)
    cost_estimates = estimator.estimate_resources(k8s_resources)
    
    # Calculate governance score
    critical_validation = len(validator.get_issues_by_level(validation_results, ValidationLevel.CRITICAL))
    critical_security = len(scanner.get_findings_by_level(security_findings, SecurityLevel.CRITICAL))
    high_security = len(scanner.get_findings_by_level(security_findings, SecurityLevel.HIGH))
    total_monthly_cost = estimator.calculate_total_cost(cost_estimates).total_cost
    
    # Governance scoring
    governance_score = 100
    
    # Deduct points for issues
    governance_score -= critical_validation * 20  # Critical validation issues
    governance_score -= critical_security * 25    # Critical security issues
    governance_score -= high_security * 10        # High security issues
    governance_score -= min(20, max(0, (len(validation_results) - 10) * 2))  # Too many validation issues
    
    # Cost factor
    if total_monthly_cost > 2000:
        governance_score -= 10  # High cost penalty
    elif total_monthly_cost > 1000:
        governance_score -= 5   # Medium cost penalty
    
    governance_score = max(0, governance_score)
    
    # Compliance level
    if governance_score >= 90:
        compliance_level = "EXCELLENT"
        compliance_color = "🟢"
    elif governance_score >= 80:
        compliance_level = "GOOD"
        compliance_color = "🟡"
    elif governance_score >= 70:
        compliance_level = "ACCEPTABLE"
        compliance_color = "🟠"
    else:
        compliance_level = "POOR"
        compliance_color = "🔴"
    
    print(f"📊 Governance Dashboard:")
    print(f"  Overall Score: {governance_score}/100 {compliance_color}")
    print(f"  Compliance Level: {compliance_level}")
    print(f"  Validation Issues: {len(validation_results)} (Critical: {critical_validation})")
    print(f"  Security Findings: {len(security_findings)} (Critical: {critical_security})")
    print(f"  Monthly Cost: ${total_monthly_cost:.2f}")
    print(f"  Resources Analyzed: {len(k8s_resources)}")
    
    # Generate recommendations
    recommendations = []
    
    if critical_validation > 0:
        recommendations.append("🔴 URGENT: Fix critical validation issues")
    if critical_security > 0:
        recommendations.append("🛡️ CRITICAL: Address security vulnerabilities immediately")
    if high_security > 2:
        recommendations.append("⚠️ HIGH: Review high-severity security findings")
    if total_monthly_cost > 1500:
        recommendations.append("💰 COST: Implement cost optimization strategies")
    if len(validation_results) > 20:
        recommendations.append("📋 QUALITY: Improve code quality to reduce validation issues")
    
    if not recommendations:
        recommendations.append("✅ Platform meets enterprise governance standards")
    
    print(f"\n💡 Governance Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    # Risk assessment
    risk_factors = []
    if critical_security > 0:
        risk_factors.append("Critical security vulnerabilities")
    if critical_validation > 0:
        risk_factors.append("Critical validation failures")
    if total_monthly_cost > 2000:
        risk_factors.append("High operational costs")
    
    risk_level = "HIGH" if len(risk_factors) >= 2 else "MEDIUM" if len(risk_factors) == 1 else "LOW"
    
    print(f"\n⚠️ Risk Assessment: {risk_level}")
    if risk_factors:
        print(f"  Risk Factors:")
        for factor in risk_factors:
            print(f"    • {factor}")
    
    return {
        "governance_score": governance_score,
        "compliance_level": compliance_level,
        "validation_issues": len(validation_results),
        "security_findings": len(security_findings),
        "monthly_cost": total_monthly_cost,
        "risk_level": risk_level,
        "recommendations": len(recommendations)
    }


def main():
    """Run enterprise validation and tools demonstration."""
    print("🏢 Celestra Enterprise Validation & Tools Demo")
    print("=" * 60)
    print("🎯 Showcasing Phase 9: Governance, Compliance & Cost Optimization")
    print("=" * 60)
    
    try:
        # Create enterprise platform
        platform_components = create_enterprise_platform()
        print(f"  ✅ Created {len(platform_components)} enterprise components")
        
        # Advanced Validation
        validation_stats = demonstrate_advanced_validation()
        
        # Security Scanning
        security_stats = demonstrate_enterprise_security_scanning()
        
        # Cost Analysis
        cost_stats = demonstrate_multi_cloud_cost_analysis()
        
        # Integrated Governance
        governance_stats = demonstrate_integrated_governance()
        
        # Final Enterprise Summary
        print("\n🎯 ENTERPRISE PLATFORM SUMMARY")
        print("=" * 60)
        
        print(f"✅ Platform successfully analyzed with enterprise-grade tools!")
        
        print(f"\n📊 VALIDATION & COMPLIANCE:")
        print(f"  🔍 Total Issues: {validation_stats['total_issues']}")
        print(f"  🔴 Critical: {validation_stats['critical']}")
        print(f"  ⚖️ Compliance Issues: {validation_stats['compliance']}")
        print(f"  🛡️ Security Issues: {validation_stats['security']}")
        print(f"  ⚡ Performance Issues: {validation_stats['performance']}")
        
        print(f"\n🔒 SECURITY POSTURE:")
        print(f"  🔍 Total Findings: {security_stats['total_findings']}")
        print(f"  🚨 Critical: {security_stats['critical']}")
        print(f"  🔴 High: {security_stats['high']}")
        print(f"  📦 Image Issues: {security_stats['image_issues']}")
        print(f"  🔐 RBAC Issues: {security_stats['rbac_issues']}")
        print(f"  🔑 Secret Issues: {security_stats['secret_issues']}")
        
        print(f"\n💰 COST OPTIMIZATION:")
        print(f"  ☁️ Providers Analyzed: {cost_stats['providers_analyzed']}")
        print(f"  🏆 Best Provider: {cost_stats['cheapest_provider'].upper()}")
        print(f"  💵 Monthly Savings: ${cost_stats['monthly_savings']:.2f}")
        print(f"  📅 Annual Savings: ${cost_stats['annual_savings']:.2f}")
        print(f"  📈 Savings Percentage: {cost_stats['savings_percent']:.1f}%")
        
        print(f"\n🏛️ GOVERNANCE:")
        print(f"  📊 Overall Score: {governance_stats['governance_score']}/100")
        print(f"  ⚖️ Compliance Level: {governance_stats['compliance_level']}")
        print(f"  ⚠️ Risk Level: {governance_stats['risk_level']}")
        print(f"  💡 Recommendations: {governance_stats['recommendations']}")
        
        print(f"\n🌟 ENTERPRISE CAPABILITIES DEMONSTRATED:")
        print(f"  ✅ Advanced Schema & Policy Validation")
        print(f"  ✅ Custom Compliance Rules & Categories")
        print(f"  ✅ Comprehensive Security Vulnerability Scanning")
        print(f"  ✅ Multi-Cloud Cost Analysis & Optimization")
        print(f"  ✅ Integrated Governance & Risk Assessment")
        print(f"  ✅ Enterprise-Grade Reporting & Recommendations")
        print(f"  ✅ Complete Compliance & Audit Trail")
        
        print(f"\n🏢 Celestra: Enterprise-Ready Kubernetes Platform!")
        print("    With complete governance, security, and cost optimization!")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 