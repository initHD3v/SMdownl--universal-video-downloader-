"""
File Management Utilities
Handles file operations, path management, and filename formatting
"""

import os
import re
from datetime import datetime
from typing import Optional


class FileManager:
    """Utility class for file operations"""
    
    # Default filename template
    DEFAULT_TEMPLATE = "%(title)s_%(height)sp.%(ext)s"
    
    # Invalid characters for filenames (Windows/macOS compatible)
    INVALID_CHARS = r'[<>:"/\\|？*]'
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Remove invalid characters from filename
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for all platforms
        """
        # Replace invalid characters
        sanitized = re.sub(cls.INVALID_CHARS, '_', filename)
        
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(' .')
        
        # Limit length (max 255 bytes for most filesystems)
        # Reserve space for extension
        max_length = 200
        if len(sanitized.encode('utf-8')) > max_length:
            # Truncate by bytes, not characters
            encoded = sanitized.encode('utf-8')
            truncated = encoded[:max_length]  # pyre-ignore[16]
            # Try to decode, ignoring incomplete characters
            sanitized = truncated.decode('utf-8', errors='ignore')
        
        return sanitized or 'untitled'
    
    @classmethod
    def format_filename(
        cls,
        title: str,
        resolution: str = "",
        template: Optional[str] = None,
        extension: str = "mp4",
    ) -> str:
        """
        Format filename using template
        
        Args:
            title: Video title
            resolution: Video resolution (e.g., "1080p")
            template: Filename template with placeholders
            extension: File extension
            
        Returns:
            Formatted filename with extension
        """
        if template is None:
            template = cls.DEFAULT_TEMPLATE
            
        # Sanitize title
        safe_title = cls.sanitize_filename(title)
        
        # Replace placeholders
        filename = template.replace("{title}", safe_title)
        filename = filename.replace("{resolution}", resolution)
        filename = filename.replace("{date}", datetime.now().strftime("%Y%m%d"))
        filename = filename.replace("{datetime}", datetime.now().strftime("%Y%m%d_%H%M%S"))
        
        # Ensure extension is present
        if not filename.endswith(f".{extension}"):
            # Remove any existing extension
            base = os.path.splitext(filename)[0]
            filename = f"{base}.{extension}"
        
        return filename
    
    @classmethod
    def ensure_directory(cls, path: str) -> bool:
        """
        Ensure directory exists, create if necessary
        
        Args:
            path: Directory path
            
        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError:
            return False
    
    @classmethod
    def get_unique_filename(cls, directory: str, filename: str) -> str:
        """
        Generate unique filename if file already exists
        
        Args:
            directory: Target directory
            filename: Original filename
            
        Returns:
            Unique filename that doesn't conflict with existing files
        """
        base, ext = os.path.splitext(filename)
        filepath = os.path.join(directory, filename)
        
        if not os.path.exists(filepath):
            return filename
        
        # File exists, generate unique name
        counter = 1
        while True:
            new_filename = f"{base}_{counter}{ext}"
            new_filepath = os.path.join(directory, new_filename)
            if not os.path.exists(new_filepath):
                return new_filename
            counter += 1
            
        return filename
    
    @classmethod
    def get_file_size(cls, filepath: str) -> int:
        """Get file size in bytes"""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0
    
    @classmethod
    def format_file_size(cls, size_bytes: int) -> str:
        """
        Format file size to human readable string
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        if size_bytes < 0:
            return "Unknown"
            
        size_float = float(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_float < 1024.0:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024.0
        
        return f"{size_float:.1f} PB"
    
    @classmethod
    def get_default_download_path(cls) -> str:
        """Get default download directory"""
        default = os.path.expanduser("~/Downloads")
        cls.ensure_directory(default)
        return default
    
    @classmethod
    def is_valid_path(cls, path: str) -> bool:
        """Check if path is valid and writable"""
        try:
            # Check if path exists and is writable
            if os.path.exists(path):
                return os.path.isdir(path) and os.access(path, os.W_OK)
            
            # Try to create parent directory
            parent = os.path.dirname(path)
            if parent and not os.path.exists(parent):
                return False
                
            return True
        except (OSError, ValueError):
            return False
