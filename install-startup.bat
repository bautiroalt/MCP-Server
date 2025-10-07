@echo off
echo Installing MCP Server to Windows Startup...

cd /d "%~dp0"

REM Create startup folder shortcut
powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\MCP Server.lnk'); $Shortcut.TargetPath = '%CD%\AUTO-START-MCP.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Auto-start MCP Server'; $Shortcut.IconLocation = 'shell32.dll,23'; $Shortcut.Save()}"

echo MCP Server will now start automatically when Windows boots!
echo To disable auto-start: Delete the shortcut from Startup folder
pause
