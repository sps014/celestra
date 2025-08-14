# Celestra UI Component Library

## 🎯 Overview

The Component Library defines all visual nodes available in the Celestra Visual Builder. Each node represents a Celestra class and provides an intuitive interface for configuring all its properties while maintaining a clean, uncluttered appearance.

## 🏗️ Node Architecture

### **Base Node Structure**
```typescript
interface CelestraNode {
  id: string;
  type: 'celestra-app' | 'celestra-service' | 'celestra-ingress' | ...;
  position: { x: number; y: number };
  data: {
    name: string;
    properties: NodeProperties;
    connections: Connection[];
    validation: ValidationState;
  };
}
```

### **Property Organization**
```
┌─────────────────────────────────────────────────────────────┐
│                    Property Organization                     │
├─────────────────────────────────────────────────────────────┤
│  🎯 Basic Properties (Always Visible)                      │
│  ├─ Essential configuration (name, image, port)            │
│  ├─ Most commonly used settings                            │
│  └─ Required for basic functionality                        │
│                                                             │
│  🔧 Advanced Properties (Expandable)                       │
│  ├─ Performance tuning (resources, scaling)                │
│  ├─ Security settings (RBAC, policies)                     │
│  └─ Monitoring and health checks                           │
│                                                             │
│  ⚙️  Expert Properties (Collapsible)                       │
│  ├─ Low-level configurations                               │
│  ├─ Custom annotations and labels                          │
│  └─ Advanced networking and storage                        │
└─────────────────────────────────────────────────────────────┘
```

## 🧩 Core Application Nodes

### **1. App Node (`celestra-app`)**
**Purpose**: Main application container with basic configuration

**Basic Properties (Always Visible):**
```
┌─────────────────────────────────────────────────────────────┐
│  📱 App: {name}                                            │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]              🔄 Replicas: [dropdown]│
│  🐳 Image: [text-input]              💾 Storage: [dropdown]│
│  🌐 Port: [dropdown]                   🏷️  Labels: [button]  │
│                                         🔧 Advanced [▼]     │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Volume] [➕ Add Secret] [➕ Add Config]│
└─────────────────────────────────────────────────────────────┘
```

**Replicas Dropdown Options:**
- `"1"`, `"2"`, `"3"`, `"5"`, `"10"`, `"Custom..."`
**Port Dropdown Options:**
- `"80"`, `"443"`, `"8080"`, `"3000"`, `"5000"`, `"Custom..."`

**Storage Dropdown Options:**
- `"1Gi"`, `"5Gi"`, `"10Gi"`, `"20Gi"`, `"50Gi"`, `"100Gi"`, `"Custom..."`

**Advanced Properties (Expandable):**
```
🔧 Advanced Configuration
├─ Resource Management
│  ├─ CPU Request: [dropdown] [dropdown]
│  ├─ Memory Request: [dropdown] [dropdown]
│  └─ Storage Class: [dropdown]
├─ Security & Permissions
│  ├─ Service Account: [dropdown]
│  ├─ Security Context: [object]
│  └─ Pod Security Standards: [dropdown]
└─ Health & Monitoring
    ├─ Liveness Probe: [object]
    ├─ Readiness Probe: [object]
    └─ Startup Probe: [object]
```

**CPU Dropdown Options:**
- `"100m"`, `"250m"`, `"500m"`, `"1000m"`, `"2000m"`, `"4000m"`, `"Custom..."`
**Memory Dropdown Options:**
- `"128Mi"`, `"256Mi"`, `"512Mi"`, `"1Gi"`, `"2Gi"`, `"4Gi"`, `"8Gi"`, `"Custom..."`
**Storage Class Dropdown Options:**
- `"gp2"`, `"gp3"`, `"io1"`, `"io2"`, `"st1"`, `"sc1"`, `"standard"`, `"Custom..."`
**Pod Security Standards Dropdown Options:**
- `"privileged"`, `"baseline"`, `"restricted"`

**Expert Properties (Collapsible):**
```
⚙️ Expert Configuration
├─ Networking
│  ├─ Host Network: [boolean]
│  ├─ DNS Policy: [dropdown]
│  └─ Network Policies: [array]
├─ Storage
│  ├─ Volume Mounts: [array]
│  ├─ Persistent Volumes: [array]
│  └─ Empty Dirs: [array]
└─ Advanced
    ├─ Affinity Rules: [object]
    ├─ Tolerations: [array]
    └─ Topology Spread: [object]
```

