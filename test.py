from src.k8s_gen import App

# Create a simple hello world web app
app = (App("hello-world")
    .image("nginxdemos/hello:latest")
    .port(80)
    .replicas(2)
    .expose())

# Generate Kubernetes manifests
print("🚀 Generating Kubernetes manifests...")
app.generate().to_yaml("./k8s/")
print("✅ Kubernetes manifests generated in ./k8s/ directory")

# You can also generate other formats:
# app.generate().to_docker_compose("./docker-compose.yml")
# app.generate().to_helm_chart("./charts/")
# app.generate().to_kustomize("./k8s/base/")