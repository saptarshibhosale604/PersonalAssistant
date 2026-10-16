# Implementation Plan: Handle Ctrl+C (KeyboardInterrupt) in CLI to Exit Gracefully

## Problem Statement
When running the Personal Assistant CLI in PowerShell (or other terminals), pressing `Ctrl+C` raises a `KeyboardInterrupt` exception. Currently, in `UI/cli.py`, `KeyboardInterrupt` is either unhandled at the outermost loop or caught as a generic exception traceback, resulting in a stack trace:
```
Traceback (most recent call last):
  File "<frozen runpy>", line 203, in _run_module_as_main
...
  File "E:\WORK\PROJECT\git\PersonalAssistant\UI\cli.py", line 598, in Input
    userInput = input("")
KeyboardInterrupt
```

User expectation: Even if the user presses `Ctrl+C`, the personal assistant should exit cleanly (just like `/exit`), displaying exit messages and closing properly.

---

## Proposed Changes

### 1. `UI/cli.py`
- Wrap `Input()` or the inner REPL main loop / `input()` call in `try...except KeyboardInterrupt:` blocks.
- Specifically, inside `Input()` where `userInput = input("")` is called (and potentially `sys.stdin.read()`), catch `KeyboardInterrupt`.
- Additionally, wrap the `while True:` REPL loop in `UI/cli.py` with `try...except KeyboardInterrupt:`.
- When `KeyboardInterrupt` is caught, perform the exact graceful exit sequence currently used in `/exit`:
  ```python
  print("\nExiting Personal Assistant CLI...")
  print(f"Log file: {os.path.abspath(log_path)}")
  sys.exit(0)
  ```

---

## Step-by-Step Implementation Steps
1. Locate `Input()` function in `UI/cli.py`:
   - Wrap `input("")` inside `try...except KeyboardInterrupt:`.
   - Ensure `sys.stdin.read()` in `"multi"` mode also handles `KeyboardInterrupt`.
2. Locate the `while True:` loop at the bottom of `UI/cli.py`:
   - Wrap the loop or `Main()` call with `except KeyboardInterrupt:`.
3. Test by running `python UI/cli.py` and pressing `Ctrl+C`.
