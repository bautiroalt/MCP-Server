@echo off
echo Starting MCP Interface Server...
cd /d "C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP\interface"
python -m http.server 3001
pause
