# NEW MCP Server - Unified Main Application Entry Point
# ----------------------------------------------------
# This is the unified server application that combines the best features from both
# the app and MCP SERVER implementations, providing a comprehensive API for managing
# context, files, real-time data streams, and MCP tool execution.
#
# Key Features:
# - JWT-based authentication and API key validation
# - Rate limiting and CORS protection
# - Prometheus metrics and health monitoring
# - Gzip compression for response optimization
# - Real-time event streaming
# - MCP tool execution (read_file, write_file, list_directory, search_files)
# - Comprehensive error handling and logging
# - MongoDB integration for persistence
# - Redis caching for performance
#
# The server uses FastAPI framework for high performance and modern API features,
# with additional middleware for security, monitoring, and performance optimization.

from fastapi import FastAPI, Request, Response, Depends, HTTPException, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import time
import logging
import psutil
from typing import Callable, Optional, List, Dict, Any
from datetime import datetime, timedelta
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
import glob
import json
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field

# Import merged API routes
from app.api import (
    file_routes, context_routes, stream_routes, 
    monitoring_routes, processing_routes, auth_routes,
    mcp_routes,  # New MCP tool routes
    analytics_routes  # META-MINDS analytics routes
)
from app.core.file_manager import file_manager
from app.core.context_manager import mcp_context_manager
from app.models.pydantic_models import ErrorResponse, ContextItem, ContextBulkOperation, ContextQuery
from app.core.user_manager import user_manager, UserManager
from fastapi.openapi.utils import get_openapi

# Logging Configuration
log_file = os.getenv("LOG_FILE", "fastmcp.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Prometheus Metrics Configuration
REQUEST_COUNT = Counter('fastmcp_request_total', 'Total request count')
REQUEST_LATENCY = Histogram('fastmcp_request_latency_seconds', 'Request latency')
ACTIVE_CONNECTIONS = Gauge('fastmcp_active_connections', 'Number of active connections')
SYSTEM_MEMORY = Gauge('fastmcp_system_memory_bytes', 'System memory usage')
SYSTEM_CPU = Gauge('fastmcp_system_cpu_percent', 'System CPU usage')

# Security Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize security components
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Environment and Rate Limiting Configuration
load_dotenv()
limiter = Limiter(key_func=get_remote_address)

# Security Settings from Environment
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001,http://localhost:3002").split(",")
API_KEY_NAME = os.getenv("API_KEY_NAME", "X-API-Key")
API_KEY = os.getenv("API_KEY", None)

# Initialize API key validation
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# MongoDB connection (from app/backend)
mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
client = AsyncIOMotorClient(mongo_url)
db = client[os.getenv("DB_NAME", "fastmcp")]

# MCP Tool Models (from app/backend)
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class MCPToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None

# MCP Tool Functions (merged from app/backend)
async def read_file_tool(file_path: str) -> str:
    """Read contents of a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

async def write_file_tool(file_path: str, content: str) -> str:
    """Write content to a file"""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

async def list_directory_tool(directory_path: str) -> List[Dict[str, Any]]:
    """List contents of a directory"""
    try:
        if not os.path.exists(directory_path):
            raise HTTPException(status_code=404, detail=f"Directory not found: {directory_path}")
        
        if not os.path.isdir(directory_path):
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {directory_path}")
        
        items = []
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            stat = os.stat(item_path)
            items.append({
                "name": item,
                "path": item_path,
                "type": "directory" if os.path.isdir(item_path) else "file",
                "size": stat.st_size
            })
        
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing directory: {str(e)}")

async def search_files_tool(directory: str, pattern: str) -> List[str]:
    """Search for files matching a pattern"""
    try:
        if not os.path.exists(directory):
            raise HTTPException(status_code=404, detail=f"Directory not found: {directory}")
        
        # Use glob to find matching files
        search_pattern = os.path.join(directory, "**", pattern)
        matching_files = glob.glob(search_pattern, recursive=True)
        
        # Sort the results
        matching_files.sort()
        
        return matching_files
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching files: {str(e)}")

# Metrics Middleware
class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        REQUEST_COUNT.inc()
        ACTIVE_CONNECTIONS.inc()
        
        SYSTEM_MEMORY.set(psutil.Process().memory_info().rss)
        SYSTEM_CPU.set(psutil.cpu_percent())
        
        logger.info(f"Request started: {request.method} {request.url.path}")
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            REQUEST_LATENCY.observe(process_time)
            response.headers["X-Process-Time"] = f"{process_time * 1000:.2f}"
            
            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"- Status: {response.status_code} - Time: {process_time * 1000:.2f}ms"
            )
            
            return response
        except Exception as e:
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"- Error: {str(e)}"
            )
            raise
        finally:
            ACTIVE_CONNECTIONS.dec()

# Authentication Middleware
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip authentication for public endpoints
        if request.url.path in ["/token", "/health", "/metrics", "/api/tools", "/api/execute"]:
            return await call_next(request)
        return await call_next(request)

# Initialize FastAPI application
app = FastAPI(
    title="NEW MCP Server",
    description="Unified Model Context Protocol Server with MCP Tools, Context Management, and Real-time Streaming",
    version="2.0.0",
    openapi_url="/mcp/openapi.json",
    docs_url="/mcp/docs",
    redoc_url="/mcp/redoc"
)

# Error Handling Configuration
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="Bad Request",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )

@app.exception_handler(FileNotFoundError)
async def file_not_found_handler(request: Request, exc: FileNotFoundError):
    """Handle FileNotFoundError exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error="Not Found",
            detail=str(exc),
            timestamp=datetime.utcnow().isoformat()
        ).dict()
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Too many requests",
            "type": "rate_limit_exceeded",
            "retry_after": exc.retry_after,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "type": "validation_error",
            "errors": exc.errors(),
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Configure data storage location
DATA_DIR = os.getenv("DATA_DIRECTORY", "./data")

