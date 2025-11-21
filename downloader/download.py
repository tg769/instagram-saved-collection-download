"""
Download media files from Instagram.
"""

from instagrapi import Client
from instagrapi.types import Media
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MediaDownloader:
    """Handles downloading different types of Instagram media."""
    
    def __init__(self, client: Client, base_path: Path):
        self.client = client
        self.base_path = base_path
        
        # Create subdirectories
        self.photos_dir = base_path / "photos"
        self.videos_dir = base_path / "videos"
        self.albums_dir = base_path / "albums"
        
        self.photos_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        self.albums_dir.mkdir(parents=True, exist_ok=True)
    
    def download_media(self, media: Media) -> Optional[Path]:
        """
        Download media based on its type.
        
        Args:
            media: Media object from instagrapi
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            media_type = media.media_type
            pk = str(media.pk)
            
            # Media type 1 = Photo
            if media_type == 1:
                return self._download_photo(media, pk)
            
            # Media type 2 = Video/Reel
            elif media_type == 2:
                return self._download_video(media, pk)
            
            # Media type 8 = Album/Carousel
            elif media_type == 8:
                return self._download_album(media, pk)
            
            else:
                logger.warning(f"Unknown media type {media_type} for pk {pk}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading media {media.pk}: {str(e)}")
            return None
    
    def _download_photo(self, media: Media, pk: str) -> Optional[Path]:
        """Download a photo."""
        try:
            logger.debug(f"Downloading photo {pk}...")
            filepath = self.client.photo_download(media.pk, folder=self.photos_dir)
            return Path(filepath)
        except Exception as e:
            logger.error(f"Failed to download photo {pk}: {str(e)}")
            return None
    
    def _download_video(self, media: Media, pk: str) -> Optional[Path]:
        """Download a video or reel."""
        try:
            logger.debug(f"Downloading video/reel {pk}...")
            filepath = self.client.video_download(media.pk, folder=self.videos_dir)
            return Path(filepath)
        except Exception as e:
            logger.error(f"Failed to download video {pk}: {str(e)}")
            return None
    
    def _download_album(self, media: Media, pk: str) -> Optional[Path]:
        """Download an album/carousel."""
        try:
            logger.debug(f"Downloading album {pk}...")
            
            # Create subfolder for this album
            album_folder = self.albums_dir / pk
            album_folder.mkdir(exist_ok=True)
            
            filepath = self.client.album_download(media.pk, folder=album_folder)
            return Path(filepath)
        except Exception as e:
            logger.error(f"Failed to download album {pk}: {str(e)}")
            return None
    
    def get_media_type_name(self, media_type: int) -> str:
        """Get human-readable media type name."""
        type_map = {
            1: "Photo",
            2: "Video",
            8: "Album"
        }
        return type_map.get(media_type, "Unknown")
