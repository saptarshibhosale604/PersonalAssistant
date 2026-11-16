# Langchain/Tools/ToolsBrowserAutomation/toolsPlaywrightToolkit.py
# RPI Tactical Browser Tools (custom Playwright toolset, dedicated-thread bridge)
#
# v2 changes (form-filling fixes):
#   * snapshot skips off-screen honeypot/autofill-decoy inputs (left:-10000000px, readonly)
#   * snapshot clears stale data-agent-id attributes first (ids were never removed -> duplicates)
#   * snapshot no longer de-duplicates form controls (empty-label inputs/switches used to vanish)
#   * snapshot scopes itself to an open modal dialog (+ its open dropdown popups)
#   * snapshot shows label / id / name / value / readonly / disabled / checked for every control
#   * errors keep Playwright's "Call log" (e.g. "element is not editable") instead of only line 1
#   * fill_input / click_element pre-check the target and fail fast with an actionable message
#   * fill_input verifies the value after typing
#   * new tools: fill_by_label, select_dropdown_option (antd/React custom selects), click_text
#   * scroll_page scrolls the open modal when there is one

import atexit
import os
import queue
import re
import threading
import time
from concurrent.futures import Future
from typing import Any, Callable, List

from langchain.tools import tool

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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
FILL_TIMEOUT_MS = 4000      # fill is pre-checked, so a short timeout is enough
TOOL_TIMEOUT_S = 60

# Retry configuration for TargetClosedError
MAX_RETRIES = 3
RETRY_DELAY_S = 2
CHROME_EXECUTABLE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
CHROME_USER_DATA_DIR = r"E:\PlaywrightChromeProfile"
CHROME_DEBUG_PORT = 9222

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


