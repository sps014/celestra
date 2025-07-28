# Celestra Comprehensive Test Suite

This directory contains a comprehensive test suite for the Celestra, covering all components and scenarios defined in the specifications.

## Test Structure

The test suite is organized into the following modules:

### Core Components Tests
- **`test_core_components.py`** - Tests for App, StatefulApp, AppGroup, Secret, ConfigMap
- **`test_workloads.py`** - Tests for Job, CronJob, Lifecycle management
- **`test_networking.py`** - Tests for Service, Ingress, Companion, Scaling, Health, NetworkPolicy
- **`test_security.py`** - Tests for RBAC, ServiceAccount, Role, SecurityPolicy

### Advanced Features Tests
- **`test_observability.py`** - Tests for monitoring, alerting, tracing, deployment strategies
- **`test_advanced_features.py`** - Tests for Dependencies, CustomResource, CostOptimization
- **`test_output_formats.py`** - Tests for YAML, Helm, Docker Compose, Terraform generation
- **`test_plugins.py`** - Tests for plugin system and template management

### Validation and Quality Tests
- **`test_validation.py`** - Tests for validation, security scanning, cost estimation
- **`test_integration.py`** - End-to-end integration tests
- **`test_examples.py`** - Real-world example scenarios

### Test Utilities
- **`utils.py`** - Test helper functions, mock classes, and assertion utilities
- **`test_run_all.py`** - Comprehensive test runner with reporting
- **`__init__.py`** - Test package initialization and configuration

## Running Tests

### Run All Tests
```bash
# Run the complete test suite
python src/test/test_run_all.py

# Run with verbose output
python src/test/test_run_all.py --verbose

# Run with fail-fast (stop on first failure)
python src/test/test_run_all.py --fail-fast

# Generate JSON report
python src/test/test_run_all.py --report test_report.json
```

### Run Specific Test Modules
```bash
# Run specific modules
python src/test/test_run_all.py --modules test_core_components test_networking

# List available modules
python src/test/test_run_all.py --list
```

### Run Individual Test Files
```bash
# Using pytest directly
pytest src/test/test_core_components.py -v
pytest src/test/test_integration.py -v

# Run specific test class
pytest src/test/test_core_components.py::TestApp -v

# Run specific test method
pytest src/test/test_core_components.py::TestApp::test_basic_app_creation -v
```

## Test Categories

### 1. Unit Tests
Individual component testing with mocked dependencies:
- Component creation and configuration
- Method chaining and fluent API
- Parameter validation
- Resource generation

### 2. Integration Tests
End-to-end scenarios testing component interactions:
- Multi-service applications
- Complex dependency chains
- Enterprise application deployments
- Multi-environment configurations

### 3. Output Format Tests
Verification of generated output formats:
- Kubernetes YAML validation
- Docker Compose generation
- Helm Chart structure
- Terraform module creation
- Kustomize overlay generation

### 4. Real-World Examples
Complete application scenarios:
- WordPress deployment
- Machine Learning pipeline
- E-commerce microservices platform
- CI/CD pipeline deployment

## Test Utilities

### TestHelper
Provides utility functions for test operations:
```python
helper = TestHelper("test_name")
temp_dir = helper.create_temp_dir()
temp_file = helper.create_temp_file(content, ".yaml")
helper.cleanup()  # Clean up resources
```

### MockKubernetesCluster
Simulates a Kubernetes cluster for testing:
```python
cluster = MockKubernetesCluster()
cluster.apply_resource(resource)
resource = cluster.get_resource("Deployment", "app-name")
cluster.list_resources("Service")
```

### AssertionHelper
Provides specialized assertions for Kubernetes resources:
```python
AssertionHelper.assert_resource_exists(resources, "Deployment", "app-name")
AssertionHelper.assert_container_has_port(container, 8080, "http")
AssertionHelper.assert_service_has_port(service, 80, 8080, "http")
AssertionHelper.assert_resource_limits(container, cpu="500m", memory="1Gi")
```

## Test Configuration

### Environment Variables
- `TEST_VERBOSE` - Enable verbose output
- `TEST_CLEANUP` - Enable/disable test cleanup (default: true)
- `TEST_TIMEOUT` - Test timeout in seconds (default: 300)

### Test Configuration File
The test suite uses configuration from `src/test/__init__.py`:
```python
TEST_CONFIG = {
    "output_dir": "test_output",
    "clean_after_test": True,
    "verbose_output": True,
    "parallel_execution": False,
}
```

## Coverage Requirements

### Functional Coverage
- ✅ All DSL components and methods
- ✅ All configuration options and parameters
- ✅ All output formats and generators
- ✅ Error handling and validation
- ✅ Integration scenarios

### Scenario Coverage
- ✅ Simple single-service applications
- ✅ Complex multi-service platforms
- ✅ Enterprise applications with all features
- ✅ Real-world deployment patterns
- ✅ Multi-environment configurations

### Quality Gates
- ✅ Kubernetes YAML validation
- ✅ Resource relationship verification
- ✅ Security policy compliance
- ✅ Performance and cost optimization
- ✅ Best practices adherence

## Continuous Integration

### Test Pipeline
```yaml
# Example CI/CD pipeline configuration
test:
  script:
    - python src/test/test_run_all.py --report ci_report.json
    - python -m pytest src/test/ --cov=src/k8s_gen --cov-report=xml
  artifacts:
    reports:
      junit: ci_report.json
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

### Quality Metrics
- **Test Coverage**: > 90%
- **Success Rate**: 100%
- **Performance**: < 5 minutes total execution
- **Reliability**: Zero flaky tests

## Debugging Tests

### Verbose Mode
```bash
# Enable detailed output
python src/test/test_run_all.py --verbose

# Show test execution details
pytest src/test/test_core_components.py -v -s
```

### Test Data Inspection
```bash
# Keep test artifacts for debugging
export TEST_CLEANUP=false
python src/test/test_run_all.py

# Inspect generated files in test_output/
ls -la test_output/
```

### Common Issues

#### Import Errors
- Ensure `src/` is in Python path
- Check for circular imports
- Verify all dependencies are installed

#### Resource Generation Failures
- Check component configuration
- Verify required parameters are set
- Ensure valid Kubernetes resource structure

#### Assertion Failures
- Use `AssertionHelper` methods for Kubernetes-specific assertions
- Check resource naming conventions
- Verify expected vs actual resource structure

## Contributing

### Adding New Tests
1. Create test class inheriting from appropriate base
2. Use `TestHelper` for setup/cleanup
3. Follow naming conventions: `test_<functionality>`
4. Add comprehensive assertions
5. Update this README if adding new test modules

### Test Best Practices
- **Isolation**: Each test should be independent
- **Cleanup**: Always clean up resources
- **Assertions**: Use specific, meaningful assertions
- **Documentation**: Document complex test scenarios
- **Performance**: Keep tests fast and efficient

### Code Coverage
- Aim for 100% line coverage on core components
- Include edge cases and error conditions
- Test both success and failure paths
- Verify integration between components

## Test Results

### Success Criteria
All tests must pass with:
- ✅ 100% success rate
- ✅ No security vulnerabilities
- ✅ Valid Kubernetes resources
- ✅ Proper resource relationships
- ✅ Performance within limits

### Reporting
Test results include:
- Individual test status
- Module-level summaries
- Overall success metrics
- Performance statistics
- Coverage reports
- Security scan results

For detailed test execution logs and reports, check the `test_output/` directory after running the test suite. 