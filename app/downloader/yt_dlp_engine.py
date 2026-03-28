"""
yt-dlp Engine Wrapper
Handles video downloading using yt-dlp library
"""

import os
import re
import logging
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

import yt_dlp  # pyre-ignore[21]

logger = logging.getLogger(__name__)


class VideoQuality(Enum):
    """Available video quality options"""
    BEST = "best"  # Auto-select best quality based on platform
    Q4K = "2160p"
    Q1080 = "1080p"
    Q720 = "720p"
    Q480 = "480p"
    AUDIO_BEST = "best_audio"
    AUDIO_MP3 = "mp3"
    AUDIO_M4A = "m4a"


# Platform-specific default quality settings
PLATFORM_QUALITY = {
    'YouTube': VideoQuality.Q1080,      # YouTube: 1080p default
    'Facebook': VideoQuality.BEST,       # Facebook: best available
    'Instagram': VideoQuality.BEST,      # Instagram: best available
    'X': VideoQuality.BEST,              # X (Twitter): best available
    'TikTok': VideoQuality.BEST,         # TikTok: best available
    'Unknown': VideoQuality.BEST,        # Fallback to best
}


@dataclass
class VideoMetadata:
    """Video metadata container"""
    url: str
    title: str
    duration: int  # in seconds
    uploader: str
    thumbnail: str
    platform: str
    available_formats: List[Dict[str, Any]]
    description: str = ""


@dataclass
class DownloadProgress:
    """Download progress information"""
    status: str  # 'downloading', 'completed', 'error', 'paused'
    progress: float  # 0-100
    speed: str  # e.g., "4.2 MB/s"
    eta: str  # e.g., "00:21"
    downloaded_bytes: int
    total_bytes: int
    filename: str
    error: Optional[str] = None


