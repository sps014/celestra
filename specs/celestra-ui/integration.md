# Celestra UI Backend Integration

## 🎯 Overview

The Backend Integration layer connects the Celestra Visual Builder to the Celestra engine, Kubernetes clusters, Docker environments, and other deployment targets. It provides **real-time communication**, **secure authentication**, **deployment orchestration**, and **monitoring integration**.

## 🏗️ Architecture Overview

### **System Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    System Architecture                      │
├─────────────────────────────────────────────────────────────┤
│  🎨 Frontend (React + Rete.js)                            │
│  ├─ Visual Builder                                         │
│  ├─ Component Library                                      │
│  ├─ Workflow Engine                                        │
│  └─ Code Generator                                         │
│                                                             │
│  🔌 API Gateway (FastAPI)                                  │
│  ├─ Authentication                                         │
│  ├─ Request Routing                                        │
│  ├─ Rate Limiting                                          │
│  └─ Load Balancing                                         │
│                                                             │
│  🚀 Celestra Engine (Python)                               │
│  ├─ DSL Processing                                         │
│  ├─ Resource Generation                                    │
│  ├─ Validation Engine                                      │
│  └─ Output Formatters                                      │
│                                                             │
│  ☸️  Deployment Targets                                     │
│  ├─ Kubernetes Clusters                                    │
│  ├─ Docker Environments                                    │
│  ├─ Cloud Platforms                                        │
│  └─ On-premise Systems                                     │
└─────────────────────────────────────────────────────────────┘
```

### **Technology Stack**
```
┌─────────────────────────────────────────────────────────────┐
│                    Technology Stack                        │
├─────────────────────────────────────────────────────────────┤
│  🎨 Frontend                                              │
│  ├─ React 18 + TypeScript                                 │
│  ├─ Rete.js for visual workflows                          │
│  ├─ Tailwind CSS for styling                              │
│  ├─ Zustand for state management                          │
│  └─ WebSocket for real-time updates                       │
│                                                             │
│  🔌 Backend                                               │
│  ├─ FastAPI (Python 3.9+)                                 │
│  ├─ Celestra Engine                                       │
│  ├─ SQLAlchemy for database                               │
│  ├─ Redis for caching                                     │
│  └─ Celery for background tasks                           │
│                                                             │
│  🚀 Infrastructure                                         │
│  ├─ Docker containers                                      │
│  ├─ Kubernetes orchestration                              │
│  ├─ PostgreSQL database                                    │
│  ├─ Redis cache                                           │
│  └─ Nginx reverse proxy                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🔌 API Design

### **REST API Endpoints**

#### **1. Authentication & Authorization**
```python
# FastAPI endpoints
@router.post("/auth/login")
async def login(credentials: LoginCredentials):
    """User authentication"""
    pass

@router.post("/auth/logout")
async def logout(token: str):
    """User logout"""
    pass

@router.post("/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token"""
    pass

@router.get("/auth/profile")
async def get_profile(token: str):
    """Get user profile"""
    pass
```

#### **2. Workflow Management**
```python
@router.post("/workflows")
async def create_workflow(workflow: WorkflowCreate):
    """Create new workflow"""
    pass

@router.get("/workflows")
async def list_workflows(user_id: str, page: int = 1):
    """List user workflows"""
    pass

@router.get("/workflows/{workflow_id}")
async def get_workflow(workflow_id: str):
    """Get workflow details"""
    pass

@router.put("/workflows/{workflow_id}")
async def update_workflow(workflow_id: str, workflow: WorkflowUpdate):
    """Update workflow"""
    pass

@router.delete("/workflows/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """Delete workflow"""
    pass
```

#### **3. Code Generation**
```python
@router.post("/generate/dsl")
async def generate_dsl(workflow: WorkflowData):
    """Generate Celestra DSL from workflow"""
    pass

@router.post("/generate/kubernetes")
async def generate_kubernetes(workflow: WorkflowData):
    """Generate Kubernetes YAML from workflow"""
    pass

@router.post("/generate/docker-compose")
async def generate_docker_compose(workflow: WorkflowData):
    """Generate Docker Compose from workflow"""
    pass

@router.post("/generate/helm")
async def generate_helm(workflow: WorkflowData):
    """Generate Helm charts from workflow"""
    pass
```

