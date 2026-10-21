"""
WAHA (WhatsApp HTTP API) Bridge for Personal Assistant.

Runs a local Flask webhook listener on port 5002 to receive incoming WhatsApp messages from WAHA,
passes them through the Personal Assistant's core LangChain Agent (`Agent.Main`),
and sends the AI response back to the WhatsApp user via WAHA's outbound REST API.
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

@app.route("/webhook", methods=["POST"])
def webhook():
    """Receive incoming webhook events from WAHA."""
    print("\n")
    data = request.json
    if not data:
        return jsonify({"status": "ignored", "reason": "empty body"}), 400

    logger.debug(f"[WhatsApp Webhook] Received event: {json.dumps(data)[:300]}")

    event = data.get("event")
    payload = data.get("payload", {})

    if event in ("message", "message.any"):
        from_me = payload.get("fromMe", False)
        print(f"[WhatsApp Event] from_me: {from_me}")

        sender = payload.get("from", "")
        recipient = payload.get("to", "")
        body = payload.get("body", "")
        message_id = payload.get("id")

        if message_id:
            if message_id in SEEN_MESSAGE_IDS:
                return jsonify({"status": "ignored", "reason": "duplicate event"}), 200
            SEEN_MESSAGE_IDS.append(message_id)

        # Incoming messages from 3rd parties: Do not reply, only log if needed.
        if not from_me:
            logger.info(f"[WhatsApp External Incoming] From 3rd party {sender}: {body} (Ignored)")
            return jsonify({"status": "ignored", "reason": "external 3rd party message"}), 200

        # Own messages: reply into the chat they were sent to.
        chat_id = recipient

        if from_me:
            # Only "Message yourself" chat drives the bot; ignore what you type to other people
            me = data.get("me") or {}
            my_ids = {me.get("id"), me.get("lid")} - {None}
            if recipient not in my_ids:
                return jsonify({"status": "ignored", "reason": "own message to another chat"}), 200
            # Skip the bot's own replies echoed back as fromMe events (prevents infinite loop)
            if body in BOT_SENT_TEXTS:
                BOT_SENT_TEXTS.remove(body)
                return jsonify({"status": "ignored", "reason": "bot's own echo message"}), 200

        if not body:
            return jsonify({"status": "ignored", "reason": "empty message body"}), 200

        logger.info(f"[WhatsApp Incoming/Self] From Me: {from_me} | From {sender}: {body}")

        # Default model / settings (e.g. gemini-3.6-flash)
        model_name = "gemini-3.6-flash"
        
        try:
            # Extract clean phone number/sender ID from WAHA 'from' or 'participant' or contact info
            sender_raw = sender.split("@")[0] if "@" in sender else sender
            
            # Optional: filter for ALLOWED_SENDER if configured
            if ALLOWED_SENDER and ALLOWED_SENDER not in sender and ALLOWED_SENDER not in sender_raw:
                print(f"[WhatsApp Ignored] Message from {sender} (not allowed sender {ALLOWED_SENDER})")
                return jsonify({"status": "ignored", "reason": "unauthorized sender"}), 200

            # Invoke the CLI pipeline instead of calling Agent.Main directly
            logger.info(f"[WhatsApp CLI Routing] Processing message via UI.cli: {body}")
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
