#!/usr/bin/env python3
"""
Test script for K8s-Gen DSL Phase 9 (Validation & Tools).

This script demonstrates the advanced validation, security scanning, and cost
estimation capabilities implemented in Phase 9.
"""

from src.k8s_gen import (
    # Core components for testing
    App, StatefulApp, Secret, ConfigMap, Service,
    
    # Phase 9: Validation & Tools  
    Validator, ValidationLevel, ValidationRule,
    SecurityScanner, SecurityLevel, SecurityFinding,
    CostEstimator, CostBreakdown, CloudProvider
)


def create_test_resources():
    """Create test resources with various configurations."""
    
    # Insecure app for testing validation
    insecure_app = (App("insecure-app")
        .image("nginx:latest")  # Latest tag (warning)
        .port(8080)
        .env("PASSWORD", "admin123")  # Insecure password
        .replicas(1))
    
    # Secure app for comparison
    secure_app = (App("secure-app")
        .image("nginx:1.21.6")  # Specific version
        .port(8080)
        .env("LOG_LEVEL", "info")
        .resources(cpu="200m", memory="256Mi")  # With limits
        .replicas(3))
    
    # Expensive workload for cost testing
    expensive_app = (App("expensive-app")
        .image("tensorflow/tensorflow:2.8.0")
        .port(8888)
        .resources(cpu="4", memory="16Gi")  # High resource usage
        .replicas(5))
    
    # Database with storage
    database = (StatefulApp("postgres-db")
        .image("postgres:14")
        .port(5432)
        .env("POSTGRES_PASSWORD", "weak123")  # Weak password for testing
        .storage("/var/lib/postgresql/data", "100Gi")  # Large storage
        .resources(cpu="2", memory="8Gi"))
    
    # Service configurations
    load_balancer_service = (Service("lb-service")
        .selector({"app": "insecure-app"})
        .add_port("http", 80, 8080)
        .type("LoadBalancer"))
    
    # Secrets with issues
    insecure_secret = (Secret("insecure-secret")
        .add("password", "password123")  # Weak password
        .add("api_key", "admin")  # Suspicious content
        .add("database_url", "postgres://root:root@db:5432/app"))  # Root credentials
    
    # Configuration
    app_config = (ConfigMap("app-config")
        .add("debug", "true")
        .add("log_level", "debug"))
    
    return [
        insecure_app, secure_app, expensive_app, database,
        load_balancer_service, insecure_secret, app_config
    ]


def test_validator():
    """Test advanced validation capabilities."""
    print("🔍 Testing Advanced Validator...")
    
    # Create validator with all features enabled
    validator = (Validator()
        .enable_schema_validation()
        .enable_best_practices()
        .enable_policy_validation()
        .enable_strict_mode())
    
    # Add custom validation rule
    def check_environment_naming(resource):
        """Check if environment variables follow naming convention."""
        issues = []
        if resource.get("kind") in ["Deployment", "StatefulSet"]:
            containers = []
            pod_spec = resource.get("spec", {}).get("template", {}).get("spec", {})
            containers.extend(pod_spec.get("containers", []))
            
            for container in containers:
                env_vars = container.get("env", [])
                for env_var in env_vars:
                    name = env_var.get("name", "")
                    if not name.isupper() or "_" not in name:
                        issues.append(f"Environment variable '{name}' should be UPPER_CASE")
        return issues
    
    validator.add_custom_rule(
        "env-naming-convention",
        ValidationLevel.INFO,
        check_environment_naming,
        "Environment variables should follow UPPER_CASE convention",
        ["best-practices", "naming"]
    )
    
    # Get test resources and convert to Kubernetes manifests
    test_resources = create_test_resources()
    k8s_resources = []
    
    for resource in test_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Run validation
    validation_results = validator.validate_resources(k8s_resources)
    
    # Analyze results
    total_issues = len(validation_results)
    critical_issues = len(validator.get_issues_by_level(validation_results, ValidationLevel.CRITICAL))
    error_issues = len(validator.get_issues_by_level(validation_results, ValidationLevel.ERROR))
    warning_issues = len(validator.get_issues_by_level(validation_results, ValidationLevel.WARNING))
    info_issues = len(validator.get_issues_by_level(validation_results, ValidationLevel.INFO))
    
    print(f"  📊 Validation Summary:")
    print(f"    Total Issues: {total_issues}")
    print(f"    Critical: {critical_issues}")
    print(f"    Errors: {error_issues}")
    print(f"    Warnings: {warning_issues}")
    print(f"    Info: {info_issues}")
    
    # Test category filtering
    security_issues = validator.get_issues_by_category(validation_results, "security")
    best_practice_issues = validator.get_issues_by_category(validation_results, "best-practices")
    
    print(f"    Security Issues: {len(security_issues)}")
    print(f"    Best Practice Issues: {len(best_practice_issues)}")
    
    # Generate and display report
    report = validator.generate_report(validation_results)
    print(f"  📋 Generated validation report ({len(report)} chars)")
    
    return {
        "total_issues": total_issues,
        "critical": critical_issues,
        "errors": error_issues,
        "warnings": warning_issues,
        "info": info_issues,
        "security_issues": len(security_issues),
        "best_practice_issues": len(best_practice_issues)
    }


