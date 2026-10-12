# PLAN: Cross-Platform .env File Integration

## Objective
Plan the robust integration of `.env` file configuration across the Personal Assistant project in a cross-platform manner (supporting both Windows PowerShell/CMD and Linux/Docker/Raspberry Pi environments), including the creation of a `.envTemplate` file.

---

## 1. Create `.envTemplate` File
A template file `.envTemplate` has been created in the root directory containing placeholders for all required environment variables (`GOOGLE_API_KEY`, `OPENAI_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `MISTRAL_API_KEY`, `NVIDIA_API_KEY`, and `LANGSMITH_*` configurations).

---

## 2. Cross-Platform Environment Loading Strategy
To ensure environment variables load seamlessly across Windows and Linux/Docker without hardcoding platform-specific commands in Python scripts or relying solely on manual shell setups, we will use Python's **`python-dotenv`** package as the primary mechanism, supplemented by shell-specific loader scripts.

### A. Python-Level Loading (`python-dotenv`)
1. **Dependencies:** Add `python-dotenv` to `requirements.txt`.
2. **Entry Point Initialization:** In core entry points (`UI/cli.py`, `UI/WebApp/app.py`, LLM initializers), automatically load the `.env` file at startup if present:
   ```python
   from dotenv import load_dotenv
   load_dotenv() # automatically searches for .env in current and parent directories
   ```

### B. Shell-Specific Loading Helpers (Windows & Linux)

For users who want to export environment variables directly into their shell session before running scripts:

1. **Linux / Bash / Docker (`load_env.sh` or `.bashrc` integration):**
   ```bash
   #!/bin/bash
   if [ -f .env ]; then
       export $(grep -v '^#' .env | xargs)
       echo "Environment variables loaded from .env"
   else
       echo ".env file not found. Please copy .envTemplate to .env"
   fi
   ```
   *Usage:* `source load_env.sh` (or `. ./load_env.sh`)

2. **Windows PowerShell (`load_env.ps1`):**
   ```powershell
   if (Test-Path .env) {
       Get-Content .env | ForEach-Object {
           if ($_ -match '^([^#=]+)=(.*)$') {
               [Environment]::SetEnvironmentVariable($Matches[1].Trim(), $Matches[2].Trim(), 'Process')
           }
       }
       Write-Host "Environment variables loaded from .env into PowerShell process." -ForegroundColor Green
   } else {
       Write-Host ".env file not found. Please copy .envTemplate to .env" -ForegroundColor Red
   }
   ```
   *Usage:* `./load_env.ps1`

---

## 3. Implementation Steps & Files to Update
1. **Root Files:**
   - `.envTemplate` (Created)
   - `load_env.sh` (New helper for Linux/Bash)
   - `load_env.ps1` (New helper for PowerShell)
   - `.gitignore` (Ensure `.env` is ignored, while `.envTemplate` is tracked)
2. **Python Integration:**
   - Update `requirements.txt` to include `python-dotenv`.
   - Update `UI/cli.py`, `UI/WebApp/app.py`, and `LLM/llm.py` (or central initialization module) to call `load_dotenv()`.
3. **Documentation:**
   - Update `README.md` and `CLAUDE.md` with instructions on setting up `.env` from `.envTemplate` for both Windows and Linux/Docker.
