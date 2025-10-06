@echo off
echo Starting MCP Server...
echo.

echo Starting Interface Server on port 3001...
start "Interface Server" cmd /k "cd /d C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP && python -m http.server 3001 --directory interface"

echo Starting Backend Server on port 8000...
start "Backend Server" cmd /k "cd /d C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP\backend && set PYTHONPATH=%CD% && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo.
echo Servers starting...
echo Interface: http://localhost:3001/mcp-interface.html
echo Backend: http://localhost:8000
echo.
echo Press any key to exit...
pause
