#!/usr/bin/env python3
"""
Simple HTTP Server for MCP Interface
Serves the interface files with proper CORS headers
"""

import http.server
import socketserver
import os
from urllib.parse import urlparse

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == "__main__":
    PORT = 3001
    
    # Change to the interface directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
        print(f"MCP Interface Server running on http://localhost:{PORT}")
        print(f"Interface: http://localhost:{PORT}/mcp-interface.html")
        print(f"CORS Test: http://localhost:{PORT}/test-cors.html")
        print("Press Ctrl+C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
