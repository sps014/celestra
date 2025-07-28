#!/usr/bin/env python3
"""
Examples Test Suite.

Real-world example tests for Celestra:
- WordPress deployment
- Machine Learning pipeline
- E-commerce platform
- CI/CD pipeline
"""

import pytest

from src.celestra import (
    App, StatefulApp, AppGroup, Job, CronJob, Secret, ConfigMap,
    Service, Ingress, Observability, Scaling
)
from .utils import TestHelper, AssertionHelper, MockKubernetesCluster


class TestWordPressExample:
    """Test WordPress deployment example."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("wordpress_example")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_wordpress_deployment(self):
        """Test complete WordPress deployment."""
        # MySQL Database
        mysql_db = (StatefulApp("mysql")
                    .image("mysql:8.0")
                    .port(3306, "mysql")
                    .env("MYSQL_ROOT_PASSWORD", "rootpassword")
                    .env("MYSQL_DATABASE", "wordpress")
                    .env("MYSQL_USER", "wordpress")
                    .env("MYSQL_PASSWORD", "wordpresspassword")
                    .storage("20Gi")
                    .resources(cpu="500m", memory="1Gi"))
        
        # WordPress Application
        wordpress = (App("wordpress")
                     .image("wordpress:6.1")
                     .port(80, "http")
                     .env("WORDPRESS_DB_HOST", "mysql:3306")
                     .env("WORDPRESS_DB_NAME", "wordpress")
                     .env("WORDPRESS_DB_USER", "wordpress")
                     .env("WORDPRESS_DB_PASSWORD", "wordpresspassword")
                     .resources(cpu="300m", memory="512Mi")
                     .replicas(2)
                     .expose())
        
        # Generate resources
        mysql_resources = mysql_db.generate_kubernetes_resources()
        wordpress_resources = wordpress.generate_kubernetes_resources()
        all_resources = mysql_resources + wordpress_resources
        
        # Verify MySQL StatefulSet
        AssertionHelper.assert_resource_exists(all_resources, "StatefulSet", "mysql")
        
        # Verify WordPress Deployment
        AssertionHelper.assert_resource_exists(all_resources, "Deployment", "wordpress")
        
        # Note: Services are generated automatically for exposed apps
        # We can verify the main components are created
        assert len(all_resources) >= 2  # At least StatefulSet and Deployment


class TestMLPipelineExample:
    """Test Machine Learning pipeline example."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("ml_pipeline_example")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_ml_training_pipeline(self):
        """Test ML training pipeline."""
        # Data Preparation Job
        data_prep = (Job("data-preparation")
                     .image("data-prep:latest")
                     .command(["python", "prepare_data.py"])
                     .env("DATA_SOURCE", "s3://ml-bucket/raw/")
                     .env("OUTPUT_PATH", "s3://ml-bucket/processed/")
                     .resources(cpu="2", memory="4Gi")
                     .completions(1))
        
        # Model Training Job (conceptually runs after data prep)
        model_training = (Job("model-training")
                          .image("ml-training:latest")
                          .command(["python", "train_model.py"])
                          .env("DATA_PATH", "s3://ml-bucket/processed/")
                          .env("MODEL_OUTPUT", "s3://ml-bucket/models/")
                          .resources(cpu="4", memory="16Gi"))
        
        # Model Evaluation Job
        model_evaluation = (Job("model-evaluation")
                            .image("ml-evaluation:latest")
                            .command(["python", "evaluate_model.py"])
                            .env("MODEL_PATH", "s3://ml-bucket/models/")
                            .env("RESULTS_PATH", "s3://ml-bucket/results/")
                            .resources(cpu="1", memory="2Gi"))
        
        # Generate all resources
        all_resources = []
        for job in [data_prep, model_training, model_evaluation]:
            all_resources.extend(job.generate_kubernetes_resources())
        
        # Verify all jobs are created
        AssertionHelper.assert_resource_exists(all_resources, "Job", "data-preparation")
        AssertionHelper.assert_resource_exists(all_resources, "Job", "model-training")
        AssertionHelper.assert_resource_exists(all_resources, "Job", "model-evaluation")
        
        # Verify job configurations
        assert len(all_resources) == 3


