"""
Main Window UI Component
PySide6 based main window for SMdown
"""

import os
import re
import logging
from typing import Optional, Callable, List
from datetime import datetime

import requests  # pyre-ignore[21]

from PySide6.QtWidgets import (  # pyre-ignore[21]
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QProgressBar,
    QComboBox, QFrame, QScrollArea, QListWidget, QListWidgetItem,
    QRadioButton, QButtonGroup, QFileDialog, QMessageBox,
    QGroupBox, QSplitter, QTextEdit, QSizePolicy, QSpacerItem,
)
from PySide6.QtCore import Qt, Signal, Slot, QThread, QUrl as QUrlCore, QTimer  # pyre-ignore[21]
from PySide6.QtGui import QPixmap, QFont, QIcon, QDesktopServices  # pyre-ignore[21]

from app.downloader.yt_dlp_engine import YtDlpEngine, VideoQuality, VideoMetadata, DownloadProgress  # pyre-ignore[21]
from app.downloader.queue_manager import QueueManager, QueueItem, QueueItemStatus  # pyre-ignore[21]
from app.utils.file_manager import FileManager  # pyre-ignore[21]
from app.services.clipboard_monitor import ClipboardMonitor  # pyre-ignore[21]

logger = logging.getLogger(__name__)


class ThumbnailFetchThread(QThread):
    """Thread for fetching thumbnail image"""
    finished = Signal(object)  # QPixmap or None
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
    finished = Signal(object)  # VideoMetadata or None
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


class DownloadWorkerThread(QThread):
    """Thread for downloading video"""
    progress = Signal(object)  # DownloadProgress
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self, url: str, output_path: str, quality: VideoQuality):
        super().__init__()
        self.url = url
        self.output_path = output_path
        self.quality = quality
        self.engine = YtDlpEngine()
        
    def run(self):
        def progress_callback(progress: DownloadProgress):
            self.progress.emit(progress)
            
        success = self.engine.download(
            url=self.url,
            output_path=self.output_path,
            quality=self.quality,
            progress_callback=progress_callback,
        )
        
        if success:
            self.finished.emit(True)
        else:
            self.error.emit("Download failed")


