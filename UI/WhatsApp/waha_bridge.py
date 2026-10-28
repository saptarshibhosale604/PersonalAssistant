"""
WAHA (WhatsApp HTTP API) Bridge for Personal Assistant.

Runs a local Flask webhook listener on port 5002 to receive incoming WhatsApp messages from WAHA,
passes them through the Personal Assistant's core LangChain Agent (`Agent.Main`),
and sends the AI response back to the WhatsApp user via WAHA's outbound REST API.

SECURITY / MESSAGE FILTERING POLICY:
- ALLOWED: Messages sent by you TO you (Self-chat / "Message Yourself" mode).
- DENIED:  Messages sent by you TO others (Outbound messages to other users/groups).
- DENIED:  Messages sent by others TO you (Incoming messages from external contacts).
"""

import os
import sys
import json
import requests
from collections import deque
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import Langchain.agent as Agent
import UserContext.userContext as UserContext
import UI.cli as CLI
from Log.custom_logger import logger

app = Flask(__name__)

# WAHA configuration
WAHA_BASE_URL = os.getenv("WAHA_BASE_URL", "http://localhost:3000")
WAHA_SESSION = os.getenv("WAHA_SESSION", "session_01m4w6fcbnbvqc6j5be35bp1vb")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "0169fae66756404188915888e0827b7c")

# Thread ID for WhatsApp context tracking
WHATSAPP_THREAD_ID = 9999

# Allowed sender phone number filter (empty string or None to allow all)
# WAHA WebJS engine uses LID format (e.g. 131967181967606@lid) for some chats while phone is 919922113131@c.us
# We can allow specific numbers, or set ALLOWED_SENDER = "" to allow all senders.
ALLOWED_SENDER = os.getenv("WAHA_ALLOWED_SENDER", "")

# Recently seen message IDs (dedupe when WAHA delivers both "message" and "message.any")
SEEN_MESSAGE_IDS = deque(maxlen=200)
# Recently sent bot replies; our own replies come back as fromMe events and must be skipped
BOT_SENT_TEXTS = deque(maxlen=50)

