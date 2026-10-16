# Free & Open-Source WhatsApp Integration (WAHA Docker Engine) & Setup Summary

**Status**: ✅ Complete  
**Reference**: [WAHA Official Quick Start Documentation](https://waha.devlike.pro/docs/overview/quick-start/)

---

## 🚀 Step-by-Step Setup Guide

Follow these verified steps to set up the WAHA Docker Engine, configure webhooks, and start the WhatsApp bridge for your Personal Assistant.

### Step 1: Verify Docker Image
Download the WAHA Docker image and test running it to ensure everything works correctly. This command echoes `ok` to verify the container entrypoint functions properly:
```bash
docker run --rm --entrypoint /bin/sh devlikeapro/waha -c "echo ok"
# Expected output: ok
```

### Step 2: Generate Authentication Credentials
Generate secure environment credentials for WAHA by mounting your local working directory into the container.
1. Navigate to the WhatsApp UI directory:
   ```bash
   cd E:\WORK\PROJECT\git\PersonalAssistant\UI\WhatsApp
   ```
2. Run the initialization command to generate and save the `.env` file containing API keys and dashboard credentials:
   ```bash
   docker run --rm -v "${PWD}:/app/env" devlikeapro/waha init-waha /app/env
   ```
   > ⚠️ **Important**: Ensure the generated credentials are saved locally in `UI\WhatsApp\.env`. (Do not commit actual keys or `.env` files to public repositories).

### Step 3: Run the WAHA Container
Start the WAHA Docker container with your generated environment variables and mount a local sessions volume to persist your WhatsApp login state across restarts:
```bash
docker run -it --env-file "$(PWD)/.env" -v "$(PWD)/sessions:/app/.sessions" --rm -p 3000:3000 --name waha devlikeapro/waha
```

### Step 4: Access WAHA Dashboard
Open your browser and navigate to the WAHA dashboard:
- **URL**: `http://localhost:3000/dashboard/`

### Step 5: Start a WhatsApp Session
In the WAHA dashboard under **Sessions**, start a session with your custom session ID (e.g., `session_01m4w6fcbnbvqc6j5be35bp1vb`) and scan the QR code using WhatsApp on your phone (**Linked Devices** -> **Link a Device**).

### Step 6: Configure Webhooks & Filters
Configure WAHA to forward incoming messages to your local bridge webhook endpoint while ignoring status updates, group chats, channels, and broadcasts. 

Run this PowerShell script to update your session configuration via the WAHA REST API:
```powershell
$body = @{
   config = @{
     webhooks = @(@{ url = "http://host.docker.internal:5002/webhook"; events = @("message.any") })
     ignore   = @{ status = $true; groups = $true; channels = $true; broadcast = $true }
   }
}

Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/YOUR_SESSION_ID" -Method PUT `
   -Headers @{ "x-api-key" = "YOUR_API_KEY" } -ContentType "application/json" -Body ($body | ConvertTo-Json -Depth 10)
```

### Step 7: Check Session Status
Verify whether your WAHA session is running and authenticated successfully:
```powershell
Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/YOUR_SESSION_ID" -Headers @{ "x-api-key" = "YOUR_API_KEY" }
```

### Step 8: Run the WAHA Bridge Flask Server
Start the Python bridge server (`waha_bridge.py`), which listens on port `5002` for incoming webhook messages, passes them to your Personal Assistant agent (`Agent.Main`), and responds back via WAHA:
```bash
python -m UI.WhatsApp.waha_bridge
```

---

## 📂 Architecture & Components

- **WAHA (`devlikeapro/waha`)**: Docker container handling the WhatsApp Web protocol, REST endpoints (`/api/sendText`), and Webhook events (`/webhook`).
- **`UI/WhatsApp/waha_bridge.py`**: Flask server listening on port `5002`. Receives incoming WhatsApp messages, feeds them into your LangChain agent (`Agent.Main(...)`), and replies automatically.

---

## ⚙️ Summary of Endpoints & Message Flow

### Flask Bridge Endpoints (`waha_bridge.py`)
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Receives incoming WhatsApp message events from WAHA |
| `/health` | GET | Health check endpoint |

### Message Lifecycle
1. **Incoming**: WhatsApp message arrives → WAHA Docker Container detects it → Fires POST webhook to `http://host.docker.internal:5002/webhook`.
2. **Processing**: Flask Bridge receives payload → Invokes `Agent.Main(userInput=body, ...)` running your core LLM and tools.
3. **Outgoing**: AI response generated → Bridge calls WAHA REST API (`POST http://localhost:3000/api/sendText`) → Sends message back to user on WhatsApp.

---

## Important Notes & Troubleshooting

### Windows Firewall
Port `5002` must be accessible from inside the Docker container via `host.docker.internal`. If webhook delivery fails, ensure you allow inbound traffic on port 5002:
```powershell
New-NetFirewallRule -DisplayName "WAHA Bridge" -Direction Inbound -LocalPort 5002 -Protocol TCP -Action Allow
```

### Troubleshooting Tips
- **Webhook not receiving**: Check Docker container logs (`docker logs waha -f`) to inspect webhook delivery attempts.
- **Bridge not responding**: Verify that port `5002` is actively listening (`netstat -an | findstr 5002`).
- **Authentication errors**: Ensure your `x-api-key` header matches the key generated in your `.env` file during Step 2. Never hardcode actual keys in shared documentation.
