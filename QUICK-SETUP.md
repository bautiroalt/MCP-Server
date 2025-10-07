# MCP Server - Quick Setup Guide

## 🚀 ONE-CLICK START

### Option 1: Desktop Shortcut (Recommended)
1. **Double-click**: `create-desktop-shortcut.bat`
2. **Double-click**: "MCP Server" icon on your desktop
3. **Done!** Browser opens automatically

### Option 2: Direct Start
1. **Double-click**: `AUTO-START-MCP.bat`
2. **Wait 10 seconds** for servers to start
3. **Browser opens automatically**

## 🔧 ADVANCED OPTIONS

### Auto-Start on Windows Boot
1. **Double-click**: `install-startup.bat`
2. **MCP Server will start automatically** when Windows boots

### Keep Servers Running (Optional)
1. **Double-click**: `keep-alive.bat`
2. **Monitors servers** and restarts if they crash
3. **Keeps running** until you close the window

## 📋 WHAT HAPPENS AUTOMATICALLY

1. **Backend Server** starts on http://localhost:8000
2. **Interface Server** starts on http://localhost:3001
3. **Browser opens** to http://localhost:3001/mcp-interface.html
4. **File uploads work** immediately
5. **No "server not found" errors**

## 🔄 MAKING CODE CHANGES

1. **Edit any code** in the project
2. **Refresh browser page** (F5 or Ctrl+R)
3. **Changes appear immediately**

## 🛑 STOPPING SERVERS

- **Close browser tab** (interface stops automatically)
- **Close minimized server windows** (if visible)
- **Press Ctrl+C** in any server window

## ✅ VERIFICATION

- **Backend**: http://localhost:8000/health
- **Interface**: http://localhost:3001/mcp-interface.html
- **File Upload**: Works in the interface

## 🆘 TROUBLESHOOTING

### If servers don't start:
1. **Check Python is installed**: `python --version`
2. **Check ports are free**: `netstat -an | findstr ":8000"`
3. **Run AUTO-START-MCP.bat** again

### If "server not found" appears:
1. **Wait 10 seconds** and refresh browser
2. **Check servers are running**: Look for minimized windows
3. **Restart**: Close all and run AUTO-START-MCP.bat again

## 🎯 RESULT

**One double-click = Complete MCP Server running!**
**No manual steps, no errors, no waiting!**
