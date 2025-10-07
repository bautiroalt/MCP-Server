@echo off
title MCP Server Auto-Start
echo ============================================================
echo    MCP SERVER - AUTO START SYSTEM
echo ============================================================
echo.

cd /d "%~dp0"

echo [1/4] Checking if servers are already running...
netstat -an | findstr ":8000" >nul
if %errorlevel% == 0 (
    echo Backend server already running on port 8000
) else (
    echo Starting Backend Server...
    start "MCP Backend Server" /min cmd /c "cd backend && python minimal-server.py"
    timeout /t 3 /nobreak >nul
)

netstat -an | findstr ":3001" >nul
if %errorlevel% == 0 (
    echo Interface server already running on port 3001
) else (
    echo Starting Interface Server...
    start "MCP Interface Server" /min cmd /c "cd interface && python -m http.server 3001"
    timeout /t 2 /nobreak >nul
)

echo [2/4] Waiting for servers to initialize...
timeout /t 5 /nobreak >nul

echo [3/4] Verifying servers are running...
:check_backend
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo Backend not ready, waiting...
    timeout /t 2 /nobreak >nul
    goto check_backend
)
echo Backend server is ready!

:check_interface
curl -s http://localhost:3001/mcp-interface.html >nul 2>&1
if %errorlevel% neq 0 (
    echo Interface not ready, waiting...
    timeout /t 2 /nobreak >nul
    goto check_interface
)
echo Interface server is ready!

echo [4/4] Opening MCP Server Interface...
start http://localhost:3001/mcp-interface.html

echo.
echo ============================================================
echo    MCP SERVER IS READY!
echo ============================================================
echo.
echo Backend: http://localhost:8000
echo Interface: http://localhost:3001/mcp-interface.html
echo.
echo Both servers are running in minimized windows.
echo To stop servers: Close the minimized windows or press Ctrl+C
echo.
echo Press any key to close this window...
pause >nul
