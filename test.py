from src.k8s_gen import App

# Create a simple hello world web app
app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .replicas(2)
    .expose())

# Generate Docker Compose file
print("🚀 Generating Docker Compose file...")
app.generate().to_docker_compose("./docker-compose.yml")
print("✅ Docker Compose file generated: ./docker-compose.yml")

# You can also generate other formats:
# app.generate().to_yaml("./k8s/")           # Kubernetes manifests
# app.generate().to_helm_chart("./charts/")  # Helm chart
# app.generate().to_kustomize("./k8s/base/")  # Kustomize