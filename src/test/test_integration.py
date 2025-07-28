#!/usr/bin/env python3
"""
Integration Test Suite.

End-to-end tests for Celestra integration scenarios.
"""

import pytest
from src.celestra import App, StatefulApp, Service, Ingress, AppGroup


class TestMicroservicesPlatform:
    def test_complete_ecommerce_platform(self):
        # Simple microservices platform test
        user_service = (App("user-service")
                        .image("user-service:v1.0.0")
                        .port(8080, "http")
                        .env("ENV", "production")
                        .replicas(2))
        
        product_service = (App("product-service")
                           .image("product-service:v1.0.0")
                           .port(8080, "http")
                           .env("ENV", "production")
                           .replicas(2))
        
        # Create service group
        platform = AppGroup("ecommerce-platform")
        platform.add_service(user_service)
        platform.add_service(product_service)
        
        # Verify platform is created correctly
        assert len(platform._services) == 2
        assert user_service._name == "user-service"
        assert product_service._name == "product-service"


class TestEnterpriseApplication:
    def test_enterprise_app_with_all_features(self):
        # Simple enterprise application
        app = (App("enterprise-app")
               .image("enterprise:v1.0.0")
               .port(8080, "http")
               .port(9090, "metrics")
               .env("ENV", "production")
               .env("LOG_LEVEL", "info")
               .resources(cpu="1", memory="2Gi")
               .replicas(3))
        
        # Create supporting database
        database = (StatefulApp("enterprise-db")
                    .image("postgres:13")
                    .port(5432, "db")
                    .env("POSTGRES_DB", "enterprise")
                    .storage("100Gi"))
        
        # Verify application configuration
        assert app._name == "enterprise-app"
        assert len(app._ports) == 2
        assert app._environment["ENV"] == "production"
        assert app._replicas == 3
        
        # Verify database configuration
        assert database._name == "enterprise-db"
        assert database._storage_size == "100Gi"


class TestMultiEnvironmentDeployment:
    def test_dev_staging_prod_environments(self):
        # Development environment
        dev_app = (App("myapp-dev")
                   .image("myapp:dev")
                   .port(8080)
                   .env("ENV", "development")
                   .resources(cpu="100m", memory="256Mi")
                   .replicas(1))
        
        # Staging environment
        staging_app = (App("myapp-staging")
                       .image("myapp:staging")
                       .port(8080)
                       .env("ENV", "staging")
                       .resources(cpu="500m", memory="1Gi")
                       .replicas(2))
        
        # Production environment
        prod_app = (App("myapp-prod")
                    .image("myapp:v1.0.0")
                    .port(8080)
                    .env("ENV", "production")
                    .resources(cpu="1", memory="2Gi")
                    .replicas(5))
        
        # Verify environment-specific configurations
        assert dev_app._environment["ENV"] == "development"
        assert dev_app._replicas == 1
        
        assert staging_app._environment["ENV"] == "staging"
        assert staging_app._replicas == 2
        
        assert prod_app._environment["ENV"] == "production"
        assert prod_app._replicas == 5
        
        # Verify different resource allocations
        assert dev_app._resources["requests"]["cpu"] == "100m"
        assert staging_app._resources["requests"]["cpu"] == "500m"
        assert prod_app._resources["requests"]["cpu"] == "1" 