# Plan: Implementation of `toolsProjectContextManager.py`

## 📋 Objective
Create a new tool script named `Langchain/Tools/toolsProjectContextManager.py` that contains a LangChain tool named `ReadProjectContext`. This tool will read and return the content of the `projectInfo.md` file located at the root of the project.

---

## 🛠️ Implementation Steps

### Step 1: Create `Langchain/Tools/toolsProjectContextManager.py`
- **Path:** `Langchain/Tools/toolsProjectContextManager.py`
- **Imports:** 
  - `from langchain.tools import tool`
  - `import os`
- **Tool Definition:**
  ```python
  @tool("ReadProjectContext", description="Read the projectInfo.md file to get project overview, technology stack, structure, and active status.")
  def ReadProjectContext() -> str:
      """Read the projectInfo.md file."""
      # Determine path relative to workspace or module location
      # projectInfo.md is at the root of the project repository.
      possible_paths = [
          "projectInfo.md",
          "./projectInfo.md",
          "../projectInfo.md",
          "../../projectInfo.md"
      ]
      
      for path in possible_paths:
          if os.path.exists(path):
              try:
                  with open(path, "r", encoding="utf-8") as f:
                      return f.read()
              except Exception as e:
                  return f"Error reading projectInfo.md at {path}: {str(e)}"
                  
      return "Error: projectInfo.md file not found."
  ```
- **Standard Tool Module Exports:**
  ```python
  toolsBasic = [ReadProjectContext]
  toolsIntermediate = []
  toolsAdvance = []

  tools = toolsAdvance + toolsIntermediate + toolsBasic

  def ToolsList():
      global tools
      return tools
  ```

### Step 2: Register in `toolsManager.py`
- Update `TOOLS_MODULES` dictionary in `Langchain/Tools/toolsManager.py` to include:
  ```python
  "toolsProjectContextManager": "Langchain.Tools.toolsProjectContextManager",
  ```
- Update `DEFAULT_CONFIG` in `toolsManager.py` to enable it by default if appropriate:
  ```python
  "toolsProjectContextManager": True,
  ```

### Step 3: Verification & Testing
- Write a quick test script or run a python snippet using `toolsManager` or importing `toolsProjectContextManager` directly to verify `ReadProjectContext()` successfully loads and returns `projectInfo.md`.
