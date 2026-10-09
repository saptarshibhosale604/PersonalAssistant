# Plan: Enhanced Structured Logging for Personal Assistant

## Current State Analysis

### What's Already Working
- `USER_INPUT_COUNT` tracked in `cli.py` (global variable)
- UserInput logged via `logger.info(f"[UserInput] {userInput}")` in `cli.py:Main()`
- AgentOutput logged via `logger.info(f"[AgentOutput] {response}")` in `cli.py:Output()` and `agent.py`
- Token metrics extracted in `agent.py:PrintPostProcessingLLMVariables()` but only printed to console
- Tool calls detected in `agent.py:ExtractStreamContent()` for "updates" stream mode
- Tool messages captured in "messages" stream mode

### What's Missing
1. Structured log format with consistent fields
2. Token metrics not written to log file (only console)
3. Tool calls not logged to file
4. Tool messages not logged to file
5. No correlation between user input, tool calls, and agent output

---

## Proposed Solution: Structured JSON Logging with Correlation IDs

### 1. Create a Structured Logger Module (`Log/structured_logger.py`)

```python
# New module for structured logging with correlation IDs
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextvars import ContextVar

# Context variable to track current request correlation ID
correlation_id_var: ContextVar[Optional[str]] = ContextVar('correlation_id', default=None)
user_input_count_var: ContextVar[int] = ContextVar('user_input_count', default=0)

class StructuredLogger:
    """Structured JSON logger with correlation ID support."""
    
    def __init__(self, name: str = "personal_assistant"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
    def _log_structured(self, level: int, event_type: str, data: Dict[str, Any]) -> None:
        """Log a structured JSON entry with correlation ID and user input count."""
        correlation_id = correlation_id_var.get()
        user_input_count = user_input_count_var.get()
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": logging.getLevelName(level),
            "event_type": event_type,
            "correlation_id": correlation_id,
            "user_input_count": user_input_count,
            **data
        }
        
        # Log as JSON string for structured parsing
        self.logger.log(level, json.dumps(log_entry, ensure_ascii=False))
    
    def log_user_input(self, user_input: str, correlation_id: str) -> None:
        correlation_id_var.set(correlation_id)
        user_input_count_var.set(user_input_count_var.get() + 1)
        self._log_structured(logging.INFO, "UserInput", {
            "user_input": user_input,
            "user_input_count": user_input_count_var.get()
        })
    
    def log_agent_output(self, agent_output: str, correlation_id: str) -> None:
        correlation_id_var.set(correlation_id)
        self._log_structured(logging.INFO, "AgentOutput", {
            "agent_output": agent_output
        })
    
    def log_tool_call(self, tool_name: str, tool_args: Dict, correlation_id: str, 
                      interrupt_index: int = 0, total_interrupts: int = 0) -> None:
        correlation_id_var.set(correlation_id)
        self._log_structured(logging.INFO, "ToolCall", {
            "tool_name": tool_name,
            "tool_args": tool_args,
            "interrupt_index": interrupt_index,
            "total_interrupts": total_interrupts
        })
    
    def log_tool_message(self, tool_name: str, tool_result: str, correlation_id: str) -> None:
        correlation_id_var.set(correlation_id)
        self._log_structured(logging.INFO, "ToolMessage", {
            "tool_name": tool_name,
            "tool_result": tool_result
        })
    
    def log_token_metrics(self, input_tokens: int, output_tokens: int, total_tokens: int,
                          tokens_per_second: float, total_duration_seconds: float,
                          correlation_id: str, model_name: str = "") -> None:
        correlation_id_var.set(correlation_id)
        self._log_structured(logging.INFO, "TokenMetrics", {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "tokens_per_second": round(tokens_per_second, 2),
            "total_duration_seconds": round(total_duration_seconds, 2),
            "model_name": model_name
        })
```

### 2. Update `custom_logger.py` to Support Both Formats

