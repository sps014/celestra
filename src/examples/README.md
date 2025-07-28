# K8s-Gen DSL Examples

This directory contains comprehensive examples demonstrating the features and capabilities of the K8s-Gen Domain-Specific Language.

## Examples Overview

### 🔗 [multiple_ports_showcase.py](./multiple_ports_showcase.py)
**Multiple Ports Configuration**
- Demonstrates multi-port support across all components (App, StatefulApp, Job, CronJob, Service)
- Shows different port types (HTTP, HTTPS, metrics, admin, gRPC, debug)
- Includes comprehensive port mapping and service configuration

### 🏢 [enterprise_validation_demo.py](./enterprise_validation_demo.py)
**Enterprise Security & Validation**
- Enterprise-grade security configurations
- Validation and compliance features
- Security scanning and policy enforcement
- Cost estimation and optimization
- Production-ready governance patterns

### 🚀 [complete_platform_demo.py](./complete_platform_demo.py)
**Complete Cloud-Native Platform**
- Full microservices architecture
- Observability and monitoring stack
- Advanced deployment strategies
- External service integrations
- Dependency management
- Multi-format output generation

### ⚙️ [advanced_application_demo.py](./advanced_application_demo.py)
**Advanced Application Patterns**
- Sidecar containers and companions
- Init containers and lifecycle hooks
- Health checks and probes
- Scaling configurations
- Complex networking patterns

### 🔐 [rbac_security_demo.py](./rbac_security_demo.py)
**RBAC Security Configuration**
- Role-Based Access Control (RBAC)
- ServiceAccounts, Roles, and RoleBindings
- ClusterRoles and ClusterRoleBindings
- Security policies and best practices
- Multi-tenant access control

### 📄 [kubernetes_yaml_generation_example.py](./kubernetes_yaml_generation_example.py)
**YAML Generation & Validation**
- Real Kubernetes YAML generation
- Multiple component port verification
- Actual file output and validation
- Production-ready manifest examples

## Running Examples

### From the examples directory:
```bash
cd src/examples
python multiple_ports_showcase.py
python enterprise_validation_demo.py
python complete_platform_demo.py
python advanced_application_demo.py
python rbac_security_demo.py
python kubernetes_yaml_generation_example.py
```

### From the project root:
```bash
python -m src.examples.multiple_ports_showcase
python -m src.examples.enterprise_validation_demo
python -m src.examples.complete_platform_demo
python -m src.examples.advanced_application_demo
python -m src.examples.rbac_security_demo
python -m src.examples.kubernetes_yaml_generation_example
```

### As Python modules:
```python
from src.examples import multiple_ports_showcase
from src.examples import enterprise_validation_demo
# etc.
```

## Generated Output

Each example generates Kubernetes manifests in the `kubernetes_manifests/` directory:
- **YAML files**: Standard Kubernetes resources
- **Helm charts**: For templated deployments
- **Docker Compose**: For local development
- **Validation reports**: Security and compliance checks

## Key Learning Areas

1. **Basic DSL Usage**: Start with `multiple_ports_showcase.py`
2. **Security Patterns**: Review `rbac_security_demo.py`
3. **Production Deployment**: Study `enterprise_validation_demo.py`
4. **Complete Systems**: Explore `complete_platform_demo.py`
5. **Advanced Features**: Learn from `advanced_application_demo.py`
6. **Real Output**: Validate with `kubernetes_yaml_generation_example.py`

## Prerequisites

Ensure the K8s-Gen DSL is properly installed:
```bash
# From project root
pip install -e .
```

Or ensure the src directory is in your Python path when running examples. 