def _LaunchChromeWithDebugging():
    """Launch Chrome with remote debugging enabled on port 9222."""
    import subprocess
    import time

    # Kill any existing Chrome processes on the debug port
    try:
        subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True, timeout=5)
    except Exception:
        pass

    time.sleep(1)

    # Launch Chrome with debugging
    chrome_args = [
        CHROME_EXECUTABLE,
        f"--remote-debugging-port={CHROME_DEBUG_PORT}",
        f"--user-data-dir={CHROME_USER_DATA_DIR}",
        "--no-first-run",
        "--no-default-browser-check"
    ]

    try:
        subprocess.Popen(chrome_args, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        print(f"[INFO] Launched Chrome with remote debugging on port {CHROME_DEBUG_PORT}")
    except Exception as e:
        print(f"[ERROR] Failed to launch Chrome: {e}")
        return False

    # Wait for Chrome to be ready
    for _ in range(15):
        try:
            import requests
            response = requests.get(f"http://localhost:{CHROME_DEBUG_PORT}/json/version", timeout=2)
            if response.status_code == 200:
                print(f"[INFO] Chrome debugging port {CHROME_DEBUG_PORT} is ready")
                return True
        except Exception:
            time.sleep(1)

    print(f"[ERROR] Chrome debugging port {CHROME_DEBUG_PORT} not ready after 15 seconds")
    return False


def _ResetBrowserState():
    """Reset all browser state variables."""
    global _pw, _browser, _context
    try:
        if _browser is not None:
            _browser.close()
    except Exception:
        pass
    try:
        if _context is not None:
            _context.close()
    except Exception:
        pass
    try:
        if _pw is not None:
            _pw.stop()
    except Exception:
        pass
    _pw = _browser = _context = None


def _EnsureContext():
    global _pw, _browser, _context

    # If context exists and is valid, return it
    if _context is not None:
        try:
            # Quick health check
            _ = _context.pages
            return _context
        except Exception:
            # Context is dead, reset and retry
            _ResetBrowserState()

    # Retry loop with Chrome relaunch
    for attempt in range(MAX_RETRIES):
        try:
            if _pw is None:
                _pw = sync_playwright().start()

            if CDP_URL:
                # Try to connect to existing Chrome
                try:
                    _browser = _pw.chromium.connect_over_cdp(CDP_URL)
                    _context = _browser.contexts[0] if _browser.contexts else _browser.new_context()
                    # Test the connection
                    _ = _context.pages
                    return _context
                except Exception as e:
                    error_msg = str(e).lower()
                    if "targetclosed" in error_msg or "connection refused" in error_msg or "connect" in error_msg:
                        print(f"[WARN] CDP connection failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                        if attempt < MAX_RETRIES - 1:
                            print(f"[INFO] Relaunching Chrome with debugging...")
                            if _LaunchChromeWithDebugging():
                                time.sleep(RETRY_DELAY_S)
                                continue
                    raise
            else:
                # Launch persistent context directly
                opts = dict(
                    user_data_dir=PROFILE_DIR,
                    headless=HEADLESS,
                    viewport={"width": 1280, "height": 800},
                )
                try:
                    _context = _pw.chromium.launch_persistent_context(channel="chrome", **opts)
                except Exception:
                    _context = _pw.chromium.launch_persistent_context(**opts)
                return _context

        except Exception as e:
            error_msg = str(e).lower()
            if "targetclosed" in error_msg and attempt < MAX_RETRIES - 1:
                print(f"[WARN] TargetClosedError (attempt {attempt + 1}/{MAX_RETRIES}), relaunching Chrome...")
                _ResetBrowserState()
                if _LaunchChromeWithDebugging():
                    time.sleep(RETRY_DELAY_S)
                    continue
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(RETRY_DELAY_S)

    raise Exception("Failed to establish browser context after all retries")


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


def _FormatError(e: BaseException) -> str:
    """Keep the useful part of Playwright errors.

    Playwright puts the real reason ("element is not editable", "intercepts pointer events",
    "element is not enabled") in the *call log* below line 1. Returning only line 1 hid it from the agent.
    """
    lines = [ln.strip() for ln in str(e).strip().splitlines() if ln.strip()]
    if not lines:
        return type(e).__name__
    head = lines[0][:250]
    log_start = next((i for i, ln in enumerate(lines) if ln.startswith("Call log")), None)
    if log_start is None:
        return head
    seen, keep = set(), []
    for ln in lines[log_start + 1:]:
        if ln not in seen:
            seen.add(ln)
            keep.append(ln[:220])
    return head + "\n" + "\n".join(keep[-6:])


def _Run(fn: Callable[[], str]) -> str:
    """Run on the Playwright thread; turn any failure into text the agent can react to."""
    try:
        return _thread.run(fn)
    except Exception as e:  # noqa: BLE001
        return f"[ERROR] {type(e).__name__}: {_FormatError(e)}"


# --------------------------- JS helpers ---------------------------
_SNAPSHOT_JS = r"""
(args) => {
  const { max, wholePage } = args;
  const sel = 'input:not([type=hidden]), textarea, select, [role="textbox"], [role="radio"], [role="checkbox"], [role="switch"], [role="combobox"], [role="listbox"], a[href], button, [role=button], [role=link], [role=tab], [role=menuitem], [role=option]';
  const CONTROLS = 'input:not([type=hidden]):not([readonly]):not([disabled]), textarea:not([readonly]):not([disabled]), select:not([disabled])';

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

  // 1) Remove ids from earlier snapshots. Otherwise elements that are not in this snapshot keep an
  //    old number and the same [data-agent-id='N'] can match two elements.
  for (const el of queryDeep(document, '[data-agent-id]')) el.removeAttribute('data-agent-id');

  const isShown = (el) => {
    try {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
    } catch (e) { return false; }
  };

  // 2) If a modal is open, only list the modal + open dropdown popups (they render in portals).
  const modals = queryDeep(document, '[aria-modal="true"], dialog[open]').filter(isShown);
  let roots = [document];
  let scope = 'page';
  if (modals.length) {
    const popups = queryDeep(document, '.ant-select-dropdown, .ant-dropdown, [role=listbox], [role=menu]').filter(isShown);
    roots = modals.concat(popups);
    scope = 'modal';
  }
  const elements = Array.from(new Set(roots.flatMap(r => queryDeep(r, sel))));

  function labelOf(el, role) {
    let t = '';
    if (el.labels && el.labels.length) t = Array.from(el.labels).map(l => l.innerText).join(' ');
    if (!t) {
      const ariaLabelledBy = el.getAttribute('aria-labelledby');
      if (ariaLabelledBy) {
        for (const idStr of ariaLabelledBy.split(/\s+/)) {
          const labelEl = document.getElementById(idStr);
          if (labelEl && labelEl.innerText) t += (t ? ' ' : '') + labelEl.innerText;
        }
      }
    }
    if (!t) t = el.getAttribute('aria-label') || '';
    if (!t && ['switch', 'checkbox', 'radio'].includes(role)) {
      // switches have no text of their own: use the nearby caption ("Eviction ...")
      let p = el.parentElement;
      for (let i = 0; i < 3 && p && !t; i++, p = p.parentElement) {
        const x = (p.innerText || '').trim();
        if (x && x.length < 100) t = x;
      }
    }
    if (!t) {
      // <label> that is not wired with for/id: climb until the container holds more than this one control
      let p = el.parentElement;
      for (let i = 0; i < 7 && p && p !== document.body; i++, p = p.parentElement) {
        if (p.querySelectorAll(CONTROLS).length > 1) break;
        const lab = p.querySelector('label');
        if (lab && lab.innerText.trim()) { t = lab.innerText; break; }
      }
    }
    return t.trim().replace(/\s+/g, ' ').slice(0, 80);
  }

  const out = [], seen = new Set();

  for (const el of elements) {
    if (out.length >= max) break;

    try {
      const r = el.getBoundingClientRect();
      const s = getComputedStyle(el);
      if (!r.width || !r.height || s.visibility === 'hidden' || s.display === 'none') continue;
      // Off-screen horizontally = autofill honeypot / decoy (e.g. position:absolute; left:-10000000px)
      if (r.right <= 0 || r.left >= innerWidth) continue;
      if (!wholePage && (r.bottom < -1 || r.top > innerHeight)) continue;
    } catch (e) {}

    const tag = el.tagName ? el.tagName.toLowerCase() : 'element';
    const role = el.getAttribute('role') || '';
    const isInput = ['input', 'textarea', 'select'].includes(tag);
    const isField = isInput || ['textbox', 'switch', 'checkbox', 'radio', 'combobox', 'listbox'].includes(role);

    let text;
    if (isField) {
      text = (labelOf(el, role) || el.placeholder || el.getAttribute('aria-label') || el.getAttribute('name') || '')
        .trim().replace(/\s+/g, ' ').slice(0, 80);
    } else {
      text = (el.innerText || el.getAttribute('aria-label') || el.title || el.alt || '')
        .trim().replace(/\s+/g, ' ').slice(0, 80);
    }

    let href = null;
    if (el.href) { try { const u = new URL(el.href); href = (u.origin + u.pathname).slice(0, 100); } catch (e) {} }

    if (!text && !href && !isField && !role) continue;

    // De-duplicate only plain links/buttons. Form controls are never merged
    // (two empty-label inputs used to collapse into one).
    if (!isField) {
      const key = tag + '|' + text + '|' + (href || '');
      if (seen.has(key)) continue;
      seen.add(key);
    }

    // current value / state
    const itype = el.type || null;
    let value = null;
    if (isInput && !['checkbox', 'radio', 'button', 'submit'].includes(itype)) {
      value = itype === 'password' ? (el.value ? '********' : '') : String(el.value || '').slice(0, 60);
    }
    const antSel = el.closest ? el.closest('.ant-select') : null;
    if (antSel) {
      const si = antSel.querySelector('.ant-select-selection-item');
      if (si) value = (si.innerText || '').trim().slice(0, 60);
    }
    let checked = null;
    if (isInput && ['checkbox', 'radio'].includes(itype)) checked = !!el.checked;
    else if (el.getAttribute('aria-checked') !== null) checked = el.getAttribute('aria-checked') === 'true';

    const id = out.length + 1;
    try {
      el.setAttribute('data-agent-id', String(id));
    } catch (e) {}

    out.push({
      id, tag, type: itype, role, text, href, value, checked,
      elId: el.id || '',
      name: el.getAttribute('name') || '',
      placeholder: (el.placeholder || '').slice(0, 40),
      readonly: !!el.readOnly,
      disabled: !!(el.disabled || el.getAttribute('aria-disabled') === 'true'),
    });
  }
  return { items: out, scope };
}
"""

_STATE_JS = r"""
(el) => {
  const r = el.getBoundingClientRect();
  const s = getComputedStyle(el);
  return {
    tag: el.tagName.toLowerCase(),
    hidden: !r.width || !r.height || s.visibility === 'hidden' || s.display === 'none',
    offscreen: r.right <= 0 || r.left >= innerWidth,
    readonly: !!el.readOnly,
    disabled: !!(el.disabled || el.getAttribute('aria-disabled') === 'true'),
    role: el.getAttribute('role') || '',
    id: el.id || '',
    name: el.getAttribute('name') || '',
  };
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

_SCROLL_JS = r"""
(dy) => {
  // when a modal is open the page body is usually overflow:hidden; scroll the modal instead
  const starts = Array.from(document.querySelectorAll('.ant-modal-wrap, [aria-modal="true"]'));
  for (const start of starts) {
    let x = start;
    while (x && x !== document.documentElement) {
      if (x.scrollHeight > x.clientHeight + 4 && /(auto|scroll)/.test(getComputedStyle(x).overflowY)) {
        x.scrollBy(0, dy);
        return 'modal';
      }
      x = x.parentElement;
    }
  }
  window.scrollBy(0, dy);
  return 'page';
}
"""


# ------------------------- Shared helpers -------------------------
def _Evaluate(page, js: str, arg: Any, tries: int = 3) -> Any:
    """page.evaluate that survives 'Execution context was destroyed' (navigation in flight)."""
    last = None
    for _ in range(tries):
        try:
            return page.evaluate(js, arg)
        except Exception as e:  # noqa: BLE001
            msg = str(e)
            if "context was destroyed" in msg or "navigation" in msg.lower():
                last = e
                _Settle(page)
                continue
            raise
    raise last  # type: ignore[misc]


def _CollectSnapshot(page, whole_page: bool, limit: int) -> dict:
    return _Evaluate(page, _SNAPSHOT_JS, {"max": limit, "wholePage": bool(whole_page)})


def _FormatItem(it: dict) -> str:
    kind = it["tag"] + (f"[{it['type']}]" if it.get("type") else "")
    if it.get("role"):
        kind += f" role={it['role']}"
    line = f'[{it["id"]}] {kind} "{it["text"]}"'
    extras = []
    if it.get("elId"):
        extras.append(f"#{it['elId']}")
    if it.get("name"):
        extras.append(f"name={it['name']}")
    if it.get("value"):
        extras.append(f"value={it['value']!r}")
    if it.get("checked") is not None:
        extras.append("checked" if it["checked"] else "unchecked")
    if it.get("readonly"):
        extras.append("READONLY")
    if it.get("disabled"):
        extras.append("DISABLED")
    if extras:
        line += " (" + ", ".join(extras) + ")"
    if it.get("href"):
        line += f" -> {it['href']}"
    return line


def _CheckTarget(loc, need_editable: bool = False, action: str = "click") -> str:
    """Return an actionable error string if the target can't be used, else ''."""
    n = loc.count()
    if n == 0:
        return (
            "[ERROR] No element matches that selector. data-agent-id numbers are reassigned on every "
            "page_snapshot, so call page_snapshot again and use the fresh number "
            "(or a stable selector such as #some-id / [name=...])."
        )
    st = loc.first.evaluate(_STATE_JS, timeout=2000)
    if st["hidden"]:
        return "[ERROR] The target element is not visible. Call page_snapshot and pick a visible one."
    if st["offscreen"]:
        return (
            "[ERROR] The target is positioned off-screen. That is typically an autofill honeypot/decoy input, "
            "not the real field. Do NOT use it. Call page_snapshot and use the visible field with the right label."
        )
    if st["disabled"]:
        return (
            "[ERROR] The target is disabled. For a submit/Next button this usually means a required field "
            "is still empty or invalid: fill the form fields first, then retry."
        )
    if need_editable and st["readonly"]:
        if st["role"] == "combobox":
            return (
                "[ERROR] This is a custom dropdown (readonly combobox), you can't type into it. "
                "Use select_dropdown_option(field, option_text) instead."
            )
        return (
            "[ERROR] The target is READONLY. It is either a decoy or a custom widget. "
            "Call page_snapshot and use another field (look for one without READONLY and with the right label)."
        )
    return ""


def _AfterAction(page, ctx):
    page.wait_for_timeout(500)  # give a navigation / new tab time to start
    page = ctx.pages[-1]
    page.bring_to_front()
    _Settle(page)
    return page


def _FillSelector(page, selector: str, text: str, press_enter: bool) -> str:
    loc = page.locator(selector)
    problem = _CheckTarget(loc, need_editable=True)
    if problem:
        return problem
    target = loc.first
    try:
        target.fill(text, timeout=FILL_TIMEOUT_MS)
    except Exception:  # noqa: BLE001 - fallback for inputs that reject .fill()
        target.click(timeout=3000)
        page.keyboard.press("Control+A")
        page.keyboard.type(text, delay=15)

    try:
        actual = target.input_value(timeout=1500)
    except Exception:  # noqa: BLE001
        actual = None
    note = ""
    if actual is not None and actual != text:
        note = (
            f"\n[WARN] Field now contains {actual!r} but expected {text!r}. "
            "The page may have reformatted or cleared it: call page_snapshot to check."
        )
    if press_enter:
        page.press(selector, "Enter")
        page.wait_for_timeout(500)
        page = page.context.pages[-1]
        _Settle(page)
    done = "and pressed Enter" if press_enter else "(not submitted)"
    shown = f" Field now shows: {actual!r}." if actual is not None else ""
    return f"Filled {selector} {done}.{shown}{note}\n{_Describe(page)}"


def _FindItemByLabel(page, label: str, predicate):
    data = _CollectSnapshot(page, True, 100)
    want = label.strip().lower()
    for it in data["items"]:
        if predicate(it) and want in (it.get("text") or "").lower():
            return it, data["items"]
    return None, data["items"]


def _Scope(page):
    """Open modal if there is one, else the whole page."""
    modal = page.locator('[aria-modal="true"]:visible')
    return modal.last if modal.count() else page


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
        "List the clickable/typeable elements as numbered items (plus URL and title). Form fields show their "
        "label, #id, name, current value and flags (READONLY, DISABLED, checked). If a modal dialog is open, "
        "ONLY the dialog is listed. Target an item with [data-agent-id='N'] in click_element / fill_input. "
        "Numbers are reassigned on every call, so call it again after every navigation, click, fill or scroll. "
        "Set whole_page=true to include elements below the fold. "
        "For forms prefer fill_by_label / select_dropdown_option / click_text; they don't need numbers."
    ),
)
def PageSnapshot(whole_page: bool = False, max_items: int = 40) -> str:
    def _do() -> str:
        page = _GetPage()
        limit = max(5, min(int(max_items), 100))
        data = _CollectSnapshot(page, whole_page, limit)
        items = data["items"]
        lines = [_Describe(page)]
        if data.get("scope") == "modal":
            lines.append(
                "Scope: an open modal dialog. Elements behind it are hidden from this list. "
                "Finish or cancel the dialog first."
            )
        lines.append(f"Elements ({len(items)}):")
        lines.extend(_FormatItem(it) for it in items)
        if not items:
            lines.append("(nothing interactive in view: try scroll_page, or wait and snapshot again)")
        return "\n".join(lines)

    return _Run(_do)


