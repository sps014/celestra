"""
Hello World Docker Demo using Celestra.

This example demonstrates how to:
1. Define a simple hello world application
2. Generate Docker Compose configuration
3. Run the application using execution methods
4. Show logs and status
5. Clean up resources
"""

import sys
import os
import time
from pathlib import Path

# Add the current directory to the path to import from local source
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celestra.core.app import App
from celestra.output.docker_compose_output import DockerComposeOutput


def hello_world_docker_demo():
    """Run a hello world Docker application using Celestra."""
    print("=== Hello World Docker Demo ===\n")
    
    # Step 1: Define the hello world application
    print("1. Defining Hello World Application...")
    hello_app = (App("hello-world")
        .image("hello-world:latest")  # Official Docker hello-world image
        .port(8080)  # Expose port (though hello-world doesn't use it)
        .environment({
            "GREETING": "Hello from Celestra!",
            "VERSION": "1.0.0"
        })
        .resources(
            cpu="100m",
            memory="128Mi"
        ))
    
    print("   ✓ Application defined:")
    print(f"      - Name: {hello_app.name}")
    print(f"      - Image: hello-world:latest")
    print(f"      - Port: 8080")
    print(f"      - Environment: {{'GREETING': 'Hello from Celestra!', 'VERSION': '1.0.0'}}")
    
    # Step 2: Create Docker Compose output and generate configuration
    print("\n2. Generating Docker Compose Configuration...")
    docker_output = DockerComposeOutput()
    
    # Set options for better development experience
    docker_output.set_options({
        "include_volumes": True,
        "add_health_checks": True,
        "add_dependencies": True,
        "generate_env_file": True,
        "restart_policy": "unless-stopped"
    })
    
    # Generate the compose file
    compose_file = "./hello-world-compose.yml"
    docker_output.generate(hello_app, compose_file)
    print(f"   ✓ Generated: {compose_file}")
    
    # Step 3: Show the generated configuration
    print("\n3. Generated Docker Compose Configuration:")
    if os.path.exists(compose_file):
        with open(compose_file, 'r') as f:
            content = f.read()
            print("   Content:")
            print("   " + "="*50)
            for line in content.split('\n'):
                if line.strip():
                    print(f"   {line}")
            print("   " + "="*50)
    
    # Step 4: Run the application
    print("\n4. Running Hello World Application...")
    
    try:
        # Pull the image first
        print("   - Pulling hello-world image...")
        docker_output.pull()
        print("   ✓ Image pulled successfully")
        
        # Start the service
        print("   - Starting hello-world service...")
        docker_output.up(d=True)  # Use -d flag for docker-compose
        print("   ✓ Service started successfully")
        
        # Wait a moment for the service to start
        print("   - Waiting for service to start...")
        time.sleep(3)
        
        # Show service status
        print("   - Checking service status...")
        docker_output.ps()
        print("   ✓ Status retrieved")
        
        # Show logs
        print("   - Showing service logs...")
        docker_output.logs(tail=20)
        print("   ✓ Logs retrieved")
        
        # Show running containers
        print("   - Showing running containers...")
        docker_output.ps()
        print("   ✓ Container status shown")
        
        # Interactive mode - let user see the logs
        print("\n5. Application is running! Press Enter to continue...")
        input()
        
    except Exception as e:
        print(f"   ✗ Error running application: {e}")
        print("   Note: This might be expected if Docker is not running or hello-world image is not available")
    
    # Step 5: Clean up
    print("\n6. Cleaning up resources...")
    try:
        # Stop the service
        print("   - Stopping hello-world service...")
        docker_output.down()
        print("   ✓ Service stopped successfully")
        
        # Remove the compose file
        if os.path.exists(compose_file):
            os.remove(compose_file)
            print("   ✓ Compose file removed")
            
    except Exception as e:
        print(f"   ✗ Error during cleanup: {e}")
    
    print("\n" + "="*50)
    print("Demo completed!")
    print("\nWhat we accomplished:")
    print("1. ✅ Defined a hello world application using Celestra DSL")
    print("2. ✅ Generated Docker Compose configuration automatically")
    print("3. ✅ Used execution methods to run Docker commands")
    print("4. ✅ Managed the application lifecycle (start, logs, status, stop)")
    print("5. ✅ Cleaned up resources automatically")
    print("\nKey benefits demonstrated:")
    print("- No manual YAML writing required")
    print("- Consistent API for Docker operations")
    print("- Automatic resource management")
    print("- Clean, readable Python code")


def hello_world_with_custom_image():
    """Alternative demo using a custom hello world image."""
    print("\n=== Alternative: Custom Hello World Image ===\n")
    
    # Define a custom hello world app
    custom_app = (App("custom-hello")
        .image("busybox:latest")  # Use busybox for a simple hello world
        .environment({
            "MESSAGE": "Welcome to Celestra Docker execution!",
            "TIMESTAMP": str(int(time.time()))
        }))
    
    print("1. Custom Hello World Application:")
    print(f"   - Name: {custom_app.name}")
    print(f"   - Image: busybox:latest")
    print(f"   - Environment: {{'MESSAGE': 'Welcome to Celestra Docker execution!', 'TIMESTAMP': '{str(int(time.time()))}'}}")
    
    # Generate and run
    docker_output = DockerComposeOutput()
    compose_file = "./custom-hello-compose.yml"
    
    try:
        print("\n2. Generating and running custom app...")
        docker_output.generate(custom_app, compose_file)
        
        # Run the custom app
        docker_output.up()
        print("   ✓ Custom app started")
        
        # Show logs
        print("   - Custom app logs:")
        docker_output.logs()
        
        # Wait for completion
        print("   - Waiting for app to complete...")
        time.sleep(15)
        
        # Show final logs
        print("   - Final logs:")
        docker_output.logs()
        
        # Clean up
        docker_output.down()
        if os.path.exists(compose_file):
            os.remove(compose_file)
        print("   ✓ Custom app cleaned up")
        
    except Exception as e:
        print(f"   ✗ Error with custom app: {e}")


def main():
    """Run the hello world Docker demo."""
    print("Celestra Hello World Docker Demo")
    print("=" * 60)
    print("\nThis demo shows how to run Docker containers using Celestra's execution methods.")
    print("Requirements:")
    print("- Docker must be running")
    print("- Internet connection to pull images")
    print("- Celestra library (using local source)\n")
    
    try:
        # Main demo
        hello_world_docker_demo()
        
        # Alternative demo
        hello_world_with_custom_image()
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        print("Cleaning up any running containers...")
        try:
            docker_output = DockerComposeOutput()
            docker_output.down()
        except:
            pass
        print("Demo stopped.")
    
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        print("This might be expected if Docker is not available.")


if __name__ == "__main__":
    main() 