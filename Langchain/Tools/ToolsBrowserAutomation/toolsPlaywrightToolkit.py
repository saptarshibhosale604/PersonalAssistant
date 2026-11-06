# Langchain/Tools/ToolsBrowserAutomation/toolsPlaywrightToolkit.py
# RPI Tactical Browser Tools (custom Playwright toolset, dedicated-thread bridge)
#
# Why custom instead of the prebuilt PlayWrightBrowserToolkit:
#   * the prebuilt toolkit cannot type or press keys, so the agent fell back to guessing URLs
#   * it has no waiting, no bot-check detection, and returns huge unfiltered page text
#
# Design:
#   * ONE dedicated daemon thread owns Playwright (the sync API is bound to the thread that created it)
#   * the browser starts lazily on first use, so no window opens at app startup
#   * every tool returns a short, bounded string and never raises (errors come back as text)
#   * page_snapshot gives the LLM numbered elements, so it no longer has to guess CSS selectors

import atexit
import os
import queue
import threading
from concurrent.futures import Future
from typing import Any, Callable, List

from langchain.tools import tool

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ----------------------------- Config -----------------------------
HEADLESS = False
PROFILE_DIR = os.path.join(os.path.expanduser("~"), ".rpi_browser_profile")  # keeps cookies/logins between runs
CDP_URL = os.environ.get("RPI_BROWSER_CDP_URL", "http://localhost:9222")  # e.g. http://localhost:9222 to drive your own Chrome
NAV_TIMEOUT_MS = 20000
ACTION_TIMEOUT_MS = 8000
TOOL_TIMEOUT_S = 60

_BLOCK_MARKERS = (
    "/sorry/", "captcha", "unusual traffic", "robot check",
    "are you a human", "verify you are human", "access denied",
)


