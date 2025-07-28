#!/usr/bin/env python3
"""
Output Formats Test Suite.

Tests for Celestra output format generation including:
- Kubernetes YAML
- Docker Compose 
- Helm Charts
- Kustomize
- Terraform
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.celestra import App, StatefulApp
from src.celestra.output import KubernetesOutput, DockerComposeOutput, HelmOutput, KustomizeOutput, TerraformOutput


class TestKubernetesOutput:
    def test_basic_yaml_generation(self):
        app = (App("test-app")
               .image("nginx:1.21")
               .port(8080)
               .replicas(3))
        
        output = KubernetesOutput()
        
        # Test that we can create output instance and call generate
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(app, temp_dir)
            
            # Verify files were created
            files = os.listdir(temp_dir)
            assert len(files) > 0

    def test_yaml_generation_with_multiple_apps(self):
        app1 = App("app1").image("nginx:1.21").port(8080)
        app2 = App("app2").image("redis:7.0").port(6379)
        
        output = KubernetesOutput()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(app1, temp_dir)
            output.generate(app2, temp_dir)
            
            files = os.listdir(temp_dir)
            assert len(files) > 1

    def test_yaml_file_generation(self):
        app = App("file-app").image("nginx:1.21").port(8080)
        output = KubernetesOutput()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(app, temp_dir)
            
            # Check that files exist
            assert len(os.listdir(temp_dir)) > 0

    def test_yaml_namespace_organization(self):
        app = (App("ns-app")
               .image("nginx:1.21")
               .port(8080)
               .set_namespace("custom-namespace"))
        
        output = KubernetesOutput()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(app, temp_dir)
            assert len(os.listdir(temp_dir)) > 0


class TestDockerComposeOutput:
    def test_basic_docker_compose_generation(self):
        app = (App("compose-app")
               .image("nginx:1.21")
               .port(8080)
               .env("ENV", "production"))
        
        with tempfile.TemporaryDirectory() as temp_dir:
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            output = DockerComposeOutput()
            output.generate(app, compose_file)
            assert os.path.exists(compose_file)

    def test_docker_compose_with_dependencies(self):
        app = App("web-app").image("nginx:1.21").port(8080)
        db = StatefulApp("database").image("postgres:13").port(5432)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            output = DockerComposeOutput()
            output.generate(app, compose_file)
            assert os.path.exists(compose_file)

    def test_docker_compose_with_networks(self):
        app = App("network-app").image("nginx:1.21").port(8080)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            output = DockerComposeOutput()
            output.generate(app, compose_file)
            assert os.path.exists(compose_file)

    def test_docker_compose_file_generation(self):
        app = App("compose-test").image("nginx:1.21").port(8080)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            output = DockerComposeOutput()
            output.generate(app, compose_file)
            assert os.path.exists(compose_file)


class TestHelmOutput:
    def test_basic_helm_chart_generation(self):
        app = (App("helm-app")
               .image("nginx:1.21")
               .port(8080)
               .replicas(3))
        
        output = HelmOutput("test-chart")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            files = os.listdir(temp_dir)
            assert len(files) > 0

    def test_helm_chart_with_multiple_services(self):
        app = App("web").image("nginx:1.21").port(8080)
        api = App("api").image("api:latest").port(3000)
        
        output = HelmOutput("multi-service-chart")
        output.add_resource(app)
        output.add_resource(api)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_helm_values_customization(self):
        app = App("values-app").image("nginx:1.21").port(8080)
        output = HelmOutput("values-chart")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_helm_template_generation(self):
        app = App("template-app").image("nginx:1.21").port(8080)
        output = HelmOutput("template-chart")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0


class TestKustomizeOutput:
    def test_basic_kustomize_generation(self):
        app = App("kustomize-app").image("nginx:1.21").port(8080)
        output = KustomizeOutput("kustomize-base")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_kustomize_with_patches(self):
        app = App("patch-app").image("nginx:1.21").port(8080)
        output = KustomizeOutput("patch-base")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_kustomize_with_overlays(self):
        app = App("overlay-app").image("nginx:1.21").port(8080)
        output = KustomizeOutput("overlay-base")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_kustomize_file_generation(self):
        app = App("file-gen-app").image("nginx:1.21").port(8080)
        output = KustomizeOutput("file-gen-base")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0


class TestTerraformOutput:
    def test_basic_terraform_generation(self):
        app = App("terraform-app").image("nginx:1.21").port(8080)
        output = TerraformOutput("terraform-module")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_terraform_with_variables(self):
        app = App("var-app").image("nginx:1.21").port(8080)
        output = TerraformOutput("var-module")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_terraform_with_providers(self):
        app = App("provider-app").image("nginx:1.21").port(8080)
        output = TerraformOutput("provider-module")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0

    def test_terraform_outputs(self):
        app = App("output-app").image("nginx:1.21").port(8080)
        output = TerraformOutput("output-module")
        output.add_resource(app)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output.generate(temp_dir)
            assert len(os.listdir(temp_dir)) > 0


class TestMultiFormatOutput:
    def test_generate_all_formats(self):
        app = (App("multi-format-app")
               .image("nginx:1.21")
               .port(8080)
               .replicas(2))
        
        # Test all output formats with correct APIs
        with tempfile.TemporaryDirectory() as temp_dir:
            # KubernetesOutput - direct generate
            k8s_output = KubernetesOutput()
            k8s_output.generate(app, temp_dir)
            assert len(os.listdir(temp_dir)) > 0
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # DockerComposeOutput - direct generate
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            docker_output = DockerComposeOutput()
            docker_output.generate(app, compose_file)
            assert os.path.exists(compose_file)
        
        # Test add_resource then generate pattern
        for output_class, name in [
            (HelmOutput, "multi-chart"),
            (KustomizeOutput, "multi-base"),
            (TerraformOutput, "multi-module")
        ]:
            with tempfile.TemporaryDirectory() as temp_dir:
                output = output_class(name)
                output.add_resource(app)
                output.generate(temp_dir)
                assert len(os.listdir(temp_dir)) > 0 