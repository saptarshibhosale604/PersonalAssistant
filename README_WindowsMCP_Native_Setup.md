# Windows-MCP Native Setup Guide for Personal Assistant (Windows Host)

This guide documents the complete setup of **Windows-MCP** (Model Context Protocol Server for Windows) integrated with the **Personal Assistant (RPI/JARVIS)** project — **both running natively on the same Windows 10/11 machine**. No Docker, no Pi, no container networking. Pure Windows-native deployment.

---

## 📋 Overview

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WINDOWS HOST (Single Machine)                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Windows-MCP Server (Background Service)                            │   │
│  │  windows-mcp serve --transport streamable-http                      │   │
│  │  --host 127.0.0.1 --port 8000                                       │   │
│  │  --auth-key "SECRET"                                                │   │
│  │                                                                      │   │
│  │  Tools: Click, Type, Screenshot, Snapshot, AppLaunch, AppSwitch,    │   │
│  │  Shortcut, Scroll, Move, PowerShell, FileRead/Write, ProcessList,   │   │
│  │  Clipboard, Notification, Registry, DisplayInv, ControlStatus,      │   │
│  │  Browser DOM Mode (Chrome/Edge/Firefox)                             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ▲                                        │
│                                    │ localhost:8000/mcp/                    │
│                                    │ HTTP + Bearer Auth                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Personal Assistant (Native Python)                                 │   │
│  │  ┌─────────────────────────────────────────────────────────────┐   │   │
│  │  │  LangChain MCP Client (langchain-mcp-adapters)              │   │   │
│  │  │  MultiServerMCPClient → Windows-MCP Tools                   │   │   │
│  │  │                                                             │   │   │
│  │  │  toolsWindowsMCP.py → Wrapper tools (sync interface)        │   │   │
│  │  │  toolsManager.py → Dynamic enable/disable via /tools update │   │   │
│  │  │  Agent.Main() → Natural language → Windows actions          │   │   │
│  │  └─────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Key Differences from Docker/Pi Setup:**
- ✅ No TLS/SSL certificates needed (localhost only)
- ✅ No firewall rules needed (localhost only)
- ✅ No `host.docker.internal` networking complexity
- ✅ Simpler auth (no IP allowlist required for localhost)
- ✅ Direct process communication, lower latency

---

## 🖥️ Phase 1: Windows-MCP Server Deployment

### Prerequisites
- Windows 10/11
- Python 3.14+ (install via `winget install Python.Python.3.14` or python.org)
- UV package manager

### Installation Steps

```powershell
# 1. Install UV (if not already installed)
irm https://astral.sh/uv/install.ps1 | iex

# 2. Install Windows-MCP as persistent service (localhost only, no TLS)
uvx windows-mcp install --transport streamable-http --host 127.0.0.1 --port 8000

# 3. Generate auth key + config (no TLS for localhost)
windows-mcp auth --transport streamable-http --host 127.0.0.1 --port 8000
# Output: ~/.windows-mcp/config.toml
# Prints: WINDOWS_MCP_AUTH_KEY=your-generated-key-here
#         WINDOWS_MCP_URL=http://127.0.0.1:8000/mcp/

# 4. Verify scheduled task created
Get-ScheduledTask -TaskName "windows-mcp-server"

# 5. Check logs
Get-Content ~/.windows-mcp/server.log -Wait
Get-Content ~/.windows-mcp/server.error.log -Wait
```

### Generated Config (`~/.windows-mcp/config.toml`)
```toml
[server]
transport = "streamable-http"
host = "127.0.0.1"
port = 8000
auth_key = "generated-secret-key-here"
# No SSL certs needed for localhost

[security]
ip_allowlist = ["127.0.0.1/32", "::1/128"]  # Localhost only

[control]
enabled = true
policy = "relaxed"        # relaxed | balanced | strict
idle_timeout_seconds = 10.0
consent_countdown_seconds = 10
```

