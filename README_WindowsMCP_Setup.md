# Windows-MCP Setup Guide for Personal Assistant

This guide documents the complete setup of **Windows-MCP** (Model Context Protocol Server for Windows) integration with the Personal Assistant (RPI/JARVIS) project.

---

## 📋 Overview

**Windows-MCP** (`https://github.com/CursorTouch/Windows-MCP`) is a production-grade MCP server that exposes native Windows UI Automation to any LLM. It runs on Windows 10/11 and provides 20+ tools for desktop control, application management, file system, registry, browser automation (DOM mode), and system administration.

**Integration Architecture:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WINDOWS HOST (Physical PC / VM)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  windows-mcp serve --transport streamable-http                      │   │
│  │  --host 0.0.0.0 --port 8000                                         │   │
│  │  --auth-key "SECRET" --ip-allowlist "192.168.1.0/24"                │   │
│  │  --ssl-certfile cert.pem --ssl-keyfile key.pem                      │   │
│  │                                                                      │   │
│  │  Tools Exposed: Click, Type, Screenshot, Snapshot, AppLaunch,       │   │
│  │  AppSwitch, Shortcut, Scroll, Move, PowerShell, FileRead/Write,     │   │
│  │  ProcessList/Kill, Clipboard, Notification, Registry, DisplayInv,   │   │
│  │  ControlStatus, Browser DOM Mode (Chrome/Edge/Firefox)              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │ HTTPS + Bearer Auth + mTLS optional
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RASPBERRY PI / DOCKER (Personal Assistant)                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LangChain MCP Client (langchain-mcp-adapters)                      │   │
│  │  MultiServerMCPClient → Windows-MCP Tools                           │   │
│  │                                                                      │   │
│  │  toolsWindowsMCP.py → Wrapper tools (sync interface)                │   │
│  │  toolsManager.py → Dynamic enable/disable via /tools update         │   │
│  │  Agent.Main() → Natural language → Windows actions                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Phase 1: Windows Host Deployment

### Prerequisites
- Windows 10/11
- Python 3.14+ (install via `winget install Python.Python.3.14` or python.org)
- UV package manager

### Installation Steps

```powershell
# 1. Install UV
irm https://astral.sh/uv/install.ps1 | iex

# 2. Install Windows-MCP as persistent service
uvx windows-mcp install --transport streamable-http --host 0.0.0.0 --port 8000

# 3. Generate auth key + self-signed TLS cert + config
windows-mcp auth --transport streamable-http --host 0.0.0.0 --port 8000 --with-tls
# Output: ~/.windows-mcp/config.toml, cert.pem, key.pem
# Prints example client config for Claude Desktop / custom clients

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
host = "0.0.0.0"
port = 8000
auth_key = "generated-secret-key-here"
ssl_certfile = "cert.pem"
ssl_keyfile = "key.pem"

[security]
ip_allowlist = ["192.168.1.0/24"]  # ADJUST to Pi's subnet / Tailscale CIDR

[control]
enabled = true
policy = "relaxed"        # relaxed | balanced | strict
idle_timeout_seconds = 10.0
consent_countdown_seconds = 10
```

### Firewall Rule (PowerShell Admin)
```powershell
New-NetFirewallRule -DisplayName "Windows-MCP" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow
```

### Certificate Generation (if --with-tls fails)
If the built-in `--with-tls` fails (OpenSSL not found), generate certs manually:

