import os
import subprocess
import threading
import time
import signal
import platform
from pathlib import Path
from typing import Optional
from langchain.tools import tool

# Optional: psutil for better process inspection (install if not present)
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

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


# --------------------------------------------------------------------------
# PROCESS REGISTRY - Track background/async commands for manual management
# --------------------------------------------------------------------------
_process_registry = {}
_registry_lock = threading.Lock()


def _register_process(pid: int, command: str, process_obj) -> None:
    """Register a running process for later management."""
    with _registry_lock:
        _process_registry[pid] = {
            "pid": pid,
            "command": command,
            "process": process_obj,
            "start_time": time.time(),
            "status": "running"
        }


def _unregister_process(pid: int) -> bool:
    """Remove process from registry."""
    with _registry_lock:
        if pid in _process_registry:
            del _process_registry[pid]
            return True
        return False


def _get_process_info(pid: int) -> dict:
    """Get process info from registry."""
    with _registry_lock:
        return _process_registry.get(pid, {})


def _list_running_processes() -> list:
    """List all tracked running processes."""
    with _registry_lock:
        return [
            {"pid": pid, "command": info["command"], "duration": time.time() - info["start_time"]}
            for pid, info in _process_registry.items()
            if info["status"] == "running"
        ]


def _terminate_process_tree(pid: int, process_obj=None) -> bool:
    """Forcefully terminate a process and all its children (cross-platform)."""
    try:
        if platform.system() == "Windows":
            # Windows: Use taskkill /T /F for tree kill
            result = subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        else:
            # Unix: Kill process group
            try:
                pgid = os.getpgid(pid)
                os.killpg(pgid, signal.SIGTERM)
                time.sleep(0.5)
                # Check if still alive
                if PSUTIL_AVAILABLE and psutil.pid_exists(pid):
                    os.killpg(pgid, signal.SIGKILL)
                elif not PSUTIL_AVAILABLE:
                    # Fallback: try SIGKILL anyway
                    try:
                        os.killpg(pgid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            except ProcessLookupError:
                pass  # Already dead
            return True
    except Exception:
        return False


# --------------------------------------------------------------------------
# FILE TOOLS (Unchanged)
# --------------------------------------------------------------------------
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


# --------------------------------------------------------------------------
# ENHANCED BASH EXECUTION TOOLS
# --------------------------------------------------------------------------
@tool("toolExecuteBash", description="Execute non-interactive shell commands inside the workspace directory with robust timeout handling and process tree termination.")
def ExecuteBash(command: str, timeout: int = 30) -> str:
    """Runs a command with guaranteed process tree termination on timeout.
    
    Uses process groups (Unix) or CREATE_NEW_PROCESS_GROUP (Windows) to ensure
    child processes are also terminated when the command times out.
    """
    try:
        cwd_dir = RESTRICTED_DIR if USE_RESTRICTED_DIR else Path.cwd()
        if USE_RESTRICTED_DIR:
            cwd_dir.mkdir(parents=True, exist_ok=True)

        # Launch with process group for tree termination
        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                creationflags=creation_flags
            )
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                preexec_fn=os.setsid
            )

        _register_process(process.pid, command, process)

        try:
            stdout, stderr = process.communicate(timeout=timeout)
            _unregister_process(process.pid)
            
            output = stdout or ""
            if stderr:
                output += f"\n[STDERR]\n{stderr}"

            max_chars = 4000
            if len(output) > max_chars:
                half = max_chars // 2
                output = output[:half] + f"\n\n... [Truncated: {len(output) - max_chars} chars omitted] ...\n\n" + output[-half:]

            return f"Execution Dir: {cwd_dir}\nExit Code: {process.returncode}\nOutput:\n{output.strip()}"
            
        except subprocess.TimeoutExpired:
            # Multi-stage termination: SIGTERM -> SIGKILL -> taskkill /T /F
            _terminate_process_tree(process.pid, process)
            _unregister_process(process.pid)
            return f"Error: Command timed out after {timeout} seconds. Process tree forcefully terminated."
            
    except Exception as e:
        return f"Error executing command: {str(e)}"


@tool("toolKillBash", description="Forcefully terminate a hanging shell command by PID. Use toolListBash to see running commands.")
def KillBash(pid: int) -> str:
    """Manually kill a specific running bash command by its process ID.
    
    This is the MANUAL KILL SWITCH - use when a command hangs and you need
    to force-terminate it immediately without waiting for timeout.
    """
    try:
        info = _get_process_info(pid)
        command_desc = info.get("command", "unknown") if info else "unknown (not in registry)"
        
        success = _terminate_process_tree(pid)
        _unregister_process(pid)
        
        if success:
            return f"Successfully terminated process {pid} (command: {command_desc})."
        else:
            return f"Termination attempted for PID {pid}. Check with toolListBash to confirm."
    except Exception as e:
        return f"Error killing process {pid}: {str(e)}"