- Keep existing human-readable format for console output
- Add JSON file handler for structured logs
- Maintain backward compatibility with existing log files

### 3. Integrate with `cli.py`

```python
# In cli.py - Main() function
from Log.structured_logger import structured_logger, correlation_id_var, user_input_count_var
import uuid

@PrintFunctionName
def Main() -> None:
    global USER_INPUT_COUNT
    USER_INPUT_COUNT += 1
    
    # Generate correlation ID for this interaction
    correlation_id = f"req-{USER_INPUT_COUNT:06d}-{uuid.uuid4().hex[:8]}"
    correlation_id_var.set(correlation_id)
    user_input_count_var.set(USER_INPUT_COUNT)
    
    logger.debug(f"[Debug] UserInputCount: {USER_INPUT_COUNT}")
    
    userInput = Input()
    if userInput and len(userInput.strip()) > 0:
        # Log structured user input
        structured_logger.log_user_input(userInput, correlation_id)
        
        assistantOutput = Processing(userInput)
        if assistantOutput is not None:
            Output(assistantOutput)
            # Log structured agent output
            structured_logger.log_agent_output(str(assistantOutput), correlation_id)
```

### 4. Integrate with `agent.py`

#### In `ExtractStreamContent()` - Tool Calls:
```python
elif streamMode == "updates":
    # ... existing code ...
    for actionRequest in firstInterrupt.value["action_requests"]:
        toolName = actionRequest["name"]
        args = actionRequest.get("args", actionRequest.get("arguments", {}))
        
        # NEW: Log structured tool call
        structured_logger.log_tool_call(
            tool_name=toolName,
            tool_args=args,
            correlation_id=correlation_id_var.get() or "unknown",
            interrupt_index=REQUESTED_TOOLS_NUMBER_PER_USER_INPUT,
            total_interrupts=REQUESTED_TOOLS_NUMBER_PER_AGENT_INTERRUPT
        )
        # ... existing code ...
```

#### In `ExtractStreamContent()` - Tool Messages:
```python
if streamMode == "messages":
    # ... existing code ...
    if messageType == "tool":
        FormatMessageTypes("ToolMessage")
        print(f"{messageChunk.text}", end="", flush=True)
        print()
        FormatMessageTypes("")
        print()
        
        # NEW: Log structured tool message
        structured_logger.log_tool_message(
            tool_name=getattr(messageChunk, "name", "unknown_tool"),
            tool_result=messageChunk.text,
            correlation_id=correlation_id_var.get() or "unknown"
        )
```

#### In `PrintPostProcessingLLMVariables()` - Token Metrics:
```python
# After extracting metrics, log them structured
structured_logger.log_token_metrics(
    input_tokens=usageMetadata.get('input_tokens', 0),
    output_tokens=usageMetadata.get('output_tokens', 0),
    total_tokens=usageMetadata.get('total_tokens', 0),
    tokens_per_second=tokensPerSecond,
    total_duration_seconds=responseMetadata.get('total_duration', 0) / 1_000_000_000,
    correlation_id=correlation_id_var.get() or "unknown",
    model_name=responseMetadata.get('model_name', '')
)
```

### 5. Log File Structure

#### Human-readable log (existing `latest.log`):
```
2026-10-09 10:36:16,268 - INFO - Welcome to Personal Assistant CLI
2026-10-09 10:36:27,644 - INFO - [UserInput] You are using POWERSHELL CMD. JUST PLAN...
2026-10-09 10:36:30,123 - INFO - [AgentOutput] I understand. Here's my plan...
```