@tool(
    "click_element",
    description=(
        "Click an element by CSS selector, normally [data-agent-id='N'] from page_snapshot. "
        "Fails fast with a reason if the element is disabled/hidden. "
        "Waits for the resulting navigation and follows new tabs. Returns the new URL/title."
    ),
)
def ClickElement(selector: str) -> str:
    def _do() -> str:
        page = _GetPage()
        ctx = page.context
        loc = page.locator(selector)
        problem = _CheckTarget(loc, need_editable=False)
        if problem:
            return problem
        loc.first.click()
        page = _AfterAction(page, ctx)
        return f"Clicked {selector}\n{_Describe(page)}"

    return _Run(_do)


@tool(
    "click_text",
    description=(
        "Click a visible button/link/tab/menu item/option by its text, e.g. click_text('Next'), "
        "click_text('Free'), click_text('Google Cloud Platform'). If a modal is open, only the modal is searched. "
        "No page_snapshot number needed. Set exact=true to match the whole text."
    ),
)
def ClickText(text: str, exact: bool = False) -> str:
    def _do() -> str:
        page = _GetPage()
        ctx = page.context
        body = re.escape(text.strip())
        pat = re.compile(f"^\\s*{body}\\s*$" if exact else body, re.I)
        scope = _Scope(page)
        getters = (
            lambda: scope.get_by_role("button", name=pat),
            lambda: scope.get_by_role("link", name=pat),
            lambda: scope.get_by_role("tab", name=pat),
            lambda: scope.get_by_role("menuitem", name=pat),
            lambda: scope.get_by_role("radio", name=pat),
            lambda: scope.locator(".ant-select-item-option, .ant-segmented-item").filter(has_text=pat),
            lambda: scope.get_by_text(pat),
        )
        for get in getters:
            loc = get()
            if loc.count() == 0:
                continue
            target = loc.first
            try:
                if target.is_disabled():
                    return (
                        f"[ERROR] '{text}' is disabled. A required form field is probably still empty/invalid: "
                        "run page_snapshot and fill the missing fields first."
                    )
            except Exception:  # noqa: BLE001
                pass
            target.click()
            page = _AfterAction(page, ctx)
            return f"Clicked text {text!r}\n{_Describe(page)}"
        return f"[ERROR] No visible element with text {text!r}. Call page_snapshot to see what is available."

    return _Run(_do)