### Restart Service (if config changed)
```powershell
Stop-ScheduledTask -TaskName 'windows-mcp-server'
Start-Sleep 2
Start-ScheduledTask -TaskName 'windows-mcp-server'
Start-Sleep 3
Get-ScheduledTask -TaskName 'windows-mcp-server' | Get-ScheduledTaskInfo
```

### Verify Server is Running
```powershell
# Test health endpoint
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" -Method Get

# Test MCP endpoint (requires auth)
$headers = @{ "Authorization" = "Bearer YOUR_AUTH_KEY_FROM_STEP_3" }
Invoke-RestMethod -Uri "http://127.0.0.1:8000/mcp/" -Method Get -Headers $headers
```

---

## 🐍 Phase 2: Personal Assistant Native Installation

### 1. Clone & Setup Project
```powershell
# Clone repository
git clone https://github.com/your-repo/PersonalAssistant.git
cd PersonalAssistant

# Create virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install langchain-mcp-adapters>=0.1.0
```

### 2. Create `toolsWindowsMCP.py` Module
**File:** `Langchain/Tools/toolsWindowsMCP.py`

```python
"""
Windows-MCP Native Tools Wrapper
Connects to Windows-MCP server running on localhost:8000
Provides 22 synchronous wrapper tools for Personal Assistant
"""

import os
import asyncio
from typing import Optional, List, Dict, Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool

# ─── Configuration ───
WINDOWS_MCP_URL = os.getenv("WINDOWS_MCP_URL", "http://127.0.0.1:8000/mcp/")
WINDOWS_MCP_AUTH_KEY = os.getenv("WINDOWS_MCP_AUTH_KEY", "")

# ─── MCP Client Singleton ───
_mcp_client: Optional[MultiServerMCPClient] = None
_mcp_tools: List[BaseTool] = []

async def _get_mcp_client() -> MultiServerMCPClient:
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MultiServerMCPClient({
            "windows-mcp": {
                "url": WINDOWS_MCP_URL,
                "transport": "streamable_http",
                "headers": {"Authorization": f"Bearer {WINDOWS_MCP_AUTH_KEY}"} if WINDOWS_MCP_AUTH_KEY else {}
            }
        })
    return _mcp_client

async def _load_mcp_tools() -> List[BaseTool]:
    global _mcp_tools
    if not _mcp_tools:
        client = await _get_mcp_client()
        _mcp_tools = await client.get_tools()
    return _mcp_tools

def _run_async(coro):
    """Run async coroutine in sync context."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Running in async context - create new task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        return asyncio.run(coro)

# ─── Wrapper Tool Functions ───

def windows_click(x: int, y: int, button: str = "left", clicks: int = 1) -> str:
    """Click at coordinates on Windows desktop."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_click")
    return _run_async(tool.ainvoke({"x": x, "y": y, "button": button, "clicks": clicks}))

def windows_type(text: str, interval: float = 0.01) -> str:
    """Type text on Windows desktop."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_type")
    return _run_async(tool.ainvoke({"text": text, "interval": interval}))

def windows_screenshot(window_title: Optional[str] = None, save_path: Optional[str] = None) -> str:
    """Take a screenshot of the Windows desktop or a specific window."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_screenshot")
    args = {}
    if window_title: args["window_title"] = window_title
    if save_path: args["save_path"] = save_path
    return _run_async(tool.ainvoke(args))

def windows_snapshot(window_title: Optional[str] = None, use_dom: bool = False) -> str:
    """Capture the current UI state (element tree) of the Windows desktop or a specific window."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_snapshot")
    args = {}
    if window_title: args["window_title"] = window_title
    if use_dom: args["use_dom"] = use_dom
    return _run_async(tool.ainvoke(args))

def windows_app_launch(app_name: str, args: Optional[List[str]] = None) -> str:
    """Launch a Windows application by name or path."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_app_launch")
    invoke_args = {"app_name": app_name}
    if args: invoke_args["args"] = args
    return _run_async(tool.ainvoke(invoke_args))

def windows_app_switch(app_name: str) -> str:
    """Switch to/focus a running Windows application."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_app_switch")
    return _run_async(tool.ainvoke({"app_name": app_name}))

def windows_shortcut(keys: str) -> str:
    """Send a keyboard shortcut (hotkey) on Windows."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_shortcut")
    return _run_async(tool.ainvoke({"keys": keys}))

def windows_scroll(x: int, y: int, delta: int) -> str:
    """Scroll the mouse wheel on Windows."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_scroll")
    return _run_async(tool.ainvoke({"x": x, "y": y, "delta": delta}))

def windows_move_mouse(x: int, y: int, duration: float = 0.2) -> str:
    """Move the mouse cursor to coordinates on Windows."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_move_mouse")
    return _run_async(tool.ainvoke({"x": x, "y": y, "duration": duration}))

def windows_powershell(command: str, timeout: int = 30) -> str:
    """Execute a PowerShell command on the Windows host."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_powershell")
    return _run_async(tool.ainvoke({"command": command, "timeout": timeout}))

def windows_file_read(path: str) -> str:
    """Read a file from the Windows host filesystem."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_file_read")
    return _run_async(tool.ainvoke({"path": path}))

def windows_file_write(path: str, content: str) -> str:
    """Write a file to the Windows host filesystem."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_file_write")
    return _run_async(tool.ainvoke({"path": path, "content": content}))

def windows_file_system(mode: str, path: str, content: Optional[str] = None) -> str:
    """Read/write/list files on the Windows host filesystem."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_file_system")
    args = {"mode": mode, "path": path}
    if content is not None: args["content"] = content
    return _run_async(tool.ainvoke(args))

def windows_process_list() -> str:
    """List running processes on the Windows host."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_process_list")
    return _run_async(tool.ainvoke({}))

def windows_process_kill(pid: int) -> str:
    """Kill a process on the Windows host."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_process_kill")
    return _run_async(tool.ainvoke({"pid": pid}))

def windows_clipboard_get() -> str:
    """Get clipboard content from the Windows host."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_clipboard_get")
    return _run_async(tool.ainvoke({}))

def windows_clipboard_set(content: str) -> str:
    """Set clipboard content on the Windows host."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_clipboard_set")
    return _run_async(tool.ainvoke({"content": content}))

def windows_notification(title: str, message: str, app_id: str = "Windows-MCP") -> str:
    """Send a Windows toast notification."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_notification")
    return _run_async(tool.ainvoke({"title": title, "message": message, "app_id": app_id}))

def windows_registry_read(key: str, value_name: str) -> str:
    """Read a Windows Registry value."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_registry_read")
    return _run_async(tool.ainvoke({"key": key, "value_name": value_name}))

def windows_registry_write(key: str, value_name: str, value: str, value_type: str = "REG_SZ") -> str:
    """Write a Windows Registry value. ⚠️ USE WITH EXTREME CAUTION"""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_registry_write")
    return _run_async(tool.ainvoke({"key": key, "value_name": value_name, "value": value, "value_type": value_type}))

def windows_display_inventory() -> str:
    """Get display/monitor information from the Windows host."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_display_inventory")
    return _run_async(tool.ainvoke({}))

def windows_control_status() -> str:
    """Get the current desktop control status from Windows-MCP."""
    tools = _run_async(_load_mcp_tools())
    tool = next(t for t in tools if t.name == "windows_control_status")
    return _run_async(tool.ainvoke({}))

# ─── Tool Registry for toolsManager.py ───
TOOLS = {
    "windows_click": windows_click,
    "windows_type": windows_type,
    "windows_screenshot": windows_screenshot,
    "windows_snapshot": windows_snapshot,
    "windows_app_launch": windows_app_launch,
    "windows_app_switch": windows_app_switch,
    "windows_shortcut": windows_shortcut,
    "windows_scroll": windows_scroll,
    "windows_move_mouse": windows_move_mouse,
    "windows_powershell": windows_powershell,
    "windows_file_read": windows_file_read,
    "windows_file_write": windows_file_write,
    "windows_file_system": windows_file_system,
    "windows_process_list": windows_process_list,
    "windows_process_kill": windows_process_kill,
    "windows_clipboard_get": windows_clipboard_get,
    "windows_clipboard_set": windows_clipboard_set,
    "windows_notification": windows_notification,
    "windows_registry_read": windows_registry_read,
    "windows_registry_write": windows_registry_write,
    "windows_display_inventory": windows_display_inventory,
    "windows_control_status": windows_control_status,
}

def get_tools() -> Dict[str, callable]:
    """Return all Windows-MCP tools for registration."""
    return TOOLS
```

