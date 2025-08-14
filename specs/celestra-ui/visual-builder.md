# Celestra Visual Builder Specification

## 🎯 Overview

The Celestra Visual Builder is a web-based visual scripting IDE built with **Rete.js** that provides an intuitive interface for building complex Kubernetes and Docker Compose configurations. The design prioritizes **power without clutter** - every API feature is accessible but organized in a user-friendly way.

## 🏗️ Architecture

### **Technology Stack**
- **Frontend**: React + TypeScript + Rete.js
- **Backend**: FastAPI + Celestra Engine
- **State Management**: Zustand
- **Styling**: Tailwind CSS + Headless UI
- **Real-time**: WebSocket for live collaboration

### **Core Components**
```
┌─────────────────────────────────────────────────────────────┐
│                    Celestra Visual IDE                      │
├─────────────────────────────────────────────────────────────┤
│  📦 Component Library  │  🎯 Canvas (Rete.js)             │
│  ├─ App               │  ┌─────────────────────────────────┐   │
│  ├─ Service           │  │  [App: "web-app"]              │   │
│  ├─ Ingress           │  │  ├─ Image: nginx:latest        │   │
│  ├─ Secret            │  │  ├─ Port: 8080                 │   │
│  └─ ConfigMap         │  │  └─ Storage: 10Gi              │   │
│                        │  └─────────────────────────────────┘   │
│  🔧 Properties Panel  │  [Service: "web-service"]              │
│  ├─ Basic Config      │  ├─ Type: ClusterIP                   │
│  ├─ Advanced Config  │  └─ Port: 8080                       │
│  └─ Validation       │                                         │
├─────────────────────────────────────────────────────────────┤
│  🚀 Deployment Panel │  📝 Generated DSL Code                │
│  ├─ Deploy K8s       │  ```python                           │
│  ├─ Deploy Docker    │  app = App("web-app")                │
│  ├─ Validate         │      .image("nginx:latest")           │
│  └─ Export           │      .port(8080)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Node Design Principles

### **1. Progressive Disclosure**
- **Basic Properties**: Always visible (name, image, port)
- **Advanced Properties**: Expandable sections
- **Expert Properties**: Collapsible advanced panels

### **2. Visual Hierarchy**
- **Primary Actions**: Large, prominent buttons
- **Secondary Actions**: Medium-sized controls
- **Tertiary Options**: Small, subtle controls

### **3. Context-Aware UI**
- **Smart Defaults**: Pre-filled based on context
- **Conditional Fields**: Show/hide based on selections
- **Validation**: Real-time feedback and suggestions

### **4. Smart Comboboxes**
- **Error Prevention**: No typos in common values
- **Standardization**: Consistent configurations
- **Faster Input**: Quick selection vs. typing
- **Best Practices**: Industry-standard values
- **Flexibility**: "Custom..." option for overrides

### **5. Dynamic Input System**
When users select "Custom..." from any dropdown, the UI dynamically presents an appropriate input field:

```
┌─────────────────────────────────────────────────────────────┐
│                    Dynamic Input Examples                   │
├─────────────────────────────────────────────────────────────┤
│  🔄 Replicas: [Custom...] [number-input] [↩️ Revert]     │
│     💡 Enter any positive number: 25, 100, 1000           │
│                                                             │
│  💾 Storage: [Custom...] [text-input] [↩️ Revert]         │
│     💡 Enter storage with units: 500Mi, 2.5Gi, 1Ti       │
│                                                             │
│  🌐 Port: [Custom...] [number-input] [↩️ Revert]          │
│     💡 Enter port number: 8080, 9000, 10000               │
│                                                             │
│  ⏰ Schedule: [Custom...] [text-input] [↩️ Revert]         │
│     💡 Enter cron expression: "*/5 * * * *"                │
└─────────────────────────────────────────────────────────────┘
```

**Input Type Detection:**
- **Numeric Properties**: Show number input with min/max validation
- **Storage Properties**: Show text input with Kubernetes format validation  
- **Port Properties**: Show number input with range validation (1024-65535)
- **Time Properties**: Show text input with cron/ISO format validation

**Real-time Validation:**
- ✅ **Valid Input**: Green border, no error message
- ❌ **Invalid Input**: Red border, helpful error message
- 💡 **Smart Suggestions**: Context-aware recommendations
- ↩️ **Revert Option**: Easy return to predefined options

## 🧩 Node Types & Design

### **App Node (Main Application)**
```
┌─────────────────────────────────────────────────────────────┐
│  📱 App: web-app                                           │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [web-app]                    🔄 Replicas: [dropdown]│
│  🐳 Image: [nginx:latest]              💾 Storage: [dropdown]│
│  🌐 Port: [dropdown]                     🏷️  Labels: [Add]  │
│                                         🔧 Advanced [▼]    │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Volume] [➕ Add Secret] [➕ Add Config]│
└─────────────────────────────────────────────────────────────┘
```