@tool(
    "fill_input",
    description=(
        "Type text into an input/textarea (replaces existing text). selector is usually [data-agent-id='N'] "
        "from page_snapshot (or #id / [name=...]). Refuses READONLY / DISABLED / off-screen targets with an "
        "explanation, and reports the value the field holds afterwards. Set press_enter=true to submit."
    ),
)
def FillInput(selector: str, text: str, press_enter: bool = False) -> str:
    def _do() -> str:
        page = _GetPage()
        return _FillSelector(page, selector, text, press_enter)

    return _Run(_do)


@tool(
    "fill_by_label",
    description=(
        "Fill a text field by its visible label, e.g. fill_by_label('Name', 'pi-ip'). Skips hidden decoy / "
        "readonly / disabled inputs automatically. Best tool for forms: no page_snapshot numbers needed. "
        "Does NOT work for dropdowns (use select_dropdown_option) or switches (use click_text / click_element)."
    ),
)
def FillByLabel(label: str, text: str, press_enter: bool = False) -> str:
    def _do() -> str:
        page = _GetPage()
        textual = lambda it: (  # noqa: E731
            it["tag"] in ("input", "textarea")
            and not it.get("readonly")
            and not it.get("disabled")
            and it.get("type") not in ("checkbox", "radio", "button", "submit", "file")
        )
        it, items = _FindItemByLabel(page, label, textual)
        if it is None:
            fields = [f"{i['text']!r}" for i in items if textual(i)]
            return (
                f"[ERROR] No editable field labelled {label!r}. Editable fields right now: "
                f"{', '.join(fields) if fields else '(none)'}"
            )
        return _FillSelector(page, f"[data-agent-id='{it['id']}']", text, press_enter)

    return _Run(_do)


