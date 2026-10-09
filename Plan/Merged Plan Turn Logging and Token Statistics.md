# Implementation Plan: Turn Logging and Token Statistics

## Overview
This document outlines the plan for implementing a robust, structured turn-logging system (`Log/turn_logger.py`) and integrating it across the CLI (`UI/cli.py`), Web App (`UI/WebApp/app.py`), and Agent execution (`Langchain/agent.py`).

---

## Objectives
1. **Structured Per-Turn Logging:** Consolidate each interaction turn (User Input -> Tool Calls -> Tool Messages -> Agent Output -> LLM Metrics & Token Usage) into a clean, human-readable log format.
2. **Robust Fallbacks:** Handle missing token statistics gracefully (displaying `n/a` instead of crashing or outputting `None`).
3. **Multi-Interface Integration:** Wire turn logging seamlessly into both the CLI interactive loop and the Flask Web App streaming endpoints.
4. **Testability:** Provide comprehensive unit and integration tests (`test_turn_logger.py`).

---

## Architecture & Components

### 1. Turn Logger Module (`Log/turn_logger.py`)
- **`TurnRecord` Dataclass:** Stores state for the active turn (count, user_input, started_at, tool_calls, tool_messages, agent_output, token stats, duration, model_name, error).
- **Thread-safe state management:** Uses thread locks and module-level functions (`begin_turn`, `end_turn`, `add_tool_call`, `add_tool_message`, `add_usage`, `set_agent_output`) so multi-threaded web requests or single-threaded CLI sessions function correctly.
- **`format_turn(record: TurnRecord)`:** Pure formatting function generating the exact required text block format:
  ```text
  ============================================================
  UserInputCount : 1
  UserInput      : ...
  ------------------------------------------------------------
  Tool Calls     : ...
  ToolMessage    : ...
  ------------------------------------------------------------
  AgentOutput    : ...
  ------------------------------------------------------------
  Model Name         : ...
  Input Tokens       : ...
  Output Tokens      : ...
  Total Tokens       : ...
  Tokens / Second    : ...
  Total Duration     : ...
  ============================================================
  ```
- **JSON Sidecar (Optional):** Supports optional structured JSON logging for auditing/analytics (`structured_latest.log`).

### 2. Agent Integration (`Langchain/agent.py`)
- Import turn logger helper functions (`add_tool_call`, `add_tool_message`, `add_usage`).
- Inside `PrintPostProcessingLLMVariables`:
  - Extract `input_tokens`, `output_tokens`, `total_tokens`, `model_name`, and execution duration.
  - Handle `None` values gracefully with `n/a`.
  - Invoke `add_usage(...)` to record metrics to the active turn record.
- Inside `ExtractStreamContent`:
  - When tool calls are intercepted in `"updates"` mode, record them via `add_tool_call(...)`.
  - When tool messages arrive in `"messages"` mode, record them via `add_tool_message(...)`.

### 3. CLI Integration (`UI/cli.py`)
- Wrap the main user input execution block inside `Main()` with `begin_turn()` / `end_turn()`:
  ```python
  turn = begin_turn(USER_INPUT_COUNT, userInput)
  try:
      assistantOutput = Processing(userInput)
      if assistantOutput is not None:
          Output(assistantOutput)
          set_agent_output(str(assistantOutput))
  except Exception as e:
      current_turn = get_current_turn()
      if current_turn:
          current_turn.set_error(f"{type(e).__name__}: {e}")
      raise
  finally:
      end_turn()
  ```

### 4. Web App Integration (`UI/WebApp/app.py`)
- Wrap the streaming generator in `/streamUserInputMessage` with `begin_turn()` / `end_turn()` using a thread-safe turn record.

---

## Testing & Verification
- Unit test suite (`test_turn_logger.py`) verifies:
  - Basic turn formatting and fallback for missing tokens (`n/a`).
  - Tool calls and tool messages formatting.
  - Metric accumulation across multi-step agent turns.
  - Integration with mock agent outputs.
