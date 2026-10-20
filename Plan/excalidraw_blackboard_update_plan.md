# Implementation Plan: Excalidraw Blackboard Tools Update

## Overview
This plan outlines the updates to `Langchain\Tools\ToolsBlackboard\toolsBlackboard.py` to:
1. Change the default save directory for Excalidraw files to `Langchain\Tools\ToolsBlackboard\Drawings`.
2. Rename the creation tool from `create_excalidraw_diagram` to `create_excalidraw_drawings`.
3. Add a new tool `list_excalidraw_drawings` to check current drawings.
4. Add a new tool `detect_drawing_modifications` to detect human changes made to existing drawings.

---

## Detailed Step-by-Step Plan

### 1. Update Save Directory Constant
- **Target File:** `Langchain/Tools/ToolsBlackboard/toolsBlackboard.py`
- **Change:**
  ```python
  EXCALIDRAW_EXPORT_DIR = "./Langchain/Tools/ToolsBlackboard/Drawings"
  ```

### 2. Rename `create_excalidraw_diagram` to `create_excalidraw_drawings`
- **Changes:**
  - Rename function definition from `create_excalidraw_diagram` to `create_excalidraw_drawings`.
  - Update `generate_sample_architecture_diagram` to invoke `create_excalidraw_drawings` instead of `create_excalidraw_diagram`.
  - Update success message and docstrings.

### 3. Implement `list_excalidraw_drawings` Tool
- **Function Signature:**
  ```python
  @tool
  def list_excalidraw_drawings() -> str:
      """
      Check and list all current Excalidraw drawings stored in the local Drawings directory.
      Returns file names, sizes, element counts, and last modified timestamps.
      """
  ```
- **Implementation Details:**
  - Check if `EXCALIDRAW_EXPORT_DIR` exists.
  - List all `.excalidraw` files.
  - For each file, inspect:
    - File size (KB)
    - Last modified time (`os.path.getmtime`)
    - Element count by parsing JSON content (`scene_data.get("elements", [])`)
  - Return formatted summary string.

### 4. Implement `detect_drawing_modifications` Tool
- **Function Signature:**
  ```python
  @tool
  def detect_drawing_modifications(
      drawing_title: Annotated[str, "Title or name of the drawing file to check for human modifications"]
  ) -> str:
      """
      Detects if changes have been made to an existing Excalidraw drawing file by inspecting
      file modification timestamps and element structural updates.
      """
  ```
- **Implementation Details:**
  - Sanitize `drawing_title` to find the corresponding `.excalidraw` file in `EXCALIDRAW_EXPORT_DIR`.
  - Check file existence and retrieve file stats (`st_mtime`, size).
  - Read JSON content to analyze elements (count, types, IDs).
  - Compare file modification timestamp against expected generation baseline or report recent modification status and element summary to detect human edits.

### 5. Update Module Exports (`toolsBasic`)
- Update `toolsBasic` to include:
  ```python
  toolsBasic = [
      create_excalidraw_drawings,
      generate_sample_architecture_diagram,
      list_excalidraw_drawings,
      detect_drawing_modifications
  ]
  ```

---

## Edge Cases & Mitigations
1. **Directory Not Found:** Ensure `os.makedirs(EXCALIDRAW_EXPORT_DIR, exist_ok=True)` runs before file operations.
2. **Corrupt/Malformed JSON:** Wrap JSON parsing in `try...except (json.JSONDecodeError, Exception)` when reading existing drawing files in listing or modification detection.
3. **File Not Found:** Gracefully return informative error messages if a requested drawing title does not exist.
