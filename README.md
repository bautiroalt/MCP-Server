# NEW MCP Server - Unified Model Context Protocol Server

A comprehensive, production-ready Model Context Protocol (MCP) server that combines the best features from both the `app` and `MCP SERVER` implementations.

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

### Advanced Features
- **File Versioning**: Complete file version history
- **Content Extraction**: Extract text from PDFs, Word docs, Excel files
- **Bulk Operations**: Efficient batch processing
- **Event Notifications**: Real-time context and file change notifications
- **Security**: CORS protection, rate limiting, input validation
- **Scalability**: Redis caching, async processing, horizontal scaling

## 🏗️ Architecture

```
NEW MCP/
├── backend/                 # FastAPI Backend Server
│   ├── app/
│   │   ├── main.py         # Main FastAPI application
│   │   ├── core/           # Core business logic
│   │   ├── api/            # API route handlers
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
- MongoDB (optional)
- Redis (optional)

### Backend Setup
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

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Access Points
- **API Documentation**: http://localhost:8000/mcp/docs
- **Frontend Interface**: http://localhost:3000
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

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
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

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

### Docker Deployment
```bash
docker-compose up -d
```

### Firebase Deployment
```bash
firebase deploy
```

### Production Deployment
1. Use production WSGI server (Gunicorn)
2. Configure reverse proxy (Nginx)
3. Set up SSL (HTTPS)
4. Configure monitoring (Prometheus and Grafana)
5. Set up logging (Centralized logging)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

- **Documentation**: Check the docs/ folder
- **Issues**: Create GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions

---

**NEW MCP Server** - The unified, production-ready Model Context Protocol server that combines the best of both worlds! 🚀