class TestEcommercePlatformExample:
    """Test E-commerce platform example."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("ecommerce_example")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_ecommerce_microservices(self):
        """Test complete e-commerce microservices platform."""
        # Create platform
        platform = AppGroup("ecommerce-platform")
        
        # Infrastructure
        postgres = (StatefulApp("postgres")
                   .image("postgres:14")
                   .port(5432)
                   .env("POSTGRES_DB", "ecommerce")
                   .storage("/var/lib/postgresql/data", "100Gi")
                   .resources(cpu="2", memory="8Gi"))
        
        redis = (StatefulApp("redis")
                .image("redis:7.0")
                .port(6379)
                .storage("/data", "20Gi")
                .resources(cpu="500m", memory="2Gi"))
        
        # Microservices
        user_service = (App("user-service")
                       .image("ecommerce/user-service:v1.0")
                       .port(8080)
                       .connect_to([postgres, redis])
                       .replicas(3))
        
        product_service = (App("product-service")
                          .image("ecommerce/product-service:v1.0")
                          .port(8080)
                          .connect_to([postgres])
                          .replicas(2))
        
        order_service = (App("order-service")
                        .image("ecommerce/order-service:v1.0")
                        .port(8080)
                        .depends_on([user_service, product_service])
                        .connect_to([postgres])
                        .replicas(3))
        
        # API Gateway
        api_gateway = (App("api-gateway")
                      .image("nginx:1.21")
                      .port(80)
                      .expose(external_access=True)
                      .replicas(2))
        
        # Add to platform
        platform.add_services([
            postgres, redis,
            user_service, product_service, order_service,
            api_gateway
        ])
        
        # Generate platform resources
        all_resources = platform.generate_kubernetes_resources()
        
        # Verify complete platform
        assert len(all_resources) >= 12  # At least 2 StatefulSets + 4 Deployments + 6 Services
        
        # Verify infrastructure
        AssertionHelper.assert_resource_exists(all_resources, "StatefulSet", "postgres")
        AssertionHelper.assert_resource_exists(all_resources, "StatefulSet", "redis")
        
        # Verify microservices
        AssertionHelper.assert_resource_exists(all_resources, "Deployment", "user-service")
        AssertionHelper.assert_resource_exists(all_resources, "Deployment", "product-service")
        AssertionHelper.assert_resource_exists(all_resources, "Deployment", "order-service")
        AssertionHelper.assert_resource_exists(all_resources, "Deployment", "api-gateway")


class TestCICDPipelineExample:
    """Test CI/CD pipeline example."""
    
    def setup_method(self):
        """Set up test environment."""
        self.helper = TestHelper("cicd_example")
        self.cluster = MockKubernetesCluster()
    
    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup()
    
    def test_cicd_pipeline(self):
        """Test CI/CD pipeline deployment."""
        # Build Job
        build_job = (Job("build")
                     .image("docker:latest")
                     .command(["docker", "build", "-t", "myapp:$BUILD_ID", "."])
                     .env("BUILD_ID", "123")
                     .env("REGISTRY", "myregistry.com")
                     .resources(cpu="1", memory="2Gi"))
        
        # Test Job (conceptually runs after build)
        test_job = (Job("test")
                    .image("myapp:test")
                    .command(["npm", "test"])
                    .env("NODE_ENV", "test")
                    .resources(cpu="500m", memory="1Gi"))
        
        # Security Scan Job
        security_scan = (Job("security-scan")
                         .image("security-scanner:latest")
                         .command(["scan", "myapp:$BUILD_ID"])
                         .env("BUILD_ID", "123")
                         .resources(cpu="500m", memory="1Gi"))
        
        # Deploy Job
        deploy_job = (Job("deploy")
                      .image("kubectl:latest")
                      .command(["kubectl", "apply", "-f", "k8s/"])
                      .env("KUBECONFIG", "/etc/kubeconfig")
                      .resources(cpu="200m", memory="256Mi"))
        
        # Generate all resources
        all_jobs = [build_job, test_job, security_scan, deploy_job]
        all_resources = []
        for job in all_jobs:
            all_resources.extend(job.generate_kubernetes_resources())
        
        # Verify all pipeline jobs
        AssertionHelper.assert_resource_exists(all_resources, "Job", "build")
        AssertionHelper.assert_resource_exists(all_resources, "Job", "test")
        AssertionHelper.assert_resource_exists(all_resources, "Job", "security-scan")
        AssertionHelper.assert_resource_exists(all_resources, "Job", "deploy")
        
        # Verify pipeline has all stages
        assert len(all_resources) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 