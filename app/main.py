import sys
import logging
from PySide6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.core.db import init_db, ensure_directories
from app.core.logging_setup import setup_logging

def main():
    # Setup Logging
    ensure_directories()
    logger = setup_logging()
    
    logger.info("Application starting...")
    
    # Initialize Database
    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return

    # Create Application
    app = QApplication(sys.argv)
    app.setApplicationName("MC_Teklif_Pro")
    
    # Create Main Window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
