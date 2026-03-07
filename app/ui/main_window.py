"""
Main Window UI Component
Redesigned with macOS 26 (Sequoia) Design Principles
- Liquid Glass effects
- Rounded corners (20px+)
- SF Pro typography
- Subtle shadows and depth
- Vibrancy and blur effects
- Minimal, clean interface
"""

import os
import logging
import threading
import subprocess
from typing import Optional, List
from datetime import datetime

import requests  # pyre-ignore[21]

from PySide6.QtWidgets import (  # pyre-ignore[21]
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar,
    QFrame, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox, QScrollArea,
    QGroupBox, QDialog, QDialogButtonBox,
    QToolButton, QSizePolicy, QGraphicsDropShadowEffect,
    QGraphicsBlurEffect, QSpacerItem,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer  # pyre-ignore[21]
from PySide6.QtGui import QPixmap, QFont, QIcon, QPalette, QColor, QBrush, QFontDatabase  # pyre-ignore[21]

from app.downloader.yt_dlp_engine import YtDlpEngine, VideoQuality, VideoMetadata, DownloadProgress  # pyre-ignore[21]
from app.downloader.queue_manager import QueueManager, QueueItem, QueueItemStatus  # pyre-ignore[21]
from app.services.clipboard_monitor import ClipboardMonitor  # pyre-ignore[21]
from app.services.theme_manager import ThemeManager, ThemeMode  # pyre-ignore[21]
from app.services.history_manager import HistoryManager, HistoryItem  # pyre-ignore[21]
from app.services.settings_manager import SettingsManager  # pyre-ignore[21]

logger = logging.getLogger(__name__)


# Platform icons
PLATFORM_ICONS = {
    'YouTube': '▶️',
    'Facebook': '📘',
    'Instagram': '📷',
    'X': '❌',
    'TikTok': '🎵',
    'Unknown': '📹',
}


# macOS 26 Color Palette
class macOSColors:
    """macOS 26 (Sequoia) color palette"""
    # Light mode
    LIGHT = {
        'window_bg': '#F5F5F7',
        'card_bg': '#FFFFFF',
        'primary': '#007AFF',      # Apple Blue
        'primary_hover': '#0066D6',
        'text_primary': '#1D1D1F',
        'text_secondary': '#6E6E73',
        'text_tertiary': '#86868B',
        'border': '#D2D2D7',
        'border_light': '#E5E5EA',
        'success': '#34C759',      # Apple Green
        'warning': '#FF9500',      # Apple Orange
        'error': '#FF3B30',        # Apple Red
        'shadow': QColor(0, 0, 0, 20),
        'glass_bg': 'rgba(255, 255, 255, 160)',
        'glass_border': 'rgba(210, 210, 215, 0.5)',
        'glass_focus': 'rgba(0, 122, 255, 0.6)',
        'glass_hover': 'rgba(245, 245, 247, 0.8)',
        'glass_pressed': 'rgba(229, 229, 234, 0.7)',
        'list_hover': 'rgba(245, 245, 247, 0.4)',
        'list_selected': 'rgba(245, 245, 247, 0.6)',
        'card_glass': 'rgba(255, 255, 255, 180)',
        'card_border': 'rgba(255, 255, 255, 100)',
    }
    
    # Dark mode
    DARK = {
        'window_bg': '#1E1E1E',
        'card_bg': '#2C2C2E',
        'primary': '#0A84FF',      # Apple Blue (dark)
        'primary_hover': '#409CFF',
        'text_primary': '#F5F5F7',
        'text_secondary': '#98989D',
        'text_tertiary': '#6E6E73',
        'border': '#3A3A3C',
        'border_light': '#48484A',
        'success': '#30D158',
        'warning': '#FF9F0A',
        'error': '#FF453A',
        'shadow': QColor(0, 0, 0, 60),
        'glass_bg': 'rgba(44, 44, 46, 160)',
        'glass_border': 'rgba(72, 72, 74, 0.5)',
        'glass_focus': 'rgba(10, 132, 255, 0.6)',
        'glass_hover': 'rgba(58, 58, 60, 0.8)',
        'glass_pressed': 'rgba(72, 72, 74, 0.7)',
        'list_hover': 'rgba(58, 58, 60, 0.4)',
        'list_selected': 'rgba(72, 72, 74, 0.6)',
        'card_glass': 'rgba(44, 44, 46, 180)',
        'card_border': 'rgba(72, 72, 74, 100)',
    }


class ThumbnailFetchThread(QThread):
    """Thread for fetching thumbnail image"""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                pixmap = QPixmap()
                if pixmap.loadFromData(response.content):
                    self.finished.emit(pixmap)
                else:
                    self.error.emit("Failed to load image")
            else:
                self.error.emit(f"HTTP {response.status_code}")
        except Exception as e:
            self.error.emit(str(e))


class MetadataFetcherThread(QThread):
    """Thread for fetching video metadata"""
    finished = Signal(object)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.engine = YtDlpEngine()

    def run(self):
        metadata = self.engine.fetch_metadata(self.url)
        if metadata:
            self.finished.emit(metadata)
        else:
            self.error.emit("Failed to fetch video metadata")


class AboutDialog(QDialog):
    """About dialog with macOS 26 Liquid Glass styling"""
    
    def __init__(self, colors: dict, parent=None):
        super().__init__(parent)
        self.colors = colors
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("About SMdown")
        self.setFixedSize(400, 350)
        
        # Center the dialog
        if self.parent():
            parent_geo = self.parent().geometry()
            self.move(
                parent_geo.center().x() - self.width() // 2,
                parent_geo.center().y() - self.height() // 2
            )
            
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.colors['window_bg']};
                border-radius: 20px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)
        
        # Icon/Label Header
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        app_icon = QLabel("⬇️") # Mock icon
        app_icon.setFont(QFont("SF Pro Display", 48))
        app_icon.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(app_icon)
        
        app_title = QLabel("SMdown")
        app_title.setFont(QFont("SF Pro Display", 24, QFont.Bold))
        app_title.setStyleSheet(f"color: {self.colors['text_primary']};")
        app_title.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(app_title)
        
        app_version = QLabel("Version 1.2.0")
        app_version.setFont(QFont("SF Pro Display", 13))
        app_version.setStyleSheet(f"color: {self.colors['text_secondary']};")
        app_version.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(app_version)
        
        layout.addLayout(header_layout)
        
        # Description
        desc = QLabel("Elegant and powerful social media downloader for macOS.")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)
        desc.setFont(QFont("SF Pro Display", 13))
        desc.setStyleSheet(f"color: {self.colors['text_primary']};")
        layout.addWidget(desc)
        
        # Divider
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Plain)
        line.setStyleSheet(f"background-color: {self.colors['border_light']};")
        layout.addWidget(line)
        
        # Developer Info
        dev_info = QLabel(
            "Developed by <b>initialH</b><br>"
            "<small>hidayatfauzi6@gmail.com</small>"
        )
        dev_info.setAlignment(Qt.AlignCenter)
        dev_info.setOpenExternalLinks(True)
        dev_info.setTextInteractionFlags(Qt.TextBrowserInteraction)
        dev_info.setStyleSheet(f"color: {self.colors['text_secondary']};")
        layout.addWidget(dev_info)
        
        # GitHub Link
        github_link = QLabel('<a href="https://github.com/initHD3v" style="color: %s; text-decoration: none;">GitHub @initHD3v</a>' % self.colors['primary'])
        github_link.setAlignment(Qt.AlignCenter)
        github_link.setOpenExternalLinks(True)
        github_link.setFont(QFont("SF Pro Display", 13, QFont.Medium))
        layout.addWidget(github_link)
        
        layout.addStretch()
        
        # Close Button
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok)
        btn_box.accepted.connect(self.accept)
        btn_box.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['primary']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 8px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['primary_hover']};
            }}
        """)
        layout.addWidget(btn_box)


class HistoryDialog(QDialog):
    """Download history dialog with macOS 26 styling"""
    
    def __init__(self, history: HistoryManager, parent=None):
        super().__init__(parent)  # pyre-ignore[20]
        self.history = history
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        self.setWindowTitle("Download History")
        self.setMinimumSize(700, 500)
        self.resize(800, 600)
        
        # macOS 26 styling
        self.setStyleSheet("""
            QDialog {
                background-color: #F5F5F7;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📜 Download History")
        header.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        header.setStyleSheet("color: #1D1D1F;")
        layout.addWidget(header)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #D2D2D7;
                border-radius: 12px;
                background-color: white;
            }
            QListWidget::item {
                padding: 12px 16px;
                border-bottom: 1px solid #E5E5EA;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #F5F5F7;
            }
        """)
        layout.addWidget(self.history_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.clear_btn = QPushButton("🗑 Clear All")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF3B30;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #FF453A;
            }
        """)
        self.clear_btn.clicked.connect(self._on_clear_clicked)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("Close")
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #0066D6;
            }
        """)
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def load_history(self):
        """Load history items into list"""
        self.history_list.clear()
        items = self.history.get_all(limit=100)
        
        for item in items:
            widget = HistoryItemWidget(item)
            list_item = QListWidgetItem(self.history_list)
            list_item.setSizeHint(widget.sizeHint())
            self.history_list.addItem(list_item)
            self.history_list.setItemWidget(list_item, widget)
    
    def _on_clear_clicked(self):
        """Clear all history"""
        reply = QMessageBox.question(
            self, "Clear History",
            "Are you sure you want to clear all download history?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history.clear_all()
            self.load_history()


class HistoryItemWidget(QWidget):
    """Widget for displaying a single history item"""
    
    def __init__(self, item: HistoryItem):
        super().__init__()
        self.item = item
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)
        
        # Platform icon
        icon = QLabel(PLATFORM_ICONS.get(self.item.platform, '📹'))
        icon.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon)
        
        # Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        title = QLabel(self.item.title)
        title.setFont(QFont("SF Pro Display", 13, QFont.Medium))
        title.setWordWrap(True)
        info_layout.addWidget(title)
        
        meta = QLabel(f"{self.item.platform} • {self.item.quality} • {self._format_date()}")
        meta.setStyleSheet("color: #6E6E73; font-size: 12px;")
        info_layout.addWidget(meta)
        
        layout.addLayout(info_layout, 1)
        
        # File size
        size = QLabel(self._format_size())
        size.setStyleSheet("color: #86868B; font-size: 12px;")
        layout.addWidget(size)
    
    def _format_date(self):
        """Format download date"""
        try:
            dt = datetime.fromisoformat(self.item.downloaded_at)
            return dt.strftime("%b %d, %Y %H:%M")
        except:
            return "Unknown"
    
    def _format_size(self):
        """Format file size"""
        size = self.item.file_size
        if size >= 1024 * 1024 * 1024:
            return f"{size / (1024*1024*1024):.1f} GB"
        elif size >= 1024 * 1024:
            return f"{size / (1024*1024):.1f} MB"
        elif size >= 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size} B"


class DownloadStatusWidget(QWidget):
    """Minimalist Download Status Widget with a real-time progress bar"""

    def __init__(self):
        super().__init__()
        self.item_id = None
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)

        # Status text: e.g. "[download] 93.0% of 14.72MB at 1.60MB/s ETA 00:00"
        self.status_label = QLabel("Waiting for downloads...")
        status_font = QFont("Menlo", 12)
        status_font.setStyleHint(QFont.Monospace)
        self.status_label.setFont(status_font)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        layout.addWidget(self.progress_bar)

    def update_styles(self, colors: dict):
        """Dynamically update styles for DownloadStatusWidget - Hacker Terminal Aesthetic"""
        # Neon green text for hacker feel
        hacker_green = "#00FF41" 
        self.status_label.setStyleSheet(f"color: {hacker_green}; font-weight: bold;")
        
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1A1A1A;
                border: 1px solid #333;
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background-color: {hacker_green};
                border-radius: 1px;
            }}
        """)
        self.setStyleSheet(f"""
            DownloadStatusWidget {{
                background-color: #0D0D0D;
                border: 2px solid #333;
                border-radius: 8px;
            }}
        """)

    def _format_size(self, size_bytes: int) -> str:
        """Helper to format bytes to human readable MiB size"""
        if size_bytes <= 0:
            return "Unknown"
        mb_size = size_bytes / (1024 * 1024)
        return f"{mb_size:.2f}MiB"

    def update(self, item: QueueItem, colors: dict):
        """Update widget with hacker-style logic logs."""
        self.item_id = item.id
        
        if item.status == QueueItemStatus.WAITING:
            self.status_label.setText("[SYSTEM: STANDBY] - Waiting for instruction_buffer...")
            self.progress_bar.setValue(0)
        elif item.status == QueueItemStatus.DOWNLOADING:
            total_str = self._format_size(item.total_bytes)
            speed_str = item.speed if item.speed else "0 MiB/s"
            if "MB/s" in speed_str:
                speed_str = speed_str.replace("MB/s", "MiB/s")
            
            # Hacker-style detailed metrics
            log_text = (
                f"[SYSTEM: BUSY] RX_DATA_STREAM ACTIVE\n"
                f"[METRICS] PROG: {item.progress:5.1f}% | SIZE: {total_str} | SPD: {speed_str} | ETA: {item.eta}\n"
                f"[SOCKET] TUNNEL_ESTABLISHED - RECEIVING_PACKETS..."
            )
            self.status_label.setText(log_text)
            self.progress_bar.setValue(int(item.progress))
        elif item.status == QueueItemStatus.COMPLETED:
            total_str = self._format_size(item.total_bytes)
            fname = item.filename or 'file'
            if len(fname) > 30:
                fname = fname[:27] + "..."
            log_text = (
                f"[SYSTEM: SUCCESS] DATA_TRANSFER_COMPLETE\n"
                f"[DATA] SIZE: {total_str} | SAVED: {fname}\n"
                f"[STATUS] IO_BUFFER_FLUSHED"
            )
            self.status_label.setText(log_text)
            self.progress_bar.setValue(100)
        elif item.status == QueueItemStatus.ERROR:
            self.status_label.setText(f"[FATAL_ERR] INTERRUPT: {item.error or 'Unknown exception'}")
        elif item.status == QueueItemStatus.PAUSED:
            self.status_label.setText("[SYSTEM: SUSPENDED] Process paused by user_interrupt")
        elif item.status == QueueItemStatus.CANCELLED:
            self.status_label.setText("[SYSTEM: TERMINATED] Process killed")
            
        self.update_styles(colors)