@tool(
    "select_dropdown_option",
    description=(
        "Choose an option in a dropdown / select / combobox, including custom React/antd selects that can't be "
        "typed into. field = the label text (e.g. 'Primary Region') or a selector (#id, [data-agent-id='N']). "
        "option_text = text of the option (substring, case-insensitive), e.g. 'us-east-1' or 'Mumbai'. "
        "Scrolls long (virtualised) lists. If the dialog has provider tabs (AWS / GCP), click_text the tab first."
    ),
)
def SelectDropdownOption(field: str, option_text: str) -> str:
    def _do() -> str:
        page = _GetPage()
        if field.strip().startswith(("[", "#", ".")):
            trigger = page.locator(field).first
            tag = trigger.evaluate("el => el.tagName.toLowerCase()", timeout=2000)
        else:
            is_select = lambda it: (  # noqa: E731
                (it["tag"] == "select" or it.get("role") in ("combobox", "listbox")) and not it.get("disabled")
            )
            it, items = _FindItemByLabel(page, field, is_select)
            if it is None:
                names = [f"{i['text']!r}" for i in items if is_select(i)]
                return (
                    f"[ERROR] No dropdown labelled {field!r}. Dropdowns right now: "
                    f"{', '.join(names) if names else '(none)'}"
                )
            trigger = page.locator(f"[data-agent-id='{it['id']}']").first
            tag = it["tag"]

        pat = re.compile(re.escape(option_text.strip()), re.I)

        if tag == "select":  # native <select>
            trigger.select_option(label=pat.pattern)  # exact label first
            return f"Selected {option_text!r} in native select {field!r}\n{_Describe(page)}"

        trigger.click(timeout=3000)
        page.wait_for_timeout(300)

        option_css = (
            ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option",
            "[role=listbox]:visible [role=option]",
            "[role=menu]:visible [role=menuitem]",
            "[role=option]:visible",
        )
        for _ in range(12):
            for css in option_css:
                opt = page.locator(css).filter(has_text=pat)
                if opt.count():
                    opt.first.click(timeout=3000)
                    page.wait_for_timeout(300)
                    return (
                        f"Selected {option_text!r} in {field!r}. "
                        f"Call page_snapshot to confirm the value.\n{_Describe(page)}"
                    )
            # virtualised lists render only ~9 rows: scroll the open list and look again
            holder = page.locator(".rc-virtual-list-holder:visible, [role=listbox]:visible")
            if holder.count() == 0:
                break
            box = holder.last.bounding_box()
            if not box:
                break
            page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
            page.mouse.wheel(0, 180)
            page.wait_for_timeout(200)

        try:
            visible = page.locator(".ant-select-item-option:visible, [role=option]:visible").all_inner_texts()
        except Exception:  # noqa: BLE001
            visible = []
        page.keyboard.press("Escape")
        shown = "; ".join(t.replace("\n", " ") for t in visible[:12])
        return f"[ERROR] Option {option_text!r} not found in {field!r}. Options seen: {shown or '(none)'}"

    return _Run(_do)