# File Manager Initialization
from app.core.file_manager import FileManager
file_manager = FileManager(DATA_DIR)

# Initialize user manager with password hashing context
user_manager = UserManager(pwd_context)

# Token and user management functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

# MCP Tool Endpoints (merged from app/backend)
@app.get("/api/tools", tags=["MCP Tools"])
async def list_tools():
    """List all available MCP tools"""
    tools = [
        {
            "name": "read_file",
            "description": "Read contents of a file",
            "parameters": {
                "file_path": {"type": "string", "description": "Path to the file to read"}
            }
        },
        {
            "name": "write_file", 
            "description": "Write content to a file",
            "parameters": {
                "file_path": {"type": "string", "description": "Path to the file to write"},
                "content": {"type": "string", "description": "Content to write to the file"}
            }
        },
        {
            "name": "list_directory",
            "description": "List contents of a directory", 
            "parameters": {
                "directory_path": {"type": "string", "description": "Path to the directory to list"}
            }
        },
        {
            "name": "search_files",
            "description": "Search for files matching a pattern",
            "parameters": {
                "directory": {"type": "string", "description": "Directory to search in"},
                "pattern": {"type": "string", "description": "Glob pattern to match files"}
            }
        }
    ]
    return {"tools": tools}

@app.post("/api/execute", response_model=MCPToolResponse, tags=["MCP Tools"])
async def execute_tool(request: MCPToolRequest):
    """Execute an MCP tool with the provided arguments"""
    tool_functions = {
        "read_file": read_file_tool,
        "write_file": write_file_tool,
        "list_directory": list_directory_tool,
        "search_files": search_files_tool
    }
    
    if request.tool_name not in tool_functions:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
    
    try:
        tool_func = tool_functions[request.tool_name]
        result = await tool_func(**request.arguments)
        return MCPToolResponse(success=True, result=result)
    except HTTPException:
        raise
    except Exception as e:
        return MCPToolResponse(success=False, result=None, error=str(e))

# Authentication endpoints
@app.post("/token", tags=["Authentication"])
@limiter.limit("5/minute")
async def login_for_access_token(request: Request, username: str = Form(...), password: str = Form(...)):
    if username != os.getenv("ADMIN_USERNAME") or not pwd_context.verify(password, os.getenv("ADMIN_PASSWORD_HASH")):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", tags=["Authentication"])
async def read_users_me(current_user: str = Depends(get_current_user)):
    return {"username": current_user}

