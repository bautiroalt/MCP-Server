"""
Comprehensive test suite for NEW MCP Server backend API.

This test suite covers all the merged functionalities from both app and MCP SERVER implementations,
including MCP tools, context management, file operations, and real-time streaming.
"""

import pytest
import requests
import json
import os
import time
from typing import Dict, Any

# Test configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api"
MCP_API_URL = f"{BASE_URL}/mcp/api/v1"

class TestNEWMCPServer:
    """Test class for NEW MCP Server functionality."""
    
    def setup_method(self):
        """Setup test environment before each test."""
        self.session = requests.Session()
        self.test_files = []
    
    def teardown_method(self):
        """Cleanup after each test."""
        # Clean up test files
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass
    
    def test_server_health(self):
        """Test server health endpoint."""
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "2.0.0"
        assert "features" in data
    
    def test_mcp_tools_list(self):
        """Test MCP tools listing endpoint."""
        response = self.session.get(f"{API_URL}/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert len(data["tools"]) == 4
        
        tool_names = [tool["name"] for tool in data["tools"]]
        expected_tools = ["read_file", "write_file", "list_directory", "search_files"]
        assert all(tool in tool_names for tool in expected_tools)
    
    def test_mcp_tool_execution_read_file(self):
        """Test read_file MCP tool execution."""
        # First create a test file
        test_file = "/tmp/test_read.txt"
        test_content = "This is a test file for reading."
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        self.test_files.append(test_file)
        
        # Test read_file tool
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "read_file",
            "arguments": {"file_path": test_file}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert data["result"] == test_content
    
    def test_mcp_tool_execution_write_file(self):
        """Test write_file MCP tool execution."""
        test_file = "/tmp/test_write.txt"
        test_content = "This is a test file for writing."
        self.test_files.append(test_file)
        
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "write_file",
            "arguments": {
                "file_path": test_file,
                "content": test_content
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "Successfully wrote" in data["result"]
        
        # Verify file was created
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            assert f.read() == test_content
    
    def test_mcp_tool_execution_list_directory(self):
        """Test list_directory MCP tool execution."""
        test_dir = "/tmp/test_list_dir"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create test files
        test_files = ["file1.txt", "file2.txt", "subdir"]
        for file in test_files:
            if file == "subdir":
                os.makedirs(os.path.join(test_dir, file), exist_ok=True)
            else:
                with open(os.path.join(test_dir, file), 'w') as f:
                    f.write("test content")
        
        self.test_files.extend([os.path.join(test_dir, f) for f in test_files if f != "subdir"])
        
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "list_directory",
            "arguments": {"directory_path": test_dir}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert isinstance(data["result"], list)
        assert len(data["result"]) == 3
        
        # Check file structure
        names = [item["name"] for item in data["result"]]
        assert "file1.txt" in names
        assert "file2.txt" in names
        assert "subdir" in names
    
    def test_mcp_tool_execution_search_files(self):
        """Test search_files MCP tool execution."""
        test_dir = "/tmp/test_search"
        os.makedirs(test_dir, exist_ok=True)
        
        # Create test files
        test_files = ["test1.txt", "test2.txt", "test3.py", "other.txt"]
        for file in test_files:
            with open(os.path.join(test_dir, file), 'w') as f:
                f.write("test content")
            self.test_files.append(os.path.join(test_dir, file))
        
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "search_files",
            "arguments": {
                "directory": test_dir,
                "pattern": "test*.txt"
            }
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert isinstance(data["result"], list)
        assert len(data["result"]) == 2
        
        # Check that only test*.txt files are returned
        for file_path in data["result"]:
            assert file_path.endswith(".txt")
            assert "test" in os.path.basename(file_path)
    
    def test_mcp_tool_error_handling(self):
        """Test MCP tool error handling."""
        # Test with non-existent file
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "read_file",
            "arguments": {"file_path": "/nonexistent/file.txt"}
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
        assert "File not found" in data["error"]
    
    def test_invalid_tool_name(self):
        """Test error handling for invalid tool name."""
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "invalid_tool",
            "arguments": {}
        })
        
        assert response.status_code == 404
        data = response.json()
        assert "Tool 'invalid_tool' not found" in data["detail"]
    
    def test_missing_required_parameters(self):
        """Test error handling for missing required parameters."""
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "read_file",
            "arguments": {}  # Missing file_path
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == False
        assert "error" in data
    
    def test_context_management(self):
        """Test context management endpoints."""
        # Test setting context
        context_data = {
            "key": "test_context",
            "value": {"test": "data", "number": 42},
            "ttl": 3600
        }
        
        response = self.session.post(f"{MCP_API_URL}/context", json=context_data)
        assert response.status_code == 200
        
        # Test getting context
        response = self.session.get(f"{MCP_API_URL}/context/test_context")
        assert response.status_code == 200
        data = response.json()
        assert data["value"]["test"] == "data"
        assert data["value"]["number"] == 42
    
    def test_file_management(self):
        """Test file management endpoints."""
        # Test file upload (if implemented)
        # This would require multipart form data
        pass
    
    def test_streaming_endpoints(self):
        """Test streaming endpoints."""
        # Test context streaming
        response = self.session.get(f"{MCP_API_URL}/stream/context")
        assert response.status_code == 200
        assert response.headers.get("content-type") == "text/event-stream; charset=utf-8"
    
    def test_monitoring_endpoints(self):
        """Test monitoring and metrics endpoints."""
        # Test health endpoint
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert "system" in data
        assert "process" in data
        assert "connections" in data
        
        # Test metrics endpoint
        response = self.session.get(f"{BASE_URL}/metrics")
        assert response.status_code == 200
        assert "fastmcp_request_total" in response.text
    
    def test_authentication(self):
        """Test authentication endpoints."""
        # Test token endpoint (this would require valid credentials)
        response = self.session.post(f"{BASE_URL}/token", data={
            "username": "admin",
            "password": "admin"
        })
        # This might fail without proper setup, but should not crash
        assert response.status_code in [200, 401]
    
    def test_cors_headers(self):
        """Test CORS headers are present."""
        response = self.session.options(f"{BASE_URL}/api/tools")
        assert "access-control-allow-origin" in response.headers
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make multiple requests quickly
        responses = []
        for _ in range(10):
            response = self.session.get(f"{BASE_URL}/health")
            responses.append(response)
        
        # All should succeed (rate limit is high for health endpoint)
        assert all(r.status_code == 200 for r in responses)
    
    def test_error_responses(self):
        """Test error response formats."""
        # Test 404 for non-existent endpoint
        response = self.session.get(f"{BASE_URL}/nonexistent")
        assert response.status_code == 404
        
        # Test 422 for validation errors
        response = self.session.post(f"{API_URL}/execute", json={
            "tool_name": "read_file",
            "arguments": {"file_path": 123}  # Invalid type
        })
        assert response.status_code == 200  # Tool execution handles this
        data = response.json()
        assert data["success"] == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
