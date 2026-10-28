"""
Turn Logger Module (JSON Format)

Provides structured per-turn logging with token statistics, tool calls,
and agent output. Serializes the entire session into a clean JSON structure
at ./Log/SessionLog/session_[ID]_[TIMESTAMP].json
"""

import time
import json
import logging
import os
import threading
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from Log.custom_logger import logger, log_path

# Module-level state for the current turn and session turns list
_current_turn: Optional['TurnRecord'] = None
_session_turns: List[Dict[str, Any]] = []
_turn_lock = threading.Lock()

MAX_TOOL_RESULT_LENGTH = 2000  # Truncate long tool results in log


@dataclass
class TurnRecord:
    """Holds all data for a single user turn."""
    count: int
    user_input: str
    started_at: float
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    tool_messages: List[Dict[str, Any]] = field(default_factory=list)
    agent_output: str = ''
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    duration_s: Optional[float] = None
    model_name: str = ''
    error: Optional[str] = None

    def add_tool_call(self, name: str, args: Dict[str, Any]) -> None:
        """Add a tool call to the record."""
        self.tool_calls.append({"name": name, "args": args})

    def add_tool_message(self, name: str, result: Any) -> None:
        """Add a tool message/result to the record."""
        result_str = str(result)
        self.tool_messages.append({"name": name, "result": result_str})

    def add_usage(self, input_tokens: Optional[int], output_tokens: Optional[int],
                  total_tokens: Optional[int], duration_s: Optional[float],
                  model_name: str) -> None:
        """Accumulate token usage across multiple LLM calls in a turn."""
        if input_tokens is not None:
            self.input_tokens = (self.input_tokens or 0) + input_tokens
        if output_tokens is not None:
            self.output_tokens = (self.output_tokens or 0) + output_tokens
        if total_tokens is not None:
            self.total_tokens = (self.total_tokens or 0) + total_tokens
        elif input_tokens is not None and output_tokens is not None:
            self.total_tokens = (self.total_tokens or 0) + input_tokens + output_tokens
        
        if duration_s is not None:
            self.duration_s = (self.duration_s or 0.0) + duration_s
        
        if model_name and not self.model_name:
            self.model_name = model_name

    def set_agent_output(self, text: str) -> None:
        """Set the agent's final output text."""
        self.agent_output = text

    def set_error(self, error: str) -> None:
        """Mark the turn as having an error."""
        self.error = error


def _truncate(text: str, max_len: int = MAX_TOOL_RESULT_LENGTH) -> str:
    """Truncate text with a marker if it exceeds max_len."""
    if len(text) <= max_len:
        return text
    truncated = len(text) - max_len
    return text[:max_len] + f"\n[truncated {truncated} chars]"


def _format_tokens_per_second(output_tokens: Optional[int], duration_s: Optional[float]) -> float:
    """Calculate tokens per second."""
    if output_tokens is None or duration_s is None or duration_s <= 0:
        return 0.0
    return round(output_tokens / duration_s, 2)


def _flush_session_to_disk() -> None:
    """Write the complete session object to the JSON log file."""
    try:
        session_data = {
            "session_meta": {
                "log_file": os.path.basename(log_path),
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
            "turns": _session_turns
        }
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[TurnLogger] Failed to write session JSON log: {e}")


def begin_turn(count: int, user_input: str) -> TurnRecord:
    """Start a new turn record."""
    global _current_turn
    with _turn_lock:
        _current_turn = TurnRecord(
            count=count,
            user_input=user_input,
            started_at=time.perf_counter()
        )
    return _current_turn


def get_current_turn() -> Optional[TurnRecord]:
    """Get the currently active turn record, if any."""
    return _current_turn


def add_tool_call(name: str, args: Dict[str, Any]) -> None:
    """Add a tool call to the current turn."""
    turn = get_current_turn()
    if turn:
        turn.add_tool_call(name, args)


def add_tool_message(name: str, result: Any) -> None:
    """Add a tool message/result to the current turn."""
    turn = get_current_turn()
    if turn:
        turn.add_tool_message(name, result)


def add_usage(input_tokens: Optional[int], output_tokens: Optional[int],
              total_tokens: Optional[int], duration_s: Optional[float],
              model_name: str) -> None:
    """Add token usage metrics to the current turn."""
    turn = get_current_turn()
    if turn:
        turn.add_usage(input_tokens, output_tokens, total_tokens, duration_s, model_name)


def set_agent_output(text: str) -> None:
    """Set the agent output for the current turn."""
    turn = get_current_turn()
    if turn:
        turn.set_agent_output(text)


def end_turn() -> Optional[Dict[str, Any]]:
    """
    Finalize the current turn, append to session turns, flush JSON to disk, and clear.
    """
    global _current_turn
    
    with _turn_lock:
        turn = _current_turn
        if not turn:
            return None
        
        if turn.duration_s is None:
            turn.duration_s = time.perf_counter() - turn.started_at
        
        # Prepare truncated tool messages for JSON storage
        processed_tool_messages = [
            {"name": tm["name"], "result": _truncate(tm["result"])}
            for tm in turn.tool_messages
        ]
        
        turn_dict = {
            "turn_id": turn.count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_input": turn.user_input,
            "tool_calls": turn.tool_calls,
            "tool_messages": processed_tool_messages,
            "agent_output": turn.agent_output if turn.agent_output else "(No output or command handled)",
            "metrics": {
                "model_name": turn.model_name or "n/a",
                "input_tokens": turn.input_tokens,
                "output_tokens": turn.output_tokens,
                "total_tokens": turn.total_tokens,
                "tokens_per_second": _format_tokens_per_second(turn.output_tokens, turn.duration_s),
                "duration_seconds": round(turn.duration_s, 2) if turn.duration_s else 0.0,
            },
            "error": turn.error
        }
        
        _session_turns.append(turn_dict)
        _flush_session_to_disk()
        
        _current_turn = None
        return turn_dict


def set_json_sidecar_enabled(enabled: bool) -> None:
    """Legacy helper for backward compatibility."""
    pass