### 3. Register in `toolsManager.py`
```python
# In TOOLS_MODULES dict (add this entry):
"toolsWindowsMCP": "Langchain.Tools.toolsWindowsMCP",

# In DEFAULT_CONFIG (disabled by default - requires Windows-MCP server running):
"toolsWindowsMCP": False,
```

### 4. Update `toolsConfig.json`
```json
{
  "toolsWindowsMCP": true,
  ...
}
```

### 5. Environment Variables (`.env` in project root)
```bash
# Windows-MCP Connection (Native Windows)
WINDOWS_MCP_URL=http://127.0.0.1:8000/mcp/
WINDOWS_MCP_AUTH_KEY=your-auth-key-from-phase-1-step-3
```

### 6. Enable via CLI
```powershell
# Activate venv first
.\.venv\Scripts\Activate.ps1

# Run Personal Assistant
python -m Agent.Main

# In Personal Assistant CLI:
/tools update
# Select: toolsWindowsMCP
# Choose: 1 (Enable)
```

---

## 🎖️ Advanced Features

### 1. Skill Integration
**Create `Skill/windows_automation.md`:**
```markdown
# Windows Automation Skill

You are controlling a Windows desktop via Windows-MCP tools. 
Available tools: windows_click, windows_type, windows_screenshot, windows_snapshot, windows_app_launch, windows_app_switch, windows_shortcut, windows_scroll, windows_move_mouse, windows_powershell, windows_file_read, windows_file_write, windows_file_system, windows_process_list, windows_process_kill, windows_clipboard_get, windows_clipboard_set, windows_notification, windows_registry_read, windows_registry_write, windows_display_inventory, windows_control_status.

WORKFLOW:
1. Use `windows_snapshot` to understand current UI state
2. Use `windows_click` / `windows_type` / `windows_shortcut` for interaction
3. Use `windows_screenshot` for visual verification
4. Use `windows_app_launch` / `windows_app_switch` for app management
5. Use `windows_powershell` for system-level operations

SAFETY:
- Always snapshot before clicking
- Verify target window with `windows_app_switch` first
- Use `windows_control_status` to check desktop control state
- Respect the consent dialog (screen edges turn amber, 10s countdown)
- Emergency takeover: Ctrl+Alt+Shift+Backspace
```

