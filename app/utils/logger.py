import logging
import sys
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Logger dir 
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Looger set up
def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Log format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760, # MAX equal to 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Logger instance
app_logger = setup_logger("app") 