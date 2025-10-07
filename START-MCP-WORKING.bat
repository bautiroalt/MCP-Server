@echo off
echo ============================================================
echo    MCP SERVER - FINAL WORKING SOLUTION
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting Backend Server in new window...
start "MCP Backend Server" cmd /k "cd backend && python simple-server.py"

echo Waiting 10 seconds for backend to start...
timeout /t 10 /nobreak >nul

echo Starting Interface Server in new window...
start "MCP Interface Server" cmd /k "cd interface && python -m http.server 3001"

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
echo Press any key to close this window...
pause >nul
