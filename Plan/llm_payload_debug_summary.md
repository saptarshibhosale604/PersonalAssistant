
# Session Summary: Inspecting LLM Message Payload in agent.py

## 1. Problem
The user wanted to inspect and print the exact, complete first message payload (including system prompts, tools, and message history) being sent to the LLM model inside `agent.py` under `StreamAndAccumulate` and global mode handling.

An `AttributeError: 'dict' object has no attribute 'content'` occurred because `messages` passed to `StreamAndAccumulate` contained dictionary objects (e.g. `[{"role": "user", "content": userInput}]`) rather than LangChain message objects (`HumanMessage`).

## 2. Context & Discovery
- **File**: `Langchain/agent.py`
- **Target Function**: `StreamAndAccumulate(messages: list, configMemory: dict) -> str`
- **Framework**: LangChain & LangGraph (`create_agent`, Compiled State Graphs, and checkpointers).
- **Global Variables**: `LLM`, `TOOLS`, and `AGENT` initialized via `BuildAgent()`.

## 3. Implementation / Changes
1. Injected a robust debug inspection block into `StreamAndAccumulate` right before `AGENT.stream(...)`:
   ```python
   print("--- DEBUG: EXACT LLM PAYLOAD --- ")
   for m in messages:
       if hasattr(m, "content"):
           print(f"[{type(m).__name__}]: {m.content}")
       elif isinstance(m, dict):
           print(f"[{m.get('role', 'dict')}]: {m.get('content', m)}")
       else:
           print(f"[{type(m).__name__}]: {str(m)}")
   print("---------------------------------")
   ```
2. Updated `Plan\llm_payload_debug_summary.md` to document the fix for the dictionary attribute error.

## 4. Next Steps
- Run the agent interactively to view the printed payload output.
- Verify whether system prompts and history are properly structured.

