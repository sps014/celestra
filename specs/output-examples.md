# Output Examples

This document shows the actual Kubernetes and Docker Compose manifests generated from the K8s-Gen DSL code.

## Kubernetes Output Examples

### 1. Simple Web Application Output

**DSL Code:**
```python
web_app = (App("blog-app")
    .image("wordpress:latest")
    .port(80)
    .environment({"WORDPRESS_DB_HOST": "mysql"})
    .resources(cpu="500m", memory="512Mi", cpu_limit="1000m", memory_limit="1Gi")
    .scale(replicas=2, auto_scale_on_cpu=70)
    .expose(external_access=True, domain="blog.example.com")
    .lifecycle(
        Lifecycle()
            .pre_stop_http(path="/shutdown")
            .termination_grace_period(30)
    ))
```

**Generated Kubernetes YAML:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: blog-app
  labels:
    app: blog-app
    generated-by: k8s-gen
spec:
  replicas: 2
  selector:
    matchLabels:
      app: blog-app
  template:
    metadata:
      labels:
        app: blog-app
    spec:
      containers:
      - name: blog-app
        image: wordpress:latest
        ports:
        - containerPort: 80
          name: http
        env:
        - name: WORDPRESS_DB_HOST
          value: mysql
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: http
          initialDelaySeconds: 5
          periodSeconds: 5
        lifecycle:
          preStop:
            httpGet:
              path: /shutdown
              port: http
      terminationGracePeriodSeconds: 30
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: blog-app
  labels:
    app: blog-app
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: blog-app
---
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: blog-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: blog-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: blog-app
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - blog.example.com
    secretName: blog-app-tls
  rules:
  - host: blog.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: blog-app
            port:
              number: 80
```

### 2. Application with Sidecars Output

**DSL Code:**
```python
app = (App("web-server")
    .image("nginx:alpine")
    .port(80)
    .add_companion(
        Companion("log-collector")
            .image("fluentd:latest")
            .type("sidecar")
            .mount_shared_volume("/var/log")
    )
    .add_storage(
        Storage("shared-logs")
            .type("shared")
            .mount_path("/var/log")
    ))
```

**Generated Kubernetes YAML:**

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-server
  labels:
    app: web-server
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-server
  template:
    metadata:
      labels:
        app: web-server
    spec:
      containers:
      - name: web-server
        image: nginx:alpine
        ports:
        - containerPort: 80
          name: http
        volumeMounts:
        - name: shared-logs
          mountPath: /var/log
      - name: log-collector
        image: fluentd:latest
        volumeMounts:
        - name: shared-logs
          mountPath: /var/log
      volumes:
      - name: shared-logs
        emptyDir: {}
```

### 3. StatefulApp Output

**DSL Code:**
```python
postgres = (StatefulApp("postgres")
    .image("postgres:13")
    .port(5432)
    .storage("20Gi")
    .replicas(1)
    .environment({
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "admin"
    })
    .backup_schedule("0 2 * * *"))
```

**Generated Kubernetes YAML:**

```yaml
# statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  labels:
    app: postgres
    type: stateful
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:13
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: myapp
        - name: POSTGRES_USER
          value: admin
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretRef:
              name: postgres-credentials
              key: password
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 20Gi
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres
spec:
  type: ClusterIP
  ports:
  - port: 5432
    targetPort: postgres
  selector:
    app: postgres
---
# backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: postgres:13
            command: ["/bin/bash"]
            args:
            - -c
            - "pg_dump -h postgres -U admin myapp > /backup/backup-$(date +%Y%m%d).sql"
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backup
          restartPolicy: OnFailure
```

### 4. Secrets Output

**DSL Code:**
```python
# Database credentials and API keys
db_secret = (Secret("database-credentials")
    .add("username", "admin")
    .add("password", "super-secret-password")
    .add("connection-string", "postgresql://admin:password@postgres:5432/myapp")
    .mount_as_env_vars(prefix="DB_"))

api_secret = (Secret("api-keys")
    .add("stripe_key", "sk_live_...")
    .add("jwt_secret", "...")
    .from_file("tls.crt", "./certs/app.crt")
    .from_file("tls.key", "./certs/app.key")
    .type("tls"))

app.add_secrets([db_secret, api_secret])
```

**Generated Kubernetes YAML:**

