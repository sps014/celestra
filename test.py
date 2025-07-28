from src.k8s_gen import App

# Create a simple hello world web app using local build
app = (App("hello-world")
    .build(".", "Dockerfile", VERSION="1.0", ENVIRONMENT="development")
    .port_mapping(8011, 80)  # Docker Compose specific
    .expose())

print("🐳 Generating Docker Compose file with local build...")
app.generate().to_docker_compose("./docker-compose.yml")
print("✅ Docker Compose file generated: ./docker-compose.yml")

print("\n☸️  Generating Kubernetes manifests (will show warnings for port_mapping)...")
app.generate().to_yaml("./k8s/")
print("✅ Kubernetes manifests generated: ./k8s/")
print("💡 Note: For Kubernetes, use .port() + Service instead of .port_mapping()")

# You can also generate other formats:
# app.generate().to_helm_chart("./charts/")  # Helm chart
# app.generate().to_kustomize("./k8s/base/")  # Kustomize