**DNS Policy Dropdown Options:**
- `"ClusterFirst"`, `"Default"`, `"ClusterFirstWithHostNet"`, `"None"`

### **2. StatefulApp Node (`celestra-statefulapp`)**
**Purpose**: Stateful applications with persistent storage

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🗄️  StatefulApp: {name}                                   │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]              🔄 Replicas: [dropdown]│
│  🐳 Image: [text-input]              💾 Storage: [dropdown]│
│  🌐 Port: [dropdown]                  🔗 Headless: [toggle] │
│                                         🔧 Advanced [▼]     │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Volume] [➕ Add Secret] [➕ Add Config]│
└─────────────────────────────────────────────────────────────┘
```

**Replicas Dropdown Options:**
- `"1"`, `"3"`, `"5"`, `"7"`, `"Custom..."`
**Storage Dropdown Options:**
- `"1Gi"`, `"5Gi"`, `"10Gi"`, `"20Gi"`, `"50Gi"`, `"100Gi"`, `"Custom..."`
**Port Dropdown Options:**
- `"80"`, `"443"`, `"8080"`, `"3000"`, `"5000"`, `"6379"`, `"27017"`, `"Custom..."`

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ StatefulSet Specific
│  ├─ Update Strategy: [dropdown]
│  ├─ Partition: [dropdown]
│  └─ Pod Management Policy: [dropdown]
├─ Storage Management
│  ├─ Storage Class: [dropdown]
│  ├─ Access Modes: [dropdown]
│  └─ Mount Path: [dropdown]
└─ Backup & Recovery
    ├─ Backup Schedule: [dropdown]
    ├─ Retention Policy: [dropdown]
    └─ Backup Location: [dropdown]
```

**Update Strategy Dropdown Options:**
- `"RollingUpdate"`, `"OnDelete"`
**Partition Dropdown Options:**
- `"0"`, `"1"`, `"2"`, `"3"`, `"Custom..."`
**Pod Management Policy Dropdown Options:**
- `"OrderedReady"`, `"Parallel"`
**Storage Class Dropdown Options:**
- `"gp2"`, `"gp3"`, `"io1"`, `"io2"`, `"st1"`, `"sc1"`, `"standard"`, `"Custom..."`
**Access Modes Dropdown Options:**
- `"ReadWriteOnce"`, `"ReadOnlyMany"`, `"ReadWriteMany"`
**Mount Path Dropdown Options:**
- `"/data"`, `"/var/lib"`, `"/opt"`, `"/mnt"`, `"Custom..."`
**Backup Schedule Dropdown Options:**
- `"0 2 * * *"` (daily), `"0 2 * * 0"` (weekly), `"0 2 1 * *"` (monthly), `"Custom..."`
**Retention Policy Dropdown Options:**
- `"7 days"`, `"30 days"`, `"90 days"`, `"1 year"`, `"Forever"`
**Backup Location Dropdown Options:**
- `"S3"`, `"Azure Blob"`, `"GCS"`, `"Local"`, `"Custom..."`

### **3. Job Node (`celestra-job`)**
**Purpose**: One-time or batch processing jobs

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ Job: {name}                                            │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]              🔄 Parallelism: [num] │
│  🐳 Image: [text-input]              ✅ Completions: [num] │
│  🎯 Command: [array]                  ⏱️  Timeout: [text]  │
│                                         🔧 Advanced [▼]     │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Volume] [➕ Add Secret] [➕ Add Config]│
└─────────────────────────────────────────────────────────────┘
```

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Job Control
│  ├─ Restart Policy: [dropdown]
│  ├─ Backoff Limit: [dropdown]
│  └─ Active Deadline: [dropdown]
├─ Resource Management
│  ├─ CPU/Memory Limits: [object]
│  ├─ Storage Requirements: [object]
│  └─ GPU Requirements: [object]
└─ Scheduling
    ├─ Node Selector: [object]
    ├─ Affinity Rules: [object]
    └─ Tolerations: [array]
```

**Restart Policy Dropdown Options:**
- `"Never"`, `"OnFailure"`
**Backoff Limit Dropdown Options:**
- `"3"`, `"5"`, `"10"`, `"20"`, `"Custom..."`
**Active Deadline Dropdown Options:**
- `"30s"`, `"1m"`, `"5m"`, `"10m"`, `"30m"`, `"1h"`, `"Custom..."`

