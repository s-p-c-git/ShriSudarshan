# Deployment Guide - Project Shri Sudarshan

## Overview

This guide covers deploying Project Shri Sudarshan in various environments, from local development to production cloud deployments.

## Table of Contents

- [Deployment Options](#deployment-options)
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Cloud Deployments](#cloud-deployments)
- [Production Considerations](#production-considerations)
- [Monitoring and Logging](#monitoring-and-logging)

---

## Deployment Options

### Comparison

| Option | Use Case | Complexity | Scalability | Cost |
|--------|----------|------------|-------------|------|
| Local | Development, testing | Low | None | Free |
| Docker | Single server, consistent environment | Medium | Limited | Low |
| Kubernetes | Multi-server, high availability | High | Excellent | Medium-High |
| Cloud VM | Simple production | Low-Medium | Manual | Medium |
| Cloud Managed | Production at scale | Medium | Automatic | High |

---

## Local Development

### Quick Start

```bash
# Clone repository
git clone https://github.com/s-p-c-git/ShriSudarshan.git
cd ShriSudarshan

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run system
cd src
python main.py --symbol AAPL
```

### Running as Service

Use systemd on Linux:

```ini
# /etc/systemd/system/shrisudarshan.service
[Unit]
Description=Shri Sudarshan Trading System
After=network.target

[Service]
Type=simple
User=trading
WorkingDirectory=/opt/shrisudarshan
Environment="PATH=/opt/shrisudarshan/venv/bin"
ExecStart=/opt/shrisudarshan/venv/bin/python src/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable shrisudarshan
sudo systemctl start shrisudarshan
sudo systemctl status shrisudarshan
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY .env.example .env

# Create data directories
RUN mkdir -p /app/data /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Expose port (if adding web interface)
# EXPOSE 8000

# Run application
CMD ["python", "src/main.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  shrisudarshan:
    build: .
    container_name: shrisudarshan
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      # Persist databases
      - ./data:/app/data
      # Persist logs
      - ./logs:/app/logs
      # Mount source for development
      - ./src:/app/src
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO
    # Uncomment if adding web interface
    # ports:
    #   - "8000:8000"
    networks:
      - trading-network
    depends_on:
      - redis
      - postgres

  # Optional: Redis for caching and working memory
  redis:
    image: redis:7-alpine
    container_name: shrisudarshan-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - trading-network

  # Optional: PostgreSQL for episodic memory
  postgres:
    image: postgres:15-alpine
    container_name: shrisudarshan-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: shrisudarshan
      POSTGRES_USER: trading
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - trading-network

volumes:
  redis-data:
  postgres-data:

networks:
  trading-network:
    driver: bridge
```

### Building and Running

```bash
# Build image
docker-compose build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f shrisudarshan

# Stop
docker-compose down

# Restart specific service
docker-compose restart shrisudarshan
```

### Docker Production Configuration

Update `.env` for production:

```bash
# Use PostgreSQL instead of SQLite
EPISODIC_MEMORY_DB=postgresql://trading:password@postgres:5432/shrisudarshan

# Use Redis for working memory
REDIS_URL=redis://redis:6379/0

# Set production logging
LOG_LEVEL=INFO
ENABLE_CONCURRENT_ANALYSIS=true

# Production models
PREMIUM_MODEL=gpt-4o
STANDARD_MODEL=gpt-4o-mini

# Risk parameters (conservative)
MAX_POSITION_SIZE=0.03
MAX_PORTFOLIO_RISK=0.015
MAX_SECTOR_CONCENTRATION=0.20
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (minikube, GKE, EKS, AKS)
- kubectl configured
- Docker images pushed to registry

### Kubernetes Manifests

#### Namespace

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: trading
```

#### ConfigMap

```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: shrisudarshan-config
  namespace: trading
data:
  LOG_LEVEL: "INFO"
  ENABLE_CONCURRENT_ANALYSIS: "true"
  MAX_DEBATE_ROUNDS: "3"
  PREMIUM_MODEL: "gpt-4o"
  STANDARD_MODEL: "gpt-4o-mini"
```

#### Secret

```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: shrisudarshan-secrets
  namespace: trading
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-your-key-here"
  DB_PASSWORD: "your-db-password"
```

Create from command:
```bash
kubectl create secret generic shrisudarshan-secrets \
  --from-literal=OPENAI_API_KEY=sk-your-key \
  --from-literal=DB_PASSWORD=your-password \
  -n trading
```

#### PersistentVolumeClaim

```yaml
# k8s/pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: shrisudarshan-data
  namespace: trading
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: standard
```

#### Deployment

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: shrisudarshan
  namespace: trading
  labels:
    app: shrisudarshan
spec:
  replicas: 1  # Single instance for now
  selector:
    matchLabels:
      app: shrisudarshan
  template:
    metadata:
      labels:
        app: shrisudarshan
    spec:
      containers:
      - name: shrisudarshan
        image: your-registry/shrisudarshan:latest
        imagePullPolicy: Always
        envFrom:
        - configMapRef:
            name: shrisudarshan-config
        - secretRef:
            name: shrisudarshan-secrets
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 30
          periodSeconds: 60
        readinessProbe:
          exec:
            command:
            - python
            - -c
            - "import sys; sys.exit(0)"
          initialDelaySeconds: 10
          periodSeconds: 30
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: shrisudarshan-data
      - name: logs
        emptyDir: {}
```

#### Service (Optional - for web interface)

```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: shrisudarshan
  namespace: trading
spec:
  selector:
    app: shrisudarshan
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer  # or ClusterIP for internal only
```

### Deploying to Kubernetes

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply configurations
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml

# Deploy application
kubectl apply -f k8s/deployment.yaml

# (Optional) Expose service
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -n trading
kubectl logs -f deployment/shrisudarshan -n trading

# Scale (if supporting multiple instances)
kubectl scale deployment shrisudarshan --replicas=3 -n trading
```

### Kubernetes Production Tips

1. **Use Helm** for easier management:
   ```bash
   helm create shrisudarshan
   # Edit templates
   helm install shrisudarshan ./shrisudarshan -n trading
   ```

2. **Set resource limits** to prevent OOM:
   - Minimum: 1GB RAM, 0.5 CPU
   - Recommended: 2GB RAM, 1 CPU

3. **Use HorizontalPodAutoscaler** for scaling:
   ```yaml
   apiVersion: autoscaling/v2
   kind: HorizontalPodAutoscaler
   metadata:
     name: shrisudarshan-hpa
     namespace: trading
   spec:
     scaleTargetRef:
       apiVersion: apps/v1
       kind: Deployment
       name: shrisudarshan
     minReplicas: 1
     maxReplicas: 5
     metrics:
     - type: Resource
       resource:
         name: cpu
         target:
           type: Utilization
           averageUtilization: 70
   ```

---

## Cloud Deployments

### AWS Deployment

#### EC2 Instance

1. **Launch EC2** (t3.medium or larger)
2. **Install dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv git
   ```
3. **Clone and setup** as per local deployment
4. **Use systemd** to run as service
5. **Setup CloudWatch** for logs (optional)

#### ECS (Elastic Container Service)

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Create ECS service
4. Use RDS for PostgreSQL
5. Use ElastiCache for Redis

#### Lambda (Limited Use)

Not recommended for full system due to:
- 15-minute timeout
- Cold starts
- Complex orchestration

Possible for individual agents as functions.

### Google Cloud Platform

#### Compute Engine

Similar to AWS EC2:
1. Create VM instance
2. Setup application
3. Use Cloud SQL for database
4. Use Memorystore for Redis

#### Google Kubernetes Engine (GKE)

1. Create GKE cluster
2. Use Kubernetes manifests (see above)
3. Use Cloud SQL Proxy for database
4. Store secrets in Secret Manager

#### Cloud Run

For containerized deployment:
```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/shrisudarshan

# Deploy
gcloud run deploy shrisudarshan \
  --image gcr.io/PROJECT_ID/shrisudarshan \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --cpu 1 \
  --timeout 3600 \
  --set-env-vars OPENAI_API_KEY=sk-xxx
```

### Azure Deployment

#### Virtual Machines

1. Create Ubuntu VM
2. Setup similar to local deployment
3. Use Azure Database for PostgreSQL
4. Use Azure Cache for Redis

#### Azure Kubernetes Service (AKS)

1. Create AKS cluster
2. Apply Kubernetes manifests
3. Use Azure SQL or PostgreSQL
4. Store secrets in Key Vault

#### Azure Container Instances

For simpler containerized deployment:
```bash
az container create \
  --resource-group trading-rg \
  --name shrisudarshan \
  --image your-registry/shrisudarshan:latest \
  --cpu 1 --memory 2 \
  --environment-variables \
    OPENAI_API_KEY=sk-xxx
```

---

## Production Considerations

### Security

1. **API Key Management**:
   - Use secrets manager (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault)
   - Rotate keys regularly
   - Never commit keys to repository

2. **Network Security**:
   - Use VPC/private networks
   - Restrict ingress/egress
   - Enable encryption in transit

3. **Access Control**:
   - Use IAM roles
   - Principle of least privilege
   - Enable MFA for admin access

4. **Data Encryption**:
   - Encrypt databases at rest
   - Encrypt backups
   - Use TLS for all communications

### High Availability

1. **Database**:
   - Use managed database service (RDS, Cloud SQL)
   - Enable automatic backups
   - Set up read replicas

2. **Application**:
   - Run multiple instances (if stateless)
   - Use load balancer
   - Implement health checks

3. **Disaster Recovery**:
   - Regular backups
   - Cross-region replication
   - Documented recovery procedures

### Scalability

1. **Horizontal Scaling**:
   - Stateless design allows multiple instances
   - Use message queue for work distribution
   - Load balance across instances

2. **Vertical Scaling**:
   - Increase CPU/RAM as needed
   - Monitor resource usage
   - Set appropriate limits

3. **Database Scaling**:
   - Use connection pooling
   - Implement caching (Redis)
   - Consider read replicas

### Cost Optimization

1. **Compute**:
   - Use spot/preemptible instances for non-critical workloads
   - Schedule downtime for dev/test environments
   - Right-size instances

2. **Storage**:
   - Use appropriate storage tiers
   - Clean up old data
   - Compress logs

3. **API Costs**:
   - Cache responses where possible
   - Use cheaper models for routine tasks
   - Implement rate limiting

---

## Monitoring and Logging

### Application Logging

**Structured logging** is already implemented with structlog.

Configure log destinations:

```python
# src/utils/logger.py
import structlog

# Add file handler
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
)
```

### Metrics Collection

Integrate Prometheus for metrics:

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
trade_counter = Counter('trades_total', 'Total trades executed')
analysis_duration = Histogram('analysis_duration_seconds', 'Analysis duration')

# Use in code
@analysis_duration.time()
async def analyze(self, context):
    # ... analysis code
    pass

trade_counter.inc()
```

### Monitoring Stack

#### Option 1: Prometheus + Grafana

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus-data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin

volumes:
  prometheus-data:
  grafana-data:
```

#### Option 2: Cloud Native

- **AWS**: CloudWatch
- **GCP**: Cloud Monitoring
- **Azure**: Azure Monitor

### Alerting

Set up alerts for:
- System errors
- API failures
- High resource usage
- Trade execution failures
- Risk limit breaches

Example Prometheus alert:
```yaml
groups:
- name: shrisudarshan
  rules:
  - alert: HighErrorRate
    expr: rate(errors_total[5m]) > 0.1
    for: 5m
    annotations:
      summary: "High error rate detected"
```

---

## Backup and Recovery

### Database Backups

**Automated backups**:
```bash
# Cron job for daily backups
0 2 * * * pg_dump shrisudarshan > /backups/db_$(date +\%Y\%m\%d).sql
```

**Managed service backups**:
- AWS RDS: Automatic daily snapshots
- GCP Cloud SQL: Automated backups
- Azure Database: Point-in-time restore

### Application State

Backup critical files:
- Database files
- Configuration files
- Logs (recent)
- Trade history

### Recovery Procedures

1. **Database restore**:
   ```bash
   psql shrisudarshan < backup.sql
   ```

2. **Application redeploy**:
   - Pull latest code
   - Restore configuration
   - Restart services

3. **Verify integrity**:
   - Check logs
   - Test connectivity
   - Verify data consistency

---

## Performance Tuning

### Database

- Index frequently queried columns
- Use connection pooling
- Optimize queries
- Regular VACUUM (PostgreSQL)

### Application

- Enable caching
- Use concurrent execution
- Optimize LLM prompts
- Batch operations

### Network

- Use CDN for static assets
- Enable compression
- Minimize API calls
- Use regional endpoints

---

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs, check alerts
- **Weekly**: Review performance, update dependencies
- **Monthly**: Security patches, backup verification
- **Quarterly**: Cost review, architecture review

### Updates

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Run tests
pytest tests/

# Restart service
sudo systemctl restart shrisudarshan
```

---

## Troubleshooting Deployment

See [Troubleshooting Guide](TROUBLESHOOTING.md) for common issues.

**Deployment-specific issues**:

- Container won't start: Check logs with `docker logs`
- Kubernetes pod failing: Check with `kubectl describe pod`
- Permission errors: Verify file ownership and permissions
- Network connectivity: Check firewall rules and security groups
- Database connection: Verify connection string and credentials

---

## Next Steps

1. Choose deployment option based on requirements
2. Set up monitoring and logging
3. Implement backup strategy
4. Document runbooks for operations
5. Test disaster recovery procedures

---

*Last updated: 2025-11-02*
