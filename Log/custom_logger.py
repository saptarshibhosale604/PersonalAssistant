import logging
from datetime import datetime
import os

# log_dir = "/root/ProjectRpi/Rpi/PersonalAssistant/Log"
log_dir = "./Log"
os.makedirs(log_dir, exist_ok=True)

# Generate unique session identifier using timestamp and process ID
session_timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
pid = os.getpid()
session_filename = f"session_{session_timestamp}_{pid}.log"
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

# Optional: maintain a 'latest.log' symlink or copy for easy tailing
try:
    latest_path = os.path.join(log_dir, "latest.log")
    if os.path.islink(latest_path):
        os.unlink(latest_path)
    elif os.path.exists(latest_path):
        os.remove(latest_path)
    # On Windows or systems where symlink might fail without admin rights, fallback or try symlink
    if os.name == 'nt':
        # On Windows, copy or write a pointer, or create symlink if permitted
        try:
            os.symlink(session_filename, latest_path)
        except OSError:
            pass
    else:
        os.symlink(session_filename, latest_path)
except Exception:
    pass
