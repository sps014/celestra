# CLI Reference

Complete command-line interface documentation for the Celestra tool.

## Installation

```bash
# Install from PyPI
pip install Celestra

# Install from source
git clone https://github.com/Celestra/Celestra.git
cd Celestra
pip install -e .

# Verify installation
Celestra --version
```

## Global Options

Options available for all commands:

| Option | Description | Default |
|--------|-------------|---------|
| `--help, -h` | Show help message | |
| `--version, -v` | Show version information | |
| `--verbose` | Enable verbose output | False |
| `--config` | Specify config file | `./Celestra.yaml` |
| `--dry-run` | Show what would be done without executing | False |

## Commands

### init

Initialize a new Celestra project.

```bash
Celestra init [PROJECT_NAME] [OPTIONS]
```

**Arguments:**
- `PROJECT_NAME` - Name of the project to create

**Options:**
- `--template, -t` - Project template to use (default: `basic`)
- `--output, -o` - Output directory (default: current directory)
- `--force, -f` - Overwrite existing files

**Examples:**
```bash
# Create a new project
Celestra init my-app

# Create with web app template
Celestra init my-web-app --template web

# Create in specific directory
Celestra init my-app --output ./projects/

# Available templates
Celestra init --list-templates
```

**Available Templates:**
- `basic` - Simple single-service application
- `web` - Web application with database
- `microservices` - Multi-service architecture
- `ml` - Machine learning workload
- `data-pipeline` - Data processing pipeline

### generate

Generate Kubernetes manifests or other formats from DSL code.

```bash
Celestra generate [FILE] [OPTIONS]
```

**Arguments:**
- `FILE` - Python file containing DSL code (default: `app.py`)

**Options:**
- `--output, -o` - Output directory or file
- `--format, -f` - Output format (`kubernetes`, `docker-compose`, `helm`, `kustomize`, `terraform`)
- `--environment, -e` - Target environment
- `--namespace, -n` - Kubernetes namespace
- `--validate` - Validate configuration before generation
- `--watch, -w` - Watch for file changes and regenerate

**Examples:**
```bash
# Generate Kubernetes YAML
Celestra generate app.py --output ./k8s/

# Generate Docker Compose
Celestra generate app.py --format docker-compose --output ./docker-compose.yml

# Generate for specific environment
Celestra generate app.py --environment production --output ./k8s/prod/

# Generate multiple formats
Celestra generate app.py --format kubernetes,docker-compose,helm --output ./output/

# Watch for changes
Celestra generate app.py --watch --output ./k8s/
```

**Format-Specific Options:**

**Docker Compose:**
```bash
# Generate with override files
Celestra generate app.py --format docker-compose \
  --override development:./docker-compose.override.yml \
  --override production:./docker-compose.prod.yml
```

**Helm:**
```bash
# Generate Helm chart
Celestra generate app.py --format helm --output ./charts/my-app/ \
  --chart-version 1.0.0 --app-version latest
```

**Kustomize:**
```bash
# Generate Kustomize structure
Celestra generate app.py --format kustomize --output ./k8s/ \
  --overlays dev,staging,prod
```

### validate

Validate DSL configuration and generated manifests.

```bash
Celestra validate [FILE] [OPTIONS]
```

**Arguments:**
- `FILE` - Python file containing DSL code (default: `app.py`)

**Options:**
- `--format` - Format to validate (`kubernetes`, `docker-compose`, `helm`)
- `--environment` - Environment to validate against
- `--strict` - Enable strict validation mode
- `--output-format` - Output format for validation results (`text`, `json`, `yaml`)

**Examples:**
```bash
# Basic validation
Celestra validate app.py

# Validate for specific environment
Celestra validate app.py --environment production

# Strict validation with JSON output
Celestra validate app.py --strict --output-format json

# Validate generated Helm chart
Celestra validate app.py --format helm
```

### deploy

Deploy applications to Kubernetes or start with Docker Compose.

```bash
Celestra deploy [FILE] [OPTIONS]
```

**Arguments:**
- `FILE` - Python file containing DSL code (default: `app.py`)

**Options:**
- `--format` - Deployment format (`kubernetes`, `docker-compose`)
- `--environment, -e` - Target environment
- `--namespace, -n` - Kubernetes namespace
- `--context` - Kubernetes context
- `--dry-run` - Show what would be deployed
- `--wait` - Wait for deployment to complete
- `--timeout` - Deployment timeout (default: `300s`)
- `--force` - Force deployment even if validation fails

**Examples:**
```bash
# Deploy to Kubernetes
Celestra deploy app.py --environment production

# Deploy with Docker Compose
Celestra deploy app.py --format docker-compose

# Dry run deployment
Celestra deploy app.py --dry-run --environment production

# Deploy to specific namespace
Celestra deploy app.py --namespace my-app --wait
```