#### **4. Deployment Management**
```python
@router.post("/deploy/kubernetes")
async def deploy_kubernetes(deployment: K8sDeployment):
    """Deploy to Kubernetes cluster"""
    pass

@router.post("/deploy/docker-compose")
async def deploy_docker_compose(deployment: DockerDeployment):
    """Deploy using Docker Compose"""
    pass

@router.get("/deploy/status/{deployment_id}")
async def get_deployment_status(deployment_id: str):
    """Get deployment status"""
    pass

@router.post("/deploy/rollback/{deployment_id}")
async def rollback_deployment(deployment_id: str):
    """Rollback deployment"""
    pass
```

### **WebSocket API**

#### **Real-time Communication**
```python
# WebSocket connection for real-time updates
@websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    
    try:
        while True:
            # Handle incoming messages
            data = await websocket.receive_json()
            
            if data["type"] == "workflow_update":
                # Process workflow updates
                await process_workflow_update(data, websocket)
                
            elif data["type"] == "deployment_status":
                # Send deployment status updates
                await send_deployment_status(data, websocket)
                
            elif data["type"] == "validation_result":
                # Send validation results
                await send_validation_result(data, websocket)
                
    except WebSocketDisconnect:
        # Handle disconnection
        await handle_disconnect(user_id)
```

#### **Message Types**
```typescript
// WebSocket message types
interface WebSocketMessage {
  type: 'workflow_update' | 'deployment_status' | 'validation_result' | 'error';
  data: any;
  timestamp: string;
  userId: string;
}

interface WorkflowUpdateMessage {
  type: 'workflow_update';
  data: {
    workflowId: string;
    nodes: Node[];
    connections: Connection[];
    code: string;
  };
}

interface DeploymentStatusMessage {
  type: 'deployment_status';
  data: {
    deploymentId: string;
    status: 'pending' | 'running' | 'success' | 'failed';
    progress: number;
    details: string;
  };
}
```

## 🚀 Celestra Engine Integration

### **Engine Interface**
```python
# Celestra Engine integration
class CelestraEngine:
    def __init__(self):
        self.validator = ValidationEngine()
        self.generator = CodeGenerator()
        self.deployer = DeploymentEngine()
    
    async def generate_dsl(self, workflow_data: dict) -> str:
        """Generate Celestra DSL from workflow data"""
        try:
            # Validate workflow
            validation_result = await self.validator.validate_workflow(workflow_data)
            if not validation_result.is_valid:
                raise ValidationError(validation_result.errors)
            
            # Generate DSL code
            dsl_code = await self.generator.generate_dsl(workflow_data)
            return dsl_code
            
        except Exception as e:
            logger.error(f"DSL generation failed: {e}")
            raise
    
    async def generate_kubernetes(self, workflow_data: dict) -> str:
        """Generate Kubernetes YAML from workflow"""
        try:
            # Generate DSL first
            dsl_code = await self.generate_dsl(workflow_data)
            
            # Convert to Kubernetes YAML
            k8s_yaml = await self.generator.dsl_to_kubernetes(dsl_code)
            return k8s_yaml
            
        except Exception as e:
            logger.error(f"Kubernetes generation failed: {e}")
            raise
    
    async def deploy_kubernetes(self, deployment_config: dict) -> str:
        """Deploy to Kubernetes cluster"""
        try:
            # Validate deployment config
            await self.validator.validate_deployment(deployment_config)
            
            # Execute deployment
            deployment_id = await self.deployer.deploy_kubernetes(deployment_config)
            return deployment_id
            
        except Exception as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise
```

