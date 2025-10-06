"""
Firebase Functions entry point for NEW MCP Server.
This allows you to deploy your FastAPI backend as a Firebase Function.
"""

from firebase_functions import https_fn
from firebase_admin import initialize_app
import os
import sys
from pathlib import Path

# Initialize Firebase Admin
initialize_app()

# Add the backend directory to Python path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Import your FastAPI app
try:
    from app.main import app
except ImportError:
    # Fallback if direct import fails
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "main", 
        backend_path / "app" / "main.py"
    )
    main_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_module)
    app = main_module.app

@https_fn.on_request()
def new_mcp_server(req: https_fn.Request) -> https_fn.Response:
    """
    Firebase Function that serves the NEW MCP Server.
    
    This function acts as a bridge between Firebase Functions and your FastAPI app.
    """
    try:
        # Convert Firebase request to ASGI scope
        scope = {
            "type": "http",
            "method": req.method,
            "path": req.path,
            "query_string": req.query_string.encode() if req.query_string else b"",
            "headers": [(k.lower().encode(), v.encode()) for k, v in req.headers.items()],
            "client": (req.remote_addr, 0),
            "server": (req.host, 443 if req.is_secure else 80),
            "scheme": "https" if req.is_secure else "http",
        }
        
        # Create a simple ASGI application wrapper
        async def asgi_app(scope, receive, send):
            # This is a simplified version - in production, you'd want to use
            # a proper ASGI adapter like mangum
            pass
        
        # For now, return a simple response
        # In production, you'd integrate with your FastAPI app properly
        return https_fn.Response(
            "NEW MCP Server is running on Firebase Functions!",
            status=200,
            headers={"Content-Type": "text/plain"}
        )
        
    except Exception as e:
        return https_fn.Response(
            f"Error: {str(e)}",
            status=500,
            headers={"Content-Type": "text/plain"}
        )
