# Plan: Change Log File Naming Format to Sequential 4-Digit ID & Timestamp

## 1. Objectives
- **New Naming Format:** `session_<unique_4_digit_id>_<timestamp>.log` (Example: `session_0000_2026-10-08_11-08-02.log`).
- **Unique ID Generation:** Instead of using the OS Process ID (`pid`), use a zero-padded 4-digit sequential integer (`0000`, `0001`, `0002`, ...).
- **Persistence / Persistence Check:** Determine the next ID by scanning existing log files in `Log/SessionLog/` or maintaining a simple state/counter mechanism.

---

## 2. Component Analysis (`Log/custom_logger.py`)
Currently, `Log/custom_logger.py` handles session initialization:
```python
session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
pid = os.getpid()
session_filename = f"session_{session_timestamp}_{pid}.log"
log_path = os.path.join(log_dir, session_filename)
```
And updates `latest.log`:
```python
os.symlink(os.path.join("SessionLog", session_filename), latest_path)
```

---

## 3. Implementation Steps (Planned)

### Step A: Determine Sequential 4-Digit ID Logic
To find the next 4-digit ID when a new session starts:
1. Scan `Log/SessionLog/` for existing files matching the pattern `session_<id>_<timestamp>.log` (or `session_*.log`).
2. Extract the 4-digit prefix part (`<id>`) from existing files where it forms a valid integer.
3. Find the maximum existing ID integer, increment it by `1`, and format it as a zero-padded 4-digit string (`f"{next_id:04d}"`).
4. Fallback: If no valid existing session log with a 4-digit ID exists, start from `0000`.

### Step B: Update Session Filename Construction in `Log/custom_logger.py`
Replace:
```python
session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
pid = os.getpid()
session_filename = f"session_{session_timestamp}_{pid}.log"
```
With:
1. Compute `session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")`.
2. Compute `next_id` by inspecting `Log/SessionLog/`.
3. Construct `session_filename = f"session_{next_id}_{session_timestamp}.log"`.

### Step C: Update Symlink / `latest.log` Handling
Ensure references to `session_filename` when creating `latest.log` correctly point to the new filename format inside `SessionLog/`.

### Step D: Verification / Testing Strategy
- Verify that running CLI or app startup correctly generates `session_0000_...log` (if first) or increments properly (`session_0001_...log`, etc.).
- Verify `latest.log` correctly points to the newly formatted session log.