@tool("toolListBash", description="List all currently tracked running shell commands with their PIDs and run duration.")
def ListBash() -> str:
    """List all currently running background shell commands tracked by the registry."""
    processes = _list_running_processes()
    if not processes:
        return "No tracked running commands."
    
    lines = ["=== RUNNING COMMANDS ==="]
    for p in processes:
        lines.append(f"  PID: {p['pid']} | Duration: {p['duration']:.1f}s | Command: {p['command'][:100]}")
    lines.append(f"\nTotal: {len(processes)} command(s)")
    return "\n".join(lines)


@tool("toolExecuteBashAsync", description="Start a shell command in the background and return immediately with PID. Use toolListBash to monitor, toolKillBash to terminate, toolGetBashOutput to retrieve results.")
def ExecuteBashAsync(command: str) -> str:
    """Start a command asynchronously, return PID for later management.
    
    Use this for long-running commands where you want to:
    1. Start the command (get PID immediately)
    2. Do other work
    3. Check status with toolListBash
    4. Get output with toolGetBashOutput
    5. Kill if needed with toolKillBash
    """
    try:
        cwd_dir = RESTRICTED_DIR if USE_RESTRICTED_DIR else Path.cwd()
        if USE_RESTRICTED_DIR:
            cwd_dir.mkdir(parents=True, exist_ok=True)

        if platform.system() == "Windows":
            creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                creationflags=creation_flags
            )
        else:
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=cwd_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                preexec_fn=os.setsid
            )

        _register_process(process.pid, command, process)
        return f"Started background command (PID: {process.pid})\nCommand: {command}\nWorking Dir: {cwd_dir}\nUse toolListBash to monitor, toolGetBashOutput to retrieve results, toolKillBash to terminate."
    except Exception as e:
        return f"Error starting async command: {str(e)}"


@tool("toolGetBashOutput", description="Get the output of a background command by PID. Set wait=true to wait for completion (with timeout), or wait=false for non-blocking partial read.")
def GetBashOutput(pid: int, wait: bool = False, timeout: int = 30) -> str:
    """Retrieve stdout/stderr of a background command.
    
    Args:
        pid: Process ID from toolExecuteBashAsync or toolListBash
        wait: If true, wait for process to complete (up to timeout seconds)
        timeout: Max seconds to wait when wait=true
    """
    info = _get_process_info(pid)
    if not info:
        return f"Error: No tracked process with PID {pid}. Use toolListBash to see running commands."
    
    process = info["process"]
    
    if wait:
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            _unregister_process(pid)
            output = stdout or ""
            if stderr:
                output += f"\n[STDERR]\n{stderr}"
            return f"Exit Code: {process.returncode}\nOutput:\n{output.strip()}"
        except subprocess.TimeoutExpired:
            return f"Process {pid} still running after {timeout}s wait. Use toolKillBash to terminate or try again later."
    else:
        # Non-blocking read - try to get available output without waiting
        try:
            if platform.system() != "Windows":
                import select
                ready, _, _ = select.select([process.stdout, process.stderr], [], [], 0)
                stdout_data = ""
                stderr_data = ""
                if process.stdout in ready:
                    stdout_data = process.stdout.read()
                if process.stderr in ready:
                    stderr_data = process.stderr.read()
                if not stdout_data and not stderr_data:
                    return f"Process {pid} still running. No output available yet. Use wait=true to wait for completion."
                return f"[Partial Output - Process Still Running]\nSTDOUT: {stdout_data}\nSTDERR: {stderr_data}"
            else:
                # Windows: non-blocking read is limited
                return f"Process {pid} still running. Non-blocking read limited on Windows. Use wait=true to wait for completion."
        except Exception as e:
            return f"Error reading output: {str(e)}"


# @tool("toolAskHumanInput", description="Prompt the human user for input, clarification, confirmation, or additional instructions during execution.")
# def AskHumanInput(prompt_message: str) -> str:
#     """Pauses agent execution and prompts the human user in the terminal/UI for input or decision making."""
#     try:
#         print(f"\n[AGENT REQUESTS INPUT]: {prompt_message}")
#         user_response = input("Human Input Required > ").strip()
#         return f"Human response: {user_response}"
#     except Exception as e:
#         return f"Error obtaining human input: {str(e)}"


# --------------------------------------------------------------------------
# TOOL COLLECTIONS
# --------------------------------------------------------------------------
# Tools requiring human confirmation/sensitive operations / interactive prompt
toolsAdvance = [ExecuteBash, ExecuteBashAsync, KillBash, GetBashOutput]

# Read-only / safe tools
toolsIntermediate = [ReadFile, WriteFile, EditFile, ListBash]

toolsBasic = []

tools = toolsAdvance + toolsIntermediate + toolsBasic


def ToolsList():
    global tools
    return tools