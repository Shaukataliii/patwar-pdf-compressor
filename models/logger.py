import logging
import os
from datetime import datetime

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Generate log file name based on current date-time
log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + ".log"
log_filepath = os.path.join(LOG_DIR, log_filename)

# Configure logging
logging.basicConfig(
    filename=log_filepath,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create logger
logger = logging.getLogger("pdf_compressor")
logger.setLevel(logging.INFO)

# Console Handler (optional, for debugging)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Add handlers
logger.addHandler(console_handler)

# Initial log message
logger.info("Logger initialized successfully")
