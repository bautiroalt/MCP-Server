# NEW MCP Server - Unified Model Context Protocol Server

A comprehensive, production-ready Model Context Protocol (MCP) server that combines the best features from both the `app` and `MCP SERVER` implementations with **enhanced security, monitoring, and Docker support**.

## 🚀 Features

### Core MCP Functionality
- **Context Management**: Store and retrieve contextual information with TTL support
- **File Operations**: Upload, download, version, and process files
- **Real-time Streaming**: Server-Sent Events (SSE) for live data updates
- **Data Processing**: Extract and transform data from various sources
- **Authentication**: JWT-based authentication and user management
- **Monitoring**: Prometheus metrics, health checks, and performance tracking

### MCP Tools
- **read_file**: Read contents of files
- **write_file**: Write content to files
- **list_directory**: List directory contents
- **search_files**: Search files using glob patterns
- **🧠 meta_minds_analysis**: AI-powered data analytics with SMART question generation (97%+ quality)

### Advanced Features
- **File Versioning**: Complete file version history
- **Content Extraction**: Extract text from PDFs, Word docs, Excel files
- **Bulk Operations**: Efficient batch processing
- **Event Notifications**: Real-time context and file change notifications
- **Security**: CORS protection, rate limiting, input validation
- **Scalability**: Redis caching, async processing, horizontal scaling