**Invoke via:** `/windows_automation "open notepad and type hello world"`

### 2. Desktop Control Policies
Windows-MCP implements three gate policies:

| Policy | Direct Input (Click, Type, Scroll) | System Tools (PS, Notify, App, Process, Clipboard) | Background Tools (FS, Reg, Snapshot, Screenshot) |
|--------|-----------------------------------|---------------------------------------------------|------------------------------------------------|
| **Relaxed (A, default)** | ✅ Gated (consent dialog) | ❌ Ungated | ✅ Ungated |
| **Balanced (B)** | ✅ Gated | ✅ Gated | ✅ Ungated |
| **Strict (C)** | ✅ Gated | ✅ Gated | ✅ Gated |

Change policy in `~/.windows-mcp/config.toml`:
```toml
[control]
policy = "balanced"  # or "strict"
```

### 3. Browser Automation (DOM Mode)
- `use_dom=True` in `windows_snapshot` filters browser chrome, targets page content only
- Supports Chrome, Edge, Firefox (Firefox uses IAccessible2 fallback)
- Enables clean web automation without Selenium/Playwright

---

## 📋 Deployment Checklist (Native Windows)

| Step | Action | Status |
|------|--------|--------|
| 1 | Install UV on Windows | ☐ |
| 2 | `uvx windows-mcp install --transport streamable-http --host 127.0.0.1 --port 8000` | ☐ |
| 3 | `windows-mcp auth --transport streamable-http --host 127.0.0.1 --port 8000` | ☐ |
| 4 | Save `WINDOWS_MCP_AUTH_KEY` from step 3 output | ☐ |
| 5 | Verify service running: `Get-ScheduledTask -TaskName windows-mcp-server` | ☐ |
| 6 | Clone Personal Assistant repo | ☐ |
| 7 | Create venv & install deps (`pip install -r requirements.txt langchain-mcp-adapters`) | ☐ |
| 8 | Create `Langchain/Tools/toolsWindowsMCP.py` | ☐ |
| 9 | Register in `toolsManager.py` TOOLS_MODULES & DEFAULT_CONFIG | ☐ |
| 10 | Add env vars to `.env` | ☐ |
| 11 | Enable via `/tools update` → `toolsWindowsMCP` → `1` | ☐ |
| 12 | Test: "Take a screenshot of my Windows desktop" | ☐ |
| 13 | Test: "Open Notepad and type hello" | ☐ |
| 14 | Test: "Run Get-Process in PowerShell" | ☐ |

