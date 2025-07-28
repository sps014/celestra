# Installation

## Prerequisites

Before installing K8s-Gen DSL, ensure you have:

- **Python 3.8+** installed on your system
- **pip** package manager
- **Git** (optional, for cloning examples)

## Installation Methods

### Method 1: Install from Source

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/k8s-gen.git
   cd k8s-gen
   ```

2. Install dependencies:
   ```bash
   pip install -r src/requirements.txt
   ```

3. Install in development mode:
   ```bash
   pip install -e src/
   ```

### Method 2: Using pip (Coming Soon)

```bash
pip install k8s-gen
```

## Verification

Verify the installation by running:

```python
from k8s_gen import App

# Create a simple app
app = App("test-app").image("nginx:latest")
print("K8s-Gen DSL installed successfully!")
```

## Optional Dependencies

For enhanced functionality, install additional tools:

```bash
# For Kubernetes deployment
kubectl version

# For Docker images
docker --version

# For Helm charts
helm version
```

## Troubleshooting

### Common Issues

- **Python Version**: Ensure Python 3.8+ is installed
- **Path Issues**: Make sure the installation directory is in your Python path
- **Dependencies**: Run `pip install -r src/requirements.txt` if imports fail

## Next Steps

Once installed, proceed to the [Quick Start Guide](quick-start.md) to create your first application.
