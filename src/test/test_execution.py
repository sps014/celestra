"""
Test execution capabilities of output classes.

This module tests the execution methods added to DockerComposeOutput and KubernetesOutput.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from celestra import App, StatefulApp
from celestra.output.docker_compose_output import DockerComposeOutput
from celestra.output.kubernetes_output import KubernetesOutput


class TestDockerComposeExecution:
    """Test Docker Compose execution methods."""
    
    def test_docker_compose_execution_methods_exist(self):
        """Test that all execution methods exist on DockerComposeOutput."""
        output = DockerComposeOutput()
        
        # Check that execution methods exist
        assert hasattr(output, 'run')
        assert hasattr(output, 'up')
        assert hasattr(output, 'down')
        assert hasattr(output, 'start')
        assert hasattr(output, 'stop')
        assert hasattr(output, 'restart')
        assert hasattr(output, 'logs')
        assert hasattr(output, 'ps')
        assert hasattr(output, 'build')
        assert hasattr(output, 'pull')
        assert hasattr(output, 'exec')
        assert hasattr(output, 'scale')
        assert hasattr(output, 'config')
        assert hasattr(output, 'validate')
    
    def test_docker_compose_run_without_generated_file(self):
        """Test that run() raises error when no file was generated."""
        output = DockerComposeOutput()
        
        with pytest.raises(ValueError, match="No compose file specified and no file was previously generated"):
            output.run()
    
    def test_docker_compose_run_with_specified_file(self):
        """Test that run() works with specified compose file."""
        output = DockerComposeOutput()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("version: '3.8'\nservices:\n  test:\n    image: nginx:latest")
            compose_file = f.name
        
        try:
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                output.run(compose_file, command="up")
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "docker-compose"
                assert args[1] == "-f"
                assert args[2] == compose_file
                assert args[3] == "up"
        finally:
            os.unlink(compose_file)
    
    def test_docker_compose_method_chaining(self):
        """Test that execution methods support method chaining."""
        output = DockerComposeOutput()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write("version: '3.8'\nservices:\n  test:\n    image: nginx:latest")
            compose_file = f.name
        
        try:
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                
                # Test method chaining
                result = output.up(compose_file, detached=True)
                assert result is output
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert "--detached" in args
        finally:
            os.unlink(compose_file)
    
    def test_docker_compose_generate_and_run(self):
        """Test generate() followed by execution methods."""
        output = DockerComposeOutput()
        app = App("test-app").image("nginx:latest").port(8080)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            compose_file = os.path.join(temp_dir, "docker-compose.yml")
            
            # Generate the compose file
            output.generate(app, compose_file)
            
            # Now run execution methods
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                output.up()
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "docker-compose"
                assert args[1] == "-f"
                assert args[2] == compose_file
                assert args[3] == "up"


class TestKubernetesExecution:
    """Test Kubernetes execution methods."""
    
    def test_kubernetes_execution_methods_exist(self):
        """Test that all execution methods exist on KubernetesOutput."""
        output = KubernetesOutput()
        
        # Check that execution methods exist
        assert hasattr(output, 'run')
        assert hasattr(output, 'apply')
        assert hasattr(output, 'delete')
        assert hasattr(output, 'replace')
        assert hasattr(output, 'patch')
        assert hasattr(output, 'get')
        assert hasattr(output, 'describe')
        assert hasattr(output, 'edit')
        assert hasattr(output, 'logs')
        assert hasattr(output, 'port_forward')
        assert hasattr(output, 'exec')
        assert hasattr(output, 'scale')
        assert hasattr(output, 'rollout')
        assert hasattr(output, 'status')
        assert hasattr(output, 'health')
        assert hasattr(output, 'events')
        assert hasattr(output, 'validate')
        assert hasattr(output, 'diff')
    
    def test_kubernetes_run_without_generated_dir(self):
        """Test that run() raises error when no directory was generated."""
        output = KubernetesOutput()
        
        with pytest.raises(ValueError, match="No resources directory specified and no directory was previously generated"):
            output.run("apply")
    
    def test_kubernetes_run_with_specified_dir(self):
        """Test that run() works with specified resources directory."""
        output = KubernetesOutput()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy manifest file
            manifest_file = os.path.join(temp_dir, "test.yaml")
            with open(manifest_file, 'w') as f:
                f.write("apiVersion: v1\nkind: Pod\nmetadata:\n  name: test")
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                output.run("apply", temp_dir)
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "kubectl"
                assert args[1] == "apply"
                assert args[2] == "-f"
                assert args[3] == temp_dir
    
    def test_kubernetes_method_chaining(self):
        """Test that execution methods support method chaining."""
        output = KubernetesOutput()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy manifest file
            manifest_file = os.path.join(temp_dir, "test.yaml")
            with open(manifest_file, 'w') as f:
                f.write("apiVersion: v1\nkind: Pod\nmetadata:\n  name: test")
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                
                # Test method chaining
                result = output.apply(temp_dir, namespace="test", wait=True)
                assert result is output
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "kubectl"
                assert "-n" in args
                assert "test" in args
                assert "apply" in args
                assert "--wait" in args
                assert "-f" in args
                assert temp_dir in args
    
    def test_kubernetes_generate_and_apply(self):
        """Test generate() followed by execution methods."""
        output = KubernetesOutput()
        app = App("test-app").image("nginx:latest").port(8080)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Generate the Kubernetes manifests
            output.generate(app, temp_dir)
            
            # Now run execution methods
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                output.apply()
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "kubectl"
                assert "apply" in args
                assert "-f" in args
                assert temp_dir in args
    
    def test_kubernetes_command_building(self):
        """Test that kubectl commands are built correctly with options."""
        output = KubernetesOutput()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy manifest file
            manifest_file = os.path.join(temp_dir, "test.yaml")
            with open(manifest_file, 'w') as f:
                f.write("apiVersion: v1\nkind: Pod\nmetadata:\n  name: test")
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="Success", stderr="")
                
                # Test various options
                output.apply(
                    temp_dir,
                    namespace="test-namespace",
                    wait=True,
                    timeout=300,
                    dry_run="client"
                )
                
                mock_run.assert_called_once()
                args = mock_run.call_args[0][0]
                assert args[0] == "kubectl"
                assert "-n" in args
                assert "test-namespace" in args
                assert "apply" in args
                assert "--wait" in args
                assert "--timeout" in args
                assert "300" in args
                assert "--dry-run" in args
                assert "client" in args
                assert "-f" in args
                assert temp_dir in args


if __name__ == "__main__":
    pytest.main([__file__]) 