### **4. CronJob Node (`celestra-cronjob`)**
**Purpose**: Scheduled jobs with cron expressions

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  ⏰ CronJob: {name}                                        │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]              🕐 Schedule: [cron]   │
│  🐳 Image: [text-input]              🔄 Concurrency: [num] │
│  🎯 Command: [array]                  ⏸️  Suspend: [toggle] │
│                                         🔧 Advanced [▼]     │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Volume] [➕ Add Secret] [➕ Add Config]│
└─────────────────────────────────────────────────────────────┘
```

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Scheduling Control
│  ├─ Concurrency Policy: [dropdown]
│  ├─ Successful Jobs History: [dropdown]
│  └─ Failed Jobs History: [dropdown]
├─ Job Template
│  ├─ Job Spec: [object]
│  ├─ Pod Template: [object]
│  └─ Volume Templates: [array]
└─ Time Management
    ├─ Starting Deadline: [dropdown]
    ├─ Time Zone: [dropdown]
    └─ Last Schedule Time: [readonly]
```

**Concurrency Policy Dropdown Options:**
- `"Allow"`, `"Forbid"`, `"Replace"`
**Successful Jobs History Dropdown Options:**
- `"3"`, `"5"`, `"10"`, `"20"`, `"50"`, `"Custom..."`
**Failed Jobs History Dropdown Options:**
- `"1"`, `"3"`, `"5"`, `"10"`, `"Custom..."`
**Starting Deadline Dropdown Options:**
- `"30s"`, `"1m"`, `"5m"`, `"10m"`, `"30m"`, `"1h"`, `"Custom..."`
**Time Zone Dropdown Options:**
- `"UTC"`, `"America/New_York"`, `"Europe/London"`, `"Asia/Tokyo"`, `"Custom..."`

## 🌐 Networking Nodes

### **5. Service Node (`celestra-service`)**
**Purpose**: Expose applications within the cluster

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🔌 Service: {name}                                        │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]              🎯 Type: [dropdown]   │
│  🔗 Selector: [key-value]            🌐 Port: [dropdown]   │
│  📡 Target Port: [dropdown]          🔧 Advanced [▼]        │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Endpoint] [➕ Add Annotation]         │
└─────────────────────────────────────────────────────────────┘
```

**Service Type Dropdown Options:**
- `"ClusterIP"`, `"NodePort"`, `"LoadBalancer"`, `"ExternalName"`
**Port Dropdown Options:**
- `"80"`, `"443"`, `"8080"`, `"3000"`, `"5000"`, `"Custom..."`
**Target Port Dropdown Options:**
- `"80"`, `"443"`, `"8080"`, `"3000"`, `"5000"`, `"Custom..."`

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Service Configuration
│  ├─ Cluster IP: [dropdown]
│  ├─ External IPs: [array]
│  └─ Load Balancer IP: [text]
├─ Port Management
│  ├─ Port Mappings: [array]
│  ├─ Protocol: [dropdown]
│  └─ App Protocol: [dropdown]
└─ Advanced Networking
    ├─ Session Affinity: [dropdown]
    ├─ Sticky Sessions: [object]
    └─ External Traffic Policy: [dropdown]
```

**Cluster IP Dropdown Options:**
- `"None"`, `"10.0.0.1"`, `"10.0.0.10"`, `"Custom..."`
**Protocol Dropdown Options:**
- `"TCP"`, `"UDP"`, `"SCTP"`
**App Protocol Dropdown Options:**
- `"http"`, `"https"`, `"grpc"`, `"tcp"`, `"udp"`, `"Custom..."`
**Session Affinity Dropdown Options:**
- `"None"`, `"ClientIP"`
**External Traffic Policy Dropdown Options:**
- `"Cluster"`, `"Local"`

### **6. Ingress Node (`celestra-ingress`)**
**Purpose**: External access to services

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🌐 Ingress: {name}                                        │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            🏠 Host: [text]         │
│  🛣️  Path: [/] → [service:port]    🔒 TLS: [button]        │
│  🎨 Class: [dropdown]               🔧 Advanced [▼]         │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Path] [➕ Add Host] [➕ Add Rule] [➕ Add TLS]       │
└─────────────────────────────────────────────────────────────┘
```

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Routing Rules
│  ├─ Path Types: [dropdown]
│  ├─ Rewrite Rules: [array]
│  └─ Redirect Rules: [array]
├─ TLS Configuration
│  ├─ Secret Name: [dropdown]
│  ├─ Hosts: [array]
│  └─ Default Certificate: [boolean]
└─ Advanced Features
    ├─ Annotations: [key-value]
    ├─ Custom Headers: [array]
    └─ Rate Limiting: [object]
```