def test_security_scanner():
    """Test security scanning capabilities."""
    print("🔒 Testing Security Scanner...")
    
    # Create security scanner with all features enabled
    scanner = (SecurityScanner()
        .enable_image_scanning()
        .enable_rbac_analysis()
        .enable_privilege_escalation_detection()
        .enable_network_analysis()
        .enable_secret_analysis()
        .enable_policy_violations())
    
    # Get test resources and convert to Kubernetes manifests
    test_resources = create_test_resources()
    k8s_resources = []
    
    for resource in test_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Add some RBAC resources for testing
    rbac_resources = [
        {
            "apiVersion": "rbac.authorization.k8s.io/v1",
            "kind": "ClusterRoleBinding",
            "metadata": {"name": "admin-binding"},
            "roleRef": {
                "apiGroup": "rbac.authorization.k8s.io",
                "kind": "ClusterRole",
                "name": "cluster-admin"
            },
            "subjects": [
                {
                    "kind": "User",
                    "name": "admin@company.com",
                    "apiGroup": "rbac.authorization.k8s.io"
                }
            ]
        }
    ]
    
    k8s_resources.extend(rbac_resources)
    
    # Run security scan
    security_findings = scanner.scan_resources(k8s_resources)
    
    # Analyze results by severity
    total_findings = len(security_findings)
    critical_findings = len(scanner.get_findings_by_level(security_findings, SecurityLevel.CRITICAL))
    high_findings = len(scanner.get_findings_by_level(security_findings, SecurityLevel.HIGH))
    medium_findings = len(scanner.get_findings_by_level(security_findings, SecurityLevel.MEDIUM))
    low_findings = len(scanner.get_findings_by_level(security_findings, SecurityLevel.LOW))
    
    print(f"  🔒 Security Summary:")
    print(f"    Total Findings: {total_findings}")
    print(f"    Critical: {critical_findings}")
    print(f"    High: {high_findings}")
    print(f"    Medium: {medium_findings}")
    print(f"    Low: {low_findings}")
    
    # Analyze by category
    image_findings = scanner.get_findings_by_category(security_findings, "image-security")
    rbac_findings = scanner.get_findings_by_category(security_findings, "rbac")
    secret_findings = scanner.get_findings_by_category(security_findings, "secrets")
    privilege_findings = scanner.get_findings_by_category(security_findings, "privilege-escalation")
    network_findings = scanner.get_findings_by_category(security_findings, "network")
    
    print(f"    Image Security: {len(image_findings)}")
    print(f"    RBAC Issues: {len(rbac_findings)}")
    print(f"    Secret Issues: {len(secret_findings)}")
    print(f"    Privilege Escalation: {len(privilege_findings)}")
    print(f"    Network Issues: {len(network_findings)}")
    
    # Generate security report
    security_report = scanner.generate_security_report(security_findings)
    print(f"  📋 Generated security report ({len(security_report)} chars)")
    
    return {
        "total_findings": total_findings,
        "critical": critical_findings,
        "high": high_findings,
        "medium": medium_findings,
        "low": low_findings,
        "image_issues": len(image_findings),
        "rbac_issues": len(rbac_findings),
        "secret_issues": len(secret_findings)
    }


