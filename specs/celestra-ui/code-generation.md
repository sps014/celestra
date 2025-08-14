# Celestra UI Code Generation Engine

## 🎯 Overview

The Code Generation Engine is the bridge between the visual workflow builder and the Celestra DSL. It provides **real-time code generation**, **multi-format output**, and **bidirectional editing** - allowing users to see generated code instantly as they build visually, and even edit the code directly with visual updates.

## 🏗️ Architecture

### **Technology Stack**
- **Frontend**: TypeScript + Rete.js
- **Backend**: Python + Celestra Engine
- **Real-time**: WebSocket for live updates
- **Validation**: AST parsing and validation

### **Core Components**
```
┌─────────────────────────────────────────────────────────────┐
│                    Code Generation Engine                   │
├─────────────────────────────────────────────────────────────┤
│  🎯 Visual Workflow  │  🔄 Code Generator                 │
│  ├─ Rete.js Nodes    │  ├─ AST Builder                    │
│  ├─ Connections      │  ├─ DSL Generator                   │
│  └─ Properties       │  ├─ Format Converter               │
│                       │  └─ Validator                     │
│                       │                                     │
│  📝 Generated Code   │  🚀 Output Formats                  │
│  ├─ Celestra DSL     │  ├─ Kubernetes YAML                │
│  ├─ Python Code      │  ├─ Docker Compose                 │
│  ├─ YAML Output      │  ├─ Helm Charts                    │
│  └─ JSON Schema      │  └─ Terraform                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Real-time Code Generation

### **Live Code Updates**
```typescript
class CelestraCodeGenerator {
  private nodes: Node[] = [];
  private connections: Connection[] = [];
  private codeCache: Map<string, string> = new Map();

  // Real-time code generation
  onNodeChange(nodeId: string, properties: any) {
    // Update node data
    this.updateNode(nodeId, properties);
    
    // Regenerate affected code
    this.regenerateCode(nodeId);
    
    // Emit code update event
    this.emit('code-updated', this.generateFullCode());
  }

  // Regenerate code when connections change
  onConnectionChange(connectionId: string, connection: Connection) {
    this.updateConnection(connectionId, connection);
    this.regenerateCode(connection.source);
    this.emit('code-updated', this.generateFullCode());
  }
}
```

### **Incremental Generation**
```
┌─────────────────────────────────────────────────────────────┐
│                    Incremental Generation                   │
├─────────────────────────────────────────────────────────────┤
│  📱 App Node Changes                                       │
│  ├─ Name: "web-app" → "api-server"                        │
│  ├─ Image: "nginx:latest" → "api:v2.0"                    │
│  └─ Port: 8080 → 3000                                     │
│                                                             │
│  🔄 Code Regeneration                                      │
│  ├─ Update App definition                                  │
│  ├─ Update Service selector                                │
│  ├─ Update Ingress path                                    │
│  └─ Update all references                                  │
│                                                             │
│  📝 Generated Code                                         │
│  ```python                                                 │
│  app = App("api-server")                                   │
│      .image("api:v2.0")                                    │
│      .port(3000)                                           │
│  ```                                                       │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 DSL Generation

### **Celestra DSL Structure**
```typescript
interface DSLStructure {
  imports: string[];
  components: ComponentDefinition[];
  connections: ConnectionDefinition[];
  output: OutputDefinition[];
}

interface ComponentDefinition {
  type: string;
  name: string;
  properties: PropertyDefinition[];
  methods: MethodCall[];
}

interface MethodCall {
  method: string;
  arguments: any[];
  chaining: boolean;
}
```

