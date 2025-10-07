@echo off
echo Creating MCP Server Desktop Shortcut...

cd /d "%~dp0"

powershell -Command "& {$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MCP Server.lnk'); $Shortcut.TargetPath = '%CD%\AUTO-START-MCP.bat'; $Shortcut.WorkingDirectory = '%CD%'; $Shortcut.Description = 'Start MCP Server - Auto Launch'; $Shortcut.IconLocation = 'shell32.dll,23'; $Shortcut.Save()}"

echo Desktop shortcut created!
echo You can now double-click "MCP Server" on your desktop to start the server.
pause
