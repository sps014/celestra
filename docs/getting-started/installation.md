# Installation Guide

This guide covers all the ways to install Celestra and its dependencies.

## Prerequisites

Before installing Celestra, ensure you have:

### Required Software

- **Python 3.8+** - Celestra is built for modern Python
- **pip** - Python package installer
- **Git** - For cloning the repository

### Optional Dependencies

- **Docker** - For local development and containerization
- **kubectl** - For Kubernetes deployment
- **minikube** or **kind** - For local Kubernetes clusters
- **helm** - For Helm chart generation

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The easiest way to install Celestra is from the Python Package Index:

```bash
pip install celestra
```

For a specific version:

```bash
pip install celestra==1.0.0
```

### Method 2: Install from Source

For development or to get the latest features:

```bash
# Clone the repository
git clone https://github.com/your-username/celestra.git
cd celestra

# Install in development mode
pip install -e src/
```

### Method 3: Install with Dependencies

Install Celestra with all optional dependencies:

```bash
pip install celestra[all]
```

Or install specific extras:

```bash
# For Kubernetes development
pip install celestra[kubernetes]

# For Docker Compose development
pip install celestra[docker]

# For Helm chart generation
pip install celestra[helm]
```

## Environment Setup

### Python Virtual Environment (Recommended)

It's recommended to use a virtual environment:

```bash
# Create a virtual environment
python -m venv celestra-env

# Activate the virtual environment
# On macOS/Linux:
source celestra-env/bin/activate

# On Windows:
celestra-env\Scripts\activate

# Install Celestra
pip install celestra
```

### Using conda

If you prefer conda:

```bash
# Create a conda environment
conda create -n celestra python=3.9

# Activate the environment
conda activate celestra

# Install Celestra
pip install celestra
```

## Kubernetes Setup

### Local Kubernetes Clusters

#### Option 1: Minikube

```bash
# Install minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start minikube
minikube start

# Verify installation
kubectl cluster-info
```

#### Option 2: kind

```bash
# Install kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create a cluster
kind create cluster

# Verify installation
kubectl cluster-info
```

#### Option 3: Docker Desktop

If you have Docker Desktop installed:

1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Enable Kubernetes
4. Click "Apply & Restart"

### Cloud Kubernetes Clusters

#### Google Cloud (GKE)

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth login

# Create a cluster
gcloud container clusters create my-cluster --zone us-central1-a

# Get credentials
gcloud container clusters get-credentials my-cluster --zone us-central1-a
```

#### Amazon EKS

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS
aws configure

# Create a cluster (requires eksctl)
eksctl create cluster --name my-cluster --region us-west-2
```

#### Azure AKS

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create a cluster
az aks create --resource-group myResourceGroup --name myAKSCluster --node-count 1

# Get credentials
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster
```

## Docker Setup

### Install Docker

#### Ubuntu/Debian

```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Add user to docker group
sudo usermod -aG docker $USER
```

#### macOS

Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop).

#### Windows

Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop).

### Verify Docker Installation

```bash
docker --version
docker run hello-world
```

## Helm Setup

### Install Helm

#### Linux/macOS

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Windows

Download from [helm.sh](https://helm.sh/docs/intro/install/).

### Verify Helm Installation

```bash
helm version
```

## Verification

### Test Celestra Installation

Create a simple test file `test_celestra.py`:

```python
from celestra import App

# Create a simple app
app = App("test-app").image("nginx:latest").port(80)

# Generate Kubernetes YAML
app.generate().to_yaml("./test-output/")

print("✅ Celestra is working correctly!")
```

Run the test:

```bash
python test_celestra.py
```

### Test Kubernetes Connection

```bash
# Check cluster info
kubectl cluster-info

# List nodes
kubectl get nodes

# List namespaces
kubectl get namespaces
```

### Test Docker

```bash
# Run a test container
docker run --rm hello-world

# Check Docker daemon
docker info
```

## Configuration

### Celestra Configuration

Create a configuration file `celestra.yaml`:

```yaml
# Default settings
defaults:
  namespace: default
  image_pull_policy: IfNotPresent
  restart_policy: Always

# Output settings
output:
  kubernetes:
    api_version: v1
    format: yaml
  docker_compose:
    version: "3.8"
  helm:
    chart_version: "0.1.0"

# Validation settings
validation:
  security_scan: true
  cost_optimization: true
  resource_limits: true
```

### kubectl Configuration

Configure kubectl for your cluster:

```bash
# For minikube
minikube kubectl -- get pods

# For kind
kind export kubeconfig

# For cloud clusters, follow the provider-specific instructions above
```

## Troubleshooting

### Common Installation Issues

#### 1. Permission Denied

```bash
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution**: Use a virtual environment or install with `--user` flag:

```bash
pip install --user celestra
```

#### 2. Python Version Issues

```bash
ERROR: Package 'celestra' requires a different Python: 3.8.0 not in '>=3.8,<4.0'
```

**Solution**: Upgrade Python to 3.8+ or use pyenv:

```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.9
pyenv install 3.9.0
pyenv global 3.9.0

# Install Celestra
pip install celestra
```

#### 3. Kubernetes Connection Issues

```bash
The connection to the server localhost:8080 was refused
```

**Solution**: Start your Kubernetes cluster:

```bash
# For minikube
minikube start

# For kind
kind create cluster

# For Docker Desktop
# Enable Kubernetes in Docker Desktop settings
```

#### 4. Docker Permission Issues

```bash
Got permission denied while trying to connect to the Docker daemon socket
```

**Solution**: Add user to docker group and restart:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Getting Help

- **Documentation**: Check the [complete documentation](../index.md)
- **GitHub Issues**: Report bugs at [github.com/your-username/Celestra/issues](https://github.com/your-username/Celestra/issues)
- **Discussions**: Ask questions at [github.com/your-username/Celestra/discussions](https://github.com/your-username/Celestra/discussions)

## Next Steps

Now that you have Celestra installed, you can:

1. **[Quick Start](quick-start.md)** - Create your first application
2. **[Core Concepts](core-concepts.md)** - Learn the fundamentals
3. **[Components Guide](../components/index.md)** - Explore all available components
4. **[Examples](../examples/index.md)** - See real-world examples

Ready to get started? Check out the [Quick Start Guide](quick-start.md)! 