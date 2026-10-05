import os
import subprocess
from pathlib import Path
from typing import Optional
from langchain.tools import tool

# --------------------------------------------------------------------------
# CONFIGURATION & RESTRICTED DIRECTORY SETUP
# --------------------------------------------------------------------------
# Set to True to enforce sandbox directory locking, or False for unrestricted access.
# USE_RESTRICTED_DIR: bool = True
USE_RESTRICTED_DIR: bool = False

# Target workspace path when restricted mode is enabled
RESTRICTED_DIR = Path("/home/ssbrpi06/CustomKeyboard").resolve()


def _sanitize_path(file_path: str) -> Path:
    """Ensures file paths cannot escape RESTRICTED_DIR if restricted mode is enabled.
    Prevents path traversal attacks (e.g., ../../etc/passwd).
    """
    path = Path(file_path)

    if not USE_RESTRICTED_DIR:
        return path.resolve()

    RESTRICTED_DIR.mkdir(parents=True, exist_ok=True)
    resolved = (RESTRICTED_DIR / path).resolve()

    if not str(resolved).startswith(str(RESTRICTED_DIR)):
        raise PermissionError(
            f"Access Denied: Path '{file_path}' attempts to access outside the hardcoded directory '{RESTRICTED_DIR}'."
        )
    return resolved


@tool("toolReadFile", description="Read content from a file in the workspace directory.")
def ReadFile(file_path: str, start_line: Optional[int] = None, end_line: Optional[int] = None) -> str:
    """Reads content from a file inside the allowed workspace.
    Supports reading specific line ranges to conserve context memory.
    """
    try:
        path = _sanitize_path(file_path)
        if not path.is_file():
            base = RESTRICTED_DIR if USE_RESTRICTED_DIR else "system"
            return f"Error: File '{file_path}' does not exist inside {base}."
        
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total_lines = len(lines)
        if start_line is not None or end_line is not None:
            s = max(0, (start_line or 1) - 1)
            e = min(total_lines, end_line or total_lines)
            return f"--- {path.name} (Lines {s+1}-{e} of {total_lines}) ---\n" + "".join(lines[s:e])
        
        return "".join(lines)
    except Exception as e:
        return f"Error reading file: {str(e)}"


@tool("toolWriteFile", description="Create or overwrite a file in the workspace directory.")
def WriteFile(file_path: str, content: str) -> str:
    """Creates a new file or completely overwrites an existing file."""
    try:
        path = _sanitize_path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        temp_path = path.with_suffix(path.suffix + ".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        os.replace(temp_path, path)
        return f"Successfully wrote {len(content)} bytes to '{path}'."
    except Exception as e:
        return f"Error writing to file: {str(e)}"


@tool("toolEditFile", description="Perform an inline text replacement on a file in the workspace directory.")
def EditFile(file_path: str, old_string: str, new_string: str) -> str:
    """Replaces exact occurrences of old_string with new_string inside a file."""
    try:
        path = _sanitize_path(file_path)
        if not path.is_file():
            base = RESTRICTED_DIR if USE_RESTRICTED_DIR else "system"
            return f"Error: File '{file_path}' does not exist inside {base}."

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        occurrences = content.count(old_string)
        if occurrences == 0:
            return f"Error: 'old_string' not found in '{file_path}'."
        elif occurrences > 1:
            return f"Error: 'old_string' matched {occurrences} locations in '{file_path}'. Provide more context."

        updated_content = content.replace(old_string, new_string, 1)

        temp_path = path.with_suffix(path.suffix + ".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        os.replace(temp_path, path)

        return f"Successfully updated '{path}'."
    except Exception as e:
        return f"Error editing file: {str(e)}"


@tool("toolExecuteBash", description="Execute non-interactive shell commands inside the workspace directory.")
def ExecuteBash(command: str, timeout: int = 30) -> str:
    """Runs a bash command in the background with timeouts and context safeguards."""
    try:
        cwd_dir = RESTRICTED_DIR if USE_RESTRICTED_DIR else Path.cwd()
        if USE_RESTRICTED_DIR:
            cwd_dir.mkdir(parents=True, exist_ok=True)

        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd_dir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\n[STDERR]\n{result.stderr}"

        max_chars = 4000
        if len(output) > max_chars:
            half = max_chars // 2
            output = output[:half] + f"\n\n... [Truncated: {len(output) - max_chars} chars omitted] ...\n\n" + output[-half:]

        return f"Execution Dir: {cwd_dir}\nExit Code: {result.returncode}\nOutput:\n{output.strip()}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout} seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"


# Category-based tool collections matching otherTools.py format
toolsAdvance = [ExecuteBash]  # Tools requiring human confirmation/sensitive operations
toolsIntermediate = [ReadFile, WriteFile, EditFile]
toolsBasic = []

tools = toolsAdvance + toolsIntermediate + toolsBasic

def ToolsList():
    global tools
    return tools