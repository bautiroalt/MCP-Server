#!/usr/bin/env python3
"""
MCP Server Auto-Start Script
Starts both backend and interface servers automatically
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting Backend Server...")
    backend_dir = Path(__file__).parent / "backend"
    
    # Start backend in background
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("✅ Backend server starting on http://localhost:8000")
    return backend_process

def start_interface():
    """Start the interface HTTP server"""
    print("🌐 Starting Interface Server...")
    interface_dir = Path(__file__).parent / "interface"
    
    # Start interface server in background
    interface_process = subprocess.Popen(
        [sys.executable, "-m", "http.server", "3001"],
        cwd=interface_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print("✅ Interface server starting on http://localhost:3001")
    return interface_process

def main():
    print("=" * 60)
    print("   MCP SERVER AUTO-START")
    print("=" * 60)
    print()
    
    # Start backend
    backend_process = start_backend()
    time.sleep(3)  # Wait for backend to initialize
    
    # Start interface
    interface_process = start_interface()
    time.sleep(2)  # Wait for interface to initialize
    
    print()
    print("=" * 60)
    print("   SERVERS RUNNING!")
    print("=" * 60)
    print()
    print("🌐 Interface: http://localhost:3001/mcp-interface.html")
    print("🔧 Backend API: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("❤️  Health Check: http://localhost:8000/health")
    print()
    print("Opening browser...")
    print()
    
    # Open browser automatically
    time.sleep(2)
    webbrowser.open("http://localhost:3001/mcp-interface.html")
    
    print("✅ MCP Server is ready!")
    print()
    print("Press Ctrl+C to stop all servers...")
    print()
    
    try:
        # Keep script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
        backend_process.terminate()
        interface_process.terminate()
        print("✅ All servers stopped")

if __name__ == "__main__":
    main()