**Smart Comboboxes:**
- **Replicas**: `1`, `2`, `3`, `5`, `10`, `Custom...`
- **Storage**: `1Gi`, `5Gi`, `10Gi`, `20Gi`, `50Gi`, `100Gi`, `Custom...`
- **Port**: `80`, `443`, `8080`, `3000`, `5000`, `Custom...`

**Dynamic Input Behavior:**
When "Custom..." is selected, the UI dynamically shows an appropriate input field:
- **Replicas**: Shows number input with validation (1-1000)
- **Storage**: Shows text input with format validation (Ki, Mi, Gi, Ti)
- **Port**: Shows number input with range validation (1024-65535)

**Advanced Panel (Collapsible):**
```
🔧 Advanced Configuration
├─ Resource Limits
│  ├─ CPU: [1000m] [2000m]
│  └─ Memory: [512Mi] [1Gi]
├─ Security Context
│  ├─ Run as User: [1000]
│  └─ Read-only Root: [☑️]
└─ Health Checks
    ├─ Liveness: [/health] [30s]
    └─ Readiness: [/ready] [5s]
```

### **Service Node (Kubernetes Service)**
```
┌─────────────────────────────────────────────────────────────┐
│  🔌 Service: web-service                                   │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [web-service]              🎯 Type: [dropdown] │
│  🔗 Selector: [app=web-app]           🌐 Port: [dropdown] │
│  📡 Target Port: [dropdown]           🔧 Advanced [▼]     │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Endpoint] [➕ Add Annotation]         │
└─────────────────────────────────────────────────────────────┘
```

**Smart Comboboxes:**
- **Type**: `ClusterIP`, `NodePort`, `LoadBalancer`, `ExternalName`
- **Port**: `80`, `443`, `8080`, `3000`, `5000`, `Custom...`
- **Target Port**: `80`, `443`, `8080`, `3000`, `5000`, `Custom...`

### **Ingress Node (Kubernetes Ingress)**
```
┌─────────────────────────────────────────────────────────────┐
│  🌐 Ingress: web-ingress                                   │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [web-ingress]            🏠 Host: [example.com] │
│  🛣️  Path: [/] → [web-service:8080]  🔒 TLS: [Add]         │
│  🎨 Class: [dropdown]                 🔧 Advanced [▼]       │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Path] [➕ Add Host] [➕ Add Rule] [➕ Add TLS]       │
└─────────────────────────────────────────────────────────────┘
```

**Smart Comboboxes:**
- **Class**: `nginx`, `traefik`, `haproxy`, `istio`, `Custom...`

## 🔄 Flow Direction & Connections

### **Connection Types**
```
┌─────────────────────────────────────────────────────────────┐
│                    Connection Semantics                     │
├─────────────────────────────────────────────────────────────┤
│  🔗 Depends On: [App] ──→ [Service]                       │
│     Service depends on App being deployed first            │
│                                                             │
│  🌐 Exposes: [App] ──→ [Ingress]                           │
│     Ingress exposes the App through Service                │
│                                                             │
│  🔐 Configures: [Secret] ──→ [App]                        │
│     Secret provides configuration to App                   │
│                                                             │
│  💾 Stores: [ConfigMap] ──→ [App]                         │
│     ConfigMap provides data to App                         │
└─────────────────────────────────────────────────────────────┘
```

### **Visual Flow Indicators**
- **Solid Lines**: Direct dependencies
- **Dashed Lines**: Optional relationships
- **Color Coding**: 
  - 🟢 Green: Healthy/Ready
  - 🟡 Yellow: Warning/Configuring
  - 🔴 Red: Error/Invalid
  - 🔵 Blue: Information/Neutral

## 🚀 Deployment Integration

### **Deploy Button States**
```
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Panel                         │
├─────────────────────────────────────────────────────────────┤
│  🚀 Deploy to Kubernetes                                   │
│  ├─ [🔍 Validate] [📦 Build] [🚀 Deploy] [📊 Monitor]     │
│  └─ Status: [✅ Ready] [🔄 Deploying] [❌ Failed]          │
│                                                             │
│  🐳 Deploy to Docker Compose                               │
│  ├─ [🔍 Validate] [📦 Build] [🚀 Deploy] [📊 Monitor]     │
│  └─ Status: [✅ Ready] [🔄 Deploying] [❌ Failed]          │
└─────────────────────────────────────────────────────────────┘
```

### **Real-time Deployment Flow**
```
1. 🔍 Validation
   ├─ Check node configurations
   ├─ Validate connections
   └─ Verify resource requirements

2. 📦 Build
   ├─ Generate Celestra DSL
   ├─ Convert to target format
   └─ Prepare deployment package

3. 🚀 Deploy
   ├─ Execute kubectl/docker-compose
   ├─ Monitor deployment progress
   └─ Handle rollbacks if needed

4. 📊 Monitor
   ├─ Watch pod/service status
   ├─ Check health endpoints
   └─ Display real-time metrics
```

