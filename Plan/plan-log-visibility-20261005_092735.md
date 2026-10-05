# Plan: Log Visibility for User Input and Agent Output

## 📌 Context & Project Background
- **Project Name:** Personal Assistant (RPI / JARVIS)
- **Environment:** Raspberry Pi / Docker / CLI & Web App (`UI/cli.py`, `Langchain/agent.py`)
- **Current Issue:** 
  - Examining `Logs/logs.log` (or `Log/log.log`) shows internal metrics, tool calls (`tool_name`, `args`), and execution step counts (`agentCallingCountPerUserInput`), but it lacks clear, explicit logging of:
    1. **User Input** (what prompt the user actually typed or sent).
    2. **Agent Output** (what text response the assistant generated and returned to the user).
  - The assistant output line currently logs empty values like `2026-10-05 09:09:50,882 - INFO - [Info] assistantOutput:` without the actual content payload.

---

## 🎯 Objectives
Modify the logging mechanisms in `UI/cli.py` and `Langchain/agent.py` so that:
1. Every user input is explicitly logged to the log file with a clear tag (e.g., `[UserInput]`).
2. Every final assistant response / generated text is explicitly logged to the log file with a clear tag (e.g., `[AgentOutput]`).

---

## 🛠️ Implementation Plan

### 1. Update `UI/cli.py`
- In `Main()`, right after capturing `userInput`, add an INFO/DEBUG log entry:
  ```python
  logger.info(f"[UserInput] {userInput}")
  ```
- In `Output(assistantOutput)`, ensure the output content is properly logged:
  ```python
  logger.info(f"[AgentOutput] {assistantOutput}")
  ```

### 2. Update `Langchain/agent.py`
- In `StreamAndAccumulate`, `StreamAndAccumulateResume`, and `StreamResumeAndAccumulate`, capture the accumulated `response` string before returning and log it:
  ```python
  logger.info(f"[AgentOutput] {response}")
  ```

---

## 🧪 Verification & Testing
1. Run a test interaction via the CLI or test script.
2. Inspect `Log/log.log` / `Logs/logs.log` to verify that `[UserInput]` and `[AgentOutput]` entries appear clearly alongside tool calls and execution metadata.