# ------------------------ Dedicated thread ------------------------
class _PlaywrightThread:
    """A single daemon thread that executes every Playwright call, one at a time.

    A daemon thread (instead of ThreadPoolExecutor) stays alive while atexit hooks run,
    which lets us close the browser cleanly on exit.
    """

    def __init__(self) -> None:
        self._jobs: "queue.Queue" = queue.Queue()
        self._thread = threading.Thread(target=self._loop, name="playwright", daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while True:
            job = self._jobs.get()
            if job is None:
                return
            fn, future = job
            if not future.set_running_or_notify_cancel():
                continue
            try:
                future.set_result(fn())
            except BaseException as e:  # noqa: BLE001 - forwarded to the caller
                future.set_exception(e)

    def run(self, fn: Callable[[], Any], timeout: float = TOOL_TIMEOUT_S) -> Any:
        future: Future = Future()
        self._jobs.put((fn, future))
        return future.result(timeout=timeout)

    def stop(self) -> None:
        self._jobs.put(None)


_thread = _PlaywrightThread()

# Browser state (touched only from the Playwright thread)
_pw = None
_browser = None  # only set in CDP mode
_context = None


def _EnsureContext():
    global _pw, _browser, _context
    if _context is not None:
        return _context
    if _pw is None:
        _pw = sync_playwright().start()
    if CDP_URL:
        _browser = _pw.chromium.connect_over_cdp(CDP_URL)
        _context = _browser.contexts[0] if _browser.contexts else _browser.new_context()
    else:
        opts = dict(
            user_data_dir=PROFILE_DIR,
            headless=HEADLESS,
            viewport={"width": 1280, "height": 800},
        )
        try:
            _context = _pw.chromium.launch_persistent_context(channel="chrome", **opts)  # real Chrome if installed
        except Exception:
            _context = _pw.chromium.launch_persistent_context(**opts)  # bundled Chromium
    return _context


def _GetPage():
    """Newest tab of the shared context (follows target=_blank links automatically)."""
    ctx = _EnsureContext()
    page = ctx.pages[-1] if ctx.pages else ctx.new_page()
    page.set_default_timeout(ACTION_TIMEOUT_MS)
    page.set_default_navigation_timeout(NAV_TIMEOUT_MS)
    return page


def _Settle(page) -> None:
    """Best-effort wait so the next tool sees a loaded page instead of an empty/interstitial one."""
    try:
        page.wait_for_load_state("domcontentloaded", timeout=NAV_TIMEOUT_MS)
    except Exception:
        pass
    try:
        page.wait_for_load_state("networkidle", timeout=4000)
    except Exception:
        pass


def _BlockWarning(page) -> str:
    try:
        probe = f"{page.url} {page.title()} {page.inner_text('body', timeout=1500)[:800]}".lower()
    except Exception:
        return ""
    if any(marker in probe for marker in _BLOCK_MARKERS):
        return (
            "\n[BLOCKED] This looks like a bot-check/CAPTCHA page. Do not retry the same URL. "
            "Tell the user, or use another site/search engine (e.g. https://duckduckgo.com/html/?q=...)."
        )
    return ""


def _Describe(page) -> str:
    try:
        title = page.title()
    except Exception:
        title = "?"
    return f"URL: {page.url}\nTitle: {title}{_BlockWarning(page)}"


def _Run(fn: Callable[[], str]) -> str:
    """Run on the Playwright thread; turn any failure into text the agent can react to."""
    try:
        return _thread.run(fn)
    except Exception as e:  # noqa: BLE001
        first = (str(e).strip().splitlines() or [""])[0][:300]
        return f"[ERROR] {type(e).__name__}: {first}"


# --------------------------- JS helpers ---------------------------
_SNAPSHOT_JS = r"""
(args) => {
  const { max, wholePage } = args;
  const sel = 'input:not([type=hidden]), textarea, select, [role="textbox"], [role="radio"], [role="checkbox"], [role="listbox"], a[href], button, [role=button], [role=link], [role=tab], [role=menuitem]';
  const out = [], seen = new Set();

  // Recursively query elements including inside Shadow DOMs
  function queryDeep(root, selector) {
    let results = Array.from(root.querySelectorAll(selector));
    for (const el of root.querySelectorAll('*')) {
      if (el.shadowRoot) {
        results = results.concat(queryDeep(el.shadowRoot, selector));
      }
    }
    return results;
  }

  const elements = queryDeep(document, sel);

  for (const el of elements) {
    if (out.length >= max) break;
    
    try {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      if (!r.width || !r.height || s.visibility === 'hidden' || s.display === 'none') continue;
      if (!wholePage && (r.bottom < -1 || r.top > innerHeight)) continue;
    } catch (e) {}

    const tag = el.tagName ? el.tagName.toLowerCase() : 'element';
    
    // Resolve aria-labelledby to get the actual Google Forms question text
    let labelText = '';
    const ariaLabelledBy = el.getAttribute('aria-labelledby');
    if (ariaLabelledBy) {
      // aria-labelledby can contain multiple space-separated IDs
      const ids = ariaLabelledBy.split(/\s+/);
      for (const idStr of ids) {
        const labelEl = document.getElementById(idStr);
        if (labelEl && labelEl.innerText) {
          labelText += (labelText ? ' ' : '') + labelEl.innerText;
        }
      }
    }

    const text = (labelText || el.innerText || el.value || el.placeholder || el.getAttribute('aria-label') || el.getAttribute('data-initial-value') || el.title || el.alt || '')
      .trim().replace(/\s+/g, ' ').slice(0, 80);

    let href = null;
    if (el.href) { try { const u = new URL(el.href); href = (u.origin + u.pathname).slice(0, 100); } catch (e) {} }

    if (!text && !href && !['input', 'textarea', 'select'].includes(tag) && !el.getAttribute('role')) continue;

    const key = tag + '|' + text + '|' + (href || '');
    if (seen.has(key)) continue;
    seen.add(key);

    const id = out.length + 1;
    try {
      el.setAttribute('data-agent-id', String(id));
    } catch (e) {}
    
    out.push({ id, tag, type: el.type || null, text, href });
  }
  return out;
}
"""

_TEXT_JS = r"""
(selector) => {
  const root = document.querySelector(selector);
  if (!root) return null;
  const noise = root.querySelectorAll('script,style,noscript,nav,header,footer,svg,[role=navigation],[role=banner],#navbar,#navFooter');
  const prev = [];
  noise.forEach(n => { prev.push(n.style.display); n.style.display = 'none'; });
  const text = root.innerText || '';
  noise.forEach((n, i) => { n.style.display = prev[i]; });
  return text.replace(/[ \t]+/g, ' ').replace(/\n{2,}/g, '\n').trim();
}
"""


# ------------------------------ Tools ------------------------------
@tool(
    "navigate_browser",
    description=(
        "Open a full https:// URL and wait for it to load. Returns HTTP status, final URL, title, and a "
        "[BLOCKED] warning if a bot-check/CAPTCHA is shown. Call page_snapshot next."
    ),
)
def NavigateBrowser(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    def _do() -> str:
        page = _GetPage()
        response = page.goto(url, wait_until="domcontentloaded")
        _Settle(page)
        status = response.status if response else "n/a"
        return f"Status: {status}\n{_Describe(page)}"

    return _Run(_do)


@tool("previous_webpage", description="Go back one page in the browser history.")
def PreviousWebpage() -> str:
    def _do() -> str:
        page = _GetPage()
        response = page.go_back(wait_until="domcontentloaded")
        if response is None:
            return "[INFO] No previous page in history."
        _Settle(page)
        return _Describe(page)

    return _Run(_do)


@tool(
    "page_snapshot",
    description=(
        "List the clickable/typeable elements currently in view as numbered items (plus URL and title). "
        "Target one with the selector [data-agent-id='N'] in click_element / fill_input. "
        "Set whole_page=true to include elements below the fold. "
        "Call again after every navigation, click or scroll because numbers change."
    ),
)
def PageSnapshot(whole_page: bool = False, max_items: int = 40) -> str:
    def _do() -> str:
        page = _GetPage()
        limit = max(5, min(int(max_items), 100))
        items = page.evaluate(_SNAPSHOT_JS, {"max": limit, "wholePage": bool(whole_page)})
        lines = [_Describe(page), f"Elements ({len(items)}):"]
        for it in items:
            kind = it["tag"] + (f"[{it['type']}]" if it.get("type") else "")
            target = f" -> {it['href']}" if it.get("href") else ""
            lines.append(f'[{it["id"]}] {kind} "{it["text"]}"{target}')
        if not items:
            lines.append("(nothing interactive in view: try scroll_page, or wait and snapshot again)")
        return "\n".join(lines)

    return _Run(_do)


@tool(
    "click_element",
    description=(
        "Click an element by CSS selector, normally [data-agent-id='N'] from page_snapshot. "
        "Waits for the resulting navigation and follows new tabs. Returns the new URL/title."
    ),
)
def ClickElement(selector: str) -> str:
    def _do() -> str:
        page = _GetPage()
        ctx = page.context
        page.click(selector)
        page.wait_for_timeout(500)  # give a navigation / new tab time to start
        page = ctx.pages[-1]
        page.bring_to_front()
        _Settle(page)
        return f"Clicked {selector}\n{_Describe(page)}"

    return _Run(_do)


@tool(
    "fill_input",
    description=(
        "Type text into an input/textarea (replaces existing text). selector is usually [data-agent-id='N'] "
        "from page_snapshot. Set press_enter=true to submit, e.g. a search box."
    ),
)
def FillInput(selector: str, text: str, press_enter: bool = False) -> str:
    def _do() -> str:
        page = _GetPage()
        page.fill(selector, text)
        if press_enter:
            page.press(selector, "Enter")
            page.wait_for_timeout(500)
            page = page.context.pages[-1]
            _Settle(page)
        done = "and pressed Enter" if press_enter else "(not submitted)"
        return f"Filled {selector} {done}\n{_Describe(page)}"

    return _Run(_do)


@tool("press_key", description="Press a keyboard key on the page, e.g. Enter, Tab, Escape, PageDown.")
def PressKey(key: str) -> str:
    def _do() -> str:
        page = _GetPage()
        page.keyboard.press(key)
        page.wait_for_timeout(300)
        _Settle(page)
        return f"Pressed {key}\n{_Describe(page)}"

    return _Run(_do)


@tool(
    "scroll_page",
    description="Scroll the page up or down by N screens (default 1) to load/reveal more content. Then call page_snapshot.",
)
def ScrollPage(direction: str = "down", screens: float = 1.0) -> str:
    def _do() -> str:
        page = _GetPage()
        height = page.evaluate("window.innerHeight")
        sign = -1 if direction.lower().startswith("u") else 1
        page.evaluate("(dy) => window.scrollBy(0, dy)", sign * height * 0.8 * float(screens))
        page.wait_for_timeout(400)  # allow lazy-loaded content
        return f"Scrolled {'up' if sign < 0 else 'down'} {screens} screen(s). Call page_snapshot to see what is now in view."

    return _Run(_do)


@tool(
    "extract_text",
    description=(
        "Read the page text (or just one CSS selector) with nav/header/footer noise removed, truncated to max_chars. "
        "Use it to read content (listings, prices, articles); use page_snapshot to find things to click."
    ),
)
def ExtractText(selector: str = "body", max_chars: int = 5000) -> str:
    def _do() -> str:
        page = _GetPage()
        limit = max(500, min(int(max_chars), 15000))
        text = page.evaluate(_TEXT_JS, selector)
        if text is None:
            return f"[ERROR] No element matches '{selector}'."
        if len(text) > limit:
            text = text[:limit] + f"\n...[truncated {len(text) - limit} chars: scroll_page, narrow the selector, or raise max_chars]"
        return f"URL: {page.url}\n{text}"

    return _Run(_do)


# ----------------------------- Lifecycle -----------------------------
def _Shutdown() -> None:
    def _close() -> None:
        global _pw, _browser, _context
        try:
            if _browser is not None:
                _browser.close()  # CDP mode: only disconnects, your Chrome stays open
            elif _context is not None:
                _context.close()
        finally:
            _browser = _context = None
            if _pw is not None:
                _pw.stop()
                _pw = None

    try:
        _thread.run(_close, timeout=10)
    except Exception:
        pass
    _thread.stop()


atexit.register(_Shutdown)


def ToolsList() -> List[Any]:
    """Returns the list of tools provided by this module."""
    if not PLAYWRIGHT_AVAILABLE:
        print("[ERROR] playwright is not installed. Run: pip install playwright && playwright install chromium")
        return []
    return [
        NavigateBrowser,
        PreviousWebpage,
        PageSnapshot,
        ClickElement,
        FillInput,
        PressKey,
        ScrollPage,
        ExtractText,
    ]