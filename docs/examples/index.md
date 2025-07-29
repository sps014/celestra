# Examples

This section contains comprehensive examples demonstrating how to use Celestra for various deployment scenarios, from simple applications to complex production platforms.

## 🎯 Quick Start Examples

### Simple Applications
Perfect for getting started with Celestra:

- **[Hello World](simple/hello-world.md)** - Your first Celestra application
- **[NGINX Web Server](simple/nginx-app.md)** - Basic web server deployment
- **[Node.js Application](simple/nodejs-app.md)** - Simple Node.js app with database

## 🏗️ Production Deployments

### Web Applications
Real-world web application deployments:

*Coming soon - Production deployment examples will be added here*

### API Services
Production API deployments:

*Coming soon - API service examples will be added here*

### Message Queues
Event streaming and messaging platforms:

*Coming soon - Message queue examples will be added here*

## 🔧 Complex Platforms

### Microservices Architecture
Complete microservices platforms:

*Coming soon - Microservices architecture examples will be added here*

### Data Processing
Big data and analytics platforms:

*Coming soon - Data processing examples will be added here*

### Monitoring and Observability
Complete monitoring stacks:

*Coming soon - Monitoring and observability examples will be added here*

## 🎨 Configuration Examples

### Configuration Management
Learn to manage application configuration:

*Coming soon - Configuration management examples will be added here*

### Security Configurations
Security-focused examples:

*Coming soon - Security configuration examples will be added here*

## 🚀 Deployment Patterns

### High Availability
Production-ready high availability setups:

*Coming soon - High availability patterns will be added here*

### Development Workflows
Development and testing patterns:

*Coming soon - Development workflow patterns will be added here*

## 📊 Use Case Examples

### Industry-Specific
Examples for different industries:

*Coming soon - Industry-specific examples will be added here*

### Technology Stacks
Popular technology combinations:

*Coming soon - Technology stack examples will be added here*

## 🎯 Getting Started

### Choose Your Path

**New to Celestra?** Start with:
1. **[Hello World](simple/hello-world.md)** - Basic concepts
2. **[NGINX Web Server](simple/nginx-app.md)** - Simple web app

**Building Production Apps?** Try:
*Coming soon - Production examples will be added here*

**Advanced Use Cases?** Explore:
*Coming soon - Advanced examples will be added here*

## 🔧 Example Structure

Each example follows a consistent structure:

### 1. **Overview**
- What you'll build
- Key features
- Architecture diagram

### 2. **Prerequisites**
- Required software
- Cluster requirements
- Resource estimates

### 3. **Step-by-Step Guide**
- Complete code examples
- Configuration details
- Deployment instructions

### 4. **Verification**
- Health checks
- Testing procedures
- Troubleshooting tips

### 5. **Customization**
- Configuration options
- Scaling strategies
- Security considerations

## 🚀 Running Examples

### Quick Start

```bash
# Clone the examples repository
git clone https://github.com/sps014/celestra-examples.git
cd celestra-examples

# Run a simple example
python examples/simple/hello-world.py

# Deploy to Kubernetes
kubectl apply -f ./output/
```

### Example Categories

**Simple Examples** - Perfect for learning:
```bash
# Run simple examples
python examples/simple/nginx-app.py
python examples/simple/nodejs-app.py
```

**Production Examples** - Real-world deployments:
*Coming soon - Production examples will be added here*

**Complex Examples** - Advanced architectures:
*Coming soon - Complex examples will be added here*

## 🎯 Contributing Examples

We welcome contributions! To add your own example:

1. **Create the example** in the appropriate directory
2. **Follow the structure** outlined above
3. **Include comprehensive documentation**
4. **Add tests** for verification
5. **Submit a pull request**

### Example Template

```python
# example_template.py
"""
Example Name: Brief description

This example demonstrates [key features].

Architecture:
- Component 1: Description
- Component 2: Description
- Component 3: Description
"""

from celestra import App, StatefulApp, ConfigMap, Secret

def create_example():
    """Create the example application"""
    
    # Component 1
    component1 = App("component1").image("image:tag").port(8080)
    
    # Component 2
    component2 = StatefulApp("component2").image("image:tag").storage("10Gi")
    
    # Configuration
    config = ConfigMap("config").add("key", "value")
    
    # Generate manifests
    component1.generate().to_yaml("./output/")
    component2.generate().to_yaml("./output/")
    config.generate().to_yaml("./output/")
    
    print("✅ Example manifests generated in ./output/")

if __name__ == "__main__":
    create_example()
```

## 📚 Related Documentation

- **[Getting Started](../getting-started/quick-start.md)** - Installation and first steps
- **[Components Guide](../components/index.md)** - All available components
- **[Tutorials](../tutorials/index.md)** - Step-by-step guides

## 🚀 Next Steps

Ready to start building? Choose an example that matches your needs:

- **Simple applications** → Start with [Hello World](simple/hello-world.md)
- **Production deployments** → *Coming soon*
- **Complex platforms** → *Coming soon*

Need help? Check out the [Getting Started Guide](../getting-started/quick-start.md) or [Tutorials](../tutorials/index.md)! 