### **Workflow Processing**
```python
class WorkflowProcessor:
    def __init__(self):
        self.celestra_engine = CelestraEngine()
        self.cache = RedisCache()
    
    async def process_workflow(self, workflow_data: dict) -> WorkflowResult:
        """Process visual workflow and generate outputs"""
        try:
            # Check cache first
            cache_key = self.generate_cache_key(workflow_data)
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Process workflow
            result = await self.process_workflow_internal(workflow_data)
            
            # Cache result
            await self.cache.set(cache_key, result, ttl=3600)
            
            return result
            
        except Exception as e:
            logger.error(f"Workflow processing failed: {e}")
            raise
    
    async def process_workflow_internal(self, workflow_data: dict) -> WorkflowResult:
        """Internal workflow processing"""
        # Extract nodes and connections
        nodes = workflow_data.get('nodes', [])
        connections = workflow_data.get('connections', [])
        
        # Validate workflow structure
        await self.validate_workflow_structure(nodes, connections)
        
        # Generate different outputs
        dsl_code = await self.celestra_engine.generate_dsl(workflow_data)
        k8s_yaml = await self.celestra_engine.generate_kubernetes(workflow_data)
        docker_compose = await self.celestra_engine.generate_docker_compose(workflow_data)
        
        return WorkflowResult(
            dsl_code=dsl_code,
            kubernetes_yaml=k8s_yaml,
            docker_compose=docker_compose,
            validation_result=ValidationResult(is_valid=True)
        )
```

## ☸️ Kubernetes Integration

### **Cluster Management**
```python
class KubernetesManager:
    def __init__(self):
        self.clusters = {}
        self.kubeconfigs = {}
    
    async def add_cluster(self, cluster_config: ClusterConfig) -> str:
        """Add Kubernetes cluster"""
        try:
            # Validate cluster configuration
            await self.validate_cluster_config(cluster_config)
            
            # Test cluster connectivity
            await self.test_cluster_connection(cluster_config)
            
            # Store cluster configuration
            cluster_id = str(uuid.uuid4())
            self.clusters[cluster_id] = cluster_config
            
            # Initialize kubectl client
            await self.initialize_kubectl_client(cluster_id, cluster_config)
            
            return cluster_id
            
        except Exception as e:
            logger.error(f"Failed to add cluster: {e}")
            raise
    
    async def deploy_to_cluster(self, cluster_id: str, deployment_config: dict) -> str:
        """Deploy to specific Kubernetes cluster"""
        try:
            # Get cluster configuration
            cluster_config = self.clusters.get(cluster_id)
            if not cluster_config:
                raise ValueError(f"Cluster {cluster_id} not found")
            
            # Generate Kubernetes manifests
            manifests = await self.generate_manifests(deployment_config)
            
            # Apply manifests to cluster
            deployment_id = await self.apply_manifests(cluster_id, manifests)
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Deployment to cluster {cluster_id} failed: {e}")
            raise
    
    async def monitor_deployment(self, cluster_id: str, deployment_id: str) -> DeploymentStatus:
        """Monitor deployment status"""
        try:
            # Get deployment status from cluster
            status = await self.get_deployment_status(cluster_id, deployment_id)
            
            # Parse and format status
            formatted_status = self.format_deployment_status(status)
            
            return formatted_status
            
        except Exception as e:
            logger.error(f"Failed to monitor deployment: {e}")
            raise
```