## 🎯 Rete.js Integration

### **Node Registration**
```typescript
import { ClassicPreset } from 'rete';

// Register all Celestra node types
const nodeTypes = {
  'celestra-app': AppNode,
  'celestra-service': ServiceNode,
  'celestra-ingress': IngressNode,
  'celestra-secret': SecretNode,
  'celestra-configmap': ConfigMapNode,
  'celestra-statefulapp': StatefulAppNode,
  'celestra-job': JobNode,
  'celestra-cronjob': CronJobNode,
  'celestra-networkpolicy': NetworkPolicyNode,
  'celestra-rbac': RBACNode
};
```

### **Real-time Code Generation**
```typescript
class CelestraCodeGenerator {
  generateCode(nodes: Node[], connections: Connection[]) {
    let code = '';
    
    // Generate imports based on used nodes
    const imports = this.detectImports(nodes);
    code += imports.map(imp => `from celestra import ${imp}`).join('\n');
    code += '\n\n';
    
    // Generate component definitions
    nodes.forEach(node => {
      code += this.generateNodeCode(node);
    });
    
    // Generate connections and dependencies
    code += this.generateConnectionsCode(connections);
    
    // Generate output generation
    code += this.generateOutputCode();
    
    return code;
  }
}
```

## 🎨 UI/UX Guidelines

### **Color Scheme**
- **Primary**: Blue (#3B82F6) - Main actions
- **Success**: Green (#10B981) - Success states
- **Warning**: Yellow (#F59E0B) - Warnings
- **Error**: Red (#EF4444) - Errors
- **Neutral**: Gray (#6B7280) - Information

### **Typography**
- **Headers**: Inter, 18-24px, Semi-bold
- **Body**: Inter, 14-16px, Regular
- **Code**: JetBrains Mono, 13px, Regular
- **Labels**: Inter, 12px, Medium

### **Spacing**
- **Small**: 4px (0.25rem)
- **Medium**: 8px (0.5rem)
- **Large**: 16px (1rem)
- **Extra Large**: 24px (1.5rem)

### **Responsive Design**
- **Desktop**: Full feature set, side-by-side panels
- **Tablet**: Collapsible panels, touch-friendly controls
- **Mobile**: Stacked layout, simplified controls

## 🔧 Advanced Features

### **Template System**
```
┌─────────────────────────────────────────────────────────────┐
│                    Template Library                         │
├─────────────────────────────────────────────────────────────┤
│  📚 Pre-built Templates                                    │
│  ├─ 🖥️  Web Application (App + Service + Ingress)         │
│  ├─ 🗄️  Database (StatefulApp + Service + ConfigMap)      │
│  ├─ 🔐 Secure App (App + Secret + RBAC)                   │
│  └─ 📊 Monitoring (App + Service + Observability)          │
│                                                             │
│  💾 Save Current as Template                               │
│  [Save Template] [Share Template] [Export Template]        │
└─────────────────────────────────────────────────────────────┘
```

### **Validation Engine**
```
┌─────────────────────────────────────────────────────────────┐
│                    Validation Panel                         │
├─────────────────────────────────────────────────────────────┤
│  ✅ Configuration Valid                                     │
│  ⚠️  2 Warnings                                            │
│  ❌ 1 Error                                                │
│                                                             │
│  📋 Issues:                                                │
│  ├─ ⚠️  App 'web-app' has no health checks                 │
│  ├─ ⚠️  Service 'web-service' has no selector              │
│  └─ ❌  Ingress 'web-ingress' has invalid host format      │
└─────────────────────────────────────────────────────────────┘
```

### **Collaboration Features**
- **Real-time editing** with multiple users
- **Comment system** on nodes and connections
- **Version control** integration
- **Change tracking** and approval workflows

## 🚀 Implementation Roadmap

### **Phase 1: Core Builder (Month 1-2)**
- Basic Rete.js integration
- Core node types (App, Service, Ingress)
- Real-time code generation
- Basic validation

### **Phase 2: Advanced Features (Month 3-4)**
- All Celestra node types
- Advanced configuration panels
- Template system
- Enhanced validation

### **Phase 3: Deployment (Month 5-6)**
- Kubernetes deployment integration
- Docker Compose deployment
- Real-time monitoring
- Rollback capabilities

### **Phase 4: Enterprise (Month 7-8)**
- Collaboration features
- GitOps integration
- Advanced templates
- Performance optimization

## 🎯 Success Metrics

- **Usability**: 90% of users can create basic deployments in <5 minutes
- **Power**: Support 100% of Celestra API features
- **Performance**: Generate and deploy in <30 seconds
- **Adoption**: 50% of Celestra users prefer visual interface over DSL

This design balances **power with simplicity** - every API feature is accessible through intuitive, progressive disclosure while maintaining a clean, uncluttered interface that makes complex deployments feel simple and visual! 🎨✨ 