#!/usr/bin/env python3
"""
MCP Server Interface - HTTP Server
Serves the MCP interface with proper CORS headers
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Configuration
PORT = 3000
INTERFACE_FILE = "mcp-interface.html"

class CORSHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

def main():
    # Change to the script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Check if interface file exists
    if not os.path.exists(INTERFACE_FILE):
        print(f"❌ Error: {INTERFACE_FILE} not found!")
        print(f"Please make sure the file exists in: {script_dir}")
        sys.exit(1)
    
    # Create HTTP server with CORS support
    try:
        with socketserver.TCPServer(("", PORT), CORSHTTPRequestHandler) as httpd:
            print("🚀 MCP Server Interface Starting...")
            print(f"📁 Serving from: {script_dir}")
            print(f"🌐 Interface URL: http://localhost:{PORT}/{INTERFACE_FILE}")
            print(f"🔧 Backend API: http://localhost:8000")
            print("\n" + "="*60)
            print("🎯 MCP SERVER INTERFACE FEATURES:")
            print("="*60)
            print("🔧 MCP Tools - Execute Model Context Protocol tools")
            print("📝 Context Management - Manage conversation context")
            print("📁 File Operations - Upload, download, manage files")
            print("📡 Real-time Streaming - Live data streaming")
            print("📊 Monitoring - System health and performance metrics")
            print("="*60)
            print("\n💡 TIP: Make sure your MCP backend is running on port 8000")
            print("   Backend command: cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
            print("\n🔄 Starting server with CORS support... (Press Ctrl+C to stop)")
            print("-" * 60)
            
            # Try to open browser automatically
            try:
                webbrowser.open(f"http://localhost:{PORT}/{INTERFACE_FILE}")
                print("🌐 Opening interface in your default browser...")
            except:
                print("⚠️  Could not open browser automatically")
                print(f"   Please manually open: http://localhost:{PORT}/{INTERFACE_FILE}")
            
            # Start serving
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        print("👋 Thank you for using MCP Server Interface!")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Error: Port {PORT} is already in use!")
            print("   Please stop any other server running on this port")
            print("   Or change the PORT variable in this script")
        else:
            print(f"❌ Error starting server: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
