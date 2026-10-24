"""
RPI Universal Reminder Daemon (Optimized Production Version)

Runs continuously on Windows, Linux, and macOS.
Imports and executes reminderDispatcher logic directly in-process 
(avoiding subprocess overhead) for maximum CPU and memory efficiency.
"""

import time
import sys
import os
from datetime import datetime

# Ensure project root is in sys.path for direct module import
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from Script.reminderDispatcher import dispatch_reminders

CHECK_INTERVAL_SECONDS = 60

# Configuration: Set to True to send to WhatsApp, False to print reminder sent and actual reminder name locally without sending actual reminder.
SEND_TO_WHATSAPP = False

def main():
    print("=" * 60)
    print(f"  RPI Universal In-Process Reminder Daemon Started")
    print(f"  Platform: {sys.platform}")
    print(f"  Interval: {CHECK_INTERVAL_SECONDS} seconds")
    print(f"  Mode: In-Process Execution (Zero Subprocess Overhead)")
    print(f"  WhatsApp Dispatch Enabled: {SEND_TO_WHATSAPP}")
    print(f"  Press Ctrl+C to stop.")
    print("=" * 60)

    try:
        while True:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Checking reminders...")
            try:
                dispatch_reminders(send_to_whatsapp=SEND_TO_WHATSAPP)
            except Exception as e:
                print(f"[ERROR] Dispatcher execution error: {e}", file=sys.stderr)
            
            time.sleep(CHECK_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\n[INFO] RPI Reminder Daemon stopped gracefully by master SSB.")
    except Exception as e:
        print(f"\n[FATAL] Daemon crashed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
