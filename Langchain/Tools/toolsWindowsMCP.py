"""
Windows-MCP Tools Integration Module

Connects Personal Assistant to Windows-MCP server via MCP protocol.
Provides native Windows UI automation tools to the agent.

FIXED: Uses proper async invocation (ainvoke) for MCP tools that are async-only.
FIXED: Tool parameter names match Windows-MCP server schemas.
"""

import os
import asyncio
import concurrent.futures
from typing import Annotated, List, Any, Optional
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from Log.log_utils import PrintFunctionName

# ─── Configuration ──────────────────────────────────────────────────────
WINDOWS_MCP_URL = os.getenv("WINDOWS_MCP_URL", "http://127.0.0.1:8000/mcp/")
WINDOWS_MCP_AUTH_KEY = os.getenv("WINDOWS_MCP_AUTH_KEY", "")

# Global client cache
_mcp_client: Optional[MultiServerMCPClient] = None
_mcp_tools_cache: List[Any] = []


def _get_mcp_client() -> MultiServerMCPClient:
    """Get or create the MCP client singleton (HTTP + Bearer auth)."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MultiServerMCPClient({
            "windows-mcp": {
                "url": WINDOWS_MCP_URL,
                "transport": "streamable_http",
                "headers": {"Authorization": f"Bearer {WINDOWS_MCP_AUTH_KEY}"} if WINDOWS_MCP_AUTH_KEY else {}
            }
        })
    return _mcp_client


async def _fetch_mcp_tools() -> List[Any]:
    """Fetch tools from Windows-MCP server."""
    global _mcp_tools_cache
    if not _mcp_tools_cache:
        client = _get_mcp_client()
        _mcp_tools_cache = await client.get_tools()
    return _mcp_tools_cache


def _run_async(coro):
    """
    Run async coroutine in sync context.
    Handles both cases: running in existing event loop or not.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        # Running in async context - use thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    else:
        # No running loop - safe to use asyncio.run
        return asyncio.run(coro)


# ─── Tool Wrappers (Sync interface for LangChain) ───────────────────────