**Path Types Dropdown Options:**
- `"Exact"`, `"Prefix"`, `"ImplementationSpecific"`
**Secret Name Dropdown Options:**
- `"tls-secret"`, `"wildcard-secret"`, `"custom-secret"`, `"Create New..."`

### **7. NetworkPolicy Node (`celestra-networkpolicy`)**
**Purpose**: Control network traffic between pods

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🛡️  NetworkPolicy: {name}                                 │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            🎯 Pod Selector: [obj]  │
│  🔒 Policy Types: [array]          🌐 Ingress Rules: [arr] │
│  📤 Egress Rules: [array]          🔧 Advanced [▼]         │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Ingress Rule] [➕ Add Egress Rule] [➕ Add Exception]│
└─────────────────────────────────────────────────────────────┘
```

## 🔐 Security Nodes

### **8. Secret Node (`celestra-secret`)**
**Purpose**: Store sensitive data

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🔐 Secret: {name}                                         │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            🔒 Type: [dropdown]     │
│  📝 Data: [key-value]              🔧 Advanced [▼]         │
│  📁 Files: [file-upload]                                   │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Key] [➕ Add File] [➕ Add External Source]         │
└─────────────────────────────────────────────────────────────┘
```

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Data Sources
│  ├─ Environment Variables: [array]
│  ├─ External Sources: [dropdown]
│  └─ Generated Secrets: [dropdown]
├─ Mounting Options
│  ├─ Mount Path: [dropdown]
│  ├─ File Permissions: [dropdown]
│  └─ Sub Path: [text]
└─ Security
    ├─ Encryption: [dropdown]
    ├─ Rotation Policy: [dropdown]
    └─ Access Control: [array]
```

**External Sources Dropdown Options:**
- `"AWS Secrets Manager"`, `"Azure Key Vault"`, `"HashiCorp Vault"`, `"Google Secret Manager"`
**Generated Secrets Dropdown Options:**
- `"Random Password"`, `"SSH Key Pair"`, `"TLS Certificate"`, `"JWT Token"`
**Mount Path Dropdown Options:**
- `"/etc/secrets"`, `"/var/secrets"`, `"/app/secrets"`, `"/config/secrets"`, `"Custom..."`
**File Permissions Dropdown Options:**
- `"0400"`, `"0600"`, `"0640"`, `"0644"`, `"Custom..."`
**Encryption Dropdown Options:**
- `"AES-256"`, `"ChaCha20"`, `"RSA-2048"`, `"None"`
**Rotation Policy Dropdown Options:**
- `"30 days"`, `"60 days"`, `"90 days"`, `"180 days"`, `"Never"`

### **9. ConfigMap Node (`celestra-configmap`)**
**Purpose**: Store configuration data

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  💾 ConfigMap: {name}                                      │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            📝 Data: [key-value]    │
│  📁 Files: [file-upload]           🔄 Hot Reload: [toggle] │
│  📂 Directories: [folder-upload]   🔧 Advanced [▼]         │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Key] [➕ Add File] [➕ Add Directory] [➕ Add Template]│
└─────────────────────────────────────────────────────────────┘
```

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Configuration Sources
│  ├─ Key-Value Pairs: [array]
│  ├─ File Contents: [array]
│  ├─ Directory Contents: [array]
│  └─ Templates: [dropdown]
├─ Mounting & Usage
│  ├─ Mount Path: [dropdown]
│  ├─ Sub Path: [text]
│  └─ Default Mode: [dropdown]
└─ Advanced Features
    ├─ Hot Reload: [dropdown]
    ├─ Validation: [dropdown]
    └─ Transformation: [dropdown]
