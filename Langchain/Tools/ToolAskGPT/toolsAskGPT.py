"""
ask_chatgpt_tool.py

A LangChain @tool that drives the chatgpt.com web UI via Playwright to submit
a prompt and return the assistant's response.

IMPORTANT CAVEATS (read before using):
- This automates OpenAI's consumer web UI, not the official API. It is more
  fragile (selectors change) and may violate chatgpt.com's Terms of Use.
  Prefer the official OpenAI API if you just need programmatic completions.
- Requires a one-time interactive login the first time it runs (or whenever
  the saved session expires). A visible browser window will open for that.

Setup:
    pip install playwright langchain-core
    playwright install chromium

Run standalone (for testing, outside LangChain):
    python ask_chatgpt_tool.py "What is the capital of France?"
"""

import sys
import time
import json
from pathlib import Path
from typing import Optional

from playwright.sync_api import (
    sync_playwright,
    Page,
    BrowserContext,
    TimeoutError as PlaywrightTimeoutError,
)

try:
    from langchain_core.tools import tool
except ImportError:
    # Allows standalone testing even if langchain isn't installed yet.
    def tool(func):
        return func


# ---------------------------------------------------------------------------
# Config — the first things to update if ChatGPT's UI changes.
# ---------------------------------------------------------------------------

CHATGPT_URL = "https://chatgpt.com"
STATE_FILE = Path("state.json")

PROMPT_TEXTBOX_SELECTOR = "#prompt-textarea"          # contenteditable div
SEND_BUTTON_SELECTOR = "[data-testid='send-button']"
STOP_BUTTON_SELECTOR = "[data-testid='stop-button']"
ASSISTANT_MESSAGE_SELECTOR = "[data-message-author-role='assistant']"
LOGIN_BUTTON_SELECTOR = "button:has-text('Log in')"

NAV_TIMEOUT_MS = 30_000
LOGIN_WAIT_TIMEOUT_MS = 300_000       # 5 minutes to log in by hand
# LOGIN_WAIT_TIMEOUT_MS = 2_000  # 2 seconds
GENERATION_TIMEOUT_S = 120            # hard cap on waiting for a reply
STABILITY_CHECKS_REQUIRED = 3         # consecutive unchanged reads
STABILITY_POLL_INTERVAL_S = 0.5

CHROME_USER_DATA_DIR = (
    r"C:\Users\LENOVO\AppData\Local\Google\Chrome\User Data"
)

# CHROME_PROFILE = "Default"      # or "Default", "Profile 1", etc.
CHROME_PROFILE = "Profile 1"      # or "Default", "Profile 1", etc.

class AskChatGPTError(Exception):
    """Raised when the browser automation fails in a way the caller should know about."""


# ---------------------------------------------------------------------------
# Session handling
# ---------------------------------------------------------------------------

def _is_logged_in(page: Page) -> bool:
    """Best-effort check: logged-out pages show a 'Log in' button."""
    try:
        page.wait_for_selector(LOGIN_BUTTON_SELECTOR, timeout=3000)
        return False  # login button found -> not logged in
    except PlaywrightTimeoutError:
        return True   # no login button -> assume logged in


