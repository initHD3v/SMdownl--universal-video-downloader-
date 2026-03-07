"""
Settings Manager
Handles user preferences including default download location
"""

import os
import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSettings

logger = logging.getLogger(__name__)


class SettingsManager:
    """Manage application settings"""
    
    def __init__(self):
        self.settings = QSettings('SMdown', 'AppSettings')
        self._download_path: Optional[str] = None
    
    def get_download_path(self) -> str:
        """Get default download path"""
        if self._download_path is None:
            # Load from settings
            path = self.settings.value('download_path', '')
            if not path or not os.path.exists(path):
                # Default to ~/Downloads
                path = str(Path.home() / 'Downloads')
            self._download_path = path
        
        return self._download_path
    
    def set_download_path(self, path: str):
        """Set default download path"""
        if os.path.exists(path):
            self._download_path = path
            self.settings.setValue('download_path', path)
            self.settings.sync()
            logger.info("Download path set to: %s", path)
        else:
            logger.warning("Path does not exist: %s", path)
    
    def get_theme_mode(self) -> str:
        """Get saved theme mode"""
        return self.settings.value('theme_mode', 'system')
    
    def set_theme_mode(self, mode: str):
        """Set theme mode"""
        self.settings.setValue('theme_mode', mode)
        self.settings.sync()
    
    def get_window_geometry(self) -> bytes:
        """Get saved window geometry"""
        return self.settings.value('window_geometry', b'')
    
    def set_window_geometry(self, geometry: bytes):
        """Save window geometry"""
        self.settings.setValue('window_geometry', geometry)
        self.settings.sync()
    
    def get_max_concurrent_downloads(self) -> int:
        """Get max concurrent downloads setting"""
        return int(self.settings.value('max_concurrent', '1'))
    
    def set_max_concurrent_downloads(self, count: int):
        """Set max concurrent downloads"""
        self.settings.setValue('max_concurrent', str(count))
        self.settings.sync()