```

**Templates Dropdown Options:**
- `"Environment Config"`, `"Database Config"`, `"API Config"`, `"Custom Template"`
**Mount Path Dropdown Options:**
- `"/etc/config"`, `"/var/config"`, `"/app/config"`, `"/config"`, `"Custom..."`
**Default Mode Dropdown Options:**
- `"0644"`, `"0640"`, `"0600"`, `"0755"`, `"Custom..."`
**Hot Reload Dropdown Options:**
- `"Enabled"`, `"Disabled"`, `"Conditional"`
**Validation Dropdown Options:**
- `"JSON Schema"`, `"YAML Schema"`, `"Custom Validator"`, `"None"`
**Transformation Dropdown Options:**
- `"Environment Variables"`, `"JSON Path"`, `"Template Engine"`, `"None"`

## 🎛️ RBAC Nodes

### **10. ServiceAccount Node (`celestra-serviceaccount`)**
**Purpose**: Identity for pods

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  👤 ServiceAccount: {name}                                 │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            🔑 Secrets: [array]     │
│  🏷️  Labels: [key-value]           🔐 Image Pull: [array]  │
│  🔧 Advanced [▼]                                           │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Secret] [➕ Add Image Pull Secret] [➕ Add Annotation]│
└─────────────────────────────────────────────────────────────┘
```

### **11. Role/ClusterRole Node (`celestra-role`)**
**Purpose**: Define permissions

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🎭 Role: {name}                                           │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            📋 Rules: [array]       │
│  🏷️  Labels: [key-value]           🔧 Advanced [▼]         │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Rule] [➕ Add Label] [➕ Add Annotation]             │
└─────────────────────────────────────────────────────────────┘
```

**Advanced Properties:**
```
🔧 Advanced Configuration
├─ Permission Rules
│  ├─ API Groups: [dropdown]
│  ├─ Resources: [dropdown]
│  ├─ Verbs: [dropdown]
│  └─ Resource Names: [array]
├─ Aggregation
│  ├─ Cluster Role Selector: [object]
│  └─ Match Labels: [key-value]
└─ Metadata
    ├─ Annotations: [key-value]
    └─ Finalizers: [array]
```

**API Groups Dropdown Options:**
- `""` (core), `"apps"`, `"batch"`, `"networking.k8s.io"`, `"rbac.authorization.k8s.io"`, `"storage.k8s.io"`
**Resources Dropdown Options:**
- `"pods"`, `"services"`, `"deployments"`, `"configmaps"`, `"secrets"`, `"persistentvolumes"`, `"Custom..."`
**Verbs Dropdown Options:**
- `"get"`, `"list"`, `"watch"`, `"create"`, `"update"`, `"patch"`, `"delete"`, `"deletecollection"`

## 🚀 Advanced Feature Nodes

### **12. DeploymentStrategy Node (`celestra-deployment-strategy`)**
**Purpose**: Control how deployments are updated

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🚀 DeploymentStrategy: {name}                             │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            🎯 Type: [dropdown]     │
│  🔄 Strategy: [dropdown]            ⏱️  Timeout: [dropdown] │
│  🔧 Advanced [▼]                                           │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Rule] [➕ Add Condition] [➕ Add Hook]               │
└─────────────────────────────────────────────────────────────┘
```

**Type Dropdown Options:**
- `"RollingUpdate"`, `"Recreate"`, `"BlueGreen"`, `"Canary"`
**Strategy Dropdown Options:**
- `"RollingUpdate"`, `"Recreate"`
**Timeout Dropdown Options:**
- `"30s"`, `"1m"`, `"5m"`, `"10m"`, `"30m"`, `"1h"`, `"Custom..."`

### **13. Observability Node (`celestra-observability`)**
**Purpose**: Monitoring and logging configuration

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  📊 Observability: {name}                                  │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            📈 Metrics: [dropdown]  │
│  📝 Logging: [dropdown]             🔍 Tracing: [dropdown] │
│  🚨 Alerts: [dropdown]              🔧 Advanced [▼]        │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Metric] [➕ Add Log] [➕ Add Alert] [➕ Add Dashboard]│
└─────────────────────────────────────────────────────────────┘
```

**Metrics Dropdown Options:**
- `"Prometheus"`, `"Custom Metrics"`, `"None"`
**Logging Dropdown Options:**
- `"Fluentd"`, `"ELK Stack"`, `"Custom Logger"`, `"None"`
**Tracing Dropdown Options:**
- `"Jaeger"`, `"Zipkin"`, `"OpenTelemetry"`, `"None"`
**Alerts Dropdown Options:**
- `"Prometheus AlertManager"`, `"Custom Alerts"`, `"None"`

### **14. AppGroup Node (`celestra-appgroup`)**
**Purpose**: Group multiple applications together

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🏗️  AppGroup: {name}                                      │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            🎯 Environment: [dropdown]│
│  🔄 Replicas: [dropdown]            🌍 Namespace: [dropdown]│
│  📊 Resource Quotas: [dropdown]     🔧 Advanced [▼]         │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add App] [➕ Add Service] [➕ Add Config] [➕ Add Secret]│
└─────────────────────────────────────────────────────────────┘
```

