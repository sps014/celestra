# 🐳 Celestra DSL - PyScript Dockerfile Generator

A simple PyScript application that demonstrates your Celestra DSL running in the browser.

## 📁 Files

- **`pyscript.json`** - PyScript configuration (specifies `celestra` package)
- **`index.html`** - HTML interface with form inputs
- **`main.py`** - Python code using your Celestra DSL

## 🚀 How to Run

### Option 1: Local Development Server
```bash
# Navigate to the wasm-test folder
cd wasm-test

# Start a local server
python -m http.server 8000

# Open in browser
# http://localhost:8000
```

### Option 2: GitHub Pages
1. Push these files to a GitHub repository
2. Enable GitHub Pages in repository settings
3. Get a free URL like: `https://username.github.io/repo-name`

### Option 3: Any Static Hosting
- Netlify, Vercel, or any static file hosting service

## 🎯 What It Does

1. **User Input**: App name, base image, port
2. **Celestra DSL**: Uses your actual `App` class from PyPI
3. **Dockerfile Generation**: Creates a Dockerfile based on the configuration
4. **Browser Output**: Shows the generated Dockerfile in the browser

## 🔧 How It Works

- **PyScript**: Runs Python in the browser using WebAssembly
- **Celestra Package**: Imports your actual package from PyPI
- **Real DSL**: Uses your actual `App.image()` and `App.port()` methods
- **No Backend**: Everything runs in the browser

## 💡 Example Usage

1. Enter app name: `my-webapp`
2. Enter base image: `nginx:alpine`
3. Enter port: `80`
4. Click "Generate Dockerfile"
5. See the generated Dockerfile using your Celestra DSL!

## 🌟 Benefits

- **Zero Backend Costs**: Runs entirely in browser
- **Real Celestra**: Uses your actual package, not a mock
- **Professional**: Same API as your Python package
- **Deployable**: Can be hosted anywhere for free