class VideoInfoWidget(QWidget):
    """Widget to display video information"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Thumbnail
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(320, 180)
        self.thumbnail_label.setAlignment(Qt.AlignCenter)
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a2e;
                border-radius: 8px;
                color: #666;
            }
        """)
        self.thumbnail_label.setText("No Thumbnail")
        layout.addWidget(self.thumbnail_label, alignment=Qt.AlignCenter)
        
        # Video details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(8)
        
        # Title
        self.title_label = QLabel("Video Title")
        self.title_label.setFont(QFont(".AppleSystemUIFont", 16, QFont.Bold))
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("color: #ffffff;")
        details_layout.addWidget(self.title_label)
        
        # Uploader
        self.uploader_label = QLabel("Channel / Uploader")
        self.uploader_label.setStyleSheet("color: #888; font-size: 13px;")
        details_layout.addWidget(self.uploader_label)
        
        # Duration and Platform
        info_layout = QHBoxLayout()
        info_layout.setSpacing(15)
        
        self.duration_label = QLabel("Duration: --:--")
        self.duration_label.setStyleSheet("color: #888; font-size: 13px;")
        info_layout.addWidget(self.duration_label)
        
        self.platform_label = QLabel("Platform: --")
        self.platform_label.setStyleSheet("color: #888; font-size: 13px;")
        info_layout.addWidget(self.platform_label)
        
        info_layout.addStretch()
        details_layout.addLayout(info_layout)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
    def update_metadata(self, metadata: VideoMetadata):
        """Update widget with video metadata"""
        self.title_label.setText(metadata.title)
        self.uploader_label.setText(metadata.uploader)

        # Format duration (safety cast to int)
        duration = int(metadata.duration or 0)
        minutes = duration // 60
        seconds = duration % 60
        self.duration_label.setText(f"Duration: {minutes}:{seconds:02d}")

        self.platform_label.setText(f"Platform: {metadata.platform}")

        # Load thumbnail
        if metadata.thumbnail:
            self.load_thumbnail(metadata.thumbnail)
            
    def load_thumbnail(self, url: str):
        """Load thumbnail from URL"""
        # Fetch thumbnail in background thread
        self._thumbnail_thread = ThumbnailFetchThread(url)
        self._thumbnail_thread.finished.connect(self._on_thumbnail_loaded)
        self._thumbnail_thread.error.connect(self._on_thumbnail_error)
        self._thumbnail_thread.start()

    def _on_thumbnail_loaded(self, pixmap: QPixmap):
        """Handle thumbnail loaded"""
        self.thumbnail_label.setText("")
        self.thumbnail_label.setPixmap(pixmap.scaled(
            self.thumbnail_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a3e;
                border-radius: 8px;
            }
        """)

    def _on_thumbnail_error(self, error: str):
        """Handle thumbnail load error"""
        self.thumbnail_label.setText(f"Thumbnail unavailable\n({error})")
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #2a2a3e;
                border-radius: 8px;
                color: #888;
                font-size: 11px;
            }
        """)
        
    def reset(self):
        """Reset widget to default state"""
        self.thumbnail_label.setText("No Thumbnail")
        self.thumbnail_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a2e;
                border-radius: 8px;
                color: #666;
            }
        """)
        self.title_label.setText("Video Title")
        self.uploader_label.setText("Channel / Uploader")
        self.duration_label.setText("Duration: --:--")
        self.platform_label.setText("Platform: --")


class AutoQualityLabel(QWidget):
    """Widget showing auto quality status"""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Quality info box
        self.quality_box = QFrame()
        self.quality_box.setStyleSheet("""
            QFrame {
                background-color: #1a1a2e;
                border: 2px solid #00d4aa;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        box_layout = QVBoxLayout(self.quality_box)
        box_layout.setSpacing(4)

        # Title with icon
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        icon = QLabel("⚡")
        icon.setStyleSheet("font-size: 18px;")
        title_layout.addWidget(icon)
        
        title = QLabel("Auto Quality")
        title.setFont(QFont(".AppleSystemUIFont", 13, QFont.Bold))
        title.setStyleSheet("color: #00d4aa;")
        title_layout.addWidget(title)
        
        title_layout.addStretch()
        box_layout.addLayout(title_layout)

        # Description
        desc = QLabel("Video will be downloaded in best available quality automatically")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #888; font-size: 12px;")
        box_layout.addWidget(desc)

        # Platform-specific quality
        self.platform_quality_label = QLabel("")
        self.platform_quality_label.setWordWrap(True)
        self.platform_quality_label.setStyleSheet("color: #aaa; font-size: 11px; margin-top: 4px;")
        box_layout.addWidget(self.platform_quality_label)

        layout.addWidget(self.quality_box)

    def update_platform_quality(self, platform: str):
        """Update label with platform-specific quality"""
        quality_map = {
            'YouTube': '1080p (Full HD)',
            'Facebook': 'Best Available',
            'Instagram': 'Best Available',
            'X': 'Best Available',
            'TikTok': 'Best Available',
            'Unknown': 'Best Available',
        }
        quality = quality_map.get(platform, 'Best Available')
        self.platform_quality_label.setText(f"📍 {platform}: {quality}")


class QueueItemWidget(QWidget):
    """Widget for displaying a single queue item"""
    
    cancel_clicked = Signal(int)
    pause_clicked = Signal(int)
    resume_clicked = Signal(int)
    
    def __init__(self, item: QueueItem):
        super().__init__()
        self.item = item
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a3e;
                border-radius: 8px;
            }
            QWidget:hover {
                background-color: #32324a;
            }
        """)
        
        # Title and status
        title_layout = QHBoxLayout()
        
        self.title_label = QLabel(self.item.metadata.title if self.item.metadata else "Fetching...")
        self.title_label.setFont(QFont(".AppleSystemUIFont", 12, QFont.Bold))
        self.title_label.setStyleSheet("color: #ffffff;")
        self.title_label.setWordWrap(True)
        title_layout.addWidget(self.title_label)
        
        # Status indicator
        self.status_label = QLabel(self._get_status_text())
        self.status_label.setStyleSheet(f"""
            color: {self._get_status_color()};
            font-size: 11px;
            padding: 2px 8px;
            background-color: #1a1a2e;
            border-radius: 4px;
        """)
        title_layout.addWidget(self.status_label)
        
        layout.addLayout(title_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(int(self.item.progress))
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1a1a2e;
                border-radius: 4px;
                text-align: center;
                color: #fff;
            }
            QProgressBar::chunk {
                background-color: #00d4aa;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Info and actions
        info_layout = QHBoxLayout()
        
        self.info_label = QLabel(f"{self.item.speed} | ETA: {self.item.eta}")
        self.info_label.setStyleSheet("color: #888; font-size: 11px;")
        info_layout.addWidget(self.info_label)
        
        info_layout.addStretch()
        
        # Action buttons
        if self.item.status == QueueItemStatus.DOWNLOADING:
            self.pause_btn = QPushButton("⏸ Pause")
            self.pause_btn.clicked.connect(lambda: self.pause_clicked.emit(self.item.id))
            self.pause_btn.setStyleSheet(self._button_style("#ffa500"))
            info_layout.addWidget(self.pause_btn)
            
            self.cancel_btn = QPushButton("⏹ Cancel")
            self.cancel_btn.clicked.connect(lambda: self.cancel_clicked.emit(self.item.id))
            self.cancel_btn.setStyleSheet(self._button_style("#ff4444"))
            info_layout.addWidget(self.cancel_btn)
        elif self.item.status == QueueItemStatus.PAUSED:
            self.resume_btn = QPushButton("▶ Resume")
            self.resume_btn.clicked.connect(lambda: self.resume_clicked.emit(self.item.id))
            self.resume_btn.setStyleSheet(self._button_style("#00d4aa"))
            info_layout.addWidget(self.resume_btn)
        
        layout.addLayout(info_layout)
        
    def _button_style(self, color: str) -> str:
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 4px;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
        """
        
    def _get_status_text(self) -> str:
        status_map = {
            QueueItemStatus.WAITING: "Waiting",
            QueueItemStatus.DOWNLOADING: "Downloading",
            QueueItemStatus.PAUSED: "Paused",
            QueueItemStatus.COMPLETED: "Completed",
            QueueItemStatus.ERROR: "Error",
            QueueItemStatus.CANCELLED: "Cancelled",
        }
        return status_map.get(self.item.status, "Unknown")
    
    def _get_status_color(self) -> str:
        color_map = {
            QueueItemStatus.WAITING: "#888888",
            QueueItemStatus.DOWNLOADING: "#00d4aa",
            QueueItemStatus.PAUSED: "#ffa500",
            QueueItemStatus.COMPLETED: "#44aa44",
            QueueItemStatus.ERROR: "#ff4444",
            QueueItemStatus.CANCELLED: "#666666",
        }
        return color_map.get(self.item.status, "#888888")
    
    def update(self, item: QueueItem):
        """Update widget with new item data"""
        self.item = item
        self.title_label.setText(item.metadata.title if item.metadata else "Fetching...")
        self.status_label.setText(self._get_status_text())
        self.status_label.setStyleSheet(f"""
            color: {self._get_status_color()};
            font-size: 11px;
            padding: 2px 8px;
            background-color: #1a1a2e;
            border-radius: 4px;
        """)
        self.progress_bar.setValue(int(item.progress))
        
        if item.status == QueueItemStatus.DOWNLOADING:
            self.info_label.setText(f"{item.speed} | ETA: {item.eta}")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        logger.debug("Initializing MainWindow")
        
        self.engine = YtDlpEngine()
        self.queue_manager = QueueManager(max_concurrent=1)
        self.queue_manager.set_download_callback(self._on_queue_update)

        self._metadata_thread: Optional[MetadataFetcherThread] = None
        self._download_thread: Optional[DownloadWorkerThread] = None
        self._current_metadata: Optional[VideoMetadata] = None

        # Clipboard monitor
        self.clipboard_monitor = ClipboardMonitor(check_interval=2.0)
        self._clipboard_enabled = False

        # Thumbnail fetcher
        self._thumbnail_thread: Optional[ThumbnailFetchThread] = None

        self.setup_ui()
        self.setup_connections()
        
        logger.info("MainWindow initialized successfully")
        
    def setup_ui(self):
        """Setup the main window UI"""
        self.setWindowTitle("SMdown - Universal Video Downloader")
        self.setMinimumSize(900, 700)
        self.resize(1000, 750)
        
        # Apply dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        title = QLabel("🎬 SMdown")
        title.setFont(QFont(".AppleSystemUIFont", 28, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(title)
        
        subtitle = QLabel("Universal Video Downloader for macOS")
        subtitle.setStyleSheet("color: #888; font-size: 14px;")
        header_layout.addWidget(subtitle)
        
        main_layout.addLayout(header_layout)
        
        # URL Input Section
        url_section = self._create_url_section()
        main_layout.addWidget(url_section)
        
        # Splitter for video info and queue
        splitter = QSplitter(Qt.Vertical)
        
        # Video Info Section
        video_info_widget = QWidget()
        video_info_layout = QVBoxLayout(video_info_widget)
        video_info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_info = VideoInfoWidget()
        video_info_layout.addWidget(self.video_info)
        
        # Quality selection and download button
        control_widget = self._create_control_section()
        video_info_layout.addWidget(control_widget)
        
        splitter.addWidget(video_info_widget)
        
        # Queue Section
        queue_widget = self._create_queue_section()
        splitter.addWidget(queue_widget)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
    def _create_url_section(self) -> QWidget:
        """Create URL input section"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #2a2a3e;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)
        
        # Input field
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste video link here (YouTube, Facebook, Instagram, X...)")
        self.url_input.setFont(QFont(".AppleSystemUIFont", 13))
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a2e;
                border: 2px solid #3a3a5e;
                border-radius: 8px;
                padding: 12px 15px;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #00d4aa;
            }
        """)
        input_layout.addWidget(self.url_input)
        
        self.fetch_btn = QPushButton("📥 Fetch")
        self.fetch_btn.setFont(QFont(".AppleSystemUIFont", 13, QFont.Bold))
        self.fetch_btn.setFixedWidth(100)
        self.fetch_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: #1e1e2e;
                border: none;
                border-radius: 8px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #00e6b8;
            }
            QPushButton:pressed {
                background-color: #00c49a;
            }
            QPushButton:disabled {
                background-color: #4a4a6e;
                color: #888;
            }
        """)
        input_layout.addWidget(self.fetch_btn)
        
        layout.addLayout(input_layout)
        
        # Batch download hint
        hint_label = QLabel("💡 Tip: You can paste multiple URLs, one per line for batch download")
        hint_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(hint_label)
        
        return widget
        
    def _create_control_section(self) -> QWidget:
        """Create quality selection and download button section"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #2a2a3e;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # Auto Quality indicator
        self.quality_label = AutoQualityLabel()
        layout.addWidget(self.quality_label)

        # Download options
        options_layout = QHBoxLayout()
        options_layout.setSpacing(15)

        # Output path
        path_label = QLabel("Save to:")
        path_label.setStyleSheet("color: #888;")
        options_layout.addWidget(path_label)

        self.output_path = QLineEdit(FileManager.get_default_download_path())
        self.output_path.setStyleSheet("""
            QLineEdit {
                background-color: #1a1a2e;
                border: 1px solid #3a3a5e;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
            }
        """)
        options_layout.addWidget(self.output_path, 1)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a5e;
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #4a4a6e;
            }
        """)
        options_layout.addWidget(self.browse_btn)
        
        layout.addLayout(options_layout)
        
        # Download button
        self.download_btn = QPushButton("⬇ Download Video")
        self.download_btn.setFont(QFont(".AppleSystemUIFont", 14, QFont.Bold))
        self.download_btn.setFixedHeight(50)
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4aa;
                color: #1e1e2e;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #00e6b8;
            }
            QPushButton:pressed {
                background-color: #00c49a;
            }
            QPushButton:disabled {
                background-color: #4a4a6e;
                color: #888;
            }
        """)
        layout.addWidget(self.download_btn)
        
        return widget
        
    def _create_queue_section(self) -> QWidget:
        """Create download queue section"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #2a2a3e;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        queue_title = QLabel("📋 Download Queue")
        queue_title.setFont(QFont(".AppleSystemUIFont", 14, QFont.Bold))
        queue_title.setStyleSheet("color: #ffffff;")
        header_layout.addWidget(queue_title)
        
        header_layout.addStretch()
        
        self.clear_btn = QPushButton("Clear Completed")
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a5e;
                color: #fff;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #4a4a6e;
            }
        """)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.setStyleSheet("""
            QListWidget {
                background-color: #1a1a2e;
                border: none;
                border-radius: 8px;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #2a2a3e;
            }
            QListWidget::item:selected {
                background-color: #3a3a5e;
            }
        """)
        layout.addWidget(self.queue_list)
        
        return widget
        
    def setup_connections(self):
        """Setup signal/slot connections"""
        self.fetch_btn.clicked.connect(self._on_fetch_clicked)
        self.download_btn.clicked.connect(self._on_download_clicked)
        self.browse_btn.clicked.connect(self._on_browse_clicked)
        self.clear_btn.clicked.connect(self._on_clear_clicked)

        # URL input enter key
        self.url_input.returnPressed.connect(self._on_fetch_clicked)
        
        # Setup clipboard monitor callback
        self.clipboard_monitor.start(self._on_clipboard_video_detected)  # pyre-ignore[16]
        
    def _on_fetch_clicked(self):
        """Handle fetch button click"""
        url = self.url_input.text().strip()
        if not url:
            logger.warning("Fetch clicked with empty URL")
            QMessageBox.warning(self, "Warning", "Please enter a video URL")
            return

        logger.info("Fetching metadata for URL: %s", url[:50] + "..." if len(url) > 50 else url)
        
        # Disable fetch button during fetch
        self.fetch_btn.setEnabled(False)
        self.fetch_btn.setText("Fetching...")

        # Fetch metadata in background thread
        self._metadata_thread = MetadataFetcherThread(url)
        thread = self._metadata_thread
        if thread:
            thread.finished.connect(self._on_metadata_fetched)
            thread.error.connect(self._on_metadata_error)
            thread.start()

    def _on_metadata_fetched(self, metadata: VideoMetadata):
        """Handle metadata fetch completion"""
        logger.info("Metadata fetched: %s by %s (%s)", metadata.title, metadata.uploader, metadata.platform)

        self._current_metadata = metadata
        self.video_info.update_metadata(metadata)
        
        # Update auto quality label with platform info
        self.quality_label.update_platform_quality(metadata.platform)

        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("📥 Fetch")

    def _on_metadata_error(self, error: str):
        """Handle metadata fetch error"""
        logger.error("Failed to fetch metadata: %s", error)
        
        QMessageBox.critical(self, "Error", f"Failed to fetch video info:\n{error}")

        self.fetch_btn.setEnabled(True)
        self.fetch_btn.setText("📥 Fetch")
        
    def _on_clipboard_video_detected(self, url: str):
        """Handle video URL detected from clipboard"""
        # Show notification dialog
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Video Link Detected")
        msg.setText(f"Video link detected from clipboard:\n{url}")
        msg.setInformativeText("Do you want to paste it and fetch video info?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        
        # Set custom styling
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2a2a3e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #00d4aa;
                color: #1e1e2e;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #00e6b8;
            }
        """)
        
        result = msg.exec()
        if result == QMessageBox.Yes:
            self.url_input.setText(url)
            self._on_fetch_clicked()

    def _on_download_clicked(self):
        """Handle download button click"""
        url_text = self.url_input.text().strip()
        if not url_text:
            logger.warning("Download clicked with empty URL")
            QMessageBox.warning(self, "Warning", "Please enter a video URL")
            return

        # Get output path
        output_path = self.output_path.text()
        if not os.path.exists(output_path):
            logger.warning("Output path does not exist: %s", output_path)
            QMessageBox.warning(self, "Warning", "Output directory does not exist")
            return

        # Check if multiple URLs (batch download)
        urls = [u.strip() for u in url_text.split('\n') if u.strip()]
        logger.info("Download clicked - %d URL(s)", len(urls))

        # Always fetch metadata first to avoid issues with playlist/radio URLs
        if len(urls) > 1:
            # Batch download
            logger.info("Starting batch download for %d URLs", len(urls))
            self._start_batch_download(urls)
            QMessageBox.information(
                self, "Batch Download Started",
                f"Added {len(urls)} videos to download queue."
            )
        else:
            # Single URL - always fetch metadata first
            url = urls[0]
            logger.info("Fetching metadata before download: %s", url[:50])
            
            # Check if we already have metadata for this exact URL
            meta = self._current_metadata
            if meta and meta.url == url:
                logger.info("Using cached metadata: %s", meta.title)
                self._start_single_download(url)
            else:
                # Fetch metadata first
                logger.info("Fetching fresh metadata for URL")
                self._on_fetch_clicked()
                # Wait for metadata to be fetched, then user can download
                QMessageBox.information(
                    self, 
                    "Fetching Video Info",
                    "Fetching video information. Please click Download again after the video info is loaded."
                )

        # Reset button state
        self.download_btn.setEnabled(True)
        self.download_btn.setText("⬇ Download Video")
        
    def _on_download_progress(self, progress: DownloadProgress):
        """Handle download progress update"""
        # Update UI with progress - will be handled by queue manager callback
        pass

    def _on_download_finished(self, success: bool):
        """Handle download completion"""
        self.download_btn.setEnabled(True)
        self.download_btn.setText("⬇ Download Video")

        if success:
            QMessageBox.information(
                self, "Success",
                f"Download completed!\nSaved to: {self.output_path.text()}"
            )

    def _on_download_error(self, error: str):
        """Handle download error"""
        self.download_btn.setEnabled(True)
        self.download_btn.setText("⬇ Download Video")

        QMessageBox.critical(self, "Error", f"Download failed:\n{error}")

    def _on_browse_clicked(self):
        """Handle browse button click"""
        current_path = self.output_path.text()
        directory = QFileDialog.getExistingDirectory(
            self, "Select Download Directory", current_path
        )
        if directory:
            self.output_path.setText(directory)

    def _on_clear_clicked(self):
        """Handle clear completed button click"""
        self.queue_manager.clear_completed()
        self._refresh_queue_list()

    def _on_queue_update(self, event: str, item: Optional[QueueItem]):
        """Handle queue manager updates"""
        # Update queue list widget
        if event in ['item_added', 'item_updated', 'item_removed', 'queue_cleared', 'progress_updated']:
            self._refresh_queue_list()

    def _refresh_queue_list(self):
        """Refresh the queue list widget"""
        self.queue_list.clear()
        queue_items = self.queue_manager.get_queue()
        
        for item in queue_items:
            widget = QueueItemWidget(item)
            widget.cancel_clicked.connect(self._on_queue_item_cancel)
            widget.pause_clicked.connect(self._on_queue_item_pause)
            widget.resume_clicked.connect(self._on_queue_item_resume)
            
            list_item = QListWidgetItem(self.queue_list)
            list_item.setSizeHint(widget.sizeHint())
            self.queue_list.addItem(list_item)
            self.queue_list.setItemWidget(list_item, widget)

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
        # Start queue processing to resume download
        self.queue_manager.start_queue()

    def _start_batch_download(self, urls: List[str]):
        """Start batch download for multiple URLs"""
        output_path = self.output_path.text()
        # Use BEST quality - will auto-select based on platform
        quality = VideoQuality.BEST

        logger.info("Starting batch download: %d URLs, quality=AUTO, output=%s",
                   len(urls), output_path)

        # Add all URLs to queue
        added = 0
        for url in urls:
            url = url.strip()
            if not url:
                continue

            # Fetch metadata for each URL (in batch, we fetch synchronously)
            # This might take time but only for batch downloads
            url_preview = url[:50]  # pyre-ignore[6]
            logger.debug("Fetching metadata for batch URL: %s", url_preview)
            try:
                metadata = self.engine.fetch_metadata(url)
            except Exception as e:
                logger.error("Failed to fetch metadata for %s: %s", url_preview, e)
                metadata = None

            self.queue_manager.add_to_queue(
                url=url,
                quality=quality,
                output_path=output_path,
                metadata=metadata,
            )
            added += 1

        logger.info("Added %d items to download queue", added)

        # Start queue processing
        self.queue_manager.start_queue()
        self._refresh_queue_list()

    def _start_single_download(self, url: str):
        """Start download for single URL"""
        if not self._current_metadata:
            logger.warning("Single download called without metadata")
            QMessageBox.warning(self, "Warning", "Please fetch video info first")
            return

        output_path = self.output_path.text()
        if not os.path.exists(output_path):
            logger.warning("Output path does not exist: %s", output_path)
            QMessageBox.warning(self, "Warning", "Output directory does not exist")
            return

        # Use BEST quality - will auto-select based on platform
        quality = VideoQuality.BEST
        meta = self._current_metadata
        if meta:
            logger.info("Adding to queue: %s (quality=AUTO, platform=%s)", 
                       meta.title, meta.platform)
        else:
            logger.info("Adding to queue: %s (quality=AUTO)", url)

        # Add to queue
        self.queue_manager.add_to_queue(
            url=url,
            quality=quality,
            output_path=output_path,
            metadata=self._current_metadata,
        )

        # Start queue processing
        self.queue_manager.start_queue()
        self._refresh_queue_list()

        # Reset button state
        self.download_btn.setEnabled(True)
        self.download_btn.setText("⬇ Download Video")

    def closeEvent(self, event):
        """Handle window close event"""
        # Stop clipboard monitor
        self.clipboard_monitor.stop()
        event.accept()
