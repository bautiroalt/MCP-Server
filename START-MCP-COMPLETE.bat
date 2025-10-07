@echo off
echo ============================================================
echo    MCP SERVER - COMPLETE AUTO START
echo ============================================================
echo.
echo Starting both Backend and Interface servers...
echo.

cd /d "%~dp0"

echo Starting Backend Server...
start "MCP Backend Server" cmd /k "start-backend-fixed.bat"

timeout /t 5 /nobreak >nul

echo Starting Interface Server...
start "MCP Interface Server" cmd /k "start-interface-fixed.bat"

timeout /t 3 /nobreak >nul

echo.
echo ============================================================
echo    SERVERS STARTING!
echo ============================================================
echo.
echo Backend: http://localhost:8000
echo Interface: http://localhost:3001/mcp-interface.html
echo.
echo Opening browser...
echo.

timeout /t 2 /nobreak >nul
start http://localhost:3001/mcp-interface.html

echo ✅ MCP Server is starting!
echo.
echo Press any key to close this window...
pause >nul
