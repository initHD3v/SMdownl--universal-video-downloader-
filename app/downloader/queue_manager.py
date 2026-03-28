"""
Download Queue Manager
Manages download queue with pause, resume, cancel, and reorder functionality
"""

import os
import threading
import logging
from typing import Optional, List, Callable, Dict
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from PySide6.QtCore import QObject, Signal  # pyre-ignore[21]

from app.downloader.yt_dlp_engine import YtDlpEngine, VideoQuality, DownloadProgress, VideoMetadata  # pyre-ignore[21]

logger = logging.getLogger(__name__)


class QueueItemStatus(Enum):
    """Status of a queue item"""
    WAITING = "waiting"
    DOWNLOADING = "downloading"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class QueueItem:
    """Represents a single item in the download queue"""
    id: int
    url: str
    metadata: Optional[VideoMetadata]
    quality: VideoQuality
    output_path: str
    status: QueueItemStatus = QueueItemStatus.WAITING
    progress: float = 0.0
    speed: str = ""
    eta: str = ""
    error: Optional[str] = None
    added_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    filename: Optional[str] = None
    downloaded_bytes: int = 0
    total_bytes: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for UI display"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.metadata.title if self.metadata else 'Fetching...',  # pyre-ignore[16]
            'platform': self.metadata.platform if self.metadata else 'Unknown',  # pyre-ignore[16]
            'quality': self.quality.value,
            'status': self.status.value,
            'progress': self.progress,
            'speed': self.speed,
            'eta': self.eta,
            'error': self.error,
            'downloaded_bytes': self.downloaded_bytes,
            'total_bytes': self.total_bytes,
        }


