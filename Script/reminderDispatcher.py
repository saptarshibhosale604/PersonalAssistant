"""
Reminder Dispatcher Daemon

Reads reminder.json every minute, checks for pending reminders matching the current time,
and dispatches WhatsApp notifications via WAHA HTTP API.
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

REMINDER_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reminder.json")

WAHA_API_URL = os.getenv("WAHA_API_URL", "http://localhost:3000")
WAHA_API_KEY = os.getenv("WAHA_API_KEY", "")
WAHA_SESSION = os.getenv("WAHA_SESSION", "default")

def dispatch_reminders() -> None:
    if not os.path.exists(REMINDER_FILE):
        return

    try:
        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Dispatcher failed to read reminder.json: {e}")
        return

    reminders = data.get("reminders", [])
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    updated = False

    for r in reminders:
        if r.get("status") == "pending":
            remind_at = r.get("remind_at", "")
            # Compare up to minute precision: YYYY-MM-DD HH:MM
            if remind_at.startswith(now_str):
                task = r.get("task", "Reminder")
                chat_id = r.get("chat_id", "default")
                
                # Send via WAHA API
                success = send_whatsapp_notification(task, chat_id)
                if success:
                    r["status"] = "sent"
                    updated = True
                    print(f"[SUCCESS] Dispatched reminder: '{task}' to {chat_id}")
                else:
                    print(f"[ERROR] Failed to dispatch reminder: '{task}'")

    if updated:
        temp_file = REMINDER_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_file, REMINDER_FILE)

def send_whatsapp_notification(task: str, chat_id: str) -> bool:
    url = f"{WAHA_API_URL.rstrip('/')}/api/sendText"
    payload = {
        "session": WAHA_SESSION,
        "chatId": chat_id,
        "text": f"⏰ *RPI Reminder Alert for SSB!*\n\n{task}"
    }
    headers = {
        "Authorization": f"Bearer {WAHA_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in [200, 201]:
            return True
        else:
            print(f"[WAHA ERROR] Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"[WAHA EXCEPTION] {str(e)}")
        return False

if __name__ == "__main__":
    dispatch_reminders()