def _ensure_logged_in(context: BrowserContext, page: Page) -> None:
    """
    Verifies the current session is authenticated. If not, opens/keeps a
    visible browser and blocks until the user logs in manually, then
    persists the session to STATE_FILE for next time.
    """
    print("[ask_chatgpt] Checking login status...")
    page.goto(CHATGPT_URL, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")

    if _is_logged_in(page):
        print("[ask_chatgpt] Existing session is valid.")
        return

    print("[ask_chatgpt] Not logged in. Please log in in the opened browser window.")
    print(f"[ask_chatgpt] Waiting up to {LOGIN_WAIT_TIMEOUT_MS // 1000}s for login...")
    input("HumanInterrupt01")

    # Poll until the login button disappears (i.e. user has logged in).
    deadline = time.time() + (LOGIN_WAIT_TIMEOUT_MS / 1000)
    while time.time() < deadline:
        if _is_logged_in(page):
            print("[ask_chatgpt] Login detected. Saving session...")
            context.storage_state(path=str(STATE_FILE))
            print(f"[ask_chatgpt] Session saved to {STATE_FILE.resolve()}")
            return
        time.sleep(2)

    raise AskChatGPTError("Timed out waiting for manual login.")


# ---------------------------------------------------------------------------
# Core interaction
# ---------------------------------------------------------------------------

def _start_new_chat(page: Page) -> None:
    print("[ask_chatgpt] Starting a new chat...")
    page.goto(CHATGPT_URL, timeout=NAV_TIMEOUT_MS, wait_until="domcontentloaded")
    page.wait_for_selector(PROMPT_TEXTBOX_SELECTOR, timeout=NAV_TIMEOUT_MS)


def _send_prompt(page: Page, prompt: str) -> None:
    print("[ask_chatgpt] Typing prompt...")
    box = page.locator(PROMPT_TEXTBOX_SELECTOR)
    box.click()
    box.fill(prompt)

    print("[ask_chatgpt] Sending prompt...")
    # Prefer the explicit send button over Enter; Enter can behave
    # differently in contenteditable boxes (e.g. newline vs submit).
    send_button = page.locator(SEND_BUTTON_SELECTOR)
    try:
        send_button.click(timeout=5000)
    except PlaywrightTimeoutError:
        # Fallback if the send button selector changed.
        box.press("Enter")


def _wait_for_completion(page: Page) -> None:
    """
    Waits for generation to finish using two signals:
      1. The stop button disappears (generation stopped).
      2. The last assistant message's text is stable across several polls.
    Both are required to reduce false positives from either signal alone.
    """
    print("[ask_chatgpt] Waiting for response to start...")
    try:
        page.wait_for_selector(ASSISTANT_MESSAGE_SELECTOR, timeout=NAV_TIMEOUT_MS)
    except PlaywrightTimeoutError:
        raise AskChatGPTError("No assistant message appeared — the prompt may not have sent.")

    print("[ask_chatgpt] Generating response", end="", flush=True)
    start = time.time()
    last_text: Optional[str] = None
    stable_count = 0

    while time.time() - start < GENERATION_TIMEOUT_S:
        # Signal 1: stop button gone means the model has finished streaming.
        stop_visible = page.locator(STOP_BUTTON_SELECTOR).count() > 0

        # Signal 2: text stability.
        current_text = page.locator(ASSISTANT_MESSAGE_SELECTOR).last.inner_text()
        if current_text == last_text:
            stable_count += 1
        else:
            stable_count = 0
        last_text = current_text

        print(".", end="", flush=True)

        if not stop_visible and stable_count >= STABILITY_CHECKS_REQUIRED:
            print("\n[ask_chatgpt] Response finished.")
            return

        time.sleep(STABILITY_POLL_INTERVAL_S)

    print()
    raise AskChatGPTError(
        f"Timed out after {GENERATION_TIMEOUT_S}s waiting for generation to finish."
    )


def _read_response(page: Page) -> str:
    print("[ask_chatgpt] Reading response...")
    time.sleep(5)
    messages = page.locator(ASSISTANT_MESSAGE_SELECTOR)
    count = messages.count()
    if count == 0:
        raise AskChatGPTError("No assistant messages found on page.")
    return messages.last.inner_text()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def _ask_chatgpt_impl(prompt: str, headless: bool = False) -> str:
    print(f"[ask_chatgpt] Launching browser (headless={headless})...")
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=headless)
        # try:
        #     if STATE_FILE.exists():
        #         context = browser.new_context(storage_state=str(STATE_FILE))
        #     else:
        #         context = browser.new_context()

        #     page = context.new_page()
        try:

            CHROME_USER_DATA_DIR = r"E:\PlaywrightChromeProfile"

            context = p.chromium.launch_persistent_context(
                user_data_dir=CHROME_USER_DATA_DIR,
                channel="chrome",
                headless=False,
            )
            # context = p.chromium.launch_persistent_context(
            #     user_data_dir=CHROME_USER_DATA_DIR,
            #     channel="chrome",
            #     headless=False,
            #     args=[
            #         f"--profile-directory={CHROME_PROFILE}",
            #     ],
            # )
            page = context.new_page()

            try:
                _ensure_logged_in(context, page)
                _start_new_chat(page)
                _send_prompt(page, prompt)
                _wait_for_completion(page)
                answer = _read_response(page)
            except AskChatGPTError:
                raise
            except Exception as e:
                # Wrap unexpected Playwright/browser errors in our own type
                # so the LangChain tool layer gets a predictable exception.
                raise AskChatGPTError(f"Unexpected browser automation error: {e}") from e

            # Refresh saved session state in case cookies rotated.
            context.storage_state(path=str(STATE_FILE))
            return answer
        finally:
            # browser.close()
            print("[ask_chatgpt] Browser closed.")


@tool
def ask_chatgpt(prompt: str) -> str:
    """
    Opens chatgpt.com in a browser, starts a new chat, sends `prompt`,
    waits for the assistant to finish responding, and returns the response
    text. Raises AskChatGPTError on failure (login timeout, no response,
    generation timeout, etc.) — callers should catch this and surface a
    clear error to the user rather than letting it propagate silently.
    """
    try:
        return _ask_chatgpt_impl(prompt)
    except AskChatGPTError as e:
        print(f"[ask_chatgpt] ERROR: {e}")
        # Return an error string rather than raising, so a LangChain agent
        # can see the failure as a tool observation and decide what to do
        # next (e.g. retry, tell the user, fall back to another tool).
        return f"ERROR: {e}"


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ask_chatgpt_tool.py '<prompt>'")
        sys.exit(1)

    test_prompt = sys.argv[1]
    result = ask_chatgpt.invoke({"prompt": test_prompt}) if hasattr(ask_chatgpt, "invoke") else _ask_chatgpt_impl(test_prompt)
    print("\n=== RESPONSE ===")
    print(result)