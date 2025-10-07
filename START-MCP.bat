@echo off
title MCP Server - One Click Start
echo ============================================================
echo    MCP SERVER - ONE CLICK START
echo ============================================================
echo.

cd /d "%~dp0"

echo Starting MCP Server...
echo.

REM Kill any existing Python processes on ports 8000 and 3001
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /f /pid %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3001"') do taskkill /f /pid %%a >nul 2>&1

REM Start backend server
echo Starting Backend Server...
start "MCP Backend" /min cmd /c "cd backend && python minimal-server.py"

REM Wait for backend to start
timeout /t 5 /nobreak >nul

REM Start interface server  
echo Starting Interface Server...
start "MCP Interface" /min cmd /c "cd interface && python -m http.server 3001"

REM Wait for interface to start
timeout /t 3 /nobreak >nul

REM Verify servers are running
echo Verifying servers...
:check_servers
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo Waiting for backend...
    timeout /t 2 /nobreak >nul
    goto check_servers
)

curl -s http://localhost:3001/mcp-interface.html >nul 2>&1
if %errorlevel% neq 0 (
    echo Waiting for interface...
    timeout /t 2 /nobreak >nul
    goto check_servers
)

echo.
echo ============================================================
echo    MCP SERVER IS READY!
echo ============================================================
echo.
echo Backend: http://localhost:8000
echo Interface: http://localhost:3001/mcp-interface.html
echo.
echo Opening browser...
start http://localhost:3001/mcp-interface.html

echo.
echo MCP Server is running!
echo To stop: Close the minimized windows or press Ctrl+C
echo.
pause
