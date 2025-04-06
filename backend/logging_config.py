# backend/logging_config.py

import logging
from backend.config import LOG_LEVEL, LOG_FILE

def setup_logging():
    """
    Set up logging configuration for the application.
    """
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

# Call setup_logging when this module is imported
setup_logging()
