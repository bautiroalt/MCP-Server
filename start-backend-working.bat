@echo off
echo ============================================================
echo    MCP BACKEND SERVER - WORKING VERSION
echo ============================================================
echo.

cd /d "%~dp0\backend"

echo Starting Backend Server from: %CD%
echo.

python simple-server.py

pause
