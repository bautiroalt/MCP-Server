# NEW MCP Server - API Documentation

## Overview

The NEW MCP Server provides a comprehensive API for Model Context Protocol (MCP) operations, context management, file operations, and real-time streaming. This unified server combines the best features from both the `app` and `MCP SERVER` implementations.

## Base URLs

- **Main API**: `http://localhost:8000`
- **MCP Tools**: `http://localhost:8000/api`
- **Advanced Features**: `http://localhost:8000/mcp/api/v1`

## Authentication

The server supports multiple authentication methods:

### JWT Authentication
```bash
# Get token
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"

# Use token
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/mcp/api/v1/context"
```

### API Key Authentication (Optional)
```bash
curl -H "X-API-Key: your-api-key" \
     "http://localhost:8000/mcp/api/v1/context"
```

## MCP Tools API

### List Available Tools
```http
GET /api/tools
```

**Response:**
```json
{
  "tools": [
    {
      "name": "read_file",
      "description": "Read contents of a file",
      "parameters": {
        "file_path": {
          "type": "string",
          "description": "Path to the file to read"
        }
      }
    },
    {
      "name": "write_file",
      "description": "Write content to a file",
      "parameters": {
        "file_path": {
          "type": "string",
          "description": "Path to the file to write"
        },
        "content": {
          "type": "string",
          "description": "Content to write to the file"
        }
      }
    },
    {
      "name": "list_directory",
      "description": "List contents of a directory",
      "parameters": {
        "directory_path": {
          "type": "string",
          "description": "Path to the directory to list"
        }
      }
    },
    {
      "name": "search_files",
      "description": "Search for files matching a pattern",
      "parameters": {
        "directory": {
          "type": "string",
          "description": "Directory to search in"
        },
        "pattern": {
          "type": "string",
          "description": "Glob pattern to match files"
        }
      }
    }
  ]
}
```

### Execute MCP Tool
```http
POST /api/execute
```

**Request Body:**
```json
{
  "tool_name": "read_file",
  "arguments": {
    "file_path": "/path/to/file.txt"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": "File content here",
  "error": null,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Context Management API

### Set Context
```http
POST /mcp/api/v1/context
```

**Request Body:**
```json
{
  "key": "user:123:preferences",
  "value": {
    "theme": "dark",
    "notifications": true
  },
  "ttl": 3600,
  "metadata": {
    "source": "api"
  }
}
```

### Get Context
```http
GET /mcp/api/v1/context/{key}
```

### List Context
```http
GET /mcp/api/v1/context?prefix=user:&limit=100
```

### Delete Context
```http
DELETE /mcp/api/v1/context/{key}
```

### Bulk Context Operations
```http
POST /mcp/api/v1/context/bulk
```

**Request Body:**
```json
{
  "operation": "set",
  "items": [
    {
      "key": "key1",
      "value": "value1"
    },
    {
      "key": "key2",
      "value": "value2"
    }
  ]
}
```

## File Management API

### Upload File
```http
POST /mcp/api/v1/files/upload
Content-Type: multipart/form-data
```

### Download File
```http
GET /mcp/api/v1/files/{file_path}
```

### List Files
```http
GET /mcp/api/v1/files?prefix=documents/&limit=50
```

### Get File Info
```http
GET /mcp/api/v1/files/{file_path}/info
```

### Delete File
```http
DELETE /mcp/api/v1/files/{file_path}
```

### Upload Directory
```http
POST /mcp/api/v1/files/upload-directory
```

## Real-time Streaming API

### Context Changes Stream
```http
GET /mcp/api/v1/stream/context?key_prefix=user:&event_types=create,update
```

### File Events Stream
```http
GET /mcp/api/v1/stream/files?path_prefix=documents/
```

### All Events Stream
```http
GET /mcp/api/v1/stream/all
```

## Data Processing API

### Extract Content
```http
POST /mcp/api/v1/process/extract
Content-Type: multipart/form-data
```

### Validate Data
```http
POST /mcp/api/v1/process/validate
```

**Request Body:**
```json
{
  "data": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "schema": {
    "type": "object",
    "properties": {
      "name": {"type": "string"},
      "email": {"type": "string", "format": "email"}
    },
    "required": ["name", "email"]
  }
}
```

### Batch Processing
```http
POST /mcp/api/v1/process/batch
Content-Type: multipart/form-data
```

## User Management API

### Register User
```http
POST /mcp/api/v1/register
```

**Request Body:**
```json
{
  "username": "newuser",
  "password": "securepass",
  "email": "user@example.com",
  "full_name": "New User"
}
```

### Get Current User
```http
GET /mcp/api/v1/users/me
```

### List Users (Admin)
```http
GET /mcp/api/v1/users
```

## Monitoring API

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "2.0.0",
  "uptime": 3600,
  "system": {
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_usage": 60.1
  },
  "process": {
    "memory_used": 1048576,
    "memory_percent": 2.5,
    "cpu_percent": 1.2,
    "thread_count": 8,
    "open_files": 12
  },
  "connections": {
    "active": 5,
    "total_requests": 1000
  },
  "features": {
    "mcp_tools": true,
    "context_management": true,
    "file_operations": true,
    "real_time_streaming": true,
    "authentication": true,
    "monitoring": true
  }
}
```