```yaml
# secret-database-credentials.yaml
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  labels:
    app: myapp
    generated-by: k8s-gen
type: Opaque
data:
  username: YWRtaW4=  # base64 encoded
  password: c3VwZXItc2VjcmV0LXBhc3N3b3Jk  # base64 encoded
  connection-string: cG9zdGdyZXNxbDovL2FkbWluOnBhc3N3b3JkQHBvc3RncmVzOjU0MzIvbXlhcHA=
---
# secret-api-keys.yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  labels:
    app: myapp
type: kubernetes.io/tls
data:
  stripe_key: c2tfbGl2ZV8uLi4=
  jwt_secret: Li4u
  tls.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0t...
  tls.key: LS0tLS1CRUdJTiBQUklWQVRFIEtFWS0tLS0t...
---
# Updated deployment.yaml (with secrets)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        env:
        - name: DB_USERNAME
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: username
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: password
        - name: DB_CONNECTION_STRING
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: connection-string
        volumeMounts:
        - name: api-keys
          mountPath: /etc/ssl/certs
          readOnly: true
      volumes:
      - name: api-keys
        secret:
          secretName: api-keys
```

### 5. Jobs and CronJobs Output

**DSL Code:**
```python
# Database migration job
migration = (Job("db-migration")
    .image("myapp/migrator:latest")
    .command(["python", "migrate.py", "--up"])
    .timeout("10m")
    .on_success(cleanup=True))

# Scheduled backup
backup_job = (CronJob("daily-backup")
    .image("postgres:13")
    .schedule("0 2 * * *")
    .command(["sh", "-c", "pg_dump -h postgres mydb > /backup/backup-$(date +%Y%m%d).sql"])
    .retention_limit(successful=7, failed=3))

app.add_jobs([migration, backup_job])
```

**Generated Kubernetes YAML:**

```yaml
# job-db-migration.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
  labels:
    app: myapp
    component: migration
spec:
  template:
    metadata:
      labels:
        app: myapp
        component: migration
    spec:
      restartPolicy: Never
      containers:
      - name: db-migration
        image: myapp/migrator:latest
        command: ["python", "migrate.py", "--up"]
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
      activeDeadlineSeconds: 600
  backoffLimit: 3
  ttlSecondsAfterFinished: 100
---
# cronjob-daily-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: daily-backup
  labels:
    app: myapp
    component: backup
spec:
  schedule: "0 2 * * *"
  successfulJobsHistoryLimit: 7
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        metadata:
          labels:
            app: myapp
            component: backup
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: postgres:13
            command:
            - sh
            - -c
            - "pg_dump -h postgres mydb > /backup/backup-$(date +%Y%m%d).sql"
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

### 6. Advanced Ingress Output

**DSL Code:**
```python
# Multi-service routing with advanced features
api_ingress = (Ingress("api-gateway")
    .host("api.mycompany.com")
    .path("/api/v1/users", user_service, port=8080)
    .path("/api/v1/products", product_service, port=8081)
    .ssl_certificate(cert_manager="letsencrypt-prod")
    .rate_limiting(requests_per_minute=1000)
    .cors(origins=["https://myapp.com"])
    .middleware(["auth", "logging"]))

app.add_ingress([api_ingress])
```

**Generated Kubernetes YAML:**

```yaml
# ingress-api-gateway.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api-gateway
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://myapp.com"
    nginx.ingress.kubernetes.io/cors-allow-methods: "GET, POST, PUT, DELETE, OPTIONS"
    nginx.ingress.kubernetes.io/cors-allow-headers: "Authorization, Content-Type"
    nginx.ingress.kubernetes.io/auth-url: "http://auth-service.default.svc.cluster.local/auth"
    nginx.ingress.kubernetes.io/configuration-snippet: |
      more_set_headers "X-Request-ID: $req_id";
      access_log /var/log/nginx/api-access.log main;
spec:
  tls:
  - hosts:
    - api.mycompany.com
    secretName: api-gateway-tls
  rules:
  - host: api.mycompany.com
    http:
      paths:
      - path: /api/v1/users
        pathType: Prefix
        backend:
          service:
            name: user-service
            port:
              number: 8080
      - path: /api/v1/products
        pathType: Prefix
        backend:
          service:
            name: product-service
            port:
              number: 8081
```

### 7. RBAC Output

**DSL Code:**
```python
# Service account and RBAC
service_account = ServiceAccount("app-service-account")
app_role = (Role("app-role")
    .allow("get", "list", "watch").on("pods", "services")
    .allow("create", "update").on("configmaps"))

app.rbac(service_account=service_account, roles=[app_role])
```

**Generated Kubernetes YAML:**

```yaml
# serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: default
  labels:
    app: myapp
    generated-by: k8s-gen
automountServiceAccountToken: false
---
# role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: app-role
  namespace: default
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
- apiGroups: [""]
  resources: ["configmaps"]
  verbs: ["create", "update"]