@tool("windows_click", description="Click at coordinates or on a UI element on the Windows desktop. Provide either loc=[x,y] or label=element_id.")
def WindowsClick(
    loc: Annotated[Optional[List[int]], "Coordinates [x, y] to click"] = None,
    label: Annotated[Optional[int], "UI element label/id to click"] = None,
    button: Annotated[str, "Mouse button: left, right, middle"] = "left",
    clicks: Annotated[int, "Number of clicks (0=hover, 1=single, 2=double)"] = 1,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    click_tool = next((t for t in tools if t.name == "Click"), None)
    if not click_tool:
        return "Error: Click tool not available on Windows-MCP server"
    try:
        args = {"button": button, "clicks": clicks}
        if loc is not None:
            args["loc"] = loc
        if label is not None:
            args["label"] = label
        result = _run_async(click_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Click failed: {e}"


@tool("windows_type", description="Type text at coordinates or on a UI element. Provide either loc=[x,y] or label=element_id.")
def WindowsType(
    text: Annotated[str, "Text to type"],
    loc: Annotated[Optional[List[int]], "Coordinates [x, y] to type at"] = None,
    label: Annotated[Optional[int], "UI element label/id to type at"] = None,
    clear: Annotated[bool, "Clear existing text first"] = False,
    caret_position: Annotated[str, "Where to position caret: start, idle, end"] = "idle",
    press_enter: Annotated[bool, "Press Enter after typing"] = False,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    type_tool = next((t for t in tools if t.name == "Type"), None)
    if not type_tool:
        return "Error: Type tool not available on Windows-MCP server"
    try:
        args = {"text": text, "clear": clear, "caret_position": caret_position, "press_enter": press_enter}
        if loc is not None:
            args["loc"] = loc
        if label is not None:
            args["label"] = label
        result = _run_async(type_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Type failed: {e}"


@tool("windows_screenshot", description="Take a screenshot of the Windows desktop or a specific window.")
def WindowsScreenshot(
    use_annotation: Annotated[bool, "Draw bounding boxes on UI elements"] = False,
    width_reference_line: Annotated[Optional[int], "Overlay grid width reference"] = None,
    height_reference_line: Annotated[Optional[int], "Overlay grid height reference"] = None,
    display: Annotated[Optional[List[int]], "Display indices to capture"] = None,
    region: Annotated[Optional[List[int]], "Region [left, top, right, bottom] to capture"] = None,
    save_path: Annotated[Optional[str], "Path to save screenshot"] = None,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    screenshot_tool = next((t for t in tools if t.name == "Screenshot"), None)
    if not screenshot_tool:
        return "Error: Screenshot tool not available on Windows-MCP server"
    try:
        args = {}
        if use_annotation:
            args["use_annotation"] = use_annotation
        if width_reference_line is not None:
            args["width_reference_line"] = width_reference_line
        if height_reference_line is not None:
            args["height_reference_line"] = height_reference_line
        if display is not None:
            args["display"] = display
        if region is not None:
            args["region"] = region
        if save_path is not None:
            args["save_path"] = save_path
        result = _run_async(screenshot_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Screenshot failed: {e}"


@tool("windows_snapshot", description="Capture the current UI state (element tree) of the Windows desktop or a specific window.")
def WindowsSnapshot(
    use_vision: Annotated[bool, "Include screenshot with cursor highlight"] = False,
    use_dom: Annotated[bool, "Use DOM mode for browser automation"] = False,
    use_annotation: Annotated[bool, "Draw bounding boxes on UI elements"] = True,
    use_ui_tree: Annotated[bool, "Extract interactive element tree"] = True,
    width_reference_line: Annotated[Optional[int], "Overlay grid width reference"] = None,
    height_reference_line: Annotated[Optional[int], "Overlay grid height reference"] = None,
    display: Annotated[Optional[List[int]], "Display indices to capture"] = None,
    region: Annotated[Optional[List[int]], "Region [left, top, right, bottom] to capture"] = None,
    save_path: Annotated[Optional[str], "Path to save screenshot"] = None,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    snapshot_tool = next((t for t in tools if t.name == "Snapshot"), None)
    if not snapshot_tool:
        return "Error: Snapshot tool not available on Windows-MCP server"
    try:
        args = {}
        if use_vision:
            args["use_vision"] = use_vision
        if use_dom:
            args["use_dom"] = use_dom
        if not use_annotation:
            args["use_annotation"] = use_annotation
        if not use_ui_tree:
            args["use_ui_tree"] = use_ui_tree
        if width_reference_line is not None:
            args["width_reference_line"] = width_reference_line
        if height_reference_line is not None:
            args["height_reference_line"] = height_reference_line
        if display is not None:
            args["display"] = display
        if region is not None:
            args["region"] = region
        if save_path is not None:
            args["save_path"] = save_path
        result = _run_async(snapshot_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Snapshot failed: {e}"


@tool("windows_app_launch", description="Launch a Windows application by Start Menu name.")
def WindowsAppLaunch(
    name: Annotated[str, "Application name (Start Menu display name)"],
    app_args: Annotated[Optional[List[str]], "Command line arguments"] = None,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    app_tool = next((t for t in tools if t.name == "App"), None)
    if not app_tool:
        return "Error: App tool not available on Windows-MCP server"
    try:
        invoke_args = {"mode": "launch", "name": name}
        if app_args:
            invoke_args["args"] = app_args
        result = _run_async(app_tool.ainvoke(invoke_args))
        return str(result)
    except Exception as e:
        return f"App launch failed: {e}"


@tool("windows_app_switch", description="Switch to/focus a running Windows application.")
def WindowsAppSwitch(
    name: Annotated[str, "Application name or window title"],
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    app_tool = next((t for t in tools if t.name == "App"), None)
    if not app_tool:
        return "Error: App tool not available on Windows-MCP server"
    try:
        result = _run_async(app_tool.ainvoke({"mode": "switch", "name": name}))
        return str(result)
    except Exception as e:
        return f"App switch failed: {e}"


@tool("windows_shortcut", description="Send a keyboard shortcut (hotkey) on Windows.")
def WindowsShortcut(
    shortcut: Annotated[str, "Keys to press (e.g., 'ctrl+c', 'win+d', 'alt+tab')"],
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    shortcut_tool = next((t for t in tools if t.name == "Shortcut"), None)
    if not shortcut_tool:
        return "Error: Shortcut tool not available on Windows-MCP server"
    try:
        result = _run_async(shortcut_tool.ainvoke({"shortcut": shortcut}))
        return str(result)
    except Exception as e:
        return f"Shortcut failed: {e}"


@tool("windows_scroll", description="Scroll at coordinates or on a UI element. Provide either loc=[x,y] or label=element_id.")
def WindowsScroll(
    loc: Annotated[Optional[List[int]], "Coordinates [x, y] to scroll at"] = None,
    label: Annotated[Optional[int], "UI element label/id to scroll at"] = None,
    type: Annotated[str, "Scroll type: vertical or horizontal"] = "vertical",
    direction: Annotated[str, "Scroll direction: up, down, left, right"] = "down",
    wheel_times: Annotated[int, "Number of wheel clicks (1 ≈ 3-5 lines)"] = 1,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    scroll_tool = next((t for t in tools if t.name == "Scroll"), None)
    if not scroll_tool:
        return "Error: Scroll tool not available on Windows-MCP server"
    try:
        args = {"type": type, "direction": direction, "wheel_times": wheel_times}
        if loc is not None:
            args["loc"] = loc
        if label is not None:
            args["label"] = label
        result = _run_async(scroll_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Scroll failed: {e}"


@tool("windows_move_mouse", description="Move mouse cursor to coordinates or a UI element. Provide either loc=[x,y] or label=element_id.")
def WindowsMoveMouse(
    loc: Annotated[Optional[List[int]], "Coordinates [x, y] to move to"] = None,
    label: Annotated[Optional[int], "UI element label/id to move to"] = None,
    drag: Annotated[bool, "Perform drag-and-drop from current position"] = False,
    from_loc: Annotated[Optional[List[int]], "Drag start coordinates [x, y]"] = None,
    duration: Annotated[Optional[float], "Move duration in seconds"] = None,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    move_tool = next((t for t in tools if t.name == "Move"), None)
    if not move_tool:
        return "Error: Move tool not available on Windows-MCP server"
    try:
        args = {}
        if loc is not None:
            args["loc"] = loc
        if label is not None:
            args["label"] = label
        if drag:
            args["drag"] = drag
        if from_loc is not None:
            args["from_loc"] = from_loc
        if duration is not None:
            args["duration"] = duration
        result = _run_async(move_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Move failed: {e}"


@tool("windows_powershell", description="Execute a PowerShell command on the Windows host.")
def WindowsPowerShell(
    command: Annotated[str, "PowerShell command to execute"],
    timeout: Annotated[int, "Timeout in seconds"] = 30,
    max_output: Annotated[int, "Maximum output characters"] = 20000,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    ps_tool = next((t for t in tools if t.name == "PowerShell"), None)
    if not ps_tool:
        return "Error: PowerShell tool not available on Windows-MCP server"
    try:
        result = _run_async(ps_tool.ainvoke({"command": command, "timeout": timeout, "max_output": max_output}))
        return str(result)
    except Exception as e:
        return f"PowerShell failed: {e}"


@tool("windows_file_system", description="Read/write/list files on the Windows host filesystem. Modes: read, write, copy, move, delete, list, search, info.")
def WindowsFileSystem(
    mode: Annotated[str, "Operation mode: read, write, copy, move, delete, list, search, info"],
    path: Annotated[str, "File or directory path on Windows host"],
    destination: Annotated[Optional[str], "Destination path for copy/move"] = None,
    content: Annotated[Optional[str], "Content for write mode"] = None,
    pattern: Annotated[Optional[str], "Glob pattern for search mode"] = None,
    recursive: Annotated[bool, "Recursive for delete/list"] = False,
    append: Annotated[bool, "Append for write mode"] = False,
    overwrite: Annotated[bool, "Overwrite for copy/move"] = False,
    offset: Annotated[Optional[int], "Line offset for read mode"] = None,
    limit: Annotated[Optional[int], "Line limit for read mode"] = None,
    encoding: Annotated[str, "Text encoding"] = "utf-8",
    show_hidden: Annotated[bool, "Show hidden files"] = False,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    fs_tool = next((t for t in tools if t.name == "FileSystem"), None)
    if not fs_tool:
        return "Error: FileSystem tool not available on Windows-MCP server"
    try:
        args = {"mode": mode, "path": path}
        if destination is not None:
            args["destination"] = destination
        if content is not None:
            args["content"] = content
        if pattern is not None:
            args["pattern"] = pattern
        if recursive:
            args["recursive"] = recursive
        if append:
            args["append"] = append
        if overwrite:
            args["overwrite"] = overwrite
        if offset is not None:
            args["offset"] = offset
        if limit is not None:
            args["limit"] = limit
        if encoding != "utf-8":
            args["encoding"] = encoding
        if show_hidden:
            args["show_hidden"] = show_hidden
        result = _run_async(fs_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"FileSystem failed: {e}"


@tool("windows_process_list", description="List running processes on the Windows host.")
def WindowsProcessList(
    sort_by: Annotated[str, "Sort by: memory, cpu, name"] = "memory",
    limit: Annotated[int, "Maximum number of processes"] = 20,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    process_tool = next((t for t in tools if t.name == "Process"), None)
    if not process_tool:
        return "Error: Process tool not available on Windows-MCP server"
    try:
        result = _run_async(process_tool.ainvoke({"mode": "list", "sort_by": sort_by, "limit": limit}))
        return str(result)
    except Exception as e:
        return f"Process list failed: {e}"


@tool("windows_process_kill", description="Kill a process on the Windows host by PID or name.")
def WindowsProcessKill(
    pid: Annotated[Optional[int], "Process ID to kill"] = None,
    name: Annotated[Optional[str], "Process name to kill"] = None,
    force: Annotated[bool, "Force kill"] = False,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    process_tool = next((t for t in tools if t.name == "Process"), None)
    if not process_tool:
        return "Error: Process tool not available on Windows-MCP server"
    try:
        args = {"mode": "kill", "force": force}
        if pid is not None:
            args["pid"] = pid
        if name is not None:
            args["name"] = name
        result = _run_async(process_tool.ainvoke(args))
        return str(result)
    except Exception as e:
        return f"Process kill failed: {e}"


@tool("windows_clipboard_get", description="Get clipboard content from the Windows host.")
def WindowsClipboardGet() -> str:
    tools = _run_async(_fetch_mcp_tools())
    clip_tool = next((t for t in tools if t.name == "Clipboard"), None)
    if not clip_tool:
        return "Error: Clipboard tool not available on Windows-MCP server"
    try:
        result = _run_async(clip_tool.ainvoke({"mode": "get"}))
        return str(result)
    except Exception as e:
        return f"Clipboard get failed: {e}"


@tool("windows_clipboard_set", description="Set clipboard content on the Windows host.")
def WindowsClipboardSet(
    text: Annotated[str, "Content to set on clipboard"],
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    clip_tool = next((t for t in tools if t.name == "Clipboard"), None)
    if not clip_tool:
        return "Error: Clipboard tool not available on Windows-MCP server"
    try:
        result = _run_async(clip_tool.ainvoke({"mode": "set", "text": text}))
        return str(result)
    except Exception as e:
        return f"Clipboard set failed: {e}"


@tool("windows_notification", description="Send a Windows toast notification.")
def WindowsNotification(
    title: Annotated[str, "Notification title"],
    message: Annotated[str, "Notification message"],
    app_id: Annotated[str, "App ID for notification (from Get-StartApps)"] = "Windows-MCP",
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    notif_tool = next((t for t in tools if t.name == "Notification"), None)
    if not notif_tool:
        return "Error: Notification tool not available on Windows-MCP server"
    try:
        result = _run_async(notif_tool.ainvoke({"title": title, "message": message, "app_id": app_id}))
        return str(result)
    except Exception as e:
        return f"Notification failed: {e}"


@tool("windows_registry_read", description="Read a Windows Registry value. Path uses PowerShell format (e.g., HKCU:\\Software\\MyApp).")
def WindowsRegistryRead(
    path: Annotated[str, "Registry key path (e.g., HKCU:\\Software\\MyApp)"],
    name: Annotated[str, "Value name to read"],
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    reg_tool = next((t for t in tools if t.name == "Registry"), None)
    if not reg_tool:
        return "Error: Registry tool not available on Windows-MCP server"
    try:
        result = _run_async(reg_tool.ainvoke({"mode": "get", "path": path, "name": name}))
        return str(result)
    except Exception as e:
        return f"Registry read failed: {e}"


@tool("windows_registry_write", description="Write a Windows Registry value. WARNING: Modifying the Windows Registry can cause system instability. Use with extreme caution. Always backup the registry before making changes.")
def WindowsRegistryWrite(
    path: Annotated[str, "Registry key path (e.g., HKCU:\\Software\\MyApp)"],
    name: Annotated[str, "Value name"],
    value: Annotated[str, "Value to write"],
    type: Annotated[str, "Registry value type: String, ExpandString, Binary, DWord, MultiString, QWord"] = "String",
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    reg_tool = next((t for t in tools if t.name == "Registry"), None)
    if not reg_tool:
        return "Error: Registry tool not available on Windows-MCP server"
    try:
        result = _run_async(reg_tool.ainvoke({"mode": "set", "path": path, "name": name, "value": value, "type": type}))
        return str(result)
    except Exception as e:
        return f"Registry write failed: {e}"


@tool("windows_display_inventory", description="Get display/monitor information from the Windows host.")
def WindowsDisplayInventory() -> str:
    tools = _run_async(_fetch_mcp_tools())
    disp_tool = next((t for t in tools if t.name == "DisplayInventory"), None)
    if not disp_tool:
        return "Error: DisplayInventory tool not available on Windows-MCP server"
    try:
        result = _run_async(disp_tool.ainvoke({}))
        return str(result)
    except Exception as e:
        return f"Display inventory failed: {e}"


@tool("windows_control_status", description="Get the current desktop control status from Windows-MCP.")
def WindowsControlStatus(
    release: Annotated[bool, "Release AI control of desktop"] = False,
) -> str:
    tools = _run_async(_fetch_mcp_tools())
    status_tool = next((t for t in tools if t.name == "ControlStatus"), None)
    if not status_tool:
        return "Error: ControlStatus tool not available on Windows-MCP server"
    try:
        result = _run_async(status_tool.ainvoke({"release": release}))
        return str(result)
    except Exception as e:
        return f"Control status failed: {e}"


# ─── Tool List Export ───────────────────────────────────────────────────

toolsWindowsMCP = [
    WindowsClick,
    WindowsType,
    WindowsScreenshot,
    WindowsSnapshot,
    WindowsAppLaunch,
    WindowsAppSwitch,
    WindowsShortcut,
    WindowsScroll,
    WindowsMoveMouse,
    WindowsPowerShell,
    WindowsFileSystem,
    WindowsProcessList,
    WindowsProcessKill,
    WindowsClipboardGet,
    WindowsClipboardSet,
    WindowsNotification,
    WindowsRegistryRead,
    # WindowsRegistryWrite,  # Commented out: Registry write can cause system instability
    WindowsDisplayInventory,
    WindowsControlStatus,
]


def ToolsList():
    """Return the list of Windows-MCP tools for toolsManager."""
    return toolsWindowsMCP