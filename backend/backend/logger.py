import logging
import os

# Set up a log directory and file
log_directory = 'logs'
os.makedirs(log_directory, exist_ok=True)
log_file = os.path.join(log_directory, 'project.log')

# Configure the logger
logging.basicConfig(
    level=logging.INFO,  # Set minimum logging level
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),  # Log to file
        logging.StreamHandler()  # Log to console
    ],
    encoding='utf-8'
)

# Get a named logger
logger = logging.getLogger("project_logger")