class QueueManager(QObject):
    """Manages the download queue"""
    
    # Define signals for thread-safe UI updates
    queue_updated = Signal(str, object)
    
    def __init__(self, max_concurrent: int = 1):
        super().__init__()
        self.max_concurrent = max_concurrent
        self._queue: List[QueueItem] = []
        self._active_downloads: Dict[int, threading.Thread] = {}
        self._engine = YtDlpEngine()
        self._lock = threading.Lock()
        self._current_id = 0
        self._stop_event = threading.Event()
        
    def _emit_update(self, event: str, item: QueueItem):
        """Safely emit update signal"""
        self.queue_updated.emit(event, item)
        
    def _get_next_id(self) -> int:
        """Generate next unique ID"""
        with self._lock:
            self._current_id += 1
            return self._current_id
    
    def add_to_queue(
        self,
        url: str,
        quality: VideoQuality = VideoQuality.Q1080,
        output_path: Optional[str] = None,
        metadata: Optional[VideoMetadata] = None,
    ) -> QueueItem:
        """Add a new item to the download queue"""
        if output_path is None:
            output_path = os.path.expanduser("~/Downloads")
            
        item = QueueItem(
            id=self._get_next_id(),
            url=url,
            metadata=metadata,
            quality=quality,
            output_path=output_path,
        )
        
        with self._lock:
            self._queue.append(item)
            
        self._emit_update('item_added', item)
            
        return item
    
    def remove_from_queue(self, item_id: int) -> bool:
        """Remove an item from the queue"""
        with self._lock:
            for i, item in enumerate(self._queue):
                if item.id == item_id:
                    if item.status == QueueItemStatus.DOWNLOADING:
                        # Can't remove actively downloading items
                        return False
                    self._queue.pop(i)
                    self._emit_update('item_removed', item)
                    return True
        return False
    
    def reorder_queue(self, item_id: int, new_position: int) -> bool:
        """Reorder an item in the queue"""
        with self._lock:
            # Find the item
            item_index: int = -1
            for i, item in enumerate(self._queue):
                if item.id == item_id:
                    item_index = i
                    break
                    
            if item_index == -1:
                return False
            if self._queue[item_index].status == QueueItemStatus.DOWNLOADING:
                return False
                
            # Remove and reinsert at new position
            item = self._queue.pop(item_index)
            new_position = max(0, min(new_position, len(self._queue)))
            self._queue.insert(new_position, item)
            
        self._emit_update('queue_reordered', item)
            
        return True
    
    def pause_item(self, item_id: int) -> bool:
        """Pause a waiting or downloading item"""
        with self._lock:
            for item in self._queue:
                if item.id == item_id:
                    if item.status == QueueItemStatus.WAITING:
                        item.status = QueueItemStatus.PAUSED
                        self._emit_update('item_updated', item)
                        return True
                    elif item.status == QueueItemStatus.DOWNLOADING:
                        # Mark for cancellation (handled in download thread)
                        item.status = QueueItemStatus.PAUSED
                        self._emit_update('item_updated', item)
                        return True
        return False
    
    def resume_item(self, item_id: int) -> bool:
        """Resume a paused item"""
        with self._lock:
            for item in self._queue:
                if item.id == item_id:
                    if item.status == QueueItemStatus.PAUSED:
                        item.status = QueueItemStatus.WAITING
                        self._emit_update('item_updated', item)
                        return True
        return False
    
    def cancel_item(self, item_id: int) -> bool:
        """Cancel a queue item"""
        with self._lock:
            for item in self._queue:
                if item.id == item_id:
                    if item.status in [QueueItemStatus.WAITING, QueueItemStatus.PAUSED]:
                        item.status = QueueItemStatus.CANCELLED
                        self._emit_update('item_updated', item)
                        return True
                    elif item.status == QueueItemStatus.DOWNLOADING:
                        item.status = QueueItemStatus.CANCELLED
                        self._emit_update('item_updated', item)
                        return True
        return False
    
    def retry_item(self, item_id: int) -> bool:
        """Retry a failed or cancelled item"""
        with self._lock:
            for item in self._queue:
                if item.id == item_id:
                    if item.status in [QueueItemStatus.ERROR, QueueItemStatus.CANCELLED]:
                        item.status = QueueItemStatus.WAITING
                        item.progress = 0
                        item.error = None
                        self._emit_update('item_updated', item)
                        return True
        return False
    
    def get_queue(self) -> List[QueueItem]:
        """Get current queue items"""
        with self._lock:
            return list(self._queue)
    
    def get_active_count(self) -> int:
        """Get count of actively downloading items"""
        with self._lock:
            return sum(1 for item in self._queue if item.status == QueueItemStatus.DOWNLOADING)
    
    def get_waiting_count(self) -> int:
        """Get count of waiting items"""
        with self._lock:
            return sum(1 for item in self._queue if item.status == QueueItemStatus.WAITING)
    
    def _download_worker(self, item: QueueItem):
        """Worker thread for downloading items"""
        logger.info("=" * 60)
        logger.info("Download worker STARTED for item %d", item.id)
        logger.info("  URL: %s", item.url)
        logger.info("  Title: %s", item.metadata.title if item.metadata else "N/A")  # pyre-ignore[16]
        logger.info("  Output path: %s", item.output_path)
        logger.info("  Quality: %s", item.quality)
        logger.info("  Path exists: %s", os.path.exists(item.output_path) if item.output_path else "N/A")
        logger.info("=" * 60)

        # Create progress callback that properly updates item
        def progress_callback(progress: DownloadProgress):
            """Handle progress updates"""
            try:
                # Update item attributes directly
                with self._lock:
                    # Skip if cancelled
                    if item.status == QueueItemStatus.CANCELLED:
                        return

                    item.progress = progress.progress
                    item.speed = progress.speed
                    item.eta = progress.eta
                    item.filename = progress.filename
                    item.downloaded_bytes = progress.downloaded_bytes
                    item.total_bytes = progress.total_bytes

                    if progress.status == 'error':
                        item.status = QueueItemStatus.ERROR
                        item.error = progress.error
                        logger.error("Download error for item %d: %s", item.id, progress.error)
                    elif progress.status == 'completed':
                        item.status = QueueItemStatus.COMPLETED
                        item.completed_at = datetime.now()
                        logger.info("Download COMPLETED for item %d: %s", item.id, progress.filename)

                # Notify UI (Signal is cross-thread safe inherently)
                self._emit_update('progress_updated', item)

            except Exception as e:
                logger.error("Error in progress callback for item %d: %s", item.id, e, exc_info=True)

        try:
            # Get platform from metadata for auto quality selection
            platform = item.metadata.platform if item.metadata else None  # pyre-ignore[16]

            logger.info("Calling engine.download() for item %d: %s", item.id, item.metadata.title if item.metadata else item.url)  # pyre-ignore[16]
            logger.info("  Platform: %s", platform)
            logger.info("  Output path writable: %s", os.access(item.output_path, os.W_OK) if item.output_path else "N/A")

            success = self._engine.download(
                url=item.url,
                output_path=item.output_path,
                quality=item.quality,
                progress_callback=progress_callback,
                platform=platform,
            )

            logger.info("Download completed for item %d: success=%s, filename=%s", item.id, success, item.filename)
            logger.info("  Final status: %s", item.status.value)
            logger.info("  Final error: %s", item.error if item.error else "None")

            if not success:
                with self._lock:
                    # Don't overwrite error status from progress callback
                    if item.status != QueueItemStatus.ERROR:
                        item.status = QueueItemStatus.ERROR
                    if not item.error:
                        item.error = "Download failed"
                logger.error("Download marked as failed for item %d", item.id)

        except Exception as e:
            logger.error("Download worker error for item %d: %s", item.id, e, exc_info=True)
            with self._lock:
                item.status = QueueItemStatus.ERROR
                item.error = str(e)

        finally:
            # Remove from active downloads
            with self._lock:
                if item.id in self._active_downloads:
                    self._active_downloads.pop(item.id)

            # Notify UI
            self._emit_update('item_updated', item)

            logger.info("Download worker FINISHED for item %d", item.id)
            logger.info("=" * 60)

    def start_queue(self):
        """Start processing the download queue"""
        logger.info("Starting queue processing")
        
        # Get waiting items (copy to avoid lock issues)
        with self._lock:
            waiting_items = [
                item for item in self._queue 
                if item.status == QueueItemStatus.WAITING
            ]
        
        logger.info("Found %d waiting items", len(waiting_items))
        
        for item in waiting_items:
            try:
                active_count = self.get_active_count()
                logger.info("Checking item %d: status=%s, active=%d", item.id, item.status.value, active_count)
                
                if active_count < self.max_concurrent:
                    logger.info("Starting download thread for item %d: %s", item.id, item.metadata.title if item.metadata else "Unknown")  # pyre-ignore[16]

                    # Set status to DOWNLOADING before starting thread
                    with self._lock:
                        item.status = QueueItemStatus.DOWNLOADING

                    # Use daemon=False to ensure download completes even if app closes
                    thread = threading.Thread(target=self._download_worker, args=(item,), daemon=False, name=f"Download-{item.id}")

                    with self._lock:
                        self._active_downloads[item.id] = thread

                    thread.start()
                    logger.info("Thread started for item %d (daemon=%s)", item.id, thread.daemon)
                else:
                    logger.info("Max concurrent downloads reached (%d)", self.max_concurrent)
                    
            except Exception as e:
                logger.error("Error starting download for item %d: %s", item.id, e, exc_info=True)
                # Mark as error
                item.status = QueueItemStatus.ERROR
                item.error = str(e)
        
        logger.info("Queue processing completed")

    def clear_completed(self):
        """Remove completed and cancelled items from queue"""
        with self._lock:
            self._queue = [
                item for item in self._queue
                if item.status not in [QueueItemStatus.COMPLETED, QueueItemStatus.CANCELLED]
            ]
