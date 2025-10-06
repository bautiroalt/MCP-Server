# 🚀 Deployment Files

This folder contains all deployment-related files for the MCP Server.

## 📁 Files:

- **`docker-compose.yml`** - Docker Compose configuration
- **`Dockerfile`** - Docker container configuration
- **`deploy-firebase.md`** - Firebase deployment guide
- **`firebase.json`** - Firebase configuration
- **`.firebaserc`** - Firebase project settings
- **`storage.rules`** - Firebase Storage security rules

## 🐳 Docker Deployment:

```bash
# Start all services
docker-compose up -d

# Services included:
# - MCP Server (FastAPI)
# - MongoDB
# - Redis
# - Nginx
# - Prometheus
# - Grafana
```

## 🔥 Firebase Deployment:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Deploy to Firebase
firebase deploy
```

## 📊 Monitoring:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **MCP Server**: http://localhost:8000
