# Plan: Centralized Cloud & Local PII Storage (`CloudPII`)

## 1. Objective
Create a dedicated local directory structure named `CloudPII` to securely store and organize all personal data files, PII, local databases, and environment configuration files away from the public code repository, preparing them for private cloud syncing (OneDrive, Google Drive, iCloud, Dropbox, etc.).
No need to add Sessions, logs as we are not interested to push them to cloud.

---

## 2. Directory Structure (`CloudPII`)
Establish the following directory hierarchy inside `CloudPII/`:
```text
CloudPII/
├── ToolsJobSwitchAssist/
│   └── job_applications.json          # Migrated from Langchain/Tools/ToolsJobSwitchAssist/
├── EnvVars/
│   └── .env                           # Migrated and generalized from root .env and toolsConfig.json
├── UserContext/
│   └── (Personal context files)       # Migrated from UserContext/
```

---

## 3. Implementation Steps (Planned)

### Step 1: Create Directory Tree
- Create `CloudPII/` at the workspace root.
- Create subdirectories:
  - `CloudPII/ToolsJobSwitchAssist/`
  - `CloudPII/EnvVars/`
  - `CloudPII/UserContext/`

### Step 2: Move PII & Local Data Files
- Move `Langchain/Tools/ToolsJobSwitchAssist/job_applications.json` to `CloudPII/ToolsJobSwitchAssist/job_applications.json`.
- Move `.env` and `toolsConfig.json` to `CloudPII/EnvVars/`.
- Move any files in `UserContext/` to `CloudPII/UserContext/`.

### Step 3: Replace with Placeholders / Symlinks / Config Updates
- Ensure application scripts look up or expect data files in `CloudPII/` or via environment variables pointing to `CloudPII/`.
- Create clean template files (e.g., `job_applications.template.json` or `.envTemplate`) in the source repository directories as safe placeholders.

### Step 4: Verify `.gitignore`
- Ensure `CloudPII/` is explicitly added to `.gitignore` to prevent any accidental commits.