def test_cost_estimator():
    """Test cost estimation capabilities."""
    print("💰 Testing Cost Estimator...")
    
    # Test different cloud providers
    providers_tested = []
    
    for provider in [CloudProvider.AWS, CloudProvider.GCP, CloudProvider.AZURE]:
        print(f"  ☁️ Testing {provider.value.upper()} pricing...")
        
        # Create cost estimator for provider
        estimator = (CostEstimator(provider, "us-west-2")
            .enable_spot_instances(0.7)
            .set_target_utilization(0.75))
        
        # Custom pricing for testing
        if provider == CloudProvider.AWS:
            estimator.set_compute_pricing(0.0464, 0.00696)  # t3.medium
            estimator.set_storage_pricing(0.10, 0.045)      # GP2, SC1
            estimator.set_network_pricing(0.09, 0.025)      # Data transfer, LB
        
        # Get test resources and convert to Kubernetes manifests
        test_resources = create_test_resources()
        k8s_resources = []
        
        for resource in test_resources:
            k8s_manifests = resource.generate_kubernetes_resources()
            k8s_resources.extend(k8s_manifests)
        
        # Estimate costs
        resource_costs = estimator.estimate_resources(k8s_resources)
        total_cost = estimator.calculate_total_cost(resource_costs)
        
        print(f"    📊 {provider.value.upper()} Monthly Cost: ${total_cost.total_cost:.2f}")
        print(f"      Compute: ${total_cost.compute_cost:.2f}")
        print(f"      Storage: ${total_cost.storage_cost:.2f}")
        print(f"      Network: ${total_cost.network_cost:.2f}")
        
        providers_tested.append({
            "provider": provider.value,
            "total_cost": total_cost.total_cost,
            "compute_cost": total_cost.compute_cost,
            "storage_cost": total_cost.storage_cost,
            "network_cost": total_cost.network_cost,
            "resource_count": len(resource_costs)
        })
    
    # Generate detailed report for AWS
    aws_estimator = CostEstimator(CloudProvider.AWS, "us-west-2")
    aws_costs = aws_estimator.estimate_resources(k8s_resources)
    aws_total = aws_estimator.calculate_total_cost(aws_costs)
    
    cost_report = aws_estimator.generate_cost_report(aws_costs)
    print(f"  📋 Generated cost report ({len(cost_report)} chars)")
    
    # Test cost analysis features
    cost_by_category = aws_estimator.get_cost_by_category(aws_costs)
    print(f"  📈 Cost by Category:")
    for category, cost in cost_by_category.items():
        print(f"    {category}: ${cost:.2f}")
    
    return {
        "providers_tested": len(providers_tested),
        "provider_results": providers_tested,
        "total_resources_estimated": len(aws_costs),
        "aws_monthly_cost": aws_total.total_cost,
        "cost_categories": len(cost_by_category)
    }


