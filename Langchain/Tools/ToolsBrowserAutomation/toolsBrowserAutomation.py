# toolsBrowserAutomation.py
# RPI Tactical Browser Automation Suite
# Provides advanced web navigation, reading, scraping, interaction, and workflow execution.

import os
import json
from typing import Annotated, Dict, Any, List
from langchain.tools import tool

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


def _get_or_launch_browser(p):
    """Connects to Chrome via CDP on port 9222 or launches headless/headful Chrome."""
    try:
        return p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    except Exception:
        # Fallback to standard launch or existing browser context
        chrome_paths = [
            r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\Application\\chrome.exe")
        ]
        launch_path = next((p_ath for p_ath in chrome_paths if os.path.exists(p_ath)), None)
        if not launch_path:
            # Fallback to Playwright bundled Chromium if Chrome is not found
            return p.chromium.launch(headless=False)
            
        debug_dir = os.path.expandvars(r"%LOCALAPPDATA%\\TempChromeDebug")
        os.makedirs(debug_dir, exist_ok=True)
        import subprocess
        subprocess.Popen([launch_path, "--remote-debugging-port=9222", f"--user-data-dir={debug_dir}"])
        import time
        for _ in range(10):
            try:
                return p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            except Exception:
                time.sleep(1)
        return p.chromium.launch(headless=False)


@tool("browser_navigate", description="Navigates the browser to a specified URL.")
def BrowserNavigate(url: Annotated[str, "Target URL to navigate to"]) -> str:
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url, timeout=30000)
            page.wait_for_load_state("domcontentloaded")
            return f"[SUCCESS] Navigated to {url}. Page Title: {page.title()}"
    except Exception as e:
        return f"[ERROR] Navigation failed: {str(e)}"


@tool("browser_get_page_content", description="Extracts the text content, title, and URL of the active browser page.")
def BrowserGetPageContent() -> str:
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else None
            if not page:
                return "[ERROR] No active browser page found."
            
            content_data = page.evaluate("""() => {
                return {
                    url: window.location.href,
                    title: document.title,
                    text: document.body.innerText.substring(0, 8000)
                };
            }""")
            return json.dumps(content_data, indent=2)
    except Exception as e:
        return f"[ERROR] Failed to extract page content: {str(e)}"


@tool("browser_click_element", description="Clicks an element identified by CSS selector or matching text on the active page.")
def BrowserClickElement(selector_or_text: Annotated[str, "CSS selector or button/link text to click"]) -> str:
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else None
            if not page:
                return "[ERROR] No active browser page found."
            
            # Try CSS selector first
            try:
                page.click(selector_or_text, timeout=3000)
                return f"[SUCCESS] Clicked element matching CSS selector: {selector_or_text}"
            except Exception:
                # Fallback to text search
                clicked = page.evaluate(f"""(text) => {{
                    const els = Array.from(document.querySelectorAll('a, button, input[type="submit"], [role="button"]'));
                    const target = els.find(el => el.innerText && el.innerText.toLowerCase().includes(text.toLowerCase()));
                    if (target) {{
                        target.click();
                        return true;
                    }}
                    return false;
                }}""", selector_or_text)
                if clicked:
                    return f"[SUCCESS] Clicked element containing text: {selector_or_text}"
                return f"[ERROR] Could not find or click element: {selector_or_text}"
    except Exception as e:
        return f"[ERROR] Click action failed: {str(e)}"


@tool("browser_type_text", description="Types text into an input field identified by a CSS selector.")
def BrowserTypeText(
    selector: Annotated[str, "CSS selector of the input field"],
    text: Annotated[str, "Text to type into the field"]
) -> str:
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else None
            if not page:
                return "[ERROR] No active browser page found."
            page.fill(selector, text)
            return f"[SUCCESS] Typed text into selector {selector}"
    except Exception as e:
        return f"[ERROR] Typing action failed: {str(e)}"


@tool("browser_take_screenshot", description="Takes a PNG screenshot of the current active browser viewport.")
def BrowserTakeScreenshot(filename: Annotated[str, "Output image filename (default: browser_snapshot.png)"] = "browser_snapshot.png") -> str:
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            page = browser.contexts[0].pages[0] if browser.contexts and browser.contexts[0].pages else None
            if not page:
                return "[ERROR] No active browser page found."
            page.screenshot(path=filename, full_page=True)
            return f"[SUCCESS] Screenshot saved successfully as {filename}"
    except Exception as e:
        return f"[ERROR] Screenshot failed: {str(e)}"


@tool("browser_execute_workflow", description="Executes a multi-step sequence of browser actions provided in JSON format.")
def BrowserExecuteWorkflow(steps_json: Annotated[str, "JSON string containing a list of action steps (navigate, click, type, wait)"]) -> str:
    if not PLAYWRIGHT_AVAILABLE:
        return "[ERROR] Playwright is not installed."
    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as e:
        return f"[ERROR] Invalid JSON workflow steps: {str(e)}"
        
    try:
        with sync_playwright() as p:
            browser = _get_or_launch_browser(p)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.pages[0] if context.pages else context.new_page()
            
            logs = []
            for idx, step in enumerate(steps):
                action = step.get("action")
                if action == "navigate":
                    page.goto(step.get("url"), timeout=30000)
                    logs.append(f"Step {idx+1}: Navigated to {step.get('url')}")
                elif action == "type":
                    page.fill(step.get("selector"), step.get("text", ""))
                    logs.append(f"Step {idx+1}: Typed into {step.get('selector')}")
                elif action == "click":
                    page.click(step.get("selector"))
                    logs.append(f"Step {idx+1}: Clicked {step.get('selector')}")
                elif action == "wait":
                    import time
                    time.sleep(step.get("seconds", 2))
                    logs.append(f"Step {idx+1}: Waited {step.get('seconds', 2)}s")
            
            return "[SUCCESS] Workflow executed successfully.\\n" + "\\n".join(logs)
    except Exception as e:
        return f"[ERROR] Workflow execution failed: {str(e)}"


def ToolsList():
    return [
        BrowserNavigate,
        BrowserGetPageContent,
        BrowserClickElement,
        BrowserTypeText,
        BrowserTakeScreenshot,
        BrowserExecuteWorkflow
    ]

BROWSER_AUTOMATION_TOOLS = ToolsList()