#### Structured JSON log (new `structured_latest.log`):
```json
{"timestamp": "2026-10-09T10:36:27.644Z", "level": "INFO", "event_type": "UserInput", "correlation_id": "req-000001-a1b2c3d4", "user_input_count": 1, "user_input": "You are using POWERSHELL CMD. JUST PLAN..."}
{"timestamp": "2026-10-09T10:36:28.100Z", "level": "INFO", "event_type": "ToolCall", "correlation_id": "req-000001-a1b2c3d4", "user_input_count": 1, "tool_name": "toolShell", "tool_args": {"command": "ls -la"}, "interrupt_index": 1, "total_interrupts": 1}
{"timestamp": "2026-10-09T10:36:28.500Z", "level": "INFO", "event_type": "ToolMessage", "correlation_id": "req-000001-a1b2c3d4", "user_input_count": 1, "tool_name": "toolShell", "tool_result": "total 64\ndrwxr-xr-x 2 user user 4096 Oct 9 10:36 .\n..."}
{"timestamp": "2026-10-09T10:36:30.123Z", "level": "INFO", "event_type": "AgentOutput", "correlation_id": "req-000001-a1b2c3d4", "user_input_count": 1, "agent_output": "I understand. Here's my plan..."}
{"timestamp": "2026-10-09T10:36:30.125Z", "level": "INFO", "event_type": "TokenMetrics", "correlation_id": "req-000001-a1b2c3d4", "user_input_count": 1, "input_tokens": 15638, "output_tokens": 252, "total_tokens": 15890, "tokens_per_second": 45.23, "total_duration_seconds": 2.34, "model_name": "gemini-3.6-flash"}
```

### 6. Web App Integration (`UI/WebApp/app.py`)

Apply same correlation ID pattern to web endpoints:
```python
@app.route('/streamUserInputMessage', methods=['GET'])
def stream_user_input_message():
    correlation_id = f"web-{int(time.time()*1000)}-{uuid.uuid4().hex[:8]}"
    correlation_id_var.set(correlation_id)
    # ... rest of function
```

---

## Additional Suggestions

| Area | Suggestion | Priority |
|------|------------|----------|
| **Log Rotation** | Add `RotatingFileHandler` with max 10MB, 5 backups | High |
| **Log Querying** | Add CLI tool to query structured logs by correlation_id, user_input_count, event_type | Medium |
| **Metrics Dashboard** | Export token metrics to Prometheus/Grafana for monitoring | Low |
| **Privacy** | Add PII redaction for user_input/tool_args in production | High |
| **Performance** | Use async logging (queue + background thread) to avoid blocking | Medium |
| **Testing** | Add unit tests for structured logger with various event types | High |
| **Documentation** | Document log schema for downstream consumers | Medium |

---

## Implementation Order

1. **Phase 1**: Create `structured_logger.py` with JSON file handler
2. **Phase 2**: Update `custom_logger.py` to initialize both loggers
3. **Phase 3**: Integrate correlation ID tracking in `cli.py:Main()`
4. **Phase 4**: Add structured logging calls in `agent.py` (tool calls, tool messages, token metrics)
5. **Phase 5**: Add structured logging to `UI/WebApp/app.py`
6. **Phase 6**: Add log rotation and retention policies
7. **Phase 7**: Create log analysis utility script

---

## Example Final Log Output

### Structured log entry for a complete interaction:
```json
{
  "timestamp": "2026-10-09T10:36:30.125Z",
  "level": "INFO",
  "event_type": "TokenMetrics",
  "correlation_id": "req-000001-a1b2c3d4",
  "user_input_count": 1,
  "input_tokens": 15638,
  "output_tokens": 252,
  "total_tokens": 15890,
  "tokens_per_second": 45.23,
  "total_duration_seconds": 2.34,
  "model_name": "gemini-3.6-flash"
}
```

This matches exactly what was requested:
- ✅ UserInputCount: 1
- ✅ UserInput (in separate UserInput event)
- ✅ AgentOutput (in separate AgentOutput event)  
- ✅ Tool Calls (in ToolCall events)
- ✅ ToolMessage (in ToolMessage events)
- ✅ Input Tokens: 15638
- ✅ Output Tokens: 252
- ✅ Total Tokens: 15890
- ✅ Tokens/Second: 45.23
- ✅ Total Duration: 2.34s