class PreviewCard(QWidget):
    """Video preview card with macOS 26 Liquid Glass styling"""
    
    download_clicked = Signal()
    
    def __init__(self):
        super().__init__()
        self._metadata: Optional[VideoMetadata] = None
        self._thumbnail_thread: Optional[ThumbnailFetchThread] = None
        self.setup_ui()
    
    def setup_ui(self):
        # Liquid Glass effect - semi-transparent with blur
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Glass container
        glass_layout = QVBoxLayout(self)
        glass_layout.setContentsMargins(0, 0, 0, 0)
        
        # Enforce compactness
        self.setFixedHeight(150) # Fixed height to prevent vertical bloat
        
        # Glass background widget
        self.glass_bg = QFrame()
        
        # Add blur effect
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(30)
        self.glass_bg.setGraphicsEffect(blur)
        
        # Shadow for depth
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(40)
        shadow.setColor(QColor(0, 0, 0, 35))
        shadow.setOffset(0, 4)
        self.glass_bg.setGraphicsEffect(shadow)
        
        # Horizontal Content Layout
        card_content_layout = QHBoxLayout(self.glass_bg)
        card_content_layout.setContentsMargins(12, 12, 12, 12)
        card_content_layout.setSpacing(16)
        card_content_layout.setAlignment(Qt.AlignVCenter)
        
        # Left: Thumbnail (Slightly smaller for compactness)
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(180, 101) # 16:9 aspect ratio
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setText("No Thumbnail")
        card_content_layout.addWidget(self.thumbnail_label)
        
        # Center: Video Details (Vertically centered)
        details_column = QVBoxLayout()
        details_column.setSpacing(2)
        details_column.setAlignment(Qt.AlignVCenter)
        
        self.title_label = QLabel("Video Title")
        self.title_label.setFont(QFont("SF Pro Display", 15, QFont.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(40)
        details_column.addWidget(self.title_label)
        
        # Metadata Row: Logo/Platform • Channel • 4:32
        metadata_row = QHBoxLayout()
        metadata_row.setSpacing(6)
        
        self.platform_icon = QLabel("")
        self.platform_icon.setFont(QFont("SF Pro Display", 14))
        metadata_row.addWidget(self.platform_icon)
        
        self.uploader_label = QLabel("Channel")
        self.uploader_label.setFont(QFont("SF Pro Display", 12))
        metadata_row.addWidget(self.uploader_label)
        
        self.separator = QLabel("•")
        self.separator.setStyleSheet("color: #888;")
        metadata_row.addWidget(self.separator)
        
        self.duration_label = QLabel("0:00")
        self.duration_label.setFont(QFont("SF Pro Display", 12))
        metadata_row.addWidget(self.duration_label)
        
        metadata_row.addStretch()
        details_column.addLayout(metadata_row)
        
        # Quality Row
        self.quality_row = QLabel("Quality: Auto Best Available")
        self.quality_row.setFont(QFont("SF Pro Display", 13))
        details_column.addWidget(self.quality_row)
        
        card_content_layout.addLayout(details_column, 1)
        
        # Right: Download Button (Vertically centered)
        self.download_btn = QPushButton("↓ Download")
        self.download_btn.setFixedHeight(48)
        self.download_btn.setFixedWidth(140)
        self.download_btn.setCursor(Qt.PointingHandCursor)
        self.download_btn.clicked.connect(self.download_clicked.emit)
        card_content_layout.addWidget(self.download_btn)
        
        glass_layout.addWidget(self.glass_bg)
    
    def update_styles(self, colors: dict):
        """Update styles for the preview card based on the current theme colors"""
        # Glass background widget
        self.glass_bg.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['card_glass']};
                border: 1px solid {colors['card_border']};
                border-radius: 16px;
            }}
        """)
        
        # Thumbnail with rounded corners
        self.thumbnail_label.setStyleSheet(f"""
            QLabel {{
                background-color: {colors['glass_hover']};
                border-radius: 12px;
                color: {colors['text_secondary']};
            }}
        """)
        
        # Text elements
        self.title_label.setStyleSheet(f"color: {colors['text_primary']};")
        self.uploader_label.setStyleSheet(f"color: {colors['text_secondary']};")
        self.duration_label.setStyleSheet(f"color: {colors['text_secondary']};")
        self.quality_row.setStyleSheet(f"color: {colors['text_secondary']};")
        
        # Download button styling (more prominent like the reference)
        self.download_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 17px;
                font-weight: 600;
                box-shadow: 0 4px 15px {colors['primary']}40;
            }}
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}
            QPushButton:disabled {{
                background-color: {colors['border']};
                color: {colors['text_tertiary']};
            }}
        """)
    
    def update_metadata(self, metadata: VideoMetadata):
        """Update card with metadata"""
        self._metadata = metadata
        self.title_label.setText(metadata.title)
        
        # Platform icons (Emojis for simplicity and compliance with "no text" rule)
        platform_icons = {
            'YouTube': '🔴',
            'Instagram': '📸',
            'Facebook': '📘',
            'X': '𝕏',
            'TikTok': '🎵',
            'Unknown': '🔗'
        }
        self.platform_icon.setText(platform_icons.get(metadata.platform, '🔗'))
        
        self.uploader_label.setText(metadata.uploader)
        
        # Format duration (cast to int to avoid float format errors)
        duration = int(metadata.duration or 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.setText(f"{minutes}:{seconds:02d}")
        
        self.quality_row.setText(f"Quality: Auto Best Available")
        
        if metadata.thumbnail:
            self.load_thumbnail(metadata.thumbnail)
    
    def load_thumbnail(self, url: str):
        """Load thumbnail from URL"""
        self._thumbnail_thread = ThumbnailFetchThread(url)
        thread = self._thumbnail_thread
        if thread:
            thread.finished.connect(self._on_thumbnail_loaded)
            thread.error.connect(self._on_thumbnail_error)
            thread.start()
    
    def _on_thumbnail_loaded(self, pixmap: QPixmap):
        """Handle thumbnail loaded"""
        self.thumbnail_label.setText("")
        self.thumbnail_label.setPixmap(pixmap.scaled(
            self.thumbnail_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.thumbnail_label.setStyleSheet("")
    
    def _on_thumbnail_error(self, error: str):
        """Handle thumbnail load error"""
        self.thumbnail_label.setText(f"Thumbnail\nunavailable")
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #F5F5F7;
                border-radius: 12px;
                color: #98989D;
                font-size: 12px;
            }
        """)

    def get_selected_quality(self) -> VideoQuality:
        """Always return BEST for auto quality"""
        return VideoQuality.BEST


class MainWindow(QMainWindow):
    """Main application window - macOS 26 (Sequoia) Design"""

    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.engine = YtDlpEngine()
        self.queue_manager = QueueManager(max_concurrent=1)
        self.queue_manager.queue_updated.connect(self._on_queue_update)
        self.history_manager = HistoryManager()
        self.settings_manager = SettingsManager()
        self.clipboard_monitor = ClipboardMonitor(check_interval=2.0)
        
        # Theme manager with app reference
        from PySide6.QtWidgets import QApplication  # pyre-ignore[21]
        self.theme_manager = ThemeManager(QApplication.instance())
        
        # State
        self._metadata_thread: Optional[MetadataFetcherThread] = None
        self._current_metadata: Optional[VideoMetadata] = None
        self._thumbnail_thread: Optional[ThumbnailFetchThread] = None
        
        # Setup UI
        self.setup_ui()
        self.setup_connections()
        
        # Apply initial theme
        self._update_styles()
        
        logger.info("MainWindow initialized with macOS 26 design")
        
    def _update_styles(self):
        """Update stylesheets for all child widgets dynamically based on the current theme"""
        mode = self.theme_manager.get_current_mode()
        
        # Determine the appearance context (System resolves to either Light or Dark in PySide)
        is_dark = self.theme_manager.is_dark_mode()
        if mode == ThemeMode.SYSTEM:
            # We must force a choice for CSS elements based on is_dark_mode calculation
            colors = macOSColors.DARK if is_dark else macOSColors.LIGHT
        elif mode == ThemeMode.DARK:
            colors = macOSColors.DARK
        else:
            colors = macOSColors.LIGHT
            
        # Update Main Window Background
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {colors['window_bg']};
            }}
        """)
        
        # Update Header Title
        self.title_label_ref.setStyleSheet(f"color: {colors['text_primary']};")
        
        # Update Theme Button
        self.theme_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {colors['glass_bg']};
                border: 1px solid {colors['glass_border']};
                border-radius: 20px;
                font-size: 20px;
                color: {colors['text_primary']};
            }}
            QToolButton:hover {{
                background-color: {colors['glass_hover']};
                border-color: {colors['glass_focus']};
            }}
            QToolButton:pressed {{
                background-color: {colors['glass_pressed']};
            }}
        """)
        
        # Update URL Input
        self.url_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {colors['glass_bg']};
                border: 1px solid {colors['glass_border']};
                border-radius: 12px;
                padding: 0 18px;
                color: {colors['text_primary']};
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {colors['glass_focus']};
                background-color: {colors['card_glass']};
            }}
        """)
        
        # Update Fetch Button
        self.fetch_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {colors['primary']};
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px;
                font-size: 15px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {colors['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['primary']};
            }}
            QPushButton:disabled {{
                background-color: {colors['border']};
            }}
        """)
        
        # Update Status Widget
        self.status_widget.update_styles(colors)
        
        # Control Buttons Container Styles
        btn_style = f"""
            QPushButton {{
                background-color: {colors['glass_bg']};
                color: {colors['text_primary']};
                border: 1px solid {colors['glass_border']};
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {colors['glass_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['glass_pressed']};
            }}
        """
        self.pause_all_btn.setStyleSheet(btn_style)
        self.cancel_all_btn.setStyleSheet(btn_style)
        self.settings_btn.setStyleSheet(btn_style)
        self.history_btn.setStyleSheet(btn_style)
        self.about_btn.setStyleSheet(btn_style)
        
        # Propagate to sub-widgets
        self.preview_card.update_styles(colors)
        

    
    def _apply_light_theme(self):
        """Deprecated: Styles now managed by _update_styles()"""
        pass
    
    def _apply_dark_theme(self):
        """Deprecated: Styles now managed by _update_styles()"""
        pass
    
    def setup_ui(self):
        """Setup the main window UI - macOS 26 Design"""
        self.setWindowTitle("SMdown - video downloader")
        self.setMinimumSize(850, 700)
        self.resize(950, 750)
        
        # Central widget
        central = QWidget() # pyre-ignore[20]
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        
        # Header with title and theme toggle
        header_layout = QHBoxLayout() # pyre-ignore[20]
        header_layout.setSpacing(16)
        
        # App title
        self.title_label_ref = QLabel("SMdown - video downloader")
        self.title_label_ref.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        header_layout.addWidget(self.title_label_ref)
        
        header_layout.addStretch()
        
        # Theme toggle button - with Liquid Glass effect
        self.theme_btn = QToolButton()
        self.theme_btn.setFixedSize(40, 40)
        self.theme_btn.setText("☀️")
        self.theme_btn.setToolTip("Toggle Theme (Light/Dark/System)")
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(self.theme_btn)
        
        main_layout.addLayout(header_layout)
        
        # URL Input Section with Liquid Glass
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste a YouTube, Facebook, Instagram, or X video link...")
        self.url_input.setFont(QFont("SF Pro Display", 14))
        self.url_input.setFixedHeight(48)
        self.url_input.setAttribute(Qt.WA_TranslucentBackground, True)
        input_layout.addWidget(self.url_input, 1)
        
        self.fetch_btn = QPushButton("Fetch")
        self.fetch_btn.setFixedHeight(48)
        self.fetch_btn.setFixedWidth(110)
        input_layout.addWidget(self.fetch_btn)
        
        main_layout.addLayout(input_layout)
        
        # Preview Card
        self.preview_card = PreviewCard()
        self.preview_card.download_clicked.connect(self._on_download_clicked)
        self.preview_card.hide()
        main_layout.addWidget(self.preview_card)
        
        # Download Status Section (Narrow and Centered)
        status_row = QHBoxLayout()
        status_row.addStretch()
        
        self.status_widget = DownloadStatusWidget()
        self.status_widget.setMaximumWidth(600)
        self.status_widget.hide()
        
        status_row.addWidget(self.status_widget)
        status_row.addStretch()
        main_layout.addLayout(status_row)
        
        # Global Controls Bar with Liquid Glass
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)
        
        # Left controls
        self.pause_all_btn = QPushButton("⏸ Pause All")
        self.pause_all_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(245, 245, 247, 0.6);
                color: #1D1D1F;
                border: 1px solid rgba(210, 210, 215, 0.4);
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(229, 229, 234, 0.7);
            }
            QPushButton:pressed {
                background-color: rgba(210, 210, 215, 0.5);
            }
        """)
        self.pause_all_btn.hide()
        controls_layout.addWidget(self.pause_all_btn)
        
        self.cancel_all_btn = QPushButton("✕ Cancel All")
        self.cancel_all_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(245, 245, 247, 0.6);
                color: #1D1D1F;
                border: 1px solid rgba(210, 210, 215, 0.4);
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(229, 229, 234, 0.7);
            }
            QPushButton:pressed {
                background-color: rgba(210, 210, 215, 0.5);
            }
        """)
        self.cancel_all_btn.hide()
        controls_layout.addWidget(self.cancel_all_btn)
        
        controls_layout.addStretch()
        
        # Settings button
        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(245, 245, 247, 0.6);
                color: #1D1D1F;
                border: 1px solid rgba(210, 210, 215, 0.4);
                padding: 12px 18px;
                border-radius: 10px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(229, 229, 234, 0.7);
            }
            QPushButton:pressed {
                background-color: rgba(210, 210, 215, 0.5);
            }
        """)
        controls_layout.addWidget(self.settings_btn)
        
        self.history_btn = QPushButton("📜 History")
        controls_layout.addWidget(self.history_btn)
        
        # About button
        self.about_btn = QPushButton("ⓘ About")
        controls_layout.addWidget(self.about_btn)
        
        main_layout.addLayout(controls_layout)
    
    def setup_connections(self):
        """Setup signal/slot connections"""
        self.fetch_btn.clicked.connect(self._on_fetch_clicked)
        self.url_input.returnPressed.connect(self._on_fetch_clicked)
        
        # Theme toggle - use clicked signal
        self.theme_btn.clicked.connect(self._on_theme_toggle)
        
        self.pause_all_btn.clicked.connect(self._on_pause_all)
        self.cancel_all_btn.clicked.connect(self._on_cancel_all)
        self.settings_btn.clicked.connect(self._on_settings_clicked)
        self.history_btn.clicked.connect(self._on_history_clicked)
        self.about_btn.clicked.connect(self._on_about_clicked)
        
        # Start clipboard monitor
        self.clipboard_monitor.start(self._on_clipboard_video_detected)
    
    def _on_theme_toggle(self):
        """Handle theme toggle button click"""
        current = self.theme_manager.get_current_mode()
        
        # Cycle: Light -> Dark -> System -> Light
        if current == ThemeMode.LIGHT:
            new_mode = ThemeMode.DARK
            icon = "🌙"
            self._apply_dark_theme()
        elif current == ThemeMode.DARK:
            new_mode = ThemeMode.SYSTEM
            icon = "⚙"
            # System theme - use light as default
            self._apply_light_theme()
        else:
            new_mode = ThemeMode.LIGHT
            icon = "☀️"
            self._apply_light_theme()
        
        # Instead of directly changing the palette, we invoke _update_styles()
        # to ensure all custom glass widgets get repainted properly.
        self.theme_manager.set_theme(new_mode)
        self.theme_btn.setText(icon)
        self._update_styles()
        logger.info("Theme toggled to: %s", new_mode.value)
    
    def _on_fetch_clicked(self):
        """Handle fetch button click"""
        url = self.url_input.text().strip()
        
        # Validate URL
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a video URL")
            return
        
        # Check if URL is from supported platform
        if not self.engine.is_supported_url(url):
            platform = self.engine.detect_platform(url)
            QMessageBox.critical(
                self, 
                "Unsupported Platform",
                f"This URL is from '{platform}' which is not supported.\n\n"
                f"Supported platforms:\n"
                f"• YouTube\n"
                f"• Facebook\n"
                f"• Instagram\n"
                f"• X (Twitter)\n"
                f"• TikTok"
            )
            # Auto-clear invalid URL
            self.url_input.clear()
            self.url_input.setFocus()
            return

        logger.info("Fetching metadata for: %s", url)
        
        # Disable buttons during fetch
        self._set_ui_busy(True)
        
        self._metadata_thread = MetadataFetcherThread(url)
        thread = self._metadata_thread
        if thread:
            thread.finished.connect(self._on_metadata_fetched)
            thread.error.connect(self._on_metadata_error)
            thread.start()

    def _on_metadata_fetched(self, metadata: VideoMetadata):
        """Handle metadata fetch completion"""
        logger.info("Metadata fetched: %s", metadata.title)
        
        self._current_metadata = metadata
        self.preview_card.update_metadata(metadata)
        self.preview_card.show()

        # Re-enable UI
        self._set_ui_busy(False)
    
    def _on_metadata_error(self, error: str):
        """Handle metadata fetch error"""
        logger.error("Failed to fetch metadata: %s", error)
        
        QMessageBox.critical(self, "Error", f"Failed to fetch video info:\n{error}")
        
        # Re-enable UI and clear input
        self._set_ui_busy(False)
        self.url_input.clear()
        self.url_input.setFocus()
    
    def _set_ui_busy(self, busy: bool):
        """Enable/disable UI elements during operations"""
        self.fetch_btn.setEnabled(not busy)
        self.fetch_btn.setText("Fetching..." if busy else "Fetch")
        
        # Disable URL input during fetch/download
        self.url_input.setEnabled(not busy)
        
        # Disable download button when fetching
        if busy:
            self.preview_card.download_btn.setEnabled(False)
        else:
            # Enable download only if we have metadata
            self.preview_card.download_btn.setEnabled(self._current_metadata is not None)
    
    def _set_download_ui_busy(self, busy: bool):
        """Enable/disable UI elements specifically during download"""
        # Disable URL input and fetch button
        self.url_input.setEnabled(not busy)
        self.fetch_btn.setEnabled(not busy)
        
        # Disable download button
        self.preview_card.download_btn.setEnabled(not busy)
        
        if busy:
            self.preview_card.download_btn.setText("⬇ Downloading...")
        else:
            self.preview_card.download_btn.setText("⬇ Download")
    
    def _on_clipboard_video_detected(self, url: str):
        """Handle video URL detected from clipboard"""
        logger.info("Clipboard: Video URL detected - %s", url)
    
    def _on_download_clicked(self):
        """Handle download button click from preview card"""
        metadata = self._current_metadata
        if not metadata:
            logger.warning("Download clicked without metadata")
            return

        url = metadata.url
        output_path = self.settings_manager.get_download_path()
        quality = VideoQuality.BEST  # Always use auto quality

        logger.info("Download started: %s (quality=AUTO)", metadata.title)

        # Disable UI during download
        self._set_download_ui_busy(True)

        # Add to queue with BEST quality - platform will auto-select
        self.queue_manager.add_to_queue(
            url=url,
            quality=quality,
            output_path=output_path,
            metadata=self._current_metadata,
        )

        # Show download status and controls
        self.status_widget.show()
        self.pause_all_btn.show()
        self.cancel_all_btn.show()

        # Start queue processing in background thread
        self._start_queue_thread()

    def _start_queue_thread(self):
        """Start queue processing in background thread to prevent UI freeze"""
        def process_queue():
            try:
                self.queue_manager.start_queue()
                # Trigger UI update from main thread
                QTimer.singleShot(0, self._refresh_queue_list)
            except Exception as e:
                logger.error("Queue processing error: %s", e)
                QTimer.singleShot(0, lambda: QMessageBox.critical(
                    self, "Download Error", f"Failed to start download:\n{str(e)}"
                ))

        thread = threading.Thread(target=process_queue, daemon=True)
        thread.start()
    
    def _on_queue_update(self, event: str, item: Optional[QueueItem]):
        """Handle queue manager updates"""
        # Always update UI from main thread using QTimer
        if event in ['item_added', 'item_removed']:
            QTimer.singleShot(0, self._refresh_queue_list)
        elif event in ['progress_updated', 'item_updated'] and item:
            # We must create a copy of the item data or capture its ID to pass it to the timer safely
            item_id = item.id
            QTimer.singleShot(0, lambda: self._update_queue_item_progress(item_id))
        
        # Check for completed downloads
        if event == 'item_updated' and item:
            if item.status in [QueueItemStatus.COMPLETED, QueueItemStatus.ERROR, QueueItemStatus.CANCELLED]:
                # Download finished - re-enable UI and clear input
                QTimer.singleShot(0, self._on_download_finished)
            
            if item.status == QueueItemStatus.COMPLETED and item.metadata:
                self.history_manager.add_item(
                    url=item.url,
                    title=item.metadata.title,
                    platform=item.metadata.platform,
                    quality=item.quality.name,
                    file_path=item.filename or "",
                    file_size=0,
                    thumbnail=item.metadata.thumbnail,
                    duration=item.metadata.duration,
                )
                logger.info("Added to history: %s", item.metadata.title)
                self._show_notification("Download Complete", f"{item.metadata.title} has finished downloading.")
                
    def _show_notification(self, title: str, message: str):
        """Show native macOS notification"""
        try:
            # Escape double quotes for AppleScript
            safe_title = title.replace('"', '\\"')
            safe_message = message.replace('"', '\\"')
            script = f'display notification "{safe_message}" with title "{safe_title}"'
            subprocess.run(["osascript", "-e", script], check=False)
        except Exception as e:
            logger.error("Failed to show notification: %s", e)
    
    def _on_download_finished(self):
        """Called when download completes - re-enable UI and clear input"""
        # Re-enable UI
        self._set_download_ui_busy(False)
        
        # Hide download controls
        self.pause_all_btn.hide()
        self.cancel_all_btn.hide()
        
        # Clear URL input
        self.url_input.clear()
        
        # Clear current metadata
        self._current_metadata = None
        
        # Hide preview and status to return to minimalist state
        self.preview_card.hide()
        self.status_widget.hide()
        
        logger.info("Download finished - UI reset and elements hidden")

    def _refresh_queue_list(self):
        """Refresh the status widget with the active download status"""
        queue_items = self.queue_manager.get_queue()
        
        # Find active or wait for a specific item to display
        active_item = next((i for i in queue_items if i.status == QueueItemStatus.DOWNLOADING), None)
        
        # If no downloading item, show the most recent or completed
        if not active_item and queue_items:
            active_item = queue_items[-1]
            
        # Determine current color schema
        is_dark = self.theme_manager.is_dark_mode()
        mode = self.theme_manager.get_current_mode()
        if mode == ThemeMode.SYSTEM:
            colors = macOSColors.DARK if is_dark else macOSColors.LIGHT
        elif mode == ThemeMode.DARK:
            colors = macOSColors.DARK
        else:
            colors = macOSColors.LIGHT
        
        if active_item:
            self.status_widget.update(active_item, colors)
            
            # Show/Hide controls based on active download
            if active_item.status == QueueItemStatus.DOWNLOADING:
                self.pause_all_btn.show()
                self.cancel_all_btn.show()
            else:
                self.pause_all_btn.hide()
                self.cancel_all_btn.hide()
        else:
            self.status_widget.status_label.setText("[SYSTEM: IDLE] - Ready for input...")
            self.status_widget.progress_bar.setValue(0)
            self.pause_all_btn.hide()
            self.cancel_all_btn.hide()
            self.status_widget.update_styles(colors)
            
    def _update_queue_item_progress(self, item_id: int):
        """Update the status widget's progress"""
        # Get the latest state of the item from the queue manager
        queue_items = self.queue_manager.get_queue()
        target_item = next((i for i in queue_items if i.id == item_id), None)
        
        if not target_item:
            return
            
        # Determine current color schema
        is_dark = self.theme_manager.is_dark_mode()
        mode = self.theme_manager.get_current_mode()
        if mode == ThemeMode.SYSTEM:
            colors = macOSColors.DARK if is_dark else macOSColors.LIGHT
        elif mode == ThemeMode.DARK:
            colors = macOSColors.DARK
        else:
            colors = macOSColors.LIGHT
            
        # We only update if this is the currently tracked item or a new active item
        if self.status_widget.item_id == item_id or target_item.status == QueueItemStatus.DOWNLOADING:
            self.status_widget.update(target_item, colors)
    
    def _on_queue_item_cancel(self, item_id: int):
        """Handle queue item cancel"""
        self.queue_manager.cancel_item(item_id)
        self._refresh_queue_list()

    def _on_queue_item_pause(self, item_id: int):
        """Handle queue item pause"""
        self.queue_manager.pause_item(item_id)
        self._refresh_queue_list()

    def _on_queue_item_resume(self, item_id: int):
        """Handle queue item resume"""
        self.queue_manager.resume_item(item_id)
        self._refresh_queue_list()
        self.queue_manager.start_queue()
    
    def _on_pause_all(self):
        """Pause all downloads"""
        queue = self.queue_manager.get_queue()
        for item in queue:
            if item.status == QueueItemStatus.DOWNLOADING:
                self.queue_manager.pause_item(item.id)
        self._refresh_queue_list()
        logger.info("Paused all downloads")
    
    def _on_cancel_all(self):
        """Cancel all waiting/paused downloads"""
        queue = self.queue_manager.get_queue()
        for item in queue:
            if item.status in [QueueItemStatus.WAITING, QueueItemStatus.PAUSED]:
                self.queue_manager.cancel_item(item.id)
        self._refresh_queue_list()
        logger.info("Cancelled all pending downloads")
    
    def _on_history_clicked(self):
        """Show history dialog"""
        dialog = HistoryDialog(self.history_manager, self)
        dialog.exec()
    
    def _on_about_clicked(self):
        """Show about dialog"""
        # Determine current color schema
        is_dark = self.theme_manager.is_dark_mode()
        mode = self.theme_manager.get_current_mode()
        if mode == ThemeMode.SYSTEM:
            colors = macOSColors.DARK if is_dark else macOSColors.LIGHT
        elif mode == ThemeMode.DARK:
            colors = macOSColors.DARK
        else:
            colors = macOSColors.LIGHT
            
        dialog = AboutDialog(colors, self)
        dialog.exec()
    
    def _on_settings_clicked(self):
        """Show settings dialog"""
        current_path = self.settings_manager.get_download_path()
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Settings")
        dialog.setText("Download Location Settings")
        dialog.setInformativeText(f"Current: {current_path}")
        dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        change_btn = dialog.addButton("Change Location", QMessageBox.ActionRole)
        
        result = dialog.exec()
        
        if dialog.clickedButton() == change_btn:
            directory = QFileDialog.getExistingDirectory(
                self, "Select Download Directory", current_path
            )
            if directory:
                self.settings_manager.set_download_path(directory)
                QMessageBox.information(
                    self, "Settings Updated",
                    f"Download location changed to:\n{directory}"
                )
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.clipboard_monitor.stop()
        self.theme_manager.save_theme(self.theme_manager.get_current_mode())
        event.accept()
