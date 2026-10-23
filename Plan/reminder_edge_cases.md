# Edge Cases and Mitigations for Reminder System

1. **Timezone Discrepancies**
   - **Risk:** Container system time (`UTC`) differing from local system time (`IST`/`EST`), causing reminders to trigger at the wrong hour.
   - **Mitigation:** Enforce local system timezone (`datetime.now()`) consistently across both tool scheduling and the dispatcher daemon.

2. **Ambiguous Natural Language Time**
   - **Risk:** User specifies ambiguous times like "at 3" without designating AM/PM or 24-hour format.
   - **Mitigation:** Clear tool docstring prompting the LLM agent to clarify or assume logical future context (e.g., if current time is 10 AM, "at 3" means 3 PM).

3. **WAHA Session Offline or Disconnected**
   - **Risk:** WhatsApp Web session disconnected in the WAHA container, causing HTTP requests to fail.
   - **Mitigation:** Wrap WAHA API calls in `try-except` blocks to log errors gracefully in `/var/log/reminder.log` without crashing the dispatcher script.

4. **Concurrent JSON File Access**
   - **Risk:** The LLM agent writing a new reminder to `reminder.json` at the exact millisecond the dispatcher script reads or updates it.
   - **Mitigation:** Implement atomic file writes (writing to a temporary file in the same directory and performing an `os.replace` operation).
