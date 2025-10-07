@echo off
title MCP Server Monitor
echo ============================================================
echo    MCP SERVER - KEEP ALIVE MONITOR
echo ============================================================
echo.

cd /d "%~dp0"

:monitor_loop
echo [%date% %time%] Checking server status...

REM Check backend server
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo Backend server down! Restarting...
    start "MCP Backend Server" /min cmd /c "cd backend && python minimal-server.py"
    timeout /t 3 /nobreak >nul
)

REM Check interface server
curl -s http://localhost:3001/mcp-interface.html >nul 2>&1
if %errorlevel% neq 0 (
    echo Interface server down! Restarting...
    start "MCP Interface Server" /min cmd /c "cd interface && python -m http.server 3001"
    timeout /t 2 /nobreak >nul
)

echo Servers are healthy. Checking again in 30 seconds...
timeout /t 30 /nobreak >nul
goto monitor_loop
