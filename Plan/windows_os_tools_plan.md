# Plan: Windows OS Operations Tools (`Langchain\Tools\toolsWindowsOS.py`)

## Objective
Create a new tool file named `Langchain\Tools\toolsWindowsOS.py` containing a list of 6 tools designed to operate and query the Windows operating system using Python standard libraries (`os`, `subprocess`, `shutil`, `platform`, `getpass`).

---

## Proposed Tools List

1. **`get_system_info`**
   - **Description:** Retrieves basic Windows system information, including OS release, architecture, computer name, and current username.
   - **Underlying Modules:** `platform`, `getpass`, `socket`.
   - **Parameters:** None.
   - **Output:** JSON/Dict string containing system details.

2. **`list_running_processes`**
   - **Description:** Lists top running Windows processes (Name and PID) to check system activity.
   - **Underlying Operation:** Executes PowerShell command `Get-Process | Select-Object -First 15 Name, Id, WorkingSet` via `subprocess`.
   - **Parameters:** `limit` (int, default=15).
   - **Output:** Formatted string of running processes.

3. **`get_disk_usage`**
   - **Description:** Checks available disk space and total storage capacity for specified Windows drives (e.g., `C:`).
   - **Underlying Operation:** Uses Python `shutil.disk_usage()`.
   - **Parameters:** `drive_path` (str, default=`"C:\\"`).
   - **Output:** Total, used, and free disk space in Gigabytes (GB).

4. **`list_directory_contents`**
   - **Description:** Lists files and folders in a specified Windows directory path with file sizes and modification times.
   - **Underlying Operation:** Uses Python `os.listdir()`, `os.path`, and `os.stat()`.
   - **Parameters:** `directory_path` (str).
   - **Output:** Structured list of files and subdirectories.

5. **`set_screen_brightness`**
   - **Description:** Sets the display brightness of the Windows PC to a specified percentage (0-100%).
   - **Underlying Operation:** Uses PowerShell / WMI (`WmiMonitorBrightnessMethods`) via `subprocess`.
   - **Parameters:** `brightness_percentage` (int, 0 to 100).
   - **Output:** Success message or error.

6. **`set_system_volume`**
   - **Description:** Sets the master system audio volume to a specified percentage (0-100%).
   - **Underlying Operation:** Uses PowerShell / .NET audio control or pycaw/nircmd via `subprocess`.
   - **Parameters:** `volume_percentage` (int, 0 to 100).
   - **Output:** Success message or error.

---

## Status
- **Phase:** Planning Only (No code implemented yet).
- **Target File:** `Langchain\Tools\toolsWindowsOS.py`