### **DSL Generation Algorithm**
```typescript
class DSLGenerator {
  generateDSL(nodes: Node[], connections: Connection[]): string {
    let code = '';
    
    // 1. Generate imports
    code += this.generateImports(nodes);
    
    // 2. Generate component definitions
    code += this.generateComponents(nodes);
    
    // 3. Generate connections and dependencies
    code += this.generateConnections(connections);
    
    // 4. Generate output generation
    code += this.generateOutput(nodes);
    
    return code;
  }

  private generateImports(nodes: Node[]): string {
    const imports = new Set<string>();
    
    nodes.forEach(node => {
      const nodeType = this.getNodeType(node);
      if (nodeType) {
        imports.add(nodeType);
      }
    });
    
    return Array.from(imports)
      .map(imp => `from celestra import ${imp}`)
      .join('\n') + '\n\n';
  }

  private generateComponents(nodes: Node[]): string {
    let code = '';
    
    nodes.forEach(node => {
      code += this.generateComponent(node);
    });
    
    return code;
  }

  private generateComponent(node: Node): string {
    const nodeType = this.getNodeType(node);
    const name = node.data.name;
    let code = `${nodeType.toLowerCase()} = ${nodeType}("${name}")`;
    
    // Add method calls based on properties
    node.data.properties.forEach(prop => {
      if (prop.value !== undefined && prop.value !== '') {
        code += `\n    .${prop.key}(${this.formatValue(prop.value)})`;
      }
    });
    
    return code + '\n\n';
  }
}
```

### **Method Chaining Generation**
```typescript
class MethodChainGenerator {
  generateMethodChain(node: Node): string {
    const methods = this.extractMethods(node);
    let chain = `${this.getNodeType(node)}("${node.data.name}")`;
    
    methods.forEach(method => {
      chain += `\n    .${method.name}(${this.formatArguments(method.args)})`;
    });
    
    return chain;
  }

  private extractMethods(node: Node): Method[] {
    const methods: Method[] = [];
    
    // Extract basic properties
    if (node.data.properties.image) {
      methods.push({ name: 'image', args: [node.data.properties.image] });
    }
    
    if (node.data.properties.port) {
      methods.push({ name: 'port', args: [node.data.properties.port] });
    }
    
    // Extract advanced properties
    if (node.data.properties.replicas) {
      methods.push({ name: 'replicas', args: [node.data.properties.replicas] });
    }
    
    // Extract security properties
    if (node.data.properties.serviceAccount) {
      methods.push({ name: 'service_account', args: [node.data.properties.serviceAccount] });
    }
    
    return methods;
  }
}
```

## 🔄 Bidirectional Editing

### **Code to Visual Updates**
```typescript
class BidirectionalEditor {
  // Parse DSL code and update visual representation
  parseDSLAndUpdate(code: string): void {
    try {
      // Parse the DSL code
      const ast = this.parseDSL(code);
      
      // Update visual nodes
      this.updateVisualNodes(ast);
      
      // Update connections
      this.updateVisualConnections(ast);
      
      // Emit update event
      this.emit('visual-updated');
    } catch (error) {
      this.emit('parse-error', error);
    }
  }

  private parseDSL(code: string): AST {
    // Use Python AST parser or custom parser
    return this.astParser.parse(code);
  }

  private updateVisualNodes(ast: AST): void {
    ast.components.forEach(component => {
      const nodeId = this.findNodeByName(component.name);
      if (nodeId) {
        this.updateNodeProperties(nodeId, component.properties);
      }
    });
  }
}
```

### **Live Code Editing**
```
┌─────────────────────────────────────────────────────────────┐
│                    Live Code Editing                        │
├─────────────────────────────────────────────────────────────┤
│  📝 Code Editor (Monaco)                                   │
│  ```python                                                 │
│  app = App("web-app")                                      │
│      .image("nginx:latest")                                │
│      .port(8080)                                           │
│      .replicas(3)                                          │
│  ```                                                       │
│                                                             │
│  🔄 Real-time Updates                                      │
│  ├─ Visual nodes update                                    │
│  ├─ Properties sync                                        │
│  ├─ Connections maintain                                    │
│  └─ Validation runs                                        │
│                                                             │
│  🎯 Visual Canvas                                          │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  📱 App: web-app                                        │ │
│  │  ├─ Image: nginx:latest                                 │ │
│  │  ├─ Port: 8080                                          │ │
│  │  └─ Replicas: 3                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Multi-format Output

### **Output Format Generators**

#### **1. Kubernetes YAML Generator**
```typescript
class KubernetesYAMLGenerator {
  generateYAML(nodes: Node[], connections: Connection[]): string {
    const resources = [];
    
    // Generate Kubernetes resources for each node
    nodes.forEach(node => {
      const resource = this.generateK8sResource(node);
      if (resource) {
        resources.push(resource);
      }
    });
    
    // Convert to YAML
    return this.toYAML(resources);
  }

