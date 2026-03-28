#!/usr/bin/env python3
"""
SMdown - Universal Video Downloader for macOS
Main application entry point
"""

import sys
import os

# CRITICAL: Write to stderr immediately for debugging
def debug_print(msg):
    print(f"[DEBUG] {msg}", file=sys.stderr)
    sys.stderr.flush()

debug_print("Script started")
debug_print(f"sys.executable: {sys.executable}")
debug_print(f"sys.frozen: {getattr(sys, 'frozen', False)}")
debug_print(f"Working dir: {os.getcwd()}")

try:
    import logging
    debug_print("logging imported")
except Exception as e:
    debug_print(f"Failed to import logging: {e}")
    raise

from datetime import datetime
debug_print("datetime imported")

# Add app directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
debug_print(f"Script dir: {script_dir}")
sys.path.insert(0, os.path.dirname(os.path.dirname(script_dir)))
debug_print(f"Path updated: {sys.path[:3]}")

# Import path utilities FIRST
try:
    from app.utils.path_utils import get_logs_dir, get_app_root_path, get_resource_path
    debug_print("path_utils imported")
except Exception as e:
    debug_print(f"Failed to import path_utils: {e}")
    raise

from app.utils.timing import init_startup_timer, log_timing, timed_function, timed_block, get_elapsed_time
debug_print("timing imported")

# Initialize startup timer IMMEDIATELY
startup_time = init_startup_timer()
debug_print("Timer initialized")

# Setup logging with proper path for bundled app
log_dir = get_logs_dir()
log_file = os.path.join(log_dir, f'smdown_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

# Simple logging setup with immediate flush
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8', mode='a'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Disable buffering for stdout
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

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


def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Catch unhandled exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        # Call the default handler for keyboard interrupt
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception:", exc_info=(exc_type, exc_value, exc_traceback))
    print(f"\n❌ Fatal Error: {exc_value}")
    import traceback
    traceback.print_exception(exc_type, exc_value, exc_traceback)


def setup_application() -> QApplication:
    """Setup and configure the QApplication"""
    logger.info("Setting up QApplication...")

    # Install global exception handler
    sys.excepthook = global_exception_handler

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
    log_timing("=" * 70)
    log_timing("SMdown Application Starting")
    log_timing(f"App root: {get_app_root_path()}")
    log_timing(f"Logs dir: {get_logs_dir()}")
    log_timing(f"Frozen (bundled): {getattr(sys, 'frozen', False)}")
    log_timing(f"sys.executable: {sys.executable}")
    if hasattr(sys, '_MEIPASS'):
        log_timing(f"sys._MEIPASS: {sys._MEIPASS}")
    log_timing("=" * 70)

    # Check for required dependencies
    with timed_block("Dependency Check"):
        try:
            import yt_dlp
            log_timing(f"yt-dlp found: {yt_dlp.__version__ if hasattr(yt_dlp, '__version__') else 'unknown'}")
        except ImportError:
            logger.error("yt-dlp is not installed", exc_info=True)
            print("Error: yt-dlp is not installed.")
            print("Please install dependencies: pip install -r requirements.txt")
            sys.exit(1)

        try:
            from PySide6.QtWidgets import QApplication
            log_timing("PySide6 found")
        except ImportError:
            logger.error("PySide6 is not installed", exc_info=True)
            print("Error: PySide6 is not installed.")
            print("Please install dependencies: pip install -r requirements.txt")
            sys.exit(1)

    # Install Qt message handler
    qInstallMessageHandler(qt_message_handler)

    # Create application
    log_timing("Creating QApplication...")
    app = setup_application()
    log_timing("QApplication created")

    # Create and show main window
    log_timing("Creating MainWindow...")
    try:
        window = MainWindow()
        log_timing("MainWindow created")
        window.show()
        log_timing("MainWindow displayed")
    except Exception as e:
        logger.error("Failed to create MainWindow: %s", e, exc_info=True)
        print(f"Error: Failed to create main window: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    log_timing("=" * 70)
    log_timing(f"TOTAL STARTUP TIME: {get_elapsed_time():.3f}s")
    log_timing("=" * 70)

    # Run application
    log_timing("Starting application event loop")
    try:
        exit_code = app.exec()
        log_timing(f"Application exited with code: {exit_code}")
    except Exception as e:
        logger.error("Exception in event loop: %s", e, exc_info=True)
        raise
    finally:
        log_timing("Application exiting")
        logger.info("Application exiting with code: %d", exit_code)
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
