# IMPLEMENTATION PLAN: Reminder Alert Echo Prevention in WAHA Bridge

## Mission Objective
Prevent `reminderDispatcher.py` notifications from being treated as user input by `waha_bridge.py` and processed by the LLM agent.

---

## Step-by-Step Execution Plan

### Step 1: Modify `Script/reminderDispatcher.py`
- Add a unique system marker `[RPI_SYS_ALERT]` to the reminder message payload sent via WAHA.
- **Files to Modify:** `Script/reminderDispatcher.py`

### Step 2: Modify `UI/WhatsApp/waha_bridge.py`
- Add an inspection guard in the Flask webhook handler (`webhook()`).
- If `[RPI_SYS_ALERT]` or the reminder signature (`RPI Reminder Alert for General SSB`) is present in the message body, ignore/drop the message immediately before invoking `CLI.ProcessCLIInput`.
- **Files to Modify:** `UI/WhatsApp/waha_bridge.py`

### Step 3: Verification & Testing
- Restart `reminderDispatcher.py` and `waha_bridge.py`.
- Trigger a test reminder and verify that WAHA webhook successfully intercepts and ignores the system notification without triggering LLM responses.
