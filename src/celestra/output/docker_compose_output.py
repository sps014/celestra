"""
Docker Compose output format for Celestra DSL.

This module contains the DockerComposeOutput class for generating Docker Compose
files from DSL builders for local development.
"""

from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import subprocess
import os

from .base_output import OutputFormat
from ..utils.decorators import docker_compose_only


class DockerComposeOutput(OutputFormat):
    """
    Output format for generating Docker Compose files.
    
    This class generates Docker Compose YAML files from DSL builders,
    optimized for local development and testing.
    
    Example:
        ```python
        output = DockerComposeOutput()
        output.set_option("include_volumes", True)
        output.set_option("add_health_checks", True)
        output.generate(app, "./docker-compose.yml")
        ```
    """
    
    def __init__(self):
        """Initialize the Docker Compose output format."""
        super().__init__()
        # Set default options
        self.set_options({
            "version": "3.8",  # Docker Compose version
            "include_volumes": True,  # Include volume definitions
            "include_networks": True,  # Include network definitions
            "add_health_checks": True,  # Add health checks to services
            "add_dependencies": True,  # Add service dependencies
            "generate_env_file": False,  # Generate .env file
            "use_build_context": False,  # Use build context instead of images
            "expose_ports": True,  # Expose service ports
            "add_labels": True,  # Add labels to services
            "restart_policy": "unless-stopped"  # Default restart policy
        })
        # Store the last generated compose file path
        self._last_compose_file: Optional[Path] = None
    
    def generate(
        self, 
        builder: Any,
        output_file: Union[str, Path] = "./docker-compose.yml",
        base_file: Optional[str] = None,
        override_files: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Generate Docker Compose file.
        
        Args:
            builder: DSL builder to generate from
            output_file: Path to write Docker Compose file
            base_file: Base compose file path
            override_files: Environment-specific override files
        """
        # Convert builder to Docker Compose format
        compose_config = self._convert_builder_to_compose(builder)
        
        # Create output directory if needed
        output_path = Path(output_file)
        self._ensure_output_directory(output_path.parent)
        
        # Generate main compose file
        self._write_compose_file(compose_config, output_path)
        
        # Generate environment file if requested
        if self.get_option("generate_env_file", False):
            env_file_path = output_path.parent / ".env"
            self._write_env_file(builder, env_file_path)
        
        # Generate override files if specified
        if override_files:
            for env_name, override_path in override_files.items():
                override_config = self._generate_override_config(builder, env_name)
                self._write_compose_file(override_config, Path(override_path))
        
        print(f"Generated Docker Compose file: {output_path}")
        self._update_last_compose_file(output_path)
    
    def _convert_builder_to_compose(self, builder: Any) -> Dict[str, Any]:
        """
        Convert a DSL builder to Docker Compose configuration.
        
        Args:
            builder: DSL builder
            
        Returns:
            Dict[str, Any]: Docker Compose configuration
        """
        compose_config = {
            "version": self.get_option("version", "3.8"),
            "services": {},
            "volumes": {},
            "networks": {}
        }
        
        # Handle different builder types
        if hasattr(builder, '_services'):  # AppGroup
            self._convert_app_group(builder, compose_config)
        else:  # Single App or StatefulApp
            self._convert_single_app(builder, compose_config)
        
        # Add default network if enabled
        if self.get_option("include_networks", True) and not compose_config["networks"]:
            compose_config["networks"]["default"] = {
                "driver": "bridge"
            }
        
        # Remove empty sections
        if not compose_config["volumes"]:
            del compose_config["volumes"]
        if not compose_config["networks"]:
            del compose_config["networks"]
        
        return compose_config
    
    def _convert_app_group(self, app_group: Any, compose_config: Dict[str, Any]) -> None:
        """
        Convert an AppGroup to Docker Compose services.
        
        Args:
            app_group: AppGroup builder
            compose_config: Docker Compose configuration to update
        """
        for service in app_group._services:
            service_name = service.name
            service_config = self._convert_service_to_compose(service)
            compose_config["services"][service_name] = service_config
        
        # Add shared volumes and networks
        self._add_shared_resources(app_group, compose_config)
        
        # Apply dependencies
        if hasattr(app_group, '_dependencies'):
            self._apply_service_dependencies(app_group._dependencies, compose_config)
    
    def _convert_single_app(self, app: Any, compose_config: Dict[str, Any]) -> None:
        """
        Convert a single App/StatefulApp to Docker Compose service.
        
        Args:
            app: App or StatefulApp builder
            compose_config: Docker Compose configuration to update
        """
        service_name = app.name
        service_config = self._convert_service_to_compose(app)
        compose_config["services"][service_name] = service_config
    
    def _convert_service_to_compose(self, service: Any) -> Dict[str, Any]:
        """
        Convert a service (App/StatefulApp) to Docker Compose service configuration.
        
        Args:
            service: Service builder
            
        Returns:
            Dict[str, Any]: Docker Compose service configuration
        """
        service_config = {}
        
        # Image or build context
        if hasattr(service, '_build_context') and service._build_context:
            # Use build configuration when available
            build_config = {
                "context": service._build_context,
                "dockerfile": getattr(service, '_dockerfile', 'Dockerfile')
            }
            
            # Add build args if any
            if hasattr(service, '_build_args') and service._build_args:
                build_config["args"] = service._build_args
            
            service_config["build"] = build_config
        elif hasattr(service, '_image') and service._image:
            # Use pre-built image
            service_config["image"] = service._image
        else:
            # Fallback to default image if neither build nor image is specified
            service_config["image"] = "nginx:latest"
        
        # Container name (only if not using replicas)
        replicas = getattr(service, '_replicas', 1)
        if replicas <= 1:
            service_config["container_name"] = service.name
        
        # Restart policy
        service_config["restart"] = self.get_option("restart_policy", "unless-stopped")
        
        # Ports
        if self.get_option("expose_ports", True):
            ports = self._get_service_ports(service)
            if ports:
                service_config["ports"] = ports
        
        # Environment variables
        environment = self._get_service_environment(service)
        if environment:
            service_config["environment"] = environment
        
        # Volumes
        volumes = self._get_service_volumes(service)
        if volumes:
            service_config["volumes"] = volumes
        
        # Networks
        if self.get_option("include_networks", True):
            service_config["networks"] = ["default"]
        
        # Health checks
        if self.get_option("add_health_checks", True):
            health_check = self._get_service_health_check(service)
            if health_check:
                service_config["healthcheck"] = health_check
        
        # Dependencies
        if self.get_option("add_dependencies", True):
            depends_on = self._get_service_dependencies(service)
            if depends_on:
                service_config["depends_on"] = depends_on
        
        # Labels
        if self.get_option("add_labels", True):
            labels = self._get_service_labels(service)
            if labels:
                service_config["labels"] = labels
        
        # Resources (CPU/Memory limits)
        deploy_config = self._get_service_deploy_config(service)
        if deploy_config:
            service_config["deploy"] = deploy_config
        
        return service_config
    
    def _get_service_ports(self, service: Any) -> List[str]:
        """Get port mappings for a service."""
        ports = []
        
        if hasattr(service, '_ports'):
            for port_config in service._ports:
                container_port = port_config.get("containerPort", port_config.get("port", 80))
                
                # Check if hostPort is specified for explicit mapping
                if "hostPort" in port_config:
                    host_port = port_config["hostPort"]
                else:
                    host_port = container_port  # Map to same port by default
                
                ports.append(f"{host_port}:{container_port}")
        
        return ports
    
    def _get_service_environment(self, service: Any) -> Dict[str, str]:
        """Get environment variables for a service."""
        environment = {}
        
        # Direct environment variables
        if hasattr(service, '_environment'):
            environment.update(service._environment)
        
        # Environment from secrets (simplified for Docker Compose)
        if hasattr(service, '_secrets'):
            for secret in service._secrets:
                if hasattr(secret, '_string_data'):
                    for key, value in secret._string_data.items():
                        env_key = f"{secret.name.upper()}_{key.upper()}"
                        environment[env_key] = value
        
        # Environment from config maps
        if hasattr(service, '_config_maps'):
            for config_map in service._config_maps:
                if hasattr(config_map, '_data'):
                    for key, value in config_map._data.items():
                        env_key = f"{config_map.name.upper()}_{key.upper()}"
                        environment[env_key] = value
        
        return environment
    
    def _get_service_volumes(self, service: Any) -> List[str]:
        """Get volume mappings for a service."""
        volumes = []
        
        # Persistent volumes for StatefulApps
        if hasattr(service, '_storage_size') and service._storage_size:
            mount_path = getattr(service, '_mount_path', '/data')
            volume_name = f"{service.name}-data"
            volumes.append(f"{volume_name}:{mount_path}")
        
        # ConfigMap volumes
        if hasattr(service, '_config_maps'):
            for config_map in service._config_maps:
                if hasattr(config_map, '_mount_path') and config_map._mount_path:
                    volume_name = f"{config_map.name}-config"
                    volumes.append(f"./{config_map.name}:{config_map._mount_path}:ro")
        
        # Secret volumes (for development only)
        if hasattr(service, '_secrets'):
            for secret in service._secrets:
                if hasattr(secret, '_mount_path') and secret._mount_path:
                    volume_name = f"{secret.name}-secret"
                    volumes.append(f"./{secret.name}:{secret._mount_path}:ro")
        
        return volumes
    
    def _get_service_health_check(self, service: Any) -> Optional[Dict[str, Any]]:
        """Get health check configuration for a service."""
        if hasattr(service, '_health') and service._health:
            health = service._health
            
            # Try to extract health check from the health object
            if hasattr(health, 'http_get'):
                path = health.http_get.get('path', '/health')
                port = health.http_get.get('port', 8080)
                return {
                    "test": [f"CMD", "curl", "-f", f"http://localhost:{port}{path}"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "40s"
                }
            elif hasattr(health, 'exec_action'):
                command = health.exec_action.get('command', ['true'])
                return {
                    "test": ["CMD"] + command,
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3,
                    "start_period": "40s"
                }
        
        # Default health check based on service type
        if hasattr(service, '_ports') and service._ports:
            port = service._ports[0].get('containerPort', 8080)
            return {
                "test": [f"CMD", "curl", "-f", f"http://localhost:{port}/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3,
                "start_period": "40s"
            }
        
        return None
    
    def _get_service_dependencies(self, service: Any) -> Optional[Dict[str, Dict[str, str]]]:
        """Get service dependencies."""
        if hasattr(service, '_dependencies') and service._dependencies:
            depends_on = {}
            for dep in service._dependencies:
                depends_on[dep] = {"condition": "service_healthy"}
            return depends_on
        
        if hasattr(service, '_connections') and service._connections:
            depends_on = {}
            for connection in service._connections:
                depends_on[connection] = {"condition": "service_started"}
            return depends_on
        
        return None
    
    def _get_service_labels(self, service: Any) -> Dict[str, str]:
        """Get labels for a service."""
        labels = {}
        
        if hasattr(service, '_labels'):
            labels.update(service._labels)
        
        # Add Docker Compose specific labels
        labels.update({
            "com.k8s-gen.service": service.name,
            "com.k8s-gen.version": "1.0.0"
        })
        
        return labels
    
    def _get_service_deploy_config(self, service: Any) -> Optional[Dict[str, Any]]:
        """Get deployment configuration for a service."""
        deploy_config = {}
        
        # Resource limits
        if hasattr(service, '_resources') and service._resources:
            resources = service._resources
            
            if 'limits' in resources:
                limits = {}
                if 'cpu' in resources['limits']:
                    limits['cpus'] = resources['limits']['cpu']
                if 'memory' in resources['limits']:
                    limits['memory'] = resources['limits']['memory']
                
                if limits:
                    deploy_config['resources'] = {'limits': limits}
        
        # Replicas (for Docker Swarm mode)
        if hasattr(service, '_replicas') and service._replicas > 1:
            deploy_config['replicas'] = service._replicas
        
        return deploy_config if deploy_config else None
    
    def _add_shared_resources(self, app_group: Any, compose_config: Dict[str, Any]) -> None:
        """Add shared volumes and networks from AppGroup."""
        # Add shared volumes
        if self.get_option("include_volumes", True):
            for service in app_group._services:
                if hasattr(service, '_storage_size') and service._storage_size:
                    volume_name = f"{service.name}-data"
                    compose_config["volumes"][volume_name] = {}
        
        # Add shared networks
        if self.get_option("include_networks", True):
            compose_config["networks"]["default"] = {
                "driver": "bridge"
            }
    
    def _apply_service_dependencies(self, dependencies: Dict[str, List[str]], compose_config: Dict[str, Any]) -> None:
        """Apply service dependencies to compose configuration."""
        for service_name, deps in dependencies.items():
            if service_name in compose_config["services"]:
                service_config = compose_config["services"][service_name]
                
                if "depends_on" not in service_config:
                    service_config["depends_on"] = {}
                
                for dep in deps:
                    service_config["depends_on"][dep] = {"condition": "service_healthy"}
    
    def _generate_override_config(self, builder: Any, environment: str) -> Dict[str, Any]:
        """Generate environment-specific override configuration."""
        override_config = {
            "version": self.get_option("version", "3.8"),
            "services": {}
        }
        
        # Environment-specific overrides
        if environment == "development":
            # Add development-specific configurations
            self._add_development_overrides(builder, override_config)
        elif environment == "production":
            # Add production-specific configurations
            self._add_production_overrides(builder, override_config)
        
        return override_config
    
    def _add_development_overrides(self, builder: Any, override_config: Dict[str, Any]) -> None:
        """Add development-specific overrides."""
        # Enable file watching, debugging, etc.
        if hasattr(builder, '_services'):  # AppGroup
            for service in builder._services:
                service_name = service.name
                override_config["services"][service_name] = {
                    "environment": {
                        "NODE_ENV": "development",
                        "DEBUG": "true"
                    },
                    "volumes": [
                        "./src:/app/src"  # Mount source code for hot reload
                    ]
                }
        else:  # Single service
            override_config["services"][builder.name] = {
                "environment": {
                    "NODE_ENV": "development",
                    "DEBUG": "true"
                },
                "volumes": [
                    "./src:/app/src"
                ]
            }
    
    def _add_production_overrides(self, builder: Any, override_config: Dict[str, Any]) -> None:
        """Add production-specific overrides."""
        # Add production optimizations
        if hasattr(builder, '_services'):  # AppGroup
            for service in builder._services:
                service_name = service.name
                override_config["services"][service_name] = {
                    "environment": {
                        "NODE_ENV": "production"
                    },
                    "restart": "always",
                    "logging": {
                        "driver": "json-file",
                        "options": {
                            "max-size": "10m",
                            "max-file": "3"
                        }
                    }
                }
        else:  # Single service
            override_config["services"][builder.name] = {
                "environment": {
                    "NODE_ENV": "production"
                },
                "restart": "always",
                "logging": {
                    "driver": "json-file",
                    "options": {
                        "max-size": "10m",
                        "max-file": "3"
                    }
                }
            }
    
    def _write_compose_file(self, compose_config: Dict[str, Any], output_path: Path) -> None:
        """Write Docker Compose configuration to file."""
        from ..utils.helpers import format_yaml
        
        content = format_yaml(compose_config)
        self._write_file(output_path, content)
    
    def _write_env_file(self, builder: Any, env_file_path: Path) -> None:
        """Write environment variables to .env file."""
        env_vars = []
        
        # Extract environment variables from the builder
        if hasattr(builder, '_environment'):
            for key, value in builder._environment.items():
                env_vars.append(f"{key}={value}")
        
        # Add default environment variables
        env_vars.extend([
            "COMPOSE_PROJECT_NAME=k8s-gen-app",
            "COMPOSE_FILE=docker-compose.yml"
        ])
        
        content = "\n".join(env_vars)
        self._write_file(env_file_path, content)

    # ===== EXECUTION METHODS =====
    
    @docker_compose_only
    def run(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose command with the specified options.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional docker-compose options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        compose_path = self._get_compose_file_path(compose_file)
        command = self._build_docker_compose_command(compose_path, **options)
        
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Docker Compose command executed successfully: {' '.join(command)}")
            if result.stdout:
                print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing Docker Compose command: {e}")
            if e.stderr:
                print(f"Error output: {e.stderr}")
            raise
        
        return self
    
    @docker_compose_only
    def up(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose up.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options like detached, build, etc.
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="up", **options)
    
    @docker_compose_only
    def down(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose down.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options like volumes, remove-orphans, etc.
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="down", **options)
    
    @docker_compose_only
    def start(self, service: Optional[str] = None, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose start.
        
        Args:
            service: Specific service to start (optional)
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        if service:
            return self.run(compose_file, command="start", service=service, **options)
        return self.run(compose_file, command="start", **options)
    
    @docker_compose_only
    def stop(self, service: Optional[str] = None, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose stop.
        
        Args:
            service: Specific service to stop (optional)
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        if service:
            return self.run(compose_file, command="stop", service=service, **options)
        return self.run(compose_file, command="stop", **options)
    
    @docker_compose_only
    def restart(self, service: Optional[str] = None, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose restart.
        
        Args:
            service: Specific service to restart (optional)
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        if service:
            return self.run(compose_file, command="restart", service=service, **options)
        return self.run(compose_file, command="restart", **options)
    
    @docker_compose_only
    def logs(self, service: Optional[str] = None, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose logs.
        
        Args:
            service: Specific service to show logs for (optional)
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options like follow, tail, etc.
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        if service:
            return self.run(compose_file, command="logs", service=service, **options)
        return self.run(compose_file, command="logs", **options)
    
    @docker_compose_only
    def ps(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose ps.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="ps", **options)
    
    @docker_compose_only
    def build(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose build.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options like no-cache, pull, etc.
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="build", **options)
    
    @docker_compose_only
    def pull(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose pull.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="pull", **options)
    
    @docker_compose_only
    def exec(self, service: str, command: str, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose exec.
        
        Args:
            service: Service to execute command in
            command: Command to execute
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options like user, workdir, etc.
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="exec", service=service, exec_command=command, **options)
    
    @docker_compose_only
    def scale(self, services: Dict[str, int], compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose scale.
        
        Args:
            services: Dictionary of service names to replica counts
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        scale_args = []
        for service, replicas in services.items():
            scale_args.extend([service, str(replicas)])
        
        return self.run(compose_file, command="scale", scale_services=scale_args, **options)
    
    @docker_compose_only
    def config(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Run docker-compose config.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options like services, volumes, etc.
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="config", **options)
    
    @docker_compose_only
    def validate(self, compose_file: Optional[str] = None, **options) -> "DockerComposeOutput":
        """
        Validate docker-compose configuration.
        
        Args:
            compose_file: Path to docker-compose file (defaults to last generated)
            **options: Additional options
            
        Returns:
            DockerComposeOutput: Self for method chaining
        """
        return self.run(compose_file, command="config", quiet=True, **options)
    
    # ===== PRIVATE HELPER METHODS =====
    
    def _get_compose_file_path(self, compose_file: Optional[str] = None) -> Path:
        """
        Get the compose file path, using the last generated one if none specified.
        
        Args:
            compose_file: Optional compose file path
            
        Returns:
            Path: Path to the compose file
            
        Raises:
            ValueError: If no compose file path is available
        """
        if compose_file:
            return Path(compose_file)
        elif self._last_compose_file:
            return self._last_compose_file
        else:
            raise ValueError("No compose file specified and no file was previously generated. Call generate() first or specify a compose_file path.")
    
    def _build_docker_compose_command(self, compose_path: Path, **options) -> List[str]:
        """
        Build the docker-compose command with options.
        
        Args:
            compose_path: Path to the compose file
            **options: Command options
            
        Returns:
            List[str]: List of command arguments
        """
        command = ["docker-compose"]
        
        # Add compose file flag
        command.extend(["-f", str(compose_path)])
        
        # Extract the main command
        main_command = options.pop("command", "up")
        command.append(main_command)
        
        # Add service name if specified
        if "service" in options:
            command.append(options.pop("service"))
        
        # Add exec command if specified
        if "exec_command" in options:
            command.extend(options.pop("exec_command").split())
        
        # Add scale services if specified
        if "scale_services" in options:
            command.extend(options.pop("scale_services"))
        
        # Process boolean flags
        for key, value in options.items():
            if isinstance(value, bool) and value:
                # Handle special docker-compose flags
                if key == "d":
                    command.append("-d")
                else:
                    # Convert camelCase to kebab-case
                    flag = key.replace("_", "-")
                    if not flag.startswith("-"):
                        flag = f"--{flag}"
                    command.append(flag)
            elif isinstance(value, (str, int)):
                # Convert camelCase to kebab-case
                flag = key.replace("_", "-")
                if not flag.startswith("-"):
                    flag = f"--{flag}"
                command.extend([flag, str(value)])
        
        return command
    
    def _update_last_compose_file(self, compose_file: Union[str, Path]) -> None:
        """
        Update the last generated compose file path.
        
        Args:
            compose_file: Path to the compose file
        """
        self._last_compose_file = Path(compose_file) 