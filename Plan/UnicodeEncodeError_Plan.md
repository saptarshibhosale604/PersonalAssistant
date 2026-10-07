# Plan to fix UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f44b'

## Problem
The logging call `logger.info(f"[AgentOutput] {response}")` writes a string containing the emoji 👋 (U+1F44B) to a stream encoded with `cp1252` (Windows‑Western). The codec does not know how to map that Unicode code‑point, raising `UnicodeEncodeError`.

## Goal
Make the logging pipeline able to handle Unicode characters (especially emojis) without crashing.

---

## 1. Diagnose the exact logging configuration
| Item | What to look for |
|------|------------------|
| **Logger creation** | `log_utils.py` line 15 wraps the function; locate where the logger is instantiated (`logging.getLogger(...)`). |
| **Handler(s)** | Check which handler(s) are attached (StreamHandler, FileHandler, etc.). |
| **Handler encoding** | For a `StreamHandler`, the default `encoding` is often `None` → uses `sys.stdout.encoding`, which on Windows is `cp1252`. For a `FileHandler`, the encoding can be set explicitly via the `encoding` parameter. |
| **Formatter** | Verify the formatter string; the problem is the *write* step, not the format. |

**Action:** Add a quick debug print or inspect the logger object (`logger.handlers`, `handler.encoding`) to confirm the encoding source.

---

## 2. Choose one of the following remedial approaches

### A. Force the handler to use UTF‑8 encoding
- **If it’s a `StreamHandler`**: create it with `encoding='utf-8'`.
  ```python
  handler = logging.StreamHandler(sys.stdout, encoding='utf-8')
  logger.addHandler(handler)
  ```
- **If it’s a `FileHandler`**: supply `encoding='utf-8'` when constructing the handler.

*Result:* The stream will accept any Unicode code‑point, including 👋.

### B. Use `errors='replace'` (or `errors='ignore'`) when creating the handler
- Example: `logging.StreamHandler(sys.stdout, errors='replace')`
- This tells the codec to replace any unmappable character with a placeholder (`?`) instead of raising an exception.

*Result:* Logging will not crash, but emojis may appear as `?` or a replacement character.

### C. Strip / replace non‑ASCII characters before logging
- Prior to the `logger.info` call, scrub the string:
  ```python
  safe_response = response.encode('cp1252', errors='replace').decode('cp1252')
  # or simply remove emojis with a regex
  import re
  safe_response = re.sub(r'\p{Emoji}', '', response)   # Python 3.12+ \p{Emoji}
  ```
- Then log `safe_response`.

*Result:* The log will contain only characters the codec can handle; emojis are omitted.

### D. Switch to a Rich/third‑party logger that natively supports Unicode
- Libraries such as **rich**, **loguru**, or **structlog** set up a UTF‑8‑compatible handler by default and render emojis nicely in the console.

*Result:* Minimal code change; just redirect the existing logger to a Rich handler.

---

## 3. Implement the chosen fix (high‑level steps)

1. **Locate the logger setup** in `log_utils.py` (or whichever module configures logging).  
2. **Add/override a handler** with `encoding='utf-8'` **or** set `errors='replace'`.
   - If using `FileHandler`, pass the encoding when constructing it.  
3. **If opting for character scrubbing**, insert a small utility function that strips or replaces emojis before the `logger.info` call.  
4. **If switching to a different logger** (e.g., `loguru`), import it and replace the `logging.getLogger(...)` call, ensuring the rest of the code still calls `logger.info(...)`.  
5. **Run a quick test**: feed the same user input that triggered the error and verify that the console output no longer raises `UnicodeEncodeError`.

---

## 4. Verify the fix

| Test case | Expected outcome |
|-----------|------------------|
| Re‑run the assistant with a prompt that invokes the emoji‑containing response (`👋`) | Log line `[AgentOutput] Hi there! 👋 How can I help you today?` appears without exception. |
| Check that other Unicode characters (e.g., accented letters, CJK) also render correctly. | No `UnicodeEncodeError` for any character. |
| Ensure existing log files (if any) are not corrupted. | File contents remain valid; any previously written emojis are preserved if UTF‑8 encoding was used. |

---

## 5. Documentation / code comment (optional but helpful)

- Add a brief comment next to the logger configuration explaining why `encoding='utf-8'` (or `errors='replace'`) is used, e.g.:

  ```python
  # Use utf-8 encoding to support emojis and other Unicode characters in logs.
  handler = logging.StreamHandler(sys.stdout, encoding='utf-8')
  ```

---

### Summary
1. **Identify** the handler’s encoding (cp1252).  
2. **Choose** a strategy: force UTF‑8 on the handler, use `errors='replace'`, strip emojis before logging, or replace the logger with a Unicode‑aware library (rich/loguru).  
3. **Apply** the selected change in the logging setup code.  
4. **Test** with the original input to confirm the `UnicodeEncodeError` is gone.

Following this plan will resolve the traceback without altering the core agent logic, and the assistant will be able to log (and display) emoji‑rich messages safely.