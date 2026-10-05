# Plan: Add a Visual Text Barrier Between Tool Output and Agent Output

## 🎯 Goal
Ensure that there are exactly **2 newlines (`\n\n`)** (or a clean visual text barrier / separator) between a tool's output and the subsequent agent output, preventing cases where text runs together (e.g., `...venvThis is a...`).

---

## 🔍 Root Cause Analysis
- **Where it happens:** In `Langchain/agent.py` inside `ExtractStreamContent(...)` when `streamMode == "messages"` and `messageType == "tool"`.
- **Current Code:**
  ```python
  if messageType == "tool":
      FormatMessageTypes("ToolMessage")
      print(f"{messageChunk.text}", end="", flush=True)
      print()
      FormatMessageTypes("")
      print()
  ```
- Although it prints a trailing `print()`, depending on how the tool output stream chunks arrive, or how `FormatMessageTypes("")` prints its banner (`===  ===`), the spacing might be insufficient or stripped, causing the subsequent text (like `AIMessage` banner or streamed content) to immediately follow without adequate separation.

---

## 📝 Proposed Implementation Steps

### Step 1: Update Tool Output Spacing in `Langchain/agent.py`
Modify `ExtractStreamContent` under the `tool` message type to guarantee proper spacing:
- Add extra explicit newlines (`\n\n`) immediately after the tool output block.
- Ensure `FormatMessageTypes` cleanly wraps the section with proper padding and terminal spacing.

**Proposed Code Change in `Langchain/agent.py`:**
```python
        if messageType == "tool":
            FormatMessageTypes("ToolMessage")
            print(f"{messageChunk.text}", end="", flush=True)
            print("\n\n")  # Ensure a distinct 2-newline barrier
            FormatMessageTypes("")
            print("\n")   # Additional spacing before next output segment
```

### Step 2: Verify and Test
- Run a tool-invoking prompt in the CLI (e.g., `toolReadFile` or `toolExecuteBash`).
- Verify visually that the tool output is cleanly separated from the subsequent `AIMessage` banner and LLM response text by a clear visual barrier/double newline.