### 🆕 **NEW: Production-Ready Features**
- **🐳 Docker Support**: Complete containerization with Dockerfile and docker-compose.yml
- **🔒 Enhanced Security**: Advanced security middleware, CSRF protection, input validation
- **📊 Advanced Monitoring**: System metrics, performance tracking, alerting
- **⚙️ Environment Configuration**: Comprehensive .env configuration
- **🛡️ Security Headers**: XSS protection, CSRF tokens, rate limiting
- **📈 Prometheus Integration**: Detailed metrics collection and monitoring
- **🔍 Health Checks**: Kubernetes-ready liveness and readiness probes
- **📝 Audit Logging**: Complete security and activity logging
- **🚨 Alert System**: Automated alerts for system issues
- **🧠 META-MINDS Analytics**: AI-powered data analysis with SMART questions ([GitHub](https://github.com/Jatin23K/META-MINDS))

## 🏗️ Architecture

```
NEW MCP/
├── backend/                 # FastAPI Backend Server
│   ├── app/
│   │   ├── main.py         # Main FastAPI application
│   │   ├── core/           # Core business logic
│   │   ├── api/            # API route handlers
│   │   │   ├── mcp_routes.py      # MCP tools
│   │   │   └── analytics_routes.py # META-MINDS analytics
│   │   ├── integrations/   # Third-party integrations
│   │   │   └── meta_minds.py      # META-MINDS integration
│   │   ├── workflows/      # Automated workflows
│   │   │   └── meta_minds_workflow.py
│   │   ├── models/         # Pydantic models
│   │   └── templates/      # HTML templates
│   ├── requirements.txt    # Python dependencies
│   └── env.example         # Environment configuration
├── frontend/               # React Frontend
│   ├── src/
│   │   ├── App.js         # Main React application
│   │   ├── components/    # React components
│   │   └── lib/           # Utility libraries
│   ├── package.json       # Node.js dependencies
│   └── tailwind.config.js # Tailwind CSS configuration
├── data/                   # Data storage
├── tests/                  # Test files
├── docs/                   # Documentation
└── firebase.json           # Firebase configuration
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (recommended)
- MongoDB (optional)
- Redis (optional)

### 🐳 **Docker Deployment (Recommended)**
```bash
# Clone the repository
git clone https://github.com/Jatin23K/MCP-Server.git
cd MCP-Server

# Copy environment configuration
cp config.env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### 🛠️ **Manual Setup**

#### Backend Setup
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp config.env.example .env
# Edit .env with your settings

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### 🌐 **Access Points**
- **MCP Interface**: http://localhost:3001/mcp-interface.html (Enhanced Web UI)
- **API Documentation**: http://localhost:8000/mcp/docs
- **Frontend Interface**: http://localhost:3000
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/mcp/api/v1/monitoring/metrics
- **META-MINDS Analytics**: http://localhost:3001/mcp-interface.html (Analytics Tab)
- **Prometheus**: http://localhost:9090
- **Grafana Dashboard**: http://localhost:3000 (Grafana)

## 📚 API Endpoints

### MCP Tools
- `GET /api/tools` - List available MCP tools
- `POST /api/execute` - Execute MCP tool

### Context Management
- `POST /mcp/api/v1/context` - Set context
- `GET /mcp/api/v1/context/{key}` - Get context
- `DELETE /mcp/api/v1/context/{key}` - Delete context

### File Management
- `POST /mcp/api/v1/files/upload` - Upload file
- `GET /mcp/api/v1/files/{path}` - Download file
- `GET /mcp/api/v1/files` - List files
- `DELETE /mcp/api/v1/files/{path}` - Delete file

### Real-time Streaming
- `GET /mcp/api/v1/stream/context` - Context changes
- `GET /mcp/api/v1/stream/files` - File events
- `GET /mcp/api/v1/stream/all` - All events

### Authentication
- `POST /mcp/api/v1/token` - Get JWT token
- `GET /mcp/api/v1/users/me` - Get current user

### Monitoring
- `GET /monitoring/health` - Comprehensive health check
- `GET /monitoring/health/live` - Kubernetes liveness probe
- `GET /monitoring/health/ready` - Kubernetes readiness probe
- `GET /monitoring/metrics` - Prometheus metrics
- `GET /monitoring/status` - Overall system status
- `GET /monitoring/alerts` - Current alerts
- `GET /monitoring/dashboard` - Dashboard data

## 🔧 Configuration

### Environment Variables
```env
# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development

# Security
JWT_SECRET_KEY=your-secret-key
API_KEY=your-api-key

# CORS
CORS_ORIGINS=http://localhost:3000
ALLOWED_HOSTS=localhost,127.0.0.1

# Data Storage
DATA_DIRECTORY=./data
LOG_FILE=fastmcp.log

# Redis (Optional)
REDIS_URL=redis://localhost:6379

# MongoDB (Optional)
MONGO_URL=mongodb://localhost:27017
DB_NAME=fastmcp
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/backend_test.py -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📈 Monitoring

- **Prometheus Metrics**: `/metrics` endpoint
- **Health Checks**: `/health` endpoint
- **System Monitoring**: CPU, memory, disk usage
- **Request Metrics**: Latency, throughput, error rates

## 🔒 Security

- **JWT Authentication**: Secure token-based auth
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error messages

## 🚀 Deployment

### 🐳 **Docker Deployment (Recommended)**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale services
docker-compose up -d --scale mcp-server=3

# Stop services
docker-compose down
```

### 🔥 **Firebase Deployment**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase project
firebase init

# Deploy
firebase deploy
```

### 🏭 **Production Deployment**

#### 1. **Docker Production Setup**
```bash
# Build production image
docker build -t mcp-server:latest .

# Run with production settings
docker run -d \
  --name mcp-server \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e JWT_SECRET_KEY=your-secret-key \
  mcp-server:latest
```

#### 2. **Kubernetes Deployment**
```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
      - name: mcp-server
        image: mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
```

#### 3. **Production Checklist**
- ✅ Use production WSGI server (Gunicorn)
- ✅ Configure reverse proxy (Nginx)
- ✅ Set up SSL (HTTPS)
- ✅ Configure monitoring (Prometheus and Grafana)
- ✅ Set up logging (Centralized logging)
- ✅ Configure security headers
- ✅ Set up rate limiting
- ✅ Configure backup strategy
- ✅ Set up alerting
- ✅ Configure auto-scaling

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the GNU General Public License v3.0.

**Copyright (c) 2024 Jatin Kumar - All Rights Reserved**

This is free software licensed under GPL v3. You can redistribute it and/or modify it under the terms of the GNU GPL v3. Any derivative works must also be licensed under GPL v3.

For the full license text, see the [LICENSE](LICENSE) file or visit https://www.gnu.org/licenses/gpl-3.0.en.html

## 🆘 Support

- **Documentation**: Check the docs/ folder
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions

---

**NEW MCP Server** - The unified, production-ready Model Context Protocol server that combines the best of both worlds! 🚀