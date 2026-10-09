# Plan: Log Formatting and Token Statistics Enhancement

## Objective
Update the logging mechanism and agent execution outputs to ensure every session log file (and console output) cleanly captures and records:
- `UserInputCount: <number>`
- `UserInput`
- `AgentOutput`
- `Tool Calls`
- `ToolMessage`
- Token metrics:
  - `Input Tokens       : 15638` (or dynamic token counts extracted from LLM execution metadata)
  - `Output Tokens      : 252`
  - `Total Tokens       : 15890`
  - `Tokens / Second    : 0.00`
  - `Total Duration     : 0.00s`
- Any other suggestions / recommendations for robustness and performance.

---

## Proposed Implementation Plan (FOR PLANNING ONLY - NOT IMPLEMENTED)

### 1. Locate and Examine Execution Flow & Logging (`UI/cli.py`, `Langchain/agent.py`, `Log/custom_logger.py`)
- Identify where user inputs are received and counted (`UserInputCount`).
- Identify where agent invocation responses, tool calls, tool messages, and usage metadata (token counts, duration) are returned from LangChain / LangGraph callbacks or model metadata.

### 2. Design Structured Log Formatter / Callback Handler
- Create a dedicated logging wrapper or LangChain callback handler (`Log/token_logger.py` or within `Log/custom_logger.py`) that captures:
  - Incrementing counter for each user input turn (`UserInputCount`).
  - Exact text of the user prompt (`UserInput`).
  - Final response text or structured output from the agent (`AgentOutput`).
  - Details of invoked tools (`Tool Calls`).
  - Results returned by tool executions (`ToolMessage`).
  - Usage metadata (`response_metadata` or LangChain token usage callbacks for Input Tokens, Output Tokens, Total Tokens, Tokens / Second, Total Duration).

### 3. Log Output Format Specification
For each conversation turn in the log file (`Log/session_*.log` / `latest.log`), format entries as follows:
```text
============================================================
UserInputCount : 1
UserInput      : <user input text>
------------------------------------------------------------
Tool Calls     : <list/details of tool calls>
ToolMessage    : <tool execution results>
------------------------------------------------------------
AgentOutput    : <agent response text>
------------------------------------------------------------
Input Tokens       : 15638
Output Tokens      : 252
Total Tokens       : 15890
Tokens / Second    : 0.00
Total Duration     : 0.00s
============================================================
```

### 4. Additional Suggestions for Improvement
1. **Dynamic Token Extraction:** Ensure fallback handling if model providers (like Ollama or specific LLM endpoints) do not return token usage metadata in standard `response_metadata` dictionaries.
2. **Asynchronous / Thread-Safe Logging:** Use thread-safe file writing if multiple client sessions (CLI and WebApp) write to log files concurrently.
3. **Structured JSON Logs (Optional):** Consider supporting a JSON log exporter alongside plain-text session logs for easier parsing and analytics.