**Environment Dropdown Options:**
- `"development"`, `"staging"`, `"production"`, `"testing"`
**Replicas Dropdown Options:**
- `"1"`, `"2"`, `"3"`, `"5"`, `"10"`, `"Custom..."`
**Namespace Dropdown Options:**
- `"default"`, `"kube-system"`, `"monitoring"`, `"logging"`, `"Create New..."`
**Resource Quotas Dropdown Options:**
- `"Small"`, `"Medium"`, `"Large"`, `"Enterprise"`, `"Custom..."`

### **15. CustomResource Node (`celestra-customresource`)**
**Purpose**: Define custom Kubernetes resources

**Basic Properties:**
```
┌─────────────────────────────────────────────────────────────┐
│  🔧 CustomResource: {name}                                 │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [text-input]            📋 API Version: [dropdown]│
│  🎯 Kind: [dropdown]                🔍 Scope: [dropdown]   │
│  📝 Schema: [object]                 🔧 Advanced [▼]        │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Field] [➕ Add Validation] [➕ Add Printer Column]   │
└─────────────────────────────────────────────────────────────┘
```

**API Version Dropdown Options:**
- `"v1"`, `"v1alpha1"`, `"v1beta1"`, `"v2"`, `"Custom..."`
**Kind Dropdown Options:**
- `"CustomApp"`, `"Database"`, `"Cache"`, `"Queue"`, `"Custom..."`
**Scope Dropdown Options:**
- `"Namespaced"`, `"Cluster"`

## 🎨 Node Styling & Visual Design

### **Color Coding by Category**
- **🟦 Blue**: Application nodes (App, StatefulApp, Job, CronJob)
- **🟩 Green**: Networking nodes (Service, Ingress, NetworkPolicy)
- **🟨 Yellow**: Security nodes (Secret, ConfigMap)
- **🟪 Purple**: RBAC nodes (ServiceAccount, Role, ClusterRole)
- **🟧 Orange**: Advanced feature nodes (DeploymentStrategy, Observability)
- **🟫 Brown**: Grouping nodes (AppGroup)
- **🟥 Red**: Custom resource nodes (CustomResource)

### **Icon System**
- **📱 App**: Smartphone icon for applications
- **🗄️ StatefulApp**: Database icon for stateful apps
- **⚡ Job**: Lightning bolt for jobs
- **⏰ CronJob**: Clock for scheduled jobs
- **🔌 Service**: Plug for services
- **🌐 Ingress**: Globe for ingress
- **🛡️ NetworkPolicy**: Shield for security
- **🔐 Secret**: Lock for secrets
- **💾 ConfigMap**: Floppy disk for config
- **👤 ServiceAccount**: Person for identity
- **🎭 Role**: Theater mask for roles
- **🚀 DeploymentStrategy**: Rocket for deployment
- **📊 Observability**: Chart for monitoring
- **🏗️ AppGroup**: Building icon for application groups
- **🔧 CustomResource**: Wrench icon for custom resources

### **Size & Layout**
- **Compact Mode**: Minimal properties, expandable panels
- **Standard Mode**: Balanced view of basic and advanced

## 🎯 **Combobox Implementation Summary**

### **Why Comboboxes?**
✅ **Prevent Errors**: No more typos in common values  
✅ **Standardize Values**: Consistent configurations across projects  
✅ **Faster Input**: Quick selection vs. manual typing  
✅ **Discoverability**: Users see available options  
✅ **Validation**: Built-in value checking  

### **Combobox Categories Added**

#### **🔢 Numeric Values**
- **Replicas**: `1`, `2`, `3`, `5`, `10`, `Custom...`
- **Ports**: `80`, `443`, `8080`, `3000`, `5000`, `Custom...`
- **Timeouts**: `30s`, `1m`, `5m`, `10m`, `30m`, `1h`, `Custom...`
- **History Limits**: `1`, `3`, `5`, `10`, `20`, `50`, `Custom...`

