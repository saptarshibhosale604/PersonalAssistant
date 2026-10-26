"""
Tools Reminder Module

Provides LangChain tools for scheduling, listing, and managing reminders 
persisted in reminder.json and dispatched via WAHA WhatsApp API.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from langchain.tools import tool
from dotenv import load_dotenv

load_dotenv()

REMINDER_FILE = "./reminder.json"
WHATSAPP_PHONE_NUMBER = os.getenv("WHATSAPP_PHONE_NUMBER")

def _load_reminders() -> Dict[str, List[Dict[str, Any]]]:
    if not os.path.exists(REMINDER_FILE):
        return {"reminders": []}
    try:
        with open(REMINDER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"reminders": []}

def _save_reminders(data: Dict[str, List[Dict[str, Any]]]) -> None:
    temp_file = REMINDER_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(temp_file, REMINDER_FILE)

@tool
def schedule_reminder(
    task: str,
    remind_time: str,
    chat_id: Optional[str] = None
) -> str:
    """
    Schedule a reminder to be sent to SSB via WhatsApp at a specific time.
    
    Args:
        task: Description of the task or homework to remind SSB about (e.g. "do homework").
        remind_time: The time to remind, in ISO format (YYYY-MM-DD HH:MM:SS).
        chat_id: Optional WhatsApp chat ID or phone number. If omitted, uses default active session chat/number.
    """
    try:
        now = datetime.now()
        target_dt = None
        
        # Try parsing standard YYYY-MM-DD HH:MM:SS
        try:
            target_dt = datetime.strptime(remind_time, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass
            
        if not target_dt:
            try:
                target_dt = datetime.strptime(remind_time, "%Y-%m-%d %H:%M")
            except ValueError:
                pass
                
        # If still not parsed, handle expressions like "3:00 pm today" or "3:00 pm"
        if not target_dt:
            from dateutil import parser as date_parser
            try:
                parsed = date_parser.parse(remind_time, default=now)
                target_dt = parsed
            except Exception:
                pass

        if not target_dt:
            return f"[ERROR] Could not parse reminder time '{remind_time}'. Please provide time in format YYYY-MM-DD HH:MM:SS or clear natural time like '3:00 PM today'."

        reminder_id = f"rem_{int(now.timestamp())}"
        
        # Default to phone number from env if not specified
        target_chat_id = chat_id
        if not target_chat_id or target_chat_id == "default":
            if not WHATSAPP_PHONE_NUMBER:
                return "[ERROR] WHATSAPP_PHONE_NUMBER is not set in .env. Please provide a chat_id or configure WHATSAPP_PHONE_NUMBER in .env."
            target_chat_id = f"{WHATSAPP_PHONE_NUMBER}@c.us"
        elif "@" not in target_chat_id:
            target_chat_id = f"{target_chat_id}@c.us"

        new_reminder = {
            "id": reminder_id,
            "task": task,
            "remind_at": target_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "chat_id": target_chat_id
        }

        data = _load_reminders()
        data["reminders"].append(new_reminder)
        _save_reminders(data)

        return f"[SUCCESS] Reminder scheduled successfully!\n- ID: {reminder_id}\n- Task: {task}\n- Remind At: {target_dt.strftime('%Y-%m-%d %H:%M:%S')}"
    except Exception as e:
        return f"[ERROR] Failed to schedule reminder: {str(e)}"

@tool
def list_reminders() -> str:
    """
    List all pending and past reminders stored in reminder.json.
    """
    try:
        data = _load_reminders()
        reminders = data.get("reminders", [])
        if not reminders:
            return "No reminders found in reminder.json."
        
        output = "📋 *Your Reminders List:*\n"
        for r in reminders:
            output += f"- [{r['id']}] '{r['task']}' at {r['remind_at']} (Status: {r['status']})\n"
        return output
    except Exception as e:
        return f"[ERROR] Failed to list reminders: {str(e)}"

@tool
def delete_reminder(reminder_id: str) -> str:
    """
    Delete a specific reminder by its ID.
    
    Args:
        reminder_id: The unique ID of the reminder (e.g. rem_1740835200).
    """
    try:
        data = _load_reminders()
        reminders = data.get("reminders", [])
        filtered = [r for r in reminders if r["id"] != reminder_id]
        
        if len(filtered) == len(reminders):
            return f"[WARNING] Reminder with ID '{reminder_id}' not found."
            
        data["reminders"] = filtered
        _save_reminders(data)
        return f"[SUCCESS] Reminder '{reminder_id}' deleted successfully."
    except Exception as e:
        return f"[ERROR] Failed to delete reminder: {str(e)}"

# Tool categorization
toolsBasic = [schedule_reminder, list_reminders, delete_reminder]
toolsIntermediate = []
toolsAdvance = []

tools = toolsAdvance + toolsIntermediate + toolsBasic

def ToolsList() -> List[Any]:
    """
    Return the list of tools provided by this module.

    Returns:
        List[Any]: List of tool functions.
    """
    global tools
    return tools