def send_whatsapp_message(chat_id: str, text: str):
    """Send text message back to WhatsApp via WAHA API."""
    # Record before sending: the fromMe webhook for this reply can arrive before the POST returns
    BOT_SENT_TEXTS.append(text)
    url = f"{WAHA_BASE_URL}/api/sendText"
    payload = {
        "chatId": chat_id,
        "text": text,
        "session": WAHA_SESSION
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": WAHA_API_KEY
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201 or response.status_code == 200:
            logger.info(f"[WhatsApp] Successfully sent message to {chat_id}")
            return True
        else:
            logger.error(f"[WhatsApp] Failed to send message to {chat_id}: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.exception(f"[WhatsApp] Exception while sending message to {chat_id}: {e}")
        return False

def classify_message_case(payload, me_info):
    """
    Classify the message into the 3 specific cases:
    - Type 01: From me to me
    - Type 02: From me to other
    - Type 03: From other to me
    Works robustly even when body is absent/not considered.
    """
    from_me = payload.get("fromMe", False)
    info = payload.get("_data", {}).get("Info", {})
    recipient_alt = info.get("RecipientAlt", "")
    my_jids = [me_info.get("id"), me_info.get("jid"), me_info.get("lid")]
    
    if from_me:
        # Check if recipient is self (me to me vs me to other)
        is_self = (
            recipient_alt in my_jids or 
            info.get("Chat") == info.get("Sender") or
            payload.get("to") in my_jids
        )
        if is_self:
            return "TYPE_01"
        else:
            return "TYPE_02"
    else:
        return "TYPE_03"


@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive incoming webhook events from WAHA."""
    print("\n")
    data = request.json
    if not data:
        return jsonify({"status": "ignored", "reason": "empty body"}), 400

    logger.debug(f"[WhatsApp Webhook] Received event: {json.dumps(data)[:300]}")

    event = data.get("event")
    
    # GOWS / WAHA compatibility: check both payload dict and root data dict
    payload = data.get("payload")
    if not isinstance(payload, dict) or not payload:
        payload = data  # Fallback for GOWS flat structure

    if event in ("message", "message.any", "message.upsert"):
        from_me = payload.get("fromMe", False)
        sender = payload.get("from", "") or payload.get("author", "")
        recipient = payload.get("to", "") or payload.get("chatId", "") or payload.get("from", "")
        body = payload.get("body", "") or payload.get("text", "")
        message_id = payload.get("id") or data.get("id")

        me = data.get("me") or {}
        detected_case = classify_message_case(payload, me)
        
        print(f"[WhatsApp Event] event: {event} | Case: {detected_case} | from_me: {from_me} | from: {sender} | to: {recipient} | body: {body[:50]}")

        if message_id:
            if message_id in SEEN_MESSAGE_IDS:
                return jsonify({"status": "ignored", "reason": "duplicate event"}), 200
            SEEN_MESSAGE_IDS.append(message_id)

        # Skip the bot's own replies echoed back as fromMe events (prevents infinite loop)
        if body in BOT_SENT_TEXTS:
            BOT_SENT_TEXTS.remove(body)
            return jsonify({"status": "ignored", "reason": "bot's own echo message"}), 200

        # Determine chat_id and account identifiers
        my_id = me.get("id", "")
        my_lid = me.get("lid", "")
        WHATSAPP_PHONE_NUMBER = os.getenv("WHATSAPP_PHONE_NUMBER", "917058033447")

        # Handle filtering based on detected cases
        if detected_case == "TYPE_01":
            logger.info(f"[WhatsApp Self-Chat] Processing TYPE 01 (From me to me) | Body: {body}")
        elif detected_case == "TYPE_02":
            logger.debug(f"[WhatsApp Ignored] TYPE 02 (From me to other) blocked | Recipient: {recipient}")
            return jsonify({"status": "ignored", "reason": "outgoing message to another user blocked"}), 200
        else:
            logger.debug(f"[WhatsApp Ignored] TYPE 03 (From other to me) blocked | Sender: {sender}")
            # logger.warning(f"[WhatsApp Security] TYPE 03 (From other to me) blocked | Sender: {sender}")
            # print(f"[WhatsApp SECURITY ALERT] Blocked incoming message from external sender: {sender}")
            return jsonify({"status": "ignored", "reason": "messages from other senders blocked"}), 200

        chat_id = recipient
        if not chat_id or chat_id == my_id or chat_id == my_lid or "@s.whatsapp.net" in sender or "@c.us" in sender:
            chat_id = sender or recipient

        if not body:
            return jsonify({"status": "ignored", "reason": "empty message body"}), 200

        # Ignore RPI system alerts to prevent feedback loops / echo processing by LLM
        if "[RPI_SYS_ALERT]" in body or "RPI Reminder Alert for General SSB" in body:
            print(f"[WhatsApp Ignored] Dropped system reminder alert echo: {body[:60]}...")
            return jsonify({"status": "ignored", "reason": "system reminder alert echo"}), 200

        # Default model / settings
        model_name = "gemini-3.6-flash"
        
        try:
            # Invoke the CLI pipeline (`UI.cli`) as requested by General SSB
            logger.info(f"[WhatsApp CLI Routing] Processing message via UI.cli: {body}")
            print(f"[CLI-INTEGRATION] Dispatching message to cli.py | Case: {detected_case} | Body: {body}")
            ai_response = CLI.ProcessCLIInput(userInput=body)
            
            if not ai_response:
                ai_response = "I processed your request, but received no response text."
            else:
                ai_response = str(ai_response)

            print(f"[WhatsApp Outbound] To {chat_id}: {ai_response[:100]}...")
            
            # Send response back to WhatsApp
            send_whatsapp_message(chat_id, ai_response)
            
        except Exception as e:
            err_msg = f"Error processing your request in Personal Assistant: {str(e)}"
            logger.exception(f"[WhatsApp] Error processing message: {e}")
            send_whatsapp_message(chat_id, err_msg)

    return jsonify({"status": "success"}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "waha-bridge"}), 200

if __name__ == "__main__":
    port = int(os.getenv("WAHA_BRIDGE_PORT", 5002))
    print(f"Starting WAHA Bridge on port {port}...")
    print(f"WAHA Base URL: {WAHA_BASE_URL}")
    print(f"Webhook URL expected by WAHA: http://<your-host>:{port}/webhook")
    app.run(host="0.0.0.0", port=port, debug=False)