class YtDlpEngine:
    """Engine wrapper for yt-dlp downloader"""

    # Supported platforms
    SUPPORTED_PLATFORMS = ['YouTube', 'Facebook', 'Instagram', 'X', 'TikTok']

    def __init__(self, output_template: str = "%(title)s_%(height)sp.%(ext)s"):
        self.output_template = output_template
        self._current_download = None
        self._progress_hook: Optional[Callable[[DownloadProgress], None]] = None

    def is_supported_url(self, url: str) -> bool:
        """Check if URL is from supported platform"""
        platform = self.detect_platform(url)
        return platform in self.SUPPORTED_PLATFORMS

    def get_supported_platforms_info(self) -> str:
        """Get info about supported platforms"""
        return "Supported: YouTube, Facebook, Instagram, X (Twitter), TikTok"
        
    def detect_platform(self, url: str) -> str:
        """Detect video platform from URL"""
        url_lower = url.lower()

        if any(domain in url_lower for domain in ['youtube.com', 'youtu.be']):
            return 'YouTube'
        elif 'facebook.com' in url_lower or 'fb.watch' in url_lower:
            return 'Facebook'
        elif 'instagram.com' in url_lower:
            return 'Instagram'
        elif any(domain in url_lower for domain in ['x.com', 'twitter.com', 't.co']):
            return 'X'
        elif 'tiktok.com' in url_lower:
            return 'TikTok'
        else:
            return 'Unknown'

    def get_auto_quality(self, platform: str) -> VideoQuality:
        """
        Get automatic quality based on platform
        
        Args:
            platform: Platform name (YouTube, Facebook, Instagram, X, TikTok)
            
        Returns:
            VideoQuality for the platform
        """
        return PLATFORM_QUALITY.get(platform, VideoQuality.BEST)

    def _clean_youtube_url(self, url: str) -> str:
        """
        Clean YouTube URL by removing problematic parameters
        that can cause issues with metadata fetching
        
        Specifically handles:
        - Radio playlists (start_radio=1, list=RD...)
        - Autoplay lists
        - Unnecessary tracking parameters
        """
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        if 'youtube.com' not in url and 'youtu.be' not in url:
            return url

        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # Remove parameters that can cause issues
            # Keep only 'v' (video id)
            clean_params = {}

            if 'v' in params:
                clean_params['v'] = params['v']

            # Check for radio/autoplay indicators
            is_radio = False
            
            # Check start_radio parameter
            if params.get('start_radio', ['0'])[0] == '1':
                is_radio = True
                logger.debug("Radio URL detected (start_radio=1)")
            
            # Check if list parameter is a radio playlist (starts with RD)
            if 'list' in params:
                playlist_id = params['list'][0]
                if playlist_id.startswith('RD'):
                    is_radio = True
                    logger.debug("Radio playlist detected (RD prefix): %s", playlist_id)
                elif is_radio:
                    # Already detected as radio, don't include list
                    pass
                else:
                    # Regular playlist, keep it
                    clean_params['list'] = params['list']

            if is_radio:
                logger.info("Cleaning radio URL - removing playlist parameters")

            # Reconstruct URL with only necessary parameters
            new_parsed = parsed._replace(query=urlencode(clean_params, doseq=True))
            clean_url = str(urlunparse(new_parsed))
            
            logger.debug("Cleaned YouTube URL: %s -> %s", url, clean_url)
            return clean_url

        except Exception as e:
            logger.warning("Failed to clean YouTube URL %s: %s", url, e)
            # If parsing fails, return original URL
            return url

    def fetch_metadata(self, url: str) -> Optional[VideoMetadata]:
        """Fetch video metadata from URL"""
        import socket
        
        # Clean URL to remove problematic parameters
        clean_url = self._clean_youtube_url(url)
        
        logger.info("Fetching metadata for: %s", clean_url)

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            # Ignore playlist if it's a radio/autoplay list
            'noplaylist': True,
            # Extract only the single video
            'extract_flat': 'in_playlist',
            # Add socket timeout to prevent hanging
            'socket_timeout': 30,
            # Skip download for metadata
            'skip_download': True,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.debug("Extracting info from yt-dlp...")
                info = ydl.extract_info(clean_url, download=False)

                if not info:
                    logger.warning("No info returned from yt-dlp")
                    return None

                logger.debug("Metadata extracted: %s", info.get('title', 'Unknown'))

                # Extract available formats
                formats = []
                for fmt in info.get('formats', []):
                    if fmt.get('vcodec') != 'none':
                        formats.append({
                            'format_id': fmt.get('format_id', ''),
                            'resolution': fmt.get('resolution', fmt.get('height', 'unknown')),
                            'height': fmt.get('height', 0),
                            'fps': fmt.get('fps', 0),
                            'filesize': fmt.get('filesize', 0),
                        })

                # Remove duplicates and sort by quality
                seen = set()
                unique_formats = []
                for f in formats:
                    key = f['resolution']
                    if key not in seen:
                        seen.add(key)
                        unique_formats.append(f)

                unique_formats.sort(key=lambda x: x['height'], reverse=True)
                
                title = info.get('title', 'Unknown')
                logger.info("Metadata fetched successfully: %s", title)

                return VideoMetadata(
                    url=url,
                    title=title,
                    duration=info.get('duration', 0) or 0,
                    uploader=info.get('uploader', 'Unknown'),
                    thumbnail=info.get('thumbnail', ''),
                    platform=self.detect_platform(url),
                    available_formats=unique_formats,
                    description=info.get('description', '')
                )
        except socket.timeout:
            logger.error("Timeout fetching metadata for %s", clean_url)
            return None
        except Exception as e:
            logger.error("Error fetching metadata for %s: %s", clean_url, e, exc_info=True)
            return None
    
    def _progress_callback(self, d: Dict[str, Any]):
        """Internal progress hook for yt-dlp"""
        hook = self._progress_hook
        if hook:
            status = d.get('status', '')
            
            if status == 'downloading':
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes', 0) or d.get('total_bytes_estimate', 0)
                speed = d.get('speed', 0)
                eta = d.get('eta', 0)
                
                progress = 0
                if total > 0:
                    progress = (downloaded / total) * 100
                
                speed_str = self._format_speed(speed) if speed else "N/A"
                eta_str = self._format_eta(eta) if eta else "N/A"
                
                hook(DownloadProgress(
                    status='downloading',
                    progress=progress,
                    speed=speed_str,
                    eta=eta_str,
                    downloaded_bytes=downloaded,
                    total_bytes=total,
                    filename=d.get('filename', ''),
                ))
                
            elif status == 'finished':
                hook(DownloadProgress(
                    status='completed',
                    progress=100,
                    speed='',
                    eta='',
                    downloaded_bytes=0,
                    total_bytes=0,
                    filename=d.get('filename', ''),
                ))
    
    def _format_speed(self, speed: float) -> str:
        """Format download speed to human readable string"""
        if speed >= 1024 * 1024:
            return f"{speed / (1024 * 1024):.1f} MB/s"
        elif speed >= 1024:
            return f"{speed / 1024:.1f} KB/s"
        else:
            return f"{speed:.0f} B/s"
    
    def _format_eta(self, eta: Any) -> str:
        """Format ETA to MM:SS format"""
        # Safety cast to int for formatting
        eta_val = int(eta or 0)
        minutes = eta_val // 60
        seconds = eta_val % 60
        return f"{minutes:02d}:{seconds:02d}"

    def _predict_output_filename(self, outtmpl: str, url: str) -> Optional[str]:
        """
        Check if a file with similar name already exists
        
        Args:
            outtmpl: Output template (e.g., '/path/%(title)s_%(height)sp.%(ext)s')
            url: Video URL
            
        Returns:
            Existing filename if found, None otherwise
        """
        try:
            # Fetch metadata to get title
            metadata = self.fetch_metadata(url)
            if not metadata:
                return None
            
            # Get base title
            title = metadata.title
            
            # Check directory for similar files
            output_dir = os.path.dirname(outtmpl)
            if not os.path.isdir(output_dir):
                return None
            
            # Look for files with same base title (case-insensitive, normalize special chars)
            def normalize(s):
                # Replace various pipe/special chars with regular versions
                s = s.replace('｜', '|').replace('@', '').strip()
                return "".join(c for c in s.lower() if c.isalnum() or c in ' -_').strip()
            
            safe_title = normalize(title)
            logger.info("Looking for files matching: '%s' in %s", safe_title, output_dir)
            
            for filename in os.listdir(output_dir):
                if filename.lower().endswith('.mp4'):
                    safe_filename = normalize(filename)
                    if safe_filename.startswith(safe_title):
                        logger.info("Found existing file: %s", filename)
                        return os.path.join(output_dir, filename)
            
            logger.info("No matching files found")
            return None
        except Exception as e:
            logger.debug("Cannot check for existing files: %s", e, exc_info=True)
            return None
    
    def download(
        self,
        url: str,
        output_path: str,
        quality: VideoQuality,
        progress_callback: Callable[[DownloadProgress], None],
        filename_template: Optional[str] = None,
        platform: Optional[str] = None,
    ) -> bool:
        """
        Download video with specified quality
        
        Returns:
            bool: True if download succeeded, False if skipped/failed
        """
        import socket

        self._progress_hook = progress_callback

        # Clean URL for download
        clean_url = self._clean_youtube_url(url)

        # Auto-select quality based on platform if BEST is specified
        if quality == VideoQuality.BEST and platform:
            quality = self.get_auto_quality(platform)
            logger.info("Auto-selected quality for %s: %s", platform, quality.name)

        # Build output template
        if filename_template:
            outtmpl = os.path.join(output_path, filename_template)
        else:
            outtmpl = os.path.join(output_path, self.output_template)

        # Check for duplicate file BEFORE download
        logger.info("Checking for duplicate files...")
        expected_filename = self._predict_output_filename(outtmpl, clean_url)
        if expected_filename:
            logger.info("Predicted filename: %s", expected_filename)
        if expected_filename and os.path.exists(expected_filename):
            logger.warning("File already exists: %s", expected_filename)
            # Notify callback about skip
            progress_callback(DownloadProgress(
                status='error',
                progress=0,
                speed='',
                eta='',
                downloaded_bytes=0,
                total_bytes=0,
                filename=expected_filename,
                error=f"File already exists: {os.path.basename(expected_filename)}",
            ))
            return False
        else:
            logger.info("No duplicate found, proceeding with download")

        # Configure yt-dlp options based on quality
        ydl_opts: Dict[str, Any] = {
            'outtmpl': outtmpl,
            'progress_hooks': [self._progress_callback],
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            # Socket timeout to prevent hanging
            'socket_timeout': 30,
            # Extractor timeout
            'extractor_retries': 2,
            # Skip download if file exists
            'skip_download': False,
            # Don't overwrite existing files
            'nooverwrites': True,
        }

        if quality in [VideoQuality.AUDIO_BEST, VideoQuality.AUDIO_MP3, VideoQuality.AUDIO_M4A]:
            # Audio-only download
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3' if quality == VideoQuality.AUDIO_MP3 else 'm4a' if quality == VideoQuality.AUDIO_M4A else 'best',
                }],
            })
        elif quality == VideoQuality.BEST:
            # Best available quality (video + audio)
            ydl_opts.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            })
        else:
            # Video download with specific quality
            height = str(quality.value).replace('p', '')
            ydl_opts.update({
                'format': f'bestvideo[height<={height}]+bestaudio/best[height<={height}]/best',
                'merge_output_format': 'mp4',
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([clean_url])
            return True
            
        except socket.timeout:
            logger.error("Socket timeout during download")
            hook = self._progress_hook
            if hook:
                hook(DownloadProgress(
                    status='error',
                    progress=0,
                    speed='',
                    eta='',
                    downloaded_bytes=0,
                    total_bytes=0,
                    filename='',
                    error="Connection timeout",
                ))
            return False
            
        except Exception as e:
            logger.error("Download error: %s", e, exc_info=True)
            hook = self._progress_hook
            if hook:
                hook(DownloadProgress(
                    status='error',
                    progress=0,
                    speed='',
                    eta='',
                    downloaded_bytes=0,
                    total_bytes=0,
                    filename='',
                    error=str(e),
                ))
            return False

    def cancel_download(self):
        """Cancel current download (not fully supported by yt-dlp)"""
        pass
