"""
Utility functions for path handling in PyInstaller bundled apps
"""
import os
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and PyInstaller bundle
    
    Args:
        relative_path: Path relative to project root (e.g., 'assets/logo.png')
    
    Returns:
        Absolute path to the resource
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        # sys._MEIPASS points to the temporary bundle directory
        base_path = sys._MEIPASS
    else:
        # Running in normal Python environment
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    return os.path.join(base_path, relative_path)


def get_app_root_path() -> str:
    """
    Get the root path of the application
    
    Returns:
        Absolute path to application root
    """
    if getattr(sys, 'frozen', False):
        # For .app bundle, go from Contents/MacOS back to Contents
        # Then we can access Resources folder
        exe_path = sys.executable
        if '.app/Contents/MacOS' in exe_path:
            # Return the .app/Contents directory
            return os.path.dirname(os.path.dirname(exe_path))
        return sys._MEIPASS
    else:
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_logs_dir() -> str:
    """
    Get the logs directory path
    
    Returns:
        Absolute path to logs directory
    """
    if getattr(sys, 'frozen', False):
        # For bundled app, store logs in user's Library
        logs_dir = os.path.expanduser('~/Library/Logs/SMdown')
    else:
        # For dev, store in project folder
        logs_dir = os.path.join(get_app_root_path(), 'logs')
    
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def get_assets_dir() -> str:
    """
    Get the assets directory path
    
    Returns:
        Absolute path to assets directory
    """
    return get_resource_path('assets')
