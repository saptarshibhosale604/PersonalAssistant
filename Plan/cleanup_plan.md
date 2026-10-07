# Cleanup, File Migration, and .gitignore Plan

## 1. 🗑️ Files to Clean / Delete in Root (`./`)
- **`delete02.txt`**: Temporary scratch/log file.
- **`temp.md`**: Temporary markdown notes.
- **`state.json.bak`**: Root-level backup state artifact.
- **`chatbot.py`**: Obsolete/redundant root file (superseded by modular UIs in `UI/`).

---

## 2. 🚚 Files to Move (Reorganization) & Code Refactoring
When moving files, **yes, you must update their paths/references** in any scripts, imports, or execution commands where they are called to prevent `ModuleNotFoundError` or `FileNotFoundError`.

- **`userInputToScriptInvocation.py`** ➡️ Move to **`Script/userInputToScriptInvocation.py`**
  - *Code update required:* Search codebase for references/imports of `userInputToScriptInvocation` and update paths to point to `Script/userInputToScriptInvocation.py`.
- **`intentList.json`** ➡️ Move to **`UserContext/intentList.json`**
  - *Code update required:* Update file-loading logic in Python scripts that read `intentList.json` to look inside the `UserContext/` directory (e.g., using `os.path.join`).

---

## 3. 📝 `.gitignore` Updates & Additions
Add the following patterns to `.gitignore`:

```gitignore
# Temporary scratch files & backups
delete*.txt
temp.*
*.bak

# State files generated dynamically
state.json
**/state.json
**/state.json.bak

# Runtime logs and user session data
Log/*.log
```
