# Plan: Log File Per Session

## Objective
Update the logging infrastructure so that instead of grouping logs by day (e.g., `YYYY-MM-DD_log.log`) or writing to a single static file, **each application execution session generates a unique log file**.

---

## 1. Definition of a "Session"
A session starts when the application initializes (e.g., CLI startup, Web App server start, or test script entry point) and ends when the application terminates.
Each session will be uniquely identified by:
- A timestamp down to the second (or milliseconds): `YYYY-MM-DD_HH-MM-SS`
- An optional unique Session UUID or Process ID (`PID`) to ensure uniqueness if multiple instances start at the exact same second.

**Target Log File Naming Format:**
`Log/session_YYYY-MM-DD_HH-MM-SS_[PID].log`
*(Example: `Log/session_2026-10-08_14-30-12_18492.log`)*

---

## 2. Proposed Changes & Implementation Strategy

### A. Modify `Log/custom_logger.py`
1. **Session ID Generation:**
   - Generate a session timestamp and retrieve `os.getpid()` upon module import or logger initialization.
2. **Dynamic File Handler Setup:**
   - Construct the session-specific log filename: `session_{timestamp}_{pid}.log`.
   - Ensure the `Log/` directory exists.
   - Configure `logging.FileHandler` to write directly to this session file.
3. **Symlink / Latest Pointer (Optional Convenience):**
   - Optionally maintain a symbolic link or a `latest.log` file pointing to the current active session log for quick tailing (`tail -f Log/latest.log`).

### B. Session Lifecycle Management & Cleanup (Optional Enhancement)
- Implement log rotation or retention policy if session logs accumulate (e.g., keep the last 50 session logs or logs from the last N days).

---

## 3. Verification Plan
1. Start the CLI or a test script multiple times.
2. Verify that distinct log files are created in `./Log/` corresponding to each run.
3. Confirm that application logs are correctly captured inside the respective session log file.
