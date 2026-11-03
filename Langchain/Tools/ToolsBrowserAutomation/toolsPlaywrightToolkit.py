# Langchain/Tools/ToolsBrowserAutomation/toolsPlaywrightToolkit.py
# RPI Tactical Prebuilt Playwright Toolkit Integration (Dedicated-Thread Sync Bridge)
# Playwright's sync API is greenlet-bound to the thread that created it. LangGraph's ToolNode
# runs tools on arbitrary worker threads, so every Playwright call is marshalled onto ONE
# dedicated thread that owns the browser.

import atexit
from concurrent.futures import ThreadPoolExecutor
from typing import List, Any

from langchain.tools import tool
from langchain_core.tools import StructuredTool
from pydantic import create_model

try:
    from langchain_community.agent_toolkits.playwright.toolkit import PlayWrightBrowserToolkit
    from langchain_community.tools.playwright.utils import create_sync_playwright_browser
    PLAYWRIGHT_COMMUNITY_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_COMMUNITY_AVAILABLE = False

# Global state
_sync_browser = None
_playwright_toolkit = None
_wrapped_tools: List[Any] = []

# Single dedicated thread that owns the Playwright sync browser
_playwright_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="playwright")


def _WrapTool(inner: Any) -> StructuredTool:
    """Wrap a Playwright tool so its execution always happens on the Playwright thread."""

    def _runOnPlaywrightThread(**kwargs) -> Any:
        return _playwright_executor.submit(inner.invoke, kwargs).result()

    argsSchema = inner.args_schema or create_model(f"{inner.name}_Args")

    return StructuredTool.from_function(
        func=_runOnPlaywrightThread,
        name=inner.name,
        description=inner.description,
        args_schema=argsSchema,
        infer_schema=False,
    )


def _CloseBrowser() -> None:
    """Close the browser on its owning thread, then stop the thread."""
    global _sync_browser
    try:
        if _sync_browser is not None:
            _playwright_executor.submit(_sync_browser.close).result(timeout=10)
    except Exception:
        pass
    finally:
        _sync_browser = None
        _playwright_executor.shutdown(wait=False)


def GetPlaywrightTools(headless: bool = False) -> List[Any]:
    """
    Initializes the official LangChain Playwright tools. The browser is created on the dedicated
    Playwright thread, and each returned tool dispatches its work to that same thread.
    """
    global _sync_browser, _playwright_toolkit, _wrapped_tools
    if not PLAYWRIGHT_COMMUNITY_AVAILABLE:
        print("[ERROR] langchain_community or playwright is not installed.")
        return []

    try:
        if _sync_browser is None:
            # Browser MUST be created on the Playwright thread
            _sync_browser = _playwright_executor.submit(
                create_sync_playwright_browser, headless=headless
            ).result()
            _playwright_toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=_sync_browser)
            _wrapped_tools = [_WrapTool(t) for t in _playwright_toolkit.get_tools()]
            atexit.register(_CloseBrowser)
        return list(_wrapped_tools)
    except Exception as e:
        print(f"[ERROR] Failed to initialize PlayWrightBrowserToolkit: {str(e)}")
        return []


@tool("playwright_toolkit_status", description="Check status of prebuilt LangChain Playwright toolkit.")
def PlaywrightToolkitStatus() -> str:
    if not PLAYWRIGHT_COMMUNITY_AVAILABLE:
        return "[STATUS] Playwright community toolkit is NOT available (Missing packages)."
    return "[STATUS] Playwright community toolkit is AVAILABLE (Sync Mode, dedicated thread) and ready for tactical deployment."


def ToolsList() -> List[Any]:
    """Returns the list of tools provided by this module."""
    tools = GetPlaywrightTools(headless=False)
    tools.append(PlaywrightToolkitStatus)
    return tools