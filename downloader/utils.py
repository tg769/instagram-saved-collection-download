"""
Utility functions for the downloader.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Set, List
import logging

logger = logging.getLogger(__name__)


class DownloadTracker:
    """Tracks which posts have been downloaded."""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.tracker_file = data_path / "downloaded.json"
        self.downloaded_pks: Set[str] = set()
        self._load_tracker()
    
    def _load_tracker(self):
        """Load the downloaded PKs from file."""
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.downloaded_pks = set(data.get('downloaded', []))
                logger.info(f"Loaded {len(self.downloaded_pks)} previously downloaded posts.")
            except Exception as e:
                logger.error(f"Error loading tracker file: {str(e)}")
                self.downloaded_pks = set()
        else:
            logger.info("No previous download history found.")
    
    def is_downloaded(self, pk: str) -> bool:
        """Check if a post has been downloaded."""
        return pk in self.downloaded_pks
    
    def mark_downloaded(self, pk: str):
        """Mark a post as downloaded."""
        self.downloaded_pks.add(pk)
    
    def save_tracker(self):
        """Save the tracker to file."""
        try:
            data = {
                'downloaded': list(self.downloaded_pks),
                'last_updated': datetime.now().isoformat()
            }
            with open(self.tracker_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved download tracker with {len(self.downloaded_pks)} posts.")
        except Exception as e:
            logger.error(f"Error saving tracker file: {str(e)}")


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def ensure_directories(base_path: Path) -> dict:
    """
    Create all necessary directories.
    
    Args:
        base_path: Base downloads directory
        
    Returns:
        Dictionary with directory paths
    """
    directories = {
        'base': base_path,
        'photos': base_path / 'photos',
        'videos': base_path / 'videos',
        'albums': base_path / 'albums',
        'metadata': base_path / 'metadata',
    }
    
    for dir_path in directories.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return directories


def format_size(bytes: int) -> str:
    """Format bytes to human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024.0:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024.0
    return f"{bytes:.2f} TB"
