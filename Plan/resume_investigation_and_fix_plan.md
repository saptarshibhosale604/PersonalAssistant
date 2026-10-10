# Plan: Investigation & Fix for `/resume` and Session Context Memory

## 📋 Project Context & Current Findings
1. **User Question & Goal:** When a user runs `/resume 0003`, the CLI loads and previews session log `session_0003_2026-10-09_21-10-06.log`, incrementing `THREAD_ID`. However, when the user subsequently asks `What was you first message?` (or similar memory-dependent queries), the assistant responds that it has no memory of prior sessions.
2. **Technical Root Cause:** 
   - LangGraph agents rely on checkpointers (e.g., `InMemorySaver`) where conversation state and chat history are indexed strictly by `thread_id` (e.g. `thread-3`).
   - When `/resume 0003` is executed in `UI/cli.py`, it only prints the log text to the terminal and increments `THREAD_ID`. It does **not** populate LangGraph's checkpointer state or reconstruct conversation turns into the agent's memory for the new `thread_id`. Consequently, the agent starts with a blank slate under the new thread.
   - Additionally, session logs (`Log/SessionLog/session_*.log`) store formatted plain-text dumps or turn outputs, but not raw LangChain message state dictionaries (`HumanMessage`, `AIMessage`, etc.) required to rebuild checkpoint states.

---

## 🎯 Implementation Plan (Investigation & Solution)

### Phase 1: Investigate Session Log Structure & Turn Data
1. Inspect how session logs are created and structured in `./Log/SessionLog/` and `Log/turn_logger.py`.
2. Determine whether session logs contain structured message histories or only rendered terminal outputs.

### Phase 2: Design Session State Reconstitution Mechanism
- User preference: 2. **Option B (LangGraph Checkpoint Hydration):**
1. **Option A (Prompt Injection / Context Injection):** When `/resume <id>` is called, read the session log content and inject a summary or conversation history into the system prompt or initial context payload for the new thread.
2. **Option B (LangGraph Checkpoint Hydration):** Parse past turns from the session log and initialize/update the LangGraph checkpointer state (`checkpointer.put(...)`) for the new `thread_id` so the agent natively recalls the conversation history as if it happened in this session.

### Phase 3: Detailed Step-by-Step Action Plan
1. **Step 1:** Modify session logging (`Log/turn_logger.py`) or session log parser to ensure complete turns (Human message + AI message + Tool messages) are easily extractable or serialized in JSON/structured format alongside plain text logs.
2. **Step 2:** Update `/resume` handler in `UI/cli.py` to parse the selected session log and hydrate the agent checkpointer or inject conversation history into the active thread config.
3. **Step 3:** Test the resumed session interaction to ensure queries like `What was your first message?` correctly retrieve responses based on the resumed session history.

---
*Status: Plan prepared and saved to `./Plan/resume_investigation_and_fix_plan.md` as requested.*