  private generateK8sResource(node: Node): any {
    switch (node.type) {
      case 'celestra-app':
        return this.generateDeployment(node);
      case 'celestra-service':
        return this.generateService(node);
      case 'celestra-ingress':
        return this.generateIngress(node);
      case 'celestra-secret':
        return this.generateSecret(node);
      case 'celestra-configmap':
        return this.generateConfigMap(node);
      default:
        return null;
    }
  }

  private generateDeployment(node: Node): any {
    return {
      apiVersion: 'apps/v1',
      kind: 'Deployment',
      metadata: {
        name: node.data.name,
        labels: node.data.properties.labels || {}
      },
      spec: {
        replicas: node.data.properties.replicas || 1,
        selector: {
          matchLabels: {
            app: node.data.name
          }
        },
        template: {
          metadata: {
            labels: {
              app: node.data.name
            }
          },
          spec: {
            containers: [{
              name: node.data.name,
              image: node.data.properties.image,
              ports: this.generatePorts(node.data.properties.ports)
            }]
          }
        }
      }
    };
  }
}
```

#### **2. Docker Compose Generator**
```typescript
class DockerComposeGenerator {
  generateCompose(nodes: Node[], connections: Connection[]): string {
    const compose = {
      version: '3.8',
      services: {},
      networks: {},
      volumes: {}
    };
    
    // Generate services
    nodes.forEach(node => {
      if (node.type === 'celestra-app') {
        compose.services[node.data.name] = this.generateService(node);
      }
    });
    
    // Generate networks and volumes
    this.generateNetworksAndVolumes(nodes, compose);
    
    // Convert to YAML
    return this.toYAML(compose);
  }

  private generateService(node: Node): any {
    return {
      image: node.data.properties.image,
      ports: this.generatePortMappings(node.data.properties.ports),
      environment: node.data.properties.environment || {},
      volumes: this.generateVolumes(node.data.properties.volumes),
      networks: node.data.properties.networks || ['default']
    };
  }
}
```

#### **3. Helm Chart Generator**
```typescript
class HelmChartGenerator {
  generateHelm(nodes: Node[], connections: Connection[]): any {
    const chart = {
      apiVersion: 'v2',
      name: 'celestra-app',
      description: 'Generated by Celestra Visual Builder',
      version: '0.1.0',
      templates: [],
      values: {}
    };
    
    // Generate templates
    nodes.forEach(node => {
      const template = this.generateTemplate(node);
      if (template) {
        chart.templates.push(template);
      }
    });
    
    // Generate values.yaml
    chart.values = this.generateValues(nodes);
    
    return chart;
  }
}
```

### **Format Conversion Matrix**
```
┌─────────────────────────────────────────────────────────────┐
│                    Format Conversion                        │
├─────────────────────────────────────────────────────────────┤
│  Input Format → Output Format                              │
│                                                             │
│  📱 Visual Workflow                                        │
│  ├─ → Celestra DSL                                         │
│  ├─ → Kubernetes YAML                                      │
│  ├─ → Docker Compose                                       │
│  ├─ → Helm Charts                                          │
│  └─ → Terraform                                            │
│                                                             │
│  📝 Celestra DSL                                           │
│  ├─ → Visual Workflow                                      │
│  ├─ → Kubernetes YAML                                      │
│  ├─ → Docker Compose                                       │
│  ├─ → Helm Charts                                          │
│  └─ → Terraform                                            │
│                                                             │
│  ☸️  Kubernetes YAML                                        │
│  ├─ → Visual Workflow                                      │
│  ├─ → Celestra DSL                                         │
│  ├─ → Docker Compose                                       │
│  ├─ → Helm Charts                                          │
│  └─ → Terraform                                            │
└─────────────────────────────────────────────────────────────┘
```

## 🔍 Code Validation

### **Real-time Validation**
```typescript
class CodeValidator {
  validateCode(code: string): ValidationResult {
    const result: ValidationResult = {
      isValid: true,
      errors: [],
      warnings: [],
      suggestions: []
    };
    
    try {
      // Parse the code
      const ast = this.parseCode(code);
      
      // Validate syntax
      this.validateSyntax(ast, result);
      
      // Validate semantics
      this.validateSemantics(ast, result);
      
      // Validate Celestra-specific rules
      this.validateCelestraRules(ast, result);
      
    } catch (error) {
      result.isValid = false;
      result.errors.push({
        line: error.line || 0,
        column: error.column || 0,
        message: error.message,
        severity: 'error'
      });
    }
    
    return result;
  }

