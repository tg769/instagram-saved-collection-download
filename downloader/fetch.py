"""
Fetch saved media from Instagram.
"""

from instagrapi import Client
from instagrapi.types import Media
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SavedMediaFetcher:
    """Handles fetching saved media from Instagram."""
    
    def __init__(self, client: Client):
        self.client = client
    
    def get_collections(self) -> List[Dict]:
        """
        Get all saved collections.
        
        Returns:
            List of collection dictionaries with id, name, and count
        """
        try:
            logger.info("Fetching collections...")
            
            # Fetch collections using private API
            result = self.client.private_request("collections/list/")
            
            collections = []
            items = result.get("items", [])
            
            for item in items:
                collection = {
                    "id": item.get("collection_id"),
                    "name": item.get("collection_name"),
                    "type": item.get("collection_type"),
                    "count": item.get("collection_media_count", 0)
                }
                collections.append(collection)
            
            logger.info(f"Found {len(collections)} collections")
            return collections
            
        except Exception as e:
            logger.error(f"Error fetching collections: {str(e)}")
            return []
    
    def fetch_collection_medias(self, collection_id: str, amount: int = 0) -> List[Media]:
        """
        Fetch media from a specific collection.
        
        Args:
            collection_id: The collection ID to fetch from
            amount: Number of posts to fetch (0 = all)
            
        Returns:
            List of Media objects
        """
        try:
            logger.info(f"Fetching posts from collection {collection_id}...")
            
            medias = []
            max_id = None
            fetched = 0
            
            while True:
                # Build endpoint
                endpoint = f"feed/collection/{collection_id}/"
                params = {"include_igtv_preview": "false"}
                if max_id:
                    params["max_id"] = max_id
                
                result = self.client.private_request(endpoint, params=params)
                items = result.get("items", [])
                
                # Convert to Media objects
                for item in items:
                    try:
                        media_data = item.get("media")
                        if media_data:
                            media_pk = media_data.get("pk")
                            if media_pk:
                                media = self.client.media_info(media_pk)
                                medias.append(media)
                                fetched += 1
                                
                                # Check if we've reached the desired amount
                                if amount > 0 and fetched >= amount:
                                    logger.info(f"Reached target of {amount} posts")
                                    return medias
                    except Exception as e:
                        logger.warning(f"Failed to fetch media: {str(e)}")
                        continue
                
                # Check if more posts are available
                more_available = result.get("more_available", False)
                max_id = result.get("next_max_id")
                
                logger.info(f"Fetched {len(medias)} posts so far...")
                
                if not more_available or not max_id:
                    break
            
            logger.info(f"Total fetched: {len(medias)} posts")
            return medias
            
        except Exception as e:
            logger.error(f"Error fetching collection media: {str(e)}")
            return []
    
    def fetch_all_saved_medias(self) -> List[Media]:
        """
        Fetch all saved media posts from Instagram.
        Handles pagination automatically.
        
        Returns:
            List of Media objects
        """
        try:
            logger.info("Fetching saved posts...")
            
            # Try different methods depending on instagrapi version
            # amount=0 means fetch ALL posts (no limit)
            if hasattr(self.client, 'saved_medias'):
                # Newer version
                logger.info("Using saved_medias method to fetch all posts...")
                saved_medias = self.client.saved_medias(amount=0)
            elif hasattr(self.client, 'collection_medias'):
                # Older version - use collection method
                logger.info("Using collection_medias method to fetch all posts...")
                saved_medias = self.client.collection_medias("ALL_MEDIA_AUTO_COLLECTION", amount=0)
            else:
                # Fallback - try to use private API
                logger.warning("Using fallback method for fetching saved posts")
                saved_medias = self._fetch_saved_private_api()
            
            logger.info(f"Found {len(saved_medias)} saved posts.")
            return saved_medias
            
        except Exception as e:
            logger.error(f"Error fetching saved media: {str(e)}")
            return []
    
    def _fetch_saved_private_api(self) -> List[Media]:
        """Fallback method using private API with pagination."""
        try:
            # Use the private API endpoint for saved posts with pagination
            medias = []
            max_id = None
            more_available = True
            
            logger.info("Fetching saved posts using private API (may take a while)...")
            
            while more_available:
                # Build endpoint with pagination
                endpoint = "feed/saved/posts/"
                params = {"include_igtv_preview": "false"}
                if max_id:
                    params["max_id"] = max_id
                
                result = self.client.private_request(endpoint, params=params)
                items = result.get("items", [])
                
                # Convert to Media objects
                for item in items:
                    try:
                        media_pk = item.get("media", {}).get("pk")
                        if media_pk:
                            media = self.client.media_info(media_pk)
                            medias.append(media)
                    except Exception as e:
                        logger.warning(f"Failed to fetch media: {str(e)}")
                        continue
                
                # Check if more posts are available
                more_available = result.get("more_available", False)
                max_id = result.get("next_max_id")
                
                logger.info(f"Fetched {len(medias)} posts so far...")
                
                if not more_available:
                    break
            
            return medias
        except Exception as e:
            logger.error(f"Failed to use private API: {str(e)}")
            return []
    
    def get_media_info(self, media: Media) -> dict:
        """
        Extract basic information from a media object.
        
        Args:
            media: Media object from instagrapi
            
        Returns:
            Dictionary with media info
        """
        return {
            "pk": str(media.pk),
            "media_type": media.media_type,
            "user": media.user.username if media.user else "unknown",
            "caption": media.caption_text if media.caption_text else "",
            "taken_at": str(media.taken_at) if media.taken_at else "",
        }
