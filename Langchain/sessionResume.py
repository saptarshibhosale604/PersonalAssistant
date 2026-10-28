"""
Session Resume (JSON Format)

Parses session JSON logs written by Log/turn_logger.py back into
(userInput, agentOutput) turns, so /resume can seed them into agent memory.
"""

import json
from Log.log_utils import PrintFunctionName

MAX_RESUME_TURNS = 20  # keep only the most recent turns to bound prompt size
NO_OUTPUT_TEXT = "(No output or command handled)"


@PrintFunctionName
def ParseSessionLog(logFilePath: str, maxTurns: int = MAX_RESUME_TURNS) -> list:
    """Parse a session JSON log into a list of (userInput, agentOutput) tuples.

    Command-only turns and turns with no output are skipped.
    Tool usage is folded into the agent output as a short note if tools were invoked.
    """
    turns = []
    try:
        with open(logFilePath, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        
        session_turns = data.get("turns", [])
        for t in session_turns:
            userInput = t.get("user_input", "")
            agentOutput = t.get("agent_output", "")
            
            if not userInput or not agentOutput or agentOutput == NO_OUTPUT_TEXT:
                continue

            tool_calls = t.get("tool_calls", [])
            if tool_calls:
                tool_names = [tc.get("name", "unknown") for tc in tool_calls]
                agentOutput = f"[tools used: {', '.join(tool_names)}]\n{agentOutput}"

            turns.append((userInput, agentOutput))

    except Exception as e:
        print(f"[SessionResume] Error parsing JSON log {logFilePath}: {e}")

    if maxTurns and len(turns) > maxTurns:
        turns = turns[-maxTurns:]
    return turns
