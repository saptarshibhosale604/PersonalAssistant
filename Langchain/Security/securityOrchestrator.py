import os
import json
from datetime import datetime

STATE_FILE = "sessions/SecurityAudit/security_state.json"

def load_security_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "status": "INITIALIZED",
        "current_stage": 0,
        "completed_stages": [],
        "findings": [],
        "last_updated": str(datetime.now())
    }

def save_security_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    state["last_updated"] = str(datetime.now())
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

def run_stage(stage_name, stage_function):
    state = load_security_state()
    if stage_name in state["completed_stages"]:
        print(f"[SECURITY ORCHESTRATOR] Stage '{stage_name}' already completed. Skipping.")
        return True
    
    print(f"[SECURITY ORCHESTRATOR] Executing Stage: {stage_name}...")
    state["status"] = f"RUNNING_{stage_name}"
    save_security_state(state)
    
    try:
        findings = stage_function()
        if "findings" not in state:
            state["findings"] = []
        state["findings"].extend(findings)
        state["completed_stages"].append(stage_name)
        state["status"] = "IN_PROGRESS"
        save_security_state(state)
        print(f"[SECURITY ORCHESTRATOR] Stage '{stage_name}' completed successfully.")
        return True
    except Exception as e:
        print(f"[SECURITY ORCHESTRATOR ERROR] Stage '{stage_name}' failed: {e}")
        state["status"] = f"ERROR_{stage_name}"
        save_security_state(state)
        return False
