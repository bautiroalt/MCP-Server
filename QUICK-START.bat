@echo off
echo ============================================================
echo    MCP SERVER - QUICK START
echo ============================================================
echo.

cd /d "%~dp0"

echo Step 1: Starting Backend Server...
echo.
start "MCP Backend" cmd /k "cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo Waiting 10 seconds for backend to start...
timeout /t 10 /nobreak >nul

echo Step 2: Starting Interface Server...
echo.
start "MCP Interface" cmd /k "cd interface && python -m http.server 3001"

echo Waiting 5 seconds for interface to start...
timeout /t 5 /nobreak >nul

echo.
echo ============================================================
echo    SERVERS STARTED!
echo ============================================================
echo.
echo Backend: http://localhost:8000
echo Interface: http://localhost:3001/mcp-interface.html
echo.
echo Opening browser...
echo.

start http://localhost:3001/mcp-interface.html

echo ✅ MCP Server is ready!
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