def test_integration_scenario():
    """Test integrated validation, security, and cost analysis."""
    print("🔄 Testing Integrated Analysis Scenario...")
    
    # Create a comprehensive platform for testing
    platform_resources = create_test_resources()
    
    # Convert to Kubernetes manifests
    k8s_resources = []
    for resource in platform_resources:
        k8s_manifests = resource.generate_kubernetes_resources()
        k8s_resources.extend(k8s_manifests)
    
    # Initialize all analyzers
    validator = (Validator()
        .enable_schema_validation()
        .enable_best_practices())
    
    scanner = (SecurityScanner()
        .enable_image_scanning()
        .enable_secret_analysis()
        .enable_privilege_escalation_detection())
    
    estimator = (CostEstimator(CloudProvider.AWS, "us-west-2")
        .enable_spot_instances())
    
    # Run all analyses
    validation_results = validator.validate_resources(k8s_resources)
    security_findings = scanner.scan_resources(k8s_resources)
    cost_estimates = estimator.estimate_resources(k8s_resources)
    
    # Combine insights
    critical_validation = len(validator.get_issues_by_level(validation_results, ValidationLevel.CRITICAL))
    critical_security = len(scanner.get_findings_by_level(security_findings, SecurityLevel.CRITICAL))
    total_monthly_cost = estimator.calculate_total_cost(cost_estimates).total_cost
    
    print(f"  📊 Integrated Analysis Results:")
    print(f"    Critical Validation Issues: {critical_validation}")
    print(f"    Critical Security Issues: {critical_security}")
    print(f"    Monthly Cost: ${total_monthly_cost:.2f}")
    print(f"    Annual Cost: ${total_monthly_cost * 12:.2f}")
    
    # Risk assessment
    risk_score = 0
    if critical_validation > 0:
        risk_score += 3
    if critical_security > 0:
        risk_score += 5
    if total_monthly_cost > 1000:
        risk_score += 2
    
    risk_level = "LOW" if risk_score <= 2 else "MEDIUM" if risk_score <= 5 else "HIGH"
    print(f"    Overall Risk Level: {risk_level}")
    
    # Generate recommendations
    recommendations = []
    if critical_validation > 0:
        recommendations.append("Address critical validation issues before deployment")
    if critical_security > 0:
        recommendations.append("Fix critical security vulnerabilities immediately")
    if total_monthly_cost > 500:
        recommendations.append("Review cost optimization opportunities")
    
    print(f"  💡 Key Recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"    {i}. {rec}")
    
    return {
        "validation_issues": len(validation_results),
        "security_findings": len(security_findings),
        "cost_estimates": len(cost_estimates),
        "monthly_cost": total_monthly_cost,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendations": len(recommendations)
    }


def test_advanced_features():
    """Test advanced features of validation and tools."""
    print("⚡ Testing Advanced Features...")
    
    # Test custom validation rules
    validator = Validator()
    
    def check_resource_naming(resource):
        """Custom rule to check resource naming conventions."""
        issues = []
        name = resource.get("metadata", {}).get("name", "")
        if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", name):
            issues.append(f"Resource name '{name}' doesn't follow kebab-case convention")
        return issues
    
    import re
    validator.add_custom_rule(
        "naming-convention",
        ValidationLevel.WARNING,
        check_resource_naming,
        "Resources should follow kebab-case naming",
        ["naming", "best-practices"]
    )
    
    # Test security scanner with custom checks
    scanner = SecurityScanner()
    
    # Test cost estimator with different scenarios
    estimator = CostEstimator(CloudProvider.AWS)
    
    # Create test resource
    test_app = App("test-app").image("nginx:1.21").port(80).replicas(2)
    k8s_resources = test_app.generate_kubernetes_resources()
    
    # Run advanced tests
    validation_results = validator.validate_resources(k8s_resources)
    security_findings = scanner.scan_resources(k8s_resources)
    cost_estimates = estimator.estimate_resources(k8s_resources)
    
    # Test filtering and analysis
    warning_validations = validator.get_issues_by_level(validation_results, ValidationLevel.WARNING)
    naming_issues = validator.get_issues_by_category(validation_results, "naming")
    
    medium_security = scanner.get_findings_by_level(security_findings, SecurityLevel.MEDIUM)
    image_security = scanner.get_findings_by_category(security_findings, "image-security")
    
    total_cost = estimator.calculate_total_cost(cost_estimates)
    cost_by_type = estimator.get_cost_by_category(cost_estimates)
    
    print(f"  🔍 Advanced Analysis:")
    print(f"    Custom Validation Rules: {len(naming_issues)} naming issues")
    print(f"    Security Analysis: {len(image_security)} image issues")
    print(f"    Cost Breakdown: {len(cost_by_type)} categories")
    print(f"    Total Features Tested: {len(warning_validations) + len(medium_security) + len(cost_estimates)}")
    
    return {
        "custom_rules_triggered": len(naming_issues),
        "security_categories": len(scanner.get_findings_by_category(security_findings, "image-security")),
        "cost_categories": len(cost_by_type),
        "total_cost": total_cost.total_cost
    }


def main():
    """Run all Phase 9 tests."""
    print("🧪 Testing K8s-Gen DSL Phase 9 (Validation & Tools)")
    print("=" * 60)
    
    try:
        # Individual component tests
        print("\n🔍 VALIDATION ENGINE")
        print("-" * 30)
        validation_stats = test_validator()
        
        print("\n🔒 SECURITY SCANNER") 
        print("-" * 30)
        security_stats = test_security_scanner()
        
        print("\n💰 COST ESTIMATOR")
        print("-" * 30)
        cost_stats = test_cost_estimator()
        
        print("\n🔄 INTEGRATION TESTS")
        print("-" * 30)
        integration_stats = test_integration_scenario()
        
        print("\n⚡ ADVANCED FEATURES")
        print("-" * 30)
        advanced_stats = test_advanced_features()
        
        # Final summary
        print("\n🎉 PHASE 9 SUMMARY")
        print("=" * 60)
        print(f"✅ All Phase 9 tests completed successfully!")
        
        print(f"\n📊 VALIDATION ENGINE:")
        print(f"  🔍 Total Issues Found: {validation_stats['total_issues']}")
        print(f"  🔴 Critical Issues: {validation_stats['critical']}")
        print(f"  🛡️ Security Issues: {validation_stats['security_issues']}")
        print(f"  📋 Best Practice Issues: {validation_stats['best_practice_issues']}")
        
        print(f"\n🔒 SECURITY SCANNER:")
        print(f"  🔍 Total Findings: {security_stats['total_findings']}")
        print(f"  🔴 Critical Findings: {security_stats['critical']}")
        print(f"  📦 Image Issues: {security_stats['image_issues']}")
        print(f"  🔐 RBAC Issues: {security_stats['rbac_issues']}")
        print(f"  🔑 Secret Issues: {security_stats['secret_issues']}")
        
        print(f"\n💰 COST ESTIMATOR:")
        print(f"  ☁️ Providers Tested: {cost_stats['providers_tested']}")
        print(f"  📊 Resources Estimated: {cost_stats['total_resources_estimated']}")
        print(f"  💵 AWS Monthly Cost: ${cost_stats['aws_monthly_cost']:.2f}")
        print(f"  📈 Cost Categories: {cost_stats['cost_categories']}")
        
        print(f"\n🔄 INTEGRATION:")
        print(f"  📋 Validation Issues: {integration_stats['validation_issues']}")
        print(f"  🔒 Security Findings: {integration_stats['security_findings']}")
        print(f"  💰 Monthly Cost: ${integration_stats['monthly_cost']:.2f}")
        print(f"  ⚠️ Risk Level: {integration_stats['risk_level']}")
        print(f"  💡 Recommendations: {integration_stats['recommendations']}")
        
        print(f"\n🔍 FEATURE HIGHLIGHTS:")
        print(f"  🔧 Advanced Validation: Schema, policies, custom rules")
        print(f"  🛡️ Security Scanning: Images, RBAC, secrets, privileges")
        print(f"  💰 Cost Estimation: Multi-cloud, optimization, reporting")
        print(f"  🔄 Integrated Analysis: Risk assessment & recommendations")
        print(f"  ⚡ Extensible Framework: Custom rules, policies, pricing")
        
        print(f"\n✨ K8s-Gen DSL: Complete Enterprise Platform!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        raise


if __name__ == "__main__":
    main() 