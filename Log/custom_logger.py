import logging
from datetime import datetime
import os

# log_dir = "/root/ProjectRpi/Rpi/PersonalAssistant/Log"
log_dir = "./Log"
os.makedirs(log_dir, exist_ok=True)

date_str = datetime.now().strftime("%Y-%m-%d")   # yyyy-mm-dd [web:6][web:12]
log_path = os.path.join(log_dir, f"{date_str}_log.log")
# Create a custom logger
logger = logging.getLogger('my_logger')
# logger.setLevel(logging.DEBUG)  # Set global required log level
logger.setLevel(logging.DEBUG)  # Set global required log level

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# File handler
# file_handler = logging.FileHandler('/tmp/personalAssistant.log')
# file_handler = logging.FileHandler('/root/ProjectRpi/Rpi/PersonalAssistant/Log/log.log')
file_handler = logging.FileHandler(log_path)
file_handler.setLevel(logging.DEBUG)
# file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Console (stream) handler
console_handler = logging.StreamHandler()
# console_handler.setLevel(logging.INFO)
console_handler.setLevel(logging.DEBUG)
# console_handler.setFormatter(formatter)

# Add both handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# # Logging examples
# logger.info("start logging")
# logger.debug('Logging started')
# logger.info('This is an info message')
# logger.warning('This is a warning message')
# logger.error('This is an error message')
# logger.info("stop logging")
