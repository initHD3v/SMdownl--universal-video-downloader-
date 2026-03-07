"""
Download History Manager
Stores and manages download history
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class HistoryItem:
    """Represents a download history item"""
    id: int
    url: str
    title: str
    platform: str
    quality: str
    file_path: str
    file_size: int  # in bytes
    downloaded_at: str  # ISO format datetime
    thumbnail: str = ""
    duration: int = 0  # in seconds
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HistoryItem':
        """Create from dictionary"""
        return cls(**data)


class HistoryManager:
    """Manage download history"""
    
    def __init__(self, history_file: Optional[str] = None):
        if history_file is None:
            # Store in user's application support directory
            app_dir = Path.home() / 'Library' / 'Application Support' / 'SMdown'
            app_dir.mkdir(parents=True, exist_ok=True)
            history_file = str(app_dir / 'history.json')
        
        self.history_file = history_file
        self._history: List[HistoryItem] = []
        self._next_id = 1
        self._load_history()
    
    def _load_history(self):
        """Load history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [HistoryItem.from_dict(item) for item in data.get('items', [])]
                    self._next_id = data.get('next_id', 1)
                logger.info("Loaded %d history items", len(self._history))
            else:
                self._history = []
                self._next_id = 1
        except Exception as e:
            logger.error("Failed to load history: %s", e)
            self._history = []
            self._next_id = 1
    
    def _save_history(self):
        """Save history to file"""
        try:
            data = {
                'version': 1,
                'next_id': self._next_id,
                'items': [item.to_dict() for item in self._history]
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("Saved %d history items", len(self._history))
        except Exception as e:
            logger.error("Failed to save history: %s", e)
    
    def add_item(
        self,
        url: str,
        title: str,
        platform: str,
        quality: str,
        file_path: str,
        file_size: int = 0,
        thumbnail: str = "",
        duration: int = 0,
    ) -> HistoryItem:
        """Add a download to history"""
        item = HistoryItem(
            id=self._next_id,
            url=url,
            title=title,
            platform=platform,
            quality=quality,
            file_path=file_path,
            file_size=file_size,
            downloaded_at=datetime.now().isoformat(),
            thumbnail=thumbnail,
            duration=duration,
        )
        self._next_id += 1
        self._history.insert(0, item)  # Add to beginning (newest first)
        self._save_history()
        
        logger.info("Added to history: %s", title)
        return item
    
    def get_all(self, limit: int = 100) -> List[HistoryItem]:
        """Get all history items (newest first)"""
        return self._history[:limit]
    
    def get_by_platform(self, platform: str, limit: int = 50) -> List[HistoryItem]:
        """Get history items filtered by platform"""
        items = [item for item in self._history if item.platform == platform]
        return items[:limit]
    
    def search(self, query: str, limit: int = 50) -> List[HistoryItem]:
        """Search history by title or URL"""
        query_lower = query.lower()
        items = [
            item for item in self._history
            if query_lower in item.title.lower() or query_lower in item.url.lower()
        ]
        return items[:limit]
    
    def delete_item(self, item_id: int) -> bool:
        """Delete a history item"""
        for i, item in enumerate(self._history):
            if item.id == item_id:
                self._history.pop(i)
                self._save_history()
                logger.info("Deleted history item: %d", item_id)
                return True
        return False
    
    def clear_all(self):
        """Clear all history"""
        self._history = []
        self._save_history()
        logger.info("Cleared all history")
    
    def get_recent(self, days: int = 7, limit: int = 20) -> List[HistoryItem]:
        """Get recent downloads within specified days"""
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        items = []
        for item in self._history:
            try:
                downloaded = datetime.fromisoformat(item.downloaded_at).timestamp()
                if downloaded >= cutoff:
                    items.append(item)
                    if len(items) >= limit:
                        break
            except:
                continue
        return items
    
    def get_statistics(self) -> Dict:
        """Get history statistics"""
        platform_count = {}
        total_size = 0
        
        for item in self._history:
            platform_count[item.platform] = platform_count.get(item.platform, 0) + 1
            total_size += item.file_size
        
        return {
            'total_downloads': len(self._history),
            'platforms': platform_count,
            'total_size_bytes': total_size,
        }