---

## ⚠️ Known Gotchas & Mitigations (Native)

| Issue | Mitigation |
|-------|------------|
| **Service not starting** | Check `~/.windows-mcp/server.error.log`; ensure Python 3.14+ |
| **Auth failures** | Verify `WINDOWS_MCP_AUTH_KEY` in `.env` matches server config |
| **Tool name conflicts** | Windows-MCP tools prefixed with `windows_` in our wrapper |
| **Async in sync tools** | We use `asyncio.run()` — acceptable for CLI, consider `anyio` for production |
| **Python 3.14 requirement** | Windows-MCP requires 3.14+; ensure Windows host has it |
| **Registry write** | ⚠️ **WARNING**: Modifying Windows Registry can cause system instability. Always backup first. |
| **Consent dialog blocks automation** | Policy "relaxed" gates direct input; use `windows_control_status` to check |
| **Browser DOM not working** | Ensure browser is Chrome/Edge/Firefox; try `use_dom=True` in snapshot |

---

## 🎯 Command Examples (Post-Integration)

```bash
# Natural language → Windows actions
"Take a screenshot of my Windows desktop"
"Open Chrome and go to github.com"
"Click the Start button"
"Type 'hello world' in Notepad"
"Run 'Get-Process' in PowerShell"
"List all running processes"
"Copy 'secret password' to clipboard"
"Send a Windows notification saying 'Build complete'"
"Switch to Visual Studio Code"
"Press Win+D to show desktop"
"Scroll down 500 pixels"
"Read C:\\Users\\SSB\\Documents\\notes.txt"
"Kill process 1234"
"Get display info"
"Check Windows-MCP control status"
```

---

## 🔗 References

- **Windows-MCP Repo:** https://github.com/CursorTouch/Windows-MCP
- **MCP Protocol:** https://modelcontextprotocol.io/
- **langchain-mcp-adapters:** https://github.com/langchain-ai/langchain-mcp-adapters
- **Existing Windows Tools Plan:** `Plan/windows_os_tools_plan.md`
- **Existing Windows Tools Report:** `Plan/windows_os_tools_implementation_report.md`
- **Docker/Pi Integration Guide:** `README_WindowsMCP_Setup.md`

---

## 📝 Notes

This **native Windows deployment** eliminates all container networking complexity, TLS certificate management, and cross-machine latency. The Personal Assistant runs as a standard Python application on Windows, connecting to Windows-MCP via localhost HTTP. Ideal for development, single-machine automation, and scenarios where Docker/Pi infrastructure is unavailable.

**Recommendation:** Use this native setup for development and single-machine production. Use the Docker/Pi guide (`README_WindowsMCP_Setup.md`) for distributed deployments.

---

*Prepared by RPI Tactical AI — For General SSB* 🫡