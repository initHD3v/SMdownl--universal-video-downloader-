"""
Clipboard Monitor Service
Detects video links in clipboard
"""

import re
import threading
import time
from typing import Optional, Callable, List

try:
    import AppKit  # macOS specific
    MACOS_AVAILABLE = True
except ImportError:
    MACOS_AVAILABLE = False


class ClipboardMonitor:
    """Monitor clipboard for video URLs"""
    
    # Common video URL patterns
    VIDEO_URL_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?facebook\.com/.+/videos/',
        r'(?:https?://)?fb\.watch/[\w-]+',
        r'(?:https?://)?(?:www\.)?instagram\.com/(?:p|reel|tv)/[\w-]+',
        r'(?:https?://)?(?:www\.)?x\.com/[\w]+/status/[\w]+',
        r'(?:https?://)?(?:www\.)?twitter\.com/[\w]+/status/[\w]+',
        r'(?:https?://)?t\.co/[\w]+',
        r'(?:https?://)?(?:www\.)?tiktok\.com/@[\w]+/video/[\w]+',
    ]
    
    def __init__(self, check_interval: float = 2.0):
        self.check_interval = check_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_content: Optional[str] = None
        self._callback: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()
        
    def _get_clipboard_content(self) -> Optional[str]:
        """Get current clipboard content"""
        if not MACOS_AVAILABLE:
            return None
            
        try:
            pasteboard = AppKit.NSPasteboard.generalPasteboard()
            content = pasteboard.stringForType_(AppKit.NSPasteboardTypeString)
            return content
        except Exception:
            return None
    
    def _is_video_url(self, text: str) -> bool:
        """Check if text contains a video URL"""
        if not text:
            return False
            
        for pattern in self.VIDEO_URL_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _extract_video_url(self, text: str) -> Optional[str]:
        """Extract video URL from text"""
        if not text:
            return None
            
        for pattern in self.VIDEO_URL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                url = match.group(0)
                # Ensure URL has protocol
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                return url
        return None
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self._running:
            try:
                content = self._get_clipboard_content()
                
                if content and content != self._last_content:
                    with self._lock:
                        self._last_content = content
                    
                    if self._is_video_url(content):
                        video_url = self._extract_video_url(content)
                        if video_url and self._callback:
                            self._callback(video_url)
                            
            except Exception as e:
                print(f"Clipboard monitor error: {e}")
            
            time.sleep(self.check_interval)
    
    def start(self, callback: Callable[[str], None]):
        """
        Start monitoring clipboard
        
        Args:
            callback: Function to call when video URL detected
        """
        if self._running:
            return
            
        self._callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
    
    def stop(self):
        """Stop monitoring clipboard"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=3.0)
            self._thread = None
    
    def check_now(self) -> Optional[str]:
        """
        Immediately check clipboard for video URL
        
        Returns:
            Video URL if detected, None otherwise
        """
        content = self._get_clipboard_content()
        if content and self._is_video_url(content):
            return self._extract_video_url(content)
        return None
    
    def get_last_content(self) -> Optional[str]:
        """Get last detected clipboard content"""
        with self._lock:
            return self._last_content