#### **💾 Storage & Resources**
- **Storage Sizes**: `1Gi`, `5Gi`, `10Gi`, `20Gi`, `50Gi`, `100Gi`, `Custom...`
- **CPU Values**: `100m`, `250m`, `500m`, `1000m`, `2000m`, `4000m`, `Custom...`
- **Memory Values**: `128Mi`, `256Mi`, `512Mi`, `1Gi`, `2Gi`, `4Gi`, `8Gi`, `Custom...`

#### **🎯 Service Types**
- **Service Types**: `ClusterIP`, `NodePort`, `LoadBalancer`, `ExternalName`
- **Protocols**: `TCP`, `UDP`, `SCTP`
- **App Protocols**: `http`, `https`, `grpc`, `tcp`, `udp`, `Custom...`

#### **🔐 Security & Permissions**
- **Pod Security**: `privileged`, `baseline`, `restricted`
- **Encryption**: `AES-256`, `ChaCha20`, `RSA-2048`, `None`
- **File Permissions**: `0400`, `0600`, `0640`, `0644`, `Custom...`

#### **🌍 Environment & Configuration**
- **Environments**: `development`, `staging`, `production`, `testing`
- **Namespaces**: `default`, `kube-system`, `monitoring`, `logging`, `Create New...`
- **Time Zones**: `UTC`, `America/New_York`, `Europe/London`, `Asia/Tokyo`, `Custom...`

#### **📊 Monitoring & Observability**
- **Metrics**: `Prometheus`, `Custom Metrics`, `None`
- **Logging**: `Fluentd`, `ELK Stack`, `Custom Logger`, `None`
- **Tracing**: `Jaeger`, `Zipkin`, `OpenTelemetry`, `None`

### **Custom Input Option**
Every combobox includes a **"Custom..."** option that allows users to:
- Enter custom values when needed
- Override default options
- Maintain flexibility while providing guidance
- Learn from common patterns

### **Dynamic Input System**
When "Custom..." is selected, the UI dynamically presents a new input field:

```
┌─────────────────────────────────────────────────────────────┐
│  📱 App: web-app                                           │
├─────────────────────────────────────────────────────────────┤
│  🏷️  Name: [web-app]                    🔄 Replicas: [dropdown▼]│
│  🐳 Image: [nginx:latest]              💾 Storage: [dropdown▼]│
│  🌐 Port: [dropdown▼]                   🏷️  Labels: [button]  │
│                                         🔧 Advanced [▼]     │
├─────────────────────────────────────────────────────────────┤
│  [➕ Add Port] [➕ Add Volume] [➕ Add Secret] [➕ Add Config]│
└─────────────────────────────────────────────────────────────┘
```

**Example: Custom Replicas Selection**
1. User clicks **Replicas** dropdown
2. Sees options: `1`, `2`, `3`, `5`, `10`, `Custom...`
3. User selects **"Custom..."**
4. UI dynamically replaces dropdown with: `🔄 Replicas: [Custom...] [number-input]`
5. User can enter any value: `25`, `100`, `1000`, etc.

**Example: Custom Storage Selection**
1. User clicks **Storage** dropdown  
2. Sees options: `1Gi`, `5Gi`, `10Gi`, `20Gi`, `50Gi`, `100Gi`, `Custom...`
3. User selects **"Custom..."**
4. UI dynamically replaces dropdown with: `💾 Storage: [Custom...] [text-input]`
5. User can enter any value: `500Mi`, `2.5Gi`, `1Ti`, etc.

### **Smart Defaults**
Comboboxes are populated with:
- **Industry Standards**: Common Kubernetes values
- **Best Practices**: Recommended configurations
- **Production Ready**: Tested and validated options
- **Extensible**: Easy to add new options

### **Dynamic Input Behavior & Validation**

#### **Input Type Detection**
The system automatically detects the appropriate input type based on the property:

```
┌─────────────────────────────────────────────────────────────┐
│                    Dynamic Input Types                      │
├─────────────────────────────────────────────────────────────┤
│  🔢 Numeric Properties (Replicas, Timeouts)               │
│  ├─ Shows: [number-input] with min/max validation         │
│  ├─ Examples: Replicas: 1-1000, Timeout: 1s-24h          │
│  └─ Validation: Must be positive integer/float            │
│                                                             │
│  💾 Storage Properties (Memory, Storage)                  │
│  ├─ Shows: [text-input] with format validation            │
│  ├─ Examples: 500Mi, 2.5Gi, 1Ti                          │
│  └─ Validation: Must match Kubernetes resource format     │
│                                                             │
│  🌐 Port Properties (Ports, Target Ports)                 │
│  ├─ Shows: [number-input] with range validation           │
│  ├─ Examples: 1024-65535 (non-privileged ports)          │
│  └─ Validation: Must be valid port number                 │
│                                                             │
│  🕐 Time Properties (Schedules, Deadlines)                │
│  ├─ Shows: [text-input] with cron/ISO format validation  │
│  ├─ Examples: "*/5 * * * *", "2024-12-31T23:59:59Z"      │
│  └─ Validation: Must be valid cron expression or ISO date │
└─────────────────────────────────────────────────────────────┘
```