@tool("press_key", description=(
    "Press a keyboard key on the page, e.g. Enter, Tab, Escape, PageDown. "
    "Do NOT use it to type words or fill forms (use fill_input / fill_by_label): keys go to whatever has focus."
))
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
    description=(
        "Scroll the page (or the open modal dialog) up or down by N screens (default 1) to load/reveal more "
        "content. Then call page_snapshot."
    ),
)
def ScrollPage(direction: str = "down", screens: float = 1.0) -> str:
    def _do() -> str:
        page = _GetPage()
        height = page.evaluate("window.innerHeight")
        sign = -1 if direction.lower().startswith("u") else 1
        target = page.evaluate(_SCROLL_JS, sign * height * 0.8 * float(screens))
        page.wait_for_timeout(400)  # allow lazy-loaded content
        return (
            f"Scrolled {target} {'up' if sign < 0 else 'down'} {screens} screen(s). "
            "Call page_snapshot to see what is now in view."
        )

    return _Run(_do)


@tool(
    "extract_text",
    description=(
        "Read the page text (or just one CSS selector) with nav/header/footer noise removed, truncated to max_chars. "
        "Use it to read content (listings, prices, articles, tokens/keys); use page_snapshot to find things to click."
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
        ClickText,
        FillInput,
        FillByLabel,
        SelectDropdownOption,
        PressKey,
        ScrollPage,
        ExtractText,
    ]