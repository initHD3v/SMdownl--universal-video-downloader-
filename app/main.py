#!/usr/bin/env python3
"""
SMdown - Universal Video Downloader for macOS
Main application entry point
"""

import sys
import os
import logging
from datetime import datetime

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup logging
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'smdown_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtGui import QFont, QPalette, QColor

from app.ui.main_window import MainWindow
from app.services.theme_manager import ThemeManager, ThemeMode


def qt_message_handler(mode, context, message):
    """Handle Qt log messages"""
    level = {
        0: logging.DEBUG,    # QtDebugMsg
        1: logging.WARNING,  # QtWarningMsg
        2: logging.ERROR,    # QtCriticalMsg
        3: logging.ERROR,    # QtFatalMsg
    }.get(mode, logging.INFO)
    
    log_msg = f"Qt: {message}"
    if context.file:
        log_msg += f" ({context.file}:{context.line})"
    
    logger.log(level, log_msg)


def setup_application() -> QApplication:
    """Setup and configure the QApplication"""
    logger.info("Setting up QApplication...")
    
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("SMdown")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SMdown")

    # Set application style
    app.setStyle('Fusion')
    
    logger.info("QApplication setup completed")

    return app


def main():
    """Main entry point"""
    logger.info("=" * 50)
    logger.info("SMdown Application Starting")
    logger.info("=" * 50)
    
    # Check for required dependencies
    try:
        import yt_dlp
        logger.info("yt-dlp found: %s", yt_dlp.__version__ if hasattr(yt_dlp, '__version__') else "unknown")
    except ImportError:
        logger.error("yt-dlp is not installed")
        print("Error: yt-dlp is not installed.")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)

    try:
        from PySide6.QtWidgets import QApplication
        logger.info("PySide6 found")
    except ImportError:
        logger.error("PySide6 is not installed")
        print("Error: PySide6 is not installed.")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)

    # Install Qt message handler
    qInstallMessageHandler(qt_message_handler)

    # Create application
    app = setup_application()

    # Create and show main window
    logger.info("Creating MainWindow...")
    window = MainWindow()
    window.show()
    logger.info("MainWindow displayed")

    # Run application
    logger.info("Starting application event loop")
    exit_code = app.exec()
    
    logger.info("Application exiting with code: %d", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
