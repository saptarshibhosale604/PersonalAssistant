"""
Turn Logger Module

Provides structured per-turn logging with token statistics, tool calls,
and agent output. Produces a human-readable text block and optional JSON sidecar.
"""

import time
import json
import logging
import threading
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

from Log.custom_logger import logger

# Module-level state for the current turn (single-threaded CLI)
_current_turn: Optional['TurnRecord'] = None
_turn_lock = threading.Lock()

# Configuration
ENABLE_JSON_SIDECAR = False  # Can be toggled via config later
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
        # Store full result, truncation happens at format time
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


def _format_token_value(value: Optional[int]) -> str:
    """Format token value, showing 'n/a' for missing data."""
    return str(value) if value is not None else "n/a"


def _format_duration(value: Optional[float]) -> str:
    """Format duration in seconds with 2 decimal places."""
    if value is None or value <= 0:
        return "0.00s"
    return f"{value:.2f}s"


def _format_tokens_per_second(output_tokens: Optional[int], duration_s: Optional[float]) -> str:
    """Calculate and format tokens per second."""
    if output_tokens is None or duration_s is None or duration_s <= 0:
        return "0.00"
    return f"{output_tokens / duration_s:.2f}"


def format_turn(record: TurnRecord) -> str:
    """
    Format a TurnRecord into the human-readable text block.
    
    This is a pure function for easy unit testing.
    """
    lines = []
    separator = "=" * 60
    sub_separator = "-" * 60
    
    lines.append(f"\n")
    lines.append(separator)
    lines.append(f"UserInputCount : {record.count}")
    lines.append(f"UserInput      : {record.user_input}")
    lines.append(sub_separator)
    
    # Tool Calls
    if record.tool_calls:
        for tc in record.tool_calls:
            args_str = json.dumps(tc['args'], ensure_ascii=False)
            lines.append(f"Tool Calls     : {tc['name']}({args_str})")
    else:
        lines.append("Tool Calls     : none")
    
    # Tool Messages
    if record.tool_messages:
        for tm in record.tool_messages:
            result = _truncate(tm['result'])
            lines.append(f"ToolMessage    : {tm['name']} -> {result}")
    else:
        lines.append("ToolMessage    : none")
    
    lines.append(sub_separator)
    lines.append(f"AgentOutput    : {record.agent_output}")
    lines.append(sub_separator)
    
    # Token metrics
    lines.append(f"Model Name         : {record.model_name or 'n/a'}")
    lines.append(f"Input Tokens       : {_format_token_value(record.input_tokens)}")
    lines.append(f"Output Tokens      : {_format_token_value(record.output_tokens)}")
    lines.append(f"Total Tokens       : {_format_token_value(record.total_tokens)}")
    lines.append(f"Tokens / Second    : {_format_tokens_per_second(record.output_tokens, record.duration_s)}")
    lines.append(f"Total Duration     : {_format_duration(record.duration_s)}")
    
    if record.error:
        lines.append(sub_separator)
        lines.append(f"Error            : {record.error}")
    
    lines.append(separator)
    
    return "\n".join(lines)


def _get_json_logger() -> logging.Logger:
    """Get or create a separate logger for JSON sidecar output."""
    json_logger = logging.getLogger('turn_logger_json')
    json_logger.setLevel(logging.INFO)
    json_logger.propagate = False  # Don't propagate to root logger
    
    if not json_logger.handlers:
        from Log.custom_logger import log_dir
        json_path = os.path.join(log_dir, "structured_latest.log")
        handler = logging.FileHandler(json_path, encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(message)s'))  # Raw JSON lines
        json_logger.addHandler(handler)
    
    return json_logger


def begin_turn(count: int, user_input: str) -> TurnRecord:
    """
    Start a new turn record.
    
    Args:
        count: The user input count (1-based)
        user_input: The raw user input text
        
    Returns:
        The created TurnRecord
    """
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


def end_turn() -> Optional[str]:
    """
    Finalize the current turn, write the log block, and clear the record.
    
    Returns:
        The formatted text block that was logged, or None if no active turn.
    """
    global _current_turn
    
    with _turn_lock:
        turn = _current_turn
        if not turn:
            return None
        
        # Calculate duration from timer if not set by usage
        if turn.duration_s is None:
            turn.duration_s = time.perf_counter() - turn.started_at
        
        # Format the turn
        formatted = format_turn(turn)
        
        # Write to main logger as a single multi-line message
        try:
            logger.info(formatted)
        except Exception as e:
            # Logging errors must never break the agent
            print(f"[TurnLogger] Failed to write log: {e}")
        
        # Write JSON sidecar if enabled
        if ENABLE_JSON_SIDECAR:
            try:
                _write_json_sidecar(turn)
            except Exception as e:
                print(f"[TurnLogger] Failed to write JSON sidecar: {e}")
        
        # Clear the current turn
        _current_turn = None
        
        return formatted


def _write_json_sidecar(record: TurnRecord) -> None:
    """Write the turn record as a JSON line to the sidecar file."""
    json_logger = _get_json_logger()
    
    # Build JSON-serializable dict
    data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_input_count": record.count,
        "user_input": record.user_input,
        "tool_calls": record.tool_calls,
        "tool_messages": record.tool_messages,
        "agent_output": record.agent_output,
        "input_tokens": record.input_tokens,
        "output_tokens": record.output_tokens,
        "total_tokens": record.total_tokens,
        "tokens_per_second": _format_tokens_per_second(record.output_tokens, record.duration_s),
        "duration_seconds": record.duration_s,
        "model_name": record.model_name,
        "error": record.error,
    }
    
    json_logger.info(json.dumps(data, ensure_ascii=False))


def set_json_sidecar_enabled(enabled: bool) -> None:
    """Enable or disable JSON sidecar output."""
    global ENABLE_JSON_SIDECAR
    ENABLE_JSON_SIDECAR = enabled


# Import os for _get_json_logger
import os