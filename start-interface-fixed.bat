@echo off
echo ============================================================
echo    MCP INTERFACE SERVER - FIXED START
echo ============================================================
echo.

cd /d "%~dp0\interface"

echo Starting Interface Server from: %CD%
echo.

python -m http.server 3001

pause