# Configure middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(MetricsMiddleware)
# app.add_middleware(AuthMiddleware)  # Authentication middleware

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Initialize metrics monitoring
Instrumentator().instrument(app).expose(app)

# Include the API routers with a common prefix
app.include_router(auth_routes.router, prefix="/mcp/api/v1", tags=["auth"])
app.include_router(context_routes.router, prefix="/mcp/api/v1", tags=["context"])
app.include_router(file_routes.router, prefix="/mcp/api/v1", tags=["files"])
app.include_router(stream_routes.router, prefix="/mcp/api/v1", tags=["streams"])
app.include_router(monitoring_routes.router, prefix="/mcp/api/v1", tags=["monitoring"])
app.include_router(processing_routes.router, prefix="/mcp/api/v1", tags=["processing"])
app.include_router(analytics_routes.router, tags=["analytics"])  # META-MINDS analytics

# Create static and templates directories if they don't exist
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the file upload interface."""
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )

@app.get("/", include_in_schema=False)
@limiter.limit("10/minute")
async def root(request: Request):
    return {
        "message": "Welcome to the NEW MCP Unified Server! Access /mcp/docs for API documentation.",
        "server_time": datetime.now().isoformat(),
        "version": "2.0.0",
        "features": [
            "MCP Tool Execution",
            "Context Management", 
            "File Operations",
            "Real-time Streaming",
            "User Authentication",
            "Monitoring & Metrics"
        ]
    }

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting NEW MCP Server...")
    # Ensure data directories exist
    os.makedirs("data/files", exist_ok=True)
    os.makedirs("data/context", exist_ok=True)
    os.makedirs("data/versions", exist_ok=True)
    os.makedirs("data/tmp", exist_ok=True)
    os.makedirs("data/users", exist_ok=True)
    
    # Initialize context with system info
    await mcp_context_manager.set_context("system_info", {
        "startup_time": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "features": ["mcp_tools", "context_management", "file_operations", "streaming"]
    })

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down NEW MCP Server...")
    # Cleanup temporary files
    await file_manager.cleanup_temp_files()
    # Clear context
    await mcp_context_manager.delete_context("system_info")

@app.get("/health", tags=["Monitoring"])
@limiter.limit("60/minute")
async def health_check(request: Request):
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "uptime": time.time() - process.create_time(),
        "system": {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent
        },
        "process": {
            "memory_used": memory_info.rss,
            "memory_percent": process.memory_percent(),
            "cpu_percent": process.cpu_percent(),
            "thread_count": process.num_threads(),
            "open_files": len(process.open_files())
        },
        "connections": {
            "active": ACTIVE_CONNECTIONS._value.get(),
            "total_requests": REQUEST_COUNT._value.get()
        },
        "data_directory": {
            "path": os.path.abspath(DATA_DIR),
            "exists": os.path.exists(DATA_DIR),
            "is_dir": os.path.isdir(DATA_DIR),
            "disk_free": psutil.disk_usage(DATA_DIR).free if os.path.exists(DATA_DIR) else None
        },
        "features": {
            "mcp_tools": True,
            "context_management": True,
            "file_operations": True,
            "real_time_streaming": True,
            "authentication": True,
            "monitoring": True
        }
    }

# Define a custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="NEW MCP Server",
        version="2.0.0",
        description="Unified Model Context Protocol Server with MCP Tools, Context Management, and Real-time Streaming",
        routes=app.routes,
    )
    # Define the custom Bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
        "oAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/mcp/api/v1/token"
                }
            }
        }
    }
    # Apply security schemes
    for path, path_item in openapi_schema.get("paths", {}).items():
        for operation in path_item.values():
            if "Login For Access Token" in operation.get("summary", ""):
                 operation["security"] = [{
                     "oAuth2PasswordBearer": []
                 }]
            elif operation.get("summary") not in ["Health Check", "Metrics", "List Tools", "Execute Tool"]:
                 if "security" not in operation:
                     operation["security"] = []
                 operation["security"].append({"bearerAuth": []})

    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Assign the custom openapi generator
app.openapi = custom_openapi

# Add these lines at the end of app/main.py if they don't exist
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
