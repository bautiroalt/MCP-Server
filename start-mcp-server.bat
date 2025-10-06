@echo off
echo ========================================
echo    MCP SERVER STARTUP
echo ========================================
echo.

echo Starting Backend Server...
start "MCP Backend" cmd /k "cd /d C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP\backend && set PYTHONPATH=%CD% && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

echo Starting Interface Server...
start "MCP Interface" cmd /k "cd /d C:\Users\Jatin\Documents\APP\MCP_Server\NEW MCP\interface && python -m http.server 3001"

echo.
echo ========================================
echo    SERVERS STARTING...
echo ========================================
echo.
echo Backend Server: http://localhost:8000
echo Interface: http://localhost:3001
echo Main Interface: http://localhost:3001/mcp-interface.html
echo.
echo Wait for both servers to start, then open your browser!
echo.
pause
