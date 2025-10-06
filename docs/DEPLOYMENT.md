# NEW MCP Server - Deployment Guide

## Overview

This guide covers deploying the NEW MCP Server in various environments, from development to production. The server combines MCP tools, context management, file operations, and real-time streaming capabilities.

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher (for frontend)
- **Memory**: 1GB+ RAM recommended
- **Storage**: 1GB+ disk space
- **Network**: Port 8000 (backend), Port 3000 (frontend)

### Optional Dependencies
- **MongoDB**: For user data persistence
- **Redis**: For caching and session storage
- **Nginx**: For reverse proxy and load balancing

## Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd "NEW MCP"
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp env.example .env
# Edit .env with your settings
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Run Development Servers
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend
npm start
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/mcp/docs
- **Health Check**: http://localhost:8000/health

## Environment Configuration

### Backend Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Server Configuration
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Security
JWT_SECRET_KEY=your-secret-key-here-change-in-production
API_KEY=your-api-key-here
API_KEY_NAME=X-API-Key

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
ALLOWED_HOSTS=localhost,127.0.0.1

# Data Storage
DATA_DIRECTORY=./data
LOG_FILE=fastmcp.log

# Redis (Optional - for caching)
REDIS_URL=redis://localhost:6379

# MongoDB (Optional - for user data)
MONGO_URL=mongodb://localhost:27017
DB_NAME=fastmcp

# User Management
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$your-hashed-password-here

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10

# File Upload Limits
MAX_FILE_SIZE=1073741824  # 1GB in bytes
ALLOWED_EXTENSIONS=txt,pdf,png,jpg,jpeg,gif,csv,json,yaml,yml,xlsx,xls,doc,docx,py,js,html,css,md

# Monitoring
ENABLE_METRICS=true
METRICS_PATH=/metrics
HEALTH_CHECK_PATH=/health
```

### Frontend Environment Variables

Create a `.env` file in the `frontend` directory:

```env
REACT_APP_BACKEND_URL=http://localhost:8000
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_MCP_API_URL=http://localhost:8000/mcp/api/v1
```

## Production Deployment

### 1. Docker Deployment

#### Dockerfile for Backend
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p data/context data/files data/users data/tmp data/versions

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile for Frontend
```dockerfile
FROM node:16-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - MONGO_URL=mongodb://mongo:27017
    depends_on:
      - redis
      - mongo
    volumes:
      - ./data:/app/data

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  redis_data:
  mongo_data:
```

### 2. Manual Production Deployment

#### Backend Deployment
```bash
# 1. Install production dependencies
pip install gunicorn

# 2. Create production configuration
cat > gunicorn.conf.py << EOF
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
EOF

# 3. Run with Gunicorn
gunicorn -c gunicorn.conf.py app.main:app
```

#### Frontend Deployment
```bash
# 1. Build for production
npm run build

# 2. Serve with a web server (Nginx, Apache, etc.)
# Copy build/ directory to web server root
```

### 3. Nginx Configuration

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MCP API
    location /mcp/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }

    # Metrics
    location /metrics {
        proxy_pass http://backend;
        proxy_set_header Host $host;
    }
}
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS
```yaml
# task-definition.json
{
  "family": "new-mcp-server",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/new-mcp-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/new-mcp-server",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Using AWS Lambda (Serverless)
```python
# lambda_handler.py
from mangum import Mangum
from app.main import app

handler = Mangum(app)
```

### Google Cloud Deployment

#### Using Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/new-mcp-server', './backend']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/new-mcp-server']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['run', 'deploy', 'new-mcp-server', '--image', 'gcr.io/$PROJECT_ID/new-mcp-server', '--platform', 'managed', '--region', 'us-central1']
```

### Azure Deployment

#### Using Azure Container Instances
```yaml
# azure-deployment.yaml
apiVersion: 2018-10-01
location: eastus
name: new-mcp-server
properties:
  containers:
  - name: backend
    properties:
      image: your-registry.azurecr.io/new-mcp-backend:latest
      resources:
        requests:
          cpu: 1
          memoryInGb: 1
      ports:
      - port: 8000
  osType: Linux
  restartPolicy: Always
```

## Monitoring and Logging

### Prometheus Metrics
The server exposes metrics at `/metrics` endpoint:

```bash
# Example metrics
fastmcp_request_total 1000
fastmcp_request_latency_seconds_bucket{le="0.1"} 800
fastmcp_active_connections 5
fastmcp_system_memory_bytes 1048576
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "NEW MCP Server Dashboard",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(fastmcp_request_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(fastmcp_request_latency_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      }
    ]
  }
}
```

### Logging Configuration
```python
# logging_config.py
import logging
import logging.handlers

def setup_logging():
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        'new_mcp.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
```

## Security Considerations

### SSL/TLS Configuration
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}
```

### Security Headers
```python
# security_middleware.py
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["your-domain.com", "*.your-domain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## Backup and Recovery

### Database Backup
```bash
# MongoDB backup
mongodump --host localhost:27017 --db fastmcp --out /backup/mongodb/

# Redis backup
redis-cli --rdb /backup/redis/dump.rdb
```

### File System Backup
```bash
# Backup data directory
tar -czf backup-$(date +%Y%m%d).tar.gz data/

# Restore
tar -xzf backup-20240101.tar.gz
```

### Automated Backup Script
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR/$DATE

# Backup MongoDB
mongodump --host localhost:27017 --db fastmcp --out $BACKUP_DIR/$DATE/mongodb/

# Backup Redis
redis-cli --rdb $BACKUP_DIR/$DATE/redis/dump.rdb

# Backup files
tar -czf $BACKUP_DIR/$DATE/files.tar.gz data/

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in configuration
export PORT=8001
```

#### 2. Permission Denied
```bash
# Fix file permissions
chmod -R 755 data/
chown -R www-data:www-data data/
```

#### 3. Memory Issues
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Increase swap if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### 4. Database Connection Issues
```bash
# Check MongoDB status
systemctl status mongod

# Check Redis status
systemctl status redis

# Test connections
mongo --host localhost:27017
redis-cli ping
```

### Performance Tuning

#### 1. Database Optimization
```python
# MongoDB indexes
db.context.create_index("key")
db.context.create_index("ttl")
db.files.create_index("file_path")
db.users.create_index("username")
```

#### 2. Redis Configuration
```conf
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

#### 3. Application Tuning
```python
# gunicorn.conf.py
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
timeout = 30
keepalive = 2
```

## Scaling

### Horizontal Scaling
```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: new-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: new-mcp-server
  template:
    metadata:
      labels:
        app: new-mcp-server
    spec:
      containers:
      - name: backend
        image: new-mcp-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: MONGO_URL
          value: "mongodb://mongo-service:27017"
```

### Load Balancer Configuration
```yaml
# nginx-load-balancer.conf
upstream backend {
    least_conn;
    server backend-1:8000;
    server backend-2:8000;
    server backend-3:8000;
}

server {
    listen 80;
    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## Maintenance

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
mongo --eval "db.adminCommand('ping')"
redis-cli ping

# Disk space
df -h

# Memory usage
free -h
```

### Updates
```bash
# Update application
git pull origin main
pip install -r requirements.txt
systemctl restart new-mcp-server

# Database migrations
python migrate.py

# Clear caches
redis-cli FLUSHALL
```

---

For more information, see the [API documentation](API.md) or [development guide](DEVELOPMENT.md).
