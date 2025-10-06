@echo off
echo 🚀 Starting MCP Server Interface...
echo.

cd /d "%~dp0"

echo 📁 Current directory: %CD%
echo 📄 Interface file: mcp-interface.html
echo.

if not exist "mcp-interface.html" (
    echo ❌ Error: mcp-interface.html not found!
    echo Please make sure the file exists in the current directory.
    pause
    exit /b 1
)

echo ✅ Interface file found!
echo.
echo 🌐 Starting HTTP server on port 3000...
echo 🔧 Backend should be running on port 8000
echo.
echo 🎯 MCP SERVER INTERFACE FEATURES:
echo ======================================
echo 🔧 MCP Tools - Execute Model Context Protocol tools
echo 📝 Context Management - Manage conversation context  
echo 📁 File Operations - Upload, download, manage files
echo 📡 Real-time Streaming - Live data streaming
echo 📊 Monitoring - System health and performance metrics
echo ======================================
echo.
echo 🌐 Opening interface in your browser...
echo 💡 If browser doesn't open automatically, go to: http://localhost:3000/mcp-interface.html
echo.
echo 🛑 Press Ctrl+C to stop the server
echo.

start http://localhost:3000/mcp-interface.html

python -m http.server 3000