### dev

Start local development environment with Docker Compose.

```bash
Celestra dev [FILE] [OPTIONS]
```

**Arguments:**
- `FILE` - Python file containing DSL code (default: `app.py`)

**Options:**
- `--down` - Stop the development environment
- `--build` - Rebuild containers before starting
- `--logs` - Show container logs
- `--follow` - Follow log output
- `--watch` - Watch for file changes and restart
- `--service` - Operate on specific service only

**Examples:**
```bash
# Start development environment
Celestra dev app.py

# Start and follow logs
Celestra dev app.py --logs --follow

# Stop development environment
Celestra dev app.py --down

# Watch for changes and auto-restart
Celestra dev app.py --watch

# Rebuild and start
Celestra dev app.py --build
```

### secrets

Manage secrets and sensitive configuration.

```bash
Celestra secrets [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

#### generate
Generate secrets from DSL configuration.

```bash
Celestra secrets generate [FILE] [OPTIONS]
```

**Options:**
- `--output, -o` - Output directory for secret files
- `--format` - Output format (`yaml`, `json`, `env`)
- `--encrypt` - Encrypt secrets using specified key

**Examples:**
```bash
# Generate secret manifests
Celestra secrets generate app.py --output ./secrets/

# Generate encrypted secrets
Celestra secrets generate app.py --encrypt --key-file ./key.txt
```

#### sync
Synchronize secrets with external secret stores.

```bash
Celestra secrets sync [OPTIONS]
```

**Options:**
- `--vault-addr` - Vault server address
- `--aws-region` - AWS region for Parameter Store/Secrets Manager
- `--dry-run` - Show what would be synced

**Examples:**
```bash
# Sync with HashiCorp Vault
Celestra secrets sync --vault-addr https://vault.company.com