---
# rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-role-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: default
roleRef:
  kind: Role
  name: app-role
  apiGroup: rbac.authorization.k8s.io
---
# Updated deployment.yaml (with service account)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      serviceAccountName: app-service-account
      automountServiceAccountToken: false
      containers:
      - name: myapp
        image: myapp:latest
```

### 8. ConfigMap Output

**DSL Code:**
```python
# Multi-format configuration
config = (ConfigMap("app-config")
    .add("database_url", "postgresql://localhost:5432/myapp")
    .add("api_key", "your-api-key-here")
    .add_json("features", {
        "feature_a": True,
        "feature_b": False,
        "limits": {"max_users": 1000}
    })
    .from_file("nginx.conf", "./config/nginx.conf")
    .mount_path("/etc/config"))

app.add_config([config])
```

**Generated Kubernetes YAML:**

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  labels:
    app: myapp
    generated-by: k8s-gen
data:
  database_url: "postgresql://localhost:5432/myapp"
  api_key: "your-api-key-here"
  features.json: |
    {
      "feature_a": true,
      "feature_b": false,
      "limits": {
        "max_users": 1000
      }
    }
  nginx.conf: |
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html;
        }
    }
---
# Updated deployment.yaml (with config mount)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  template:
    spec:
      containers:
      - name: myapp
        image: myapp:latest
        volumeMounts:
        - name: app-config
          mountPath: /etc/config
          readOnly: true
      volumes:
      - name: app-config
        configMap:
          name: app-config
          defaultMode: 0644
```

## Docker Compose Output Examples

### 1. Simple Docker Compose Output

**DSL Code:**
```python
# Create configuration
wp_config = ConfigMap("wordpress-config").add("WORDPRESS_DB_HOST", "mysql")

# Create database
mysql = (StatefulApp("mysql")
    .image("mysql:8.0")
    .port(3306)
    .storage("20Gi")
    .environment({"MYSQL_DATABASE": "blog", "MYSQL_ROOT_PASSWORD": "secret"}))

# Create web app
web_app = (App("blog-app")
    .image("wordpress:latest")
    .port(80)
    .connect_to([mysql])
    .add_config([wp_config])
    .scale(replicas=2)
    .expose(external_access=True))

# Generate Docker Compose
web_app.generate().to_docker_compose("./docker-compose.yml")
```

**Generated Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    container_name: mysql
    restart: unless-stopped
    ports:
      - "3306:3306"
    environment:
      MYSQL_DATABASE: blog
      MYSQL_ROOT_PASSWORD: secret
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - app-network
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      timeout: 20s
      retries: 10

  blog-app:
    image: wordpress:latest
    container_name: blog-app
    restart: unless-stopped
    ports:
      - "80:80"
    environment:
      WORDPRESS_DB_HOST: mysql
    volumes:
      - ./config/wordpress-config:/etc/wordpress:ro
    networks:
      - app-network
    depends_on:
      mysql:
        condition: service_healthy
    deploy:
      replicas: 2
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

volumes:
  mysql_data:
    driver: local

networks:
  app-network:
    driver: bridge
```

**Docker Compose Override for Development:**
```yaml
# docker-compose.override.yml (for development)
version: '3.8'

services:
  mysql:
    ports:
      - "3306:3306"  # Expose MySQL port for debugging
    volumes:
      - ./mysql-dev-data:/var/lib/mysql  # Use local directory

  blog-app:
    ports:
      - "8080:80"  # Different port for development
    volumes:
      - ./wp-content:/var/www/html/wp-content  # Mount source code
    environment:
      WORDPRESS_DEBUG: 1
    deploy:
      replicas: 1  # Single instance for development
```

**Docker Compose for Production:**
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  mysql:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  blog-app:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 5
    environment:
      WORDPRESS_DEBUG: 0
```

### 2. Microservices Docker Compose Output

**DSL Code:**
```python
microservices = AppGroup("ecommerce")

# Stateful services
postgres = StatefulApp("postgres").image("postgres:13").storage("20Gi")
redis = StatefulApp("redis").image("redis:alpine").storage("5Gi")

# Microservices
user_service = (App("user-service")
    .image("mycompany/users:v1.0.0")
    .port(8080)
    .connect_to([postgres, redis]))

product_service = (App("product-service")
    .image("mycompany/products:v1.0.0")
    .port(8081)
    .connect_to([postgres]))

api_gateway = (App("api-gateway")
    .image("nginx:alpine")
    .port(80)
    .depends_on([user_service, product_service])
    .expose(external_access=True))

microservices.add_services([postgres, redis, user_service, product_service, api_gateway])
microservices.generate().to_docker_compose("./docker-compose.yml")
```

