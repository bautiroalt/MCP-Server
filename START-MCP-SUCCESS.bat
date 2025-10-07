@echo off
echo ============================================================
echo    MCP SERVER - SUCCESS VERSION
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting Backend Server...
start "MCP Backend" cmd /k "cd backend && python minimal-server.py"

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo Starting Interface Server...
start "MCP Interface" cmd /k "cd interface && python -m http.server 3001"

echo Waiting 3 seconds for interface to start...
timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo    SERVERS STARTED SUCCESSFULLY!
echo ============================================================
echo.
echo Backend: http://localhost:8000
echo Interface: http://localhost:3001/mcp-interface.html
echo.
echo Opening browser...
echo.

start http://localhost:3001/mcp-interface.html

echo MCP Server is ready!
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