### Metrics
```http
GET /metrics
```

Returns Prometheus metrics in text format.

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": "Error Type",
  "detail": "Detailed error message",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Rate Limiting

The server implements rate limiting to prevent abuse:

- **Health endpoint**: 60 requests/minute
- **Token endpoint**: 5 requests/minute
- **General API**: 10 requests/minute
- **Root endpoint**: 10 requests/minute

## CORS Configuration

The server supports CORS for cross-origin requests:

- **Allowed Origins**: Configurable via `CORS_ORIGINS` environment variable
- **Allowed Methods**: All HTTP methods
- **Allowed Headers**: All headers
- **Credentials**: Supported

## WebSocket Support

Real-time streaming is implemented using Server-Sent Events (SSE):

```javascript
const eventSource = new EventSource('/mcp/api/v1/stream/all');
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received event:', data);
};
```

## Examples

### Complete MCP Tool Workflow

```bash
# 1. List available tools
curl http://localhost:8000/api/tools

# 2. Create a file
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "write_file",
    "arguments": {
      "file_path": "/tmp/example.txt",
      "content": "Hello, World!"
    }
  }'

# 3. Read the file
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "read_file",
    "arguments": {
      "file_path": "/tmp/example.txt"
    }
  }'

# 4. List directory contents
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "list_directory",
    "arguments": {
      "directory_path": "/tmp"
    }
  }'

# 5. Search for files
curl -X POST http://localhost:8000/api/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "search_files",
    "arguments": {
      "directory": "/tmp",
      "pattern": "*.txt"
    }
  }'
```

### Context Management Workflow

```bash
# 1. Set context
curl -X POST http://localhost:8000/mcp/api/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "key": "user:123:session",
    "value": {
      "login_time": "2024-01-01T00:00:00Z",
      "preferences": {
        "theme": "dark"
      }
    },
    "ttl": 3600
  }'

# 2. Get context
curl http://localhost:8000/mcp/api/v1/context/user:123:session

# 3. Update context
curl -X POST http://localhost:8000/mcp/api/v1/context \
  -H "Content-Type: application/json" \
  -d '{
    "key": "user:123:session",
    "value": {
      "login_time": "2024-01-01T00:00:00Z",
      "preferences": {
        "theme": "light"
      }
    },
    "ttl": 3600
  }'

# 4. Delete context
curl -X DELETE http://localhost:8000/mcp/api/v1/context/user:123:session
```

## SDK Examples

### Python SDK
```python
import requests

class MCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def execute_tool(self, tool_name, arguments):
        response = self.session.post(
            f"{self.base_url}/api/execute",
            json={"tool_name": tool_name, "arguments": arguments}
        )
        return response.json()
    
    def set_context(self, key, value, ttl=None):
        data = {"key": key, "value": value}
        if ttl:
            data["ttl"] = ttl
        response = self.session.post(
            f"{self.base_url}/mcp/api/v1/context",
            json=data
        )
        return response.json()

# Usage
client = MCPClient()
result = client.execute_tool("read_file", {"file_path": "/tmp/test.txt"})
client.set_context("user:123:prefs", {"theme": "dark"}, ttl=3600)
```

### JavaScript SDK
```javascript
class MCPClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async executeTool(toolName, arguments) {
        const response = await fetch(`${this.baseUrl}/api/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tool_name: toolName, arguments })
        });
        return response.json();
    }
    
    async setContext(key, value, ttl = null) {
        const data = { key, value };
        if (ttl) data.ttl = ttl;
        const response = await fetch(`${this.baseUrl}/mcp/api/v1/context`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return response.json();
    }
}

// Usage
const client = new MCPClient();
const result = await client.executeTool('read_file', { file_path: '/tmp/test.txt' });
await client.setContext('user:123:prefs', { theme: 'dark' }, 3600);
```

## Performance Considerations

- **Async Processing**: All operations are asynchronous for high performance
- **Caching**: Redis integration for distributed caching
- **Rate Limiting**: Prevents abuse and ensures fair usage
- **Compression**: Gzip compression for response optimization
- **Connection Pooling**: Efficient database connections
- **Background Tasks**: Non-blocking operations

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: Prevents DoS attacks
- **Input Validation**: Comprehensive data validation
- **Error Handling**: Secure error messages
- **Audit Logging**: Track all user actions

---

For more information, visit the [main documentation](../README.md) or check the [deployment guide](DEPLOYMENT.md).
