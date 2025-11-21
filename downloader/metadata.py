"""
Extract and save metadata for downloaded media.
"""

from typing import TYPE_CHECKING, List, Optional
from pathlib import Path
import json
import re
import logging

if TYPE_CHECKING:
    from instagrapi.types import Media

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Extracts and saves metadata for Instagram media."""
    
    def __init__(self, metadata_dir: Path):
        self.metadata_dir = metadata_dir
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
    
    def extract_metadata(self, media) -> dict:
        """
        Extract comprehensive metadata from a media object.
        
        Args:
            media: Media object from instagrapi or mock object
            
        Returns:
            Dictionary containing metadata
        """
        metadata = {
            "pk": str(media.pk),
            "media_type": media.media_type,
            "media_type_name": self._get_media_type_name(media.media_type),
            "caption": media.caption_text if media.caption_text else "",
            "username": media.user.username if media.user else "unknown",
            "user_id": str(media.user.pk) if media.user else "",
            "taken_at": str(media.taken_at) if media.taken_at else "",
            "like_count": media.like_count if hasattr(media, 'like_count') else 0,
            "comment_count": media.comment_count if hasattr(media, 'comment_count') else 0,
            "product_type": media.product_type if hasattr(media, 'product_type') else "",
            "code": media.code if hasattr(media, 'code') else "",
            "hashtags": self._extract_hashtags(media.caption_text) if media.caption_text else [],
            "mentions": self._extract_mentions(media.caption_text) if media.caption_text else [],
            "downloaded_at": self._get_timestamp()
        }
        
        # Add audio information for reels/videos
        if media.media_type == 2 and hasattr(media, 'clips_metadata'):
            if media.clips_metadata and hasattr(media.clips_metadata, 'original_sound_info'):
                sound_info = media.clips_metadata.original_sound_info
                if sound_info:
                    metadata["audio"] = {
                        "audio_id": str(sound_info.audio_asset_id) if hasattr(sound_info, 'audio_asset_id') else "",
                        "original_audio_title": sound_info.original_audio_title if hasattr(sound_info, 'original_audio_title') else ""
                    }
            elif media.clips_metadata and hasattr(media.clips_metadata, 'music_info'):
                music_info = media.clips_metadata.music_info
                if music_info:
                    metadata["audio"] = {
                        "audio_id": str(music_info.audio_asset_id) if hasattr(music_info, 'audio_asset_id') else "",
                        "original_audio_title": music_info.display_artist if hasattr(music_info, 'display_artist') else ""
                    }
        
        # Add location if available
        if hasattr(media, 'location') and media.location:
            metadata["location"] = {
                "name": media.location.name if hasattr(media.location, 'name') else "",
                "city": media.location.city if hasattr(media.location, 'city') else "",
            }
        
        # Add carousel info for albums
        if media.media_type == 8 and hasattr(media, 'resources'):
            metadata["carousel_count"] = len(media.resources)
        
        return metadata
    
    def save_metadata(self, media, pk: str) -> Optional[Path]:
        """
        Save metadata to a JSON file.
        
        Args:
            media: Media object
            pk: Post primary key
            
        Returns:
            Path to metadata file or None if failed
        """
        try:
            metadata = self.extract_metadata(media)
            filepath = self.metadata_dir / f"{pk}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Saved metadata for {pk}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error saving metadata for {pk}: {str(e)}")
            return None
    
    @staticmethod
    def _extract_hashtags(text: str) -> List[str]:
        """Extract hashtags from text."""
        if not text:
            return []
        # Find all hashtags
        hashtags = re.findall(r'#(\w+)', text)
        return list(set(hashtags))  # Remove duplicates
    
    @staticmethod
    def _extract_mentions(text: str) -> List[str]:
        """Extract user mentions from text."""
        if not text:
            return []
        # Find all mentions
        mentions = re.findall(r'@(\w+)', text)
        return list(set(mentions))  # Remove duplicates
    
    @staticmethod
    def _get_media_type_name(media_type: int) -> str:
        """Get human-readable media type name."""
        type_map = {
            1: "Photo",
            2: "Video/Reel",
            8: "Album/Carousel"
        }
        return type_map.get(media_type, "Unknown")
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
