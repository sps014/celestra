from src.k8s_gen import App

# Create a simple hello world web app using local build
app = (App("hello-world")
    .build(".", "Dockerfile.demo", VERSION="1.0", ENVIRONMENT="development")
    .port_mapping(8011, 80)
    .expose())

# Generate Docker Compose file
print("🚀 Generating Docker Compose file with local build...")
app.generate().to_docker_compose("./docker-compose.yml")
print("✅ Docker Compose file generated: ./docker-compose.yml")
print("🔨 This will build from Dockerfile.demo instead of using pre-built image")

# You can also generate other formats:
# app.generate().to_yaml("./k8s/")           # Kubernetes manifests
# app.generate().to_helm_chart("./charts/")  # Helm chart
# app.generate().to_kustomize("./k8s/base/")  # Kustomize