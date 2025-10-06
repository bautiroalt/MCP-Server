"""
MCP Tool Routes for NEW MCP Server.

This module provides API endpoints for Model Context Protocol (MCP) tool execution,
combining the functionality from both the app/backend and MCP SERVER implementations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import os
import glob
import json
import uuid

# Create router
router = APIRouter(prefix="/mcp", tags=["MCP Tools"])

# MCP Tool Models
class MCPTool(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Dict[str, str]]

class MCPToolRequest(BaseModel):
    tool_name: str
    arguments: Dict[str, Any]

class MCPToolResponse(BaseModel):
    success: bool
    result: Any
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class MCPToolList(BaseModel):
    tools: List[MCPTool]

# MCP Tool Functions
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

# Available MCP Tools
MCP_TOOLS = {
    "read_file": {
        "name": "read_file",
        "description": "Read contents of a file",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the file to read"}
        }
    },
    "write_file": {
        "name": "write_file", 
        "description": "Write content to a file",
        "parameters": {
            "file_path": {"type": "string", "description": "Path to the file to write"},
            "content": {"type": "string", "description": "Content to write to the file"}
        }
    },
    "list_directory": {
        "name": "list_directory",
        "description": "List contents of a directory", 
        "parameters": {
            "directory_path": {"type": "string", "description": "Path to the directory to list"}
        }
    },
    "search_files": {
        "name": "search_files",
        "description": "Search for files matching a pattern",
        "parameters": {
            "directory": {"type": "string", "description": "Directory to search in"},
            "pattern": {"type": "string", "description": "Glob pattern to match files"}
        }
    }
}

# Tool function mapping
TOOL_FUNCTIONS = {
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    "list_directory": list_directory_tool,
    "search_files": search_files_tool
}

@router.get("/tools", response_model=MCPToolList, tags=["MCP Tools"])
async def list_mcp_tools():
    """List all available MCP tools"""
    tools = [MCPTool(**tool_data) for tool_data in MCP_TOOLS.values()]
    return MCPToolList(tools=tools)

@router.get("/tools/{tool_name}", response_model=MCPTool, tags=["MCP Tools"])
async def get_mcp_tool(tool_name: str):
    """Get details of a specific MCP tool"""
    if tool_name not in MCP_TOOLS:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return MCPTool(**MCP_TOOLS[tool_name])

@router.post("/execute", response_model=MCPToolResponse, tags=["MCP Tools"])
async def execute_mcp_tool(request: MCPToolRequest):
    """Execute an MCP tool with the provided arguments"""
    if request.tool_name not in TOOL_FUNCTIONS:
        raise HTTPException(status_code=404, detail=f"Tool '{request.tool_name}' not found")
    
    try:
        tool_func = TOOL_FUNCTIONS[request.tool_name]
        result = await tool_func(**request.arguments)
        return MCPToolResponse(success=True, result=result)
    except HTTPException:
        raise
    except Exception as e:
        return MCPToolResponse(success=False, result=None, error=str(e))

@router.get("/status", tags=["MCP Tools"])
async def mcp_status():
    """Get MCP server status"""
    return {
        "status": "active",
        "tools_available": len(MCP_TOOLS),
        "tools": list(MCP_TOOLS.keys()),
        "timestamp": datetime.utcnow().isoformat()
    }