  private validateCelestraRules(ast: AST, result: ValidationResult): void {
    // Check for required properties
    ast.components.forEach(component => {
      if (component.type === 'App' && !component.properties.image) {
        result.warnings.push({
          line: component.line,
          column: component.column,
          message: `App '${component.name}' should have an image specified`,
          severity: 'warning'
        });
      }
    });
    
    // Check for proper connections
    this.validateConnections(ast, result);
  }
}
```

### **Validation Rules**
```
┌─────────────────────────────────────────────────────────────┐
│                    Validation Rules                         │
├─────────────────────────────────────────────────────────────┤
│  🔍 Syntax Validation                                      │
│  ├─ Python syntax correctness                              │
│  ├─ Method call validity                                   │
│  ├─ Parameter types                                        │
│  └─ Chaining syntax                                        │
│                                                             │
│  🎯 Semantic Validation                                    │
│  ├─ Required properties                                    │
│  ├─ Property dependencies                                  │
│  ├─ Value constraints                                      │
│  └─ Resource limits                                        │
│                                                             │
│  🔐 Celestra Validation                                    │
│  ├─ Class compatibility                                    │
│  ├─ Method availability                                     │
│  ├─ Connection validity                                    │
│  └─ Output format support                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🎨 Code Editor Integration

### **Monaco Editor Features**
```typescript
class MonacoEditorIntegration {
  setupEditor(container: HTMLElement): monaco.editor.IStandaloneCodeEditor {
    // Configure Monaco editor
    const editor = monaco.editor.create(container, {
      value: this.initialCode,
      language: 'python',
      theme: 'vs-dark',
      automaticLayout: true,
      minimap: { enabled: true },
      scrollBeyondLastLine: false,
      fontSize: 14,
      fontFamily: 'JetBrains Mono'
    });
    
    // Add Celestra-specific features
    this.addCelestraFeatures(editor);
    
    // Setup change listener
    editor.onDidChangeModelContent(() => {
      this.onCodeChange(editor.getValue());
    });
    
    return editor;
  }

  private addCelestraFeatures(editor: monaco.editor.IStandaloneCodeEditor): void {
    // Add Celestra language support
    monaco.languages.register({ id: 'celestra' });
    
    // Add syntax highlighting
    monaco.languages.setMonarchTokensProvider('celestra', this.celestraLanguage);
    
    // Add IntelliSense
    monaco.languages.registerCompletionItemProvider('celestra', {
      provideCompletionItems: (model, position) => {
        return this.provideCelestraCompletions(model, position);
      }
    });
    
    // Add error highlighting
    this.setupErrorHighlighting(editor);
  }
}
```

### **IntelliSense & Auto-completion**
```typescript
class CelestraIntelliSense {
  provideCelestraCompletions(model: monaco.editor.ITextModel, position: monaco.Position): monaco.languages.CompletionItem[] {
    const completions: monaco.languages.CompletionItem[] = [];
    
    // Get current line and context
    const line = model.getLineContent(position.lineNumber);
    const word = model.getWordUntilPosition(position);
    
    // Provide class completions
    if (this.isAtClassStart(line, position)) {
      completions.push(...this.getClassCompletions());
    }
    
    // Provide method completions
    if (this.isAtMethodCall(line, position)) {
      completions.push(...this.getMethodCompletions(line, position));
    }
    
    // Provide property completions
    if (this.isAtProperty(line, position)) {
      completions.push(...this.getPropertyCompletions(line, position));
    }
    
    return completions;
  }

  private getClassCompletions(): monaco.languages.CompletionItem[] {
    return [
      {
        label: 'App',
        kind: monaco.languages.CompletionItemKind.Class,
        insertText: 'App("${1:name}")',
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Main application container'
      },
      {
        label: 'Service',
        kind: monaco.languages.CompletionItemKind.Class,
        insertText: 'Service("${1:name}")',
        insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
        documentation: 'Kubernetes service for exposing applications'
      }
      // ... more classes
    ];
  }
}
```

