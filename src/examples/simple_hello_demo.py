"""
Simple Hello World Demo using Celestra.

This is a minimal demo that shows how to:
1. Create a hello world app
2. Generate Docker Compose
3. Run it with execution methods
"""

import sys
import os

# Add the current directory to the path to import from local source
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celestra.core.app import App
from celestra.output.docker_compose_output import DockerComposeOutput


def simple_hello_demo():
    """Simple hello world demo."""
    print("=== Simple Hello World Demo ===\n")
    
    # 1. Create a simple app
    print("1. Creating hello world app...")
    app = App("hello").image("hello-world:latest")
    print(f"   ✓ Created app: {app.name}")
    
    # 2. Generate Docker Compose
    print("\n2. Generating Docker Compose...")
    output = DockerComposeOutput()
    compose_file = "./hello-compose.yml"
    output.generate(app, compose_file)
    print(f"   ✓ Generated: {compose_file}")
    
    # 3. Show the file
    print("\n3. Generated file content:")
    if os.path.exists(compose_file):
        with open(compose_file, 'r') as f:
            print(f.read())
    
    # 4. Try to run it
    print("\n4. Running with execution methods...")
    try:
        # Pull image
        print("   - Pulling image...")
        output.pull()
        print("   ✓ Image pulled")
        
        # Start service
        print("   - Starting service...")
        output.up(d=True)
        print("   ✓ Service started")
        
        # Show status
        print("   - Service status:")
        output.ps()
        
        # Show logs
        print("   - Service logs:")
        output.logs()
        
        # Stop service
        print("   - Stopping service...")
        output.down()
        print("   ✓ Service stopped")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("   (This is expected if Docker is not running)")
    
    # 5. Cleanup
    print("\n5. Cleaning up...")
    if os.path.exists(compose_file):
        os.remove(compose_file)
        print("   ✓ Compose file removed")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    simple_hello_demo() 