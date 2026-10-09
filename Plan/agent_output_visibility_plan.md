# Plan: Agent Output Visibility and Turn Logging Alignment

## 📌 Objective
Ensure that agent output (`AgentOutput`) is correctly captured, accumulated, and displayed in both the console and turn logs (`Log/log.log`), particularly across different execution flows (e.g. streaming mode vs non-streaming, tool invocation / resumption loops).

---

## 🔍 Root Cause Analysis
1. **Empty Agent Output in Turn Logs:** 
   - During certain agent turns (such as turns involving tool calls, interrupts, or multi-step prompt executions), the `response` variable accumulated in streaming functions like `StreamAndAccumulate`, `StreamAndAccumulateResume`, or `StreamResumeAndAccumulate` may return empty or get reset between loop iterations.
   - When `Processing(userInput)` returns `None` or an empty string, `Output()` or `set_agent_output()` does not receive the full final assistant response text, leading to `AgentOutput    : ` appearing empty in `Log/log.log`.

2. **Flow Discrepancies:**
   - In `Langchain/agent.py`, different LLM modes (`local-4b`, `global*`) handle agent response accumulation differently. When resuming from tool interrupts via `Command(resume=...)`, stream chunks might only output tool messages or internal state changes without updating the final accumulated string returned by `Main()`.

---

## 📝 Proposed Solution Plan

1. **Improve Response Accumulation in Agent Streaming Functions:**
   - Ensure `StreamAndAccumulate`, `StreamAndAccumulateResume`, and `StreamResumeAndAccumulate` robustly accumulate all text chunks (`messageChunk.text`) across standard output and resume operations.
   - If streaming chunks do not yield text (e.g. during pure tool execution or state resume events), ensure the final message content from agent state or the last message is captured and returned as `agentResponse`.

2. **Enhance Turn Logging Robustness (`Log/turn_logger.py` & `UI/cli.py`):**
   - In `UI/cli.py` (`Main`), ensure `set_agent_output()` is called with the actual non-empty assistant output. If `assistantOutput` is empty or `None` but a response was generated during agent execution, capture it.
   - Add a fallback mechanism in `turn_logger.py` or `agent.py` to ensure `[AgentOutput]` is never logged empty when a valid response was streamed or generated.

3. **Testing & Verification:**
   - Run pytest suite (`pytest`) to ensure existing unit tests pass.
   - Perform end-to-end log inspections to verify that `AgentOutput` correctly displays assistant responses.
