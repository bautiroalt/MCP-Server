Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the current directory
strCurrentDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Create shortcut
Set objShortcut = objShell.CreateShortcut(strCurrentDir & "\MCP Server.lnk")
objShortcut.TargetPath = strCurrentDir & "\AUTO-START-MCP.bat"
objShortcut.WorkingDirectory = strCurrentDir
objShortcut.Description = "Start MCP Server - Auto Launch"
objShortcut.IconLocation = "shell32.dll,23"
objShortcut.Save

WScript.Echo "MCP Server shortcut created successfully!"
