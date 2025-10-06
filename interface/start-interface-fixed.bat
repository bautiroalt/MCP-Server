@echo off
echo Starting MCP Interface Server...
cd /d "C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP\interface"
echo Current directory: %CD%
echo Files in directory:
dir
echo.
echo Starting HTTP server on port 3001...
python -m http.server 3001