**Generated Docker Compose:**

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:13
    container_name: ecommerce-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: ecommerce
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secret}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ecommerce-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d ecommerce"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:alpine
    container_name: ecommerce-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - ecommerce-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  user-service:
    image: mycompany/users:v1.0.0
    container_name: ecommerce-user-service
    restart: unless-stopped
    ports:
      - "8080:8080"
    environment:
      DB_HOST: postgres
      REDIS_HOST: redis
      SPRING_PROFILES_ACTIVE: docker
    networks:
      - ecommerce-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  product-service:
    image: mycompany/products:v1.0.0
    container_name: ecommerce-product-service
    restart: unless-stopped
    ports:
      - "8081:8081"
    environment:
      DB_HOST: postgres
      SPRING_PROFILES_ACTIVE: docker
    networks:
      - ecommerce-network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8081/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  api-gateway:
    image: nginx:alpine
    container_name: ecommerce-api-gateway
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - ecommerce-network
    depends_on:
      user-service:
        condition: service_healthy
      product-service:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local

networks:
  ecommerce-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Helm Chart Output

### Generated Helm Chart Structure

**DSL Code:**
```python
app = (App("api-server")
    .image("mycompany/api:latest")
    .port(8080)
    .scale(replicas=3))

app.generate().to_helm_chart("./charts/api-server/")
```

**Generated Helm Chart Structure:**
```
charts/api-server/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── ingress.yaml
│   └── NOTES.txt
└── .helmignore
```

**Chart.yaml:**
```yaml
apiVersion: v2
name: api-server
description: A Helm chart for api-server generated by k8s-gen
type: application
version: 0.1.0
appVersion: "latest"
```

**values.yaml:**
```yaml
replicaCount: 3

image:
  repository: mycompany/api
  pullPolicy: IfNotPresent
  tag: "latest"

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: false
  className: ""
  annotations: {}
  hosts:
    - host: chart-example.local
      paths:
        - path: /
          pathType: Prefix
  tls: []

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80

resources: {}
nodeSelector: {}
tolerations: []
affinity: {}
```

**templates/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "api-server.fullname" . }}
  labels:
    {{- include "api-server.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "api-server.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "api-server.selectorLabels" . | nindent 8 }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: 8080
              protocol: TCP
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
```

## Output Format Mapping

| DSL Concept | Kubernetes Resources | Docker Compose Resources |
|-------------|---------------------|--------------------------|
| `App()` | Deployment + Service | Service definition |
| `StatefulApp()` | StatefulSet + Service + PVC + CronJob | Service with volumes + healthcheck |
| `Secret()` | Secret + Volume mounts + Env vars | Environment variables (secrets) |
| `ConfigMap()` | ConfigMap + Volume mounts | Environment variables + file mounts |
| `Job()` | Job | Run-once service with restart policy |
| `CronJob()` | CronJob | Scheduled service with cron-like timing |
| `Ingress()` | Ingress + Certificate + NetworkPolicy | Published ports + labels |
| `ServiceAccount()` | ServiceAccount + Role + RoleBinding | User and group settings |
| `.scale()` | HorizontalPodAutoscaler | Deploy replicas + restart_policy |
| `.expose(external_access=True)` | LoadBalancer Service + Ingress | Published ports |
| `.add_storage(type="persistent")` | PersistentVolumeClaim | Named volumes |
| `.add_storage(type="config")` | ConfigMap | File mounts + environment |
| `.add_storage(type="secret")` | Secret | Environment variables (secrets) |
| `.add_companion(type="sidecar")` | Additional container in Pod | Additional service in compose |
| `.add_companion(type="init")` | InitContainer in Pod | depends_on with init service |
| `.health()` | Liveness/Readiness Probes | healthcheck configuration |
| `.lifecycle()` | Lifecycle hooks (preStop, postStart) | restart_policy + stop_signal |
| `.security()` | SecurityContext + PodSecurityPolicy | user, security_opt settings |
| `.observability()` | ServiceMonitor + PrometheusRule + ConfigMap | logging and monitoring configs |
| `.deployment_strategy()` | Deployment strategy + Argo Rollouts | Deploy configuration |
| `.external_services()` | ExternalName Service + ConfigMap | external_links and networks |
| `AppGroup()` | Namespace + multiple Deployments/StatefulSets | Multiple services + networks |
| `.connect_to()` | Service references + environment variables | depends_on + networks + env vars |
| `.service_mesh()` | Service + VirtualService + DestinationRule | networks + external networks | 