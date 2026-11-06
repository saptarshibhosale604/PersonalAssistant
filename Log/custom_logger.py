import logging
from datetime import datetime
import os
import re

# log_dir = "/root/ProjectRpi/Rpi/PersonalAssistant/Log"
log_dir = "./Log/SessionLog"
os.makedirs(log_dir, exist_ok=True)

# Determine next sequential 4-digit ID
existing_files = os.listdir(log_dir)
max_id = -1
# Pattern matching new format: session_0000_2026-10-08_11-08-02.log or similar
# Also handles old format gracefully if present: session_2026-10-08_11-08-02_26640.log
for filename in existing_files:
    match = re.match(r'^session_(\d{4})_', filename)
    if match:
        try:
            file_id = int(match.group(1))
            if file_id > max_id:
                max_id = file_id
        except ValueError:
            pass

next_id = max_id + 1 if max_id >= 0 else 0
session_id_str = f"{next_id:04d}"

# Generate session timestamp
session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
session_filename = f"session_{session_id_str}_{session_timestamp}.json"
log_path = os.path.join(log_dir, session_filename)

# Create a custom logger
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)  # Set global required log level

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler for this specific session
file_handler = logging.FileHandler(log_path, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Console (stream) handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Add both handlers to the logger (avoid duplicate handlers if imported multiple times)
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Optional: maintain a 'latest.json' symlink or copy in Log/ (parent of log_dir) for easy tailing
def _update_latest_symlink(filename: str) -> None:
    try:
        parent_dir = os.path.dirname(log_dir)
        latest_path = os.path.join(parent_dir, "latest.json")
        if os.path.islink(latest_path):
            os.unlink(latest_path)
        elif os.path.exists(latest_path):
            os.remove(latest_path)
        if os.name == 'nt':
            try:
                os.symlink(os.path.join("SessionLog", filename), latest_path)
            except OSError:
                pass
        else:
            os.symlink(os.path.join("SessionLog", filename), latest_path)
    except Exception:
        pass

_update_latest_symlink(session_filename)


def start_new_session() -> str:
    """Closes current session file handler, increments session ID, and creates a fresh session JSON file."""
    global log_path, session_id_str, session_filename
    
    # 1. Remove old file handler from logger
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
            logger.removeHandler(handler)
            
    # 2. Determine next sequential ID
    existing_files = os.listdir(log_dir)
    max_id = -1
    for filename in existing_files:
        match = re.match(r'^session_(\d{4})_', filename)
        if match:
            try:
                file_id = int(match.group(1))
                if file_id > max_id:
                    max_id = file_id
            except ValueError:
                pass

    next_id = max_id + 1 if max_id >= 0 else 0
    session_id_str = f"{next_id:04d}"

    # 3. Generate new timestamp & filename
    session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    session_filename = f"session_{session_id_str}_{session_timestamp}.json"
    log_path = os.path.join(log_dir, session_filename)

    # 4. Add new file handler
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 5. Clear turn_logger session turns
    from Log import turn_logger
    turn_logger.reset_session_turns()

    # 6. Update latest.json symlink
    _update_latest_symlink(session_filename)

    return log_path
