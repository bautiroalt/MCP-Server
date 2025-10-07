@echo off
echo ============================================================
echo    MCP BACKEND SERVER - FIXED START
echo ============================================================
echo.

cd /d "%~dp0\backend"
set PYTHONPATH=%CD%

echo Starting Backend Server from: %CD%
echo PYTHONPATH set to: %PYTHONPATH%
echo.

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
