from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import File, UploadFile
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import glob
import json

# Create the main app
app = FastAPI(title="MCP Server", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
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

# MCP Tool Functions
async def read_file_tool(file_path: str) -> str:
    """Read contents of a file"""
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise Exception(f"Error reading file: {str(e)}")

async def write_file_tool(file_path: str, content: str) -> str:
    """Write content to a file"""
    try:
        path = Path(file_path)
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"Successfully wrote {len(content)} characters to {file_path}"
    except Exception as e:
        raise Exception(f"Error writing file: {str(e)}")

async def list_directory_tool(directory_path: str) -> List[Dict[str, Any]]:
    """List contents of a directory"""
    try:
        path = Path(directory_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        items = []
        for item in path.iterdir():
            items.append({
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file",
                "size": item.stat().st_size if item.is_file() else None
            })
        
        return sorted(items, key=lambda x: (x["type"] == "file", x["name"]))
    except Exception as e:
        raise Exception(f"Error listing directory: {str(e)}")

async def search_files_tool(directory: str, pattern: str) -> List[str]:
    """Search for files matching a pattern"""
    try:
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        # Use glob to search for files
        search_pattern = str(path / "**" / pattern)
        matches = glob.glob(search_pattern, recursive=True)
        
        return sorted(matches)
    except Exception as e:
        raise Exception(f"Error searching files: {str(e)}")

# MCP Tool Registry
MCP_TOOLS = {
    "read_file": {
        "function": read_file_tool,
        "description": "Read the contents of a file",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the file to read", "required": True}
        }
    },
    "write_file": {
        "function": write_file_tool,
        "description": "Write content to a file (creates file if it doesn't exist)",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the file to write", "required": True},
            "content": {"type": "string", "description": "Content to write to the file", "required": True}
        }
    },
    "list_directory": {
        "function": list_directory_tool,
        "description": "List all files and directories in a directory",
        "parameters": {
            "directory_path": {"type": "string", "description": "Path to the directory to list", "required": True}
        }
    },
    "search_files": {
        "function": search_files_tool,
        "description": "Search for files matching a pattern (supports wildcards)",
        "parameters": {
            "directory": {"type": "string", "description": "Directory to search in", "required": True},
            "pattern": {"type": "string", "description": "File pattern to match (e.g., '*.txt', 'test_*.py')", "required": True}
        }
    }
}

# API Routes
@api_router.get("/")
async def root():
    return {"message": "MCP Server API", "version": "1.0.0"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "message": "Server is running"}

@api_router.get("/tools")
async def list_tools():
    """List all available MCP tools"""
    tools = []
    for tool_name, tool_info in MCP_TOOLS.items():
        tools.append({
            "name": tool_name,
            "description": tool_info["description"],
            "parameters": tool_info["parameters"]
        })
    return {"tools": tools}

@api_router.post("/execute", response_model=MCPToolResponse)
async def execute_tool(request: MCPToolRequest):
    """Execute an MCP tool"""
    try:
        tool_name = request.tool_name
        arguments = request.arguments
        
        # Check if tool exists
        if tool_name not in MCP_TOOLS:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        tool_info = MCP_TOOLS[tool_name]
        tool_function = tool_info["function"]
        
        # Validate required parameters
        for param_name, param_info in tool_info["parameters"].items():
            if param_info.get("required") and param_name not in arguments:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required parameter: {param_name}"
                )
        
        # Execute the tool
        result = await tool_function(**arguments)
        
        return MCPToolResponse(success=True, result=result)
    
    except HTTPException:
        raise
    except Exception as e:
        return MCPToolResponse(success=False, result=None, error=str(e))

# File upload endpoint
@api_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a file"""
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = Path("data/files")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix if file.filename else ""
        file_path = upload_dir / f"{file_id}{file_extension}"
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_id": file_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "size": len(content)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# File list endpoint
@api_router.get("/files")
async def list_files():
    """List uploaded files"""
    try:
        files_dir = Path("data/files")
        if not files_dir.exists():
            return {"files": []}
        
        files = []
        for file_path in files_dir.iterdir():
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        return {"files": sorted(files, key=lambda x: x["modified"], reverse=True)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting MCP Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("❤️  Health check: http://localhost:8000/api/health")
    print("📖 API docs: http://localhost:8000/docs")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