## 🚀 Performance Optimization

### **Code Generation Caching**
```typescript
class CodeGenerationCache {
  private cache = new Map<string, string>();
  private dependencyGraph = new Map<string, Set<string>>();

  generateCode(nodes: Node[], connections: Connection[]): string {
    const cacheKey = this.generateCacheKey(nodes, connections);
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }
    
    // Generate new code
    const code = this.generateCodeFromScratch(nodes, connections);
    
    // Cache the result
    this.cache.set(cacheKey, code);
    
    // Update dependency graph
    this.updateDependencyGraph(nodes, connections);
    
    return code;
  }

  private generateCacheKey(nodes: Node[], connections: Connection[]): string {
    // Create a hash of node configurations and connections
    const nodeHash = nodes.map(n => `${n.id}:${JSON.stringify(n.data.properties)}`).join('|');
    const connectionHash = connections.map(c => `${c.source}:${c.target}:${c.type}`).join('|');
    
    return `${nodeHash}|${connectionHash}`;
  }
}
```

### **Incremental Updates**
```typescript
class IncrementalCodeGenerator {
  updateCode(nodeId: string, changes: any): string {
    // Find affected code sections
    const affectedSections = this.findAffectedSections(nodeId);
    
    // Update only affected parts
    affectedSections.forEach(section => {
      this.updateCodeSection(section, changes);
    });
    
    // Regenerate affected code
    return this.regenerateAffectedCode(affectedSections);
  }

  private findAffectedSections(nodeId: string): CodeSection[] {
    const sections: CodeSection[] = [];
    
    // Find the node's own code section
    sections.push(this.findNodeCodeSection(nodeId));
    
    // Find dependent code sections
    const dependents = this.findDependentNodes(nodeId);
    dependents.forEach(dep => {
      sections.push(this.findNodeCodeSection(dep));
    });
    
    return sections;
  }
}
```

## 🎯 Success Metrics

### **Code Generation Performance**
- **Generation Time**: <100ms for typical workflows
- **Update Time**: <50ms for incremental updates
- **Cache Hit Rate**: >80% for repeated operations
- **Memory Usage**: <50MB for large workflows

### **Code Quality**
- **Syntax Correctness**: 100% valid Python code
- **Semantic Validation**: Real-time error detection
- **Format Support**: 100% of Celestra output formats
- **Bidirectional Sync**: Perfect visual-code synchronization

### **User Experience**
- **Real-time Updates**: Instant code generation
- **IntelliSense**: Full Celestra API support
- **Error Highlighting**: Clear error indication
- **Code Navigation**: Easy code-to-visual navigation

## 🚀 Future Enhancements

### **Advanced Code Generation**
- **Smart Defaults**: AI-powered property suggestions
- **Code Optimization**: Automatic performance improvements
- **Best Practices**: Built-in Celestra best practices
- **Custom Templates**: User-defined code patterns

### **Extended Format Support**
- **Pulumi**: Infrastructure as code
- **Ansible**: Configuration management
- **Chef**: Infrastructure automation
- **Custom DSLs**: User-defined languages

### **Collaboration Features**
- **Code Review**: Built-in code review tools
- **Version Control**: Git integration
- **Code Sharing**: Template sharing system
- **Team Workflows**: Collaborative editing

This code generation engine provides **real-time, bidirectional, multi-format code generation** that seamlessly bridges the visual workflow builder with the power of the Celestra DSL! 🎨✨ 