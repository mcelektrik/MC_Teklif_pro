import logging
from logging.handlers import RotatingFileHandler
from app.core.settings import LOG_FILE

def setup_logging():
    logger = logging.getLogger("MC_Teklif_Pro")
    logger.setLevel(logging.INFO)
    
    # Check if handlers are already added to avoid duplicates
    if not logger.handlers:
        # File Handler (Rotating)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=1024*1024, backupCount=5, encoding="utf-8"
        )
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    return logger