```powershell
# Create self-signed certificate with exportable private key
$cert = New-SelfSignedCertificate -DnsName 'localhost' -CertStoreLocation 'Cert:\CurrentUser\My' -NotAfter (Get-Date).AddYears(1) -KeyAlgorithm RSA -KeyLength 4096 -FriendlyName 'Windows-MCP-Final' -KeyExportPolicy Exportable -Provider 'Microsoft Enhanced Cryptographic Provider v1.0'

# Export to PFX
certutil -user -p windows-mcp -exportpfx My $cert.Thumbprint 'E:\WORK\PROJECT\git\PersonalAssistant\cert_final.pfx' NoChain,NoRoot

# Convert to PEM using .NET
Add-Type -AssemblyName System.Security
$cert2 = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2('E:\WORK\PROJECT\git\PersonalAssistant\cert_final.pfx', 'windows-mcp', [System.Security.Cryptography.X509Certificates.X509KeyStorageFlags]::Exportable)

# Export certificate
$pemCert = '-----BEGIN CERTIFICATE-----' + [Environment]::NewLine + [Convert]::ToBase64String($cert2.Export([System.Security.Cryptography.X509Certificates.X509ContentType]::Cert), [System.Base64FormattingOptions]::InsertLineBreaks) + [Environment]::NewLine + '-----END CERTIFICATE-----'
[System.IO.File]::WriteAllText('C:\Users\LENOVO\.windows-mcp\cert.pem', $pemCert)

# Export private key (PKCS#8 via CngKey)
$key = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($cert2)
$cngKey = $key.Key
$pemKey = '-----BEGIN PRIVATE KEY-----' + [Environment]::NewLine + [Convert]::ToBase64String($cngKey.Export([System.Security.Cryptography.CngKeyBlobFormat]::Pkcs8PrivateBlob), [System.Base64FormattingOptions]::InsertLineBreaks) + [Environment]::NewLine + '-----END PRIVATE KEY-----'
[System.IO.File]::WriteAllText('C:\Users\LENOVO\.windows-mcp\key.pem', $pemKey)
```

### Restart Service
```powershell
Stop-ScheduledTask -TaskName 'windows-mcp-server'
Start-Sleep 2
Start-ScheduledTask -TaskName 'windows-mcp-server'
Start-Sleep 3
Get-ScheduledTask -TaskName 'windows-mcp-server' | Get-ScheduledTaskInfo
```

---

## 🐳 Phase 2: Personal Assistant (Pi/Docker) Integration

### 1. Add Dependency
```dockerfile
# Dockerfile
RUN pip install langchain-mcp-adapters>=0.1.0
```

```txt
# requirements.txt
langchain-mcp-adapters>=0.1.0
```

### 2. Create `toolsWindowsMCP.py` Module
**File:** `Langchain/Tools/toolsWindowsMCP.py`

This module provides 22 wrapper tools that connect to Windows-MCP via MCP protocol:
- `windows_click`, `windows_type`, `windows_screenshot`, `windows_snapshot`
- `windows_app_launch`, `windows_app_switch`, `windows_shortcut`
- `windows_scroll`, `windows_move_mouse`, `windows_powershell`
- `windows_file_read`, `windows_file_write`, `windows_file_system`
- `windows_process_list`, `windows_process_kill`
- `windows_clipboard_get`, `windows_clipboard_set`
- `windows_notification`
- `windows_registry_read`, `windows_registry_write` ⚠️ **Use with extreme caution**
- `windows_display_inventory`, `windows_control_status`

### 3. Register in `toolsManager.py`
```python
# In TOOLS_MODULES dict:
"toolsWindowsMCP": "Langchain.Tools.toolsWindowsMCP",

# In DEFAULT_CONFIG:
"toolsWindowsMCP": False,  # Disabled by default (requires Windows host)
```

### 4. Update `toolsConfig.json`
```json
{
  "toolsWindowsMCP": true,
  ...
}
```

### 5. Environment Variables (`.env`)
```bash
# Windows-MCP Connection
WINDOWS_MCP_URL=https://192.168.1.100:8000/mcp/
WINDOWS_MCP_AUTH_KEY=EYRk-zIft8WoL-EVDTxvXH2-ln5IYcUnvML1EYFK-TI
WINDOWS_MCP_VERIFY_SSL=false
```

### 6. Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  personal_assistant:
    build: .
    container_name: personal_assistant
    environment:
      - WINDOWS_MCP_URL=https://host.docker.internal:8000/mcp/
      - WINDOWS_MCP_AUTH_KEY=${WINDOWS_MCP_AUTH_KEY}
      - WINDOWS_MCP_VERIFY_SSL=false
      # ... other env vars
    volumes:
      - ./:/App
      - ollama:/root/.ollama
    ports:
      - "11434:11434"
      - "5001:5001"
      - "5002:5002"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

volumes:
  ollama:
```

### 7. Enable via CLI
```bash
# In Personal Assistant CLI:
/tools update
# Select: toolsWindowsMCP
# Choose: 1 (Enable)
```

---

## 🎖️ Advanced Features

### 1. Skill Integration
**Create `Skill/windows_automation`:**
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

### 3. Browser Automation (DOM Mode)
- `use_dom=True` in `windows_snapshot` filters browser chrome, targets page content only
- Supports Chrome, Edge, Firefox (Firefox uses IAccessible2 fallback)
- Enables clean web automation without Selenium/Playwright on Pi

---

## 📋 Deployment Checklist

| Step | Action | Status |
|------|--------|--------|
| 1 | Install UV on Windows host | ☐ |
| 2 | `uvx windows-mcp install --transport streamable-http --host 0.0.0.0 --port 8000` | ☐ |
| 3 | `windows-mcp auth --transport streamable-http --host 0.0.0.0 --port 8000 --with-tls` | ☐ |
| 4 | Configure `ip_allowlist` in `~/.windows-mcp/config.toml` for Pi subnet | ☐ |
| 5 | Add firewall rule for port 8000 | ☐ |
| 6 | Add `langchain-mcp-adapters` to Dockerfile/requirements | ☐ |
| 7 | Create `Langchain/Tools/toolsWindowsMCP.py` | ☐ |
| 8 | Register in `toolsManager.py` TOOLS_MODULES & DEFAULT_CONFIG | ☐ |
| 9 | Add env vars to `.env` / docker-compose.yml | ☐ |
| 10 | Rebuild Docker image | ☐ |
| 11 | Enable via `/tools update` → `toolsWindowsMCP` → `1` | ☐ |
| 12 | Test: "Take a screenshot of my Windows desktop" | ☐ |
| 13 | Test: "Open Notepad on Windows and type hello" | ☐ |
| 14 | Test: "Run Get-Process in PowerShell on Windows" | ☐ |

---

## ⚠️ Known Gotchas & Mitigations

| Issue | Mitigation |
|-------|------------|
| **Self-signed cert** | Set `WINDOWS_MCP_VERIFY_SSL=false` or add cert to trust store |
| **Network latency** | Use Tailscale/VPN for stable Pi↔Windows connection |
| **Firewall** | Allow port 8000 on Windows (see Phase 1) |
| **Docker host networking** | Use `host.docker.internal` (Docker Desktop) or `extra_hosts: host.docker.internal:host-gateway` |
| **Tool name conflicts** | Windows-MCP tools prefixed with `windows_` in our wrapper |
| **Async in sync tools** | We use `asyncio.run()` — acceptable for CLI, consider `anyio` for production |
| **Python 3.14 requirement** | Windows-MCP requires 3.14+; ensure Windows host has it |
| **IP allowlist** | Must include Pi's IP / Tailscale CIDR / Docker subnet |
| **Registry write** | ⚠️ **WARNING**: Modifying Windows Registry can cause system instability. Always backup first. |

---

## 🎯 Command Examples (Post-Integration)

```bash
# Natural language → Windows actions
"Take a screenshot of my Windows PC"
"Open Chrome on Windows and go to github.com"
"Click the Start button on Windows"
"Type 'hello world' in Notepad on Windows"
"Run 'Get-Process' in PowerShell on Windows"
"List all running processes on my Windows machine"
"Copy 'secret password' to Windows clipboard"
"Send a Windows notification saying 'Build complete'"
"Switch to Visual Studio Code on Windows"
"Press Win+D to show desktop on Windows"
"Scroll down 500 pixels on Windows"
"Read C:\\Users\\SSB\\Documents\\notes.txt on Windows"
"Kill process 1234 on Windows"
"Get display info from Windows"
"Check Windows-MCP control status"
```

---

## 🔗 References

- **Windows-MCP Repo:** https://github.com/CursorTouch/Windows-MCP
- **MCP Protocol:** https://modelcontextprotocol.io/
- **langchain-mcp-adapters:** https://github.com/langchain-ai/langchain-mcp-adapters
- **Existing Windows Tools Plan:** `Plan/windows_os_tools_plan.md`
- **Existing Windows Tools Report:** `Plan/windows_os_tools_implementation_report.md`
- **Integration Plan:** `Plan/windows_mcp_integration_plan.md`

---

## 📝 Notes

This integration transforms Personal Assistant into a **cross-platform command nexus** — Linux-hosted brain, Windows-native hands. The Windows-MCP server handles all complex UIA/COM interop, desktop consent gating, and browser DOM extraction natively on Windows, while the Pi orchestrates via clean MCP protocol.

**Recommendation:** Proceed with Phase 1 immediately. Windows-MCP is mature (12k+ stars, 2M+ Claude Desktop users, v0.8.9 Nov 2026).

---

*Prepared by RPI Tactical AI — For General SSB* 🫡