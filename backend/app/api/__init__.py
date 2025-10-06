"""
API routes for NEW MCP Server
"""

from . import (
    auth_routes,
    context_routes,
    file_routes,
    monitoring_routes,
    processing_routes,
    stream_routes,
    mcp_routes,
    analytics_routes
)

__all__ = [
    "auth_routes",
    "context_routes",
    "file_routes",
    "monitoring_routes",
    "processing_routes",
    "stream_routes",
    "mcp_routes",
    "analytics_routes"
]

