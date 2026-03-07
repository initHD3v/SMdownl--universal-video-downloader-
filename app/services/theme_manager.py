"""
Theme Manager Service
Handles dark/light/system theme switching
"""

import logging
from enum import Enum
from typing import Optional

from PySide6.QtWidgets import QApplication  # pyre-ignore[21]
from PySide6.QtCore import QSettings, Signal, QObject  # pyre-ignore[21]
from PySide6.QtGui import QPalette, QColor  # pyre-ignore[21]

logger = logging.getLogger(__name__)


class ThemeMode(Enum):
    """Theme mode options"""
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class ThemeManager(QObject):
    """Manage application theme"""
    
    theme_changed = Signal(str)  # Emits new theme mode
    
    # Light theme colors (matching mockup)
    LIGHT_PALETTE = {
        'window': '#F5F5F7',
        'window_text': '#1D1D1F',
        'base': '#FFFFFF',
        'alternate_base': '#F5F5F7',
        'text': '#1D1D1F',
        'button': '#FFFFFF',
        'button_text': '#1D1D1F',
        'highlight': '#007AFF',  # macOS blue
        'highlighted_text': '#FFFFFF',
        'link': '#0066CC',
        'link_visited': '#551A8B',
    }
    
    # Dark theme colors (current)
    DARK_PALETTE = {
        'window': '#1e1e2e',
        'window_text': '#ffffff',
        'base': '#2a2a3e',
        'alternate_base': '#1a1a2e',
        'text': '#ffffff',
        'button': '#3a3a5e',
        'button_text': '#ffffff',
        'highlight': '#00d4aa',
        'highlighted_text': '#1e1e2e',
        'link': '#00d4aa',
        'link_visited': '#00c49a',
    }
    
    def __init__(self, app: Optional[QApplication] = None):
        super().__init__()
        self.app = app
        self.settings = QSettings('SMdown', 'ThemeSettings')
        self._current_mode = ThemeMode.SYSTEM
        
    def load_theme(self):
        """Load saved theme from settings"""
        saved = self.settings.value('theme_mode', 'light')  # Default to light theme
        try:
            self._current_mode = ThemeMode(saved)
        except ValueError:
            self._current_mode = ThemeMode.LIGHT
        
        logger.info("Loaded theme: %s", self._current_mode.value)
        return self._current_mode
    
    def save_theme(self, mode: ThemeMode):
        """Save theme to settings"""
        self.settings.setValue('theme_mode', mode.value)
        self.settings.sync()
        logger.info("Saved theme: %s", mode.value)
    
    def set_theme(self, mode: ThemeMode):
        """Set application theme"""
        if self.app is None:
            logger.warning("No QApplication available")
            return
            
        self._current_mode = mode
        self.save_theme(mode)
        
        # Determine actual colors to use
        if mode == ThemeMode.SYSTEM:
            # Use system appearance
            self.app.setStyle('Fusion')  # pyre-ignore[16]
            # Don't set custom palette, let system handle it
        elif mode == ThemeMode.LIGHT:
            self._apply_light_theme()
        else:  # DARK
            self._apply_dark_theme()
        
        self.theme_changed.emit(mode.value)
        logger.info("Theme applied: %s", mode.value)
    
    def _apply_light_theme(self):
        """Apply light theme palette"""
        if self.app is None:
            return
            
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.LIGHT_PALETTE['window']))
        palette.setColor(QPalette.WindowText, QColor(self.LIGHT_PALETTE['window_text']))
        palette.setColor(QPalette.Base, QColor(self.LIGHT_PALETTE['base']))
        palette.setColor(QPalette.AlternateBase, QColor(self.LIGHT_PALETTE['alternate_base']))
        palette.setColor(QPalette.Text, QColor(self.LIGHT_PALETTE['text']))
        palette.setColor(QPalette.Button, QColor(self.LIGHT_PALETTE['button']))
        palette.setColor(QPalette.ButtonText, QColor(self.LIGHT_PALETTE['button_text']))
        palette.setColor(QPalette.Highlight, QColor(self.LIGHT_PALETTE['highlight']))
        palette.setColor(QPalette.HighlightedText, QColor(self.LIGHT_PALETTE['highlighted_text']))
        palette.setColor(QPalette.Link, QColor(self.LIGHT_PALETTE['link']))
        palette.setColor(QPalette.LinkVisited, QColor(self.LIGHT_PALETTE['link_visited']))
        
        self.app.setPalette(palette)  # pyre-ignore[16]
        self.app.setStyle('Fusion')  # pyre-ignore[16]
        
    def _apply_dark_theme(self):
        """Apply dark theme palette"""
        if self.app is None:
            return
            
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(self.DARK_PALETTE['window']))
        palette.setColor(QPalette.WindowText, QColor(self.DARK_PALETTE['window_text']))
        palette.setColor(QPalette.Base, QColor(self.DARK_PALETTE['base']))
        palette.setColor(QPalette.AlternateBase, QColor(self.DARK_PALETTE['alternate_base']))
        palette.setColor(QPalette.Text, QColor(self.DARK_PALETTE['text']))
        palette.setColor(QPalette.Button, QColor(self.DARK_PALETTE['button']))
        palette.setColor(QPalette.ButtonText, QColor(self.DARK_PALETTE['button_text']))
        palette.setColor(QPalette.Highlight, QColor(self.DARK_PALETTE['highlight']))
        palette.setColor(QPalette.HighlightedText, QColor(self.DARK_PALETTE['highlighted_text']))
        palette.setColor(QPalette.Link, QColor(self.DARK_PALETTE['link']))
        palette.setColor(QPalette.LinkVisited, QColor(self.DARK_PALETTE['link_visited']))
        
        self.app.setPalette(palette)  # pyre-ignore[16]
        self.app.setStyle('Fusion')  # pyre-ignore[16]
    
    def get_current_mode(self) -> ThemeMode:
        """Get current theme mode"""
        return self._current_mode
    
    def is_dark_mode(self) -> bool:
        """Check if currently using dark mode"""
        if self._current_mode == ThemeMode.SYSTEM:
            # Check system appearance
            try:
                from PySide6.QtCore import QSysInfo  # pyre-ignore[21]
                # macOS dark mode detection
                return False  # Default to light for system
            except:
                return False
        return self._current_mode == ThemeMode.DARK
