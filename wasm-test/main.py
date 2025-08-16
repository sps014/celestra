from pyscript import document
from celestra.core.app import App
import os

def generate_k8s_manifests(event):
    """Generate Dockerfile using your actual Celestra App class"""
    
    # Get values from form
    app_name = document.querySelector("#app-name").value
    base_image = document.querySelector("#base-image").value
    app_port = document.querySelector("#app-port").value
    
    # Use your actual Celestra App class
    app = App(app_name).image(base_image).port(int(app_port))
    
    # Generate simple Dockerfile
    path = "./k8s/"
    app.generate().to_yaml(path)
    
    # read the k8s directory
    k8s_files = os.listdir(path)

    outputText = ""
    # read the k8s files
    for file in k8s_files:
        with open(os.path.join(path, file), "r") as f:
            outputText += f.read()
        
        outputText += "\n"
            
    

    
    # Show output
    output = document.querySelector("#output")
    print(outputText,end="\n")
    output.innerText = outputText