#### **Real-time Validation**
As users type custom values, the system provides immediate feedback:

```
┌─────────────────────────────────────────────────────────────┐
│                    Validation Feedback                      │
├─────────────────────────────────────────────────────────────┤
│  ✅ Valid Input: [🟢 25] (Replicas)                       │
│  ❌ Invalid Input: [🔴 -5] (Replicas)                     │
│     Error: "Replicas must be a positive number"           │
│                                                             │
│  ✅ Valid Input: [🟢 2.5Gi] (Storage)                     │
│  ❌ Invalid Input: [🔴 2.5GB] (Storage)                   │
│     Error: "Storage must use Kubernetes format (Ki, Mi, Gi, Ti)"│
│                                                             │
│  ✅ Valid Input: [🟢 8080] (Port)                         │
│  ❌ Invalid Input: [🔴 99999] (Port)                      │
│     Error: "Port must be between 1024 and 65535"          │
└─────────────────────────────────────────────────────────────┘
```

#### **Smart Suggestions**
The system provides intelligent suggestions for custom values:

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Suggestions                        │
├─────────────────────────────────────────────────────────────┤
│  🔄 Replicas: [Custom...] [25]                           │
│     💡 Suggestions: 20, 30, 50 (based on common patterns)│
│                                                             │
│  💾 Storage: [Custom...] [2.5Gi]                         │
│     💡 Suggestions: 2Gi, 3Gi, 5Gi (nearest standard)     │
│                                                             │
│  🌐 Port: [Custom...] [8080]                              │
│     💡 Suggestions: 8000, 9000, 10000 (common dev ports) │
└─────────────────────────────────────────────────────────────┘
```

#### **Revert to Dropdown**
Users can easily switch back to predefined options:

```
┌─────────────────────────────────────────────────────────────┐
│                    Revert Functionality                     │
├─────────────────────────────────────────────────────────────┤
│  🔄 Replicas: [Custom...] [25] [↩️ Revert]               │
│     Click "Revert" to return to dropdown with options     │
│                                                             │
│  💾 Storage: [Custom...] [2.5Gi] [↩️ Revert]             │
│     Click "Revert" to return to dropdown with options     │
└─────────────────────────────────────────────────────────────┘
```
- **Detailed Mode**: All properties visible, collapsible sections

## 🔧 Property Input Types

### **Text Inputs**
- **Single Line**: Names, simple values
- **Multi Line**: Commands, descriptions
- **Code**: YAML, JSON, scripts

### **Number Inputs**
- **Integer**: Ports, replicas, timeouts
- **Float**: CPU limits, memory
- **Duration**: Timeouts, intervals

### **Selection Inputs**
- **Dropdown**: Types, strategies, policies
- **Multi-select**: Labels, annotations, ports
- **Toggle**: Boolean values
- **Radio**: Exclusive choices

### **Complex Inputs**
- **Key-Value**: Labels, annotations, environment
- **Array**: Ports, volumes, secrets
- **Object**: Security context, resource limits
- **File Upload**: Config files, secrets

## 🎯 Validation & Error Handling

### **Real-time Validation**
- **Field Level**: Immediate feedback on input
- **Node Level**: Configuration completeness
- **Graph Level**: Connection validity
- **Deployment Level**: Resource requirements

### **Error States**
- **Warning**: Non-critical issues (yellow)
- **Error**: Critical issues (red)
- **Info**: Helpful suggestions (blue)
- **Success**: Valid configuration (green)

### **Validation Rules**
- **Required Fields**: Must be filled
- **Format Validation**: Correct syntax
- **Dependency Checks**: Required connections
- **Resource Limits**: Cluster capacity
- **Security Policies**: Compliance rules

This component library provides **100% API coverage** while maintaining an **intuitive, uncluttered interface** through progressive disclosure and smart organization! 🎨✨ 