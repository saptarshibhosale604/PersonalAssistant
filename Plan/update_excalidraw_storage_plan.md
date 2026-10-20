# Implementation Plan: Update Excalidraw Storage Directory to CloudPII\ToolsBlackboard\Drawings

## 1. Architectural Analysis
- Currently, `toolsBlackboard.py` defines:
  ```python
  EXCALIDRAW_EXPORT_DIR = "./Langchain/Tools/ToolsBlackboard/Drawings"
  ```
- The requested target path is:
  ```python
  EXCALIDRAW_EXPORT_DIR = "./CloudPII/ToolsBlackboard/Drawings"
  ```
- Existing drawings are stored in `./Langchain/Tools/ToolsBlackboard/Drawings`. To prevent breaking access to existing drawings like `Valorant_Agents_Blackboard.excalidraw`, we will migrate existing files upon startup.

---

## 2. Step-by-Step Implementation Steps

### Step 1: Update Constant & Add Migration in `Langchain/Tools/ToolsBlackboard/toolsBlackboard.py`
Change `EXCALIDRAW_EXPORT_DIR`:
```python
EXCALIDRAW_EXPORT_DIR = "./CloudPII/ToolsBlackboard/Drawings"
OLD_EXCALIDRAW_EXPORT_DIR = "./Langchain/Tools/ToolsBlackboard/Drawings"
```
Add migration logic:
```python
import shutil

os.makedirs(EXCALIDRAW_EXPORT_DIR, exist_ok=True)
if os.path.exists(OLD_EXCALIDRAW_EXPORT_DIR):
    for filename in os.listdir(OLD_EXCALIDRAW_EXPORT_DIR):
        old_file = os.path.join(OLD_EXCALIDRAW_EXPORT_DIR, filename)
        new_file = os.path.join(EXCALIDRAW_EXPORT_DIR, filename)
        if os.path.isfile(old_file) and not os.path.exists(new_file):
            shutil.copy2(old_file, new_file)
```

---

## 3. Files to Modify
- **`Langchain/Tools/ToolsBlackboard/toolsBlackboard.py`**

---

## 4. Potential Edge Cases & Handling
- **Missing Old Directory**: Handled by checking `os.path.exists(OLD_EXCALIDRAW_EXPORT_DIR)`.
- **File Collision**: Handled by `not os.path.exists(new_file)` check during migration.
- **Directory Permissions**: Handled by `os.makedirs(..., exist_ok=True)`.
