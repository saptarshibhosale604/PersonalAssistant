# WAHA Webhook Configuration Summary

**Date**: 2026-10-13  
**Status**: ✅ Complete

---

## Configuration Details

### WAHA Docker Container
- **Container name**: `waha`
- **Image**: `devlikeapro/waha`
- **Port**: 3000 (mapped to localhost:3000)
- **Session volume**: `E:\WORK\PROJECT\git/sessions:/app/.sessions`

### Authentication Credentials (auto-generated via `init-waha`)
| Credential | Value |
|------------|-------|
| **API Key** | `0169fae66756404188915888e0827b7c` |
| **Dashboard Username** | `admin` |
| **Dashboard Password** | `de7e511b76f8476d969fea4f1f0ec59b` |
| **Swagger Username** | `admin` |
| **Swagger Password** | `de7e511b76f8476d969fea4f1f0ec59b` |

### Active WhatsApp Session
- **Session ID**: `session_01m4v3qya8pbrgxh954j3k10d8`
- **Status**: `WORKING`
- **Engine**: `WEBJS`
- **Connected as**: `Saptarshi Bhosale` (917058033447@c.us)
- **WhatsApp Web Version**: 2.3000.1050196505

---

## Webhook Configuration

### API Call Used
```bash
curl -X PUT "http://localhost:3000/api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb" \
  -H "x-api-key: 0169fae66756404188915888e0827b7c" \
  -H "Content-Type: application/json" \
  -d '{"config": {"webhooks": [{"url": "http://host.docker.internal:5002/webhook", "events": ["message"]}]}}'
```
```Powershell
$body = @{
    config = @{
        webhooks = @(
            @{
                url = "http://host.docker.internal:5002/webhook"
                events = @("message")
            }
        )
    }
}

Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb" `
    -Method PUT `
    -Headers @{ "x-api-key" = "0169fae66756404188915888e0827b7c" } `
    -ContentType "application/json" `
    -Body ($body | ConvertTo-Json -Depth 10)
```

### Persisted Session Config
```json
{
  "config": {
    "webhooks": [
      {
        "url": "http://host.docker.internal:5002/webhook",
        "events": ["message"]
      }
    ]
  }
}
```

---

## WAHA Bridge (Flask Server)

### What is the use of this Flask Server (`waha_bridge.py`)?
The Flask server acts as the **bridge (connector)** between **WAHA (WhatsApp HTTP API running in Docker)** and your **Personal Assistant Core Agent (`Agent.Main`)**.

Here is the exact lifecycle of how it works when someone sends you a WhatsApp message:
1. **Incoming WhatsApp Message:** Someone sends a WhatsApp message to your connected WhatsApp number (+91 70580 33447).
2. **WAHA Container:** WAHA (running in Docker on port 3000) detects this incoming message.
3. **Webhook Trigger:** WAHA fires a webhook (`POST /webhook`) to `http://host.docker.internal:5002/webhook`.
4. **Flask Bridge (`waha_bridge.py`):** 
   - Receives the webhook request.
   - Extracts the sender's phone number and the message text (`body`).
   - Passes the message to your Personal Assistant core: `Agent.Main(userInput=body, thread_id=9999, ...)` which runs your LangChain agent, tools, and LLM (Gemini).
   - Takes the resulting AI response and calls WAHA's outbound REST API (`POST http://localhost:3000/api/sendText`) to reply directly back to the user on WhatsApp.

Without this Flask server, WAHA would receive WhatsApp messages, but your Personal Assistant wouldn't know about them or be able to respond.

### Start Command
```bash
python -m UI.WhatsApp.waha_bridge
```

### Configuration
- **Port**: 5002
- **Host**: 0.0.0.0 (all interfaces)
- **WAHA Base URL**: http://localhost:3000
- **WAHA Session**: default (uses session_01m4v3qya8pbrgxh954j3k10d8)
- **Thread ID**: 9999 (for WhatsApp context tracking)
- **Model**: gemini-3.5-flash-lite (globalGemini02)

### Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Receives incoming WhatsApp messages from WAHA |
| `/health` | GET | Health check |

### Message Flow
1. **Incoming**: WhatsApp → WAHA (Docker) → POST `http://host.docker.internal:5002/webhook`
2. **Process**: Bridge → `Agent.Main(userInput, thread_id=9999, llmName="gemini-3.6-flash")`
3. **Outgoing**: Bridge → WAHA `/api/sendText` → WhatsApp

---

## Important Notes

### Windows Firewall
Port 5002 must be accessible from Docker container via `host.docker.internal`. 
If webhook delivery fails, add Windows Firewall rule:
```powershell
New-NetFirewallRule -DisplayName "WAHA Bridge" -Direction Inbound -LocalPort 5002 -Protocol TCP -Action Allow
```

### Testing the Integration
1. Ensure bridge is running: `python -m UI.WhatsApp.waha_bridge`
2. Send a WhatsApp message to the connected number (+91 70580 33447)
3. Check bridge logs for incoming message processing
4. Verify AI response is sent back via WhatsApp

### Troubleshooting
- **Webhook not receiving**: Check Docker logs `docker logs waha -f` for webhook delivery attempts
- **Bridge not responding**: Verify port 5002 is listening: `netstat -an | findstr 5002`
- **Auth errors**: Ensure `x-api-key` header is included in all WAHA API calls

---

## Files Reference
- **Bridge code**: `UI/WhatsApp/waha_bridge.py`
- **README**: `UI/WhatsApp/README.md`
- **This summary**: `UI/WhatsApp/WAHA_SETUP_SUMMARY.md`