# Implementation & Integration Plan: Adding Human-in-the-Loop Input Tool to `toolsCodingAgent.py`

This document outlines the complete plan for adding an **Ask Human Input** tool (`toolAskHumanInput`) into `toolsCodingAgent.py` (and categorizing it appropriately as an advanced/sensitive tool that requires confirmation or interactive prompting when needed).

---

## 📋 Objectives
1. **Create `AskHumanInput` Tool:** Implement a LangChain `@tool` function inside `Langchain/Tools/toolsCodingAgent.py` that pauses agent execution, prompts the user via standard input (`input()`), and returns the human's response to the agent.
2. **Categorize Correctly:** Place `AskHumanInput` into `toolsAdvance` (or `toolsIntermediate`), ensuring it integrates seamlessly with the existing `ToolsList()` export.
3. **Ensure Compatibility:** Maintain full compatibility with LangChain 1.x / `langchain_core.tools`, existing tool structures, and PowerShell/Docker execution environments.

---

## 🛠️ Proposed Changes

### 1. File to Modify: `Langchain/Tools/toolsCodingAgent.py`

Add the following tool definition:

```python
@tool("toolAskHumanInput", description="Prompt the human user for input, clarification, confirmation, or additional instructions during execution.")
def AskHumanInput(prompt_message: str) -> str:
    """Pauses agent execution and prompts the human user in the terminal/UI for input or decision making."""
    try:
        print(f"\n[AGENT REQUESTS INPUT]: {prompt_message}")
        user_response = input("Human Input Required > ").strip()
        return f"Human response: {user_response}"
    except Exception as e:
        return f"Error obtaining human input: {str(e)}"
```

### 2. Update Tool Lists in `toolsCodingAgent.py`

Update `toolsAdvance` to include `AskHumanInput`:

```python
# Category-based tool collections matching otherTools.py format
toolsAdvance = [ExecuteBash, AskHumanInput]  # Tools requiring human confirmation/sensitive operations / interactive prompt
toolsIntermediate = [ReadFile, WriteFile, EditFile]
toolsBasic = []

tools = toolsAdvance + toolsIntermediate + toolsBasic
```

---

## 🧪 Verification & Testing Plan
1. **Syntax Check:** Run a Python syntax check on `toolsCodingAgent.py`:
   ```powershell
   python -m py_compile Langchain/Tools/toolsCodingAgent.py
   ```
2. **Tool Loading Verification:** Run a test script or command to verify `toolsManager` loads `toolsCodingAgent` successfully and includes `toolAskHumanInput`:
   ```powershell
   python -c "from Langchain.Tools.toolsManager import GetToolsList, LoadToolsConfig; LoadToolsConfig(); tools = GetToolList(); print([t.name for t in tools])"
   ```
3. **CLI Integration Test:** Start `python UI/cli.py` (or test via python script) and verify that the agent can successfully invoke `toolAskHumanInput` when ambiguity arises or when explicitly instructed.
