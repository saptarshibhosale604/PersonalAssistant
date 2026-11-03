# Langchain/Tools/ToolsBrowserAutomation/toolsPlaywrightToolkit.py
# RPI Tactical Prebuilt Playwright Toolkit Integration
# Integrates official langchain_community Playwright toolkit for robust browser automation.

import os
from typing import List, Any
from langchain.tools import tool

try:
    from langchain_community.agent_toolkits.playwright.toolkit import PlayWrightBrowserToolkit
    from langchain_community.tools.playwright.utils import create_sync_playwright_browser
    PLAYWRIGHT_COMMUNITY_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_COMMUNITY_AVAILABLE = False

# Global state for sync browser and toolkit
_sync_browser = None
_playwright_toolkit = None


def GetPlaywrightTools(headless: bool = False) -> List[Any]:
    """
    Initializes and returns official prebuilt LangChain Playwright tools.
    Provides Navigate, Click, ExtractText, ExtractHyperlinks, GetElements, etc.
    """
    global _sync_browser, _playwright_toolkit
    if not PLAYWRIGHT_COMMUNITY_AVAILABLE:
        print("[ERROR] langchain_community or playwright is not installed.")
        return []
    
    try:
        if _sync_browser is None:
            _sync_browser = create_sync_playwright_browser(headless=headless)
            _playwright_toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=_sync_browser)
        return _playwright_toolkit.get_tools()
    except Exception as e:
        print(f"[ERROR] Failed to initialize PlayWrightBrowserToolkit: {str(e)}")
        return []


@tool("playwright_toolkit_status", description="Check status of prebuilt LangChain Playwright toolkit.")
def PlaywrightToolkitStatus() -> str:
    if not PLAYWRIGHT_COMMUNITY_AVAILABLE:
        return "[STATUS] Playwright community toolkit is NOT available (Missing packages)."
    return "[STATUS] Playwright community toolkit is AVAILABLE and ready for tactical deployment."


def ToolsList() -> List[Any]:
    """Returns the list of tools provided by this module."""
    tools = GetPlaywrightTools(headless=False)
    tools.append(PlaywrightToolkitStatus)
    return tools