### **Deployment Execution**
```python
class KubernetesDeployer:
    def __init__(self):
        self.executor = CommandExecutor()
        self.validator = ManifestValidator()
    
    async def deploy_workflow(self, workflow_data: dict, cluster_config: dict) -> str:
        """Deploy workflow to Kubernetes cluster"""
        try:
            # Generate Kubernetes manifests
            manifests = await self.generate_manifests(workflow_data)
            
            # Validate manifests
            validation_result = await self.validator.validate_manifests(manifests)
            if not validation_result.is_valid:
                raise ValidationError(validation_result.errors)
            
            # Create temporary manifest files
            manifest_files = await self.create_manifest_files(manifests)
            
            # Apply manifests using kubectl
            deployment_id = await self.apply_manifests(manifest_files, cluster_config)
            
            # Clean up temporary files
            await self.cleanup_manifest_files(manifest_files)
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Kubernetes deployment failed: {e}")
            raise
    
    async def apply_manifests(self, manifest_files: List[str], cluster_config: dict) -> str:
        """Apply manifests to cluster using kubectl"""
        try:
            # Build kubectl command
            cmd = self.build_kubectl_command(manifest_files, cluster_config)
            
            # Execute deployment
            result = await self.executor.execute_command(cmd)
            
            # Parse deployment ID from result
            deployment_id = self.parse_deployment_id(result.stdout)
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Manifest application failed: {e}")
            raise
```

## 🐳 Docker Integration

### **Docker Compose Management**
```python
class DockerComposeManager:
    def __init__(self):
        self.executor = CommandExecutor()
        self.validator = ComposeValidator()
    
    async def deploy_workflow(self, workflow_data: dict, docker_config: dict) -> str:
        """Deploy workflow using Docker Compose"""
        try:
            # Generate Docker Compose file
            compose_yaml = await self.generate_compose_file(workflow_data)
            
            # Validate compose file
            validation_result = await self.validator.validate_compose(compose_yaml)
            if not validation_result.is_valid:
                raise ValidationError(validation_result.errors)
            
            # Create temporary compose file
            compose_file = await self.create_compose_file(compose_yaml)
            
            # Deploy using docker-compose
            deployment_id = await self.deploy_compose(compose_file, docker_config)
            
            # Clean up temporary file
            await self.cleanup_compose_file(compose_file)
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Docker Compose deployment failed: {e}")
            raise
    
    async def deploy_compose(self, compose_file: str, docker_config: dict) -> str:
        """Execute docker-compose deployment"""
        try:
            # Build docker-compose command
            cmd = self.build_compose_command(compose_file, docker_config)
            
            # Execute deployment
            result = await self.executor.execute_command(cmd)
            
            # Parse deployment ID from result
            deployment_id = self.parse_compose_deployment_id(result.stdout)
            
            return deployment_id
            
        except Exception as e:
            logger.error(f"Compose deployment failed: {e}")
            raise
    
    async def monitor_compose_deployment(self, deployment_id: str) -> DeploymentStatus:
        """Monitor Docker Compose deployment status"""
        try:
            # Get service status
            cmd = f"docker-compose ps --format json"
            result = await self.executor.execute_command(cmd)
            
            # Parse service status
            status = self.parse_compose_status(result.stdout)
            
            # Format deployment status
            formatted_status = self.format_compose_status(status)
            
            return formatted_status
            
        except Exception as e:
            logger.error(f"Failed to monitor compose deployment: {e}")
            raise
```

## 🔐 Security & Authentication

### **Authentication System**
```python
class AuthenticationManager:
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET")
        self.token_blacklist = RedisSet("token_blacklist")
    
    async def authenticate_user(self, credentials: LoginCredentials) -> AuthResult:
        """Authenticate user credentials"""
        try:
            # Validate credentials
            user = await self.validate_credentials(credentials)
            if not user:
                raise AuthenticationError("Invalid credentials")
            
            # Generate JWT tokens
            access_token = self.generate_access_token(user)
            refresh_token = self.generate_refresh_token(user)
            
            # Store refresh token
            await self.store_refresh_token(user.id, refresh_token)
            
            return AuthResult(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise
    
    async def validate_token(self, token: str) -> User:
        """Validate JWT token"""
        try:
            # Check if token is blacklisted
            if await self.token_blacklist.contains(token):
                raise AuthenticationError("Token is blacklisted")
            
            # Decode and validate token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            user_id = payload.get("user_id")
            
            # Get user from database
            user = await self.get_user_by_id(user_id)
            if not user:
                raise AuthenticationError("User not found")
            
            return user
            
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            raise
```

