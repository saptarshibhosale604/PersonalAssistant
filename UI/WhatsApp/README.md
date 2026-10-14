# Free & Open-Source WhatsApp Integration (WAHA Docker Engine)

Integrate WhatsApp with your Personal Assistant completely for free using **WAHA (WhatsApp HTTP API)** (`devlikeapro/waha`), which runs locally in Docker and connects via WhatsApp Web QR code scan.

---

## 🚀 Quick Setup Guide

### Step 1: Start WAHA Docker Container
Run the free open-source WAHA Docker container:
```bash
docker run -d -it -p 3000:3000 --name waha devlikeapro/waha
```

### Step 2: Scan QR Code & Authenticate
1. Open your browser and go to **`http://localhost:3000`** (WAHA Swagger UI and session manager).
2. Start the default session or view the QR code in the WAHA dashboard / logs (`docker logs waha`).
3. Open WhatsApp on your phone -> **Linked Devices** -> **Link a Device** -> Scan the QR code.
4. Once authenticated, WAHA is connected to your WhatsApp account.

### Step 3: Run the WAHA Bridge
Start the local bridge server (`waha_bridge.py`), which listens for incoming webhook events on port `5002` and connects them to the Personal Assistant agent (`Agent.Main`):
```bash
python UI/WhatsApp/waha_bridge.py

python -m UI.WhatsApp.waha_bridge
```

### Step 4: Configure WAHA Webhook
Configure WAHA to forward incoming messages to your local bridge webhook endpoint. You can set this via environment variable when starting WAHA or via API:
- Webhook URL: `http://host.docker.internal:5002/webhook` (if WAHA is in Docker and bridge is on host) or `http://localhost:5002/webhook` (if both run on host).
- Example WAHA API call to set webhook:
  ```bash
  curl -X POST "http://localhost:3000/api/sessions/default" -H "Content-Type: application/json" -d '{"webhook": {"url": "http://localhost:5002/webhook", "events": ["message"]}}'
  ```

---

## 📂 Architecture
- **WAHA (`devlikeapro/waha`)**: Docker container handling WhatsApp Web protocol and providing REST endpoints (`/api/sendText`) + Webhook events (`/webhook`).
- **`UI/WhatsApp/waha_bridge.py`**: Flask server listening on port `5002`. Receives incoming WhatsApp messages, feeds them into `Langchain.agent.Main(...)`, and replies back automatically.
