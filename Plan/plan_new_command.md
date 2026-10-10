# Plan: Implementing the `/new` Command in CLI (`UI/cli.py`)

## 📌 Objective
Implement the `/new` command in the Personal Assistant CLI so that typing `/new` resets the session and cleanly restarts the CLI process (`python -m UI.cli`) without causing infinite recursion or nested subprocess loops.

---

## 🛠️ Implementation Details

### 1. The Infinite Loop Risk
Directly calling `python -m UI.cli` or recursively invoking `Main()` inside the running Python process can cause an infinite loop or improper state accumulation. 

### 2. Solution: Process Replacement (`os.execv`)
To emulate starting `python -m UI.cli` fresh in the same terminal window while terminating the current thread/process cleanly:
- Use Python's built-in `os.execv()` combined with `sys.executable`.
- `os.execv` replaces the current process image with a new Python interpreter running `-m UI.cli` under the exact same process ID (PID) and terminal context.

---

## 📝 Code Change in `UI/cli.py`

Inside `BasicCmds02(userInput: str)`:

```python
    # --------------------------------------------------
    # New Session - Restart CLI Process
    # --------------------------------------------------

    elif command == "/new":
        print("Starting new session (/new)...")
        global THREAD_ID, _os_prefix_added
        THREAD_ID += 1
        _os_prefix_added = False  # Reset OS prefix flag for new session
        
        # Cleanly restart python -m UI.cli replacing current process
        python_executable = sys.executable
        os.execv(python_executable, [python_executable, "-m", "UI.cli"])
        return True
```

---

## ✅ Verification Steps
1. Run the CLI.
2. Type `/new`.
3. Verify that the current session terminates and a brand new CLI instance starts cleanly in the terminal.