### **Authorization & RBAC**
```python
class AuthorizationManager:
    def __init__(self):
        self.permission_cache = RedisCache()
    
    async def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for resource action"""
        try:
            # Check cache first
            cache_key = f"permission:{user.id}:{resource}:{action}"
            cached_result = await self.permission_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Check user permissions
            has_permission = await self.check_user_permissions(user, resource, action)
            
            # Cache result
            await self.permission_cache.set(cache_key, has_permission, ttl=300)
            
            return has_permission
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False
    
    async def check_user_permissions(self, user: User, resource: str, action: str) -> bool:
        """Check user permissions from database"""
        try:
            # Get user roles
            roles = await self.get_user_roles(user.id)
            
            # Check role permissions
            for role in roles:
                if await self.role_has_permission(role, resource, action):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"User permission check failed: {e}")
            return False
```

## 📊 Monitoring & Observability

### **Deployment Monitoring**
```python
class DeploymentMonitor:
    def __init__(self):
        self.metrics_collector = MetricsCollector()
        self.alert_manager = AlertManager()
    
    async def monitor_deployment(self, deployment_id: str, deployment_config: dict):
        """Monitor deployment progress and health"""
        try:
            # Start monitoring loop
            while True:
                # Get deployment status
                status = await self.get_deployment_status(deployment_id)
                
                # Collect metrics
                await self.collect_deployment_metrics(deployment_id, status)
                
                # Check for completion
                if status.is_completed():
                    await self.handle_deployment_completion(deployment_id, status)
                    break
                
                # Check for failures
                if status.is_failed():
                    await self.handle_deployment_failure(deployment_id, status)
                    break
                
                # Check for timeouts
                if status.is_timed_out():
                    await self.handle_deployment_timeout(deployment_id, status)
                    break
                
                # Wait before next check
                await asyncio.sleep(5)
                
        except Exception as e:
            logger.error(f"Deployment monitoring failed: {e}")
            await self.handle_monitoring_error(deployment_id, e)
    
    async def collect_deployment_metrics(self, deployment_id: str, status: DeploymentStatus):
        """Collect deployment metrics"""
        try:
            metrics = {
                "deployment_id": deployment_id,
                "status": status.status,
                "progress": status.progress,
                "timestamp": datetime.utcnow().isoformat(),
                "duration": status.duration,
                "resource_usage": status.resource_usage
            }
            
            # Send metrics to monitoring system
            await self.metrics_collector.record_metrics("deployment", metrics)
            
        except Exception as e:
            logger.error(f"Failed to collect deployment metrics: {e}")
```

### **Health Checks & Alerts**
```python
class HealthCheckManager:
    def __init__(self):
        self.health_checks = {}
        self.alert_manager = AlertManager()
    
    async def register_health_check(self, check_id: str, check_config: dict):
        """Register health check for deployment"""
        try:
            # Create health check
            health_check = HealthCheck(
                id=check_id,
                type=check_config["type"],
                endpoint=check_config["endpoint"],
                interval=check_config["interval"],
                timeout=check_config["timeout"]
            )
            
            # Store health check
            self.health_checks[check_id] = health_check
            
            # Start monitoring
            asyncio.create_task(self.monitor_health_check(health_check))
            
        except Exception as e:
            logger.error(f"Failed to register health check: {e}")
            raise
    
    async def monitor_health_check(self, health_check: HealthCheck):
        """Monitor health check endpoint"""
        try:
            while True:
                # Perform health check
                result = await self.perform_health_check(health_check)
                
                # Update health status
                await self.update_health_status(health_check.id, result)
                
                # Send alerts if needed
                if not result.is_healthy:
                    await self.alert_manager.send_alert(
                        f"Health check failed for {health_check.id}",
                        result.details
                    )
                
                # Wait for next check
                await asyncio.sleep(health_check.interval)
                
        except Exception as e:
            logger.error(f"Health check monitoring failed: {e}")
```

## 🚀 Performance & Scalability