# Sync with AWS Secrets Manager
Celestra secrets sync --aws-region us-east-1
```

#### encrypt/decrypt
Encrypt or decrypt secret files.

```bash
Celestra secrets encrypt [FILES] --key-file [KEY_FILE]
Celestra secrets decrypt [FILES] --key-file [KEY_FILE]
```

### jobs

Manage Jobs and CronJobs.

```bash
Celestra jobs [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

#### run
Run a job immediately.

```bash
Celestra jobs run [JOB_NAME] [OPTIONS]
```

**Options:**
- `--wait` - Wait for job completion
- `--logs` - Show job logs
- `--timeout` - Job timeout

**Examples:**
```bash
# Run database migration
Celestra jobs run db-migration --wait --logs

# Run with custom timeout
Celestra jobs run data-processing --timeout 3600
```

#### list
List jobs and their status.

```bash
Celestra jobs list [OPTIONS]
```

**Options:**
- `--status` - Filter by status (`running`, `completed`, `failed`)
- `--namespace` - Kubernetes namespace

#### logs
Show logs for a specific job.

```bash
Celestra jobs logs [JOB_NAME] [OPTIONS]
```

**Options:**
- `--follow, -f` - Follow log output
- `--tail` - Number of lines to show

### rbac

Manage RBAC (Role-Based Access Control) resources.

```bash
Celestra rbac [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

#### validate
Validate RBAC configuration.

```bash
Celestra rbac validate [FILE] [OPTIONS]
```

#### generate
Generate RBAC manifests.

```bash
Celestra rbac generate [FILE] [OPTIONS]
```

**Options:**
- `--output, -o` - Output directory
- `--namespace` - Target namespace

#### check
Check RBAC permissions for a user or service account.

```bash
Celestra rbac check [USER_OR_SA] [OPTIONS]
```

**Options:**
- `--resource` - Resource to check access for
- `--verb` - Verb to check (get, list, create, etc.)

### security

Security scanning and policy management.

```bash
Celestra security [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

#### scan
Scan configuration for security issues.

```bash
Celestra security scan [FILE] [OPTIONS]
```

**Options:**
- `--report` - Output report file
- `--format` - Report format (`text`, `json`, `html`)
- `--severity` - Minimum severity level (`low`, `medium`, `high`, `critical`)

**Examples:**
```bash
# Basic security scan
Celestra security scan app.py

# Generate HTML report
Celestra security scan app.py --report ./security-report.html --format html

# Show only high and critical issues
Celestra security scan app.py --severity high
```

#### policies
Manage security policies.

```bash
Celestra security policies [list|apply|delete] [OPTIONS]
```

### monitor

Set up and manage monitoring and observability.

```bash
Celestra monitor [SUBCOMMAND] [OPTIONS]
```

**Subcommands:**

#### setup
Set up monitoring stack (Prometheus, Grafana, Jaeger).

```bash
Celestra monitor setup [FILE] [OPTIONS]
```

**Options:**
- `--namespace` - Monitoring namespace
- `--storage-class` - Storage class for persistent volumes
- `--ingress-host` - Ingress hostname for monitoring UIs

#### dashboards
Manage Grafana dashboards.

```bash
Celestra monitor dashboards [import|export|list] [OPTIONS]
```

**Options:**
- `--dashboard-dir` - Directory containing dashboard files
- `--dashboard-id` - Specific dashboard ID

#### alerts
Manage alerting rules.

```bash
Celestra monitor alerts [test|apply|list] [OPTIONS]
```

**Options:**
- `--dry-run` - Test alerts without applying
- `--rules-file` - Alerting rules file

**Examples:**
```bash
# Setup monitoring stack
Celestra monitor setup app.py --namespace monitoring

# Import dashboards
Celestra monitor dashboards import --dashboard-dir ./dashboards/

# Test alerting rules
Celestra monitor alerts test --dry-run
```

## Configuration File

Celestra can be configured using a YAML configuration file:

```yaml
# Celestra.yaml
project:
  name: "my-app"
  version: "1.0.0"
  
defaults:
  namespace: "default"
  environment: "development"
  
output:
  kubernetes:
    directory: "./k8s/"
    namespace_per_environment: true
  
  docker_compose:
    file: "./docker-compose.yml"
    override_files:
      development: "./docker-compose.override.yml"
      production: "./docker-compose.prod.yml"
  
  helm:
    directory: "./charts/"
    chart_version: "0.1.0"

environments:
  development:
    replicas: 1
    resources:
      cpu: "100m"
      memory: "256Mi"
  
  staging:
    replicas: 2
    resources:
      cpu: "500m"
      memory: "512Mi"
  
  production:
    replicas: 5
    resources:
      cpu: "1000m"
      memory: "1Gi"
    auto_scaling: true

validation:
  strict: true
  security_scan: true
  
monitoring:
  enabled: true
  namespace: "monitoring"
  
secrets:
  encryption:
    enabled: true
    key_file: "./encryption.key"
  
  external_sources:
    vault:
      address: "https://vault.company.com"
    aws:
      region: "us-east-1"

plugins:
  - name: "datadog"
    config:
      api_key_secret: "datadog-api-key"
  - name: "custom-security"
    path: "./plugins/security.py"
```

## Environment Variables

Configure Celestra using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `celestra_CONFIG` | Path to configuration file | `./Celestra.yaml` |
| `celestra_ENVIRONMENT` | Default environment | `development` |
| `celestra_NAMESPACE` | Default Kubernetes namespace | `default` |
| `celestra_OUTPUT_DIR` | Default output directory | `./output/` |
| `celestra_VERBOSE` | Enable verbose output | `false` |
| `celestra_DRY_RUN` | Enable dry-run mode | `false` |

## Exit Codes

Celestra uses standard exit codes:

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | General error |
| 2 | Validation error |
| 3 | Configuration error |
| 4 | Network error |
| 5 | Permission error |

## Shell Completion

Enable shell completion for better command-line experience:

```bash
# Bash
eval "$(Celestra completion bash)"

# Zsh
eval "$(Celestra completion zsh)"

# Fish
Celestra completion fish | source

# PowerShell
Celestra completion powershell | Out-String | Invoke-Expression
```

Add to your shell profile to make it permanent:

```bash
# Add to ~/.bashrc or ~/.zshrc
eval "$(Celestra completion bash)"  # or zsh
```

## Troubleshooting

### Common Issues

**1. Import Error**
```bash
Error: ModuleNotFoundError: No module named 'celestra'
```
Solution: Ensure Celestra is properly installed: `pip install Celestra`

**2. Validation Errors**
```bash
Error: App must specify a container image
```
Solution: Check your DSL code for required fields.

**3. Permission Denied**
```bash
Error: Permission denied writing to output directory
```
Solution: Check file permissions or use `sudo` if necessary.

**4. Kubernetes Connection Issues**
```bash
Error: Unable to connect to Kubernetes cluster
```
Solution: Check your `kubectl` configuration and cluster connectivity.

### Debug Mode

Enable debug mode for detailed troubleshooting:

```bash
Celestra --verbose generate app.py
celestra_VERBOSE=true Celestra generate app.py
```

### Log Files

Celestra logs are written to:
- Linux/macOS: `~/.Celestra/logs/`
- Windows: `%APPDATA%\Celestra\logs\`

### Getting Help

- Documentation: https://Celestra.readthedocs.io
- GitHub Issues: https://github.com/Celestra/Celestra/issues
- Community Slack: https://Celestra.slack.com
- Stack Overflow: Tag questions with `Celestra` 