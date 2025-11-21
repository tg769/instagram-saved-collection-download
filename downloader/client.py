"""
Instagram client initialization and authentication.
"""

# Apply compatibility patch for Python 3.14+
try:
    from . import compat
except:
    pass

from instagrapi import Client
from instagrapi.exceptions import LoginRequired, PleaseWaitFewMinutes
import logging

logger = logging.getLogger(__name__)


class InstagramClient:
    """Handles Instagram client initialization and authentication."""
    
    def __init__(self):
        self.client = Client()
        self.client.delay_range = [1, 3]  # Delay between requests
        
    def login_with_session(self, sessionid: str) -> bool:
        """
        Login to Instagram using session ID.
        
        Args:
            sessionid: Instagram session cookie value
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            logger.info("Attempting to login with session ID...")
            self.client.login_by_sessionid(sessionid)
            
            # Test authentication by fetching user info
            user_id = self.client.user_id
            user_info = self.client.user_info(user_id)
            
            logger.info(f"Successfully logged in as @{user_info.username}")
            return True
            
        except LoginRequired:
            logger.error("Login failed. Session ID may be invalid or expired.")
            return False
        except PleaseWaitFewMinutes:
            logger.error("Instagram is asking to wait. You may be rate-limited.")
            return False
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return False
    
    def get_client(self) -> Client:
        """Return the authenticated client instance."""
        return self.client
    
    def get_username(self) -> str:
        """Get the username of the logged-in user."""
        try:
            user_info = self.client.user_info(self.client.user_id)
            return user_info.username
        except Exception as e:
            logger.error(f"Error getting username: {str(e)}")
            return "unknown"