### **Caching Strategy**
```python
class CacheManager:
    def __init__(self):
        self.redis_client = Redis()
        self.memory_cache = {}
        self.cache_config = self.load_cache_config()
    
    async def get_cached_result(self, key: str) -> Optional[Any]:
        """Get cached result from multiple cache layers"""
        try:
            # Check memory cache first (fastest)
            if key in self.memory_cache:
                return self.memory_cache[key]
            
            # Check Redis cache
            cached_result = await self.redis_client.get(key)
            if cached_result:
                # Store in memory cache for faster access
                self.memory_cache[key] = cached_result
                return cached_result
            
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")
            return None
    
    async def set_cached_result(self, key: str, value: Any, ttl: int = 3600):
        """Set cached result in multiple cache layers"""
        try:
            # Store in memory cache
            self.memory_cache[key] = value
            
            # Store in Redis cache
            await self.redis_client.set(key, value, ex=ttl)
            
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")
```

### **Background Task Processing**
```python
class TaskProcessor:
    def __init__(self):
        self.celery_app = Celery("celestra_ui")
        self.task_queue = asyncio.Queue()
    
    async def submit_task(self, task_type: str, task_data: dict) -> str:
        """Submit background task for processing"""
        try:
            # Create task
            task = Task(
                id=str(uuid.uuid4()),
                type=task_type,
                data=task_data,
                status="pending",
                created_at=datetime.utcnow()
            )
            
            # Submit to Celery
            celery_task = self.celery_app.send_task(
                f"tasks.{task_type}",
                args=[task_data],
                task_id=task.id
            )
            
            # Store task reference
            await self.store_task_reference(task.id, celery_task.id)
            
            return task.id
            
        except Exception as e:
            logger.error(f"Task submission failed: {e}")
            raise
    
    async def get_task_status(self, task_id: str) -> TaskStatus:
        """Get background task status"""
        try:
            # Get Celery task ID
            celery_task_id = await self.get_celery_task_id(task_id)
            
            # Get task status from Celery
            celery_task = self.celery_app.AsyncResult(celery_task_id)
            
            # Convert to internal status
            status = self.convert_celery_status(celery_task)
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get task status: {e}")
            raise
```

## 🎯 Success Metrics

### **Integration Performance**
- **API Response Time**: <200ms for 95% of requests
- **WebSocket Latency**: <50ms for real-time updates
- **Deployment Time**: <2 minutes for typical workflows
- **Cache Hit Rate**: >80% for repeated operations

### **Reliability Metrics**
- **API Uptime**: 99.9% availability
- **Deployment Success Rate**: >95%
- **Error Recovery**: <5 minutes for automatic recovery
- **Data Consistency**: 100% for critical operations

### **Security Metrics**
- **Authentication Success Rate**: >99%
- **Authorization Accuracy**: 100% for permission checks
- **Data Encryption**: 100% for sensitive data
- **Audit Trail**: Complete for all operations

## 🚀 Future Enhancements

### **Advanced Integration Features**
- **Multi-cluster Management**: Unified management of multiple Kubernetes clusters
- **Hybrid Cloud Support**: Seamless deployment across cloud and on-premise
- **GitOps Integration**: Direct Git repository integration for workflows
- **CI/CD Pipeline Integration**: Jenkins, GitHub Actions, GitLab CI integration

### **Scalability Improvements**
- **Horizontal Scaling**: Auto-scaling based on load
- **Load Balancing**: Intelligent request distribution
- **Microservices Architecture**: Break down into smaller, focused services
- **Event-driven Architecture**: Asynchronous processing for better performance

### **Monitoring & Observability**
- **Distributed Tracing**: End-to-end request tracing
- **Advanced Metrics**: Custom business metrics and KPIs
- **Predictive Analytics**: AI-powered performance prediction
- **Automated Remediation**: Self-healing systems

This backend integration provides **seamless connectivity**, **secure communication**, and **scalable performance** while maintaining the reliability and security required for enterprise deployment management! 🚀✨ 