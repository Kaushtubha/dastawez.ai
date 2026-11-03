# DEPLOYMENT GUIDE

## Production Deployment Options for DocuMind AI

This guide covers multiple deployment strategies for production environments.

---

## 📋 Table of Contents

1. [Docker Deployment (Recommended)](#docker-deployment-recommended)
2. [Cloud Platform Deployment](#cloud-platform-deployment)
3. [VPS Deployment](#vps-deployment)
4. [Kubernetes Deployment](#kubernetes-deployment)
5. [Troubleshooting](#troubleshooting)

---

## Docker Deployment (Recommended)

### Prerequisites
- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- Git

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/documind-ai.git
cd documind-ai

# Configure environment
cp .env.example .env
# Edit .env with your production settings

# Build and deploy
docker-compose up -d --build

# Check logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Docker Configuration

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: documind-backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=production
      - DEBUG=False
    volumes:
      - uploads:/app/uploads
      - ./logs:/app/logs
    networks:
      - documind-network
    depends_on:
      - qdrant

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
    container_name: documind-frontend
    restart: always
    ports:
      - "80:80"
    networks:
      - documind-network
    depends_on:
      - backend

  qdrant:
    image: qdrant/qdrant:latest
    container_name: documind-qdrant
    restart: always
    ports:
      - "6333:6333"
    volumes:
      - qdrant_storage:/qdrant/storage
    networks:
      - documind-network

volumes:
  uploads:
  qdrant_storage:

networks:
  documind-network:
    driver: bridge
```

### SSL/HTTPS Configuration with Nginx

**nginx.conf:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Cloud Platform Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Build and push to ECR:**
```bash
aws ecr create-repository --repository-name documind-backend
aws ecr create-repository --repository-name documind-frontend

docker tag documind-backend:latest <account-id>.dkr.ecr.region.amazonaws.com/documind-backend:latest
docker push <account-id>.dkr.ecr.region.amazonaws.com/documind-backend:latest
```

2. **Create ECS Task Definitions**
3. **Deploy to ECS Cluster**
4. **Configure Application Load Balancer**
5. **Set up RDS for database (optional)**

#### Using Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

### Google Cloud Platform

#### Using Cloud Run

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT-ID/documind

# Deploy to Cloud Run
gcloud run deploy documind \
  --image gcr.io/PROJECT-ID/documind \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Microsoft Azure

#### Using Azure App Service

```bash
# Login to Azure
az login

# Create resource group
az group create --name DocuMindRG --location eastus

# Create App Service Plan
az appservice plan create --name DocuMindPlan --resource-group DocuMindRG --is-linux

# Deploy
az webapp up --resource-group DocuMindRG --plan DocuMindPlan
```

### Heroku

```bash
# Install Heroku CLI
npm install -g heroku

# Login
heroku login

# Create app
heroku create documind-ai

# Add PostgreSQL (optional)
heroku addons:create heroku-postgresql:hobby-dev

# Deploy
git push heroku main

# Open app
heroku open
```

---

## VPS Deployment (DigitalOcean, Linode, etc.)

### Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/yourusername/documind-ai.git
cd documind-ai
```

### Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH, HTTP, HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Check status
sudo ufw status
```

### Set up SSL with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal is configured automatically
# Test renewal
sudo certbot renew --dry-run
```

### Systemd Service (Alternative to Docker)

**/etc/systemd/system/documind-backend.service:**
```ini
[Unit]
Description=DocuMind AI Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/documind-ai
Environment="PATH=/var/www/documind-ai/.venv/bin"
ExecStart=/var/www/documind-ai/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable documind-backend
sudo systemctl start documind-backend
sudo systemctl status documind-backend
```

---

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster (GKE, EKS, AKS, or self-hosted)
- kubectl configured
- Helm (optional)

### Kubernetes Manifests

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: documind-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: documind-backend
  template:
    metadata:
      labels:
        app: documind-backend
    spec:
      containers:
      - name: backend
        image: your-registry/documind-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: APP_ENV
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: documind-backend-service
spec:
  selector:
    app: documind-backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f deployment.yaml

# Check deployment
kubectl get deployments
kubectl get pods
kubectl get services

# View logs
kubectl logs -l app=documind-backend
```

### Helm Chart (Optional)

```bash
# Create Helm chart
helm create documind-chart

# Package and deploy
helm package .
helm install documind ./documind-chart-0.1.0.tgz
```

---

## Troubleshooting

### Common Issues

**1. Container won't start:**
```bash
docker-compose logs backend
docker-compose logs frontend
```

**2. Database connection errors:**
```bash
# Check DATABASE_URL in .env
# Ensure database is accessible
```

**3. CORS issues:**
```bash
# Verify CORS_ORIGINS includes your frontend URL
# Check backend logs for CORS errors
```

**4. Port conflicts:**
```bash
# Change PORT in .env
# Update docker-compose.yml accordingly
```

**5. Memory issues:**
```bash
# Increase container memory limits
# Monitor with: docker stats
```

### Performance Optimization

- Use Redis for caching
- Enable Gzip compression
- Configure CDN for static assets
- Use connection pooling for database
- Implement horizontal scaling

### Monitoring & Logging

**Prometheus + Grafana:**
```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

---

## Security Best Practices

1. **Use environment variables** for sensitive data
2. **Enable HTTPS** in production
3. **Implement rate limiting**
4. **Regular security updates**
5. **Use secrets management** (Vault, AWS Secrets Manager)
6. **Configure firewalls** properly
7. **Enable logging and monitoring**
8. **Backup databases regularly**

---

## Support

For additional help:
- Open a GitHub issue
- Check documentation: `/docs`
- Contact: support@documind.ai

---

**Last Updated:** March 2024  
**Version:** 1.0.0
